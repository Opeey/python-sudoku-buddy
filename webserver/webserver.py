#!/usr/bin/python
# -*- coding: utf-8 -*-

import cherrypy
import cv2
import sFunc
import os
import re
import numpy as np
import uuid

import cgi
import tempfile

import ctypes
from ctypes import c_int
libsa = ctypes.CDLL("./libsa.so.1.0")

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


def addCookie(key, value):
	cookie = cherrypy.response.cookie

	cookie[key] = value
	cookie[key]['path'] = '/'
	cookie[key]['max-age'] = 3600

def getCookie(key):
	cookie = cherrypy.request.cookie

	if key in cookie.keys():
		return cookie[key].value
	else:
		return ""

def deleteCookie(key):
	cookie = cherrypy.response.cookie
	request = cherrypy.request.cookie

	if key in request.keys():
		cookie[key] = ""
		cookie[key]['expires'] = 0

class myFieldStorage(cgi.FieldStorage):
	"""Our version uses a named temporary file instead of the default
	non-named file; keeping it visibile (named), allows us to create a
	2nd link after the upload is done, thus avoiding the overhead of
	making a copy to the destination filename."""
	
	def make_file(self, binary=None):
		return tempfile.NamedTemporaryFile()


def noBodyProcess():
	"""Sets cherrypy.request.process_request_body = False, giving
	us direct control of the file upload destination. By default
	cherrypy loads it to memory, we are directing it to disk."""
	cherrypy.request.process_request_body = False

cherrypy.tools.noBodyProcess = cherrypy.Tool('before_request_body', noBodyProcess)

class Sudoku(object):
	
	_cp_config = {'request.error_response': reset}

	def printHead(self, js=""):
		return """
			<head>
				<meta charset="utf-8">
				<title>Sudoku</title>
				<link rel="stylesheet" type="text/css" href="css/style.css">
				<script src="js/jquery-2.1.1.min.js" type="text/javascript"></script>
				"""+self.javascript(js)+"""
			</head>
		"""

	def javascript(self, ownCode=""):
		return """
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

	def printBody(self):
		return open(os.path.join('./', 'html/', 'body.html')).read()

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

	@cherrypy.expose
	def upload(self, sudoku):

		deleteCookie("solution")

		addCookie('sudoku', sudoku.file.read())

		return self.index(refresh=True)

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

	@cherrypy.expose
	def new(self):

		deleteCookie("solution")
		deleteCookie("sudoku")

		return self.index(refresh=True)

class myFieldStorage(cgi.FieldStorage):
	"""Our version uses a named temporary file instead of the default
	non-named file; keeping it visibile (named), allows us to create a
	2nd link after the upload is done, thus avoiding the overhead of
	making a copy to the destination filename."""
	
	def make_file(self, binary=None):
		return tempfile.NamedTemporaryFile()


def noBodyProcess():
	"""Sets cherrypy.request.process_request_body = False, giving
	us direct control of the file upload destination. By default
	cherrypy loads it to memory, we are directing it to disk."""
	cherrypy.request.process_request_body = False

cherrypy.tools.noBodyProcess = cherrypy.Tool('before_request_body', noBodyProcess)


class Images:
	
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