#include <stdio.h>
#include <stdlib.h>

#include <time.h>
#include <errno.h>

#include <math.h>

#include "simulatedAnnealing.h"

#define UNSET 0
#define FIXED 1
#define NON_FIXED 0

int buildSudoku(FILE *f, struct sudoku *s) {
	int i;
	int j;
	int k;

	int c;

	struct rectangle *rects;
	
	rects = s->rects;

	int start = 0;

	/* 1 - 3 */
	for (i=0; i<3; i++) {
		for (j=0; j<3; j++) {
			for (k=0; k<3; k++) {
				c = fgetc(f);

				if (c == '\n') {
					c = fgetc(f);
				}

				if (c == '_') {
					rects[j].cells[start+k].value = UNSET;
					rects[j].cells[start+k].fixed = NON_FIXED;
				} else {
					rects[j].cells[start+k].value = (int) (c - '0');
					rects[j].cells[start+k].fixed = FIXED;
				}
			}
		}
		start+=3;
	}

	printf("\n");

	start = 0;
	/* 4 - 6 */
	for (i=0; i<3; i++) {
		for (j=3; j<6; j++) {
			for (k=0; k<3; k++) {
				c = fgetc(f);

				if (c == '\n') {
					c = fgetc(f);
				}

				if (c == '_') {
					rects[j].cells[start+k].value = UNSET;
					rects[j].cells[start+k].fixed = NON_FIXED;
				} else {
					rects[j].cells[start+k].value = (int) (c - '0');
					rects[j].cells[start+k].fixed = FIXED;
				}
			}
		}
		start+=3;
		(void)fgetc(f);
	}

	start = 0;
	/* 7 - 9 */
	for (i=0; i<3; i++) {
		for (j=6; j<9; j++) {
			for (k=0; k<3; k++) {
				c = fgetc(f);

				if (c == '\n') {
					c = fgetc(f);
				}

				if (c == '_') {
					rects[j].cells[start+k].value = UNSET;
					rects[j].cells[start+k].fixed = NON_FIXED;
				} else {
					rects[j].cells[start+k].value = (int) (c - '0');
					rects[j].cells[start+k].fixed = FIXED;
				}
			}
		}
		start+=3;
		(void)fgetc(f);
	}
	
	return 1;
}

void printSudoku(struct sudoku s) {
	int startk;
	int startj;

	int i;
	int j;
	int k;

	int line;

	startj = 0;
	printf("  -----------------------\n");
	for (line=0;line<3;line++) {
		startk = 0;
		for (i=0; i<3; i++) {
			printf(" | ");
			for (j=startj; j<startj+3; j++) {
				for (k=0; k<3; k++) {
					int val = s.rects[j].cells[startk+k].value;
					if (val == 0) {
						printf("_ ");
					} else {
						printf("%d ", val);
					}
				}
				printf("| ");
			}
			printf("\n");
			startk+=3;
		}
		printf("  -----------------------\n");
		startj+=3;
	}
}

void initializeSudoku(struct sudoku *s) {
	int i;
	int j;
	int k;

	int random;

	struct rectangle *rects;
	
	rects = s->rects;

	for (i=0;i<9;i++) {
		int forbiddenNumbers[9];
		int forbidCounter = 0;
		for (j=0;j<9;j++) {
			if (rects[i].cells[j].fixed == FIXED) {
				forbiddenNumbers[forbidCounter] = rects[i].cells[j].value;
				forbidCounter++;
			}
		}

		for (j=0;j<9;j++) {
			if (rects[i].cells[j].fixed == NON_FIXED) {
				random = (rand() % 9) + 1;
				for (k=0;k<forbidCounter;k++) {
					if (random == forbiddenNumbers[k]) {
						random = (rand() % 9) + 1;
						k = -1;
					}
				}

				forbiddenNumbers[forbidCounter] = random;
				forbidCounter++;

				rects[i].cells[j].value = random;

				if (forbidCounter == 9) {
					break;
				}
			}
		}
	}
}

int calcCost(struct sudoku s) {
	int cost;
	int i;
	int j;
	int k;
	int l;
	int startcell;
	int startrect;

	cost = 0;


	/* Columns */

	startrect = 0;
	for (i=0;i<3;i++) {
		startcell = 0;
		for (j=0;j<3;j++) {
			int inNumbers[9];
			int inCounter = 0;

			for (k=0; k<3; k++) {
				if (inCounter == 0) {
					inNumbers[0] = s.rects[startrect+k].cells[startcell].value;
					inCounter++;
				}

				for (l=0;l<inCounter;l++) {
					if (inNumbers[l] == s.rects[startrect+k].cells[startcell].value) {
						break;
					}
					if (l == inCounter-1) {
						inNumbers[inCounter] = s.rects[startrect+k].cells[startcell].value;
						inCounter++;
						break;
					}
				}

				for (l=0;l<inCounter;l++) {
					if (inNumbers[l] == s.rects[startrect+k].cells[startcell+1].value) {
						break;
					}
					if (l == inCounter-1) {
						inNumbers[inCounter] = s.rects[startrect+k].cells[startcell+1].value;
						inCounter++;
						break;
					}
				}

				for (l=0;l<inCounter;l++) {
					if (inNumbers[l] == s.rects[startrect+k].cells[startcell+2].value) {
						break;
					}
					if (l == inCounter-1) {
						inNumbers[inCounter] = s.rects[startrect+k].cells[startcell+2].value;
						inCounter++;
						break;
					}
				}



			}

			cost += (9 - inCounter);

			startcell+=3;
		}
		startrect+=3;
	}


	/* Rows */

	startrect = 0;
	for (i=0;i<3;i++) {
		startcell = 0;
		for (j=0;j<3;j++) {
			int inNumbers[9];
			int inCounter = 0;

			for (k=0; k<7; k+=3) {
				if (inCounter == 0) {
					inNumbers[0] = s.rects[startrect+k].cells[startcell].value;
					inCounter++;
				}

				for (l=0;l<inCounter;l++) {
					if (inNumbers[l] == s.rects[startrect+k].cells[startcell].value) {
						break;
					}
					if (l == inCounter-1) {
						inNumbers[inCounter] = s.rects[startrect+k].cells[startcell].value;
						inCounter++;
						break;
					}
				}

				for (l=0;l<inCounter;l++) {
					if (inNumbers[l] == s.rects[startrect+k].cells[startcell+3].value) {
						break;
					}
					if (l == inCounter-1) {
						inNumbers[inCounter] = s.rects[startrect+k].cells[startcell+3].value;
						inCounter++;
						break;
					}
				}

				for (l=0;l<inCounter;l++) {
					if (inNumbers[l] == s.rects[startrect+k].cells[startcell+6].value) {
						break;
					}
					if (l == inCounter-1) {
						inNumbers[inCounter] = s.rects[startrect+k].cells[startcell+6].value;
						inCounter++;
						break;
					}
				}
			}

			cost += (9 - inCounter);

			startcell++;
		}
		startrect++;
	}

	return cost;
}

