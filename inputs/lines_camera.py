"""
created on thursday September 26 2019

@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomediacles, UQAC
    Office: H2-1180

project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

from engineering import surround_eng

import sys
import numpy as np
import cv2
import datetime

np.set_printoptions(threshold=sys.maxsize)


class LinesCamera:

    def __init__(self):
        # Initialize video capture from port 0 w/ file path
        self.cap = cv2.VideoCapture('/dev/v4l/by-path/platform-ff540000.usb-usb-0:1.4:1.0-video-index0')
        self.process_this_frame = False

    def continuous_watch(self):
        while True:
            # Only process every other frame of video to save time
            if self.process_this_frame:
                # Get image from USB webcam
                ret, frame = self.cap.read()
                # Find lines
                final_frame = self.get_lines_frame(frame)
                # Enlarge image
                final_frame = cv2.resize(final_frame, (0, 0), fx=4, fy=4)
                # Show image
                cv2.imshow('FWAME', final_frame)

            # 1 frame every 2 frame condition
            self.process_this_frame = not self.process_this_frame
            # Kill switch
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
        self.cap.release()

    def watch(self):
        # Get image from USB webcam
        frame = cv2.imread('piste_3.jpg')  # ret, frame = self.cap.read()
        # Find lines
        final_frame = self.get_lines_frame(frame)
        # Resize image
        final_frame = cv2.resize(final_frame, (0, 0), fx=4, fy=4)
        # Show image
        cv2.imwrite('houghlines3.jpg', final_frame)
        # Camera capture release
        # self.cap.release()

    def get_lines_frame(self, frame):
        # Cut received frame
        frame = frame[230:-80]
        # Resize frame to 1/4
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        # Color correction
        gray_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        # Contours
        edges_frame = cv2.Canny(gray_frame, 100, 100)
        # Find lines
        lines_frame = cv2.HoughLinesP(edges_frame, 1, np.pi / 180, 15, None, 10, 160)
        # Add lines to image frame
        final_frame = self.add_lines(lines_frame, small_frame)

        return final_frame

    def add_lines(self, lines_frame, small_frame):
        if lines_frame is not None:
            lines_frame = self.sort_lines(lines_frame)
            for i in range(0, len(lines_frame)):
                l = lines_frame[i][0]
                cv2.line(small_frame, (l[0], l[1]), (l[2], l[3]), (0, 255, 0), 1)

        return small_frame

    def find_lines(self, edges_frame, threshold=40, tolerance=2, cut=0):
        # Resize frame to desired value (horizontal cut)
        cut_frame = edges_frame[cut:]
        # Evaluate image in segments
        eval_frames = np.hsplit(edges_frame, (len(cut_frame[0])) / threshold)

        row_sum = []
        column_sum = []

        i = -1
        past = datetime.datetime.now()
        for f in eval_frames:
            i += 1
            correction = threshold * i
            # 1D rows and columns sum arrays
            for rows in f:
                row_sum.append(np.sum(rows))
            for columns in f.T:
                column_sum.append(np.sum(columns))

            # Scanning for lines
            for row in range(cut, len(f)):
                for column in range(0, len(f[row])):
                    # General matrix column position from relative f column position
                    general_column = column + correction
                    # is linear
                    if row_sum[row] != 0 and (f[row][column] / 255 * column_sum[column] / row_sum[row]) > tolerance:
                        cut_frame[row-cut][general_column] = 255
                    # is not
                    else:
                        cut_frame[row-cut][general_column] = 0

            del row_sum[:]
            del column_sum[:]
        print(datetime.datetime.now() - past)
        return cut_frame

    def sort_lines(self, lines_frame, threshold=5, slope=0.1):
        # Remove horizontal lines
        i = 0
        while i < len(lines_frame):
            x1, y1, x2, y2 = lines_frame[i][0]
            # Is horizontal
            if np.abs((y2 - y1)/(x2 - x1)) < slope:
                lines_frame = np.delete(lines_frame, i, 0)
            else:
                i += 1

        # Remove repetitions
        i, j = 0, 1
        while i < len(lines_frame):
            while j < len(lines_frame):
                if np.abs(np.mean(lines_frame[i][0] - lines_frame[j][0])) < threshold:
                    lines_frame = np.delete(lines_frame, j, 0)
                else:
                    j += 1
            i += 1

        return lines_frame


if __name__ == '__main__':
    line = LinesCamera()
    line.continuous_watch()
