import cv2
import os

import numpy as np
from numpy import linalg

# Library to open a Photograph of a Sudoku Game and do some operations on it,
# like binary algorithms, corner detetection and other cool stuff 

# Opens an image with the specified path
# Returns a numpy-array
def open(path):
	return cv2.imread(path)

# Saves the given image(numpy-array) into path
def save(path, image):
	cv2.imwrite(path, image)

# Scales an image by given factor
def scale(image, factor):
	return cv2.resize(image, (0, 0), fx=factor, fy=factor)

# Returns a greyscaled version of the given image
def greyscale(image):
	return np.mean(image, axis=2)

# Blurs the image with gaussianBlur
def blur(image):
	return cv2.GaussianBlur(image, (5, 5), 0)

# Calculates a binary from given greyscale image.
# Uses the sauvola-algorithm and a window of size*size
def binarize(image, size=15):
	tmp0 = np.cumsum(image, axis=1)

	va = np.cumsum(tmp0, axis=0)
	tmp1=image**2
	tmp2 = np.cumsum(tmp1, axis=1)
	vb = np.cumsum(tmp2, axis=0)
	binary = np.zeros((image.shape[0], image.shape[1]))

	oldSize = size

	y = 0
	for row in image:
		x = 0
		for pixel in row:
			if ((y < size) | (x < size)):
				size = min(x,y)

			if (size > 0):
				my = float((va[y][x]-va[y-size][x]-va[y][x-size]+va[y-size][x-size])/size**2)
				i = float(((vb[y,x]-vb[y-size,x]-vb[y,x-size]+vb[y-size,x-size])/size**2)-(my**2))
				if (i < 0):
					i = 0
				o = np.sqrt(i)
				k = 0.2
				t = my * ( 1 + k * ( (o/128) - 1 ) )
				if image [y][x] >= t:
					binary[y][x] = 0
				else:
					binary[y][x] = 255

			size = oldSize
			x = x+1
		y = y+1
		

	return binary

# Calculates the intersection of f and g
def intersection(f, g):
	x = g[0] - f[0]
	n = f[1] - g[1]
	intersecX = n / x
	intersecY = g[0] * intersecX + g[1]
	return np.double([intersecX, intersecY])