int main(int argc, char *argv[]) {
	
	srand(time(NULL));

	int cost; /* Cost of actual state */
	int newcost; /* Cost of new state */

	int A; /* Number of non-fixed Cells */
	int M; /* Marcov-Chain Size */
	int m; /* Loop variable for M */
	int N; /* Number of Marcov-Chains until reheat */
	int n; /* Loop variable for N */

	int i; /* Variables for first Cell */
	int j;

	int k; /* Variables for second Cell */
	int l;

	int heat; /* Counter for reheats */

	double t0; /* Initial temperature */
	double t; /* Current temperature */

	double alpha;

	char *gtIn; /* *.gt File - Input */

	int status; /* status variable */

	struct sudoku s;

	if (argc != 2) {
		fprintf(stderr, "usage: %s <*.gt file>\n", argv[0]);
		return EXIT_FAILURE;
	}

	gtIn = argv[1];

	FILE *f = fopen(gtIn, "r");
	if (f == NULL) {
		fprintf(stderr, "could'nt open file - %s", gtIn);
		fclose(f);
		return EXIT_FAILURE;
	}

	status = buildSudoku(f, &s);
	if (status == 0){
		fprintf(stderr, "buildsudoku failed!");
		return EXIT_FAILURE;
	}

	fclose(f);

	initializeSudoku(&s);

	printf("Initial Solution:\n");
	printSudoku(s);


	cost = 500;
	newcost = 500;
	cost = calcCost(s);
	printf("Cost: %d\n", cost);



	A = 0;
	for (n=0;n<9;n++) {
		for (m=0;m<9;m++) {
			if (s.rects[n].cells[m].fixed == NON_FIXED) {
				A++;
			}
		}
	}

	t0 = 2.5;
	M = A*A;
	N = 25;

	alpha = 0.9;
	t = t0;

	heat = 1;

	for (n=1;n<=N;n++) {
		for(m=1;m<=M;m++) {
			int oldval;

			i = rand() % 9;
			j = rand() % 9;

			while (s.rects[(int)(i/3)+((int)(j/3)*3)].cells[(int)(i%3)+((int)(j%3)*3)].fixed == FIXED) {
				i = rand() % 9;
				j = rand() % 9;
			}

			k = rand() % 3;
			l = rand() % 3;

			while ((s.rects[(int)(i/3)+((int)(j/3)*3)].cells[(int)(k%3)+((int)(l%3)*3)].fixed == FIXED) || ( ((int)(k%3)+((int)(l%3)*3)) == ((int)(i%3)+((int)(j%3)*3)) ) ) {
				k = rand() % 3;
				l = rand() % 3;
			}

			oldval = s.rects[(int)(i/3)+((int)(j/3)*3)].cells[(int)(i%3)+((int)(j%3)*3)].value;
			s.rects[(int)(i/3)+((int)(j/3)*3)].cells[(int)(i%3)+((int)(j%3)*3)].value = s.rects[(int)(i/3)+((int)(j/3)*3)].cells[(int)(k%3)+((int)(l%3)*3)].value;
			s.rects[(int)(i/3)+((int)(j/3)*3)].cells[(int)(k%3)+((int)(l%3)*3)].value = oldval;

			newcost = calcCost(s);
			if (newcost == 0) {
				cost = newcost;
				break;
			}

			if ((newcost < cost) || ( ((double) rand()/(RAND_MAX )) < exp((double)(cost-newcost)/t))) {
				cost = newcost;
			} else {
				oldval = s.rects[(int)(i/3)+((int)(j/3)*3)].cells[(int)(i%3)+((int)(j%3)*3)].value;
				s.rects[(int)(i/3)+((int)(j/3)*3)].cells[(int)(i%3)+((int)(j%3)*3)].value = s.rects[(int)(i/3)+((int)(j/3)*3)].cells[(int)(k%3)+((int)(l%3)*3)].value;
				s.rects[(int)(i/3)+((int)(j/3)*3)].cells[(int)(k%3)+((int)(l%3)*3)].value = oldval;
			}
		}
		if (cost == 0) {
			printf("Chain %d... T=%f... Cost=%d\n", n, t, cost);
			printf("Cost = 0 -- Finished\n");
			break;
		}
		
		printf("Chain %d... T=%f... Cost=%d\n", n, t, cost);

		t*=alpha;

		if (n == N) {
			n = 1;
			t = t0;

			heat+=1;

			printf("Annealing %d...\n", heat);
		}
	}

	printSudoku(s);

	return EXIT_SUCCESS;
}