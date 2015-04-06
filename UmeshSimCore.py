import sys
import os
import time
import random
import threading
import math
import rtree

from UmeshSimNodeImpl import *
from UmeshSimNodeAnt import *

from PyQt4 import QtGui, QtCore


class UmeshSimNetwork(object):

	def __init__(self):

		# the network maintains its own graphics scene for displaying
		# all nodes and connections between them
		self._scene = QtGui.QGraphicsScene()
		self._nodes = {}
		self._rtree = rtree.index.Index()
		random.seed()
		x = 0
		y = 0
		for i in xrange(10000):
			node = UmeshSimNode(x, y, UmeshSimNodeAnt(), self)
			node.setName("node%d" % i)
			self._scene.addItem(node)
			self._nodes[i] = node
			self._rtree.insert(i, (x, y))

			azimuth = random.random() * 3.1416 * 2
			length = random.random() * 100 + 300
			x += length * math.cos(azimuth)
			y += length * math.sin(azimuth)

	def scene(self):
		return self._scene


class UmeshSimNode(QtGui.QGraphicsItem):

	COLOR_RANGE = QtGui.QColor(128, 128, 128)
	COLOR_NB_LINKS = QtGui.QColor(255, 128, 128)

	def __init__(self, x, y, impl, network):
		super(UmeshSimNode, self).__init__()

		# node behaviour implementation
		self._impl = impl

		self._name = ""
		self._network = network
		self._hover = False

		self._text_font = QtGui.QFont()
		self._text_font.setPointSize(10)
		self._text_font.setBold(False)

		self.setPos(x, y)
		self.setAcceptHoverEvents(True)


	def paint(self, painter, option, widget):
		painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform | QtGui.QPainter.HighQualityAntialiasing);

		# mark range and neightbors
		if self._hover:
			radius = self.radius()
			painter.setPen(QtGui.QPen(UmeshSimNode.COLOR_RANGE))
			painter.setBrush(QtCore.Qt.NoBrush)
			painter.drawEllipse(QtCore.QRectF(-radius, -radius, radius * 2, radius * 2));

			painter.setPen(QtGui.QPen(UmeshSimNode.COLOR_NB_LINKS))
			for n in self.neighbors():
				painter.drawLine(QtCore.QPointF(0, 0), n.pos() - self.pos())

		painter.setFont(self._text_font)
		painter.setPen(QtGui.QPen(QtGui.QColor(40, 120, 6)))
		rect = QtCore.QRectF(-50, 15, 100, 10)
		painter.drawText(rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter, self._name)

		painter.setPen(QtGui.QPen(QtGui.QColor(76, 154, 6)))
		painter.setBrush(QtGui.QBrush(QtGui.QColor(138, 226, 52)))
		if self._hover:
			painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 236, 70)))

		painter.drawEllipse(QtCore.QRectF(-10, -10, 20, 20));


	def boundingRect(self):
		# depends on the maximum link length
		return QtCore.QRectF(-500, -500, 1000, 1000)


	def shape(self):
		path = QtGui.QPainterPath()
		path.addEllipse(QtCore.QRectF(-20, -20, 40, 40))
		return path

	def setName(self, name):
		self._name = name


	def hoverEnterEvent(self, event):
		self._hover = True
		self.update()
		super(UmeshSimNode, self).hoverEnterEvent(event)


	def hoverLeaveEvent(self, event):
		self._hover = False
		self.update()
		super(UmeshSimNode, self).hoverLeaveEvent(event)


	def neighbors(self):
		nb = []
		for n in self._network._rtree.nearest((self.pos().x(), self.pos().y()), 10):
			p = self._network._nodes[n].pos() - self.pos()
			if p.manhattanLength() < 500 and self._network._nodes[n] != self:
				nb.append(self._network._nodes[n])
		return nb

	def radius(self):
		maxlen = 0
		for n in self._network._rtree.nearest((self.pos().x(), self.pos().y()), 10):
			p = self._network._nodes[n].pos() - self.pos()
			if p.manhattanLength() < 500 and self._network._nodes[n] != self and p.manhattanLength() > maxlen:
				maxlen = p.manhattanLength()
		return maxlen



class UmeshSimView(QtGui.QGraphicsView):

	def __init__(self):
		super(UmeshSimView, self).__init__()
		self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
		self._is_panning = False
		self._mouse_pressed = False
		self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform | QtGui.QPainter.HighQualityAntialiasing);


	def mousePressEvent(self,  event):
		if event.button() == QtCore.Qt.LeftButton:
			self._mouse_pressed = True
			self._is_panning = True
			self.setCursor(QtCore.Qt.ClosedHandCursor)
			self._drag_pos = event.pos()
			event.accept()
		else:
			super(UmeshSimView, self).mousePressEvent(event)


	def mouseMoveEvent(self, event):
		if self._mouse_pressed and self._is_panning:
			newPos = event.pos()
			diff = newPos - self._drag_pos
			self._drag_pos = newPos
			self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - diff.x())
			self.verticalScrollBar().setValue(self.verticalScrollBar().value() - diff.y())
			event.accept()
		else:
			super(UmeshSimView, self).mouseMoveEvent(event)


	def mouseReleaseEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self._is_panning = False
			self._mouse_pressed = False
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

		self._settings = QtCore.QSettings("umesh-sim.ini", QtCore.QSettings.IniFormat)
		self.setObjectName("mainwindow")

		self._network = UmeshSimNetwork()
		self._gr_view = UmeshSimView()
		self._gr_view.setScene(self._network.scene())
		self.setCentralWidget(self._gr_view)

		self.show()
		self.loadSettings()


	def saveSettings(self):
		self._settings.beginGroup("main")
		self._settings.setValue("state", self.saveState())
		self._settings.endGroup()


	def loadSettings(self):
		self._settings.beginGroup("main")
		self.restoreState(self._settings.value("state").toByteArray())
		self._settings.endGroup()


	def closeEvent(self, event):
		self.saveSettings()
		QtGui.qApp.quit()
