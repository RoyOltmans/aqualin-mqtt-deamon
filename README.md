# aqualin-mqtt-deamon
Aqualin BLE Python control rev 0.1

Description: Lightweight aqualin BLE mqtt deamon controller

# Motivation
2 months ago I created a solution to switch a aqualin BLE controled selenoid valve on and off via bash. 

See this repository https://github.com/RoyOltmans/aqualin

This project lacked the automation needs I have to combine this solution for example with Home-assistant. Therefor I started with a MQTT deamon that publishes the battery state of one or more valve's and based on the business rules executed via MQTT controles the valve state on or off.

# Requirements
This project has been build on linux raspbian on a Raspberry Pi Zero W.

Firstly you need the MAC or MAX addresses of the valve's.

Install the required tool:
    
    $  sudo apt install git bluetooth bluez

Identify the valve's:

    $  sudo hcitool lescan

write down the mac address eg 01:02:03:04:05:06

A MQTT 

mosquitto_sub -h [MQTT Host] -t '#' -v

mosquitto_pub -h [MQTT Host] -t home/aqualin/[Aquilin BLE MAC]/status/on -m [payload, timer in minutes]
mosquitto_pub -h [MQTT Host] -t home/aqualin/[Aquilin BLE MAC]/status/on -m 30
