"""
created on thursday September 26 2019
last updated on tuesday April 30th 2020
@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomedicales, UQAC
    Office: H2-1180
project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

import busio
from adafruit_lidarlite import *


class LidarLiteV3:

    SCL = 3
    SDA = 2
    last_dist = None
    lidar = None

    def __init__(self):
        i2c = busio.I2C(self.SCL, self.SDA)  # Create library object using our Bus I2C port
        self.lidar = LIDARLite(i2c, configuration=CONFIG_HIGHSENSITIVE)  # High sens. configuration, with i2c wires

    def get_distance(self):
        return self.lidar.distance

    def set_last_distance(self, d):
        self.last_dist = d
