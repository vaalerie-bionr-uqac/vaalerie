"""
created on thrusday September 26 2019

@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomediacles, UQAC
    Office: H2-1180

project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

import ASUS.GPIO as gpio
import time


class Guidance:

    steering = 0
    speed = 0

    def __init__(self, rear_light_pin, steering_pin, speed_pin, hz):
        # 26 is IN
        self.rear_light_pin = rear_light_pin
        self.steering_pin = steering_pin
        self.speed_pin = speed_pin
        self.hz = hz

        self.initialize_gpio()

    def control_steering(self, steering_input):
        self.steering.ChangeDutyCycle(steering_input)
        time.sleep(5)
        self.steering.stop()
        gpio.cleanup()

    def control_speed(self, speed_input):
        # Control motor speed from duty cycle (map 2.5 to 12.5)
        self.speed.ChangeDutyCycle(speed_input)

    def brake_is_on(self, state):
        # Open rear lights when brakes are applied
        gpio.output(self.rear_light_pin, int(state))

    def initialize_gpio(self):
        # Setup TINKERBOARD GPIO's
        gpio.setwarnings(False)
        gpio.setmode(gpio.BOARD)

        # Setup GPIO inputs and outputs
        gpio.setup(self.rear_light_pin, gpio.OUT)
        gpio.setup(self.steering_pin, gpio.OUT)
        gpio.setup(self.speed_pin, gpio.OUT)

        # Outputs controls
        self.steering = gpio.PWM(self.steering_pin, self.hz)
        self.steering.start(2.5)  # Start servo at 0 degrees

        self.speed = gpio.PWM(self.speed_pin, self.hz)
        self.speed.start(0)  # Initialize with 0 speed
