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
from PyQt5.QtGui import QPainter, QPixmap, QPainterPath
from PyQt5.QtWidgets import (
	QApplication, QGraphicsScene, 
	QFileDialog, QGraphicsTextItem, 
	QMessageBox)
from PyQt5.QtCore import Qt
import sys, os, math
import TimingDiagrammerUI

fontMap = {'sans':'Sans', 'serif':'Serif', 
			'mono':'Monospace', 'fixed': 'Fixed',
			}

colorMap = {
	'a': 'antiquewhite', 
	'A': 'aquamarine', 
	'b': 'light blue', 
	'B': 'bisque', 
	'c': 'lightcyan', 
	'C': 'cornflowerblue', 
	'd': 'skyblue', 
	'D': 'deepskyblue', 
	'g': 'mediumaquamarine', 
	'G': 'springgreen', 
	'l': 'lavender', 
	'm': 'mistyrose', 
	'k': 'khaki', 
	'o': 'orange',
	'O': 'orchid',
	'p': 'pink', 
	'P': 'peachpuff', 
	'r': 'rosybrown', 
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
	'i': 'indigo', 
	'l': 'limegreen', 
	'm': 'maroon', 
	'M': 'magenta', 
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
		super(TimingDiagrammer, self).__init__(parent)
		self.setupUi(self)
		self.actionNew.triggered.connect(self.fileNew)
		self.actionOpen.triggered.connect(self.fileOpen)
		self.actionSave.triggered.connect(self.fileSave)
		self.actionSaveAs.triggered.connect(self.fileSaveAs)
		self.actionExport.triggered.connect(self.fileExport)
		self.actionExit.triggered.connect(self.fileExit)
		self.actionSettings.triggered.connect(self.optionsSettings)

		self.setAutoFillBackground(True)
		self.scene = QGraphicsScene(self)
		self.scene.setBackgroundBrush(Qt.white);

		self.graphicsView.setAlignment(Qt.AlignTop | Qt.AlignLeft)
		self.graphicsView.setScene(self.scene)
		#self.graphicsView.setRenderHints(QPainter.Antialiasing) # | QPainter.HighQualityAntialiasing)
		self.xMargin = 30
		self.yMargin = 50
		self.scene.addLine(QtCore.QLineF(-self.xMargin, -self.yMargin, -self.xMargin-1, -self.yMargin-1), QtGui.QPen(Qt.transparent)) #to anchor to top left


		self.gridPenColor = "#aaaaaa"
		self.gridPen = QtGui.QPen(Qt.DotLine)
		self.gridPen.setColor(QtGui.QColor(self.gridPenColor))

		self.triPenColor = "olive"
		self.triPen = QtGui.QPen()
		self.triPen.setColor(QtGui.QColor(self.triPenColor))

		self.gapBrushColor = "#eeeeee"
		self.gapPen = QtGui.QPen()
		self.gapPen.setColor(QtGui.QColor(self.gapBrushColor))
		self.gapPen.setWidth(7)

		self.riseClockArrow = False
		self.fallClockArrow = False
		self.droppedXCoord = -1
		self.droppedYCoord = -1
		self.pendingArrowDelay = 0
		self.parent = parent
		self.currentLineNumber = 1
		self.arrowSize = 9
		self.arrowLineAdjust = 9
		self.arrowTextAdjust = 46
		self.currentLineHasArrow = False
		self.waveHeight = 30
		self.waveHalfDuration = 40
		self.waveTransitionTime = 10
		self.timeDelta = 0
		self.waveHalfPeriod = self.waveHalfDuration + self.waveTransitionTime
		self.sigNameColWidth = 50
		self.sigNameFont = "Sans"
		self.sigNameFontSize = 12
		self.signalNameXOffset = 10
		self.signalNameXSpacing = 50
		self.signalWaveXOffset = 50
		self.signalWaveYOffset = 90
		self.signalWaveYSpacing = 35
		self.arrowVertOffset = -self.waveHeight/2 - self.signalWaveYSpacing
		self.textVertOffset = -self.waveHeight/2
		self.arrowMarkAdjustUp = self.waveHeight
		self.arrowMarkAdjustDn = self.waveHeight/4
		self.fontName = 'Sans'
		self.fontSize = 10
		self.editorIsModified = False
		self.preferenceValuesList = []
		self.evenGridsEnabledGlobal = True
		self.oddGridsEnabledGlobal = True

		self.currentDirName = "."
		self.currentFileName = ""
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
		self.setWindowTitle("Timing Diagrammer - Untitled")

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

	def resolvednextCDONTUSE (self, cmd):
		#when next char is in 0123456789|/,
		#returns the first non-integer
		#in the stream
		#print ("called resolved with ", cmd)
		if cmd == '':
			return ''
		if cmd[0] in '0123456789|/$':
			i = 0
			val = '0'
			while val in '0123456789|/$':
				#print (" -- i = ", i, " -- len cmd = ", len(cmd))
				if i == len (cmd) - 1:
					#print (" --breaking-- i = ", i, " -- len cmd = ", len(cmd))
					break
				val = cmd[i+1]
				#print ("- val is now = ", val)
				i += 1
			if cmd[i] not in "0123456789|/":
				nxt = cmd[i]
			else:
				nxt = chr(0)
			return nxt #next is modifier, next char
		else:
			return cmd[0]

	def tdDrawArrowHead(self, startPoint, direction='L'): #returns QPolygonF
		x, y = startPoint
		arrowSize = self.arrowSize
		if direction == 'R':
			arrowSize = -arrowSize

		pointList = [QtCore.QPointF(x, y),
						QtCore.QPointF(x + arrowSize, y - arrowSize/2),
						QtCore.QPointF(x + arrowSize*3/4, y),
						QtCore.QPointF(x + arrowSize, y + arrowSize/2),
						QtCore.QPointF(x, y)]
		p = self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("black")))
		p.setZValue(1)
					

	def getfvLists(self, annotSpecCmd):
		#print ("getfvLists: annotSpecCmd = ", annotSpecCmd)
		attributeMapList = []
		if annotSpecCmd == '':
			#print ("getfvLists: null cmd4")
			return attributeMapList
		for step in annotSpecCmd.split(','):
			#print ("step is ", step)
			attributeMap = {}
			attributeMap['delay'] = 0
			attributeMap['width'] = 199
			attributeMap['color'] = 'black'
			attributeMap['font'] = self.fontName
			attributeMap['size'] = self.fontSize
			attributeMap['vert'] = 0
			attributeMap['center'] = True
			if step == '':
				attributeMapList.append(attributeMap)
				continue
			step = step.replace('  ', ' ')
			step = step.replace(' =', '=')
			step = step.replace('= ', '=')
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
					if value > 50:
						value = 50
					attributeMap['delay'] = int(value)
				elif field == "width":
					try:
						value = int(value)
						if value < 20:
							value = 20
						#print ("appended width = ", value)
					except:
						value = 199
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
						value = int(val)
					except:
						value = 0
					if value > 20:
						value = 20
					attributeMap['vert'] = int(value * (self.waveHeight + self.signalWaveYSpacing) / 15)
			attributeMapList.append(attributeMap)
	
		#print ("===============================")
		#print ("attributeMapList = ", attributeMapList)
	
		return attributeMapList

	def doAnnotationCmd (self, cmd, annotSpecCmd):
		attributeMapList = self.getfvLists(annotSpecCmd.strip())

		if self.currentLineHasArrow == True:
			self.textVertOffset = self.arrowVertOffset + self.arrowTextAdjust
		else:
			self.textVertOffset = -self.waveHeight/2

		annotNum = 0
		#print ("doAnnotationCmd: cmd = ", cmd)
		for annot in cmd.split(','):
			annot = annot.replace(chr(1), '#')
			annot = annot.replace(chr(2), ';')
			annot = annot.replace(chr(6), ',')
			#print ("doAnnotationCmd: annot = ", annot)
			if len(attributeMapList) > 0:
				delay = attributeMapList[0]['delay']
				width = attributeMapList[0]['width']
				color = attributeMapList[0]['color']
				font = attributeMapList[0]['font']
				size = attributeMapList[0]['size']
				vert = attributeMapList[0]['vert']
				center = attributeMapList[0]['center']
				attributeMapList = attributeMapList[1:]
			else:
				delay = 0
				width = 199
				color = 'black'
				font = self.fontName
				size = self.fontSize
				vert = 0
				center = True

			#print ("delay = ", delay, "width = ", width, "color = ", color, "vertAdj = ", vertAdj," -- annot is ", annot)
			if annot != '':
				#print ("annotNum = ", annotNum)

				self.putText(annot, self.sigNameColWidth + 
					self.signalWaveXOffset + 
					self.waveHalfPeriod * delay / 9 +
					self.waveHalfPeriod * annotNum + (self.waveHalfPeriod/2 if center == True else 0),
					self.signalWaveYOffset +
					(self.currentLineNumber - self.linesWithArrow * self.arrowLineAdjust / 9) *
						(self.waveHeight + self.signalWaveYSpacing) + self.linesWithArrow * 2 * self.arrowLineAdjust + self.textVertOffset - vert, center, 
						font, size, color, width, self.currentLineHasArrow)
						
			annotNum += 1

	def processCommand (self, cmd, line, cmdNum, cmd3isNull, cmd4):
		#print ("processCommand: cmdNum = ", cmdNum, "cmd = ", cmd, "cmd4 = ", cmd4)
		if cmdNum == 1:
			#process signal name
			#simplifies parsing multi-char tokens
			cmd = cmd.replace(chr(2), ';')
			cmd = cmd.replace(chr(6), ',')
			cmd = cmd.replace(chr(1), '#')
			self.tdDrawText(cmd)

		elif cmdNum == 2:
			self.currentLineHasArrow = False
			#process waves
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
				#print ("processCmd-mainloop: thisC=", thisC, " ord lastC=", ord(lastC), lastC)
				if lastC == '$':
					#print ("processCmd-mainloop: lastC was $")
					cNum += 1
					self.currentColor = thisC
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
				yBasis = self.signalWaveYOffset + (self.currentLineNumber - self.linesWithArrow * self.arrowLineAdjust / 9) *\
					(self.waveHeight + self.signalWaveYSpacing) + self.linesWithArrow * 2 * self.arrowLineAdjust

				if thisC == '|':
					if waveCount > 0:
						x0 = xBasis
						self.scene.addLine(QtCore.QLineF(x0 - self.waveTransitionTime/2 - self.timeDelta,
							yBasis - self.waveHeight - self.arrowMarkAdjustUp,
							x0 - self.waveTransitionTime/2 - self.timeDelta,
							yBasis + self.arrowMarkAdjustDn))
				elif thisC in 'PpCcKkQq': #clock pulses
					if thisC == "Q":
						self.riseClockArrow = True
						self.fallClockArrow = True
						#self.tdDrawClock(waveCount, "P", nextC, (xBasis, yBasis))
						self.tdDrawClock(waveCount, 'P', 'Pp'['CcKkQq'.find(nextC)%2], (xBasis, yBasis))
					elif thisC == "q":
						self.riseClockArrow = True
						self.fallClockArrow = True
						#self.tdDrawClock(waveCount, 'p', nextC, (xBasis, yBasis))
						self.tdDrawClock(waveCount, 'p', 'Pp'['CcKkQq'.find(nextC)%2], (xBasis, yBasis))
					elif thisC == "K":
						self.riseClockArrow = False
						self.fallClockArrow = True
						#self.tdDrawClock(waveCount, 'P', nextC, (xBasis, yBasis))
						self.tdDrawClock(waveCount, 'P', 'Pp'['CcKkQq'.find(nextC)%2], (xBasis, yBasis))
					elif thisC == "k":
						self.riseClockArrow = False
						self.fallClockArrow = True
						#self.tdDrawClock(waveCount, 'p', nextC, (xBasis, yBasis))
						self.tdDrawClock(waveCount, 'p', 'Pp'['CcKkQq'.find(nextC)%2], (xBasis, yBasis))
					elif thisC == "C":
						self.riseClockArrow = True
						self.fallClockArrow = False
						#self.tdDrawClock(waveCount, 'P', nextC, (xBasis, yBasis))
						self.tdDrawClock(waveCount, 'P', 'Pp'['CcKkQq'.find(nextC)%2], (xBasis, yBasis))
					elif thisC == "c":
						self.riseClockArrow = True
						self.fallClockArrow = False
						#self.tdDrawClock(waveCount, 'p', nextC, (xBasis, yBasis))
						self.tdDrawClock(waveCount, 'p', 'Pp'['CcKkQq'.find(nextC)%2], (xBasis, yBasis))
					else:
						self.riseClockArrow = False
						self.fallClockArrow = False
						self.tdDrawClock(waveCount, thisC, nextC, (xBasis, yBasis))
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
					self.tdDrawLow(waveCount, nextC, (xBasis, yBasis))
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
				elif thisC == 's':
					self.tdDrawSpace(waveCount, cmd, (xBasis, yBasis))
					waveCount += 1
					self.timeDelta = 0
				elif thisC == '<' or thisC == '>' or thisC == '-':
					self.currentLineHasArrow = True
					self.tdDrawHorizArrow(waveCount, thisC, nextC, (xBasis, yBasis))
					if thisC != '>':
						waveCount += 1
				elif thisC in "0123456789":
					#print (" -- additional delay = ", self.timeDelta)
					#a number follows a command for additional delay
					self.timeDelta = int(int(thisC) * self.waveHalfDuration / 9)
					#print (" -- additional delay set to = ", self.timeDelta)

				elif thisC == '/':
					self.tdDrawGap(waveCount, lastC, nextC, (xBasis, yBasis))
					self.timeDelta = 0
				elif thisC != '$':
					#print ("Error: Wrong code: " + thisC + ".")
					self.label.setText("Error: Wrong code: " + thisC + ".")

				cNum += 1
				if line == 1:
					topSpacing = self.waveHeight
				else:
					topSpacing = 0

				# vertical line on the signal name
				self.scene.addLine(QtCore.QLineF(self.signalWaveXOffset + self.sigNameColWidth, 
					yBasis - topSpacing - self.signalWaveYSpacing, 
					self.signalWaveXOffset + self.sigNameColWidth, 
					yBasis + self.waveHeight))
				
				if thisC not in '0123456789/':
					#print ("char is NOT FWDSLASH -- thisC = ", thisC)
					lastC = thisC

				#FIXME: move the scene location that was changed into the graphics viewport
				#self.graphicsView.ensureVisible(xBasis, yBasis, self.waveHalfPeriod, self.signalWaveYSpacing)
			#for

			#print ("-- cmdNum is 2 -- A seeing cmd = ", cmd, " self.currentLineHasArrow = ", self.currentLineHasArrow)
			if self.currentLineHasArrow == True:# and cmd3isNull == True:
				self.arrowVertOffset = -self.waveHeight/2 - self.signalWaveYSpacing
				self.linesWithArrow += 1

			self.timeDelta = 0
					
		elif cmdNum == 3:
			#print ("-- B seeing cmd = ", cmd, "-- seeing cmd4 = ", cmd4, " self.currentLineHasArrow = ", self.currentLineHasArrow)
			if self.currentLineHasArrow == True:
				self.arrowVertOffset = -self.waveHeight/2 - self.signalWaveYSpacing
				self.doAnnotationCmd (cmd, cmd4)
			else:
				self.doAnnotationCmd (cmd, cmd4)
			#print ("-- B self.linesWithArrow = ", self.linesWithArrow)

	def processDirective (self, data):
		#print ("processDirective: data is ", data)
		directiveList = data.strip().split()
		if directiveList[0] == "grid":
			#print ("----show grid directive found")
			if directiveList[1] == "both":
				#print ("------show grid both directive found")
				self.evenGridsEnabledGlobal = True
				self.oddGridsEnabledGlobal = True
			elif directiveList[1] == "even":
				self.evenGridsEnabledGlobal = True
				self.oddGridsEnabledGlobal = False
			elif directiveList[1] == "odd":
				self.evenGridsEnabledGlobal = False
				self.oddGridsEnabledGlobal = True
		else:
			if len(directiveList) > 1:
				try:
					val2 = int(directiveList[1])
				except:
					val2 = -1
			else:
				val2 = -1
			#print ("val2 = ", val2)
			if directiveList[0] == "arrtxtadj":
				self.arrowTextAdjust = max (0, val2)
				self.arrowTextAdjust = min (self.arrowTextAdjust, 46)
			elif directiveList[0] == "arrowadj":
				self.arrowLineAdjust = max (0, val2)	
				self.arrowLineAdjust = min (self.arrowLineAdjust, 9)	
			elif directiveList[0] == "arradjup":
				self.arrowMarkAdjustUp = max (0, val2)	
				self.arrowMarkAdjustUp = min (self.arrowMarkAdjustUp, self.waveHeight*2)	
			elif directiveList[0] == "arradjdn":
				self.arrowMarkAdjustDn = max (0, val2)
				self.arrowMarkAdjustDn = min (self.arrowMarkAdjustDn, self.waveHeight*2)
			elif val2 > 19 and directiveList[0] == "height":
				self.waveHeight = val2
			elif val2 > 39 and directiveList[0] == "tick":
				self.waveHalfPeriod = int(val2 / 2)
				self.waveHalfDuration = self.waveHalfPeriod - self.waveTransitionTime
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
			elif directiveList[0] == "signalwidth":
				if len(directiveList) > 1:
					try:
						val2 = int(directiveList[1])
					except:
						self.sigNameColWidth = 100

					if val2 > 20 and val2 < 500:
						self.sigNameColWidth = val2
					else:
						self.sigNameColWidth = 100
				else:
					self.sigNameColWidth = 100


	def drawWaves1Line (self, line, data):
		self.pendingArrowDelay = 0
		dataList = data.strip().split(';')
		#print ("drawWaves1Line: dataList = ", dataList)
		cmdNum = 0
		for cmd in dataList:
			####if cmd.find('some text data') >= 0 or cmd.find('AOIR1') >= 0:
			####	print ("====textVertOffset is ", self.textVertOffset)
			#cmd = cmd.replace (chr(2), ';') #put back the ';' character
			cmd4 = ''
			#print ("cmd is ", cmd, "line value passed is ", line, "cmdNum = ", cmdNum)
			if cmdNum == 0:
				cmdNum = 1
				self.currentLineNumber = line
			cmd3isNull = True
			if cmdNum == 2 and len(dataList) > 2:
				#for arrows in cmd2, send information whether cmd3 is null
				#or doesn't exist
				cmd3isNull = (dataList[2].strip() == '')
					
			if cmdNum == 3 and len(dataList) == 4:
				#for the annotation command, send the adjustment that follows in cmd4
				cmd4 = dataList[3]
			#print ("cmd4 is ", cmd4, "line value passed is ", line, "cmdNum = ", cmdNum)
			self.processCommand(cmd, line, cmdNum, cmd3isNull, cmd4)
			cmdNum += 1

	def reDrawCanvas (self, keyVal=''):
		self.scene.clear()
		self.linesWithArrow = 0
		lastLine = self.plainTextEdit.document().lineCount()
		dataArray = []
		line = 0
		for i in range (0, lastLine):
			data = self.plainTextEdit.document().findBlockByLineNumber(i).text()
			if i == lastLine - 1:
				data += keyVal
			data = data.replace('\#', chr(1)) #replace literal '#' before separating comments
			data = data.replace('\;', chr(2)) #replace literal ';' before separating comments
			data = data.replace('\,', chr(6)) #replace literal ','
			if data.strip().find('#!') == 0:
				if data[2:] != '':
					self.processDirective(data[2:])
					continue
			dataList = data.split('#')
			#print ("========DATALIST = ", dataList)
			command = dataList[0].strip()
			#print ("==============command = ", command)
			if command != '':
				#print ("==============calling drawWaves1Line with data = ", data)
				self.drawWaves1Line (line, data)
				line += 1

		self.label.setText("Status: Ready")
		self.currentLineHasArrow = False
		self.textVertOffset = -self.waveHeight/2

	def textChangedHandler(self):
		self.editorIsModified = True
		self.plainTextEdit.ensureCursorVisible()
		self.setWindowTitle("Timing Diagrammer - " + self.currentFileName + " [modified]")
		self.reDrawCanvas()

	def closeEvent(self, event):
		event.accept()
		self.fileExit()

	def fileNew (self, event=None):
		self.currentFileName = ""
		self.setWindowTitle("Timing Diagrammer - Untitled")
		if self.editorIsModified == True:
			self.fileSave(None)
		self.scene.clear()
		self.plainTextEdit.clear()
		self.editorIsModified == False

	def fileOpen (self, event=None):
		if self.editorIsModified == True:
			self.fileSave(None)

		self.expandDir()
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fDialog = QFileDialog()
		fDialog.setDirectory(self.currentDirName)
		fileName, _ = fDialog.getOpenFileName(self,"Open Timing Diagrammer File", "","*.tim", options=options)
		self.currentDirName = os.path.dirname(fileName)
		self.currentFileName = os.path.basename(fileName)

		if self.currentFileName == '':
			return
		if not os.path.isfile(fileName) or self.currentFileName == '':
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Error: File " + fileName + " not found.")
			msg.setWindowTitle("File Not Found Error")
			msg.exec_()
			return

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
			self.currentDirName = '.'
		else:
			self.currentDirName = os.path.expanduser(self.currentDirName)

	def writeCurrentFileBackend(self):
		self.expandDir()
		fullFileName = os.path.join(self.currentDirName, self.currentFileName)
		try:
			with open(fullFileName, 'w', encoding="utf-8", newline='\n') as f:
				f.write(self.plainTextEdit.toPlainText())
				f.close()
				self.editorIsModified = False
				self.setWindowTitle("Timing Diagrammer - " + self.currentFileName)
		except:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Error: Could not write to file " + fullFileName + ".")
			msg.setWindowTitle("File Write Error")
			msg.exec_()

	def writeCurrentFile (self):
		if self.currentFileName[-4:] != '.tim':
			self.currentFileName += '.tim'
		if os.name == 'nt':
			self.currentFileName = self.currentFileName.lower()
		if self.currentFileName != '.tim' and os.path.exists(self.currentDirName):
			qm = QMessageBox()
			qm.setIcon(QMessageBox.Question)
			ret = qm.Yes
			if os.path.isfile(self.currentFileName):
				ret = qm.question(self,'File Exists', "File exists. Overwrite?", qm.Yes | qm.No)
			if ret == qm.Yes:
				self.writeCurrentFileBackend()
		elif self.currentFileName == '.tim':
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Error: Illegal file name.")
			msg.setWindowTitle("File Write Error")
			msg.exec_()
		elif not os.path.exists(self.currentDirName):
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Error: Illegal directory.")
			msg.setWindowTitle("File Write Error")
			msg.exec_()

	def fileSave (self, event=None):
		print ("fileSave: self.currentFileName = ", self.currentFileName)
		if self.currentFileName != '' and self.currentFileName != '.tim':
			self.writeCurrentFile()
		else:
			self.fileSaveAs(None)

	def fileSaveAs (self, event=None):
		fDialog = QFileDialog()
		if not os.path.exists(self.currentDirName):
			self.currentDirName = "."
		fDialog.setDirectory(self.currentDirName)
		fileName, _ = fDialog.getSaveFileName(self, 'Save File', '', '*.tim')
		print ("fileSaveAs: fileName = ", fileName)
		if fileName != '' and fileName != '.tim':
			self.currentDirName = os.path.dirname(fileName)
			self.currentFileName = os.path.basename(fileName)
			self.writeCurrentFile()

	def fileExport (self, event=None):
		size = QtCore.QRectF(self.scene.sceneRect()).toRect().size()
		x = size.width() + self.xMargin 
		y = size.height() + self.yMargin
	
		#draw a marker at bottom right
		self.scene.addLine(QtCore.QLineF(x, y, x+1, y+1)) #to anchor to bottom right

		size = QtCore.QRectF(self.scene.sceneRect()).toRect().size()
		pixmap = QPixmap(size).scaled(size.width()*2, size.height()*2)
		pixmap.fill(QtGui.QColor("white"))
		painter = QPainter(pixmap)
		self.scene.render(painter)
		painter.end()		
		canExport = False
		if self.currentFileName != '' and self.currentFileName != '.tim':
			if self.currentFileName[-4:] == '.tim' and os.path.exists(self.currentDirName):
				fullFileName = os.path.join(self.currentDirName, self.currentFileName[:self.currentFileName.rfind('.')])
			else:
				fullFileName = "./waves"
			canExport = True
		else:
			qm = QMessageBox()
			qm.setIcon(QMessageBox.Question)
			ret = qm.Yes
			if not os.path.isfile(self.currentFileName):
				ret = qm.question(self,'File Save Requirement', "File must be saved before exporting. Continue?", qm.Yes | qm.No)
				if ret == qm.Yes:
					self.fileSaveAs(None)
					canExport = True
		if canExport == True:
			fullFileName = os.path.join(self.currentDirName, self.currentFileName[:self.currentFileName.rfind('.')])
			pixmap.save(fullFileName + ".jpg")
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setText("Success: Waveform exported to image:" + fullFileName + ".jpg.")
			msg.setWindowTitle("Waveform Export")
			msg.exec_()

	def fileExit (self, event=None):
		#print ("fileExit: self.fileExit = ", self.editorIsModified)
		if self.editorIsModified == True:
			qm = QMessageBox()
			qm.setIcon(QMessageBox.Question)
			ret = qm.question(self,'Unsaved code', "Code has not been saved. Save?", qm.Yes | qm.No)
			if ret == qm.Yes:
				self.fileSave(None)

		self.close()

	def optionsSettings (self, event=None):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Information)
		msg.setText("Timing Diagrammer is under construction.")
		msg.setWindowTitle("Timing Diagrammer Notice")
		msg.exec_()

	def textWidthHeight(self, qtext):
		boundingRect = qtext.boundingRect().toRect().size()
		#print ("boundingRect size = ", boundingRect)
		width = boundingRect.width()
		height = boundingRect.height()
		return width, height

	def putText(self, text, x, y, adjust=True, font="Sans", fsize=10, color="black", wrapWidth=199, fill=True):
		textTrimmed = text.lstrip()
		numSpaces = len(text) - len(textTrimmed)
		xWithSpaces = x + numSpaces * 3
		qtext = self.scene.addText(textTrimmed, QtGui.QFont(font, fsize, QtGui.QFont.Light))
		qtext.setDefaultTextColor(QtGui.QColor(color))
		width, height = self.textWidthHeight(qtext)
		qtext.setTextWidth(wrapWidth)
		qtext.setZValue(2)

		if adjust == True:
			if fill == True:
				r = self.scene.addRect(QtCore.QRectF(xWithSpaces - width/2, y - height/2, width, height), 
					QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("white")))
				r.setZValue(1)
			qtext.setPos(xWithSpaces - width/2, y - height/2)
		else:
			if fill == True:
				r = self.scene.addRect(QtCore.QRectF(x, y - height/2, width, height), 
					QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("white")))
				r.setZValue(1)
			qtext.setPos(x, y - height/2)
		
	def tdDrawText(self, text):
		qtext = self.scene.addText(text)
		boundingRect = qtext.boundingRect().toRect().size()
		#print ("boundingRect size = ", boundingRect)
		#fix alignment and anchor
		width = boundingRect.width()
		height = boundingRect.height()

		x = self.signalNameXSpacing + self.sigNameColWidth
		y = self.signalWaveYOffset + (self.currentLineNumber - self.linesWithArrow * self.arrowLineAdjust / 9) *\
			(self.waveHeight + self.signalWaveYSpacing) + self.linesWithArrow * 2 * self.arrowLineAdjust

		qtext.setPos(x - width, y - self.waveHeight/2 - height/2)

		if width > self.sigNameColWidth:
			width -= self.sigNameColWidth

		#this is to ensure jpeg export with adequate margins
		self.scene.addLine(QtCore.QLineF(-width, 0, -width-self.sigNameColWidth-1, 0), QtGui.QPen(Qt.transparent)) #to anchor to top left

	def tdDrawHorizArrow(self, waveCount=-1, thisC=None, nextC=None, basis=(0, 0)):
		xBasis, yBasis = basis
		self.textVertOffset = -self.waveHeight
		y0 = yBasis + self.arrowVertOffset
		if thisC == '<':
			self.pendingArrowDelay = self.timeDelta
			#print ("saw < -- arrowVertOffset = ", self.arrowVertOffset)
			a = xBasis + self.timeDelta
			c = xBasis + self.waveHalfDuration + self.waveTransitionTime/2
			if waveCount != 0:
				a -= self.waveTransitionTime/2
			self.tdDrawArrowHead((a, y0), 'L')
			l = self.scene.addLine(QtCore.QLineF(a, y0, c, y0))
			l.setZValue(1)

			l = self.scene.addLine(QtCore.QLineF(a,
				yBasis - self.waveHeight - self.arrowMarkAdjustUp,
				a, y0 + self.arrowMarkAdjustDn))
			l.setZValue(1)

		elif thisC == '>':
			#print ("saw > -- arrowVertOffset = ", self.arrowVertOffset)
			a = xBasis - self.waveTransitionTime/2 + self.pendingArrowDelay
			y0 = yBasis + self.arrowVertOffset
			
			self.tdDrawArrowHead((a, y0), 'R')
			self.scene.addLine(QtCore.QLineF(a, y0, 
				a, y0))

			self.scene.addLine(QtCore.QLineF(a, yBasis - self.waveHeight - self.arrowMarkAdjustUp,
				a, y0 + self.arrowMarkAdjustDn))
			self.pendingArrowDelay = 0 #reset back to 0

		elif thisC == '-':
			#print ("saw - -- arrowVertOffset = ", self.arrowVertOffset)
			a = xBasis - self.waveTransitionTime/2
			c = xBasis + self.waveHalfDuration + self.waveTransitionTime/2 + self.pendingArrowDelay
			if waveCount == 0:
				a = xBasis + self.timeDelta
			self.scene.addLine(QtCore.QLineF(a, y0, 
				c, y0))

		self.timeDelta = 0
		self.currentLineHasArrow = True

	def tdDrawClock(self, waveCount=-1, thisC=None, nextC=None, basis=(0, 0)):
		xBasis, yBasis = basis
		if thisC == 'P': #upper case
			#print ("Doing P -- at the beginning seeing timeDelata =", self.timeDelta)
			#print ("self.riseClockArrow = ", self.riseClockArrow, " self.fallClockArrow = ", self.fallClockArrow)
			x0 = xBasis
			x1 = x0 + self.waveHalfDuration + self.timeDelta
			if waveCount == 0:
				x0 += self.waveTransitionTime/2 #tweak to match the start time of non-clock signals
			y0 = yBasis
			y1 = yBasis

			self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))

			#draw the grid
			if self.evenGridsEnabledGlobal == True:
				self.scene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime/2 - self.timeDelta, 
					yBasis - self.waveHeight - self.signalWaveYSpacing, 
					x1 + self.waveTransitionTime/2 - self.timeDelta, 
					yBasis), self.gridPen)

			x0 = x1 
			x1 += self.waveTransitionTime
			y0 = yBasis
			y1 = yBasis - self.waveHeight
			self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))

			x0 = x1
			x1 += self.waveHalfDuration - self.timeDelta
			y0 = yBasis - self.waveHeight
			y1 = yBasis - self.waveHeight
			self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))

			#draw the falling edge grid
			if self.oddGridsEnabledGlobal == True:
				self.scene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime/2, 
					yBasis - self.waveHeight - self.signalWaveYSpacing, 
					x1 + self.waveTransitionTime/2, 
					yBasis), self.gridPen)

			#print ("thisC is UPPER P and nextC is ", nextC, " cmdNum = ", cmdNum)
			if nextC in "pP":
				#print ("CASE UPPER P of P is seen")
				x0 = x1 
				x1 += self.waveTransitionTime
				y0 = yBasis - self.waveHeight
				y1 = yBasis
				self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))

				x0 = x1
				x1 += self.waveTransitionTime/2 
				y0 = yBasis
				y1 = yBasis
				self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))
			elif nextC == 'z':
				x0 = x1
				x1 += self.waveTransitionTime
				y0 = yBasis - self.waveHeight
				y1 = yBasis - self.waveHeight/2
				self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))
				self.scene.addLine(QtCore.QLineF(x1, y1, x1 + self.waveTransitionTime/2, y1))
			elif nextC in 'hfF':
				x0 = x1
				x1 += self.waveTransitionTime
				self.scene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, 
					x1, yBasis - self.waveHeight))
				self.scene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight, 
					x1 + self.waveTransitionTime/2, yBasis - self.waveHeight))
			elif nextC in 'lrR':
				x0 = x1
				x1 += self.waveTransitionTime
				self.scene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, 
					x1, yBasis))
				self.scene.addLine(QtCore.QLineF(x1, yBasis, 
					x1 + self.waveTransitionTime/2, yBasis))
			elif nextC in 'DdXx':
				x0 = x1
				x1 += self.waveTransitionTime/2
				#print ("nextC in DdXx")
				#print ("self.currentColor == ", self.currentColor)
				if nextC in 'Dd' and self.currentColor != 'w':
					color = colorMap[self.currentColor]
				else:
					color = "light grey"

				if nextC in 'Xx' or (nextC in 'Dd' and self.currentColor != 'w'):
					#print ("== seeing nextC in 'Xx' or (nextC == 'Dd' and self.currentColor != 'w')")
					c = x0 + self.waveTransitionTime
					#self.canvas.create_polygon(x1, yBasis - self.waveHeight, 
					#	c + self.waveTransitionTime/2, yBasis - self.waveHeight, c + self.waveTransitionTime/2, yBasis)
					pointList = [QtCore.QPointF(x1, yBasis - self.waveHeight),
							QtCore.QPointF(c + self.waveTransitionTime/2, yBasis - self.waveHeight),
							QtCore.QPointF(c + self.waveTransitionTime/2, yBasis)]
						
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))

				self.scene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, x1, yBasis - self.waveHeight))
				x0 = x1
				x1 += self.waveTransitionTime
				self.scene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, 
					x1, yBasis - self.waveHeight))
				self.scene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, 
					x1, yBasis))
				
			waveCount += 2
			self.timeDelta = 0

		elif thisC == 'p': #lower case
			#print ("Doing small p -- at the beginning seeing timeDelta =", self.timeDelta)
			x0 = xBasis
			x1 = x0 + self.waveHalfDuration + self.waveTransitionTime/2 + self.timeDelta
			if waveCount == 0: #first clock
				x0 += self.waveTransitionTime/2 #tweak to match the start time of non-clock signals
			y0 = yBasis
			y1 = yBasis
			self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))

			#draw the grid
			if self.evenGridsEnabledGlobal == True:
				self.scene.addLine(QtCore.QLineF(x1 - self.timeDelta, 
					yBasis - self.waveHeight - self.signalWaveYSpacing, 
					x1 - self.timeDelta, 
					yBasis), self.gridPen)

			x0 = x1 
			y0 = yBasis
			y1 = yBasis - self.waveHeight
			self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))

			x1 += self.waveHalfPeriod - self.timeDelta
			y0 = yBasis - self.waveHeight
			y1 = yBasis - self.waveHeight
			self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))
			
			#draw the falling edge grid
			if self.oddGridsEnabledGlobal == True:
				self.scene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight - self.signalWaveYSpacing, 
					x1,	yBasis), self.gridPen)

			if nextC in "pP":
				#print ("CASE P of P is seen")
				x0 = x1
				y0 = yBasis - self.waveHeight
				y1 = yBasis
				self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1)) 

				x1 += self.waveTransitionTime/2 
				y0 = yBasis
				y1 = yBasis
				self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))
			elif nextC == 'z':
				x0 = x1
				x1 += self.waveTransitionTime
				y0 = yBasis - self.waveHeight
				y1 = yBasis - self.waveHeight/2
				self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1)) 
			elif nextC in 'hfF':
				x0 = x1
				x1 += self.waveTransitionTime
				self.scene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, 
					x1, yBasis - self.waveHeight))
			elif nextC in 'lrR':
				x0 = x1
				x1 += self.waveTransitionTime
				self.scene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, 
					x1, yBasis))
			elif nextC in 'DdXx':
				x0 = x1
				x1 += self.waveTransitionTime
				if nextC in 'Dd' and self.currentColor != 'w':
					color = colorMap[self.currentColor]
				else:
					color = "light grey"

				if nextC in 'Xx' or (nextC in 'Dd' and self.currentColor != 'w'):
					c = x0# + self.waveTransitionTime
					pointList = [QtCore.QPointF(x0, yBasis - self.waveHeight),
							QtCore.QPointF(x0 + self.waveTransitionTime, yBasis - self.waveHeight),
							QtCore.QPointF(x0 + self.waveTransitionTime, yBasis)]
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
					#self.canvas.create_polygon(x0, yBasis - self.waveHeight, 
					#	c + self.waveTransitionTime, yBasis - self.waveHeight, c + self.waveTransitionTime, yBasis)

				self.scene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, 
					x1, yBasis - self.waveHeight))
				self.scene.addLine(QtCore.QLineF(x0, yBasis - self.waveHeight, 
					x1, yBasis))

			waveCount += 2
			self.timeDelta = 0

	def tdDrawFall(self, waveCount=-1, thisC=None, nextC=None, basis=(0, 0)):
		xBasis, yBasis = basis
		x0 = xBasis + self.waveTransitionTime/2
		x1 = x0 + self.waveHalfDuration - self.timeDelta
		y0 = yBasis - self.waveHeight
		y1 = yBasis - self.waveHeight
		self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))
		color = "light grey"

		if nextC in "dxDXpP":
			if nextC in 'Dd' and self.currentColor != 'w':
				if self.currentColor in colorMap.keys():
					color = colorMap[self.currentColor]

			if nextC in 'xX' or (nextC in 'dD' and self.currentColor != 'w'):
				c = x1 + self.waveTransitionTime + self.timeDelta
				pointList = [QtCore.QPointF(x1, yBasis - self.waveHeight), 
							QtCore.QPointF(c, yBasis - self.waveHeight), 
							QtCore.QPointF(c, yBasis), 
							QtCore.QPointF(c - self.timeDelta, yBasis)]
				self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(), QtGui.QBrush(QtGui.QColor(color)))
				#self.canvas.create_polygon(x1, yBasis - self.waveHeight, c, yBasis - self.waveHeight, c, yBasis, 
				#	c - self.timeDelta, yBasis)

			if nextC in "pP":
				self.scene.addLine(QtCore.QLineF(x1, y1, x1 + self.waveTransitionTime/2, yBasis))
				self.scene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime/2, yBasis, x1 + self.timeDelta + self.waveTransitionTime, yBasis))
			else:
				self.scene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis))

			if nextC in 'dxDX':
				self.scene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime + self.timeDelta, y0))
		elif nextC in 'hf':
			self.scene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2))
			self.scene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
			self.scene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime, yBasis - self.waveHeight, x1 + self.waveTransitionTime + self.timeDelta, yBasis - self.waveHeight))
		elif nextC == 'z':
			self.scene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis - self.waveHeight/2))
			self.scene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime, yBasis - self.waveHeight/2, 
				x1 + self.waveTransitionTime + self.timeDelta, yBasis - self.waveHeight/2))

		#draw the grid
		if (self.evenGridsEnabledGlobal == True and (waveCount % 2) == 0) or (self.oddGridsEnabledGlobal == True and (waveCount % 2) == 1):
			self.scene.addLine(QtCore.QLineF(x1 + self.timeDelta, yBasis - self.waveHeight - self.signalWaveYSpacing, 
				x1 + self.timeDelta, yBasis), self.gridPen)

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
				self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				self.scene.addLine(QtCore.QLineF(x0, y0, x0 + self.waveTransitionTime, y0))
				self.scene.addLine(QtCore.QLineF(x0 + self.waveTransitionTime, y0, x1 + self.waveTransitionTime, y1))
				if nextC not in 'Fl': #anirb - 27-Dec-2022
					self.scene.addLine(QtCore.QLineF(x0 + self.waveTransitionTime, y1, x1 + self.waveTransitionTime, y1))

			self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))
			self.scene.addLine(QtCore.QLineF(x1, y1, x1 + self.timeDelta, y1))
		elif nextC == 'F':
			self.scene.addLine(QtCore.QLineF(x0, y0, x1 + self.timeDelta, y0))

	def tdDrawRise (self, waveCount=-1, thisC=None, nextC=None, basis=(0, 0)):
		#print ("Doing r -- at the beginning seeing timeDelta =", self.timeDelta)
		#print ("Doing 'r' -- at the beginning -- invertedClockHeight = ", invertedClockHeight)
		xBasis, yBasis = basis
		x0 = xBasis + self.waveTransitionTime/2
		x1 = x0 + self.waveHalfDuration - self.timeDelta
		y0 = yBasis
		y1 = yBasis
		self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))
		color = "light grey"

		if nextC in "dxDX":
			if nextC in 'xX' or (nextC in 'Dd' and self.currentColor != 'w'):
				if nextC in 'Dd' and self.currentColor != 'w':
					color = colorMap[self.currentColor]

				c = x1 + self.waveTransitionTime + self.timeDelta
				pointList = [QtCore.QPointF(x1, yBasis), 
							QtCore.QPointF(c, yBasis), 
							QtCore.QPointF(c, yBasis - self.waveHeight), 
							QtCore.QPointF(c - self.timeDelta, yBasis - self.waveHeight)]
				self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
			self.scene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime + self.timeDelta, yBasis))
		#elif nextC == 'l' or nextC == 'r':
		elif nextC in 'lr':
			self.scene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2))
			self.scene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2, x1 + self.waveTransitionTime, yBasis))
			self.scene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime, yBasis, x1 + self.waveTransitionTime + self.timeDelta, yBasis))
		elif nextC == 'z':
			self.scene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis - self.waveHeight/2))
			self.scene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime, yBasis - self.waveHeight/2, 
				x1 + self.waveTransitionTime + self.timeDelta, yBasis - self.waveHeight/2))

		#draw the grid
		if (self.evenGridsEnabledGlobal == True and (waveCount % 2) == 0) or (self.oddGridsEnabledGlobal == True and (waveCount % 2) == 1):
			self.scene.addLine(QtCore.QLineF(x1 + self.timeDelta, yBasis - self.waveHeight - self.signalWaveYSpacing, 
				x1 + self.timeDelta, yBasis), self.gridPen)

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
				self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				self.scene.addLine(QtCore.QLineF(x0, y0, x0 + self.waveTransitionTime, y0))
				self.scene.addLine(QtCore.QLineF(x0 + self.waveTransitionTime, y0, x1 + self.waveTransitionTime, y1))
				if nextC not in 'Rh': #anirb - 27-Dec-2022
					self.scene.addLine(QtCore.QLineF(x0 + self.waveTransitionTime, y1, x1 + self.waveTransitionTime, y1))
			self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))
			if self.timeDelta > 0:
				self.scene.addLine(QtCore.QLineF(x1, y1, x1 + self.timeDelta, y1))
		elif nextC == 'R':
			self.scene.addLine(QtCore.QLineF(x0, y0, x1 + self.timeDelta, y0))

	def tdDrawHigh (self, waveCount=-1, nextC=None, basis=(0, 0)):
		xBasis, yBasis = basis
		x0 = xBasis + self.waveTransitionTime/2
		if nextC in "zldxDXrR":
			x1 = x0 + self.waveHalfDuration
		else:
			x1 = x0 + self.waveHalfPeriod

		y0 = yBasis - self.waveHeight
		y1 = y0
		self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))
		if nextC in "ldxDXrR":
			#print ("== seeing h and nextC in ldxDXrRpP")
			if nextC in 'Dd' and self.currentColor != 'w':
				color = colorMap[self.currentColor]
			else:
				color = "light grey"

			if nextC in 'xX' or nextC == 'X' or (nextC in 'Dd' and self.currentColor != 'w'):
				c = x1 + self.waveTransitionTime
				pointList = [QtCore.QPointF(x1, yBasis - self.waveHeight), 
							QtCore.QPointF(c, yBasis - self.waveHeight), 
							QtCore.QPointF(c, yBasis)]
				self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(), QtGui.QBrush(QtGui.QColor(color)))
			if nextC in 'dxDX':
				self.scene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, y0))
			self.scene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis))
		elif nextC == 'z':
			self.scene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis - self.waveHeight/2))
		#draw the grid
		if (self.evenGridsEnabledGlobal == True and (waveCount % 2) == 0) or (self.oddGridsEnabledGlobal == True and (waveCount % 2) == 1):
			self.scene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration, yBasis - self.waveHeight - self.signalWaveYSpacing, 
				x0 + self.waveHalfDuration, yBasis), self.gridPen)

	def tdDrawLow (self, waveCount=-1, nextC=None, basis=(0, 0)):
		xBasis, yBasis = basis
		x0 = xBasis + self.waveTransitionTime/2
		if nextC in "zhdxDXfFpP":
			x1 = x0 + self.waveHalfDuration
		else:
			x1 = x0 + self.waveHalfPeriod
		y0 = yBasis
		y1 = y0
		self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))

		if nextC in "hdxDXfF":
			if nextC in 'Dd' and self.currentColor != 'w':
				color = colorMap[self.currentColor]
			else:
				color = "light grey"

			if nextC in 'xX' or (nextC in 'Dd' and self.currentColor != 'w'):
				#print ("== seeing l and nextC in xdDX")
				c = x1 + self.waveTransitionTime
				pointList = [QtCore.QPointF(x1, yBasis), 
							QtCore.QPointF(c, yBasis), 
							QtCore.QPointF(c, yBasis - self.waveHeight)]
				self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(), QtGui.QBrush(QtGui.QColor(color)))

			if nextC in 'dxDX':
				self.scene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis))
			self.scene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
		elif nextC == 'z':
			self.scene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis - self.waveHeight/2))

		#draw the grid
		if (self.evenGridsEnabledGlobal == True and (waveCount % 2) == 0) or (self.oddGridsEnabledGlobal == True and (waveCount % 2) == 1):
			self.scene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration, yBasis - self.waveHeight - self.signalWaveYSpacing, 
				x0 + self.waveHalfDuration, yBasis), self.gridPen)

	def tdDrawDatadx(self, waveCount=-1, lastC=None, thisC=None, nextC=None, basis=(0, 0)):
		#print ("tdDrawDatadx: thisC=", thisC, " nextC=", nextC)
		xBasis, yBasis = basis
		color = "light grey"
		if self.currentColor in colorMap.keys():
			color = colorMap[self.currentColor]
		x0 = xBasis + self.waveTransitionTime/2

		#draw the grid
		if (self.evenGridsEnabledGlobal == True and (waveCount % 2) == 0) or (self.oddGridsEnabledGlobal == True and (waveCount % 2) == 1):
			self.scene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration, yBasis - self.waveHeight - self.signalWaveYSpacing, 
				x0 + self.waveHalfDuration, yBasis), self.gridPen)

		if nextC in "zlhrRfFPp" or\
				(thisC == 'd' and (nextC in 'xX')) or\
				(thisC == 'x' and (nextC in 'dDX')):
			x1 = x0 + self.waveHalfDuration
		else:
			x1 = x0 + self.waveHalfPeriod

		if thisC == 'x' or (thisC == 'd' and self.currentColor != 'w'):
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
			h = f

			pointList = [QtCore.QPointF(a, b),
						QtCore.QPointF(c, d),
						QtCore.QPointF(e, f),
						QtCore.QPointF(g, h)]
			if (thisC == 'd' and self.currentColor != 'w'):
				self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				#self.canvas.create_polygon(a, b, c, d, e, f, g, h)
				if waveCount != 0 and lastC in 'DXz':
					# to handle cases like: D$rD - when the first D is seen, the color is not yet known, so the
					#left triangle for the next D cannot be filled - it must be deferred when the next D is being
					#processed as thisC
					if lastC == 'z':
						pointList = [QtCore.QPointF(xBasis + self.waveTransitionTime/2, yBasis),
								QtCore.QPointF(xBasis - self.waveTransitionTime/2, yBasis - self.waveHeight/2),
								QtCore.QPointF(xBasis + self.waveTransitionTime/2, yBasis - self.waveHeight)]
					else:
						pointList = [QtCore.QPointF(xBasis + self.waveTransitionTime/2, yBasis),
							QtCore.QPointF(xBasis, yBasis - self.waveHeight/2),
							QtCore.QPointF(xBasis + self.waveTransitionTime/2, yBasis - self.waveHeight)]
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
					if lastC == 'z':
						#redo the angled lines only if last was D or X or z
						self.scene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2, yBasis, xBasis - self.waveTransitionTime/2, yBasis - self.waveHeight/2))
						self.scene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2, yBasis - self.waveHeight, xBasis - self.waveTransitionTime/2, yBasis - self.waveHeight/2))
					else:
						self.scene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2, yBasis, xBasis, yBasis - self.waveHeight/2))
						self.scene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2, yBasis - self.waveHeight, xBasis, yBasis - self.waveHeight/2))
				
			else:
				self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
				#self.canvas.create_polygon(a, b, c, d, e, f, g, h)

			if nextC == 'z':
				c = x1 + self.waveTransitionTime
				d = yBasis - self.waveHeight/2
				pointList = [QtCore.QPointF(x1, yBasis),
							QtCore.QPointF(c, d),
							QtCore.QPointF(x1, yBasis - self.waveHeight)]
				if (thisC == 'd' and self.currentColor != 'w'):
				#	self.canvas.create_polygon(x1, yBasis, c, d, x1, yBasis - self.waveHeight)
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				else:
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
				#	self.canvas.create_polygon(x1, yBasis, c, d, x1, yBasis - self.waveHeight)
			elif nextC in 'lrR' or nextC == 'p' or nextC == 'P':
				c = x1 + self.waveTransitionTime
				pointList = [QtCore.QPointF(x1, yBasis),
							QtCore.QPointF(c, yBasis),
							QtCore.QPointF(x1, yBasis - self.waveHeight)]
				if (thisC == 'd' and self.currentColor != 'w'):
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
					#self.canvas.create_polygon(x1, yBasis, c, yBasis, x1, yBasis - self.waveHeight, 
					#	tags=('wave'+line), fill=colorMap[self.currentColor])
				else:
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
					#self.canvas.create_polygon(x1, yBasis, c, yBasis, x1, yBasis - self.waveHeight, 
					#	tags=('wave'+line), fill="light grey")
			elif nextC in 'hfF':
				c = x1 + self.waveTransitionTime
				pointList = [QtCore.QPointF(x1, yBasis),
							QtCore.QPointF(x1, yBasis - self.waveHeight),
							QtCore.QPointF(c, yBasis - self.waveHeight)]
				if (thisC == 'd' and self.currentColor != 'w'):
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
					#self.canvas.create_polygon(x1, yBasis, c, yBasis - self.waveHeight, x1, yBasis - self.waveHeight, 
					#	tags=('wave'+line), fill=colorMap[self.currentColor])
				else:
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
					#self.canvas.create_polygon(x1, yBasis, c, yBasis - self.waveHeight, x1, yBasis - self.waveHeight, 
					#	tags=('wave'+line), fill="light grey")
			elif nextC in 'dXD' or (thisC == 'd' and nextC == 'x'): 
				a = x1 + self.waveTransitionTime/2
				c = x1 + self.waveTransitionTime
				if (thisC == 'd' and self.currentColor != 'w'):
					pointList = [QtCore.QPointF(x1, yBasis),
								QtCore.QPointF(x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2),
								QtCore.QPointF(x1, yBasis - self.waveHeight)]
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
					#self.canvas.create_polygon(x1, yBasis, x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2, 
					#			x1, yBasis - self.waveHeight)
					if nextC in 'xX':
						pointList = [QtCore.QPointF(x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2),
									QtCore.QPointF(x1 + self.waveTransitionTime, yBasis),
									QtCore.QPointF(x1 + self.waveTransitionTime, yBasis - self.waveHeight)]
						self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
						#self.canvas.create_polygon(x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2, 
						#							x1 + self.waveTransitionTime, yBasis, 
						#							x1 + self.waveTransitionTime, yBasis - self.waveHeight)
						self.scene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
						self.scene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight, x1 + self.waveTransitionTime, yBasis))
				else:
					#print ("if B --------")
					if nextC in 'dD':
						#print ("if C --------")
						pointList = [QtCore.QPointF(x1, yBasis),
								QtCore.QPointF(x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2),
								QtCore.QPointF(x1, yBasis - self.waveHeight)]
						self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
						#self.canvas.create_polygon(x1, yBasis, x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2, 
						#x1, yBasis - self.waveHeight)
					else: #'X'
						#print ("if D --------")
						pointList = [QtCore.QPointF(x1, yBasis),
								QtCore.QPointF(x1 + self.waveTransitionTime, yBasis),
								QtCore.QPointF(x1 + self.waveTransitionTime, yBasis - self.waveHeight),
								QtCore.QPointF(x1, yBasis - self.waveHeight)]
						self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
						#self.canvas.create_polygon(x1, yBasis, x1 + self.waveTransitionTime, yBasis, x1 + self.waveTransitionTime, yBasis - self.waveHeight, x1, yBasis - self.waveHeight)
						
				if thisC == 'x':
					if nextC in 'dD' and self.currentColor != 'w':
						pointList = [QtCore.QPointF(x1 + self.waveTransitionTime, yBasis),
								QtCore.QPointF(a, yBasis - self.waveHeight/2),
								QtCore.QPointF(x1 + self.waveTransitionTime, yBasis - self.waveHeight)]
						self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
						#self.canvas.create_polygon(x1 + self.waveTransitionTime, yBasis, a, yBasis - self.waveHeight/2, x1 + self.waveTransitionTime, yBasis - self.waveHeight)
						self.scene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
						self.scene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight, x1 + self.waveTransitionTime, yBasis))
					elif nextC in 'dD':
						self.scene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
						self.scene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight, x1 + self.waveTransitionTime, yBasis))
					elif nextC in 'X':
						pointList = [QtCore.QPointF(x1 + self.waveTransitionTime, yBasis),
								QtCore.QPointF(a, yBasis - self.waveHeight/2),
								QtCore.QPointF(x1 + self.waveTransitionTime, yBasis - self.waveHeight)]
						self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
						#self.canvas.create_polygon(x1 + self.waveTransitionTime, yBasis, a, yBasis - self.waveHeight/2, x1 + self.waveTransitionTime, yBasis - self.waveHeight)
						self.scene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
						self.scene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis))
		elif thisC == 'd'and nextC in 'xX':
			#print ("if B --------")
			pointList = [QtCore.QPointF(x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2),
					QtCore.QPointF(x1 + self.waveTransitionTime, yBasis),
					QtCore.QPointF(x1 + self.waveTransitionTime, yBasis - self.waveHeight)]
			self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
			#self.canvas.create_polygon(x1 + self.waveTransitionTime/2, yBasis - self.waveHeight/2, 
			#				x1 + self.waveTransitionTime, yBasis, 
			#				x1 + self.waveTransitionTime, yBasis - self.waveHeight)
			self.scene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
			self.scene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight, x1 + self.waveTransitionTime, yBasis))

		y0 = yBasis
		y1 = y0
		self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))
		y0 = yBasis - self.waveHeight
		y1 = y0
		self.scene.addLine(QtCore.QLineF(x0, y0, x1, y1))

		if nextC in 'pP':
			#	self.scene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
			#	self.scene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
			#else:
				#clock drawn next is not inverted
			self.scene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis))
			self.scene.addLine(QtCore.QLineF(x1, yBasis - self.waveHeight, x1 + self.waveTransitionTime, yBasis))

		elif nextC in 'lrR':
			self.scene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis))
			self.scene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis))
		elif nextC in 'hfF':
			self.scene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
			self.scene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis - self.waveHeight))
		elif nextC == 'z':
			self.scene.addLine(QtCore.QLineF(x1, y0, x1 + self.waveTransitionTime, yBasis - self.waveHeight/2))
			self.scene.addLine(QtCore.QLineF(x1, yBasis, x1 + self.waveTransitionTime, yBasis - self.waveHeight/2))

		#draw the grid
		#if (self.evenGridsEnabledGlobal == True and (waveCount % 2) == 0) or (self.oddGridsEnabledGlobal == True and (waveCount % 2) == 1):
		#	self.scene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration, yBasis - self.waveHeight - self.signalWaveYSpacing, 
		#		x0 + self.waveHalfDuration,	yBasis), self.gridPen)

	def tdDrawDataDX(self, waveCount=-1, lastC=None, thisC=None, nextC=None, basis=(0, 0)):
		#print ("tdDrawDataDX: thisC=", thisC, " ord nextC=", ord(nextC), nextC)
		xBasis, yBasis = basis
		x0 = xBasis + self.waveTransitionTime/2
		x1 = x0 + self.waveHalfDuration
		y0 = yBasis
		y1 = y0

		a = x0
		b = y0
		c = x1
		d = y1

		#draw the grid
		if (self.evenGridsEnabledGlobal == True and (waveCount % 2) == 0) or (self.oddGridsEnabledGlobal == True and (waveCount % 2) == 1):
			self.scene.addLine(QtCore.QLineF(x1, y0 - self.waveHeight - self.signalWaveYSpacing, x1, y0), self.gridPen)

		x0 = x1
		x1 += self.waveTransitionTime
		e = c + self.waveTransitionTime/2
		f = y1 - self.waveHeight/2
		y1 -= self.waveHeight
		g = c
		h = y1 
		i = a
		j = h
		color = "light grey"
		if self.currentColor in colorMap.keys():
			color = colorMap[self.currentColor]

		#print ("tdDrawDataDX: 0. thisC == 'D' and self.currentColor = ", self.currentColor)
		if thisC == 'X' or (thisC == 'D' and self.currentColor != 'w'):
			if (thisC == 'D' and self.currentColor != 'w'):
				#print ("tdDrawDataDX: Z. thisC == 'D' and self.currentColor != 'w'")
				pointList = [QtCore.QPointF(a, b),
							QtCore.QPointF(c - self.timeDelta, d),
							QtCore.QPointF(e - self.timeDelta, y1 + self.waveHeight/2),
							QtCore.QPointF(g - self.timeDelta, h),
							QtCore.QPointF(i, j)]
				self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				if waveCount != 0 and lastC in 'DXz':
					#FIX PR0
					# to handle cases like: D$rD - when the first D is seen, the color is not yet known, so the
					#left triangle for the next D cannot be filled - it must be deferred when the next D is being
					#processed as thisC
					if lastC == 'z':
						pointList = [QtCore.QPointF(xBasis + self.waveTransitionTime/2, yBasis),
								QtCore.QPointF(xBasis - self.waveTransitionTime/2, yBasis - self.waveHeight/2),
								QtCore.QPointF(xBasis + self.waveTransitionTime/2, yBasis - self.waveHeight)]
					else:
						pointList = [QtCore.QPointF(xBasis + self.waveTransitionTime/2, yBasis),
								QtCore.QPointF(xBasis, yBasis - self.waveHeight/2),
								QtCore.QPointF(xBasis + self.waveTransitionTime/2, yBasis - self.waveHeight)]
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
					if lastC == 'z':
						#redo the angled lines only if last was D or X or z
						self.scene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2, yBasis, xBasis - self.waveTransitionTime/2, yBasis - self.waveHeight/2))
						self.scene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2, yBasis - self.waveHeight, xBasis - self.waveTransitionTime/2, yBasis - self.waveHeight/2))
					else:
						self.scene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2, yBasis, xBasis, yBasis - self.waveHeight/2))
						self.scene.addLine(QtCore.QLineF(xBasis + self.waveTransitionTime/2, yBasis - self.waveHeight, xBasis, yBasis - self.waveHeight/2))

			else:
				pointList = [QtCore.QPointF(a, b),
							QtCore.QPointF(c - self.timeDelta, d),
							QtCore.QPointF(e - self.timeDelta, y1 + self.waveHeight/2),
							QtCore.QPointF(g - self.timeDelta, h),
							QtCore.QPointF(i, j)]
				self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))

			if nextC == 'z':
				a = x1 - self.waveTransitionTime
				c = x1
				d = yBasis - self.waveHeight/2
				pointList = [QtCore.QPointF(x0, y0),
						QtCore.QPointF(x0 + self.waveTransitionTime, y0),
						QtCore.QPointF(x1 + self.waveTransitionTime, y1),
						QtCore.QPointF(x0 + self.waveTransitionTime, y1)]
				pointList = [QtCore.QPointF(x1 - self.waveTransitionTime, yBasis),
						QtCore.QPointF(x1, d),
						QtCore.QPointF(x1 - self.waveTransitionTime, yBasis - self.waveHeight)]
				if (thisC == 'D' and self.currentColor != 'w'):
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
					#self.canvas.create_polygon(a - self.timeDelta, yBasis, c - self.timeDelta, d, a - self.timeDelta, yBasis - self.waveHeight, 
					#	tags=('wave'+line), fill=colorMap[self.currentColor])
				else:
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
					#self.canvas.create_polygon(a - self.timeDelta, yBasis, c - self.timeDelta, d, a - self.timeDelta, yBasis - self.waveHeight, 
					#	tags=('wave'+line), fill="light grey")
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
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
				elif self.currentColor != 'w':
					pointList = [QtCore.QPointF(a, yBasis),
							QtCore.QPointF(a, yBasis - self.waveHeight),
							QtCore.QPointF(a - self.timeDelta, yBasis - self.waveHeight),
							QtCore.QPointF(e - self.timeDelta, yBasis - self.waveHeight/2),
							QtCore.QPointF(a - self.timeDelta, yBasis)]
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
			elif nextC in 'hfF':
				#print ("thisC == 'X' or (thisC == 'D' and self.currentColor != 'w') === and === nextC in 'hfF'")
				a = x1 - self.waveTransitionTime
				d = yBasis - self.waveHeight
				pointList = [QtCore.QPointF(a, yBasis),
						QtCore.QPointF(a - self.timeDelta, yBasis),
						QtCore.QPointF(a - self.timeDelta, d),
						QtCore.QPointF(x1 - self.timeDelta, d)]
				if thisC == 'D' and self.currentColor != 'w':
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				else:
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
			elif nextC in 'lrR' or nextC == 'p' or nextC == 'P':
				a = x1 - self.waveTransitionTime
				d = yBasis
				pointList = [QtCore.QPointF(a - self.timeDelta, yBasis - self.waveHeight),
						QtCore.QPointF(a - self.timeDelta, d),
						QtCore.QPointF(x1 - self.timeDelta, d)]
				if thisC == 'D' and self.currentColor != 'w':
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
				else:
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
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
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))
				#self.canvas.create_polygon(a - self.timeDelta, yBasis - self.waveHeight/2, c - self.timeDelta, yBasis, 
				#							c, yBasis, c, yBasis - self.waveHeight, c - self.timeDelta, yBasis - self.waveHeight)
				elif self.currentColor != 'w':
					self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("color")))


		if nextC == 'z':
			gx1 = xBasis + self.waveTransitionTime/2 + self.waveHalfDuration
			#draw lines last
			self.scene.addLine(QtCore.QLineF(gx1 - self.timeDelta, yBasis - self.waveHeight, 
						gx1 + self.waveTransitionTime - self.timeDelta, yBasis - self.waveHeight/2))
			self.scene.addLine(QtCore.QLineF(gx1 - self.timeDelta, yBasis, 
						gx1 + self.waveTransitionTime - self.timeDelta, yBasis - self.waveHeight/2))
			self.scene.addLine(QtCore.QLineF(gx1 + self.waveTransitionTime - self.timeDelta, yBasis - self.waveHeight/2, 
				x1, yBasis - self.waveHeight/2))

		if nextC not in 'zlrRpP':
			#angled line to top
			self.scene.addLine(QtCore.QLineF(x0 - self.timeDelta, y0, x1 - self.timeDelta, y1))
			if nextC in 'hfF':
				self.scene.addLine(QtCore.QLineF(x0 - self.timeDelta, y1, x1 - self.timeDelta, y1))
		elif nextC in 'lrR':
			self.scene.addLine(QtCore.QLineF(x0 - self.timeDelta, y0, x1 - self.timeDelta, y0))
		elif nextC in 'pP':
			self.scene.addLine(QtCore.QLineF(x0 - self.timeDelta, y1, x0 + self.waveTransitionTime - self.timeDelta, y0))
			self.scene.addLine(QtCore.QLineF(x0 - self.timeDelta, y0, x1 - self.timeDelta, y0))

		x0 = xBasis + self.waveTransitionTime/2
		x1 = x0 + self.waveHalfDuration
		y0 = yBasis - self.waveHeight
		#horizontal line at top
		self.scene.addLine(QtCore.QLineF(x0, y0, x1 - self.timeDelta, y0)) 
		x0 = x1
		x1 += self.waveTransitionTime
		y0 = yBasis - self.waveHeight
		y1 = yBasis
		if nextC not in 'zhfFpP':
			#angled line to bottom
			self.scene.addLine(QtCore.QLineF(x0 - self.timeDelta, y0, x1 - self.timeDelta, y1))

			#additional bottom lines needed to the right of crossover when timeDelta is enabled
			self.scene.addLine(QtCore.QLineF(x1 - self.timeDelta, y1, x1, y1)) 

		if nextC not in 'lrRzpP':
			#additional top lines needed to the right of crossover when timeDelta is enabled
			self.scene.addLine(QtCore.QLineF(x1 - self.timeDelta, y0, x1, y0))

		if nextC in 'hfF':
			self.scene.addLine(QtCore.QLineF(x0, y0, x1, y0))

		x0 = xBasis + self.waveTransitionTime/2
		x1 = x0 + self.waveHalfDuration
		y0 = yBasis
		y1 = y0

		#horizontal line at bottom
		self.scene.addLine(QtCore.QLineF(x0, y0, x1 - self.timeDelta, y0))

	def tdDrawSpace(self, waveCount, cmd, basis=(0, 0)):
		xBasis, yBasis = basis
		#draw the grid
		if cmd.strip().find('<') == -1 and cmd.strip().find('>') == -1 and cmd.strip().find('-') == -1: #no arrow
			#print ("-- seeing 's', this line has arrows ...")
			x0 = xBasis + self.waveTransitionTime/2
			if (self.evenGridsEnabledGlobal == True and (waveCount % 2) == 0) or (self.oddGridsEnabledGlobal == True and (waveCount % 2) == 1):
				self.scene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration,
					yBasis - self.waveHeight - self.signalWaveYSpacing, 
					x0 + self.waveHalfDuration,
					yBasis), self.gridPen)

	def tdDrawTri(self, waveCount, nextC=None, basis=(0, 0)):
		xBasis, yBasis = basis
		x0 = xBasis + self.waveTransitionTime/2
		if nextC in "dDXxlhrRfFpP":
			x1 = x0 + self.waveHalfDuration
		else:
			x1 = x0 + self.waveHalfPeriod

		y0 = yBasis - self.waveHeight/2
		y1 = y0

		#draw the grid
		if (self.evenGridsEnabledGlobal == True and (waveCount % 2) == 0) or (self.oddGridsEnabledGlobal == True and (waveCount % 2) == 1):
			self.scene.addLine(QtCore.QLineF(x0 + self.waveHalfDuration, yBasis - self.waveHeight - self.signalWaveYSpacing, 
				x0 + self.waveHalfDuration, yBasis), self.gridPen)

		if nextC in 'pP':
			c = x1 + self.waveTransitionTime/2
		else:
			c = x1 + self.waveTransitionTime

		if nextC in 'xX' or (nextC in 'dD' and self.currentColor != 'w'):
			pointList = [QtCore.QPointF(x1 - self.timeDelta, y0),
					QtCore.QPointF(c - self.timeDelta, yBasis),
					QtCore.QPointF(c, yBasis),
					QtCore.QPointF(c, yBasis - self.waveHeight),
					QtCore.QPointF(c - self.timeDelta, yBasis - self.waveHeight)]
			if nextC in 'dD' and self.currentColor != 'w':
				color = "light grey"
				if self.currentColor in colorMap.keys():
					color = colorMap[self.currentColor]
				self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))
			else:
				self.scene.addPolygon(QtGui.QPolygonF(pointList), QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor("light grey")))

		if nextC in 'dDXx':
			self.scene.addLine(QtCore.QLineF(x1 - self.timeDelta, y0, 
				x1 + self.waveTransitionTime - self.timeDelta, yBasis - self.waveHeight), self.triPen)
			self.scene.addLine(QtCore.QLineF(x1 - self.timeDelta, y0, 
				x1 + self.waveTransitionTime - self.timeDelta, yBasis), self.triPen)
			self.scene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime - self.timeDelta, yBasis - self.waveHeight, 
				x1 + self.waveTransitionTime, yBasis - self.waveHeight), self.triPen)
			self.scene.addLine(QtCore.QLineF(x1 + self.waveTransitionTime - self.timeDelta, yBasis, 
				x1 + self.waveTransitionTime, yBasis), self.triPen)
		elif nextC in 'hfF' or nextC in 'pP':
			self.scene.addLine(QtCore.QLineF(x1 - self.timeDelta, y0, c, yBasis - self.waveHeight), self.triPen)
		elif nextC in 'lrR' or nextC in 'pP':
			self.scene.addLine(QtCore.QLineF(x1 - self.timeDelta, y0, c, yBasis), self.triPen)

		self.scene.addLine(QtCore.QLineF(x0, y0, x1 - self.timeDelta, y1), self.triPen)
	
	def tdDrawGap(self, waveCount, lastC=None, nextC=None, basis=(0, 0)):
		xBasis, yBasis = basis
		x0 = xBasis - self.waveHalfDuration - 5
		color = self.gapBrushColor
		xstep = -5
		xstep2 = 7

		pointList = [QtCore.QPointF(x0 + self.waveHalfDuration/2 + xstep, yBasis - self.waveHeight - self.signalWaveYSpacing/4),
			QtCore.QPointF(x0 + self.waveHalfDuration/2 + 7 + xstep, yBasis - 3*self.waveHeight/4),
			QtCore.QPointF(x0 + self.waveHalfDuration/2 - 7 + xstep, yBasis - self.waveHeight/4),
			QtCore.QPointF(x0 + self.waveHalfDuration/2 + xstep, yBasis + self.signalWaveYSpacing/4),

			QtCore.QPointF(x0 + self.waveHalfDuration/2 + xstep2, yBasis + self.signalWaveYSpacing/4),
			QtCore.QPointF(x0 + self.waveHalfDuration/2 - 7 + xstep2, yBasis - self.waveHeight/4),
			QtCore.QPointF(x0 + self.waveHalfDuration/2 + 7 + xstep2, yBasis - 3*self.waveHeight/4),
			QtCore.QPointF(x0 + self.waveHalfDuration/2 + xstep2, yBasis - self.waveHeight - self.signalWaveYSpacing/4)]

		self.scene.addPolygon(QtGui.QPolygonF(pointList), 
			QtGui.QPen(Qt.transparent), QtGui.QBrush(QtGui.QColor(color)))

		path = QPainterPath()
		path.moveTo(QtCore.QPointF(x0 + self.waveHalfDuration/2 + xstep, yBasis - self.waveHeight - self.signalWaveYSpacing/4))
		path.cubicTo(
					QtCore.QPointF(x0 + self.waveHalfDuration/2 + 25 + xstep, yBasis - 3*self.waveHeight/4),
					QtCore.QPointF(x0 + self.waveHalfDuration/2 - 23 + xstep, yBasis - self.waveHeight/4),
					QtCore.QPointF(x0 + self.waveHalfDuration/2 + xstep, yBasis + self.signalWaveYSpacing/4))
		self.scene.addPath(path, self.gapPen)
		path.moveTo(QtCore.QPointF(x0 + self.waveHalfDuration/2 + xstep2, yBasis - self.waveHeight - self.signalWaveYSpacing/4))
		path.cubicTo(
					QtCore.QPointF(x0 + self.waveHalfDuration/2 + 35 + xstep, yBasis - 3*self.waveHeight/4),
					QtCore.QPointF(x0 + self.waveHalfDuration/2 - 15 + xstep, yBasis - self.waveHeight/4),
					QtCore.QPointF(x0 + self.waveHalfDuration/2 + xstep2, yBasis + self.signalWaveYSpacing/4))
		self.scene.addPath(path, self.gapPen)
		self.scene.addPath(path, self.gapPen)

def main():
	app = QApplication(sys.argv)
	form = TimingDiagrammer()
	form.show()
	app.exec_()

if __name__ == '__main__':
	main()
