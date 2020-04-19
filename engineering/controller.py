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


class Controller:

    lines = None

    # Pseudo-MPC parameters
    N = 12  # Horizon
    dt = 0.1  # s

    # Weights
    w_e = 4  # 24
    w_e_psi = 5  # 5

    # P.I.D. controller parameters
    p = 22  # To be modified
    i = 0.8
    d = 0.1

    e0 = None
    se = 0.0

    def __init__(self):
        self.line_cam = LinesCamera()
        self.safety = Safety()

    def steering_PID(self, car):  # PID control
        path = self.line_cam.watch()
        car.set_state(path)
        p = self.p
        i = self.i
        d = self.d
        self.se += car.e
        delta = p*car.e + i*self.se
        if self.e0:
            delta += d*(car.e - self.e0)/self.dt
        self.e0 = car.e

        if np.abs(delta) > car.del_max:
            delta = np.sign(delta)*car.del_max
        s = -np.sign(delta)
        return s*np.ceil(np.abs(delta))

    def steering_PMPC(self, car):  # Pseudo-MPC
        path = self.line_cam.watch()
        car.set_state(path)
        dlt_rng = car.get_steering_range()
        J = np.zeros(len(dlt_rng))  # Error function
        e_psif, e_f = [], []

        for index, dlt in enumerate(dlt_rng):
            if dlt == 0.0:
                xf = car.v*self.dt
                e_f.append(- np.polyval(path, xf))
                e_psif.append(- np.polyval(np.polyder(path), xf))
            else:
                s = np.sign(dlt)  # sign +1 or -1
                dlt = abs(dlt)
                i = int(dlt - 1)  # Index for pre processed steering data
                R0 = car.R0[i]  # Get turning radius from input
                psi = car.v/R0*self.dt
                L = 2*R0*np.sin(psi/2)
                theta = np.arctan(car.lr/car.R1[i])
                xf = L*np.cos(theta + psi/2)
                yf = s*L*np.sin(theta + psi/2)

                e_f.append(yf - np.polyval(path, xf))
                e_psif.append(s*psi - np.polyval(np.polyder(path), xf))

            J[index] = (self.w_e * e_f[index]) ** 2 + (self.w_e_psi * e_psif[index]) ** 2

        min_val_index = int(np.argmin(J))
        delta = dlt_rng[min_val_index]

        return delta

    def request_safety_checks(self):
        return self.safety.state

    """def simple_solve(self, car):
        path = self.line_cam.watch()
        car.set_state(path)
        print("y=", car.y, "psi=", np.degrees(car.psi))
        v = car.v
        dlt_rng = car.get_steering_range()
        print(np.degrees(dlt_rng))
        J = np.zeros(len(dlt_rng))  # Error function
        e_psif, ef = [],  []

        for index, dlt in enumerate(dlt_rng):
            # Future position
            dlt = np.radians(dlt)
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
        print(np.degrees(delta))
        return [delta, v]"""
