
from engineering import motion_eng


class Lidar:

    position_x = 0
    position_y = 0
    #
    theta_1 = 0
    theta_2 = 0

    runner_dist = 0

    def __init__(self):
        self.position_x = 0
        self.position_y = 0
        self.theta_1 = 0
        self.theta_2 = 0

        self.runner_dist = 0