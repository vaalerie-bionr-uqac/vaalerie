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
import time

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
                # _____________
                ret, frame = self.cap.read()
                # Resize frame to 1/4
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                # Color correction
                gray_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                # contours
                edges_frame = cv2.Canny(gray_frame, 100, 100)

                # Find lines
                lines_frame = cv2.HoughLinesP(gray_frame, 1, np.pi / 180, 200)

                # for line in lines_frame:
                # x1, y1, x2, y2 = line[0]
                # cv2.line(edges_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                # Show image
                cv2.imshow('Potato', edges_frame)

                # self.find_lines(edges_frame)

                # np.savetxt('Straight_lines_matrix.txt', edges_frame, delimiter=',', fmt='%d')

            # 1 frame every 2 frame condition
            self.process_this_frame = not self.process_this_frame

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
        self.cap.release()

    def watch(self):
        time.sleep(2)
        # _____________
        ret, frame = self.cap.read()
        # Resize frame to 1/4
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        # Color correction
        gray_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        # contours
        edges_frame = cv2.Canny(gray_frame, 100, 100)

        # Find lines
        # lines_frame = cv2.HoughLinesP(gray_frame, 1, np.pi / 180, 200)

        # for line in lines_frame:
        # x1, y1, x2, y2 = line[0]
        # cv2.line(edges_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        # Show image
        # cv2.imshow('Potato', edges_frame)

        # self.find_lines(edges_frame)

        np.savetxt('Curved_lines_matrix.txt', edges_frame, delimiter=' ', fmt='%d')
        np.savetxt('Cleaned_lines_matrix.txt', self.find_lines(edges_frame), delimiter=' ', fmt='%d')

        # cv2.destroyAllWindows()
        self.cap.release()

    def find_lines(self, edges_frame, threshold=10, tolerance=5):
        # Evaluate image in segments
        eval_frames = np.hsplit(edges_frame, (len(edges_frame[0])) / threshold)

        row_sum = []
        column_sum = []

        i = -1
        for f in eval_frames:
            i += 1
            for row in f:
                row_sum.append(float(np.sum(row) / 255))
            for column in f.T:
                column_sum.append(float(np.sum(column) / 255))

            # Scanning for lines
            for row in range(0, len(f)):
                for column in range(0, len(f[row])):
                    # General matrix column position from relative f column position
                    general_column = column + (threshold * i)
                    # print(row_sum[row], column_sum[column])
                    # Vertical Linear score approximation
                    if row_sum[row] != 0:
                        # Vertical linearity score calculation
                        edges_frame[row][general_column] = f[row][column] / 255 * column_sum[column] / row_sum[row]
                    else:
                        edges_frame[row][general_column] = 0
                    # Remove values out of estimated tolerance value
                    if edges_frame[row][general_column] < tolerance:
                        edges_frame[row][general_column] = 0
                    else:
                        edges_frame[row][general_column] = 1

            del row_sum[:]
            del column_sum[:]

        return edges_frame


if __name__ == '__main__':
    line = LinesCamera()
    line.watch()
