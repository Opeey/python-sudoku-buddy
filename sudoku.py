#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import sFunc
import os.path
import argparse

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

		x = (x/yFactor)/xFactor
		y = (y/yFactor)/xFactor

#		ptsFile.write(str(int(x)) + ',' + str(int(y)) + '\n')

		if abs(fileX-x) > 50:
			print "FAILED: " + str(x) + " is not near " + str(fileX)
			failed = True

		if abs(fileY-y) > 50:
			print "FAILED: " + str(y) + " is not near " + str(fileY)
			failed = True
	f.close()

else:
	print "WARNING: No .pts file found"

if failed:
	print "ERROR: One or more corner-points don't match with the trainings-data, aborting..."
	sys.exit(-1)

trans = sFunc.transform(image, corners)

raster = sFunc.raster(trans)

sFunc.save(filename + "_out.jpg", trans)

sys.exit(0)