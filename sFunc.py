import cv2

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

def resize(image, factor):
	return cv2.resize(image, (0, 0), fx=factor, fy=factor)

# Blurs the image -- Not efficient and obviously worse output
def blur(image, sigma):
	image = np.uint8(image)
	return np.float32(cv2.bilateralFilter(image, 5, sigma, sigma))
	#return cv2.GaussianBlur(image, (5, 5), 0)

# Tries to localize the Sudoku in the image
def cornerDetection(image, imagecolor, filename):
	#dst = cv2.cornerHarris(imfloat,2,3,0.04)
	#dst = cv2.dilate(dst,None)
	image = np.uint8(image)

	edges = cv2.Canny(image, 50, 100, apertureSize=5)

	save("corners/" + filename + "_canny.jpg", edges)

	contours, hierarchy = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

	cv2.drawContours(imagecolor, contours, -1, [0,255,0], 2, 8, hierarchy)

	save("corners/" + filename + "_contours.jpg", imagecolor)

	largestA = 0
	index = 0
	for contour in contours:
		
		A = cv2.contourArea(contour)

		if A > largestA:
			largestA = A
			largestIndex = index
		index+=1

	#print contours[largestIndex]

	bounding = cv2.minAreaRect(contours[largestIndex])

	#print bounding

	box = cv2.cv.BoxPoints(bounding)

	#print box

	boxX = np.array([int(box[0][0]), int(box[1][0]), int(box[2][0]), int(box[3][0])])
	boxY = np.array([int(box[0][1]), int(box[1][1]), int(box[2][1]), int(box[3][1])])

	edgesSudoku = edges[boxY.min():boxY.max(), boxX.min():boxX.max()]
	__imagecolor = np.copy(imagecolor[boxY.min():boxY.max(), boxX.min():boxX.max()])

	

	lines = cv2.HoughLines(edgesSudoku, 1, np.pi/180, 150)

	topYIntercept = 100000
	topXIntercept = 0

	bottomYIntercept = 0
	bottomXIntercept = 0

	leftXIntercept = 100000
	leftYIntercept = 0

	rightXIntercept = 0
	rightYIntercept = 0

	topLine = np.float32([1000,1000])
	bottomLine = np.float32([-1000,-1000])
	leftLine = np.float32([1000,1000])
	rightLine = np.float32([-1000,-1000])

	for rho,theta in lines[0]:

		if theta == 0:
			theta = 0.01

		x = rho/np.cos(theta)

		y = rho/(np.cos(theta)*np.sin(theta))
		
		if (theta > np.pi*50/180) and (theta < np.pi*130/180):
			if (rho < topLine[0]):
				topLine = [rho, theta]

			if (rho > bottomLine[0]):
				bottomLine = [rho, theta]
		elif (theta < np.pi*30/180) or (theta > np.pi*150/180):
			if (x > rightXIntercept):
				rightLine = [rho, theta]
				rightXIntercept = x
			elif (x <= leftXIntercept):
				leftLine = [rho, theta]
				leftXIntercept = x

	edgeLines = np.array([topLine, bottomLine, leftLine, rightLine])

	for rho,theta in edgeLines:
		a = np.cos(theta)
		b = np.sin(theta)
		
		x0 = a*rho
		y0 = b*rho

		x1 = int(x0 + 1000*(-b))
		y1 = int(y0 + 1000*(a))
		x2 = int(x0 - 1000*(-b))
		y2 = int(y0 - 1000*(a))

		cv2.line(__imagecolor,(x1,y1),(x2,y2),(0,0,255),2)

	save("corners/" + filename + "_sudoku.jpg", __imagecolor)

	for rho,theta in lines[0]:
		a = np.cos(theta)
		b = np.sin(theta)
		
		x0 = a*rho
		y0 = b*rho

		x1 = int(x0 + 1000*(-b))
		y1 = int(y0 + 1000*(a))
		x2 = int(x0 - 1000*(-b))
		y2 = int(y0 - 1000*(a))

		cv2.line(__imagecolor,(x1,y1),(x2,y2),(0,0,255),2)

	save("corners/" + filename + "_all.jpg", __imagecolor)
	# top, bottom, left, right
	equations = np.float32([[0,0], [0,0], [0,0], [0,0]])

	i = 0
	for rho,theta in edgeLines:
		m = (-np.cos(theta))/(np.sin(theta))
		b = rho/np.sin(theta)

		equations[i] = [m, b]

		i+=1

	# bottom - left | top - left | top - right | bottom - right
	sudokuEdges = np.float32([[0,0], [0,0], [0,0], [0,0]])


	# bottom - left
	x = equations[2][0] - equations[1][0]
	n = equations[1][1] - equations[2][1]
	intersecX = n / x
	intersecY = equations[2][0] * intersecX + equations[2][1]
	sudokuEdges[0] = [intersecX, intersecY]


	# top - left
	x = equations[2][0] - equations[0][0]
	n = equations[0][1] - equations[2][1]
	intersecX = n / x
	intersecY = equations[2][0] * intersecX + equations[2][1]
	sudokuEdges[1] = [intersecX, intersecY]


	# top - right
	x = equations[3][0] - equations[0][0]
	n = equations[0][1] - equations[3][1]
	intersecX = n / x
	intersecY = equations[3][0] * intersecX + equations[3][1]
	sudokuEdges[2] = [intersecX, intersecY]


	# bottom - right
	x = equations[3][0] - equations[1][0]
	n = equations[1][1] - equations[3][1]
	intersecX = n / x
	intersecY = equations[3][0] * intersecX + equations[3][1]
	sudokuEdges[3] = [intersecX, intersecY]

	return transformManual(imagecolor[boxY.min():boxY.max(), boxX.min():boxX.max()], sudokuEdges)

