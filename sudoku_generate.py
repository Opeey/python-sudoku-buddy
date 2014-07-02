#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import sFunc
import numpy as np
import os.path
import argparse

size = 25

# instanciate and configure an argument parser
parser = argparse.ArgumentParser(description='Analyzes and solves a Sudoku from a taken Image')

parser.add_argument('image', metavar='IMG',
	help='An image of a Sudoku. If specified a full processing-cycle on this image is performed.')

# parse input arguments
args = parser.parse_args()

# the input image
imgIn = args.image

# check for invalid filename
if not os.path.isfile(imgIn):
	print imgIn, "- file not found"
	sys.exit(-1)

filename = os.path.splitext(os.path.basename(imgIn))[0]
image = sFunc.open(imgIn)

height = image.shape[0]
width = image.shape[1]

# imgDir = os.path.join('./', 'ocrSets/', 'ocr_train_pts_gt/', filename)
imgDir = os.path.join('./', 'ocrSets/', 'ocr_train_pts/', filename)

if not os.path.isdir(imgDir):
	os.makedirs(imgDir)

yFactor = 1
xFactor = 1
if image.shape[1] > 1100:
	yFactor = 1100.0/image.shape[1]
	image = sFunc.scale(image, yFactor)
if image.shape[0] > 1100:
	xFactor = 1100.0/image.shape[0]
	image = sFunc.scale(image, xFactor)

grey = sFunc.greyscale(image)
blurred = sFunc.blur(grey)

binary = sFunc.binarize(blurred, 10)

corners = sFunc.cornerDetection(binary)

pts = os.path.join('./', 'pts', filename+'.pts')


failed = False
# check for valid corners, if pts file is specified
if os.path.isfile(pts):
	f = open(pts, 'r')
	for x,y in corners:
		line = f.readline().split(',')
		
		fileX = int(line[0])
		fileY = int(line[1])

		x = (x/xFactor)/yFactor
		y = (y/xFactor)/yFactor

		if abs(fileX-x) > width*0.02:
			print "FAILED: " + str(x) + " is not near " + str(fileX)
			failed = True

		if abs(fileY-y) > height*0.02:
			print "FAILED: " + str(y) + " is not near " + str(fileY)
			failed = True
	f.close()
else:
	print "WARNING: No .pts file found, continue without checking corners..."

if failed:
	print "ERROR: One or more corner-points don't match with the trainings-data, aborting..."
	sys.exit(-1)



# Generation of OCR, based on groundtruth
"""
corners = np.double([[0,0],[0,0],[0,0],[0,0]])

f = open(pts, 'r')

line = f.readline().split(',')
		
fileX = int(int(line[0])*xFactor*yFactor)
fileY = int(int(line[1])*xFactor*yFactor)

corners[0] = [fileX, fileY]

line = f.readline().split(',')
		
fileX = int(int(line[0])*xFactor*yFactor)
fileY = int(int(line[1])*xFactor*yFactor)

corners[1] = [fileX, fileY]

line = f.readline().split(',')
		
fileX = int(int(line[0])*xFactor*yFactor)
fileY = int(int(line[1])*xFactor*yFactor)

corners[2] = [fileX, fileY]

line = f.readline().split(',')
		
fileX = int(int(line[0])*xFactor*yFactor)
fileY = int(int(line[1])*xFactor*yFactor)

corners[3] = [fileX, fileY]
"""

trans = sFunc.transform(binary, corners)

raster = sFunc.raster(trans)

gt = os.path.join('./', 'gt', filename+'.gt')
 
f = open(gt, 'r').read()
 
for y in range(0, len(raster)):
	for x in range(0, len(raster[y])):
		pos = (y*9) + x + y
		if f[pos] != '_':
			numDir = os.path.join(imgDir, f[pos])
			if not os.path.isdir(numDir):
				os.mkdir(numDir)
			name = os.path.join(numDir, str((y*9) + (x+1)) + ".jpg")
			sFunc.findNum(raster[y][x], name, size, str((y*9) + (x+1)) + ".jpg")

sys.exit(0)