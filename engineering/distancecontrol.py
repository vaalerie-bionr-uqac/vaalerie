

# from inputs import athlete_cameras
from inputs.lidar import LidarLiteV3

import time
import numpy as np


class DistanceController:

    lidar = None
    car = None
    subject_distance = None
    err_list = []
    goal = 140
    integral = 0
    first_iteration = True
    then = None

    P = 0.009  # 0.008
    I = 0.0
    D = 0.0003  # 0.00000005

    def __init__(self, car):
        self.lidar = LidarLiteV3()
        self.car = car

    def distance_PID(self):
        now = time.time()
        dt = None
        try:
            e = self.lidar.get_distance() - self.goal
        except RuntimeError:
            print("RuntimeError")
            return 1.45
        self.err_list.append(e)
        if e > (1.5*self.goal) or e < (-0.75*self.goal):
            apw = 0.0

        elif self.first_iteration:
            apw = self.P * self.err_list[-1]
            self.first_iteration = False
        else:
            dt = now - self.then
            self.integral += e * dt
            apw = self.P * self.err_list[-1] + \
                  self.I * self.integral + \
                  self.D * (self.err_list[-1] - self.err_list[-2]) / dt

        self.then = now
        print(e, ",", max(min(apw, 0.3), 0.0) + 1.45, ",", dt)

        return max(min(apw, 0.3), 0.0) + 1.45