"""
created on thursday September 26 2019
last updated on tuesday May 5th 2020
@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomedicales, UQAC
    Office: H2-1180
project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

from inputs.lidar import LidarLiteV3

import time


class DistanceController:
    lidar = None
    car = None
    subject_distance = None
    err_list = []
    goal = 175
    integral = 0
    first_iteration = True
    then = None

    P = 0.002  # 0.008
    I = 0.0
    D = 0.00  # 0.00000005

    def __init__(self, car):
        self.lidar = LidarLiteV3()
        self.car = car

    def distance_PID(self):
        now = time.time()
        dt = None
        try:
            e = self.lidar.get_distance() - self.goal
            self.car.de = e + 175
        except RuntimeError:
            return 1.45
        self.err_list.append(e)
        if e > (1.5 * self.goal) or e < (-0.75 * self.goal):
            apw = 0.0

        elif self.first_iteration:
            apw = self.P * self.err_list[-1]
            self.first_iteration = False
        else:
            dt = now - self.then
            self.car.dt += dt
            self.integral += e * dt
            apw = self.P * self.err_list[-1] + \
                  self.I * self.integral + \
                  self.D * (self.err_list[-1] - self.err_list[-2]) / dt
            # print(e + 175, ",", dt)

        self.then = now

        return max(min(apw, 0.3), 0.0) + 1.45
