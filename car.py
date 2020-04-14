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
from engineering.surround_eng import SurroundEng
# import RPi.GPIO as GPIO
import numpy as np


def rad_to_pulse(delta):
    return 2.107 * delta + 0.92


def speed_to_throttle(v):
    return 0.0423 * v + 1.45


class Car:

    dD_MAX = 5
    D_MAX = 25
    D_step = 1

    L = 0.5
    w = 0.18

    v = 0  # m/s
    y = 0  # m
    delta = 0.0  # rad
    psi = np.pi/3  # rad
    beta = np.arctan(0.5 * np.tan(delta))  # rad
    e_psi = 0.0  # rad
    e = 0.0  # m

    lines = []
    throttle = 1.45
    steering_pos = 1.5

    def __init__(self):
        # Create new surroundings engineer instance
        self.surr_eng = SurroundEng()
        # Create new publisher instance
        self.publisher = Publisher()
        # Create new motion engineer instance !!!! ALERT - MUST BE CREATED !!!!
        # motion_eng = MotionEngineer()

    def lead(self):
        while self.surr_eng.request_safety_checks():
            actions = self.surr_eng.simple_solve(self)
            self.apply_actions(actions)
            # Data will be computed from this object after getting data from engineers
            # self.publisher.general_publication(self.steering_pos, self.throttle)
            break

    def apply_actions(self, actions):
        d, s = actions
        self.publisher.general_publication(rad_to_pulse(d), speed_to_throttle(s))
        self.delta = d
        self.v = s

    def set_state(self, path):
        self.y = -np.polyval(path, 0)
        self.e = self.y
        self.psi = -np.arctan(np.polyval(np.polyder(path), 0))

        while self.surr_eng.request_safety_checks():
            # Collect data from surrounding
            #self.collect_surr_data()
            # Process output data w/ MPC
            #self.mpc()
            # Provide  publisher with output data
            k = raw_input()
            if k == 'w':
                self.throttle += 0.005
            elif k == 's':
                self.throttle -= 0.005
            elif k == 'a':
                self.steering_pos -= 0.05
            elif k == 'd':
                self.steering_pos += 0.05
            elif k == 'q':
                self.throttle = 1.45
                self.isON = False
            self.send_data_to_publisher()

    #def send_data_to_publisher(self):
        # Push data to publisher
        # Data will be computed from this object after getting data from engineers
        # self.publisher.general_publication(self.steering_pos, self.throttle)

    def get_speed(self):
        return self.throttle  # Temporary, should be V from analysis

    def get_steering_range(self):
        lb = np.degrees(self.delta) - self.dD_MAX  # delta - 15 (degrees)
        if lb < -self.D_MAX:  # 25 degrees limit
            lb = -self.D_MAX

        ub = np.degrees(self.delta) + self.dD_MAX  # delta + 15 (degrees)
        if ub > self.D_MAX:  # 25 degrees limit
            ub = self.D_MAX - self.dD_MAX

        return np.arange(np.radians(lb), np.radians(ub), np.radians(self.D_step))  # WARNING !! VERIFY HERE


# Initializing sequence code
if __name__ == '__main__':
    car = Car()
    car.lead()
