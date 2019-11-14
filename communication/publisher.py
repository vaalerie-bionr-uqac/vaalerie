"""
created on thrusday September 26 2019

@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomediacles, UQAC
    Office: H2-1180

project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

from outputs import display, guidance

from outputs.guidance import Guidance
from outputs.display import Display


class Publisher:

    # Initialize Tinkerboard GPIO pins
    guidance = Guidance(11, 33, 32, 50)
    display = Display()

    def general_publication(self, steering_input, speed_input):
        self.guidance.control_steering(steering_input)
        self.guidance.control_speed(speed_input)
        self.guidance.brake_is_on(True)
        self.display.emotion_factor = 0
        # Publishing values to Bluetooth
