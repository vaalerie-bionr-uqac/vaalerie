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
import RPi.GPIO as GPIO


class Controller:

    lines = []
    objective = None
    speed = None
    steering = None
    isON = True
    motor_speed = 1.45
    steering_pos = 1.5
    position = [480, 320]

    def __init__(self):
        # Create new surroundings engineer instance
        self.surr_eng = SurroundEng()
        # Create new publisher instance
        self.publisher = Publisher()
        self.isON = True
        # Create new motion engineer instance !!!! ALERT - MUST BE CREATED !!!!
        # motion_eng = MotionEngineer()

    def control_loop(self):
        self.send_data_to_publisher()

        while self.surr_eng.request_safety_checks():
            # Collect data from surrounding
            #self.collect_surr_data()
            # Process output data w/ MPC
            #self.mpc()
            # Provide  publisher with output data
            k = raw_input()
            if k == 'w':
                self.motor_speed += 0.005
            elif k == 's':
                self.motor_speed -= 0.005
            elif k == 'a':
                self.steering_pos -= 0.05
            elif k == 'd':
                self.steering_pos += 0.05
            elif k == 'q':
                self.motor_speed = 1.45
                self.isON = False
            self.send_data_to_publisher()

    def rabbit_mpc(self):
        for line in self.lines:
            print(str(line[0]) + ',' + str(line[1]))

    def send_data_to_publisher(self):
        # Push data to publisher
        # Data will be computed from this object after getting data from engineers
        self.publisher.general_publication(self.steering_pos, self.motor_speed)

    def collect_surr_data(self):
        # Collect data from surround engineer
        self.lines = self.surr_eng.request_lines_cam_data()
        # Collect data from motion engineer
        # self.motion_eng.


# Initializing sequence code
if __name__ == '__main__':
    controller = Controller()
    controller.control_loop()
