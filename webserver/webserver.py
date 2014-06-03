#!/usr/bin/python
# -*- coding: utf-8 -*-

import cherrypy
import uuid
import os
import re

import cv2
import numpy as np

import sFunc

import ctypes
from ctypes import c_int
libsa = ctypes.CDLL("./libsa.so.1.0")

# resets the cookies, called when an error occurs
def reset():

	cookie = cherrypy.response.cookie
	request = cherrypy.request.cookie

	if "solution" in request.keys():
		cookie["solution"] = ""
		cookie["solution"]['expires'] = 0
	
	if "sudoku" in request.keys():
		cookie["sudoku"] = ""
		cookie["sudoku"]['expires'] = 0

	return "Reset successful."

# adds a new cookie, or change the value
def addCookie(key, value):
	cookie = cherrypy.response.cookie

	cookie[key] = value
	cookie[key]['path'] = '/'
	cookie[key]['max-age'] = 3600

# returns the value of a cookie or an empty string, when the cookie doesn't exist
def getCookie(key):
	cookie = cherrypy.request.cookie

	if key in cookie.keys():
		return cookie[key].value
	else:
		return ""

# deletes a cookie (deletes value and let it expire)
def deleteCookie(key):
	cookie = cherrypy.response.cookie
	request = cherrypy.request.cookie

	if key in request.keys():
		cookie[key] = ""
		cookie[key]['expires'] = 0


class Sudoku(object):

	# If an error occurs, just call reset()	- not very fancy
	_cp_config = {'request.error_response': reset}

	# returns the <head>-part of the html, with js part. Own code is in var js
	def printHead(self, js=""):
		return """
			<head>
				<meta charset="utf-8">
				<title>Sudoku</title>
				<link rel="stylesheet" type="text/css" href="css/style.css">
				"""+self.javascript(js)+"""
			</head>
		"""

	# creates the javascript and returns it
	def javascript(self, ownCode=""):
		return """
				<script src="js/jquery-2.1.1.min.js" type="text/javascript"></script>
				<script src="js/sudoku.js" type="text/javascript"></script>
				<script type="text/javascript">
					<!--
					$(document).ready(function(){
					
						function openError(msg) {
							var $this = $(".error"),
								$p = $this.children('p');

							$p.text(msg);
							$this.fadeIn("normal");
						};

						$(".close").click(function() {

							$(".error").fadeOut("normal");

						});

						"""+str(ownCode)+"""

					})
					//-->
				</script>
		"""

	# prints the body, stored in html/body.html
	def printBody(self):
		return open(os.path.join('./', 'html/', 'body.html')).read()

	# controller - collects all needed data and creates the page
	@cherrypy.expose
	def index(self, error="", refresh=False):

		if refresh:
			raise cherrypy.HTTPRedirect("/")

		_id = getCookie("id")
		if _id == "":
			_id = str(uuid.uuid4())
			addCookie("id", _id)

		sudoku = getCookie("sudoku")
		solution = getCookie("solution")
		if solution != "":
			sudoku = solution

		js=""

		if (sudoku != ""):

			idx = 0
			for i in range(0,9):
				for j in range(0,9):
					val = sudoku[idx]
					pattern = re.compile("^[0-9_]+$")
					while (pattern.match(val) == None):
						idx+=1
						val = sudoku[idx]
					if val == '_':
						val = 0
					else:
						js += "$('.cell[data-i=\""+str(i)+"\"][data-j=\""+str(j)+"\"]').addClass('fixed');\n"
					js += "$('.cell[data-i=\""+str(i)+"\"][data-j=\""+str(j)+"\"]').children('p').text('"+str(val)+"');\n"
					idx+=1

			js+= "$('p').each(function(index) { if(parseInt($(this).text()) != 0) { $(this).show(); }});"
		
		if error != "":
			js+= "openError('"+str(error)+"');"

		head = self.printHead(js)
		body = self.printBody()

		return "<!DOCTYPE HTML>\n<html>\n" + head + body + "\n</html>"

	# called when an .gt file is uploaded
	@cherrypy.expose
	def upload(self, sudoku):

		deleteCookie("solution")

		addCookie('sudoku', sudoku.file.read())

		return self.index(refresh=True)

	# solves the sudoku and writes the return in a cookie
	@cherrypy.expose
	def solve(self):
		cookie = cherrypy.request.cookie

		if "sudoku" not in cookie.keys():
			return self.index(error="Es wurde keine Datei zum lösen hochgeladen!")
		else:
			sudoku = cookie['sudoku'].value
			csolution = (c_int*81)()
			libsa.solve(sudoku, csolution)

		solution = ""
		for el in csolution:
			solution+=str(el)

		if solution == "000000000000000000000000000000000000000000000000000000000000000000000000000000000":
			return self.index(error="Zum eingegebenen Sudoku konnte keine Lösung berechnet werden!")

		cookie = cherrypy.response.cookie
		cookie['solution'] = solution
		cookie['solution']['path'] = '/'
		cookie['solution']['max-age'] = 3600

		return self.index(refresh=True)

	# resets the cookies, start a fresh sudoku
	@cherrypy.expose
	def new(self):

		deleteCookie("solution")
		deleteCookie("sudoku")

		return self.index(refresh=True)

class Images:
	
	# upload mask
	@cherrypy.expose
	def index(self):		
		return """
			<html>
			<body>
				<form action="upload" method="post" enctype="multipart/form-data">
					File: <input type="file" name="sudoku"/> <br/>
					<input type="submit"/>
				</form>
			</body>
			</html>
			"""
	
	# creates file for the image and processes it
	@cherrypy.expose
	def upload(self, sudoku):
		_id = getCookie("id")
		if _id == "":
			_id = str(uuid.uuid4())
			addCookie("id", _id)

		if not os.path.isdir(os.path.join('./', 'tmp/')):
			os.mkdir(os.path.join('./', 'tmp/'))

		filename = os.path.join('/', 'tmp/', _id+'.jpg')

		f = open(filename, "w")

		fileIn = sudoku.file.read()

		f.write(fileIn)

		image = sFunc.open(filename)

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

		trans = sFunc.transform(image, corners)

		sFunc.save(filename, trans)

		return "<img src=\""+filename+"\" alt=\"image\">"


# increase server socket timeout to 60s; we are more tolerant of bad
# quality client-server connections (cherrypy's defult is 10s)
cherrypy.server.socket_timeout = 60

if __name__ == '__main__':
	cherrypy.tree.mount(Images(), '/images')
	cherrypy.quickstart(Sudoku(), '/', 'app.config')