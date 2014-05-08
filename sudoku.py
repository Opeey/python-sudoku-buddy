#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import sFunc
import os.path
import re

if len(sys.argv) < 2:
	print "Usage:", sys.argv[0], "input-file"
	print "- Creates grey.jpg, sauvola.jpg and niblack.jpg"
	sys.exit(-1)

imgIn = sys.argv[1]

if not os.path.isfile(imgIn):
	print imgIn, "- file not found"
	sys.exit(-1)

result = re.split('/', imgIn)
filename = result[-1].replace('.jpg', '')

image = sFunc.open(imgIn)

if image.shape[1] > 1000:
	image = sFunc.resize(image, 1000.0/image.shape[1])

grey = sFunc.greyscale(image)

#grey = sFunc.blur(grey, 150)

sauvola = sFunc.sauvola(grey, 10)
sFunc.save("binary/" + filename + "_sauvola.jpg", sauvola)

trans = sFunc.cornerDetection(sauvola, image, result[-1].replace('.jpg', ''))
#trans = sFunc.transformManual(sauvola, corners)
sFunc.save("final/" + filename + "_transform.jpg", trans)