# Tries to localize the Sudoku in the image and gives back the corners in an array
# image - a binary image
def cornerDetection(binary):
	# Convert the image to uint8, canny needs this
	binary = np.uint8(binary)

	# The Canny algorithm detects the edges of the given binary image
	edges = cv2.Canny(binary, 50, 100, apertureSize=5)

	# We dilate the Edges, so the Sudoku-Border can be recognized better
	edges = cv2.dilate(edges, cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3)))

	# findContours, we can use them to find the largest Area in the picture
	# and assume that this is the sudoku
	contours, hierarchy = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

	# We assume that the Contour, with the largest Area is the Sudoku
	# So we loop over all contours and find the largest
	largestA = 0
	largestIndex = 0

	i = 0
	for contour in contours:
		
		A = cv2.contourArea(contour)

		if A > largestA:
			largestA = A
			largestIndex = i
		i+=1

	# Take the smallest (possibly rotated) rectangle of the contour
	bounding = cv2.minAreaRect(contours[largestIndex])

	# And calculate the Coordinates of the corners
	box = cv2.cv.BoxPoints(bounding)

	# Put X and Y Values in arrays
	boxX = np.array([int(box[0][0]), int(box[1][0]), int(box[2][0]), int(box[3][0])])
	boxY = np.array([int(box[0][1]), int(box[1][1]), int(box[2][1]), int(box[3][1])])

	# Get the minima and maxima, the +/- 10 is made, so nothing is 'cut away'
	xMin = boxX.min() - 10
	xMax = boxX.max() + 10
	yMin = boxY.min() - 10
	yMax = boxY.max() + 10

	# Workaround, the minAreaRect can be negative.
	# If one or more of the Edges are negative, just make them 0
	# it's not very beautiful, but it works.
	if xMin < 0:
		xMin = 0
	if xMax < 0:
		xMax = 0
	if yMin < 0:
		yMin = 0
	if yMax < 0:
		yMax = 0	
	
	# Cut the image to the area, we found with minAreRect
	sudokuArea = edges[yMin:yMax, xMin:xMax]

	# Get the height or widht, whatever is bigger
	maxLength = np.array([sudokuArea.shape[0], sudokuArea.shape[1]]).max()

	# Now calculate the HoughLines
	lines = cv2.HoughLines(sudokuArea, 1, np.pi/180, int(maxLength*0.5))

	# We start with ridiculous high or low values
	topYIntercept = 100000.0
	topXIntercept = 0.0

	bottomYIntercept = 0.0
	bottomXIntercept = 0.0

	leftXIntercept = 100000.0
	leftYIntercept = 0.0

	rightXIntercept = 0.0
	rightYIntercept = 0.0

	topLine = np.double([1000.0,1000.0])
	bottomLine = np.double([-1000.0,-1000.0])
	leftLine = np.double([1000.0,1000.0])
	rightLine = np.double([-1000.0,-1000.0])

	# Loop over all lines, and get the most left, most right, most up and most down
	for rho,theta in lines[0]:

		# Workaround, when the angle is 0 there would be a divide by zero error, so we assume it is 0.001
		if theta == 0:
			theta = 0.001

		x = rho/np.cos(theta)
		y = rho/(np.cos(theta)*np.sin(theta))
		
		# We assume that the top and bottom lines are between 50 and 130 degrees
		# and the left and right are between 150 and 30 degrees
		if (theta > np.pi*50/180) and (theta < np.pi*130/180):
			if (rho < topLine[0]):
				topLine = np.double([rho, theta])

			if (rho > bottomLine[0]):
				bottomLine = np.double([rho, theta])
		elif (theta < np.pi*30/180) or (theta > np.pi*150/180):
			if (x > rightXIntercept):
				rightLine = np.double([rho, theta])
				rightXIntercept = x
			elif (x <= leftXIntercept):
				leftLine = np.double([rho, theta])
				leftXIntercept = x

	# Put the lines in an array
	edgeLines = np.array([topLine, bottomLine, leftLine, rightLine])

	# top, bottom, left, right
	equations = np.double([[0,0], [0,0], [0,0], [0,0]])

	# Calculate the equation for every line
	i = 0
	for rho,theta in edgeLines:
		m = (-np.cos(theta))/(np.sin(theta))
		b = rho/np.sin(theta)

		equations[i] = [m, b]

		i+=1

	# bottom - left | top - left | top - right | bottom - right
	sudokuEdges = np.double([[0,0], [0,0], [0,0], [0,0]])

	# Calculate the four intersects of the equations

	# bottom - left
	sudokuEdges[0] = intersection(equations[1], equations[2])

	# top - left
	sudokuEdges[1] = intersection(equations[0], equations[2])

	# top - right
	sudokuEdges[2] = intersection(equations[0], equations[3])

	# bottom - right
	sudokuEdges[3] = intersection(equations[1], equations[3])


	# calculate back to global coordinates
	i = 0
	for edge in sudokuEdges:
		sudokuEdges[i] = [(edge[0]+xMin), (edge[1]+yMin)]
		i+=1

	return sudokuEdges

# Creates the transform-matrix to shift the sudoku from the given corners into an new image
def transform(image, corners, size=0):
	x1 = corners[0][0]
	y1 = corners[0][1]

	x2 = corners[1][0]
	y2 = corners[1][1]

	x3 = corners[2][0]
	y3 = corners[2][1]

	x4 = corners[3][0]
	y4 = corners[3][1]

	if size==0:
		height = int(corners[0][1] - corners[1][1])
		width = int(corners[2][0] - corners[1][0])
	else:
		height = size
		width = size

	x11 = 0.0
	y11 = height

	x22 = 0.0
	y22 = 0.0

	x33 = width
	y33 = 0.0

	x44 = width
	y44 = height


	a = np.array([[ x1, y1, 1, 0, 0, 0, -(x1*x11), -(y1*x11)],
                  [0, 0, 0, x1, y1, 1, -(x1*y11), -(y1*y11)],
                  [ x2, y2, 1, 0, 0, 0, -(x2*x22), -(y2*x22)],
                  [0, 0, 0, x2, y2, 1, -(x2*y22), -(y2*y22)],
                  [ x3, y3, 1, 0, 0, 0, -(x3*x33), -(y3*x33)],
                  [0, 0, 0, x3, y3, 1, -(x3*y33), -(y3*y33)],
                  [ x4, y4, 1, 0, 0, 0, -(x4*x44), -(y4*x44)],
                  [0, 0, 0, x4, y4, 1, -(x4*y44), -(y4*y44)]])

	b = np.array([x11, y11, x22, y22, x33, y33, x44, y44])

	N = linalg.solve(a, b)
	N = np.append(N, [1.00])
	M = N.reshape((3,3))

	T = cv2.warpPerspective(image,M,(width,height))

	return T

# Creates an array which holds any field in the sudoku
def raster(image):
	imgHeight = image.shape[0]
	imgWidth = image.shape[1]

	fieldHeight = int(imgHeight/9)
	fieldWidth = int(imgWidth/9)

	raster = np.zeros((9,9,fieldHeight,fieldWidth))
	
	y = 0
	for line in raster:
		x = 0
		for field in line:
			raster[y][x] = np.copy(image[(fieldHeight*y):((fieldHeight*y)+fieldHeight), (fieldWidth*x):((fieldWidth*x)+fieldWidth)])
			x+=1
		y+=1

	return raster

