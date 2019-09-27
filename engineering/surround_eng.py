
# from management import Management
# from inputs.safety import Safety
# from inputs.surround_sensor import SurrEng
from inputs.lines_camera import LinesCamera


class SurroundEng:

    def __init__(self):
        self.lc = LinesCamera()

    def request_lines_cam_data(self):
        self.lc.watch()
