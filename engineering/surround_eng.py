"""
created on thursday September 26 2019
last updated on wednesday November 13 2019

@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomedicales, UQAC
    Office: H2-1180

project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""


# from management import Management
# from inputs.safety import Safety
# from inputs.surround_sensor import SurrEng
from inputs.lines_camera import LinesCamera


class SurroundEng:

    lines = None

    def __init__(self):
        self.line_cam = LinesCamera()

    def request_lines_cam_data(self):
        self.lines = self.line_cam.watch()

        return self.lines

    """def request_safety_checks(self):
        state = 
        
        return state"""