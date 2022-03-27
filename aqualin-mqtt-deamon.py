#!/usr/bin/env python
# ---------------------------------------------------------------------------------------
# Name:        aqualin_mqtt_servive service
# Purpose:     listening to MQTT posts and sending a request to a Aqualin celenoid valve
#              determening batteru status of every aqualin unit connected
#
# Author:      roy.oltmans
#
# Created:     14-04-2020
# Copyright:   (c) roy.oltmans 2018
# Licence:     <your licence>
# ---------------------------------------------------------------------------------------
from bluepy import btle
import queue
from threading import Thread
import paho.mqtt.client as mqtt
import main_utils, os, sys, syslog, time, schedule, binascii

import inspect
import types
from typing import cast

tools = main_utils.tools()

trace = tools.fetchConfig().get('GENERAL', 'errortrace')
bleHandle = tools.fetchConfig().get('AQUALIN', 'bleHandle')
valuebase = tools.fetchConfig().get('AQUALIN', 'valueBase')
waittime = tools.fetchConfig().get('AQUALIN', 'waittime')
location = tools.fetchConfig().get('AQUALIN', 'location')
devicemaclist = tools.fetchConfig().get('AQUALIN', 'macaddresslist')
stdwatertimer = tools.fetchConfig().get('AQUALIN', 'stdwatertimer')
strmqtthost = tools.fetchConfig().get('MQTT', 'Host')
intmqttport = int(tools.fetchConfig().get('MQTT', 'Port'))
strmqttclientid = tools.fetchConfig().get('MQTT', 'Clientid')
strmqttuser = tools.fetchConfig().get('MQTT', 'User')
strmqttpass = tools.fetchConfig().get('MQTT', 'Pass')
mqttbasepath = tools.fetchConfig().get('MQTT', 'mqttbasepath')

# Set up some global variables
devicemaclist = devicemaclist.split(',')
num_fetch_threads = 2
mqtt_Queue = queue.Queue()
battery_Queue = queue.Queue()
deviceblelock = False

def lockble():
    global deviceblelock

    if trace:
        print(" "+ inspect.stack()[1].function +"() deviceblelock locking")

    deviceblelock = True

def unlockble():
    global deviceblelock

    if trace:
        print(" "+ inspect.stack()[1].function +"() deviceblelock unlocking")

    deviceblelock = False

