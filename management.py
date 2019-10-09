"""
created on friday September 27 2019

@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomediacles, UQAC
    Office: H2-1180

project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

from communication.publisher import Publisher
# from engineering.motion_eng import MotionEngineer
from engineering.surround_eng import SurroundEng


class Management:

    def __init__(self):
        # Create new publisher instance
        self.publisher = Publisher()
        # Create new motion engineer instance !!!! ALERT - MUST BE CREATED !!!!
        # motion_eng = MotionEngineer()
        # Create new surroundings engineer instance
        self.surr_eng = SurroundEng()

    def send_data_to_publisher(self):
        # Push data to publisher
        # Data will be computed from this object after getting data from engineers
        self.publisher.general_publication(7)


# Initializing sequence code
if __name__ == '__main__':
    manager = Management()
    manager.send_data_to_publisher()