# Manually create the transform-matrix to shift the sudoku into a 1000x1000 image
def transformManual(image, corners):
	x1 = corners[0][0]
	y1 = corners[0][1]

	x2 = corners[1][0]
	y2 = corners[1][1]

	x3 = corners[2][0]
	y3 = corners[2][1]

	x4 = corners[3][0]
	y4 = corners[3][1]

	
	x11 = 0.0
	y11 = 1000.0

	x22 = 0.0
	y22 = 0.0

	x33 = 1000.0
	y33 = 0.0

	x44 = 1000.0
	y44 = 1000.0


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

	T = cv2.warpPerspective(image,M,(1000,1000))

	return T

# Same as transformManual, but the transform-matrix is calculated by 
# getPerspectiveTransform()
def transform(image, corners):
	newCorners = np.array([[1000.0,1000.0],[1000.0,0.0],[0.0,0.0],[0.0,1000.0]])

	M = cv2.getPerspectiveTransform(corners,newCorners)
	T = cv2.warpPerspective(image,M,(1000,1000))

	return T

# Returns a greyscaled (mean) version of the given image
def greyscale(image):
	return np.mean(image, axis=2)

# Calculates a binary image, uses the sauvola-algorithm and a window of size*size
def sauvola(image, size=15):
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
				my = (va[y][x]-va[y-size][x]-va[y][x-size]+va[y-size][x-size])/size**2
				i = ((vb[y,x]-vb[y-size,x]-vb[y,x-size]+vb[y-size,x-size])/size**2)-(my**2)
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

# Calculates a binary image, uses the niblack-algorithm and a window of size*size
def niblack(image, size=15):
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
				my = (va[y][x]-va[y-size][x]-va[y][x-size]+va[y-size][x-size])/size**2
				i = ((vb[y,x]-vb[y-size,x]-vb[y,x-size]+vb[y-size,x-size])/size**2)-(my**2)
				if (i < 0):
					i = 0
				o = np.sqrt(i)
				t = my - 0.2 * o
				if image [y][x] >= t:
					binary[y][x] = 255

			size = oldSize
			x = x+1
		y = y+1

	return binary