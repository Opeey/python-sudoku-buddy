# Sudoku Buddy - image processing in python
Sudoku Buddy is a project i started as exercise in <b>Appliance of artificial intelligence</b> in College.
Until now (May 2014) it's still in development and i will use GitHub as online repo and documentation.

If you find something of this stuff useful, feel free to use my code and approach as inspiration.

## The goal of this project
The whole thing of this is to take up your phone, open your browser and go to the (at this time non existent) 'Sudoku Buddy'-Homepage.
This page will let you upload a photo (or just take it right away) of a sudoku, then analyzes it on the server which can give you hints
how to solve the sudoku, give you an estimate time respectively a level of difficulty, etc.

The project splits in several parts.
First task is to read a given photo, greyscale it, calculate a binary image and locate the sudoku in the image.
Further on comes the detection of the numbers via ocr and solving of the sudoku.
The last step is to 'analyze' the sudoku and put it in a category, for this it is important to collect training data
so the system can learn over time and later on estimate how difficult the sudoku is.

The whole project is coded in Python, with NumPy (http://www.numpy.org/) and the OpenCV library (http://opencv.org/).
Since this is an exercise, i will do some features and algorithms manually although OpenCV allready have methods to do
things the short way.
But i won't program every algorithm by myself, while it's in the OpenCV library.

## Reading and writing an image
There are some really short methods to read and write image-files in Python, using OpenCV.
After you import cv2 you just use the build-in methods:

	cv2.imread(path) - to read an image into a NumPy array
	cv2.imwrite(path, image) - to write an NumPy array of an image into a file

Important to know is:
While OpenCV works on images like the 'normal' way, first comes X-Coordinate and second comes Y-Coordinate, NumPy just swaps them.
So if you want to get the Pixel with X=100 and Y=500, you have to say NumPy to get <b>image[500][100]</b>.
This can be pretty confusing cause OpenCV takes X first and Y second in it's methods.
You will see how it works later.

## Getting started
When you load an image into a numpy array, without any specification in <b>imread()</b> it's read in format
uint8 - 8 bit unsigned int, which is 0 to 255 - so it's perfect for colors in an image.
Now you can use the usual way to access one pixel: <b>image[Y][X]</b>

### Greyscale
With this information you can implement a greyscale-method.
NumPy and OpenCV have a couple of ways to greyscale an image, but i simply meaned the whole image.

	def greyscale(image):
		return np.mean(image, axis=2)
	
## Binarize
To get a binary image out of the greyscaled version, we need to touch each pixel and decide if the pixel is fore-, or background. Depending on this, the pixel in the binary version will be painted white oder black.
But how do we decide what is fore-, and what is background?
We could simply set a threshold of i.e. 128, but that would not work for a very dark or light image.
So the threshold depends on how dark the image, respectively the surrounding pixels are.

### Sauvola
There are several formulas to calculate the threshold, i use the sauvola-formula because it works pretty good
for sudoku images.

	T(x,y) := μ(x,y) * (1 + k * ( s(x,y)/s'(x,y) - 1) )
	where k is 0.2 or 0.5
	s' is the maximal standard deviation, which is 128 in 8-bit
	
So you choose a window, how many pixels you want to look at. This could be 10x10 pixels or something else, you need to
try which value gives you the best results.
You mean the values and use the sauvola-formula.

For an example (and improvement) look at the binary() function in sFunc.py

## Improvements
	
### Scale
If the image is very big, like 5000x5000 pixels or something, every further operation is pretty slow.
So it's a really good idea to scale the image as soon as possible, a good value is ~1200 pixels width or height - whatever is greater.
You should not scale it to small, this could result in to high detail-loss, and you should scale on same ratio as the original image.

	# Scales an image by given factor
	def scale(image, factor):
		return cv2.resize(image, (0, 0), fx=factor, fy=factor)

### Blurring the image
On some images, the binarized version is not a sufficient outcome for later operations.
So we can improve the outcome of the binarized image, when we optimize the income.
Sometimes the image may be very noisy, so the binarized image will have many unwanted 'foreground'-parts.
To change that, we just blur the image before binarizing, so the noise will not be detected as foreground.

	# Blurs the image with gaussianBlur
	def blur(image):
		return cv2.GaussianBlur(image, (5, 5), 0)

### Cython
Cython is a pretty good way to boost your code up. I got a boost up of ~50%.
I use cython just to define all types that can be static.
You can do much more with cython, but i only used this one.

So, how does it work?
You can just include the cython version of numpy, by adding the line 

	cimport numpy as np
	
and save the file as a .pyx - which is the file extension for cython.

Now you can define all types that you want to:

	# For a function:
	def func(int arg1, char *arg2 ...):
		# Anywhere in your code:
		cdef int i = ...
		
		# NumPy Arrays:
		cdef np.ndarray[np.uint8_t, ndim=3] image = ...

You have to define the type of the content in the numpy array and the dimensions the array have.
For an 8-bit colored image the type would be <b>uint8_t</b> and the dimension would be <b>3</b>.

#### Compiling
Bad news is, you have to compile your code, everytime you want to change something.
So it is a good idea to 'cythonize' your code, after your functionality is ready, cause it's really annoying
to develop with half python / half cython and debug your code.

If your cython code is ready and you want to try if it works, you have to compile it - if you want to know how to do this, you can look at the folder cython, inside the setup.py and the compile.sh, which do all the work.

Further information: http://cython.org/

Any Questions?
Ask me at patrickhenrici@gmx.de
