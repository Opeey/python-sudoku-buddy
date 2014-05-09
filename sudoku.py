#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import sFunc
import os.path
import re

if len(sys.argv) < 2:
	print "Usage:", sys.argv[0], "input-file"
	print "- Creates output in folders: binary, corners and final"
	sys.exit(-1)

imgIn = sys.argv[1]

if not os.path.isfile(imgIn):
	print imgIn, "- file not found"
	sys.exit(-1)

result = re.split('/', imgIn)
filename = result[-1].replace('.jpg', '')

image = sFunc.open(imgIn)

if image.shape[1] > 1200:
	image = sFunc.scale(image, 1200.0/image.shape[1])
if image.shape[0] > 1200:
	image = sFunc.scale(image, 1200.0/image.shape[0])

grey = sFunc.greyscale(image)
blurred = sFunc.blur(grey)

binary = sFunc.binary(blurred, 10)
sFunc.save("binary/" + filename + ".jpg", binary)

corners = sFunc.cornerDetection(binary, image, result[-1].replace('.jpg', ''))

#trans = sFunc.transform(image, corners)

sFunc.save("final/" + filename + ".jpg", corners)