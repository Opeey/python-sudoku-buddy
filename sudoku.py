#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import sFunc
import os.path
import re
import argparse

# instanciate and configure an argument parser
parser = argparse.ArgumentParser(description='Analyzes and solves a Sudoku from a taken Image')

parser.add_argument('image', metavar='IMG',
	help='an Image of a Sudoku. If specified a full processing-cycle on this Image is performed')

# parse input arguments
args = parser.parse_args()

# the input image
imgIn = args.image

# check for invalid filename
if not os.path.isfile(imgIn):
	print imgIn, "- file not found"
	sys.exit(-1)

filename = os.path.basename(imgIn)
image = sFunc.open(imgIn)

if image.shape[1] > 1200:
	image = sFunc.scale(image, 1200.0/image.shape[1])
if image.shape[0] > 1200:
	image = sFunc.scale(image, 1200.0/image.shape[0])

grey = sFunc.greyscale(image)
blurred = sFunc.blur(grey)

binary = sFunc.binary(blurred, 10)

corners = sFunc.cornerDetection(binary)

trans = sFunc.transform(image, corners)

raster = sFunc.raster(trans)

sFunc.save("out_" + filename, trans)