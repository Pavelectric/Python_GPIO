#!/usr/bin/env python
# -*- coding: utf-8 -*- # вроде как разрешает русские буквы в программе
#####################################################################################
# The oled display 128x64 works on the I2C bus, it has the address 3c               #
# The following pins are involved - 1(3.3V), 6(GND), 3(SDA), 5(SCL)                 #
# Button connect to 13 pin (switch + 3.3V line)                                     #
# LED connect to 15 pin (330 Omh resistor to GND)                                   #
# Bme280 it has the address 0x76                                                    #
# GPS reciever Ublox m8n, work on GPSG service, adress /dev/ttyS4 (19, 21 pin)      #
# The device address can be viewed by executing the command "sudo i2cdetect-y 2"    #
# You will see your current time and date on the display + values from the weather  #
# sensor + current coordinates, speed and course. The screens are changed by        #
# pressing the button; the LED is on in the weather data reading mode               #
# Autor - Pavel (Pavelectric) pavelectric@mail.ru                                   #
#####################################################################################

import bme280 # weather board library
from device import ssd1306  # Oled Display Library
from render import canvas
from PIL import ImageFont
from time import strftime, gmtime, sleep # library of time and other things
import time # for sleep
import subprocess # bash command library
import wiringpi as wpi # GPIO library
from gps3.agps3threaded import AGPS3mechanism # GPSD library

agps_thread = AGPS3mechanism()  # Instantiate AGPS3 Mechanisms
agps_thread.stream_data()  # From localhost (), or other hosts, by example, (host='gps.ddns.net')
agps_thread.run_thread()  # Throttle time to sleep after an empty lookup, default '()' 0.2 two tenths of a second


wpi.wiringPiSetup() # GPIO configuration mode
wpi.pinMode(3, 1) # 3 pin (wiringpi version, real 15) to EXIT mode
wpi.pinMode(2, 0) # 2 pin (according to wiringpi, real 13) in the INPUT mode

device = ssd1306(port=2, address=0x3C) # we define the display on the 2nd port and the address 0x3C
font = ImageFont.load_default() # set the font
font_ra = ImageFont.truetype('OpenSans-Regular.ttf', 12) # set the font
font2 = ImageFont.truetype('fontawesome-webfont.ttf', 14) # set the font
font_cl = ImageFont.truetype('OpenSans-Regular.ttf', 32) # set the font
font_ra10 = ImageFont.truetype('Tahoma.ttf', 12) # set the font
font_ra16 = ImageFont.truetype('Tahoma.ttf', 16) # set the font
state = 0 # default status

def executCMD(cmd): # terminal execution function
    return subprocess.check_output(cmd, shell = True )

def page1(): # function "page number 1"
    IP = executCMD("hostname -I | cut -d\' \' -f1 | head --bytes -1") # IP address banging command
    Disk = executCMD("df -h | awk '$NF==\"/\"{printf \"%s\", $5}'") # disk bump command (busy)
    Temperature = executCMD("cat /sys/class/thermal/thermal_zone0/temp | cut -c 1-2") # CPU temperature bump command

    with canvas(device) as draw:
        draw.text((1, 0), strftime('%H:%M:%S'),font=font_ra, fill=255) # output time (Hour: Minute: Second)
        draw.text((71, 0), strftime('%d.%m.%y'),font=font_ra, fill=255) # output date (Number: Month: Year)
        draw.text((1, 15), ("lan :"),font=font_ra10, fill=255) # output of the word "lan"
        draw.text((30, 15), str(IP), font=font_ra10, fill=255) # output IP address
        draw.text((1, 28), ("cpu : "),font=font_ra10, fill=255) # output of the word "cpu"
        draw.text((33, 28), str(Temperature), font=font_ra10, fill=255) # CPU temperature output
        draw.text((46, 28), chr(176) + "C", font=font_ra10, fill=255) # degree icon"
        draw.text((63, 28), ("hdd :"),font=font_ra10, fill=255) # output word "hdd"
        draw.text((94, 28), str(Disk), font=font_ra10, fill=255) # output percent disk usage
        draw.line((0,43,128,43), fill="white") # just line
        draw.text((0, 42), unicode("Люблю Юленьку!",'utf-8'),font=font_ra16, fill=255) # so that the wife does not grumble :)        

def page2(): # function "page number 2"
    temperature,pressure,humidity = bme280.readBME280All() # weather sensor initialization
    IP = executCMD("hostname -I | cut -d\' \' -f1 | head --bytes -1") # IP address banging command

    with canvas(device) as draw:
        draw.text((0, 0), ("MSK"), font=font_ra, fill=255) # output of the word "MSK"
        draw.text((40, 0), strftime('%H : %M : %S'),font=font_ra, fill=255) # output time (Hour: Minute: Second)
        draw.text((0, 16), unicode("Дата",'utf-8'),font=font_ra, fill=255) # output of the word "Date"
        draw.text((40, 16), strftime('%d . %m . %y'),font=font_ra, fill=255) # output date (Number: Month: Year)
        draw.text((0, 33), unichr(61931), font=font2, fill=255) # Wi fi icon
        draw.text((40, 33), str(IP), font=font_ra, fill=255) # output IP address
        draw.text((0, 50), str(int(humidity)) + "%", font=font_ra, fill=255)    # moisture output
        draw.text((30, 50), str(int((pressure) * 0.750062)) + "mm", font=font_ra, fill=255) # pressure output in mm
        draw.text((80, 50), str(int(temperature)) + unichr(176), font=font_ra, fill=255) # temperature output + degree icon

def page3(): # function "page number 3"
    with canvas(device) as draw:
        draw.text((0, 0), unicode("Широта: " + format(agps_thread.data_stream.lat)[:7],'utf-8'), font=font_ra, fill=255) # Latitude values (lat) (RUS simbol)
        draw.text((0, 16), unicode("Долгота: " + format(agps_thread.data_stream.lon)[:7],'utf-8'), font=font_ra, fill=255) # Longitude values (lon) (RUS simbol)
        draw.text((0, 33), unicode("Скорость: " + format(agps_thread.data_stream.speed)[:3],'utf-8'), font=font_ra, fill=255) # Speed values (RUS simbol)
        draw.text((0, 50), str("Course: ")+(format(agps_thread.data_stream.track)[:3]) + unichr(176), font=font_ra, fill=255) # Course values
try:
    while True:

        button = wpi.digitalRead(2) # read the state of the button in the "button"

        if state == 0: # if state = 0
            page1() # the "1 page" function works
            wpi.digitalWrite(3, 0) # LED is off
            if button:  # if the button is pressed
                state += 1 # add 1 to "state"
                sleep(0.2) # eliminate contact bounce

        elif state == 1: # if state = 1
            page2() # the "2 page" function works
            wpi.digitalWrite(3, 1) # LED is on
            if button: # if the button is pressed
                state += 1 # add 1 to "state"
                sleep(0.2) # eliminate contact bounce

        elif state == 2: # if state = 2
            page3() # the function "3 page" works
            wpi.digitalWrite(3, 0) # LED is off
            if button: # if the button is pressed
                state = 0 # "state is "0" again
                sleep(0.2) # eliminate contact bounce

finally: # program finalization
    with canvas(device) as draw:
        draw.text((10, 25), ("Program complete"), font=font_ra, fill=255) # message upon correct completion
        wpi.digitalWrite(3,0) # turn off the LED on the 3 pin
