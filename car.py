"""
created on thursday September 26 2019
last updated on friday June 19th 2020
@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomedicales, UQAC
    Office: H2-1180
project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

from engineering.distancecontrol import DistanceController
from engineering.steeringcontrol import SteeringController
from communication.publisher import Publisher

import csv
import time
import getch
import socket
import numpy as np


def rad_to_pulse(delta):
    return -1.1459 * delta + 1.5


def mps_to_apw(v):
    return 0.0459 * v + 1.577


def apw_to_mps(apw):
    return 21.789 * apw - 34.364


def is_connected():
    if socket.gethostbyname(socket.gethostname()) == "127.0.0.1":
        return False
    else:
        return True


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


class Car:

    file = 0

    dt = 0
    de = 0

    lf = 0.13  # Distance from front axle to CM
    lr = 0.13  # Distance from rear axle to CM
    stance = 0.0635  # Distance from center line to spindle

    Ddel_max = 5  # Max steering angle input change
    del_max = 22  # Max steering angle
    del_inc = 1  # Steering input increment size

    R1 = None  # Rear wheels rotation radius
    R0 = None  # Mass center rotation radius

    v = 0.0  # m/s  speed
    delta = 0.0  # degrees
    e = 0.01  # m

    psi = 0.0  # Car relative yaw

    apw = 1.45  # Accelerator pulse width
    is_go = False
    mode = None  # 1, 2 or 3 for lead, kb ctrl and follow modes
    max_event = 5  # Maximum consecutive image analysis clipping event

    # Data logging
    EPSI = ["e psi [rad]"]
    E = ["e [m]"]
    CLIPPING_EVENTS = ["Clipping events"]
    STEERING = ["Steering [s]"]
    DELTA = ["Delta [deg]"]
    THROTTLE = ["Throttle [s]"]

    first_time = True

    def __init__(self):
        # Generate Rear wheel rotation radius database
        self.R1 = [(self.lr + self.lf + (self.stance/np.tan(np.pi/2 - a))) * np.tan(np.pi/2 - a) for a in
                   np.linspace(np.radians(self.del_inc), np.radians(self.del_max), int(self.del_max / self.del_inc))]
        self.R0 = [np.sqrt(r ** 2 + self.lr ** 2) for r in self.R1]  # Generate Front wheel rotation radius database

        self.steer_ctrlr = SteeringController(self)  # Create new steering controller instance (USES PID OR PMPC)
        self.dist_ctrlr = DistanceController(self)  # Create new distance controller instance (USES PID)
        self.publisher = Publisher()  # Create new publisher instance
        self.file = open("/home/pi/PycharmProjects/Master/data1.txt", "w")
        print("VAALERIE IS READY")
        self.init_mode()

    def init_mode(self):
        print("PLEASE SELECT CONTROL MODE :")
        print("[1] LEAD MODE, [2] KEYBOARD CONTROL MODE or [3] FOLLOW MODE")
        self.set_mode(input())

    def set_mode(self, mode):
        self.mode = mode
        if self.mode == '1':
            self.lead_init_sequence()
        elif self.mode == '2':
            self.keyboard_ctrl()
        elif self.mode == '3':
            self.follow()
        else:
            self.init_mode()

    def steer(self, output):
        self.publisher.steering_publication(rad_to_pulse(np.radians(output)))
        self.delta = output

    def throttle(self, output):
        self.publisher.throttle_publication(output)
        self.apw = output
        self.v = apw_to_mps(self.apw)

    def speedup(self, desired_output):
        if self.apw < desired_output:
            self.publisher.throttle_publication(self.apw + 0.005)  # To be modified
            self.apw = desired_output + 0.005
            self.v = apw_to_mps(self.apw)
        elif self.apw > desired_output:
            self.publisher.throttle_publication(self.apw - 0.005)  # To be modified
            self.apw = desired_output - 0.005
            self.v = apw_to_mps(self.apw)
        else:
            self.publisher.throttle_publication(self.apw)
            self.apw = desired_output
            self.v = apw_to_mps(self.apw)

    def set_state(self, path):
        self.e = -np.polyval(path, 0)  # Prevision
        self.psi = -np.arctan(np.polyval(np.polyder(path), 0))

    def lead(self, speed):
        print("LEADING...")
        event = 0
        loop = 0
        while is_connected() and self.is_go:
            try:
                # d = self.steer_ctrlr.steering_PMPC()
                d = self.steer_ctrlr.steering_PID()
                self.steer(d)
                self.speedup(speed)
                event = 0
                #self.log()

            except IndexError or TypeError or ValueError:  # Clipping event
                print("CLIPPING EVENT, {}")
                if event < self.max_event:
                    event += 1
                else:
                    print("NO LINES COULD BE FIND", self.max_event+1, "TIMES IN A ROW...")
                    print("ENDING SEQUENCE")
                    break
            except KeyboardInterrupt:
                self.publisher.general_publication(1.50, 1.45)
                raise
                break
        self.end_sequence()

    def keyboard_ctrl(self):
        print("KEYBOARD CONTROL MODE")
        print("USE :       |W|")
        print()
        print("      | A|  |S|  |D|")
        print("TO CONTROL VAALERIE")
        print("PRESS 'Q' OR 'ESC' TO STOP")

        self.is_go = True

        while self.is_go and is_connected():
            k = getch.getch()
            if k == 'w':
                self.apw += 0.005
                self.publisher.throttle_publication(self.apw)
                print(self.apw)
            elif k == 's':
                self.apw -= 0.005
                self.publisher.throttle_publication(self.apw)
            elif k == 'a':
                self.delta += 2
                self.publisher.steering_publication(rad_to_pulse(np.radians(clamp(self.delta, -self.del_max, self.del_max))))
                print(self.delta)
            elif k == 'd':
                self.delta -= 2
                self.publisher.steering_publication(rad_to_pulse(np.radians(clamp(self.delta, -self.del_max, self.del_max))))
            elif k == 'q' or '^[':
                self.is_go = False
                break
            else:
                continue
        self.publisher.general_publication(1.50, 1.45)

    def follow(self):
        self.is_go = True
        while is_connected() and self.is_go:
            try:
                d = self.steer_ctrlr.steering_PID()
                t = self.dist_ctrlr.distance_PID()
                self.throttle(t)
                self.steer(d)
                self.file.write(str(self.de) + "," + str(self.e) + ","
                                + str(t) + "," + str(d) + "," + str(self.dt) + '\n')
                self.dt = 0
            except KeyboardInterrupt:
                self.publisher.general_publication(1.50, 1.45)
                raise
        self.publisher.general_publication(1.50, 1.45)

    def get_steering_range(self):
        lb = self.delta - self.Ddel_max  # delta - 15 (degrees)
        if lb < -self.del_max:  # 25 degrees limit
            lb = -self.del_max

        ub = self.delta + self.Ddel_max + self.del_inc  # delta + 15 (degrees)
        if ub > self.del_max:  # 25 degrees limit
            ub = self.del_max + self.del_inc

        return np.arange(lb, ub, self.del_inc)

    def lead_init_sequence(self):
        print("ENTER THE DESIRED LEADING SPEED [m/s]:")
        desired_speed = float(input())
        print("VAALERIE WILL LEAD AT :", desired_speed, "m/s")
        time.sleep(1)
        """print("STOP VAALERIE AT ANY POINT BY PRESSING 'Q' OR 'ESC'")
        time.sleep(4)
        print("READY IN:")
        time.sleep(1)
        print("3")
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1")
        time.sleep(1)
        print("GO!")"""
        self.is_go = True
        self.lead(mps_to_apw(desired_speed))

    def end_sequence(self):
        self.publisher.general_publication(1.50, 1.45)
        self.steer_ctrlr.line_cam.end_sequence()
        self.file.close()


# Initializing sequence code
if __name__ == '__main__':
    car = Car()
    # car.keyboard_ctrl()
