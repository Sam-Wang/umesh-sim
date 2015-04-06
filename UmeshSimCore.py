import sys
import os
import time
from PyQt4 import QtGui, QtCore



class UmeshSimView(QtGui.QGraphicsView):

	def __init__(self):
		super(UmeshSimView, self).__init__()
		self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
		self._isPanning = False
		self._mousePressed = False


	def mousePressEvent(self,  event):
		if event.button() == QtCore.Qt.LeftButton:
			self._mousePressed = True
			self._isPanning = True
			self.setCursor(QtCore.Qt.ClosedHandCursor)
			self._dragPos = event.pos()
			event.accept()
		else:
			super(UmeshSimView, self).mousePressEvent(event)


	def mouseMoveEvent(self, event):
		if self._mousePressed and self._isPanning:
			newPos = event.pos()
			diff = newPos - self._dragPos
			self._dragPos = newPos
			self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - diff.x())
			self.verticalScrollBar().setValue(self.verticalScrollBar().value() - diff.y())
			event.accept()
		else:
			super(UmeshSimView, self).mouseMoveEvent(event)


	def mouseReleaseEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self._isPanning = False
			self._mousePressed = False
			self.setCursor(QtCore.Qt.ArrowCursor)
		else:
			super(UmeshSimView, self).mouseReleaseEvent(event)


	def wheelEvent(self,  event):
		factor = 1.2;
		if event.delta() < 0:
			factor = 1.0 / factor
		self.scale(factor, factor)


class UmeshSimApp(QtGui.QMainWindow):

	def __init__(self):
		super(UmeshSimApp, self).__init__()

		self.settings = QtCore.QSettings("umesh-sim.ini", QtCore.QSettings.IniFormat)
		self.setObjectName("mainwindow")

		self.gr_scene = QtGui.QGraphicsScene()
		self.gr_scene.addText("test")

		self.gr_view = UmeshSimView()
		self.gr_view.setScene(self.gr_scene)
		self.setCentralWidget(self.gr_view)

		self.show()
		self.loadSettings()


	def saveSettings(self):
		self.settings.beginGroup("main")
		self.settings.setValue("state", self.saveState())
		self.settings.endGroup()


	def loadSettings(self):
		self.settings.beginGroup("main")
		self.restoreState(self.settings.value("state").toByteArray())
		self.settings.endGroup()


	def closeEvent(self, event):
		self.saveSettings()
		QtGui.qApp.quit()
