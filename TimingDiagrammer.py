#   Copyright (C) 2021, 2022, 2023 Anirban Banerjee
#   
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#   
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#   
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPainter, QPixmap, QPainterPath
from PyQt5.QtWidgets import (
	QApplication, QGraphicsScene,
	QFileDialog, QGraphicsPixmapItem, QMessageBox)
from PyQt5.QtCore import Qt
import sys, os, math
import TimingDiagrammerUI

fontMap = {'sans':'Sans', 'serif':'Serif', 
			'mono':'Monospace', 'fixed': 'Fixed',
			}

#color map has pastel/light values
colorMap = {
	'a': 'antiquewhite', 
	'A': 'aquamarine', 
	'b': 'blue', 
	'B': 'brown', 
	'c': 'lightcyan', 
	'C': 'cornflowerblue', 
	'd': 'skyblue', 
	'D': 'deepskyblue', 
	'g': 'mediumaquamarine', 
	'G': 'springgreen', 
	'h': 'honeydew', 
	'H': 'hotpink', 
	'i': 'indigo', 
	'I': 'indianred', 
	'l': 'lavender', 
	'L': 'lawngreen', 
	'm': 'mistyrose', 
	'M': 'magenta', 
	'k': 'khaki', 
	'o': 'orange',
	'O': 'orchid',
	'p': 'pink', 
	'P': 'peachpuff', 
	'r': 'red', 
	'R': 'rosybrown', 
	's': 'snow',
	't': 'thistle',
	'v': 'violet', 
	'w': 'white',
	'W': 'wheat',
	'x': 'black',
	'y': 'light yellow', 
	'Y': 'yellow', 
	'z': 'plum',
	'Z': 'cornsilk'
}

#text color map has dark color values
textColorMap = {
	'a': 'aqua', 
	'A': 'aquamarine', 
	'b': 'blue', 
	'B': 'brown', 
	'c': 'chocolate', 
	'C': 'crimson', 
	'd': 'darkblue', 
	'D': 'darkred', 
	'g': 'green', 
	'G': 'goldenrod', 
	'h': 'honeydew', 
	'i': 'indigo', 
	'l': 'limegreen', 
	'L': 'lawngreen', 
	'm': 'maroon', 
	'M': 'magenta', 
	'n': 'navy', 
	'k': 'khaki', 
	'o': 'orangered',
	'O': 'olive',
	'p': 'deeppink', 
	'P': 'purple', 
	'r': 'red', 
	'R': 'firebrick', 
	's': 'slateblue',
	't': 'teal',
	'v': 'darkviolet', 
	'V': 'fuchsia', 
	'w': 'darkslategrey',
	'W': 'saddlebrown',
	'x': 'black',
	'y': 'mediumvioletred', 
	'Y': 'gold', 
	'z': 'navy',
	'Z': 'darkorchid'
}

