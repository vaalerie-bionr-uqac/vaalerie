"""
created on thursday September 26 2019
last updated on tuesday May 5th 2020
@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomedicales, UQAC
    Office: H2-1180
project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

import time
import Adafruit_PCA9685


class Guidance:

    MOTOR_PIN = 0
    STEERING_PIN = 1
    pca = None

    STEERING_SET_VAL = 620
    THROTTLE_SET_VAL = 594

    def __init__(self, hz):
        self.hz = hz
        # Open pwm control with PCA9685
        self.initialize_pwm()

    def control_steering(self, steering):
        # Control steering from duty cycle (map 0. to 1.84 ms)
        self.pca.set_pwm(self.STEERING_PIN, 0, int(self.hz * 4.096 * steering))

    def control_throttle(self, throttle):
        # Control motor speed from duty cycle (map 1 to 2 ms)
        self.pca.set_pwm(self.MOTOR_PIN, 0, int(self.hz * 4.096 * throttle))

    def initialize_pwm(self):
        # Initialize PCA9685 pwm generator
        self.pca = Adafruit_PCA9685.PCA9685()
        self.pca.set_pwm_freq(self.hz)

        # Initialize motor pin to 0 speed on init (1.5 ms - corrected to 4096 res.)
        self.pca.set_pwm(self.MOTOR_PIN, 0, self.THROTTLE_SET_VAL)
        time.sleep(1)
        self.pca.set_pwm(self.STEERING_PIN, 0, self.STEERING_SET_VAL)
