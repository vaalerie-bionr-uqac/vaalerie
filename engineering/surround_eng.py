"""
created on thursday September 26 2019
last updated on wednesday November 13 2019

@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomedicales, UQAC
    Office: H2-1180

project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

# from management import Management
from inputs.safety import Safety
# from inputs.surround_sensor import SurrEng
from inputs.lines_camera import LinesCamera
import numpy as np


class SurroundEng:

    lines = None

    # Model parameters
    N = 12  # Horizon
    dt = 0.1  # s
    Lf = 0.125  # m

    # Weights
    w_e = 5  # 24
    w_e_psi = 4  # 5

    def __init__(self):
        self.line_cam = LinesCamera()
        self.safety = Safety()

    def simple_solve(self, car):
        path = self.line_cam.watch()
        car.set_state(path)
        v = car.get_speed()
        dlt_rng = car.get_steering_range()
        J = np.zeros(len(dlt_rng))  # Error function
        e_psif, ef = [],  []

        for index, dlt in enumerate(dlt_rng):
            # Future position
            beta = np.arctan(0.5 * np.tan(dlt))  # lf/lf+lr = 0.5 -> RC car symmetry
            xf = v * np.cos(beta) * self.dt
            yf = v * np.sin(beta) * self.dt
            psif = v / (2 * self.Lf * np.tan(np.pi/2 - dlt)) * self.dt

            # Yaw error
            e_psif.append(psif - np.arctan(np.polyval(np.polyder(path), xf)))
            # Position error
            ef.append(yf - np.polyval(path, 0))  # VERIFY HERE

            J[index] = (self.w_e * ef[index]) ** 2 + (self.w_e_psi * e_psif[index]) ** 2

        min_val_index = int(np.argmin(J))

        delta = dlt_rng[min_val_index]

        return [delta, v]

    def request_lines_cam_data(self):
        return self.line_cam.watch()

    def request_safety_checks(self):
        return self.safety.state
