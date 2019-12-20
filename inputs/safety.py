"""
created on thursday September 26 2019
last updated on friday December 20 2019

@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomedicales, UQAC
    Office: H2-1180

project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

import RPi.GPIO as GPIO
# import pigpio as gpio
# import datetime


class Safety:

    pi = None
    ti, tf = 0, 0
    state = True
    oe_pin = 8
    emergency_pin = 10

    def __init__(self):
        # Setup RASPBERRY PI 4 GPIO's
        GPIO.setmode(GPIO.BOARD)
        # Remove warnings
        GPIO.setwarnings(False)
        # PCA freeze pin setup
        GPIO.setup(self.oe_pin, GPIO.OUT)
        # Emergency trigger pin setup
        GPIO.setup(self.emergency_pin, GPIO.IN)
        # Attach an interrupt for emergency pin 10 for rising edge only
        """GPIO.add_event_detect(self.emergency_pin, GPIO.RISING, callback=self.check_emergency_stop)"""

        """self.pi = gpio.pi()
        if not self.pi.connected:
            print("Not connected")
        self.pi.set_mode(15, gpio.INPUT)
        print(self.pi.read(15))"""


    #def check_emergency_stop(self, channel):
        """if GPIO.input(self.emergency_pin):
            self.ti = datetime.datetime.now()
        elif not GPIO.input(self.emergency_pin):
            self.tf = datetime.datetime.now() - self.ti
            self.tf = float(self.tf.total_seconds()*100)
            if self.tf < 1.4 or self.tf > 1.6:
                self.state = False
                print("Emergency pressed", self.tf)"""
