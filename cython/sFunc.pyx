import cv2

import numpy as np
cimport numpy as np
from numpy import linalg

# Library to open a Photograph of a Sudoku Game and do some operations on it,
# like binary algorithms, corner detetection and other cool stuff 

# Opens an image with the specified path
# Returns a numpy-array
def open(char *path):
	cdef np.ndarray[np.uint8_t, ndim=3] image = cv2.imread(path)
	return image

# Saves the given image(numpy-array) into path
def save(char *path, np.ndarray[double, ndim=2] image):
	cv2.imwrite(path, image)

# Tries to localize the Sudoku in the image
def cornerDetection(image, imagecolor):
	#dst = cv2.cornerHarris(imfloat,2,3,0.04)
	#dst = cv2.dilate(dst,None)
	dst = np.uint8(image)

	imgray = cv2.cvtColor(imagecolor,cv2.COLOR_BGR2GRAY)
	thresh = cv2.threshold(imgray,127,255,0)

	

	contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	cv2.drawContours(imagecolor,contours,-1,(0,255,0),3)

	cv2.imwrite("./corners.jpg", imagecolor)

# Manually create the transform-matrix to shift the sudoku into a 1000x1000 image
def transformManual(np.ndarray[np.uint8_t, ndim=3] image, np.ndarray[double, ndim=2] corners):
	cdef np.ndarray[double, ndim=1] b, N
	cdef np.ndarray[double, ndim=2] a, M
	cdef np.ndarray[np.uint8_t, ndim=3] T
	cdef double x1, y1, x2, y2, x3, y3, x4, y4, x11, y11, x22, y22, x33, y33, x44, y44

	x1 = corners[0][0]
	y1 = corners[0][1]

	x2 = corners[1][0]
	y2 = corners[1][1]

	x3 = corners[2][0]
	y3 = corners[2][1]

	x4 = corners[3][0]
	y4 = corners[3][1]

	
	x11 = 1000.0
	y11 = 1000.0

	x22 = 1000.0
	y22 = 0.0

	x33 = 0.0
	y33 = 0.0

	x44 = 0.0
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
def transform(np.ndarray[np.uint8_t, ndim=3] image, np.ndarray[double, ndim=2] corners):
	cdef np.ndarray[double, ndim=2] newCorners, M
	cdef np.ndarray[np.uint8_t, ndim=3] T

	newCorners = np.array([[1000.0,1000.0],[1000.0,0.0],[0.0,0.0],[0.0,1000.0]])

	M = cv2.getPerspectiveTransform(corners,newCorners)
	T = cv2.warpPerspective(image,M,(1000,1000))

	return T

# Returns a greyscaled (mean) version of the given image
def greyscale(np.ndarray[np.uint8_t, ndim=3] image):
	cdef np.ndarray[double, ndim=2] grey = np.mean(image, axis=2)
	return grey

# Calculates a binary image, uses the sauvola-algorithm and a window of size*size
def sauvola(np.ndarray[double, ndim=2] image, int size=15):
	cdef np.ndarray[double, ndim=2] tmp0, tmp1, tmp2, va, vb, binary
	cdef int oldSize, y, x
	cdef double my, i, o, k, t

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
def niblack(np.ndarray[double, ndim=2] image, int size=15):
	cdef np.ndarray[double, ndim=2] tmp0, tmp1, tmp2, va, vb, binary
	cdef int oldSize, y, x
	cdef double my, i, o, t

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