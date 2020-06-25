"""
created on thursday September 26 2019
last updated on friday June 22nd 2020
@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomedicales, UQAC
    Office: H2-1180
project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

from scipy import signal

import cv2
import numpy as np
import matplotlib.pyplot as plt


def data2path(view, intensity=170, pxl_to_mx=26, pxl_to_my=54, offset=15):
    x, y = np.where(view >= intensity)  # Discrete
    x = (-x + view.shape[0] + offset) / pxl_to_mx  # Mirror data to counteract the top left corner
    y = (-y + (view.shape[1] / 2)) / pxl_to_my  # Idem
    try:
        x, y = list(zip(*sorted(zip(x, y), key=lambda k: k[0])))  # Sort and pair x and y data DARK MAGIC...
    except ValueError:
        return [0, 0, 0]

    # plt.plot(x, y, "c.")  # Show data for visual purpose, this should me removed later: To Be Removed (TBR)

    histogram = (np.sum(view[view.shape[0] // 2:, :], axis=0) / 1000)
    peaks, _ = signal.find_peaks(histogram, distance=0.8*pxl_to_my)  # Find histogram peaks AKA lines
    peaks = (-peaks + (view.shape[1])/2) / pxl_to_my
    # print(peaks)

    while len(peaks) > 2:
        # peaks = np.delete(peaks, np.where(peaks == max(peaks, key=lambda peak_pos: abs(peak_pos))))
        peaks = np.delete(peaks, np.where(peaks == max(peaks, key=lambda peak_pos: abs(abs(peak_pos) - 0.5))))

    # print("     ", peaks)

    lines_data = []
    for peak in peaks:  # For every detected lines
        last_theta = 0
        # plt.plot(offset/pxl_to_mx, peak, "go")
        lst = [(offset/pxl_to_mx, peak)]
        for i, this_y in enumerate(y):
            n = x[i]-lst[-1][0]
            if n != 0:
                theta = abs(np.degrees(np.arctan((this_y-lst[-1][1])/n)))
                if theta < 15:
                    last_theta += theta
                    lst.append(np.array([x[i], this_y]))  # Add point to list
                    # plt.plot(x[i], this_y, "r.")

            """if abs(this_y - ((lst[-1][1] - peak) / (lst[-1][0]) * x[i] + peak)) < proximity:  # If v is within thresh
                lst.append(np.array([x[i], this_y]))  # Add point to list
                plt.plot(x[i], this_y, "g.")"""
        lines_data.append(list(zip(*lst)))  # Sort in x, y lists


    """lines_data = []
    for index, val in enumerate(peaks):  # For every peaks AKA lines
        init = (view.shape[1] / 2 - val) / pxl_to_mx
        lst = [(0.01, init)]  # 0.01 is a patch to avoid 0/0 case
        for i, v in enumerate(y):
            if abs(v - ((lst[-1][1] - init) / lst[-1][0] * x[i] + init)) < proximity:  # If v is within threshold
                lst.append(np.array([x[i], v]))  # Add point to list
        lines_data.append(list(zip(*lst)))  # Sort in x, y lists"""

    poly_lines = []
    for data in lines_data:
        x, y = data
        poly_lines.append(np.polyfit(x, y, 2))
    poly_lines = np.array(poly_lines)

    case = len(poly_lines)
    if case == 0:
        return [0, 0, 0]  # Modify to old trajectory
    elif case == 1:
        poly_lines[0][2] -= np.sign(peaks[0])*0.46
        return poly_lines[0]  # Car last error is added
    elif case == 2:
        return (poly_lines[0] + poly_lines[1]) / 2


def get_vp_polygon(frame):  # Camera position dependant
    return [[0.0, 1.0 * frame.shape[0]],  # lower left
            [0.42 * frame.shape[1], 0.0],  # upper left
            [0.58 * frame.shape[1], 0.0],  # upper right
            [1.0 * frame.shape[1], 1.0 * frame.shape[0]]]  # lower right


def unwarp(view, roi_corners):  # Region of Interest
    src = np.float32(roi_corners)

    warped_size = (view.shape[1], view.shape[0])
    offset = int(warped_size[0] / 3.0)
    dst = np.float32([[offset, warped_size[1]],
                      [offset, 0],
                      [warped_size[0] - offset, 0],
                      [warped_size[0] - offset, warped_size[1]]])

    perspective = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(view, perspective, dsize=warped_size)
    return warped


class LinesCamera:
    # Threshold and constants that can be adjusted to modify the result
    DARK = np.array([0, 0, 200])  # Dark white[h, s, v]
    BRIGHT = np.array([255, 255, 255])  # Light white[h, s, v]
    TOP = 320
    BOTTOM = -230

    webcam = None

    def __init__(self):
        self.webcam = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 960)  # 1600, 1600, 1280, 352
        self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # 1200, 1000,  720, 288
        plt.ion()

    def watch(self):
        # Read image and do prelim manipulation (rotate/convert color/unwarp)
        _, img = self.webcam.read()  # Get image from USB WebCam
        img = cv2.flip(cv2.flip(img, 0), 1)
        # img = cv2.imread("/home/pi/Desktop/calibration.png")
        img = img[self.TOP:self.BOTTOM]  # Cut to fit region of interest (up and down borders)
        img = cv2.resize(img, (0, 0), fx=0.3125, fy=1)
        # cv2.imwrite("/home/pi/Desktop/cut.png", img)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # Create an HSV image version
        unwarped = unwarp(hsv, get_vp_polygon(hsv))  # Remove image perspective
        # Line analysis by color
        inkblot = cv2.inRange(unwarped, self.DARK, self.BRIGHT)  # Setup a color mask
        # cv2.imwrite("/home/pi/Desktop/inkblot.png", inkblot)
        inkblot = cv2.erode(inkblot, np.ones((5, 5), np.uint8), iterations=1)  # Cleaning noise with erode function
        inkblot = cv2.resize(inkblot, (0, 0), fx=0.455, fy=0.588)  # Discretize data
        inkblot = inkblot[50:]
        # cv2.imwrite("/home/pi/Desktop/inkblotsmall.png", inkblot)
        objective = data2path(inkblot)  # Get objective path from data
        # objective = (lines[0] + lines[1]) / 2  # Mean function is the imaginary center line
        """X = np.linspace(0, 4, 40)  # Voir pxl_to_mx pour 27
        plt.plot(X, np.poly1d(objective)(X), "g-")
        plt.axis("equal")
        plt.show()
        plt.pause(0.00001)
        plt.clf()
        # print(objective)"""
        return objective

    def end_sequence(self):
        self.webcam.release()
