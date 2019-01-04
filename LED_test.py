######################################################
# From the "gpio readall" command,                   #
# it follows that the following "GPIO" are available #
# to us:  0, 1, 2, 3, 4, 5, 6, 7, 11, 15 and 16.     #
# We connect the LED:                                #
# "-" to 6 pin, and the "+" - to the desired GPIO.   #
# Autor - Pavel (Pavelectric) pavelectric@mail.ru    #
######################################################

import wiringpi as wpi
import time

wpi.wiringPiSetup()
wpi.pinMode(7, 1)     # try GPIO 7, on physical contact 7

while True:
        wpi.digitalWrite(7, 1)        # we light the 7th
        time.sleep(1)                 # wait 1 second
        wpi.digitalWrite(7, 0)        # extinguish the 7th
        time.sleep(1)                 # wait 1 second
        
###########################################################
# I have earned: 0, 2, 3, 4, 5, 6 and 7 GPIO              #
# did not earn: 11, 15 and 16 GPIO                        #
# Apparently the contacts work only in the "INPUT" mode.  #
###########################################################
