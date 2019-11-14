"""
created on thursday September 26 2019
last updated on wednesday November 13 2019

@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomedicales, UQAC
    Office: H2-1180

project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

import track_line_filter as tlf
import numpy as np
import cv2


class LinesCamera:

    top_cut = 182
    bottom_cut = 220
    scale_factor = 4

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
                final_frame, lines = self.get_lines(frame)
                # Enlarge image
                final_frame = cv2.resize(final_frame, (0, 0), fx=4, fy=4)
                # Show image
                cv2.imshow('VAALERIE view', final_frame)

            # 1 frame every 2 frame condition
            self.process_this_frame = not self.process_this_frame
            # Kill switch
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
        self.cap.release()

    def watch(self):
        # Get image from USB webcam
        # ret, frame = self.cap.read()
        frame = cv2.imread('inputs/piste_4.jpg')
        # Find lines
        lines = self.get_lines(frame)
        # Camera capture release
        self.cap.release()

        return lines

    def get_lines(self, frame):
        # Cut received frame
        frame = frame[self.bottom_cut:-self.top_cut]
        # Resize frame to 1/4
        small_frame_inverted = cv2.resize(frame, (0, 0), fx=1/self.scale_factor, fy=1/self.scale_factor)
        # Flip frame
        small_frame = cv2.flip(small_frame_inverted, -1)
        # Color correction
        gray_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        # Contours
        edges_frame = cv2.Canny(gray_frame, 100, 100)
        # Filter contours for track lines w/ C tlf library
        #filtered_frame = np.asarray(tlf.find_lines(edges_frame, 4, 0.6, 0))
        points = np.asarray(tlf.find_lines(edges_frame, 4, 0.6, 0))
        # Find lines
        """lines = cv2.HoughLinesP(filtered_frame, rho=1, theta=np.pi / 360, threshold=8, minLineLength=1, maxLineGap=220)
        # Sort lines for 2 best line options
        if lines is not None:
            sorted_lines = self.sort_lines(lines)
        else:
            sorted_lines = None
        # Add lines to final frame
        # final_frame = self.add_lines(sorted_lines, small_frame)"""

        return points

    def add_lines(self, lines, small_frame):
        # if lines detected
        if lines is not None:
            for i in range(0, len(lines)):
                l = lines[i][0]
                cv2.line(small_frame, (l[0], l[1]), (l[2], l[3]), (0, 255, 0), 1)

        return small_frame, lines

    def sort_lines(self, lines, threshold=15, slope=0.1):
        # Remove horizontal lines
        i = 0
        while i < len(lines):
            x1, y1, x2, y2 = lines[i][0]
            # Is horizontal
            delta_x = x2 - x1
            if delta_x != 0 and np.abs((y2 - y1)/delta_x) < slope:
                lines = np.delete(lines, i, 0)
            else:
                i += 1

        # Remove repetitions
        i = 0
        while i < len(lines):
            j = i + 1
            while j < len(lines):
                if np.allclose(lines[i][0], lines[j][0], atol=threshold):
                    lines[i][0] = np.mean((lines[i][0], lines[j][0]), axis=0)  # BEWARE OF THE DOG! BAD AVERAGING METHOD
                    lines = np.delete(lines, j, 0)
                else:
                    j += 1
            i += 1

        return self.scale_factor*lines

    # Line code must be implemented in Cython or C++ for processing time issue
    """def find_lines(self, edges_frame, threshold=40, tolerance=2, cut=0):
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
        return cut_frame"""


if __name__ == '__main__':
    line = LinesCamera()
    line.watch()