
#include <stdio.h>
#include "image.h"

int* calculateur(size_t x, size_t y, int tab[x][y]);

int* calculateur(unsigned int x, unsigned int y, int tab[x][y]){
	
	struct image im;
	int count = 0;
	for(int i=0; i<x; i++){
		for(int j=0; j<y; j++){
			int v = (int) tab[count];
			im.m[i][j] = v;
			count++;
		}
	}
	int* p = &im.m[0][0];
	return p;
}





/*    def find_lines(self, edges_frame, threshold=40, tolerance=2, cut=0):
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
 */

