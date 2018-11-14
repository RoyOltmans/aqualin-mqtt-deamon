# aqualin-mqtt-deamon
Aqualin BLE Python control rev 0.1

Description: Lightweight aqualin BLE mqtt deamon controller

All rights of the device are owned by Aqualin

This is a reverse engeneered Bluetooth Low Energy control of the aqualin BLE solenoid valve device without custumizations on the device itself. 

**Usage of this project is on your own risk.**

# Motivation
2 months ago I created a solution to switch a aqualin BLE controled selenoid valve on and off via bash. 

See this repository https://github.com/RoyOltmans/aqualin

This project lacked the automation needs I have to combine this solution for example with Home-assistant. Therefor I started with a MQTT deamon that publishes the battery state of one or more valve's and based on the business rules executed via MQTT controles the valve state on or off.

This makes further automation and control via for instance home assistant easy.

# Requirements
This project has been build on linux raspbian on a Raspberry Pi Zero W.

0) Upgrade and update all repositories:

```
    $  sudo apt-get update
       sudo apt-get upgrade
       sudo apt-get dist-upgrade
```

1) Firstly you need the MAC address(es) of the valve's.

Install the required tool and libraries to support BLE:
```
    $  sudo apt-get install git bluetooth bluez
       sudo apt-get install python
       sudo apt-get install python-pip
``` 

2) Identify the valve(s):
```
    $  sudo hcitool lescan
``` 

write down the mac address of the valve(s) eg 01:02:03:04:05:06

3) Configure the config.ini

Edit the config.ini via your favorite text editor (e.g. nano, vi etc)

4) A MQTT bus is needed install a MQTT bus (for example mosquitto) 
```
    $  sudo apt-get install mosquitto mosquitto-clients python-mosquitto
```

Detailed description can be [found here](https://learn.adafruit.com/diy-esp8266-home-security-with-lua-and-mqtt/configuring-mqtt-on-the-raspberry-pi): 

5) Install necessary supporting libraries for the project
```
    $  sudo pip install paho-mqtt
       sudo pip install schedule
       sudo pip install mercurial
```

6) Install aqualin mqtt deamon
```
    $  git clone https://github.com/RoyOltmans/aqualin-mqtt-deamon.git /opt/aqualin-mqtt-deamon
```


# Usage


```
mosquitto_sub -h [MQTT Host] -t '#' -v
```

```
mosquitto_pub -h [MQTT Host] -t home/aqualin/[Aquilin BLE MAC]/status/on -m [payload, timer in minutes]
mosquitto_pub -h [MQTT Host] -t home/aqualin/[Aquilin BLE MAC]/status/off -m [payload, timer in minutes]
```
