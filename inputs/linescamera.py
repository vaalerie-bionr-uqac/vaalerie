"""
created on thursday September 26 2019
last updated on friday June 26nd 2020
@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomedicales, UQAC
    Office: H2-1180
project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

from scipy import signal

import cv2
import numpy as np


def capture2objective(view, intensity=170, pxl_to_mx=26, pxl_to_my=54, offset=15):
    x, y = np.where(view >= intensity)  # Discard dim pixels
    x = (-x + view.shape[0] + offset) / pxl_to_mx  # Manipulate data to generate a 1 to 1m correspondence on x axis
    y = (-y + (view.shape[1] / 2)) / pxl_to_my  # Idem
    try:
        x, y = list(zip(*sorted(zip(x, y), key=lambda k: k[0])))  # Sort and pair x and y data DARK MAGIC...
    except ValueError:
        return [0, 0, 0]

    histogram = (np.sum(view[view.shape[0] // 2:, :], axis=0) / 1000)
    for i in range(50, 87):  # Discard middle lane writings (RAPIDE, LENT, 1 ,2, 3, 4)
        histogram[i] = 0
    peaks, _ = signal.find_peaks(histogram, distance=0.8*pxl_to_my)  # Find histogram peaks AKA lines
    peaks = (-peaks + (view.shape[1])/2) / pxl_to_my  # Set 1 to 1m correspondence

    while len(peaks) > 2:  # Discard unrelated peaks
        peaks = np.delete(peaks, np.where(peaks == max(peaks, key=lambda peak_pos: abs(abs(peak_pos) - 0.5))))

    data_points = []
    for peak in peaks:  # Sort and filter data for left and right lines
        last_theta = 0
        lst = [(offset/pxl_to_mx, peak)]
        for i, this_y in enumerate(y):
            n = x[i]-lst[-1][0]
            if n != 0:
                theta = abs(np.degrees(np.arctan((this_y-lst[-1][1])/n)))
                if theta < 15:
                    last_theta += theta
                    lst.append(np.array([x[i], this_y]))  # Add point to list
        data_points.append(list(zip(*lst)))  # Sort in x, y lists

    polynomials = []
    for point in data_points:  # Generate 2nd degree polynomial functions to interpret visible lines
        x, y = point
        polynomials.append(np.polyfit(x, y, 2))
    polynomials = np.array(polynomials)

    case = len(polynomials)  # Set objective in correlation to the number of detected lines
    if case == 0:  # No lines
        return [0, 0, 0]  # Modify to old trajectory
    elif case == 1:  # 1 line
        polynomials[0][2] -= np.sign(peaks[0])*0.46
        return polynomials[0]  # Car last error is added
    elif case == 2:  # 2 lines (nominal)
        return (polynomials[0] + polynomials[1]) / 2


def get_vp_polygon(frame):  # Perspective polygon of the specified camera
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
        self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def watch(self):
        # Read image and do prelim manipulation (rotate/convert color/unwarp)
        _, img = self.webcam.read()  # Get image from USB WebCam
        img = cv2.flip(cv2.flip(img, 0), 1)
        img = img[self.TOP:self.BOTTOM]  # Cut to fit region of interest (up and down borders)
        img = cv2.resize(img, (0, 0), fx=0.3125, fy=1)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # Create an HSV image version
        unwarped = unwarp(hsv, get_vp_polygon(hsv))  # Remove image perspective
        # cv2.imwrite("/home/pi/Desktop/test.png", unwarped)
        inkblot = cv2.inRange(unwarped, self.DARK, self.BRIGHT)  # Setup a color mask
        inkblot = cv2.erode(inkblot, np.ones((5, 5), np.uint8), iterations=1)  # Cleaning noise with erode function
        inkblot = cv2.resize(inkblot, (0, 0), fx=0.455, fy=0.588)  # Discretize data
        inkblot = inkblot[50:]
        objective = capture2objective(inkblot)  # Get objective path from data

        return objective

    def end_sequence(self):
        self.webcam.release()
