
from engineering import motion_eng


class AthleteCameras:

    faces = []
    reference_points = []
    runner_position_x = 0
    runner_position_y = 0
    runner_rel_speed_x = 0
    runner_rel_speed_y = 0

    def __init__(self):
        self.faces = []

    def learn_faces(self, face):
        self.faces.append(face)