class TimingDiagrammer(QtWidgets.QMainWindow, TimingDiagrammerUI.Ui_TimingDiagrammer):
	def __init__(self, parent=None):
		self.parent = parent
		super(TimingDiagrammer, self).__init__(parent)
		self.setupUi(self)
		self.actionNew.triggered.connect(self.fileNew)
		self.actionOpen.triggered.connect(self.fileOpen)
		self.actionSave.triggered.connect(self.fileSave)
		self.actionSaveAs.triggered.connect(self.fileSaveAs)
		self.actionExport.triggered.connect(self.fileExport)
		self.actionExit.triggered.connect(self.fileExit)
		self.actionAliasing.triggered.connect(self.optionsAliasing)
		self.actionSettings.triggered.connect(self.optionsSettings)
		self.actionAbout.triggered.connect(self.helpAbout)
		self.plainTextEdit.document().setDefaultFont(QtGui.QFont("Monospace", 12, QtGui.QFont.Normal))
		self.plainTextEdit.installEventFilter(self)

		self.setAutoFillBackground(False)
		self.graphicsScene = QGraphicsScene(self)
		self.graphicsScene.setBackgroundBrush(Qt.white);
		fileName = os.path.join(os.path.dirname(os.path.abspath(__file__)), "splash.jpg")
		if os.path.isfile(fileName):
			splash = QGraphicsPixmapItem(QPixmap.fromImage(QImage(fileName)))
			self.graphicsScene.addItem(splash)

		self.graphicsView.setMouseTracking(True)
		self.graphicsView.setScene(self.graphicsScene)
		self.antiAliasedView = False

		if os.name == 'nt':
			import ctypes
			ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'AnirbanBanerjee.TimingDiagrammer.2023.1')
		
		self.resetParameters()
		self.resetVariables()
		
		self.gapPenColor = "#dddddd"
		self.gapPen = QtGui.QPen()
		self.gapPen.setColor(QtGui.QColor(self.gapPenColor))
		self.gapPen.setWidth(7)

		#these two cannot be in resetVariables
		self.currentDirName = os.path.dirname(os.path.abspath(__file__))
		self.currentFileName = 'Untitled.tim'

		self.plainTextEdit.textChanged.connect(self.textChangedHandler)
		self.shortcutNew = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+N'), self)
		self.shortcutNew.activated.connect(self.fileNew)
		self.shortcutOpen = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+O'), self)
		self.shortcutOpen.activated.connect(self.fileOpen)
		self.shortcutSave = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+S'), self)
		self.shortcutSave.activated.connect(self.fileSave)
		self.shortcutExit = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Q'), self)
		self.shortcutExit.activated.connect(self.fileExit)
		self.plainTextEdit.setFocus()
		self.plainTextEdit.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
		self.setWindowTitle("Timing Diagrammer - Untitled.tim")
		#print ("========== sys.argv = ", sys.argv)
		if len(sys.argv) > 1:
			fileName = sys.argv[1]
			self.currentDirName = os.path.dirname(fileName)
			#print ("DEBUG: currentDirName = ", self.currentDirName)
			self.currentFileName = os.path.basename(fileName)
			self.setWindowTitle("Timing Diagrammer - " + self.currentFileName)
			if os.path.isfile(fileName):
				self.fileReadBackend()

	def resetVariables(self):
		#runtime variables
		self.currentLineHasArrow = False
		self.currentLineNumber = 0
		self.yBasisRegistered = 0
		self.timeDelta = 0
		self.editorIsModified = False
		self.pendingArrowDelay = 0
		self.clockEvenOddFlip = 0
		self.directionArrowTailState = 0
		self.directionArrowTail = None
		self.discardModalDialogChars = False
		self.pendingTimeDelta = 0
		self.currentLineArrowLineList = []
		self.currentLineArrowPolyList = []
		self.directionArrowsList = []
		self.overlayAnnotationList = []
		self.currentLineOverlayAnnotationQTextList = []
		self.droppedXCoord = -1
		self.droppedYCoord = -1
		self.maxWaveCount = 0

	def resetParameters(self):
		self.riseClockArrow = False
		self.fallClockArrow = False
		self.evenGridsEnabled = True
		self.oddGridsEnabled = True
		self.clockArrowSize = 15
		self.gridPenColor = "#ff0000"
		self.gridPen = QtGui.QPen(Qt.DotLine)
		self.gridPen.setColor(QtGui.QColor(self.gridPenColor))
		self.gridOtherPenColor = "#0000ff"
		self.gridOtherPen = QtGui.QPen(Qt.DotLine)
		self.gridOtherPen.setColor(QtGui.QColor(self.gridOtherPenColor))

		self.triPenColor = "olive"
		self.triPen = QtGui.QPen(Qt.DashLine)
		self.triPen.setColor(QtGui.QColor(self.triPenColor))
		self.triPen.setWidth(1)

		self.dirArrowPenColor = "blue"
		self.dirArrowPen = QtGui.QPen()
		self.dirArrowPen.setColor(QtGui.QColor(self.dirArrowPenColor))

		self.markerPenColor = "blue"
		self.markerPen = QtGui.QPen()
		self.markerPen.setColor(QtGui.QColor(self.markerPenColor))

		self.gapBrushColor = "#aaaaaa"
		self.gapBrush = QtGui.QBrush(QtGui.QColor(self.gapBrushColor))
		self.gapBrush.setStyle(Qt.BrushStyle(Qt.SolidPattern))

		self.arrowSize = 9
		self.waveHalfDuration = 40
		self.waveTransitionTime = 10
		self.waveHalfPeriod = self.waveHalfDuration + self.waveTransitionTime
		self.sigNameColWidth = 50
		self.sigNameFont = "Sans"
		self.sigNameFontSize = 12
		self.signalNameXSpacing = 50
		self.signalWaveXOffset = 50
		self.signalWaveYOffset = 150
		self.xMargin = 30
		self.yMargin = 50
		self.waveHeight = 30
		self.waveHeightChange = 0
		self.gapHeight = self.waveHeight
		self.signalWaveYSpacing = self.waveHeight
		self.arrowVertOffset = -self.waveHeight/2 - self.signalWaveYSpacing
		self.arrowLineAdjust = self.waveHeight/2
		self.arrowLineEnds = 10
		self.fontName = 'Sans'
		self.fontSize = 10

	def resolvednextC (self, cmd):
		i = 0
		last = chr(0)
		ret = chr(0)
		for c in cmd:
			#print ("for c loop - c = ", c)
			if c in '0123456789|/$':
				i += 1
				last = c
				#print ("c in '0123456789|/$")
				#print("last assigned to ", c)
				#print("A. i = ", i)
				continue
		
			#print("last is seen to be ", last)
			if last == '$':
				last = chr(0)
				#print("B. i = ", i)
				if i < len(cmd) - 1:
					ret = cmd[i+1:i+2]
					if ret not in '0123456789|/$':
						#print ("B. ret = ", ret)
						break
			else:
				ret = c
				break
			i += 1
		return ret

	def drawGrid (self, x0, yBasis, waveCount):
		if self.maxWaveCount == 0:
			#draw the grid
			if (self.evenGridsEnabled == True and (waveCount % 2) == self.clockEvenOddFlip):
				self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration, yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2 + self.waveHeightChange/2, 
					x0 + self.waveHalfDuration, yBasis), self.gridOtherPen)
			elif (self.oddGridsEnabled == True and (waveCount % 2) != self.clockEvenOddFlip):
				self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration, yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
					x0 + self.waveHalfDuration, yBasis), self.gridPen)

	def tdDrawArrowHeadAngle(self, startPoint = (100, 100), direction = (0, 1), size = 9, color = "black"):
		#direction is an angle specified as (height, base) tuple
		#where height/base = tan(angle)
		deg2rad = 3.141592653/180
		height, base = direction
		if base == 0:
			theta = -height * 1.5707963267949
		else:
			theta = -math.atan2(height, base)
		x, y = startPoint
		pointList = [QtCore.QPointF(x, y),
						QtCore.QPointF(x + size * math.cos(160*deg2rad + theta), 
							y + size * math.sin(160*deg2rad + theta)),
						QtCore.QPointF(x + 3 * size * math.cos(180*deg2rad + theta)/5, 
							y + 3 * size * math.sin(180*deg2rad + theta)/5),
						QtCore.QPointF(x + size * math.cos(200*deg2rad + theta), 
							y + size * math.sin(200*deg2rad + theta)),
							QtCore.QPointF(x, y)]

		### startPoint,  direction = (0, 1), size = 9
		p = self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
		p.setZValue(1)

	def tdDrawArrowHead(self, startPoint, direction='L'):
		x, y = startPoint
		yArrowSize = xArrowSize = self.arrowSize
		if direction == 'R':
			yArrowSize = -yArrowSize
			xArrowSize = -xArrowSize

		pointList = [QtCore.QPointF(x, y),
						QtCore.QPointF(x + xArrowSize, y - yArrowSize/2),
						QtCore.QPointF(x + xArrowSize*3/4, y),
						QtCore.QPointF(x + xArrowSize, y + yArrowSize/2),
						QtCore.QPointF(x, y)]

		p = self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("black")))
		self.currentLineArrowPolyList.append(p)
		p.setZValue(1)
					
	def parseFVData(self, annotSpec):
		leftBrktPos = annotSpec.find('[')
		rightBrktPos = annotSpec.find(']')
		if rightBrktPos == -1:
			spec = annotSpec[leftBrktPos + 1:]
		else:
			spec = annotSpec[leftBrktPos + 1: rightBrktPos]

		delay = 0
		width = -1
		color = 'black'
		font = self.fontName
		size = self.fontSize
		vert = 0
		arrow = 0
		center = True

		if spec == '':
			return (delay,
					width,
					color,
					font,
					size,
			        vert,
			        arrow,
					center)

		spec = spec.replace('  ', ' ')
		spec = spec.replace(' =', '=')
		for fvPair in spec.split(' '):
			#print ("parseFVData: fvPair is ", fvPair)
			if fvPair == '':
				continue
			fvPair = fvPair.replace(' ', '')
			fvPair = fvPair.split('=')
			if len(fvPair) < 2:
				continue
			field = fvPair[0]
			value = fvPair[1]
		
			if field == "delay":
				try:
					delay = int(value)
				except:
					delay = 0
			elif field == "width":
				try:
					width = int(value)
				except:
					width = -1
			elif field == "color":
				if value in textColorMap:
					color = textColorMap[value]
				else:
					color = 'black'
			elif field == "font":
				if value in fontMap:
					font = fontMap[value]
				else:
					font = self.fontName
			elif field == "center":
				center = value in "yY"
			elif field == "size":
				try:
					size = int(value)
					if size < 6:
						size = 6
				except:
					size = self.fontSize
			elif field == "vert":
				try:
					vert = int(value)
				except:
					vert = 0
			elif field == "arrow":
				try:
					arrow = int(value)
				except:
					arrow = 0

		return (delay,
				width,
				color,
				font,
				size,
		        vert,
		        arrow,
				center)

	def getFVData(self, annotSpecCmd):
		#print ("getFVData: annotSpecCmd = ", annotSpecCmd)
		attributeMapList = []
		if annotSpecCmd == '':
			#print ("getFVData: null cmd4")
			return attributeMapList
		for step in annotSpecCmd.split(','):
			#print ("step is ", step)
			attributeMap = {}
			attributeMap['delay'] = 0
			attributeMap['width'] = -1
			attributeMap['color'] = 'black'
			attributeMap['font'] = self.fontName
			attributeMap['size'] = self.fontSize
			attributeMap['vert'] = 0
			attributeMap['arrow'] = 0
			attributeMap['center'] = True
			if step == '':
				attributeMapList.append(attributeMap)
				continue
			step = step.replace('  ', ' ')
			step = step.replace(' =', '=')
			#print ("after adj, step is ", step)
			for fvPair in step.split(' '):
				if fvPair == '':
					continue
				fvPair = fvPair.replace(' ', '')
				fvPair = fvPair.split('=')
				if len(fvPair) < 2:
					continue
				field = fvPair[0]
				value = fvPair[1]
				#print ("fvPair is ", fvPair)
		
				if field == "delay":
					try:
						value = int(value)
					except:
						value = 0
					attributeMap['delay'] = int(value)
				elif field == "width":
					try:
						value = int(value)
					except:
						value = -1
					attributeMap['width'] = int(value)
				elif field == "color":
					if value in textColorMap:
						value = textColorMap[value]
					else:
						color = 'black'
					attributeMap['color'] = value
				elif field == "font":
					if value in fontMap:
						attributeMap['font'] = fontMap[value]
					else:
						attributeMap['font'] = self.fontName
				elif field == "center":
					if value in "yY":
						attributeMap['center'] = True
					else:
						attributeMap['center'] = False
				elif field == "size":
					try:
						value = int(value)
						if value < 6:
							value = 6
						#print ("appended fontSize = ", value)
					except:
						value = self.fontSize
						#print ("appended width = 0 default",)
					attributeMap['size'] = int(value)
				elif field == "vert":
					try:
						value = int(value)
					except:
						value = 0
					attributeMap['vert'] = value
					#print ("appended vert = ", value)
				elif field == "arrow":
					try:
						value = int(value)
					except:
						value = 0
					attributeMap['arrow'] = value
					#print ("appended arrow = ", value)

			attributeMapList.append(attributeMap)
	
		#print ("===============================")
		#print ("len attributeMapList = ", len(attributeMapList))
	
		return attributeMapList

	def doAnnotationCmd (self, cmd, annotSpecCmd, updateViewPort = False, charPosWithinCmd = -1):
		attributeMapList = self.getFVData(annotSpecCmd.strip())
		annotNum = 0
		#print ("doAnnotationCmd: cmd = ", cmd)
		#count number of commas in cmd before charPosWithinCmd
		waveNum = -1
		if charPosWithinCmd > 0:
			waveNum = cmd[:charPosWithinCmd].count(',')

		for annot in cmd.split(','):
			annot = annot.replace(chr(1), '#')
			annot = annot.replace(chr(2), ';')
			annot = annot.replace(chr(6), ',')
			#print ("doAnnotationCmd: annot = ", annot, " -- annotNum = ", annotNum)
			if len(attributeMapList) > annotNum:
				delay = attributeMapList[annotNum]['delay']
				width = attributeMapList[annotNum]['width']
				color = attributeMapList[annotNum]['color']
				font = attributeMapList[annotNum]['font']
				size = attributeMapList[annotNum]['size']
				vert = attributeMapList[annotNum]['vert']
				arrow = attributeMapList[annotNum]['arrow']
				center = attributeMapList[annotNum]['center']
			else:
				delay = 0
				width = -1
				color = 'black'
				font = self.fontName
				size = self.fontSize
				vert = 0
				arrow = 0
				center = True

			#print ("@@@ len of self.currentLineArrowPolyList = ", len(self.currentLineArrowPolyList))
			if annotNum == 0 and arrow != 0:
				for l in self.currentLineArrowLineList:
					l.setLine(l.line().x1(), l.line().y1() - arrow, l.line().x2(), l.line().y2() - arrow)
					l.setZValue(1)
				for p in self.currentLineArrowPolyList:
					#print ("@@@@@ polygon = ", p, " arrow = ", arrow)
					poly = p.polygon()
					poly.translate(0, -arrow)
					self.graphicsScene.removeItem(p)
					p = self.graphicsScene.addPolygon(poly, QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("black")))
					p.setZValue(1)

			#print ("@@@@#####@@@@ delay = ", delay, " width = ", width, " color = ", color, " vert = ", vert, " arrow = ", arrow, " -- annot is ", annot)
			if annot != '':
				brktPos = annot.find('[')
				if brktPos > 0:
					#print ("doAnnotationCmd: brktPos > 0 for annot = ", annot)
					(delay, 
					width, 
					color, 
					font, 
					size,
					vert, 
					arrow,
					center) = self.parseFVData(annot[brktPos:])

					#print (delay, 
					#	width, 
					#	color, 
					#	font, 
					#	size,
					#	vert, 
					#	arrow,
					#	center)

					annot = annot[:brktPos]

			if annot != '':
				annot = annot.replace(chr(3), '[')
				updateViewPortLocal = updateViewPort and (annotNum == waveNum or annotNum == waveNum + 1)
				#print ("annotNum = ", annotNum, " waveNum = ", waveNum)
				if self.currentLineHasArrow == True:
					self.putText(annot, self.sigNameColWidth + 
						self.signalWaveXOffset + 
						delay +
						self.waveHalfPeriod * annotNum + (self.waveHalfPeriod/2 if center == True else 0),
						self.yBasisRegistered + self.arrowVertOffset - 1 - vert,
						center, font, size, color, width, True, updateViewPortLocal)
				else:
					self.putText(annot, self.sigNameColWidth + 
						self.signalWaveXOffset + 
						delay +
						self.waveHalfPeriod * annotNum + (self.waveHalfPeriod/2 if center == True else 0),
						self.signalWaveYOffset +
							(self.currentLineNumber - self.linesWithArrow) * (self.waveHeight + self.signalWaveYSpacing) + 
							self.linesWithArrow * self.arrowLineAdjust - self.waveHeight/2 - vert, 
						center, font, size, color, width, False, updateViewPortLocal)
			annotNum += 1

	def processCommand (self, cmd, line, cmdNum, cmd4, whichCommandHasCursor = 0, charPosWithinCmd = -1):
		#print ("DEBUG ZZ cmd is ", cmd, "line value passed is ", line, "cmdNum = ", cmdNum)
		#if whichCommandHasCursor != 0:
			#print ("processCommand: cmdNum = ", cmdNum, "cmd = ", cmd, "whichCommandHasCursor = ", whichCommandHasCursor, " --- cursorIsOnThisLine = ", cursorIsOnThisLine)
		if cmdNum == 1:
			#process signal name
			#simplifies parsing multi-char tokens
			cmd = cmd.replace(chr(1), '#')
			cmd = cmd.replace(chr(2), ';')
			cmd = cmd.replace(chr(6), ',')
			self.tdDrawSigNamesText(cmd, whichCommandHasCursor == 1)
		elif cmdNum == 2:
			xCurrent = 0
			yCurrent = 0
			#process waves
			self.currentLineArrowLineList = []
			self.currentLineHasArrow = False
			if cmd.find('<') >= 0 or cmd.find('-') >= 0 or cmd.find('>') >= 0:
				self.currentLineHasArrow = True
			self.riseClockArrow = False
			self.fallClockArrow = False
			waveCount = 0
			self.invertedClockHeight = 0
			self.currentColor = 'w'
			cNum = 0
			cmd = cmd.strip()
			lastC = chr(0)
			lLastC = chr(0)
			#print ("-- seeing cmd = ", cmd, " linesWithArrow = ", self.linesWithArrow)
			#print ("------------------------------")
			for thisC in cmd:
				#print ("processCmd-mainloop: charPosWithinCmd=", charPosWithinCmd, " cNum=", cNum, " waveCount = ", waveCount)
				#print ("processCmd-mainloop: thisC=", thisC, " ord(lastC) ... lastC=", ord(lastC), lastC)
				if lastC == '$':
					#print ("processCmd-mainloop: lastC was $")
					cNum += 1
					#if thisC != 'x':
					self.currentColor = thisC
					#else:
					#	#illegal color 'x', set to 'white'
					#	self.currentColor = 'w'
					if thisC not in colorMap.keys():
						self.label.setText("Error: Wrong color code: " + thisC + ".")
						
					#print ("self.currentColor == ", self.currentColor)
					lastC = lLastC #restore from stored variable with value previous to $
					lLastC = chr(0)
					continue

				if thisC == '$':
					#print ("processCmd-mainloop: thisC is $")
					cNum += 1
					lLastC = lastC #store thisC previous to $
					lastC = '$'
					continue
				
				if cNum < len(cmd) - 1: 
					nextC = self.resolvednextC(cmd[cNum + 1:])
				else:
					nextC = chr(0)
				#print ("processCmd-mainloop: thisC == ", thisC)
				#print ("processCmd-mainloop: nextC == ", nextC)
				
				xBasis = self.signalWaveXOffset + self.sigNameColWidth + self.waveHalfPeriod * waveCount
				yBasis = self.signalWaveYOffset + (self.currentLineNumber - self.linesWithArrow) *\
					(self.waveHeight + self.signalWaveYSpacing) + self.linesWithArrow * self.arrowLineAdjust
				self.yBasisRegistered = yBasis

				#print ("processCommand: A. thisC = ", thisC, " lastC = ", lastC, " pendingTimeDelta = ", self.pendingTimeDelta)
				if thisC not in "DXz0123456789/<->|+dx" or (thisC in "dx" and lastC not in "RFDXz"): 
					#for meta chars, don't reset since following chars will decide
					#for DXz, pendingTimeDelta will be used and pendingTimeDelta will be assigned from timeDelta at end of function
					#for dx, pendingTimeDelta will be used only if the last char was R or F 
					#and pendingTimeDelta will be set to 0 at the end of the function
					self.pendingTimeDelta = 0
					#print ("B. thisC = ", thisC, " self.pendingTimeDelta reset to ", self.pendingTimeDelta)
				#print ("processCommand: B. thisC = ", thisC, " lastC = ", lastC, " pendingTimeDelta = ", self.pendingTimeDelta)

				if thisC == '|':
					if waveCount > 0 or self.timeDelta > 0:
						if self.currentColor in textColorMap:
							self.markerPen.setColor(QtGui.QColor(textColorMap[self.currentColor]))
						else:
							self.markerPen.setColor(QtGui.QColor(self.markerPenColor))
						#x0 = xBasis
						#x0 = xBasis + self.waveHalfPeriod + self.timeDelta
						x0 = xBasis + self.timeDelta
						if waveCount != 0:
							x0 -= self.waveTransitionTime/2
						#print ("saw | -- X = ", x0, " -- waveCount = ", waveCount, " -- xBasis = ", xBasis, " -- self.timeDelta", self.timeDelta)
						l = self.graphicsScene.addLine(QtCore.QLineF(x0,
							yBasis - self.waveHeight - self.waveHeight,
							x0,
							yBasis + self.waveHeight/4), self.markerPen)
						l.setZValue(3) #topmost
					self.timeDelta = 0
				elif thisC in 'PpCcKkQq': #clock pulses
					#print ("processCommand: thisC = ", thisC, " ord (nextC) = ", ord(nextC))
					if thisC == "Q":
						self.riseClockArrow = True
						self.fallClockArrow = True
						self.tdDrawClock(waveCount, lastC, 'P', 'Pp'['CcKkQq'.find(nextC)%2], (xBasis, yBasis), nextC==chr(0))
					elif thisC == "q":
						self.riseClockArrow = True
						self.fallClockArrow = True
						self.tdDrawClock(waveCount, lastC, 'p', 'Pp'['CcKkQq'.find(nextC)%2], (xBasis, yBasis), nextC==chr(0))
					elif thisC == "K":
						self.riseClockArrow = False
						self.fallClockArrow = True
						self.tdDrawClock(waveCount, lastC, 'P', 'Pp'['CcKkQq'.find(nextC)%2], (xBasis, yBasis), nextC==chr(0))
					elif thisC == "k":
						self.riseClockArrow = False
						self.fallClockArrow = True
						self.tdDrawClock(waveCount, lastC, 'p', 'Pp'['CcKkQq'.find(nextC)%2], (xBasis, yBasis), nextC==chr(0))
					elif thisC == "C":
						self.riseClockArrow = True
						self.fallClockArrow = False
						self.tdDrawClock(waveCount, lastC, 'P', 'Pp'['CcKkQq'.find(nextC)%2], (xBasis, yBasis), nextC==chr(0))
					elif thisC == "c":
						self.riseClockArrow = True
						self.fallClockArrow = False
						self.tdDrawClock(waveCount, lastC, 'p', 'Pp'['CcKkQq'.find(nextC)%2], (xBasis, yBasis), nextC==chr(0))
					else:
						self.riseClockArrow = False
						self.fallClockArrow = False
						self.tdDrawClock(waveCount, lastC, thisC, 'Pp'['CcKkQq'.find(nextC)%2], (xBasis, yBasis), nextC==chr(0))
					waveCount += 2
					self.timeDelta = 0
				elif thisC in 'rR': 
					self.tdDrawRise(waveCount, thisC, nextC, (xBasis, yBasis))
					waveCount += 1
					self.timeDelta = 0
				elif thisC in 'fF':
					self.tdDrawFall(waveCount, thisC, nextC, (xBasis, yBasis))
					waveCount += 1
					self.timeDelta = 0
				elif thisC in 'DX':
					self.tdDrawDataDX(waveCount, lastC, thisC, nextC, (xBasis, yBasis))
					waveCount += 1
					self.timeDelta = 0
				elif thisC in 'dx': #lower case
					self.tdDrawDatadx(waveCount, lastC, thisC, nextC, (xBasis, yBasis))
					waveCount += 1
					self.timeDelta = 0
				elif thisC == 'l': #lower case
					self.tdDrawLow(waveCount, nextC, lastC, (xBasis, yBasis))
					waveCount += 1
					self.timeDelta = 0
				elif thisC == 'h': #lower case
					self.tdDrawHigh(waveCount, nextC, (xBasis, yBasis))
					waveCount += 1
					self.timeDelta = 0
				elif thisC == 'z': #lower case
					self.tdDrawTri(waveCount, nextC, (xBasis, yBasis))
					waveCount += 1
					self.timeDelta = 0
				elif thisC == 'S':
					#char to draw the grid lines, but does not advance waveCount
					#does not add space
					self.tdDrawSpace(waveCount, cmd, (xBasis, yBasis))
					self.timeDelta = 0
				elif thisC == 's':
					self.tdDrawSpace(waveCount, cmd, (xBasis, yBasis))
					waveCount += 1
					self.timeDelta = 0
				elif thisC == '<' or thisC == '>' or thisC == '-':
					self.tdDrawHorizArrow(waveCount, thisC, nextC, (xBasis, yBasis))
					if thisC != '>':
						waveCount += 1
					self.timeDelta = 0
				elif thisC in "0123456789":
					#print (" -- additional delay = ", self.timeDelta)
					#a number follows a command for additional delay
					if thisC == '0' and nextC in "|<->":
						self.timeDelta = 10 * self.waveHalfDuration / 9
					else:
						self.timeDelta = int(thisC) * self.waveHalfDuration / 9
					#print (" -- additional delay set to = ", self.timeDelta)
				elif thisC == '/':
					self.tdDrawGap(waveCount, lastC, nextC, (xBasis, yBasis))
				else:
					#print ("Error: Wrong code: " + thisC + ".")
					self.label.setText("Error: Wrong code: " + thisC + ".")

				# vertical line on the signal name
				self.graphicsScene.addLine(QtCore.QLineF(self.signalWaveXOffset + self.sigNameColWidth, 
					yBasis - self.signalWaveYSpacing - self.waveHeight, 
					self.signalWaveXOffset + self.sigNameColWidth, 
					yBasis + self.waveHeight))
				
				if thisC not in '0123456789/|':
					#print ("char is NOT FWDSLASH -- thisC = ", thisC)
					lastC = thisC

				if whichCommandHasCursor == 2:
					if charPosWithinCmd == cNum or charPosWithinCmd == cNum + 1:
						xCurrent = xBasis
						yCurrent = yBasis
						#print ("==== snapshot xCurrent = ", xCurrent, "==== snapshot yCurrent = ", yCurrent)
				cNum += 1

			#for
			if whichCommandHasCursor == 2 and xCurrent > 0:
				#print ("processCommand: yCurrent = ", yCurrent, " self.currentLineNumber = ", self.currentLineNumber)
				self.graphicsView.centerOn(xCurrent, yCurrent) 

			#print ("-- cmdNum is 2 -- A seeing cmd = ", cmd, " self.currentLineHasArrow = ", self.currentLineHasArrow)
			if self.currentLineHasArrow == True:
				self.linesWithArrow += 1

			#anchor/
			xCurrent = self.signalWaveXOffset + self.sigNameColWidth + self.waveHalfPeriod * waveCount
			yCurrent = self.signalWaveYOffset + (self.currentLineNumber - self.linesWithArrow) *\
				(self.waveHeight + self.signalWaveYSpacing) + self.linesWithArrow * self.arrowLineAdjust
			self.graphicsScene.addLine(QtCore.QLineF(xCurrent + self.waveHalfPeriod + self.xMargin, 
								yCurrent + self.waveHeight + self.yMargin,  
								xCurrent + self.waveHalfPeriod + self.xMargin + 1, 
								yCurrent + self.waveHeight + self.yMargin + 1), 
								QtGui.QPen(Qt.transparent)) 
				
			self.timeDelta = 0

		elif cmdNum == 3:
			cmd = cmd.replace('\[', chr(3))
			#print ("-- B seeing cmd = ", cmd, "-- seeing cmd4 = ", cmd4, " self.currentLineHasArrow = ", self.currentLineHasArrow)
			self.doAnnotationCmd (cmd, cmd4, whichCommandHasCursor == 3, charPosWithinCmd)
			#print ("-- B self.linesWithArrow = ", self.linesWithArrow)
		#print ("==============================================================================================")

	def processDirective (self, data):
		#print ("processDirective: data is ", data)
		directiveList = data.strip().split(' ')
		#print ("processDirective: directiveList[] is ", directiveList)
		if directiveList[0] == "grid":
			#print ("----show grid directive found")
			if len(directiveList) > 1:
				if directiveList[1] == "off" or directiveList[1] == "none":
					self.evenGridsEnabled = False
					self.oddGridsEnabled = False
				elif directiveList[1] == "both":
					self.evenGridsEnabled = True
					self.oddGridsEnabled = True
				elif directiveList[1] == "odd":
					self.evenGridsEnabled = False
					self.oddGridsEnabled = True
				elif directiveList[1] == "even":
					self.evenGridsEnabled = True
					self.oddGridsEnabled = False
				else:
					try:
						self.maxWaveCount = int(directiveList[1])
					except:
						self.maxWaveCount = 0
		elif directiveList[0] == "margin":
			#print ("----show grid directive found")
			if len(directiveList) > 2:
				try:
					val2 = int(directiveList[2])
				except:
					val2 = 0
				if directiveList[1] == "top":
					if val2 < 50 or val2 > 300:
						val2 = 150
					self.signalWaveYOffset = val2
				elif directiveList[1] == "signal":
					if val2 < 46 or val2 > 100:
						val2 = 50
					self.signalWaveXOffset = val2
				elif directiveList[1] == "side":
					if val2 < 20 or val2 > 100:
						val2 = 30
					self.xMargin = val2
				elif directiveList[1] == "bottom":
					if val2 < 20 or val2 > 200:
						val2 = 50
					self.yMargin = val2
		elif directiveList[0] == "color":
			if len(directiveList) > 1:
				if directiveList[1] == "dirarr":
					#print ("----color debug directive found")
					if len(directiveList) > 2:
						#print ("----color debug directive found, directiveList[2] = ", directiveList[2], " len = ", len(directiveList[2]))
						if directiveList[2].find('#') == 0:
							self.dirArrowPenColor = directiveList[2]
						elif directiveList[2] in textColorMap:
							#print ("----color debug directive found in textColorMap")
							self.dirArrowPenColor = textColorMap[directiveList[2]]
						elif directiveList[2] in colorMap:
							#print ("----color debug directive found in colorMap")
							self.dirArrowPenColor = colorMap[directiveList[2]]
						else:
							return
						self.dirArrowPen.setColor(QtGui.QColor(self.dirArrowPenColor))
				elif directiveList[1] == "tri":
					if len(directiveList) > 2:
						if directiveList[2].find('#') == 0:
							self.triPenColor = directiveList[2]
						elif directiveList[2] in textColorMap:
							self.triPenColor = textColorMap[directiveList[2]]
						elif directiveList[2] in colorMap:
							self.triPenColor = colorMap[directiveList[2]]
						else:
							return
						self.triPen.setColor(QtGui.QColor(self.triPenColor))
				elif directiveList[1] == "gap":
					if len(directiveList) > 2:
						if directiveList[2].find('#') == 0:
							self.gapBrushColor = directiveList[2]
						elif directiveList[2] in textColorMap:
							self.gapBrushColor = textColorMap[directiveList[2]]
						elif directiveList[2] in colorMap:
							self.gapBrushColor = colorMap[directiveList[2]]
						else:
							return
						self.gapBrush.setColor(QtGui.QColor(self.gapBrushColor))
				elif directiveList[1] == "grid":
					if len(directiveList) > 3:
						if directiveList[2] == "both":
							if directiveList[3].find('#') == 0:
								self.gridOtherPenColor = self.gridPenColor = directiveList[3]
							elif directiveList[3] in textColorMap:
								self.gridOtherPenColor = self.gridPenColor = textColorMap[directiveList[3]]
							elif directiveList[3] in colorMap:
								self.gridOtherPenColor = self.gridPenColor = colorMap[directiveList[3]]
							else:
								return
							self.gridPen.setColor(QtGui.QColor(self.gridPenColor))
							self.gridOtherPen.setColor(QtGui.QColor(self.gridOtherPenColor))
						elif directiveList[2] == "odd":
							if directiveList[3].find('#') == 0:
								self.gridPenColor = directiveList[3]
							elif directiveList[3] in textColorMap:
								self.gridPenColor = textColorMap[directiveList[3]]
							elif directiveList[3] in colorMap:
								self.gridPenColor = colorMap[directiveList[3]]
							else:
								return
							self.gridPen.setColor(QtGui.QColor(self.gridPenColor))
						elif directiveList[2] == "even":
							if directiveList[3].find('#') == 0:
								self.gridOtherPenColor = directiveList[3]
							elif directiveList[3] in textColorMap:
								self.gridOtherPenColor = textColorMap[directiveList[3]]
							elif directiveList[3] in colorMap:
								self.gridOtherPenColor = colorMap[directiveList[3]]
							else:
								return
							self.gridOtherPen.setColor(QtGui.QColor(self.gridOtherPenColor))
					elif len(directiveList) > 2:
						if directiveList[2].find('#') == 0:
							self.gridOtherPenColor = self.gridPenColor = directiveList[2]
						elif directiveList[2] in textColorMap:
							self.gridOtherPenColor = self.gridPenColor = textColorMap[directiveList[2]]
						elif directiveList[2] in colorMap:
							self.gridOtherPenColor = self.gridPenColor = colorMap[directiveList[2]]
						else:
							return
						self.gridPen.setColor(QtGui.QColor(self.gridPenColor))
						self.gridOtherPen.setColor(QtGui.QColor(self.gridOtherPenColor))
					#print ("self.gridPenColor = ", self.gridPenColor)
					#print ("self.gridOtherPenColor = ", self.gridOtherPenColor)
		else:
			if len(directiveList) > 1:
				try:
					val2 = int(directiveList[1])
				except:
					val2 = 0
			else:
				val2 = 0
			#print ("val2 = ", val2)
			if val2 > 20 and directiveList[0] == "height":
				self.waveHeightChange = self.waveHeight #store the old value
				self.waveHeight = val2
				self.waveHeightChange -= self.waveHeight #subract the new value
				self.gapHeight = self.waveHeight
				self.signalWaveYSpacing = self.waveHeight
				self.arrowVertOffset = -self.waveHeight/2 - self.signalWaveYSpacing
				self.arrowLineAdjust = self.waveHeight/2
			elif val2 > 39 and directiveList[0] == "tick":
				#print ("processDirective: directiveList[0] is tick = ", directiveList[0])
				#print ("-- processDirective: setting self.waveHalfPeriod")
				self.waveHalfPeriod = val2 / 2
				self.waveHalfDuration = self.waveHalfPeriod - self.waveTransitionTime
				#print ("-- processDirective: self.waveHalfPeriod = ", self.waveHalfPeriod)
			elif val2 > 1 and directiveList[0] == "tran":
				self.waveTransitionTime = val2
				self.waveHalfDuration = self.waveHalfPeriod - self.waveTransitionTime
			elif directiveList[0] == "font":
				#print ("--Found !set -- font = ", val2)
				if len(directiveList) > 1:
					val2 = directiveList[1]
				else:
					val2 = 'Sans'
				if val2 != '':
					self.sigNameFont = val2
				else:
					val2 = 'Courier'
			elif directiveList[0] == "fontsize":
				if len(directiveList) > 2:
					try:
						val2 = int(directiveList[2])
					except:
						val2 = 12
					if val2 > 8 and val2 < 72:
						self.sigNameFontSize = val2
					else:
						self.sigNameFontSize = 12
				else:
					self.sigNameFontSize = 12
			elif directiveList[0] == "clockarrow":
				if len(directiveList) > 1:
					try:
						val2 = int(directiveList[1])
					except:
						self.clockArrowSize = 15

					if val2 > 7 and val2 < 25:
						self.clockArrowSize = val2
					else:
						self.clockArrowSize = 15
				else:
					self.clockArrowSize = 15
			elif directiveList[0] == "arrow":
				if len(directiveList) > 1:
					try:
						val2 = int(directiveList[1])
					except:
						self.arrowSize = 9
					if val2 > 7 and val2 < 25:
						self.arrowSize = val2
					else:
						self.arrowSize = 9
				else:
					self.arrowSize = 9
			elif directiveList[0] == "arrowmarker":
				if len(directiveList) > 1:
					try:
						val2 = int(directiveList[1])
					except:
						self.arrowLineEnds = 10

					if val2 > 5 and val2 < 50:
						self.arrowLineEnds = val2
					else:
						self.arrowLineEnds = 10
				else:
					self.arrowLineEnds = 10

	def drawWaves1Line (self, line, data, cursorIsOnThisLine = False, currentColumn = -1):
		if self.clockEvenOddFlip == 1:
			#if already swapped, correct to original pen colors (red/blue)
			self.gridPen, self.gridOtherPen = self.gridOtherPen, self.gridPen
			self.clockEvenOddFlip = 0
		self.pendingArrowDelay = 0
		dataList = data.strip().split(';')
		#print ("drawWaves1Line: dataList = ", dataList)
		cmdNum = 1
		self.currentLineArrowLineList = []
		self.currentLineArrowPolyList = []
		commandBoundary = 0
		lastCommandBoundary = 0
		whichCommandHasCursor = 0
		cmd1Len = 0
		for cmd in dataList:
			####if cmd.find('some text data') >= 0 or cmd.find('AOIR1') >= 0:
			if cmdNum == 1:
				cmd1Len = len(cmd)

			newPos = cmd.rfind('+')
			if newPos >= 0:
				self.directionArrowsList.append(cmd[newPos + 1:])
				return 0

			newPos = cmd.rfind('^')
			if newPos >= 0:
				self.overlayAnnotationList.append(cmd[newPos + 1:])
				return 0

			cmd4 = ''
			self.pendingTimeDelta = 0
			self.currentLineNumber = line #NOTE, starts at 0
					
			if cmdNum == 3 and len(dataList) == 4:
				#for the annotation command, send annot params in cmd4
				cmd4 = dataList[3]
			#print ("cmd4 is ", cmd4, "line value passed is ", line, "cmdNum = ", cmdNum)
			commandBoundary += len(cmd) + 1 #the semicolon is also counted
			#print ("drawWaves1Line:  -- commandBoundary = ", commandBoundary)
			if currentColumn < commandBoundary and cursorIsOnThisLine == True:
				if whichCommandHasCursor == 0:
					#only first match
					whichCommandHasCursor = cmdNum

			self.processCommand(cmd, line, cmdNum, cmd4, whichCommandHasCursor, currentColumn - lastCommandBoundary) 
			cmdNum += 1
			lastCommandBoundary = commandBoundary
			if cmdNum > 3:
				break

		return 1

	def currentDrawnBlock(self, currentBlock):
		drawnBlock = 0
		lastBlock = self.plainTextEdit.document().blockCount()
		for i in range (0, lastBlock):
			if i == currentBlock:
				break
			data = self.plainTextEdit.document().findBlockByNumber(i).text().strip()
			if data.find('#') != 0:
				drawnBlock += 1
		return drawnBlock

	def fillAllGrids(self):
		for i in range(self.maxWaveCount):
			xBasis = self.signalWaveXOffset + self.sigNameColWidth + self.waveHalfPeriod * i
			yBasis = self.signalWaveYOffset + (self.currentLineNumber - self.linesWithArrow) *\
				(self.waveHeight + self.signalWaveYSpacing) + self.linesWithArrow * self.arrowLineAdjust
			#draw the grid
			if (i % 2) == 0:
				l = self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 + self.waveHalfDuration, 
					yBasis - self.waveHeight - self.signalWaveYSpacing, 
					xBasis + self.waveTransitionTime/2 + self.waveHalfDuration, 
					yBasis), self.gridOtherPen)
				l.setZValue(-1)
			elif (i % 2) == 1:
				l = self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 + self.waveHalfDuration, 
					yBasis - self.waveHeight - self.signalWaveYSpacing, 
					xBasis + self.waveTransitionTime/2 + self.waveHalfDuration, 
					yBasis), self.gridPen)
				l.setZValue(-1)

		#do anchor
		self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveHalfPeriod + self.xMargin, yBasis,  
			xBasis + self.waveHalfPeriod + self.xMargin, yBasis), QtGui.QPen(Qt.transparent)) 

	def reDrawCanvas (self, keyVal=''):
		self.directionArrowsList = []
		self.overlayAnnotationList = []
		self.graphicsView.setAlignment(Qt.AlignTop | Qt.AlignLeft)
		currentBlock, currentColumn = self.getTextCursorPos()
		if currentColumn == 0:
			#return was pressed and at start of new line
			yCurrent = self.signalWaveYOffset + self.currentDrawnBlock(currentBlock) * (self.waveHeight + self.signalWaveYSpacing)
			self.graphicsView.centerOn(
				0, yCurrent)
			data = self.plainTextEdit.document().findBlockByNumber(currentBlock).text()

		self.graphicsScene.clear()
		self.linesWithArrow = 0
		lastBlock = self.plainTextEdit.document().blockCount()
		dataArray = []
		line = 0
		
		acceptDirective = True
		for i in range (0, lastBlock):
			data = self.plainTextEdit.document().findBlockByNumber(i).text()
			if data.strip() == '':
				continue
			#print ("reDrawCanvas: A. acceptDirective = ", acceptDirective, " self.waveHalfPeriod = ", self.waveHalfPeriod)
			#if i == lastBlock - 1:
			#	data += keyVal
			if acceptDirective == True:
				if data.strip().find('#!') == 0:
					if data[2:] != '':
						self.processDirective(data[2:])
					#print ("reDrawCanvas: B. acceptDirective = ", acceptDirective, " self.waveHalfPeriod = ", self.waveHalfPeriod)
					continue
			data = data.replace('\#', chr(1)) #replace literal '#' before separating comments
			data = data.replace('\;', chr(2)) #replace literal ';' before separating comments
			data = data.replace('\,', chr(6)) #replace literal ','
			#print ("========DATALIST = ", dataList)
			command = data.split('#')[0] #allow all leading and trailing spaces
			#print ("==============command = ", command)
			if command != '':
				acceptDirective = False
				cursorIsOnThisLine = (currentBlock == i)
				#print ("==============calling drawWaves1Line... currentBlock = ", currentBlock, " cursorIsOnThisLine = ", cursorIsOnThisLine, " i = ", i)
				if self.maxWaveCount > 0:
					self.fillAllGrids()
				line += self.drawWaves1Line (line, command, cursorIsOnThisLine, currentColumn)
				#line += 1
				self.waveHeightChange = 0

		#print the overlaid annotation
		#print ("reDrawCanvas: currentLineOverlayAnnotationQTextList entry count = ", len(self.currentLineOverlayAnnotationQTextList))
		#print ("reDrawCanvas: overlayAnnotationList entry count = ", len(self.overlayAnnotationList))
		for qtext in self.currentLineOverlayAnnotationQTextList:
			#print ("reDrawCanvas: removed currentLineOverlayAnnotationQTextList entry = ", qtext)
			try:
				self.graphicsScene.removeItem(qtext)
			except:
				pass

		self.currentLineOverlayAnnotationQTextList = []

		for s in self.overlayAnnotationList:
			x0, y0, annot = 0, 0, ''
			try:
				l =  s.split(' ')
				x0, y0 = l[0], l[1]
				annot = ' '.join(l[2:])
			except:
				x0, y0, annot = -1, -1, ''

			if x0 != -1:
				self.tdPrintOverlayAnnot (x0, y0, annot)


		#draw the direction arrows
		for s in self.directionArrowsList:
			#print("DEBUG: self.directionArrowsList = ", self.directionArrowsList)
			x0, y0, x1, y1, xm, ym = 0, 0, 0, 0, 0, 0
			try:
				[x0, y0, x1, y1, xm, ym] = s.split(' ')
			except:
				try:
					[x0, y0, x1, y1] = s.split(' ')
				except:
					[x0, y0, x1, y1] = [-1, -1, -1, -1]
			try:
				x0 = int(x0)
			except:
				x0 = -1
			try:
				y0 = int(y0)
			except:
				y0 = x0
			try:
				x1 = int(x1)
			except:
				x1 = x0
			try:
				y1 = int(y1)
			except:
				y1 = y0
			try:
				xm = int(xm)
			except:
				xm = (x0 + x1)/2
			try:
				ym = int(ym)
			except:
				ym = (y0 + y1)/2
			
			if x0 != -1:
				if xm == 0:
					xm = (x0 + x1)/2
				if ym == 0:
					ym = (y0 + y1)/2
				self.tdDrawDirectionArrow (x0, y0, x1, y1, xm, ym)
		
		#print ("=======================================================\n")
		#anchor
		rect = QtCore.QRectF(self.graphicsScene.itemsBoundingRect())
		self.graphicsScene.setSceneRect(rect)


	def getTextCursorPos(self):
		qcursor = self.plainTextEdit.textCursor()
		block = qcursor.blockNumber()
		column = qcursor.columnNumber()
		return block, column

	def textChangedHandler(self, event=None):
		self.editorIsModified = True
		self.setWindowTitle("Timing Diagrammer - " + self.currentFileName + " [modified]")
		self.plainTextEdit.ensureCursorVisible()
		self.reDrawCanvas()
		self.label.setText("Status: Ready")

	def closeEvent(self, event):
		#print ("closeEvent: self.editorIsModified = ", self.editorIsModified)
		if self.editorIsModified == True:
			qm = QMessageBox()
			qm.setIcon(QMessageBox.Question)
			ret = qm.question(self,'Unsaved code', "Code has not been saved. Save?", qm.Yes | qm.No)
			if ret == qm.Yes:
				success = self.fileSave(None)
				if success:
					msg = QMessageBox()
					msg.setIcon(QMessageBox.Information)
					msg.setText("Saved file " + os.path.join(self.currentDirName, self.currentFileName) + ".")
					msg.setWindowTitle("File Write Completed")
					msg.exec_()
		self.close()

	def mousePressEvent(self, event):
		if event.button() == Qt.LeftButton:
			pos = self.graphicsView.mapToScene(event.pos())
			#print ("DEBUG mouse left pos = ", pos)
			modifiers = QtGui.QGuiApplication.keyboardModifiers()
			if self.graphicsView.hasFocus() and modifiers == QtCore.Qt.ControlModifier:
				qcursor = self.plainTextEdit.textCursor()
				#qcursor.insertText(str(x) + ' ' + str(y) + ' ')
				x = int(pos.x())
				y = int(pos.y())
				qcursor.insertText(str(x) + ' ' + str(y) + ' ')
				if self.directionArrowTailState == 0:
					#print ("DEBUG mouse left pos = ", pos, " self.directionArrowTailState is 0")
					self.directionArrowTail = QtWidgets.QGraphicsEllipseItem(x - 5, y - 5, 10, 10);
					self.directionArrowTail.setBrush(QtGui.QColor(self.dirArrowPenColor))
					self.directionArrowTail.setPen(QtGui.QColor(self.dirArrowPenColor))
					self.graphicsScene.addItem(self.directionArrowTail)
					self.directionArrowTailState = 1
				elif self.directionArrowTailState == 1:
					self.directionArrowTailState = 2
				else:
					#optional middle arrow point for bezier curve
					self.directionArrowTailState = 0

	def eventFilter(self, obj, event):
		eventType = event.type()
		if (obj is self.plainTextEdit and self.plainTextEdit.hasFocus()) or (obj is self.graphicsView and self.graphicsView.hasFocus()):
			modifiers = QtGui.QGuiApplication.keyboardModifiers()
			eventKey = eventText = None
			if eventType == QtCore.QEvent.KeyPress or eventType == QtCore.QEvent.KeyRelease:
				eventKey = event.key()
				eventText = event.text()

			if eventType == QtCore.QEvent.KeyPress:
				if (modifiers == QtCore.Qt.ControlModifier and eventKey == Qt.Key_V):
					print ("DEBUG eventFilter: CTRL-V")
					#self.editorIsModified = True
					#self.setWindowTitle("Timing Diagrammer - " + self.currentFileName + " [modified]")
				elif (modifiers == QtCore.Qt.ControlModifier and (eventKey == Qt.Key_C or eventKey == Qt.Key_S)):
					print ("DEBUG eventFilter: CTRL-C or CTRL-S")
				elif eventText != '' and eventText != None:
					#print ("eventFilter: eventText = ", ord(eventText), "  obj", obj)
					if ord(eventText) < 128 and eventKey != Qt.Key_Escape:
						if self.discardModalDialogChars == True:
							#an enter or escape from fileSaveAs dialog can cause editorIsModified to be set to True
							self.discardModalDialogChars = False
						else:
							#key press after second mouse click
							if self.directionArrowTailState != 0:
								self.directionArrowTailState = 0

							self.editorIsModified = True
							self.setWindowTitle("Timing Diagrammer - " + self.currentFileName + " [modified]")
							#print ("eventFilter: self.editorIsModified is set to True")

		return super(TimingDiagrammer, self).eventFilter(obj, event)
	
	def fileNew (self, event=None):
		if self.editorIsModified == True:
			qm = QMessageBox()
			qm.setIcon(QMessageBox.Question)
			ret = qm.question(self,'Buffer Save Dialog', "Buffer contents have not been saved. Save?", qm.Yes | qm.No | qm.Cancel)
			if ret == qm.Cancel:
				return
			elif ret == qm.Yes:
				if self.currentFileName != 'Untitled.tim' and os.path.isfile(self.currentFileName):
					self.writeCurrentFileBackend()
			else:
				pass
				#print ("Buffer Save Dialog question returned = NO = ", ret)
		self.graphicsScene.clear()
		self.plainTextEdit.clear()
		self.resetParameters()
		self.resetVariables()
		#print ("fileNew: self.editorIsModified is set to False = ", self.editorIsModified)
		self.setWindowTitle("Timing Diagrammer - Untitled.tim")
		self.graphicsView.setAlignment(Qt.AlignCenter)
		fileName = os.path.join(os.path.dirname(os.path.abspath(__file__)), "splash.jpg")
		if os.path.isfile(fileName):
			splash = QGraphicsPixmapItem(QPixmap.fromImage(QImage(fileName)))
			self.graphicsScene.addItem(splash)


	def fileOpen (self, event=None):
		#print ("fileOpen: self.fileOpen = ", self.editorIsModified)
		if self.editorIsModified == True:
			qm = QMessageBox()
			qm.setIcon(QMessageBox.Question)
			ret = qm.question(self,'Buffer Save Dialog', "Buffer contents have not been saved. Save?", qm.Yes | qm.No | qm.Cancel)
			if ret == qm.Cancel:
				return
			elif ret == qm.Yes:
				self.fileSave(None)

		self.expandDir()
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fDialog = QFileDialog()
		fDialog.setDirectory(self.currentDirName)
		fileName, _ = fDialog.getOpenFileName(self,"Open Timing Diagrammer File", "","*.tim", options=options)

		if fileName == '':
			return
		if not os.path.isfile(fileName):
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Error: File " + fileName + " not found.")
			msg.setWindowTitle("File Not Found Error")
			msg.exec_()
			return

		self.currentDirName = os.path.dirname(fileName)
		self.currentFileName = os.path.basename(fileName)
		self.resetParameters()
		self.resetVariables()
		self.fileReadBackend()
		self.discardModalDialogChars = True

	def fileReadBackend(self):
		#print ("fileReadBackend: self.currentDirName, self.currentFileName = ", self.currentDirName, self.currentFileName)

		fullFileName = os.path.join(self.currentDirName, self.currentFileName)
		try:
			with open(fullFileName, 'r', encoding="utf-8", newline='\n') as f:
				self.plainTextEdit.setPlainText(f.read())
				f.close()
				self.editorIsModified = False
			self.reDrawCanvas()
		except:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Error: Could not read from file " + fullFileName + ".")
			msg.setWindowTitle("File Read Error")
			msg.exec_()
		self.setWindowTitle("Timing Diagrammer - " + self.currentFileName)

	def expandDir(self):
		if self.currentDirName == '':
			self.currentDirName = os.path.dirname(os.path.abspath(__file__))
		else:
			self.currentDirName = os.path.expanduser(self.currentDirName)

	def writeCurrentFileBackend(self):
		self.expandDir()
		fullFileName = os.path.join(self.currentDirName, self.currentFileName)
		success = 0
		try:
			with open(fullFileName, 'w', encoding="utf-8", newline='\n') as f:
				f.write(self.plainTextEdit.toPlainText())
				f.close()
				self.editorIsModified = False
				#print ("writeCurrentFileBackend: self.editorIsModified = ", self.editorIsModified)
				self.setWindowTitle("Timing Diagrammer - " + self.currentFileName)
			success = 1
		except:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Error: Could not write to file " + fullFileName + ".")
			msg.setWindowTitle("File Write Error")
			msg.exec_()
			success = 0
		return success

	def writeCurrentFile (self):
		success = 0
		if self.currentFileName[-4:] != '.tim':
			self.currentFileName += '.tim'
		if os.name == 'nt':
			self.currentFileName = self.currentFileName.lower()
		success = self.writeCurrentFileBackend()
		return success

	def fileSave (self, event=None):
		#print ("fileSave: self.currentFileName = ", self.currentFileName, " self.editorIsModified =", self.editorIsModified, " os.path.isfile(self.currentFileName)", os.path.isfile(self.currentFileName))
		success = 0
		fullFileName = os.path.join(self.currentDirName, self.currentFileName)
		#msg = QMessageBox()
		#msg.setIcon(QMessageBox.Critical)
		#msg.setText("fileSave: File " + fullFileName + ".")
		#msg.setWindowTitle("fileSave")
		#msg.exec_()
		if self.editorIsModified == False and os.path.isfile(fullFileName):
			return success #no need of write when existing file is not modified
		if self.currentFileName == 'Untitled.tim':
			#print ("fileSave: calling fileSaveAs (1)")
			success = self.fileSaveAs(None)
		elif os.path.isfile(fullFileName):
			#the file already exists and has been modified - overwrite
			#print ("fileSave: calling writeCurrentFile")
			success = self.writeCurrentFile()
		else:
			#print ("fileSave: calling fileSaveAs (2)")
			success = self.fileSaveAs(None)
		return success

	def fileSaveAs (self, event=None):
		success = 0
		fDialog = QFileDialog()
		if not os.path.exists(self.currentDirName):
			self.currentDirName = os.path.dirname(os.path.abspath(__file__))
		fDialog.setDirectory(self.currentDirName)
		fileName, _ = fDialog.getSaveFileName(self, 'Save File', '', '*.tim')
		#print ("fileSaveAs: fileName = ", fileName)
		if fileName != 'Untitled.tim' and fileName != '':
			self.currentDirName = os.path.dirname(fileName)
			self.currentFileName = os.path.basename(fileName)
			success = self.writeCurrentFile()
			self.discardModalDialogChars = True
		elif fileName == 'Untitled.tim':
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Error: Illegal file name.")
			msg.setWindowTitle("File Write Error")
			msg.exec_()
			success = 0 #write failed
		elif not os.path.exists(self.currentDirName):
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Error: Illegal directory.")
			msg.setWindowTitle("File Write Error")
			msg.exec_()
			success = 0 #write failed

		return success

	def fileExport (self, event=None):
		#size = QtCore.QRectF(self.graphicsScene.sceneRect()).toRect().size()
		size = QtCore.QRectF(self.graphicsScene.itemsBoundingRect()).toRect().size()
		#print ("fileExport: sceneRect width = ", size.width(), "sceneRect height = ", size.height())

		pixmap = QPixmap(size) 
		pixmap.fill(QtGui.QColor("white"))
		painter = QPainter(pixmap)
		#painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
		self.graphicsScene.render(painter)
		painter.end()		
		canExport = False
		if self.currentFileName != 'Untitled.tim':
			if self.currentFileName[-4:] == '.tim' and os.path.exists(self.currentDirName):
				fullFileName = os.path.join(self.currentDirName, self.currentFileName[:self.currentFileName.rfind('.')])
			else:
				fullFileName = "./TimingDiagrammerWave"
			canExport = True
		else:
			qm = QMessageBox()
			qm.setIcon(QMessageBox.Question)
			ret = qm.Yes
			if not os.path.isfile(self.currentFileName):
				ret = qm.question(self,'Buffer Save Dialog', "File must be saved before exporting. Continue?", qm.Yes | qm.No | qm.Cancel)
				if ret == qm.Cancel:
					return
				elif ret == qm.Yes:
					self.fileSaveAs(None)
					canExport = True
		if canExport == True:
			fullFileName = os.path.join(self.currentDirName, self.currentFileName[:self.currentFileName.rfind('.')])
			pixmap.save(fullFileName + ".png")
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setText("Success: Waveform exported to image: " + fullFileName + ".png.")
			msg.setWindowTitle("Waveform Export")
			msg.exec_()

	def fileExit (self, event=None):
		#almost duplicate of closeEvent
		#print ("fileExit: self.editorIsModified = ", self.editorIsModified)
		if self.editorIsModified == True:
			qm = QMessageBox()
			qm.setIcon(QMessageBox.Question)
			ret = qm.question(self,'Unsaved code', "Code has not been saved. Save?", qm.Yes | qm.No | qm.Cancel)
			if ret == qm.Yes:
				success = self.fileSave(None)
				if success:
					msg = QMessageBox()
					msg.setIcon(QMessageBox.Information)
					msg.setText("Saved file " + os.path.join(self.currentDirName, self.currentFileName) + ".")
					msg.setWindowTitle("File Write Completed")
					msg.exec_()
			elif ret == qm.Cancel:
				return
		self.close()

	def helpAbout(self, event=None):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Information)
		msg.setText("Timing Diagrammer Copyright (C) 2021, 2022, 2023 Anirban Banerjee <anirbax@gmail.com>")
		msg.setWindowTitle("About Timing Diagrammer")
		msg.exec_()

	def optionsAliasing(self, event=None):
		if self.actionAliasing.isChecked():
			self.antiAliasedView = True
			self.graphicsView.setRenderHint(QPainter.Antialiasing, True)
			self.graphicsView.setRenderHint(QPainter.SmoothPixmapTransform, True)
			self.graphicsView.setRenderHints(QPainter.Antialiasing, QPainter.HighQualityAntialiasing | QPainter.SmoothPixmapTransform)
		else:
			self.antiAliasedView = False
			self.graphicsView.setRenderHint(QPainter.Antialiasing, False)
			self.graphicsView.setRenderHint(QPainter.HighQualityAntialiasing, False)
			self.graphicsView.setRenderHint(QPainter.SmoothPixmapTransform, False)
		self.reDrawCanvas()

	def optionsSettings(self, event=None):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Information)
		msg.setText("Timing Diagrammer is under construction.")
		msg.setWindowTitle("Timing Diagrammer Notice")
		msg.exec_()

	def textWidthHeight(self, qtext):
		boundingRectSize = qtext.boundingRect().toRect().size()
		#print ("textWidthHeight: called from putText: qtext boundingRectSize = ", boundingRectSize)
		width = boundingRectSize.width()
		height = boundingRectSize.height()
		return width, height

	def putText(self, text, x, y, adjust=True, font="Sans", 
			fsize=10, color="black", wrapWidth=-1, fill=True, updateViewPort = False):
		qtext = self.graphicsScene.addText(text, QtGui.QFont(font, fsize, QtGui.QFont.Normal))
		qtext.setDefaultTextColor(QtGui.QColor(color))
		if wrapWidth < 10*self.waveHalfPeriod and wrapWidth != -1:
			qtext.setTextWidth(wrapWidth)
		elif wrapWidth != -1:
			qtext.setTextWidth(self.waveHalfPeriod)
		qtext.setZValue(3)
		width, height = self.textWidthHeight(qtext)
		height *= 0.55

		if adjust == True:
			xCurrent = x - width/2
			yCurrent = y - height*0.5
			if fill == True:
				r = self.graphicsScene.addRect(QtCore.QRectF(xCurrent, yCurrent, width, height*1.2), 
					QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("white")))
				r.setZValue(2)
			qtext.setPos(x - width/2, y - height*0.9)
			#print ("------------------- putText: xCurrent = ", xCurrent, " -- yCurrent = ", yCurrent)
		else:
			xCurrent = x
			yCurrent = y - height*0.5
			if fill == True:
				r = self.graphicsScene.addRect(QtCore.QRectF(xCurrent, yCurrent, width, height*1.2), 
					QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("white")))
				r.setZValue(2)
			qtext.setPos(x, y - height*0.9)
			#print ("------------------- putText: xCurrent = ", xCurrent, " -- yCurrent = ", yCurrent)

		#anchor
		self.graphicsScene.addLine(QtCore.QLineF(xCurrent + width + self.xMargin, 0,  xCurrent + width + self.xMargin, 1), QtGui.QPen(Qt.transparent)) 
		if updateViewPort == True:
			self.graphicsView.centerOn(
				xCurrent, 
				yCurrent)

	def tdDrawSigNamesText(self, text, updateViewPort = False):
		qtext = self.graphicsScene.addText(text)
		boundingRectSize = qtext.boundingRect().toRect().size()
		#print ("tdDrawSigNamesText: called from processCommand: qtext boundingRectSize = ", boundingRectSize)
		width = boundingRectSize.width()
		height = boundingRectSize.height()

		x = self.signalNameXSpacing + self.sigNameColWidth
		y = self.signalWaveYOffset + (self.currentLineNumber - self.linesWithArrow) *\
			(self.waveHeight + self.signalWaveYSpacing) + self.linesWithArrow * self.arrowLineAdjust

		xCurrent = x - width
		yCurrent = y - self.waveHeight/2 - height/2
		qtext.setPos(xCurrent, yCurrent)

		width = max(width, self.signalNameXSpacing + self.sigNameColWidth) - self.signalNameXSpacing - self.sigNameColWidth

		#this anchor is to ensure jpeg export with adequate margins
		self.graphicsScene.addLine(QtCore.QLineF(-(width + self.xMargin), 0, -(width + self.xMargin), 1), QtGui.QPen(Qt.transparent)) 
		if updateViewPort == True:
			self.graphicsView.centerOn(
				xCurrent, 
				yCurrent)

	def tdDrawHorizArrow(self, waveCount=-1, thisC=None, nextC=None, basis=(0, 0)):
		xBasis, yBasis = basis
		if thisC == '<':
			if True: #waveCount > 0:
				if self.maxWaveCount == 0:
					#draw the grid
					#FIXME
					self.drawGrid (xBasis + self.waveTransitionTime/2, yBasis, waveCount)
					#if (self.evenGridsEnabled == True and (waveCount % 2) == 0):
					#	self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 + self.waveHalfDuration, 
					#		yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
					#		xBasis + self.waveTransitionTime/2 + self.waveHalfDuration, 
					#		yBasis + self.arrowVertOffset), self.gridOtherPen)

					#elif (self.oddGridsEnabled == True and (waveCount % 2) == 1):
					#	self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 + self.waveHalfDuration, 
					#		yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
					#		xBasis + self.waveTransitionTime/2 + self.waveHalfDuration, 
					#		yBasis + self.arrowVertOffset), self.gridPen)

			a = xBasis + self.timeDelta
			c = xBasis + self.waveHalfDuration + self.waveTransitionTime/2 + self.timeDelta
			if waveCount != 0:
				a -= self.waveTransitionTime/2
			self.tdDrawArrowHead((a, yBasis + self.arrowVertOffset), 'L')
			l = self.graphicsScene.addLine(QtCore.QLineF(a, yBasis + self.arrowVertOffset, 
									c, yBasis + self.arrowVertOffset))
			#print ("2. self.currentLineNumber = ", self.currentLineNumber)
			#print ("2. self.linesWithArrow = ", self.linesWithArrow)
			#print ("2. yBasis = ", yBasis)
			#print ("2. offs = ", yBasis + self.arrowVertOffset)
			self.currentLineArrowLineList.append(l)
			l.setZValue(1)

			#print ("saw < -- X = ", a, " -- waveCount = ", waveCount, " -- xBasis = ", xBasis, " -- self.timeDelta", self.timeDelta)
			l = self.graphicsScene.addLine(QtCore.QLineF(a,
				yBasis + self.arrowVertOffset - self.arrowLineEnds,
				a, yBasis + self.arrowVertOffset + self.arrowLineEnds))
			self.currentLineArrowLineList.append(l)
			l.setZValue(1)
			self.pendingArrowDelay = self.timeDelta
			self.timeDelta = 0
		elif thisC == '-':
			if waveCount > 0:
				if self.maxWaveCount == 0:
					#draw the grid
					if (self.evenGridsEnabled == True and (waveCount % 2) == 0):
						self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 + self.waveHalfDuration, 
							yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
							xBasis + self.waveTransitionTime/2 + self.waveHalfDuration, 
							yBasis + self.arrowVertOffset + self.waveHeightChange/2), self.gridOtherPen)
					elif (self.oddGridsEnabled == True and (waveCount % 2) == 1):
						self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 + self.waveHalfDuration, 
							yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
							xBasis + self.waveTransitionTime/2 + self.waveHalfDuration, 
							yBasis + self.arrowVertOffset + self.waveHeightChange/2), self.gridPen)

			#print ("saw - -- pendingArrowDelay = ", self.pendingArrowDelay, "timeDelta = ", self.timeDelta)
			a = xBasis - self.waveTransitionTime/2 + self.pendingArrowDelay
			c = xBasis + self.waveHalfDuration + self.waveTransitionTime/2 + self.pendingArrowDelay + self.timeDelta
			if waveCount == 0:
				a = xBasis + self.timeDelta
			l = self.graphicsScene.addLine(QtCore.QLineF(a, yBasis + self.arrowVertOffset, c, yBasis + self.arrowVertOffset))
			self.currentLineArrowLineList.append(l)
			l.setZValue(1)
			self.pendingArrowDelay += self.timeDelta
			self.timeDelta = 0

		elif thisC == '>':
			a = xBasis - self.waveTransitionTime/2 + self.pendingArrowDelay
			#print ("saw > -- X = ", a, " -- xBasis = ", xBasis, " -- self.timeDelta", self.timeDelta)
			
			self.tdDrawArrowHead((a, yBasis + self.arrowVertOffset), 'R')

			l = self.graphicsScene.addLine(QtCore.QLineF(a, yBasis + self.arrowVertOffset - self.arrowLineEnds,
				a, yBasis + self.arrowVertOffset + self.arrowLineEnds))
			self.currentLineArrowLineList.append(l)
			l.setZValue(1)

			self.timeDelta = 0
			self.pendingArrowDelay = 0

		self.currentLineHasArrow = True

	def tdPrintOverlayAnnot (self, x0, y0, annot, font="Serif", fsize=15):
		qtext = self.graphicsScene.addText(annot, QtGui.QFont(font, fsize, QtGui.QFont.Normal))
		qtext.setPos(int(x0) - fsize, int(y0) - fsize)
		qtext.setDefaultTextColor(QtGui.QColor(self.dirArrowPenColor))
		qtext.setZValue(3)
		self.currentLineOverlayAnnotationQTextList.append(qtext)
		#print ("tdPrintOverlayAnnot: added currentLineOverlayAnnotationQTextList entry = ", qtext)
		self.directionArrowTailState = 0


	def tdDrawDirectionArrow (self, x0, y0, x1, y1, xm, ym):
		color = self.dirArrowPenColor
		xBias = 10 
		yBias = 10

		xl = (x0 + xm + xBias)/2
		yl = (y0 + ym + yBias)/2

		path = QPainterPath()
		path.moveTo(QtCore.QPointF(x0, y0))
		path.cubicTo(QtCore.QPointF(xl, yl),
					QtCore.QPointF(xm, ym),
					QtCore.QPointF(x1, y1))
		self.graphicsScene.addPath(path, self.dirArrowPen)

		height = ym - y1
		base = x1 - xm
		self.tdDrawArrowHeadAngle((x1, y1), (height, base), self.clockArrowSize, color)

	def tdDrawClock(self, waveCount=-1, lastC=None, thisC=None, nextC=None, basis=(0, 0), thisIsLastChar=False):
		xBasis, yBasis = basis
		x0 = xBasis
		localWaveCount = waveCount
		#print ("tdDrawClock: thisC = ", thisC, " localWaveCount = ", localWaveCount)
		if (localWaveCount % 2) == 1 and self.clockEvenOddFlip == 0:
			self.clockEvenOddFlip = 1
			#swap the pen colors (red/blue)
			self.gridPen, self.gridOtherPen = self.gridOtherPen, self.gridPen
			
		if thisC == 'P': #upper case
			if lastC == 'l':
				x0 += self.waveTransitionTime/2
			
			#print ("self.riseClockArrow = ", self.riseClockArrow, " self.fallClockArrow = ", self.fallClockArrow)
			x1 = x0 + self.waveHalfDuration + self.timeDelta

			if lastC == 'l':
				x1 -= self.waveTransitionTime/2

			if waveCount == 0 or lastC == 'z':
				x0 += self.waveTransitionTime/2 #tweak to match the start time of non-clock signals or previous tristate signal
			y0 = yBasis
			y1 = yBasis

			self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1))

			#print ("Doing P -- EVEN seeing maxWaveCount =", self.maxWaveCount, " localWaveCount", localWaveCount)
			if self.maxWaveCount == 0:
				#draw the grid
				if self.evenGridsEnabled == True and (localWaveCount % 2) == self.clockEvenOddFlip:
					self.graphicsScene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime/2 - self.timeDelta, 
						yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2,
						x1 + self.waveTransitionTime/2 - self.timeDelta, 
						yBasis), self.gridOtherPen)

			localWaveCount += 1

			x0 = x1 
			x1 += self.waveTransitionTime
			y0 = yBasis
			y1 = yBasis - self.waveHeight
			self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1))
			if self.riseClockArrow == True:
				self.tdDrawArrowHeadAngle((x1, y1), (self.waveHeight, self.waveTransitionTime), self.clockArrowSize)

			x0 = x1
			x1 += self.waveHalfDuration - self.timeDelta
			y0 = yBasis - self.waveHeight
			y1 = yBasis - self.waveHeight
			self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1))

			#draw the falling edge grid
			print ("Doing P -- ODD seeing maxWaveCount =", self.maxWaveCount, " localWaveCount", localWaveCount)
			if self.oddGridsEnabled == True and (localWaveCount % 2) != self.clockEvenOddFlip:
				self.graphicsScene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime/2, 
					yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
					x1 + self.waveTransitionTime/2, 
					yBasis), self.gridPen)

			#print ("thisC is UPPER P and nextC is ", nextC, " cmdNum = ", cmdNum)
			if nextC in "pP":
				#print ("CASE UPPER P of P is seen")
				x0 = x1 
				x1 += self.waveTransitionTime
				y0 = yBasis - self.waveHeight
				y1 = yBasis
				self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1))
			elif nextC == 'z':
				x0 = x1
				x1 += self.waveTransitionTime
				y0 = yBasis - self.waveHeight
				y1 = yBasis - self.waveHeight/2
				self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1))
				self.graphicsScene.addLine(QtCore.QLineF(x1, y1, x1 + self.waveTransitionTime/2, y1))
			elif nextC in 'hfF':
				x0 = x1
				x1 += self.waveTransitionTime
				self.graphicsScene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, 
					x1, yBasis - self.waveHeight))
				self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight, 
					x1 + self.waveTransitionTime/2, yBasis - self.waveHeight))
			elif nextC in 'lrR':
				x0 = x1
				x1 += self.waveTransitionTime
				self.graphicsScene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, 
					x1, yBasis))
				self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis, 
					x1 + self.waveTransitionTime/2, yBasis))
			elif nextC in 'DdXx':
				x0 = x1
				x1 += self.waveTransitionTime/2
				#print ("nextC in DdXx")
				#print ("self.currentColor == ", self.currentColor)
				if nextC in 'Dd' and self.currentColor != 'x':
					if self.currentColor in colorMap.keys():
						color = colorMap[self.currentColor]
					else:
						color = "light grey"
				else:
					color = "light grey"

				if nextC in 'Xx' or (nextC in 'Dd' and self.currentColor != 'x'):
					#print ("== seeing nextC in 'Xx' or (nextC in 'Dd' and self.currentColor != 'x')")
					c = x0 + self.waveTransitionTime
					#self.canvas.create_polygon(x1, yBasis - self.waveHeight, 
					#	c + self.waveTransitionTime/2, yBasis - self.waveHeight, c + self.waveTransitionTime/2, yBasis)
					pointList = [QtCore.QPointF(x1, yBasis - self.waveHeight),
							QtCore.QPointF(c + self.waveTransitionTime/2, yBasis - self.waveHeight),
							QtCore.QPointF(c + self.waveTransitionTime/2, yBasis)]
						
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))

				self.graphicsScene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, x1, yBasis - self.waveHeight))
				x0 = x1
				x1 += self.waveTransitionTime
				self.graphicsScene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, 
					x1, yBasis - self.waveHeight))
				self.graphicsScene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, 
					x1, yBasis))

			if self.fallClockArrow == True:
				self.tdDrawArrowHeadAngle((x0+self.waveTransitionTime, y1), (-self.waveHeight, self.waveTransitionTime), self.clockArrowSize)
				
		elif thisC == 'p': #lower case
			#print ("Doing small p -- at the beginning seeing riseClockArrow =", self.riseClockArrow)
			if lastC == 'l':
				x0 += self.waveTransitionTime/2
			
			x1 = x0 + self.waveHalfDuration + self.waveTransitionTime/2 + self.timeDelta
			
			if lastC == 'l':
				x1 -= self.waveTransitionTime/2

			if waveCount == 0 or lastC == 'z':
				x0 += self.waveTransitionTime/2 #tweak to match the start time of non-clock signals or previous tristate signal
			y0 = yBasis
			y1 = yBasis
			self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1))

			#print ("Doing small p -- EVEN seeing maxWaveCount =", self.maxWaveCount, " localWaveCount", localWaveCount)
			if self.maxWaveCount == 0:
				#draw the grid
				if self.evenGridsEnabled == True and (localWaveCount % 2) == self.clockEvenOddFlip:
					self.graphicsScene.addLine(QtCore.QLineF(x1 - self.timeDelta, 
						yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
						x1 - self.timeDelta, 
						yBasis), self.gridOtherPen)

			localWaveCount += 1

			x0 = x1 
			y0 = yBasis
			y1 = yBasis - self.waveHeight
			self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1))
			if self.riseClockArrow == True:
				self.tdDrawArrowHeadAngle((x1, y1), (1, 0), self.clockArrowSize)

			x1 += self.waveHalfPeriod - self.timeDelta
			y0 = yBasis - self.waveHeight
			y1 = yBasis - self.waveHeight
			self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1))
			
			#draw the falling edge grid
			#print ("Doing small p -- ODD seeing maxWaveCount =", self.maxWaveCount, " localWaveCount", localWaveCount)
			if self.oddGridsEnabled == True and (localWaveCount % 2) != self.clockEvenOddFlip:
				self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
					x1,	yBasis), self.gridPen)

			if nextC in "pP":
				#print ("CASE P of P is seen")
				x0 = x1
				y0 = yBasis - self.waveHeight
				y1 = yBasis
				self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1)) 

				x1 += self.waveTransitionTime/2 
				y0 = yBasis
				y1 = yBasis
				self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1))
			elif nextC == 'z':
				x0 = x1
				x1 += self.waveTransitionTime
				y0 = yBasis - self.waveHeight
				y1 = yBasis - self.waveHeight/2
				self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1)) 
			elif nextC in 'hfF':
				x0 = x1
				x1 += self.waveTransitionTime
				self.graphicsScene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, 
					x1, yBasis - self.waveHeight))
			elif nextC in 'lrR':
				x0 = x1
				x1 += self.waveTransitionTime
				self.graphicsScene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, 
					x1, yBasis))
			elif nextC in 'DdXx':
				x0 = x1
				x1 += self.waveTransitionTime
				if nextC in 'Dd' and self.currentColor != 'x':
					if self.currentColor in colorMap.keys():
						color = colorMap[self.currentColor]
					else:
						color = "light grey"
				else:
					color = "light grey"

				if nextC in 'Xx' or (nextC in 'Dd' and self.currentColor != 'x'):
					c = x0# + self.waveTransitionTime
					pointList = [QtCore.QPointF(x0, yBasis - self.waveHeight),
							QtCore.QPointF(x0 + self.waveTransitionTime, yBasis - self.waveHeight),
							QtCore.QPointF(x0 + self.waveTransitionTime, yBasis)]
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
					#self.canvas.create_polygon(x0, yBasis - self.waveHeight, 
					#	c + self.waveTransitionTime, yBasis - self.waveHeight, c + self.waveTransitionTime, yBasis)

				self.graphicsScene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, 
					x1, yBasis - self.waveHeight))
				self.graphicsScene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, 
					x1, yBasis))
					
			if self.fallClockArrow == True:
				self.tdDrawArrowHeadAngle((x0, y1), (-1, 0), self.clockArrowSize)

			#add total of waveTransitionTime/2 for pckq pulses
			if thisIsLastChar == True:
				x0 += self.waveTransitionTime/2
				self.graphicsScene.addLine(QtCore.QLineF(x0, y1, x0 + self.waveTransitionTime/2, y1))

		#add waveTransitionTime/4 for PCKQ pulses
		if thisIsLastChar == True and thisC == "P":
			x0 = xBasis + 2 * self.waveHalfDuration + 2 * self.waveTransitionTime
			self.graphicsScene.addLine(QtCore.QLineF(x0, yBasis, 
				x0 + self.waveTransitionTime/2, yBasis))

		waveCount += 2
		self.timeDelta = 0

	def tdDrawFall(self, waveCount=-1, thisC=None, nextC=None, basis=(0, 0)):
		xBasis, yBasis = basis
		x0 = xBasis + self.waveTransitionTime/2
		x1 = x0 + self.waveHalfDuration - self.timeDelta
		y0 = yBasis - self.waveHeight
		y1 = yBasis - self.waveHeight
		self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1))
		color = "light grey"

		if nextC in "dxDXpP":
			if nextC in 'Dd' and self.currentColor != 'x':
				if self.currentColor in colorMap.keys():
					color = colorMap[self.currentColor]

			if nextC in 'xX' or (nextC in 'dD' and self.currentColor != 'x'):
				c = x1 + self.waveTransitionTime + self.timeDelta
				pointList = [QtCore.QPointF(x1, yBasis - self.waveHeight), 
							QtCore.QPointF(c, yBasis - self.waveHeight), 
							QtCore.QPointF(c, yBasis), 
							QtCore.QPointF(c - self.timeDelta, yBasis)]
				self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))

			if nextC in "pP":
				self.graphicsScene.addLine(QtCore.QLineF(x1, y1, x1 + self.waveTransitionTime/2, yBasis))
				self.graphicsScene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime/2, yBasis, x1 + self.timeDelta + self.waveTransitionTime, yBasis))
			else:
				self.graphicsScene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis))

			if nextC in 'dxDX':
				self.graphicsScene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime + self.timeDelta, y0))
		elif nextC in 'hf':
			self.graphicsScene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2))
			self.graphicsScene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
			self.graphicsScene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime, yBasis - self.waveHeight, x1 + self.waveTransitionTime + self.timeDelta, yBasis - self.waveHeight))
		elif nextC == 'z':
			self.graphicsScene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis - self.waveHeight/2))
			self.graphicsScene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime, yBasis - self.waveHeight/2, 
				x1 + self.waveTransitionTime + self.timeDelta, yBasis - self.waveHeight/2))

		self.drawGrid (xBasis + self.waveTransitionTime/2, yBasis, waveCount)
		#FIXME
		#if self.maxWaveCount == 0:
		#	#draw the grid
		#	if (self.evenGridsEnabled == True and (waveCount % 2) == 0):
		#		self.graphicsScene.addLine(QtCore.QLineF(x1 + self.timeDelta, yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
		#			x1 + self.timeDelta, yBasis), self.gridOtherPen)
		#	elif (self.oddGridsEnabled == True and (waveCount % 2) == 1):
		#		self.graphicsScene.addLine(QtCore.QLineF(x1 + self.timeDelta, yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
		#			x1 + self.timeDelta, yBasis), self.gridPen)

		x0 = x1
		x1 += self.waveTransitionTime
		y0 = yBasis - self.waveHeight
		y1 = y0 + self.waveHeight
		#if nextC != 'h' and nextC != 'z' and nextC != 'f':
		if nextC not in 'hzfFpP':
			if thisC == 'F':
				pointList = [QtCore.QPointF(x0, y0),
							QtCore.QPointF(x0 + self.waveTransitionTime, y0),
							QtCore.QPointF(x1 + self.waveTransitionTime, y1),
							QtCore.QPointF(x0 + self.waveTransitionTime, y1)]
				self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x0 + self.waveTransitionTime, y0))
				self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveTransitionTime, y0, x1 + self.waveTransitionTime, y1))
				if nextC not in 'Fl': #anirb - 27-Dec-2022
					self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveTransitionTime, y1, x1 + self.waveTransitionTime, y1))

			self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1))
			self.graphicsScene.addLine(QtCore.QLineF(x1, y1, x1 + self.timeDelta, y1))
		elif nextC == 'F':
			self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1 + self.timeDelta, y0))
		self.pendingTimeDelta = self.timeDelta

	def tdDrawRise (self, waveCount=-1, thisC=None, nextC=None, basis=(0, 0)):
		#print ("Doing r -- at the beginning seeing timeDelta =", self.timeDelta)
		#print ("Doing 'r' -- at the beginning -- invertedClockHeight = ", invertedClockHeight)
		xBasis, yBasis = basis
		x0 = xBasis + self.waveTransitionTime/2
		x1 = x0 + self.waveHalfDuration - self.timeDelta
		y0 = yBasis
		y1 = yBasis
		self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1))
		color = "light grey"

		if nextC in "dxDX":
			if nextC in 'xX' or (nextC in 'Dd' and self.currentColor != 'x'):
				if nextC in 'Dd' and self.currentColor != 'x':
					if self.currentColor in colorMap.keys():
						color = colorMap[self.currentColor]
					else:
						color = "light grey"

				c = x1 + self.waveTransitionTime + self.timeDelta
				pointList = [QtCore.QPointF(x1, yBasis), 
							QtCore.QPointF(c, yBasis), 
							QtCore.QPointF(c, yBasis - self.waveHeight), 
							QtCore.QPointF(c - self.timeDelta, yBasis - self.waveHeight)]
				self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
			self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime + self.timeDelta, yBasis))
		elif nextC in 'lr':
			self.graphicsScene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2))
			self.graphicsScene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2, x1 + self.waveTransitionTime, yBasis))
			self.graphicsScene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime, yBasis, x1 + self.waveTransitionTime + self.timeDelta, yBasis))
		elif nextC in 'pP':
			self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime/2 + self.timeDelta, yBasis))
		elif nextC == 'z':
			self.graphicsScene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis - self.waveHeight/2))
			self.graphicsScene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime, yBasis - self.waveHeight/2, 
				x1 + self.waveTransitionTime + self.timeDelta, yBasis - self.waveHeight/2))

		self.drawGrid (xBasis + self.waveTransitionTime/2, yBasis, waveCount)
		#FIXME
		#if self.maxWaveCount == 0:
		#	#draw the grid
		#	if (self.evenGridsEnabled == True and (waveCount % 2) == 0):
		#		self.graphicsScene.addLine(QtCore.QLineF(x1 + self.timeDelta, yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
		#			x1 + self.timeDelta, yBasis), self.gridOtherPen)
		#	elif (self.oddGridsEnabled == True and (waveCount % 2) == 1):
		#		self.graphicsScene.addLine(QtCore.QLineF(x1 + self.timeDelta, yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
		#			x1 + self.timeDelta, yBasis), self.gridPen)

		x0 = x1 
		x1 += self.waveTransitionTime
		y0 = yBasis
		y1 = yBasis - self.waveHeight
		if nextC not in 'lzrRpP':
			if thisC == 'R':
				pointList = [QtCore.QPointF(x0, y0),
							QtCore.QPointF(x0 + self.waveTransitionTime, y1),
							QtCore.QPointF(x1 + self.waveTransitionTime, y1),
							QtCore.QPointF(x0 + self.waveTransitionTime, y0)]
				self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x0 + self.waveTransitionTime, y0))
				self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveTransitionTime, y0, x1 + self.waveTransitionTime, y1))
				if nextC not in 'Rh': #anirb - 27-Dec-2022
					self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveTransitionTime, y1, x1 + self.waveTransitionTime, y1))
			self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1))
			if self.timeDelta > 0:
				self.graphicsScene.addLine(QtCore.QLineF(x1, y1, x1 + self.timeDelta, y1))
		elif nextC == 'R':
			self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1 + self.timeDelta, y0))
		self.pendingTimeDelta = self.timeDelta

	def tdDrawHigh (self, waveCount=-1, nextC=None, basis=(0, 0)):
		xBasis, yBasis = basis
		x0 = xBasis + self.waveTransitionTime/2
		if nextC in "zldxDXrRpP":
			x1 = x0 + self.waveHalfDuration
		else:
			x1 = x0 + self.waveHalfPeriod

		y0 = yBasis - self.waveHeight
		y1 = y0
		self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1))
		if nextC in "ldxDXrR":
			#print ("== seeing h and nextC in ldxDXrRpP")
			if nextC in 'Dd' and self.currentColor != 'x':
				if self.currentColor in colorMap.keys():
					color = colorMap[self.currentColor]
				else:
					color = "light grey"
			else:
				color = "light grey"

			if nextC in 'xX' or nextC == 'X' or (nextC in 'Dd' and self.currentColor != 'x'):
				c = x1 + self.waveTransitionTime
				pointList = [QtCore.QPointF(x1, yBasis - self.waveHeight), 
							QtCore.QPointF(c, yBasis - self.waveHeight), 
							QtCore.QPointF(c, yBasis)]
				self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
			if nextC in 'dxDX':
				self.graphicsScene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, y0))
			self.graphicsScene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis))
		elif nextC == 'z':
			self.graphicsScene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis - self.waveHeight/2))
		elif nextC in 'pP':
			self.graphicsScene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime/2, yBasis))

		self.drawGrid (xBasis + self.waveTransitionTime/2, yBasis, waveCount)
		#if self.maxWaveCount == 0:
		#	#draw the grid
		#	if (self.evenGridsEnabled == True and (waveCount % 2) == 0):
		#		self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration, yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
		#			x0 + self.waveHalfDuration, yBasis), self.gridOtherPen)
		#	elif (self.oddGridsEnabled == True and (waveCount % 2) == 1):
		#		self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration, yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
		#			x0 + self.waveHalfDuration, yBasis), self.gridPen)

	def tdDrawLow (self, waveCount=-1, nextC=None, lastC=None, basis=(0, 0)):
		xBasis, yBasis = basis
		if lastC.lower() in "cpkq" and waveCount != 0:
			x0 = xBasis
		else:
			x0 = xBasis + self.waveTransitionTime/2

		if nextC in "zhdxDXfF":
			x1 = x0 + self.waveHalfDuration
		else:
			x1 = x0 + self.waveHalfPeriod

		if lastC.lower() in "cpkq" and waveCount != 0:
			x1 += self.waveTransitionTime/2

		y0 = yBasis
		y1 = y0
		self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1, y1))

		if nextC in "hdxDXfF":
			#if nextC in "h" and waveCount != 0:
			#	x1 -= self.waveTransitionTime/2

			if nextC in 'Dd' and self.currentColor != 'x':
				if self.currentColor in colorMap.keys():
					color = colorMap[self.currentColor]
				else:
					color = "light grey"
			else:
				color = "light grey"

			if nextC in 'xX' or (nextC in 'Dd' and self.currentColor != 'x'):
				#print ("== seeing l and nextC in xdDX")
				c = x1 + self.waveTransitionTime
				pointList = [QtCore.QPointF(x1, yBasis), 
							QtCore.QPointF(c, yBasis), 
							QtCore.QPointF(c, yBasis - self.waveHeight)]
				self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))

			if nextC in 'dxDX':
				self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis))
			self.graphicsScene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
		elif nextC == 'z':
			self.graphicsScene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis - self.waveHeight/2))

		self.drawGrid (xBasis + self.waveTransitionTime/2, yBasis, waveCount)

	def tdDrawDatadx(self, waveCount=-1, lastC=None, thisC=None, nextC=None, basis=(0, 0)):
		#print ("tdDrawDatadx: thisC=", thisC, " nextC=", nextC, " lastC=", lastC)
		#print ("tdDrawDatadx: self.currentColor=", self.currentColor, " self.pendingTimeDelta=", self.pendingTimeDelta, " lastC=", lastC)
		#print ("tdDrawDatadx: self.waveHeightChange = ", self.waveHeightChange)
		xBasis, yBasis = basis
		color = "light grey"
		if self.currentColor in colorMap.keys():
			color = colorMap[self.currentColor]

		#only clocks with zero rise/fall times
		lastWasClock = (lastC == "c" or lastC == "p") and waveCount != 0
		
		if lastWasClock:
			x0 = xBasis - self.waveTransitionTime/2
		else:
			x0 = xBasis + self.waveTransitionTime/2

		self.drawGrid (xBasis + self.waveTransitionTime/2, yBasis, waveCount)
		#FIXME
		#if self.maxWaveCount == 0:
		#	#draw the grid
		#	if (self.evenGridsEnabled == True and (waveCount % 2) == 0):
		#		self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration, yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
		#			x0 + self.waveHalfDuration, yBasis), self.gridOtherPen)
		#	elif (self.oddGridsEnabled == True and (waveCount % 2) == 1):
		#		self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration, yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
		#			x0 + self.waveHalfDuration, yBasis), self.gridPen)

		if nextC in "zlhrRfFPp" or\
				(thisC == 'd' and (nextC in 'xX')) or\
				(thisC == 'x' and (nextC in 'dDX')):
			x1 = x0 + self.waveHalfDuration
		else:
			x1 = x0 + self.waveHalfPeriod

		if lastWasClock:
			x1 += self.waveTransitionTime

		if thisC == 'x' or (thisC == 'd' and self.currentColor != 'x'):
			#print ("if A --------")
			y0 = yBasis
			y1 = yBasis
			a = x0
			b = y0
			c = x1
			d = y0
			y0 = yBasis - self.waveHeight
			y1 = y0
			e = c
			f = y0
			g = a
			if lastC == 'R':
				g += self.waveTransitionTime
			if lastC == 'F':
				a += self.waveTransitionTime
			h = f

			pointList = [QtCore.QPointF(a - self.pendingTimeDelta, b),
						QtCore.QPointF(c, d),
						QtCore.QPointF(e, f),
						QtCore.QPointF(g - self.pendingTimeDelta, h)]
			if (thisC == 'd' and self.currentColor != 'x'):
				self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				if lastC in 'DXzxhlrRfF':
					if lastC == 'z':
						pointList = [QtCore.QPointF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis),
								QtCore.QPointF(xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight/2),
								QtCore.QPointF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight)]
					elif lastC in 'lr':
						pointList = [QtCore.QPointF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight),
								QtCore.QPointF(xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis),
								QtCore.QPointF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis)]
					elif lastC in 'hf':
						pointList = [QtCore.QPointF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight),
								QtCore.QPointF(xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight),
								QtCore.QPointF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis)]
					else:
						pointList = [QtCore.QPointF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis),
							QtCore.QPointF(xBasis - self.pendingTimeDelta, yBasis - self.waveHeight/2),
							QtCore.QPointF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight)]
					if lastC != 'R' and lastC != 'F':
						self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))

					if lastC in 'lrR':
						self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight, 
							xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis))
						self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis,
							xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis))
						if lastC == 'R':
							l = self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 + self.waveTransitionTime - self.pendingTimeDelta, yBasis - self.waveHeight, 
								xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis))
					elif lastC in 'hfF':
						self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2, yBasis - self.waveHeight, 
							xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight))
						self.graphicsScene.addLine(QtCore.QLineF(xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight,
							xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis))
						if lastC == 'F':
							self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 + self.waveTransitionTime - self.pendingTimeDelta, yBasis, 
								xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight))
			else:
				self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))

			if nextC == 'z':
				c = x1 + self.waveTransitionTime
				d = yBasis - self.waveHeight/2
				pointList = [QtCore.QPointF(x1, yBasis),
							QtCore.QPointF(c, d),
							QtCore.QPointF(x1, yBasis - self.waveHeight)]
				if (thisC == 'd' and self.currentColor != 'x'):
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				else:
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
			elif nextC in 'lrR' or nextC == 'p' or nextC == 'P':
				c = x1 + self.waveTransitionTime
				pointList = [QtCore.QPointF(x1, yBasis),
							QtCore.QPointF(c, yBasis),
							QtCore.QPointF(x1, yBasis - self.waveHeight)]
				if (thisC == 'd' and self.currentColor != 'x'):
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				else:
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
			elif nextC in 'hfF':
				c = x1 + self.waveTransitionTime
				pointList = [QtCore.QPointF(x1, yBasis),
							QtCore.QPointF(x1, yBasis - self.waveHeight),
							QtCore.QPointF(c, yBasis - self.waveHeight)]
				if (thisC == 'd' and self.currentColor != 'x'):
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				else:
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
			elif nextC in 'dXD' or (thisC == 'd' and nextC == 'x'): 
				a = x1 + self.waveTransitionTime/2
				c = x1 + self.waveTransitionTime
				if (thisC == 'd' and self.currentColor != 'x'):
					pointList = [QtCore.QPointF(x1, yBasis),
								QtCore.QPointF(x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2),
								QtCore.QPointF(x1, yBasis - self.waveHeight)]
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
					if nextC in 'xX':
						pointList = [QtCore.QPointF(x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2),
									QtCore.QPointF(x1 + self.waveTransitionTime, yBasis),
									QtCore.QPointF(x1 + self.waveTransitionTime, yBasis - self.waveHeight)]
						self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
						self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
						self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight, x1 + self.waveTransitionTime, yBasis))
				else:
					#print ("if B --------")
					if nextC in 'dD':
						#print ("if C --------")
						pointList = [QtCore.QPointF(x1, yBasis),
								QtCore.QPointF(x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2),
								QtCore.QPointF(x1, yBasis - self.waveHeight)]
						self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
					else: #'X'
						#print ("if D --------")
						pointList = [QtCore.QPointF(x1, yBasis),
								QtCore.QPointF(x1 + self.waveTransitionTime, yBasis),
								QtCore.QPointF(x1 + self.waveTransitionTime, yBasis - self.waveHeight),
								QtCore.QPointF(x1, yBasis - self.waveHeight)]
						self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
						
				if thisC == 'x':
					if nextC in 'dD' and self.currentColor != 'x':
						pointList = [QtCore.QPointF(x1 + self.waveTransitionTime, yBasis),
								QtCore.QPointF(a, yBasis - self.waveHeight/2),
								QtCore.QPointF(x1 + self.waveTransitionTime, yBasis - self.waveHeight)]
						self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
						self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
						self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight, x1 + self.waveTransitionTime, yBasis))
					elif nextC in 'dD':
						self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
						self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight, x1 + self.waveTransitionTime, yBasis))
					elif nextC in 'X':
						pointList = [QtCore.QPointF(x1 + self.waveTransitionTime, yBasis),
								QtCore.QPointF(a, yBasis - self.waveHeight/2),
								QtCore.QPointF(x1 + self.waveTransitionTime, yBasis - self.waveHeight)]
						self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
						self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
						self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis))
		elif thisC == 'd'and nextC in 'xX':
			#print ("if B --------")
			pointList = [QtCore.QPointF(x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2),
					QtCore.QPointF(x1 + self.waveTransitionTime, yBasis),
					QtCore.QPointF(x1 + self.waveTransitionTime, yBasis - self.waveHeight)]
			self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
			self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
			self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight, x1 + self.waveTransitionTime, yBasis))

		y0 = yBasis
		y1 = y0
		self.graphicsScene.addLine(QtCore.QLineF(x0 - self.pendingTimeDelta, y0, x1, y1))
		y0 = yBasis - self.waveHeight
		y1 = y0
		self.graphicsScene.addLine(QtCore.QLineF(x0 - self.pendingTimeDelta, y0, x1, y1))

		if nextC in 'pP':
			self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis))
			self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight, x1 + self.waveTransitionTime, yBasis))
		elif nextC in 'lrR':
			self.graphicsScene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis))
			self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis))
		elif nextC in 'hfF':
			self.graphicsScene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
			self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
		elif nextC == 'z':
			self.graphicsScene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis - self.waveHeight/2))
			self.graphicsScene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis - self.waveHeight/2))
		
		if (thisC == 'd' and self.currentColor != 'x'):
			if waveCount != 0 and lastC in 'DXzx':
				if lastC == 'z':
					self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis, 
						xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight/2))
					self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight, 
						xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight/2))
				else:
					self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis, 
						xBasis - self.pendingTimeDelta, yBasis - self.waveHeight/2))
					self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight, 
						xBasis - self.pendingTimeDelta, yBasis - self.waveHeight/2))

				self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis, x1 - self.pendingTimeDelta, yBasis))
				self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight, x1 - self.pendingTimeDelta, yBasis - self.waveHeight))
		self.pendingTimeDelta = 0

	def tdDrawDataDX(self, waveCount=-1, lastC=None, thisC=None, nextC=None, basis=(0, 0)):
		#print ("tdDrawDataDX: thisC=", thisC, " ord nextC=", ord(nextC), nextC, " lastC=", lastC)
		#print ("tdDrawDataDX: at start, self.pendingTimeDelta=", self.pendingTimeDelta)
		xBasis, yBasis = basis
		if (lastC == "P" or lastC == "p") and waveCount != 0:
			x0 = xBasis
		else:
			x0 = xBasis + self.waveTransitionTime/2
		x1 = x0 + self.waveHalfDuration
		y0 = yBasis
		y1 = y0

		self.drawGrid (xBasis + self.waveTransitionTime/2, yBasis, waveCount)
		#FIXME
		#if self.maxWaveCount == 0:
		#	#draw the grid
		#	if (self.evenGridsEnabled == True and (waveCount % 2) == 0):
		#		self.graphicsScene.addLine(QtCore.QLineF(x1, y0 - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, x1, y0), self.gridOtherPen)
		#	elif (self.oddGridsEnabled == True and (waveCount % 2) == 1):
		#		self.graphicsScene.addLine(QtCore.QLineF(x1, y0 - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, x1, y0), self.gridPen)

		a = x0
		b = y0
		c = x1
		d = y1
		x0 = x1
		x1 += self.waveTransitionTime
		e = c + self.waveTransitionTime/2
		f = y1 - self.waveHeight/2
		y1 -= self.waveHeight
		g = c
		h = y1 
		i = a
		if lastC == 'R':
			i += self.waveTransitionTime
		elif lastC == 'F':
			a += self.waveTransitionTime
		j = h
		color = "light grey"
		if self.currentColor in colorMap.keys():
			color = colorMap[self.currentColor]

		#print ("tdDrawDataDX: 0. thisC == 'D' and self.currentColor = ", self.currentColor)
		if thisC == 'X' or (thisC == 'D' and self.currentColor != 'x'):
			if (thisC == 'D' and self.currentColor != 'x'):
				#print ("tdDrawDataDX: 1. thisC == 'D' and self.currentColor != 'x'")
				pointList = [QtCore.QPointF(a - self.pendingTimeDelta, b),
							QtCore.QPointF(c - self.timeDelta, d),
							QtCore.QPointF(e - self.timeDelta, y1 + self.waveHeight/2),
							QtCore.QPointF(g - self.timeDelta, h),
							QtCore.QPointF(i - self.pendingTimeDelta, j)]
				self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				if lastC in 'DXzxhlrRfF':
					#FIX PR0
					# to handle cases like: D$rD - when the first D is seen, the color is not yet known, so the
					#left triangle for the next D cannot be filled - it must be deferred when the next D is being
					#processed as thisC
					if lastC == 'z':
						pointList = [QtCore.QPointF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis),
								QtCore.QPointF(xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight/2),
								QtCore.QPointF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight)]
					elif lastC in 'lr':
						pointList = [QtCore.QPointF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight),
								QtCore.QPointF(xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis),
								QtCore.QPointF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis)]
					elif lastC in 'hf':
						pointList = [QtCore.QPointF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight),
								QtCore.QPointF(xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight),
								QtCore.QPointF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis)]
					else:
						pointList = [QtCore.QPointF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis),
								QtCore.QPointF(xBasis - self.pendingTimeDelta, yBasis - self.waveHeight/2),
								QtCore.QPointF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight)]
					if lastC != 'R' and lastC != 'F':
						self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))

					if lastC == 'z':
						#redo the angled lines only if last was D or X or z
						self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis, 
							xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight/2))
						self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight, 
							xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight/2))
					elif lastC in 'DXx':
						#print ("tdDrawDataDX: 1. waveCount != 0 and lastC in 'DX'")
						self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis, 
							xBasis - self.pendingTimeDelta, yBasis - self.waveHeight/2))
						self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight, 
							xBasis - self.pendingTimeDelta, yBasis - self.waveHeight/2))
					elif lastC in 'lrR':
						self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight, 
							xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis))
						self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis,
							xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis))
						if lastC == 'R':
							self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 + self.waveTransitionTime - self.pendingTimeDelta, yBasis - self.waveHeight, 
								xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis))
					elif lastC in 'hfF':
						self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2, yBasis - self.waveHeight, 
							xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight))
						self.graphicsScene.addLine(QtCore.QLineF(xBasis - self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight,
							xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis))
						if lastC == 'F':
							self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 + self.waveTransitionTime - self.pendingTimeDelta, yBasis, 
								xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight))
				#horizontal lines
				if lastC in 'DXzrR':
					self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis - self.waveHeight, 
						xBasis + self.waveTransitionTime/2, yBasis - self.waveHeight))
					self.graphicsScene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2 - self.pendingTimeDelta, yBasis, 
						xBasis + self.waveTransitionTime/2, yBasis))
			else:
				pointList = [QtCore.QPointF(a, b),
							QtCore.QPointF(c - self.timeDelta, d),
							QtCore.QPointF(e - self.timeDelta, y1 + self.waveHeight/2),
							QtCore.QPointF(g - self.timeDelta, h),
							QtCore.QPointF(i, j)]
				self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))

			if nextC == 'z':
				a = x1 - self.waveTransitionTime
				c = x1
				d = yBasis - self.waveHeight/2
				pointList = [QtCore.QPointF(x1 - self.waveTransitionTime - self.timeDelta, yBasis),
						QtCore.QPointF(x1 - self.timeDelta, d),
						QtCore.QPointF(x1 - self.waveTransitionTime - self.timeDelta, yBasis - self.waveHeight)]
				if (thisC == 'D' and self.currentColor != 'x'):
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				else:
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
			elif nextC in 'dxXD':
				#print ("tdDrawDataDX: A. nextC in 'dxXD'")
				a = x1
				e = x1 - self.waveTransitionTime/2
				f = yBasis - self.waveHeight/2
				if nextC in 'xX':
					pointList = [QtCore.QPointF(a, yBasis),
							QtCore.QPointF(a, yBasis - self.waveHeight),
							QtCore.QPointF(a - self.timeDelta, yBasis - self.waveHeight),
							QtCore.QPointF(e - self.timeDelta, yBasis - self.waveHeight/2),
							QtCore.QPointF(a - self.timeDelta, yBasis)]
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
				elif self.currentColor != 'x':
					pointList = [QtCore.QPointF(a, yBasis),
							QtCore.QPointF(a, yBasis - self.waveHeight),
							QtCore.QPointF(a - self.timeDelta, yBasis - self.waveHeight),
							QtCore.QPointF(e - self.timeDelta, yBasis - self.waveHeight/2),
							QtCore.QPointF(a - self.timeDelta, yBasis)]
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
			elif nextC in 'hfF':
				#print ("thisC == 'X' or (thisC == 'D' and self.currentColor != 'x') === and === nextC in 'hfF'")
				a = x1 - self.waveTransitionTime
				d = yBasis - self.waveHeight
				pointList = [QtCore.QPointF(a - self.timeDelta, yBasis),
						QtCore.QPointF(a - self.timeDelta, d),
						QtCore.QPointF(x1 - self.timeDelta, d)]
				if thisC == 'D' and self.currentColor != 'x':
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				else:
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
			elif nextC in 'lrRpP':
				a = x1 - self.waveTransitionTime
				d = yBasis
				pointList = [QtCore.QPointF(a - self.timeDelta, yBasis - self.waveHeight),
						QtCore.QPointF(a - self.timeDelta, d),
						QtCore.QPointF(x1 - self.timeDelta, d)]
				if thisC == 'D' and self.currentColor != 'x':
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				else:
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
		elif thisC == 'D':
			if nextC in 'xXdD':
				#print ("tdDrawDataDX: B. nextC in 'dxXD', self.currentColor = ", self.currentColor)
				a = x1 - self.waveTransitionTime/2
				c = x1
				f = yBasis - self.waveHeight
				pointList = [QtCore.QPointF(a - self.timeDelta, yBasis - self.waveHeight/2),
						QtCore.QPointF(c - self.timeDelta, yBasis),
						QtCore.QPointF(c, yBasis),
						QtCore.QPointF(c, yBasis - self.waveHeight),
						QtCore.QPointF(c - self.timeDelta, yBasis - self.waveHeight)]
				if nextC in 'xX':
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
				elif self.currentColor != 'x':
					self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))


		if nextC == 'z':
			gx1 = xBasis + self.waveTransitionTime/2 + self.waveHalfDuration
			#draw lines last
			self.graphicsScene.addLine(QtCore.QLineF(gx1 - self.timeDelta, yBasis - self.waveHeight, 
						gx1 + self.waveTransitionTime - self.timeDelta, yBasis - self.waveHeight/2))
			self.graphicsScene.addLine(QtCore.QLineF(gx1 - self.timeDelta, yBasis, 
						gx1 + self.waveTransitionTime - self.timeDelta, yBasis - self.waveHeight/2))
			self.graphicsScene.addLine(QtCore.QLineF(gx1 + self.waveTransitionTime - self.timeDelta, yBasis - self.waveHeight/2, 
				x1, yBasis - self.waveHeight/2), self.triPen)

		if nextC not in 'zlrRpP':
			#angled line to top
			self.graphicsScene.addLine(QtCore.QLineF(x0 - self.timeDelta, y0, x1 - self.timeDelta, y1))
			if nextC in 'hfF':
				self.graphicsScene.addLine(QtCore.QLineF(x0 - self.timeDelta, y1, x1 - self.timeDelta, y1))
		elif nextC in 'lrR':
			self.graphicsScene.addLine(QtCore.QLineF(x0 - self.timeDelta, y0, x1 - self.timeDelta, y0))
		elif nextC in 'pP':
			self.graphicsScene.addLine(QtCore.QLineF(x0 - self.timeDelta, y1, x0 + self.waveTransitionTime - self.timeDelta, y0))
			self.graphicsScene.addLine(QtCore.QLineF(x0 - self.timeDelta, y0, x1 - self.timeDelta, y0))

		x0 = xBasis + self.waveTransitionTime/2
		x1 = x0 + self.waveHalfDuration
		y0 = yBasis - self.waveHeight
		#horizontal line at top
		self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1 - self.timeDelta, y0)) 
		x0 = x1
		x1 += self.waveTransitionTime
		y0 = yBasis - self.waveHeight
		y1 = yBasis
		if nextC not in 'zhfF':
			#angled line to bottom
			self.graphicsScene.addLine(QtCore.QLineF(x0 - self.timeDelta, y0, x1 - self.timeDelta, y1))

			#additional bottom lines needed to the right of crossover when timeDelta is enabled
			self.graphicsScene.addLine(QtCore.QLineF(x1 - self.timeDelta, y1, x1, y1)) 

		if nextC not in 'lrRzpP':
			#additional top lines needed to the right of crossover when timeDelta is enabled
			self.graphicsScene.addLine(QtCore.QLineF(x1 - self.timeDelta, y0, x1, y0))

		x0 = xBasis + self.waveTransitionTime/2
		x1 = x0 + self.waveHalfDuration
		y0 = yBasis
		y1 = y0

		#horizontal line at bottom
		self.graphicsScene.addLine(QtCore.QLineF(x0, y0, x1 - self.timeDelta, y0))
		self.pendingTimeDelta = self.timeDelta
		#print ("tdDrawDataDX: exiting... self.pendingTimeDelta=", self.pendingTimeDelta)

	def tdDrawSpace(self, waveCount, cmd, basis=(0, 0)):
		xBasis, yBasis = basis
		x0 = xBasis + self.waveTransitionTime/2
		if cmd.strip().find('<') == -1 and cmd.strip().find('>') == -1 and cmd.strip().find('-') == -1: #no arrow
			#print ("-- seeing 's', this line has arrows ...")
			if self.maxWaveCount == 0:
				self.drawGrid (xBasis + self.waveTransitionTime/2, yBasis, waveCount)
				#FIXME
				#draw the grid
				#if (self.evenGridsEnabled == True and (waveCount % 2) == 0):
				#	self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration,
				#		yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
				#		x0 + self.waveHalfDuration,
				#		yBasis), self.gridOtherPen)
				#elif (self.oddGridsEnabled == True and (waveCount % 2) == 1):
				#	self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration,
				#		yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
				#		x0 + self.waveHalfDuration,
				#		yBasis), self.gridPen)
		else:
			if self.maxWaveCount == 0:
				self.drawGrid (xBasis + self.waveTransitionTime/2, yBasis, waveCount)
				#FIXME
				#if (self.evenGridsEnabled == True and (waveCount % 2) == 0):
				#	self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration,
				#		yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2,
				#		x0 + self.waveHalfDuration,
				#		yBasis + self.arrowVertOffset), self.gridOtherPen)
				#elif (self.oddGridsEnabled == True and (waveCount % 2) == 1):
				#	self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration,
				#		yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2,
				#		x0 + self.waveHalfDuration,
				#		yBasis + self.arrowVertOffset), self.gridPen)
			

	def tdDrawTri(self, waveCount, nextC=None, basis=(0, 0)):
		xBasis, yBasis = basis
		x0 = xBasis + self.waveTransitionTime/2
		if nextC in "dDXxlhrRfFpP":
			x1 = x0 + self.waveHalfDuration
		else:
			x1 = x0 + self.waveHalfPeriod

		y0 = yBasis - self.waveHeight/2
		y1 = y0

		if self.maxWaveCount == 0:
			self.drawGrid (xBasis + self.waveTransitionTime/2, yBasis, waveCount)
			#FIXME
			#draw the grid
			#if (self.evenGridsEnabled == True and (waveCount % 2) == 0):
			#	self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration, yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
			#		x0 + self.waveHalfDuration, yBasis), self.gridOtherPen)
			#elif (self.oddGridsEnabled == True and (waveCount % 2) == 1):
			#	self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration, yBasis - self.waveHeight - self.signalWaveYSpacing + self.waveHeightChange/2, 
			#		x0 + self.waveHalfDuration, yBasis), self.gridPen)

		c = x1 + self.waveTransitionTime

		if nextC in 'xX' or (nextC in 'dD' and self.currentColor != 'x'):
			pointList = [QtCore.QPointF(x1 - self.timeDelta, y0),
					QtCore.QPointF(c - self.timeDelta, yBasis),
					QtCore.QPointF(c, yBasis),
					QtCore.QPointF(c, yBasis - self.waveHeight),
					QtCore.QPointF(c - self.timeDelta, yBasis - self.waveHeight)]
			if nextC in 'dD' and self.currentColor != 'x':
				color = "light grey"
				if self.currentColor in colorMap.keys():
					color = colorMap[self.currentColor]
				self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
			else:
				self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))

		if nextC in 'dDXx':
			self.graphicsScene.addLine(QtCore.QLineF(x1 - self.timeDelta, y0, 
				x1 + self.waveTransitionTime - self.timeDelta, yBasis - self.waveHeight))
			self.graphicsScene.addLine(QtCore.QLineF(x1 - self.timeDelta, y0, 
				x1 + self.waveTransitionTime - self.timeDelta, yBasis))
			self.graphicsScene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime - self.timeDelta, yBasis - self.waveHeight, 
				x1 + self.waveTransitionTime, yBasis - self.waveHeight))
			self.graphicsScene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime - self.timeDelta, yBasis, 
				x1 + self.waveTransitionTime, yBasis))
			self.graphicsScene.addLine(QtCore.QLineF(x0 - self.pendingTimeDelta, y0, x1 - self.timeDelta, y1), self.triPen)
		elif nextC in 'hfF':
			self.graphicsScene.addLine(QtCore.QLineF(x0, y0, c - self.waveTransitionTime - self.timeDelta, y0), self.triPen) 
			self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration - self.timeDelta, y0, c - self.timeDelta, yBasis - self.waveHeight))
			self.graphicsScene.addLine(QtCore.QLineF(c - self.timeDelta, yBasis - self.waveHeight, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
		elif nextC in 'lrRpP':
			self.graphicsScene.addLine(QtCore.QLineF(x0, y0, c - self.waveTransitionTime - self.timeDelta, y0), self.triPen)
			self.graphicsScene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration - self.timeDelta, y0, c - self.timeDelta, yBasis))
			self.graphicsScene.addLine(QtCore.QLineF(c - self.timeDelta, yBasis, x1 + self.waveTransitionTime, yBasis))
		else:
			self.graphicsScene.addLine(QtCore.QLineF(x0, y0, c - self.waveTransitionTime, y0), self.triPen)
	
		self.pendingTimeDelta = self.timeDelta
		#print ("tdDrawTri: exiting... self.pendingTimeDelta=", self.pendingTimeDelta)

	def tdDrawGap(self, waveCount, lastC=None, nextC=None, basis=(0, 0)):
		xBasis, yBasis = basis
		xShift = -6
		x0 = xBasis - self.waveHalfDuration/2 + xShift
		color = self.gapPenColor

		pointList = [QtCore.QPointF(x0 - 5, yBasis - self.waveHeight - self.signalWaveYSpacing/4),
			QtCore.QPointF(x0 + 2, yBasis - 3*self.waveHeight/4),
			QtCore.QPointF(x0 - 12, yBasis - self.waveHeight/4),
			QtCore.QPointF(x0 - 5, yBasis + self.signalWaveYSpacing/4),

			QtCore.QPointF(x0 + 7, yBasis + self.signalWaveYSpacing/4),
			QtCore.QPointF(x0, yBasis - self.waveHeight/4),
			QtCore.QPointF(x0 + 17, yBasis - 3*self.waveHeight/4),
			QtCore.QPointF(x0 + 7, yBasis - self.waveHeight - self.signalWaveYSpacing/4)]

		self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList),
			QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))

		path = QPainterPath()
		path.moveTo(QtCore.QPointF(x0 - 5, yBasis - self.waveHeight - self.signalWaveYSpacing/4))
		path.cubicTo(
					QtCore.QPointF(x0 + 20, yBasis - 3*self.waveHeight/4),
					QtCore.QPointF(x0 - 28, yBasis - self.waveHeight/4),
					QtCore.QPointF(x0 - 5, yBasis + self.signalWaveYSpacing/4))
		self.graphicsScene.addPath(path, self.gapPen)
		path.moveTo(QtCore.QPointF(x0 + 7, yBasis - self.waveHeight - self.signalWaveYSpacing/4))
		path.cubicTo(
					QtCore.QPointF(x0 + 30, yBasis - 3*self.waveHeight/4),
					QtCore.QPointF(x0 - 15, yBasis - self.waveHeight/4),
					QtCore.QPointF(x0 + 7, yBasis + self.signalWaveYSpacing/4))
		self.graphicsScene.addPath(path, self.gapPen)


	def tdDrawGapDontUse(self, waveCount, lastC=None, nextC=None, basis=(0, 0)):
		xBasis, yBasis = basis
		x0 = xBasis - self.waveHalfDuration - 5
		xstep = -25
		xstep2 = 15

		pointList = [
			QtCore.QPointF(x0 + self.waveHalfDuration/2 + xstep, yBasis - self.gapHeight - self.signalWaveYSpacing/2),
			QtCore.QPointF(x0 + self.waveHalfDuration/2 + 7 + xstep, yBasis - 3*self.gapHeight/4),
			QtCore.QPointF(x0 + self.waveHalfDuration/2 - 7 + xstep, yBasis - self.gapHeight/4),
			QtCore.QPointF(x0 + self.waveHalfDuration/2 + xstep, yBasis + self.signalWaveYSpacing/2),

			QtCore.QPointF(x0 + self.waveHalfDuration/2 + xstep2, yBasis + self.signalWaveYSpacing/2),
			QtCore.QPointF(x0 + self.waveHalfDuration/2 - 7 + xstep2, yBasis - self.gapHeight/4),
			QtCore.QPointF(x0 + self.waveHalfDuration/2 + 7 + xstep2, yBasis - 3*self.gapHeight/4),
			QtCore.QPointF(x0 + self.waveHalfDuration/2 + xstep2, yBasis - self.gapHeight - self.signalWaveYSpacing/2)]

		p = self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), self.gapBrush)
		p.setZValue(2)
		p = self.graphicsScene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), self.gapBrush)
		###p.setBrush(QtGui.QBrush(Qt.DiagCrossPattern))
		p.setBrush(QtGui.QBrush(QtGui.QColor(self.gapBrushColor)))
		p.setZValue(3)

def main():
	app = QApplication(sys.argv)
	icon = QtGui.QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "td.ico"))
	form = TimingDiagrammer()
	form.setWindowIcon(icon)
	form.show()
	app.exec_()

if __name__ == '__main__':
	main()
