"""
created on thrusday September 26 2019

@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomediacles, UQAC
    Office: H2-1180

project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

import time
import Adafruit_PCA9685


class Guidance:

    motor_pin = 0
    steering_pin = 1
    rear_light_pin = 2
    pca = None

    def __init__(self, hz):
        self.hz = hz
        # Open pwm control with PCA9685
        self.initialize_pwm()

    def control_steering(self, steering):
        # Control steering from duty cycle (map 0. to 1.84 ms)
        self.pca.set_pwm(self.steering_pin, 0, int(self.hz * 4.096 * steering))

    def control_throttle(self, throttle):
        # Control motor speed from duty cycle (map 1 to 2 ms)
        self.pca.set_pwm(self.motor_pin, 0, int(self.hz * 4.096 * throttle))

    def brake_is_on(self, state):
        # Open rear lights when brakes are applied
        if state:
            self.pca.set_pwm(self.rear_light_pin, 0, 4096)
        else:
            self.pca.set_pwm(self.rear_light_pin, 0, 0)

    def initialize_pwm(self):
        # Initialize PCA9685 pwm generator
        self.pca = Adafruit_PCA9685.PCA9685()
        self.pca.set_pwm_freq(self.hz)

        # Initialize motor pin to 0 speed on init (1.5 ms - corrected to 4096 res.)
        self.pca.set_pwm(self.motor_pin, 0, 594)
        time.sleep(1)
        self.pca.set_pwm(self.steering_pin, 0, 620)

