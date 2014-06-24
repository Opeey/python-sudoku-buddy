#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import parser as p

def deleteEnteredCell(gt, cell):
	cellx = int(cell[1])
	celly = int(cell[3])

	lines = gt.split('\n')

	newGt = ""

	for x in range(0,len(lines)):
		for y in range(0,len(lines[x])):
			if (x == cellx) and (y == celly):
				newGt+='_'
			else:
				newGt+=lines[x][y]
		newGt+='\n'

	return newGt

def countEmptyCells(gt):
	emptyCells = 0
	for el in gt:
		if el == '_':
			emptyCells+=1
	return emptyCells

def getMinEmpty(gt):
	avrg = 0
	count = 0
	for el in range(0,9):
		# Line
		lineBegin = el*9 + el
		
		lineEnd = lineBegin+9

		empty = countEmptyCells(gt[lineBegin:lineEnd])
		avrg+=empty
		count+=1

		# Row
		row = ""
		for i in range(0,9):
			row += gt[el+i*10]

		empty = countEmptyCells(row)
		avrg+=empty
		count+=1

		# Square
		square = ""
		startValue = ((el*3)%3)+((el/3)*30)+((el%3)*3)
		for i in range(0,3):
			square += gt[startValue+(10*i):startValue+(10*i)+3]
		
		empty = countEmptyCells(square)
		avrg+=empty
		count+=1

	avrg = avrg/(count/3)

	return avrg

# instanciate and configure an argument parser
parser = argparse.ArgumentParser(description='Analyzes the blank-turns in the log file of the given player')

parser.add_argument('username', metavar='USR',
	help='The username of the player')

# parse input arguments
args = parser.parse_args()
user = args.username

log = p.parse_log(user)

gtNums = []
gts = []
estimate = []

for event in log:
	if event['sudoki_id'] not in gtNums:
		gtNums.append(event['sudoki_id'])
	if event['type'] == 'enter_value':
		if isinstance(event['tdelta'], basestring):
			estimate.append(event)
		else:
			gts.append(event)

for event in estimate:
	thisSudoku = deleteEnteredCell(event['sudoku_status'], event['cell'])
	avrg = getMinEmpty(thisSudoku)

	approxTime = 0
	backupTime = 0

	count = 0
	backupCount = 0

	for gtsEvent in gts:
		if gtsEvent['successful'] != event['successful']:
			continue

		gtsSudoku = deleteEnteredCell(gtsEvent['sudoku_status'], gtsEvent['cell'])
		thisAvrg = getMinEmpty(gtsEvent['sudoku_status'])

		if abs(avrg-thisAvrg) == 0:
			approxTime += gtsEvent['tdelta']
			count+=1
		else:
			perc = (abs(avrg-thisAvrg)/0.09) / 100.0
			backupTime += (1-perc)*gtsEvent['tdelta']
			backupCount+=1

		#perc = (abs(gtsEmpty-allEmpty)/0.81) / 100.0
		#approxTime += factor*((1-perc)*gtsEvent['tdelta'])

	if count != 0:
		approxTime = approxTime/count
	else:
		approxTime = backupTime/backupCount
	print str(event['tdelta']) + " " + str(approxTime)