
import numpy as np


def find_lines(edges_frame, threshold=40, tolerance=2, cut=0):
    # Resize frame to desired value (horizontal cut)
    cut_frame = edges_frame[cut:]
    # Evaluate image in segments
    eval_frames = np.hsplit(edges_frame, (len(cut_frame[0])) / threshold)

    row_sum = []
    column_sum = []

    i = -1
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
    return cut_frame
