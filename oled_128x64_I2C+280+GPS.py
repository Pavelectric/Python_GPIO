#!/usr/bin/env python
# -*- coding: utf-8 -*- # вроде как разрешает русские буквы в программе
#####################################################################################
# The oled display 128x64 works on the I2C bus, it has the address 3c               #
# The following pins are involved - 2(VCC), 6(GND), 3(SDA), 5(SCL)                  #
# Bme280 it has the address 0x76                                                    #
# GPS reciever Ublox m8n, work on GPSG service, adress /dev/ttyS4                   #
# The device address can be viewed by executing the command "sudo i2cdetect-y 2"    #
# You will see your current time and date on the display.                           #
# Autor - Pavel (Pavelectric) pavelectric@mail.ru                                   #
#####################################################################################

import bme280 # библиотека погодной платы
from device import ssd1306  # библиотека Oled дисплея
from render import canvas
from PIL import ImageFont
from time import strftime, gmtime, sleep # библиотека времени и прочего
import time # для sleep
import subprocess # библиотека работы с командами Bash
import wiringpi as wpi # библиотека для работы с GPIO
from gps3.agps3threaded import AGPS3mechanism # библиотека работы с GPSD

agps_thread = AGPS3mechanism()  # Instantiate AGPS3 Mechanisms
agps_thread.stream_data()  # From localhost (), or other hosts, by example, (host='gps.ddns.net')
agps_thread.run_thread()  # Throttle time to sleep after an empty lookup, default '()' 0.2 two tenths of a second


wpi.wiringPiSetup() # режим настройки GPIO
wpi.pinMode(3, 1) # 3 пин (по версии wiringpi) в режим ВЫХОД
wpi.pinMode(2, 0) # 2 пин (по версии wiringpi) в режим ВХОД

device = ssd1306(port=2, address=0x3C) # определяем дисплей на 2 порт и адрес 0x3C
font = ImageFont.load_default() # задаем шрифт
font_ra = ImageFont.truetype('OpenSans-Regular.ttf', 12) # задаем шрифт
font2 = ImageFont.truetype('fontawesome-webfont.ttf', 14) # задаем шрифт
font_cl = ImageFont.truetype('OpenSans-Regular.ttf', 32) # задаем шрифт
font_ra10 = ImageFont.truetype('Tahoma.ttf', 12) # задаем шрифт
font_ra16 = ImageFont.truetype('Tahoma.ttf', 16) # задаем шрифт
state = 0 # статус по умолчинию

def executCMD(cmd): # функция терминального выполнения 
    return subprocess.check_output(cmd, shell = True )

def page1(): # функция "страница №1"
    IP = executCMD("hostname -I | cut -d\' \' -f1 | head --bytes -1") # команда выколупывания IP адреса
    Disk = executCMD("df -h | awk '$NF==\"/\"{printf \"%s\", $5}'") # команда выколупывания объема диска (занятого)
    Temperature = executCMD("cat /sys/class/thermal/thermal_zone0/temp | cut -c 1-2") # команда выколупывания температуры процессора

    with canvas(device) as draw:
        draw.text((1, 0), strftime('%H:%M:%S'),font=font_ra, fill=255) # вывод время (Час : Минута : Секунда)
        draw.text((71, 0), strftime('%d.%m.%y'),font=font_ra, fill=255) # вывод даты (Число : Месяц : Год)
        draw.text((1, 15), ("lan :"),font=font_ra10, fill=255) # вывод слова "lan"
        draw.text((30, 15), str(IP), font=font_ra10, fill=255) # вывод IP адреса
        draw.text((1, 28), ("cpu : "),font=font_ra10, fill=255) # вывод слова "cpu"
        draw.text((33, 28), str(Temperature), font=font_ra10, fill=255) # вывод температуры процессора 
        draw.text((46, 28), chr(176) + "C", font=font_ra10, fill=255) # значек "градус"
        draw.text((63, 28), ("hdd :"),font=font_ra10, fill=255) # вывод слова "hdd"
        draw.text((94, 28), str(Disk), font=font_ra10, fill=255) # вывод процента использования диска 
        draw.line((0,43,128,43), fill="white") # просто линия
        draw.text((0, 42), unicode("Люблю Юленьку!",'utf-8'),font=font_ra16, fill=255) # чтоб жена не ворчала :)           

def page2(): # функция "страница №2"
    temperature,pressure,humidity = bme280.readBME280All() # инициализация погодного датчика
    IP = executCMD("hostname -I | cut -d\' \' -f1 | head --bytes -1") # команда выколупывания IP адреса

    with canvas(device) as draw:
        draw.text((0, 0), ("MSK"), font=font_ra, fill=255) # вывод слова "MSK"
        draw.text((40, 0), strftime('%H : %M : %S'),font=font_ra, fill=255) # вывод время (Час : Минута : Секунда)
        draw.text((0, 16), unicode("Дата",'utf-8'),font=font_ra, fill=255) # вывод слова "Дата"
        draw.text((40, 16), strftime('%d . %m . %y'),font=font_ra, fill=255) # вывод даты (Число : Месяц : Год)
        draw.text((0, 33), unichr(61931), font=font2, fill=255) #61931 значек "вайфай" 
        draw.text((40, 33), str(IP), font=font_ra, fill=255) # вывод IP адреса
        draw.text((0, 50), str(int(humidity)) + "%", font=font_ra, fill=255)    # вывод влажности
        draw.text((30, 50), str(int((pressure) * 0.750062)) + "mm", font=font_ra, fill=255) # вывод давления в мм
        draw.text((80, 50), str(int(temperature)) + unichr(176), font=font_ra, fill=255) # вывод температуры + градус

def page3(): # функция "страница №3"
    with canvas(device) as draw:
        draw.text((0, 0), unicode("Широта: " + format(agps_thread.data_stream.lat)[:7],'utf-8'), font=font_ra, fill=255) # значения Широты (lat)
        draw.text((0, 16), unicode("Долгота: " + format(agps_thread.data_stream.lon)[:7],'utf-8'), font=font_ra, fill=255) # значения Долготы (lon)
        draw.text((0, 33), unicode("Скорость: " + format(agps_thread.data_stream.speed)[:3],'utf-8'), font=font_ra, fill=255) # значения Скорости (speed)
        draw.text((0, 50), str("Course: ")+(format(agps_thread.data_stream.track)[:3]) + unichr(176), font=font_ra, fill=255) # значения Курса (track)
try:
    while True:

        button = wpi.digitalRead(2) # читаем состояние кнопки в "button"

        if state == 0: 
            page1() # работает функция "1 страница"
            wpi.digitalWrite(3, 0) # светодиод выключен
            if button:  # если нажата кнопка
                state += 1 # к "state" прибавляем 1

        elif state == 1:
            page2() # работает функция "2 страница"
            wpi.digitalWrite(3, 1) # светодиод выключен
            if button: # если нажата кнопка
                state += 1 # к "state" прибавляем 1

        elif state == 2:
            page3() # работает функция " страница"
            wpi.digitalWrite(3, 0) # светодиод выключен
            if button: # если нажата кнопка
                state = 0 # "state" снова равно "0"
finally: # финализация программы
    with canvas(device) as draw:
        draw.text((10, 25), ("Program complete"), font=font_ra, fill=255) # сообщение при корректном завершении
        wpi.digitalWrite(3,0) # выключаем светодиод на 7 пине

