#!/usr/bin/python
# -*- coding: utf-8 -*-

# This Python-Script takes a .gt file and calculates a hopefully optimal solution
# via the simulated annealing algorithm

import sys
import os.path
import argparse
import numpy as np
import random
import math

def buildSudoku(sudokuIn, fixedIn, sudoku, fixed):
	for row in range(len(sudoku)):
		for square in range(len(sudoku[row])):
			
			if row == 0:
				squareCounter = 0
			elif row == 1:
				squareCounter = 3
			elif row == 2:
				squareCounter = 6

			for squareRow in range(len(sudoku[row][square])):

				if square == 0:
					begin = 0
					end = 3
				elif square == 1:
					begin = 3
					end = 6
				elif square == 2:
					begin = 6
					end = 9

				sudoku[row][square][squareRow] = sudokuIn[squareCounter][begin:end]
				fixed[row][square][squareRow] = fixedIn[squareCounter][begin:end]
				squareCounter+=1

def initializeSudoku(sudoku, fixed):
	for row in range(len(sudoku)):
		for square in range(len(sudoku[row])):
			numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
			random.shuffle(numbers)
			for squareRow in range(len(sudoku[row][square])):
				for cell in range(len(sudoku[row][square][squareRow])):
					if fixed[row][square][squareRow][cell] == 1:
						numbers.remove(sudoku[row][square][squareRow][cell])

			for squareRow in range(len(sudoku[row][square])):
				for cell in range(len(sudoku[row][square][squareRow])):
					if fixed[row][square][squareRow][cell] == 0:
						sudoku[row][square][squareRow][cell] = numbers.pop()

def calcCost(sudoku):
	cost = 0

	for row in range(len(sudoku)):
		row1 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
		column1 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
		row2 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
		column2 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
		row3 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
		column3 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
		for square in range(len(sudoku[row])):
			for squareRow in range(len(sudoku[row][square])):
				for cell in range(len(sudoku[row][square][squareRow])):
					if squareRow == 0:
						if sudoku[row][square][squareRow][cell] in row1: row1.remove(sudoku[row][square][squareRow][cell])
					elif squareRow == 1:
						if sudoku[row][square][squareRow][cell] in row2: row2.remove(sudoku[row][square][squareRow][cell])
					elif squareRow == 2:
						if sudoku[row][square][squareRow][cell] in row3: row3.remove(sudoku[row][square][squareRow][cell])

					if cell == 0:
						if sudoku[row][square][squareRow][cell] in column1: column1.remove(sudoku[row][square][squareRow][cell])
					elif cell == 1:
						if sudoku[row][square][squareRow][cell] in column2: column2.remove(sudoku[row][square][squareRow][cell])
					elif cell == 2:
						if sudoku[row][square][squareRow][cell] in column3: column3.remove(sudoku[row][square][squareRow][cell])
		cost = cost + len(row1) + len(row2) + len(row3) + len(column1) + len(column2) + len(column3)
	return cost

def main():
	random.seed()

	# instanciate and configure an argument parser
	parser = argparse.ArgumentParser(description='Solves a sudoku via simulated annealing')

	parser.add_argument('gt', metavar='GT',
		help='A .gt file, which holds the fixed values of a sudoku')

	# parse input arguments
	args = parser.parse_args()

	# the input .gt file
	gt = args.gt

	# check for invalid filename
	if not os.path.isfile(gt):
		print gt, "- file not found"
		sys.exit(-1)

	sudokuIn = np.zeros((9, 9))
	fixedIn = np.zeros((9, 9))

	f = open(gt, 'r')
	x = 0
	for row in sudokuIn:
		line = f.readline()
		y = 0
		for column in row:
			if line[y] != '_':
				sudokuIn[x][y] = int(line[y])
				fixedIn[x][y] = 1		
			y+=1
		x+=1

	sudoku = np.zeros((3,3,3,3))
	fixed = np.zeros((3,3,3,3))

	buildSudoku(sudokuIn, fixedIn, sudoku, fixed)

	initializeSudoku(sudoku, fixed)
		
	A = fixed.size - np.count_nonzero(fixed)

	cost = calcCost(sudoku)

	t0 = 2.5
	M = A*A
	N = 25

	alpha = 0.9
	t = t0

	heat = 1
	print "annealing 1..."

	n = 1
	while n <= N:
		m = 1
		while m <= M:
			i = random.randint(0, 8)
			j = random.randint(0, 8)

			while fixed[int(i/3)][int(j/3)][int(i%3)][int(j%3)] == 1:
				i = random.randint(0, 8)
				j = random.randint(0, 8)

			cellij = sudoku[int(i/3)][int(j/3)][int(i%3)][int(j%3)]

			k = random.randint(0, 2)
			l = random.randint(0, 2)

			while (fixed[int(i/3)][int(j/3)][k][l] == 1) | ((int(i%3) == k) & (int(j%3) == l)):
				k = random.randint(0, 2)
				l = random.randint(0, 2)

			cellkl = sudoku[int(i/3)][int(j/3)][k][l]

			sudoku[int(i/3)][int(j/3)][int(i%3)][int(j%3)] = cellkl
			sudoku[int(i/3)][int(j/3)][k][l] = cellij

			newcost = calcCost(sudoku)

			if newcost == 0:
				break

			if (newcost < cost) | (random.random() < math.exp((cost-newcost)/t)):
				cost = newcost
			else:
				sudoku[int(i/3)][int(j/3)][int(i%3)][int(j%3)] = cellij
				sudoku[int(i/3)][int(j/3)][k][l] = cellkl

			m+=1

		if cost == 0:
			print "chain " + str(n) + "...T=" + str(t) + "...cost=" + str(cost)
			print "Cost = 0 -- Finished\n"
			break

		print "chain " + str(n) + "...T=" + str(t) + "...cost=" + str(cost)

		t = alpha * t

		if n == N:
			# reheat
			n = 1
			t = t0

			heat+=1

			print "annealing " + str(heat) + "..."
		else:
			n+=1

	print "Completed with cost: " + str(cost)
	print sudoku

if __name__ == "__main__":
	main()