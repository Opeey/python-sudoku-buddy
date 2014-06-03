#ifndef LIBSA_H
#define LIBSA_H

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

void sudokuToInt(struct sudoku s, int *array);

int buildSudoku(char *gt, struct sudoku *s);

void initializeSudoku(struct sudoku *s);

int calcCost(struct sudoku s);

void solve(char *gtIn, int *result);

#endif