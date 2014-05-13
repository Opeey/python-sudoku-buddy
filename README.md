# Sudoku Buddy - image processing in python
Sudoku Buddy is a project i started as exercise in 'Appliance of artificial intelligence' in College.
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
So if you want to get the Pixel with X=100 and Y=500, you have to say NumPy to get 'image[500][100]'.
This can be pretty confusing cause OpenCV takes X first and Y second in it's methods.
You will see how it works later.

## Getting started
When you load an image into a numpy array, without any specification in 'imread()' it's read in format
uint8 - 8 bit unsigned int, which is 0 to 255 - so it's perfect for colors in an image.
Now you can use the usual way to access one pixel: image[Y][X]

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
	
Any Questions?
Ask me at patrickhenrici@gmx.de