def findNum(image):
	size = 20

	if np.count_nonzero(image) <= (image.shape[0]*image.shape[1])/10:
		return np.zeros((size, size))

	image = np.uint8(image)	

	_image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3)), iterations=5)

	# The Canny algorithm detects the edges of the given binary image
	edges = cv2.Canny(_image, 50, 100, apertureSize=5)

	# findContours, we can use them to find the largest Area in the picture
	# and assume that this is the number
	contours, hierarchy = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

	# We assume that the Contour, with the largest Area is the number
	# So we loop over all contours and find the largest
	largestA = 0
	largestIndex = 0

	i = 0
	for contour in contours:
		
		A = cv2.contourArea(contour)

		if A > largestA:
			largestA = A
			largestIndex = i
		i+=1

	# Take the smallest (possibly rotated) rectangle of the contour
	bounding = cv2.minAreaRect(contours[largestIndex])

	# And calculate the Coordinates of the corners
	box = cv2.cv.BoxPoints(bounding)

	# Put X and Y Values in arrays
	boxX = np.array([int(box[0][0]), int(box[1][0]), int(box[2][0]), int(box[3][0])])
	boxY = np.array([int(box[0][1]), int(box[1][1]), int(box[2][1]), int(box[3][1])])

	# Get the minima and maxima
	xMin = boxX.min() - 2
	xMax = boxX.max() + 2
	yMin = boxY.min() - 2
	yMax = boxY.max() + 2

	# Workaround, the minAreaRect can be negative.
	# If one or more of the Edges are negative, just make them 0
	# it's not very beautiful, but it works.
	if xMin < 0:
		xMin = 0
	if xMax < 0:
		xMax = 0
	if yMin < 0:
		yMin = 0
	if yMax < 0:
		yMax = 0	

	num = transform(image, [[xMin, yMax], [xMin, yMin], [xMax, yMin], [xMax, yMax]], size=size)

	return num

def readOCRData(path, exclude=""):
	
	count = 0

	for imgDir in os.listdir(path):
		if os.path.isdir(os.path.join(path,imgDir)):
			if os.path.basename(os.path.join(path,imgDir)) != str(exclude):
				for numDir in os.listdir(os.path.join(path,imgDir)):
					if os.path.isdir(os.path.join(path,imgDir,numDir)):
						for f in os.listdir(os.path.join(path,imgDir,numDir)):
							if os.path.isfile(os.path.join(path,imgDir,numDir,f)):
								count+=1

	ocrImgData = np.zeros((count, 20, 20))
	ocrNumData = np.zeros(count)

	i = 0

	for imgDir in os.listdir(path):
		if os.path.isdir(os.path.join(path,imgDir)):
			if os.path.basename(os.path.join(path,imgDir)) != str(exclude):
				for numDir in os.listdir(os.path.join(path,imgDir)):
					if os.path.isdir(os.path.join(path,imgDir,numDir)):
						for f in os.listdir(os.path.join(path,imgDir,numDir)):
							if os.path.isfile(os.path.join(path,imgDir,numDir,f)):
								num = int(numDir)
								img = cv2.imread(os.path.join(path,imgDir,numDir,f), -1)
								ocrImgData[i] = img
								ocrNumData[i] = num
								i+=1

	return ocrImgData, ocrNumData

def ocr(numImg, ocrImgData, ocrNumData):
	ocrValues = np.zeros(len(ocrImgData))

	i = 0
	for i in range(0,len(ocrImgData)):
		val = 0
		for y in range(0,len(ocrImgData[i])):
			for x in range(0,len(ocrImgData[i][y])):
				ocrval = ocrImgData[i][y][x]
				if ocrval > 0:
					ocrval = 255
				else:
					ocrval = 0

				imgval = numImg[y][x]
				if imgval > 0:
					imgval = 255
				else:
					imgval = 0

				if ocrval == imgval:
					val+=1
				x+=1
			y+=1

		ocrValues[i] = val
		i+=1

	first = np.argmax(ocrValues)
	ocrValues[first] = 0

	second = np.argmax(ocrValues)
	ocrValues[second] = 0

	third = np.argmax(ocrValues)
	ocrValues[third] = 0

	num_1 = ocrNumData[first]
	num_2 = ocrNumData[second]
	num_3 = ocrNumData[third]

	if (num_1 == num_2) or (num_1 == num_3):
		return num_1
	elif (num_2 == num_3):
		return num_2
	else:
		return 0