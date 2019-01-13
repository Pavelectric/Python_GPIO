
#####################################################################################
# The oled display 128x64 works on the I2C bus, it has the address 3c               #
# The following pins are involved - 2(VCC), 6(GND), 3(SDA), 5(SCL)                  #
# The device address can be viewed by executing the command "sudo i2cdetect-y 2"    #
# You will see your current time and date on the display.                           #
# Autor - Pavel (Pavelectric) pavelectric@mail.ru                                   #
#####################################################################################

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from device import ssd1306
from render import canvas
from PIL import ImageFont
from time import strftime, gmtime, sleep
import os

device = ssd1306(port=2, address=0x3C)                                         # our display on port 2 with address 3C
font = ImageFont.load_default()                                                # default font assignment
font_ra = ImageFont.truetype('OpenSans-Regular.ttf', 12)                       # "Regular" font assignment

while True:
    f = os.popen('hostname -I')                                                # command execution "hostname -I"
    your_ip = f.read()                                                         # reading command output
    with canvas(device) as draw:
        draw.text((0, 0), unicode("Адрес",'utf-8'),font=font_ra, fill=255)     # line 0, off 0, "Address" in Russian
        draw.text((40, 0), your_ip[0:-1],font=font_ra, fill=255)               # line 0, off 40, output your_ip value
        draw.text((0, 16), unicode("Дата",'utf-8'),font=font_ra, fill=255)     # line 16, off 0, "Date" in Russian
        draw.text((50, 16), strftime('%d %b %Y'),font=font_ra, fill=255)       # line 16, off 50, date in format "day month year"
        draw.text((0, 33), ("MSK"), font=font_ra, fill=255)                    # line 33, off 0, "MSK"
        draw.text((50, 33), strftime('%H : %M : %S'),font=font_ra, fill=255)   # line 33, off 50, output Local time
        draw.text((0, 49), ("UTC"),font=font_ra, fill=255)                     # line 49, off 0, "UTC"
        draw.text((50, 49), strftime('%H : %M : %S',gmtime()),font=font_ra, fill=255)   # line 49, off 50, output UTC time
sleep(0.5)                                                                     # 0.5 second pause
