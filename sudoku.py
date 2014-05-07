#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import sFunc

if len(sys.argv) < 2:
	print "Usage:", sys.argv[0], "input-file"
	print "- Creates grey.jpg, sauvola.jpg and niblack.jpg"
	sys.exit(-1)

imgIn = sys.argv[1]

image = sFunc.open(imgIn)

image = sFunc.resize(image, 0.5)

grey = sFunc.greyscale(image)
#sFunc.save("grey.jpg", grey)

sauvola = sFunc.sauvola(grey)
sFunc.save("sauvola.jpg", sauvola)

sFunc.cornerDetection(sauvola, image)

#niblack = sFunc.niblack(grey)
#sFunc.save("niblack.jpg", niblack)