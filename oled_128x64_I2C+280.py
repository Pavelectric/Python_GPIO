#!/usr/bin/env python
# -*- coding: utf-8 -*-
#####################################################################################
# The oled display 128x64 works on the I2C bus, it has the address 3c               #
# The following pins are involved - 1(3.3V), 6(GND), 3(SDA), 5(SCL)                  #
# Bme280 it has the address 0x76                                                    #
# The device address can be viewed by executing the command "sudo i2cdetect-y 2"    #
# You will see your current time and date on the display.                           #
# Autor - Pavel (Pavelectric) pavelectric@mail.ru                                   #
#####################################################################################

import bme280 # weather sensor library
from device import ssd1306
from render import canvas
from PIL import ImageFont
from time import strftime, gmtime, sleep
import subprocess


device = ssd1306(port=2, address=0x3C) # display in port 2 with adress 0x3C
font = ImageFont.load_default() # font default
font_ra = ImageFont.truetype('OpenSans-Regular.ttf', 12) # font 1
font2 = ImageFont.truetype('fontawesome-webfont.ttf', 14) # font 2
font_cl = ImageFont.truetype('OpenSans-Regular.ttf', 32) # font 3

try:
    while True:

        temperature,pressure,humidity = bme280.readBME280All() #weather sensor initialization
        cmd = "hostname -I | cut -d\' \' -f1 | head --bytes -1" # command to get IP adress
        IP = subprocess.check_output(cmd, shell = True )
         
        with canvas(device) as draw:
            draw.text((0, 0), ("MSK"), font=font_ra, fill=255) # "MSK"
            draw.text((40, 0), strftime('%H : %M : %S'),font=font_ra, fill=255) # time line to display
            draw.text((0, 16), unicode("Дата",'utf-8'),font=font_ra, fill=255) # "Data" in Russian language
            draw.text((40, 16), strftime('%d . %m . %y'),font=font_ra, fill=255) # data line to display
            draw.text((0, 33), unichr(61931), font=font2, fill=255) # simbol "WiFi"
            draw.text((40, 33), str(IP), font=font_ra, fill=255) # IP adress to display       
            draw.text((0, 50), str(int(humidity)) + "%", font=font_ra, fill=255)    # humidity to dispaly
            draw.text((30, 50), str(int((pressure) * 0.750062)) + "mm", font=font_ra, fill=255) # pressure to dispaly + "mm"
            draw.text((80, 50), str(int(temperature)) + unichr(176), font=font_ra, fill=255) # temperature to display + "degree simbol"
    sleep(0.5)

finally:
    with canvas(device) as draw:
        draw.text((10, 25), ("Program complete"), font=font_ra, fill=255)

