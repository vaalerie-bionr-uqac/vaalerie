"""
created on thursday September 26 2019
last updated on wednesday November 13 2019

@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomedicales, UQAC
    Office: H2-1180

project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""
from communication.publisher import Publisher
# from engineering.motion_eng import MotionEngineer
from engineering.surround_eng import SurroundEng
import cv2


class Controller:

    lines = []
    objective = None
    speed = None
    steering = None
    isON = True
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
        while self.isON:
            # Collect data from surrounding
            #self.collect_surr_data()
            # Process output data w/ MPC
            #self.mpc()
            # Provide  publisher with output data
            self.send_data_to_publisher()
            self.isON = False

    def mpc(self):
        self.speed = self.publisher.guidance.speed
        self.steering = self.publisher.guidance.steering

        for line in self.lines:
            print(str(line[0]) + ',' + str(line[1]))

    def send_data_to_publisher(self):
        # Push data to publisher
        # Data will be computed from this object after getting data from engineers
        self.publisher.general_publication(0.52, 1.5)

    def collect_surr_data(self):
        # Collect data from surround engineer
        self.lines = self.surr_eng.request_lines_cam_data()
        # Collect data from motion engineer
        # self.motion_eng.


# Initializing sequence code
if __name__ == '__main__':
    controller = Controller()
    controller.control_loop()
