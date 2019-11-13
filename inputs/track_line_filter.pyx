#cython: language_level=3
#cython.boundscheck(False)

import numpy as np
cimport numpy as np


cpdef unsigned char[:,:] find_lines(unsigned char[:,:] edges_frame, int threshold, float tolerance, int cut):
    # Resize frame to desired value (horizontal cut)
    cdef unsigned char[:,:] cut_frame = edges_frame[cut:]

    # Lower values in cut_frame
    cdef int x, y = 0
    cdef int y_size = len(cut_frame)
    cdef int x_size = len(cut_frame[0])

    for x in range(0, x_size):
        for y in range(0, y_size):
            if cut_frame[y][x] == 255:
                cut_frame[y][x] = 1

    # Split image
    eval_frames = np.hsplit(cut_frame, (x_size/threshold))

    # Declare C variables type
    cdef unsigned char[:,:] f = np.zeros((threshold, y_size), dtype=np.ubyte)

    cdef float[:] row_sum = np.zeros(y_size, dtype=np.float32)
    cdef float[:] column_sum = np.zeros(threshold, dtype=np.float32)

    cdef unsigned char[:] rows = np.zeros(threshold, dtype=np.ubyte)
    cdef unsigned char[:] columns = np.zeros(y_size, dtype=np.ubyte)

    cdef int i, c, row, column, general_column, correction = 0

    points = []

    # Evaluate image in segments
    for f in eval_frames:

        correction = threshold * i
        i += 1

        # 1D rows and columns sum arrays
        for rows in f:
            row_sum[c] = <int> np.sum(rows)
            c += 1
        c = 0
        for columns in f.T:
            column_sum[c] = <int> np.sum(columns)
            c += 1
        c = 0

        # Scanning for lines
        for row in range(0, y_size):
            for column in range(0, threshold):
                # General matrix column position from relative f column position
                general_column = column + correction
                # is linear
                if row_sum[row] != 0 and (<float> f[row][column] * column_sum[column] / row_sum[row]) > (tolerance):
                    cut_frame[row][general_column] = 255
                    points.append([general_column, x_size - row])
                # is not
                else:
                    cut_frame[row][general_column] = 0

        row_sum[:] = 0
        column_sum[:] = 0


    return cut_frame