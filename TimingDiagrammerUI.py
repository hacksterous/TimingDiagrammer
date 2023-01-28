# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TimingDiagrammerUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TimingDiagrammer(object):
	def setupUi(self, TimingDiagrammer):
		TimingDiagrammer.setObjectName("TimingDiagrammer")
		TimingDiagrammer.setEnabled(True)
		TimingDiagrammer.resize(700, 660)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(1)
		sizePolicy.setVerticalStretch(1)
		sizePolicy.setHeightForWidth(TimingDiagrammer.sizePolicy().hasHeightForWidth())
		TimingDiagrammer.setSizePolicy(sizePolicy)
		TimingDiagrammer.setMinimumSize(QtCore.QSize(600, 660))
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap("td.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		TimingDiagrammer.setWindowIcon(icon)
		self.main = QtWidgets.QWidget(TimingDiagrammer)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(2)
		sizePolicy.setVerticalStretch(2)
		sizePolicy.setHeightForWidth(self.main.sizePolicy().hasHeightForWidth())
		self.main.setSizePolicy(sizePolicy)
		self.main.setMinimumSize(QtCore.QSize(480, 620))
		self.main.setMouseTracking(True)
		self.main.setObjectName("main")
		self.gridLayout = QtWidgets.QGridLayout(self.main)
		self.gridLayout.setContentsMargins(0, 0, 0, 0)
		self.gridLayout.setVerticalSpacing(0)
		self.gridLayout.setObjectName("gridLayout")
		self.graphicsView = QtWidgets.QGraphicsView(self.main)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
		sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
		sizePolicy.setHorizontalStretch(2)
		sizePolicy.setVerticalStretch(2)
		self.graphicsView.setSizePolicy(sizePolicy)
		self.graphicsView.setMinimumSize(QtCore.QSize(480, 460))
		self.graphicsView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		self.graphicsView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		self.graphicsView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
		self.graphicsView.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
		self.graphicsView.setObjectName("graphicsView")
		self.gridLayout.addWidget(self.graphicsView, 0, 0, 1, 1)
		self.plainTextEdit = QtWidgets.QPlainTextEdit(self.main)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(1)
		sizePolicy.setVerticalStretch(1)
		sizePolicy.setHeightForWidth(self.plainTextEdit.sizePolicy().hasHeightForWidth())
		self.plainTextEdit.setSizePolicy(sizePolicy)
		self.plainTextEdit.setMinimumSize(QtCore.QSize(480, 150))
		self.plainTextEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		self.plainTextEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		self.plainTextEdit.setPlainText("")
		self.plainTextEdit.setObjectName("plainTextEdit")
		self.gridLayout.addWidget(self.plainTextEdit, 1, 0, 1, 1)
		self.label = QtWidgets.QLabel(self.main)
		self.label.setMinimumSize(QtCore.QSize(20, 20))
		self.label.setBaseSize(QtCore.QSize(20, 20))
		self.label.setObjectName("label")
		self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
		TimingDiagrammer.setCentralWidget(self.main)
		self.menu = QtWidgets.QMenuBar(TimingDiagrammer)
		self.menu.setEnabled(True)
		self.menu.setGeometry(QtCore.QRect(0, 0, 693, 32))
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.menu.sizePolicy().hasHeightForWidth())
		self.menu.setSizePolicy(sizePolicy)
		self.menu.setMinimumSize(QtCore.QSize(100, 32))
		self.menu.setNativeMenuBar(True)
		self.menu.setObjectName("menu")
		self.menuFile = QtWidgets.QMenu(self.menu)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.menuFile.sizePolicy().hasHeightForWidth())
		self.menuFile.setSizePolicy(sizePolicy)
		self.menuFile.setMinimumSize(QtCore.QSize(100, 32))
		self.menuFile.setObjectName("menuFile")
		self.menuOptions = QtWidgets.QMenu(self.menu)
		self.menuOptions.setObjectName("menuOptions")
		self.menuHelp = QtWidgets.QMenu(self.menu)
		self.menuHelp.setObjectName("menuHelp")
		TimingDiagrammer.setMenuBar(self.menu)
		self.actionNew = QtWidgets.QAction(TimingDiagrammer)
		self.actionNew.setObjectName("actionNew")
		self.actionOpen = QtWidgets.QAction(TimingDiagrammer)
		self.actionOpen.setObjectName("actionOpen")
		self.actionSave = QtWidgets.QAction(TimingDiagrammer)
		self.actionSave.setObjectName("actionSave")
		self.actionSaveAs = QtWidgets.QAction(TimingDiagrammer)
		self.actionSaveAs.setObjectName("actionSaveAs")
		self.actionExport = QtWidgets.QAction(TimingDiagrammer)
		self.actionExport.setObjectName("actionExport")
		self.actionExit = QtWidgets.QAction(TimingDiagrammer)
		self.actionExit.setObjectName("actionExit")
		self.actionSettings = QtWidgets.QAction(TimingDiagrammer)
		self.actionSettings.setObjectName("actionSettings")
		self.actionAbout = QtWidgets.QAction(TimingDiagrammer)
		self.actionAbout.setObjectName("actionAbout")
		self.menuFile.addAction(self.actionNew)
		self.menuFile.addAction(self.actionOpen)
		self.menuFile.addAction(self.actionSave)
		self.menuFile.addAction(self.actionSaveAs)
		self.menuFile.addAction(self.actionExport)
		self.menuFile.addSeparator()
		self.menuFile.addAction(self.actionExit)
		self.menuOptions.addAction(self.actionSettings)
		self.menuHelp.addAction(self.actionAbout)
		self.menu.addAction(self.menuFile.menuAction())
		self.menu.addAction(self.menuOptions.menuAction())
		self.menu.addAction(self.menuHelp.menuAction())

		self.retranslateUi(TimingDiagrammer)
		QtCore.QMetaObject.connectSlotsByName(TimingDiagrammer)

	def retranslateUi(self, TimingDiagrammer):
		_translate = QtCore.QCoreApplication.translate
		TimingDiagrammer.setWindowTitle(_translate("TimingDiagrammer", "Timing Diagrammer"))
		self.label.setText(_translate("TimingDiagrammer", "Status: Ready"))
		self.menuFile.setTitle(_translate("TimingDiagrammer", "File"))
		self.menuOptions.setTitle(_translate("TimingDiagrammer", "Options"))
		self.menuHelp.setTitle(_translate("TimingDiagrammer", "Help"))
		self.actionNew.setText(_translate("TimingDiagrammer", "New"))
		self.actionOpen.setText(_translate("TimingDiagrammer", "Open"))
		self.actionSave.setText(_translate("TimingDiagrammer", "Save"))
		self.actionSaveAs.setText(_translate("TimingDiagrammer", "Save As"))
		self.actionExport.setText(_translate("TimingDiagrammer", "Export image"))
		self.actionExit.setText(_translate("TimingDiagrammer", "Exit"))
		self.actionSettings.setText(_translate("TimingDiagrammer", "Settings"))
		self.actionAbout.setText(_translate("TimingDiagrammer", "About"))
