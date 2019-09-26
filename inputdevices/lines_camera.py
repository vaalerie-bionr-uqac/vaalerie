
from engineering import surround_eng

import numpy as np
import cv2


class LinesCamera:

    def __init__(self):
        # Initialize video capture from port 0 w/ file path
        self.cap = cv2.VideoCapture('/dev/v4l/by-path/platform-ff540000.usb-usb-0:1.4:1.0-video-index0')
        self.process_this_frame = False
        self.LED = 164

    def watch(self):

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

            # 1 frame every 2 frame condition
            self.process_this_frame = not self.process_this_frame

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
        self.cap.release()


if __name__ == '__main__':
    line = LinesCamera()
    line.watch()
