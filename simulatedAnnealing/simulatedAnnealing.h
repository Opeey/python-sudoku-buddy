#ifndef SIMULATEDANNEALING_H
#define SIMULATEDANNEALING_H

struct cell {
	int fixed;
	int value;
};

struct rectangle {
	struct cell cells[9];
};

struct sudoku {
	struct rectangle rects[9];
};

void printSudoku(struct sudoku s);

int buildSudoku(FILE *f, struct sudoku *s);

void initializeSudoku(struct sudoku *s);

int calcCost(struct sudoku s);

#endif