def on_connect(client, userdata, flags, rc):  # The callback for when the client receives a response from the server.
    syslog.syslog("MQTT: Connected with result code " + str(rc))
    if trace:
        print("MQTT: Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
    client.subscribe(mqttbasepath+'#')


def on_message(client, userdata, msg):  # When a message is received on the MQTT bus
    msg_payload = msg.payload.decode("utf-8")
    if 'status' in msg.topic.split("/"):  # check if the req is applicable
        if 'on' in msg.topic.split("/"):  # check kind of request
            status = 'on'
            timervalue = int(msg_payload)
            if timervalue <= 0:
                timervalue = stdwatertimer
        elif 'off' in msg.topic.split("/"):
            status = 'off'
            timervalue = 00
        elif 'valve' in msg.topic.split("/"):
            if msg_payload == 'state':
                status = 'state'
            elif msg_payload == 'timer':
                status = 'timer'
            timervalue = stdwatertimer
        mqtt_Queue.put((status,timervalue,msg.topic.split("/")[2]))
        mqtt_Queue.qsize()

def getblevalue(status, timer):  # transform and prepair the Value response on or off and time the vale will be active
    valuerequest = ''  # type: str
    valuestatus = '00'
    valuecalltimer = '0000'
    valuecalltimer = hex(int(timer)).split('x')[-1]  # decimal to hex conversion for the of time
    valuecalltimer = valuecalltimer.rjust(4, '0')  # if the value is shorter than 4 digits fill them up with zeros
    if status == 'on':
        valuestatus = '01'
    elif status == 'off':
        valuestatus = '00'
    valuerequest += valuebase
    valuerequest += valuestatus
    valuerequest += valuecalltimer
    if trace:
        print("BLE instruction: ")
        print(valuerequest)

    #value_req_hex = hex(int("0x"+ valuerequest, 16))  # payload preperation to hex for writing to valve
    print("Hex:"+ valuerequest)
    return valuerequest


def setblerequest(status, devicemac, bleHandle, bleValue):
    global deviceblelock
    if trace:
        print("Connecting " + devicemac + "...")
    if deviceblelock == False:

        lockble()

        device = btle.Peripheral(str(devicemac))
        value_req_hex = hex(int(bleValue, 16))  # payload preperation to hex for writing to valve
        print("setblerequest- bleValue: "+ value_req_hex)
        print("setblerequest- Bytes:")
        print(bytes.fromhex(bleValue) )
        device.writeCharacteristic(0x0073, bytes.fromhex(bleValue), withResponse=True)
        if trace:
            print("Wait " + str(waittime) + " seconds...")
        time.sleep(int(waittime))
        device.disconnect()

        unlockble()
    else:
        time.sleep(5)
        setblerequest(status, devicemac, bleHandle, bleValue)

def getsolenoidvalve(devicemac):
    global deviceblelock
    if trace:
        print("Connecting " + devicemac + "...")
    if deviceblelock == False:
        lockble()

        device = btle.Peripheral(str(devicemac))
        if trace:
            print("Characteristic 0x0073")
            print(charateristic73)
            print(binascii.b2a_hex(charateristic73))
            print(binascii.b2a_hex(charateristic73).decode('utf-8'))
            print(str(binascii.b2a_hex(charateristic73).decode('utf-8'))[6:10])
        intvalvestate = int(str(binascii.b2a_hex(charateristic73).decode('utf-8'))[6:10],16)
        if trace:
            print( "intvalvestate: "+ str(intvalvestate))
        time.sleep(int(waittime))
        device.disconnect()

        unlockble()

        return intvalvestate
    else:
        time.sleep(5)

def runworkerbledevice():
    while True:
        queuevalues = mqtt_Queue.get()
        devicemac = queuevalues[2]
        if trace:
            print(queuevalues)
        intsolenoidstate = getsolenoidvalve(devicemac)
        if queuevalues[0] == 'state':
            if intsolenoidstate <= 0:
                strvalvestate = 'off'
            else:
                strvalvestate = 'on'
            client.publish(mqttbasepath + str(devicemac) + '/valvestate', strvalvestate)  
        elif queuevalues[0] == 'timer':
            client.publish(mqttbasepath + str(devicemac) + '/valvetimer', str(intsolenoidstate))
        else:
            # Initialize ble req
            setblerequest(queuevalues[0], devicemac, bleHandle, getblevalue(queuevalues[0], queuevalues[1]))
        if trace:
            print("BLE instruction processed...")

def runvalvecheck():
    global deviceblelock
    for i, devicemac in enumerate(devicemaclist):
        if deviceblelock == False:
            lockble()

            device = btle.Peripheral(str(devicemac))
            intsolenoidstate = getsolenoidvalve(devicemac)
            if intsolenoidstate <= 0:
                strvalvestate = 'off'
            else:
                strvalvestate = 'on'
            client.publish(mqttbasepath + str(devicemac) + '/valvestate', strvalvestate)  # publish
            if trace:
                print("Valve state is " + strvalvestate + " for device " + str(devicemac))
            time.sleep(int(waittime))
            device.disconnect()

            unlockble()
        else:
            time.sleep(5)

def runbatterycheck():
    global deviceblelock
    for i, devicemac in enumerate(devicemaclist):
        if deviceblelock == False:
            lockble()

            device = btle.Peripheral(str(devicemac))
            strbatstatus = str(binascii.b2a_hex(device.readCharacteristic(0x0081)).decode('utf-8'))
            client.publish(mqttbasepath + str(devicemac) + '/battery', strbatstatus)  # publish
            if trace:
                print("Battery status " + str(strbatstatus) + "% of device " + str(devicemac))
            time.sleep(int(waittime))
            device.disconnect()

            unlockble()
        else:
            time.sleep(5)

def runworkerblebatterystats():
    while True:
        schedule.run_pending()
        time.sleep(int(waittime))

if __name__ == '__main__':
    # First thread creating Queue for state calls
    t1 = Thread(target=runworkerbledevice)  # Start worker thread 1
    t1.setDaemon(True)
    t1.start()

    # Setting itteration check battery status every week on sunday and reporting on MQTT
    # schedule.every(10).seconds.do(runbatterycheck)  # for checking thread fullfillment
    schedule.every().sunday.at("23:55").do(runbatterycheck)

    # Setting itteration check valve status every 5min and reporting on MQTT
    schedule.every(300).seconds.do(runvalvecheck)  # for checking thread fullfillment

    # Second Thread Battery status checks all devices
    t2 = Thread(target=runworkerblebatterystats)  # Start worker thread 2 monthly
    t2.setDaemon(True)
    t2.start()

    # MQTT Startup
    client = mqtt.Client(strmqttclientid)
    client.on_connect = on_connect
    client.on_message = on_message
    if strmqttuser:
        client.username_pw_set(username=strmqttuser,password=strmqttpass)
    client.connect(strmqtthost, intmqttport, 60)
    client.loop_forever()
