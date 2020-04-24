"""
created on thursday September 26 2019
last updated on wednesday November 13 2019

@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomedicales, UQAC
    Office: H2-1180

project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

from inputs.safety import Safety
from inputs.lines_camera import LinesCamera

from datetime import datetime
import numpy as np


class SteeringController:

    lines = None

    # Pseudo-MPC parameters
    N = 12  # Horizon
    then = None

    # Weights
    w_e = 4  # 24
    w_e_psi = 5  # 5

    # P.I.D. controller parameters
    p = 22  # To be modified
    i = 0.8
    d = 0.1

    e0 = None
    se = 0.0

    car = None

    def __init__(self, car):
        self.line_cam = LinesCamera()
        self.safety = Safety()
        self.car = car

    def set_dt(self):
        if self.then is None:
            return 0.1
        else:
            return datetime.now() - self.then

    def steering_PID(self):  # PID control
        path = self.line_cam.watch()
        self.car.set_state(path)
        p = self.p
        i = self.i
        d = self.d
        self.se += self.car.e
        delta = p*self.car.e + i*self.se
        if self.e0:
            delta += d*(self.car.e - self.e0)/self.dt
        self.e0 = self.car.e

        if np.abs(delta) > self.car.del_max:
            delta = np.sign(delta)*self.car.del_max
        s = -np.sign(delta)

        return s*np.ceil(np.abs(delta))

    def steering_PMPC(self):  # Pseudo-MPC
        dt = self.set_dt()
        path = self.line_cam.watch()
        self.car.set_state(path)
        dlt_rng = self.car.get_steering_range()
        J = np.zeros(len(dlt_rng))  # Error function
        e_psif, e_f = [], []

        for index, dlt in enumerate(dlt_rng):
            if dlt == 0.0:
                xf = self.car.v*dt
                e_f.append(- np.polyval(path, xf))
                e_psif.append(- np.polyval(np.polyder(path), xf))
            else:
                s = np.sign(dlt)  # sign +1 or -1
                dlt = abs(dlt)
                i = int(dlt - 1)  # Index for pre processed steering data
                R0 = self.car.R0[i]  # Get turning radius from input
                psi = self.car.v/R0*dt
                L = 2*R0*np.sin(psi/2)
                theta = np.arctan(self.car.lr/self.car.R1[i])
                xf = L*np.cos(theta + psi/2)
                yf = s*L*np.sin(theta + psi/2)

                e_f.append(yf - np.polyval(path, xf))
                e_psif.append(s*psi - np.polyval(np.polyder(path), xf))

            J[index] = (self.w_e * e_f[index]) ** 2 + (self.w_e_psi * e_psif[index]) ** 2

        min_val_index = int(np.argmin(J))
        delta = dlt_rng[min_val_index]

        self.then = datetime.now()

        return delta

    def request_safety_checks(self):
        return self.safety.state
