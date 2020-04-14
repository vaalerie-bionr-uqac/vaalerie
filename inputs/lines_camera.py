"""
created on thursday September 26 2019
last updated on tuesday April 9th 2020
@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomedicales, UQAC
    Office: H2-1180
project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

import matplotlib.pyplot as plt
import numpy as np
import cv2

from scipy import signal


def sort_lines(view, proximity=5, intensity=170):
    x, y = np.where(view >= intensity)  # Discrete
    x = -x + view.shape[0]  # Mirror data to counteract the top left corner
    y = -y + (view.shape[1] / 2)  # Idem
    x, y = list(zip(*sorted(zip(x, y), key=lambda k: k[0])))  # Sort and pair x and y data MAGIE NOIRE...

    # plt.plot(x, y, "r.")  # Show data for visual purpose, this should me removed later: To Be Removed (TBR)

    histogram = (np.sum(view[view.shape[1] // 2:, :], axis=0) / 1000)
    peaks, _ = signal.find_peaks(histogram, distance=40)  # Find histogram peaks AKA lines

    lines_data = []
    for index, val in enumerate(peaks):  # For every peaks AKA lines
        init = view.shape[1] / 2 - val
        lst = [(0.01, init)]  # 0.01 is a patch to avoid 0/0 case
        for i, v in enumerate(y):
            if abs(v - ((lst[-1][1] - init) / lst[-1][0] * x[i] + init)) < proximity:  # If v is within threshold
                lst.append(np.array([x[i], v]))  # Add point to list
        lines_data.append(list(zip(*lst)))  # Sort in x, y lists

    poly_lines = []
    for data in lines_data:
        x, y = data
        poly_lines.append(np.polyfit(x, y, 2))

    return np.array(poly_lines)


def get_vp_polygon(frame):  # Camera position dependant
    return [[0.0, 1.0 * frame.shape[0]],  # lower left
            [0.424 * frame.shape[1], 0.0],  # upper left
            [0.56 * frame.shape[1], 0.0],  # upper right
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

    # Threshold and constants ta=hats can be adjusted to modify the result
    dark = np.array([0, 0, 205])  # Dark white[h, s, v]
    bright = np.array([255, 255, 255])  # Light white[h, s, v]
    top = 425
    bottom = -175

    def __init__(self):
        # Initialize video capture from port 0 w/ file path
        # '/dev/v4l/by-path/platform-ff540000.usb-usb-0:1.4:1.0-video-index0'
        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # On Windows

    def watch(self):
        # Import image and do prelim manipulation (resize/convert color/unwarp)
        # _, img = self.camera.read()  # Get image from USB WebCam
        img = cv2.imread('inputs\longstraight.png')  # Read image
        img = img[self.top:self.bottom]  # Cut to fit region of interest (up and down borders)
        img = cv2.resize(img, (0, 0), fx=0.25, fy=1)  # Resize image (thinner and longer)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # Create an HSV image version
        unwarped = unwarp(hsv, get_vp_polygon(hsv))  # Remove image perspective
        # Line analysis by color
        inkblot = cv2.inRange(unwarped, self.dark, self.bright)  # Setup a color mask
        inkblot = cv2.erode(inkblot, np.ones((5, 5), np.uint8), iterations=1)  # Cleaning noise with erode function
        inkblot = cv2.resize(inkblot, (0, 0), fx=0.25, fy=0.25)  # Pixel the sh*% out of it
        lines = sort_lines(inkblot)  # Sort data to extrapolate lines
        objective = (lines[0] + lines[1]) / 2  # Mean function is the imaginary center line
        # X = np.linspace(0, inkblot.shape[1], inkblot.shape[1])
        # plt.plot(X, np.poly1d((lines[0] + lines[1]) / 2)(X), "g-")
        # plt.axis("equal")
        # plt.show()
        return objective


"""if __name__ == '__main__':
    cam1 = LinesCamera()
    obj = cam1.watch()
    print(obj)"""
