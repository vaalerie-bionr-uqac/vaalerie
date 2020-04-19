"""
created on thursday September 26 2019
last updated on wednesday November 13 2019

@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomedicales, UQAC
    Office: H2-1180

project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

from pip._vendor.distlib.compat import raw_input

from communication.publisher import Publisher
# from engineering.motion_eng import MotionEngineer
from engineering.controller import Controller
import numpy as np


def rad_to_pulse(delta):
    return -1.1459 * delta + 1.5


def speed_to_throttle(v):
    return 0.0423 * v + 1.45


class Car:

    lf = 0.13  # Distance from front axle to CM
    lr = 0.13  # Distance from rear axle to CM
    stance = 0.0635  # Distance from center line to spindle

    Ddel_max = 5  # Max steering angle input change
    del_max = 22  # Max steering angle
    del_inc = 1  # Steering input increment size

    R1 = None  # Rear wheels rotation radius
    R0 = None  # Mass center rotation radius

    v = 0.5  # m/s  speed
    delta = 0.0  # degrees
    e = 0.0  # m

    psi = 0.0

    throttle = 1.45

    def __init__(self):
        # Generate Rear wheel rotation radius database
        self.R1 = [(self.lr + self.lf + (self.stance/np.tan(np.pi/2 - a))) * np.tan(np.pi/2 - a) for a in
                   np.linspace(np.radians(self.del_inc), np.radians(self.del_max), int(self.del_max / self.del_inc))]
        self.R0 = [np.sqrt(r ** 2 + self.lr ** 2) for r in self.R1]  # Generate Front wheel rotation radius database

        self.controller = Controller()  # Create new surroundings engineer instance
        self.publisher = Publisher()  # Create new publisher instance
        # motion_eng = MotionEngineer()  # Create new motion engineer instance

    def lead(self):
        while self.controller.request_safety_checks():
            d = self.controller.steering_PID(self)
            self.steer(d)

    def steer(self, delta):
        self.publisher.steering_publication(rad_to_pulse(np.radians(delta)))
        self.delta = delta

    def accelerate(self, throttle):
        self.publisher.throttle_publication(throttle)
        self.throttle = throttle

    def set_state(self, path):
        self.e = -np.polyval(path, 0)
        self.psi = -np.arctan(np.polyval(np.polyder(path), 0))

    def manual_ctrl_loop(self):
        while self.controller.request_safety_checks():
            # Provide  publisher with output data
            print(self.delta)
            k = raw_input()
            if k == 'w':
                self.throttle += 0.005
            elif k == 's':
                self.throttle -= 0.005
            elif k == 'a':
                self.delta -= 1
            elif k == 'd':
                self.delta += 1
            elif k == 'q':
                self.throttle = 1.45
                self.isON = False
            self.publisher.general_publication(rad_to_pulse(np.radians(self.delta)), self.throttle)

    # def send_data_to_publisher(self):
    # Push data to publisher
    # Data will be computed from this object after getting data from engineers
    # self.publisher.general_publication(self.steering_pos, self.throttle)

    def get_steering_range(self):
        lb = self.delta - self.Ddel_max  # delta - 15 (degrees)
        if lb < -self.del_max:  # 25 degrees limit
            lb = -self.del_max

        ub = self.delta + self.Ddel_max + self.del_inc  # delta + 15 (degrees)
        if ub > self.del_max:  # 25 degrees limit
            ub = self.del_max + self.del_inc

        return np.arange(lb, ub, self.del_inc)

# Initializing sequence code
if __name__ == '__main__':
    car = Car()
    print(car.delta)
    car.lead()
    print(car.delta)
