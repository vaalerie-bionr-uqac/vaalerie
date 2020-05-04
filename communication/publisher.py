"""
created on thrusday September 26 2019

@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomediacles, UQAC
    Office: H2-1180

project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

from outputs.guidance import Guidance


class Publisher:

    guidance = Guidance(100)

    def general_publication(self, steering, throttle):
        self.guidance.control_steering(steering)
        self.guidance.control_throttle(throttle)
        self.guidance.brake_is_on(True)

    def steering_publication(self, steering):
        self.guidance.control_steering(steering)

    def throttle_publication(self, throttle):
        self.guidance.control_throttle(throttle)
