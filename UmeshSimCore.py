import sys
import os
import time
import random
import threading
import math
import rtree

from PyQt4 import QtGui, QtCore

from UmeshSimNodeImpl import *
from UmeshSimNodeAnt import *


class UmeshSimNetwork(object):

	def __init__(self):
		# The network maintains its own graphics scene for displaying
		# all nodes and connections between them. If a node has to be
		# added or removed, all three lists must be handled correctly.
		# Use addNode and deleteNode for this purpose.
		self._scene = QtGui.QGraphicsScene()
		self._nodes = {}
		self._rtree = rtree.index.Index()

		# Initialize the network. Create some random nodes.
		random.seed()
		x = 0
		y = 0
		for i in xrange(1000):
			node = UmeshSimNode(x, y, UmeshSimNodeAnt(), self)
			node.setName("node%d" % i)
			nodeid = random.randint(0, 256 * 256 * 256 * 256)
			self.addNode(node, nodeid)

			azimuth = random.random() * 3.1416 * 2
			length = random.random() * 100 + 200
			x += length * math.cos(azimuth)
			y += length * math.sin(azimuth)

		self._running = False
		self.start()

	def scene(self):
		return self._scene


	def addNode(self, node, nodeid):
		self._scene.addItem(node)
		self._nodes[nodeid] = node
		self._rtree.insert(nodeid, (node.pos().x(), node.pos().y()))


	def deleteNode(self, nodeid):
		pass


	def start(self):
		if self._running:
			raise Exception("the network is already running")
		else:
			self._running = True
			self._step()


	def stop(self):
		if not self._running:
			raise Exception("the network is not running")
		else:
			self._running = False


	def _step(self):
		# Try to deliver pending messages from all nodes in the network
		# to their neighbors.
		for n in self._nodes.itervalues():
			n.processOutbox()

		# And then run the process method for all nodes.
		for n in self._nodes.itervalues():
			n.process()

		if self._running:
			timer = threading.Timer(1, self._step)
			timer.daemon = True
			timer.start()


class UmeshSimNode(QtGui.QGraphicsItem):

	COLOR_RANGE = QtGui.QColor(128, 128, 128)
	COLOR_NB_LINKS = QtGui.QColor(128, 128, 128)
	COLOR_ACTIVE = QtGui.QColor(206, 92, 0)
	COLOR_ACTIVE_BG = QtGui.QColor(240, 160, 0, 10)
	COLOR_SELECTED = QtGui.QColor(255, 128, 128)

	COLOR_NODE_STROKE = QtGui.QColor(128, 128, 128)
	COLOR_NODE_FILL = QtGui.QColor(192, 192, 192)
	COLOR_NODE_HSTROKE = QtGui.QColor(140, 140, 140)
	COLOR_NODE_HFILL = QtGui.QColor(210, 210, 210)

	COLOR_NODE_SRC_STROKE = QtGui.QColor(76, 154, 6)
	COLOR_NODE_SRC_FILL = QtGui.QColor(138, 226, 52)
	COLOR_NODE_DST_STROKE = QtGui.QColor(206, 92, 0)
	COLOR_NODE_DST_FILL = QtGui.QColor(252, 175, 62)
	COLOR_NODE_TEXT_NAME = QtGui.QColor(128, 128, 128)


	def __init__(self, x, y, impl, network):
		super(UmeshSimNode, self).__init__()

		# node behaviour implementation
		self._impl = impl

		self._name = ""
		self._network = network
		self._hover = False

		# Indicator of activity (set to true if there was any data
		# trasnmitted from the last call of processOutbox).
		self._data_transmitted = False

		self._text_font = QtGui.QFont()
		self._text_font.setPointSize(10)
		self._text_font.setBold(False)

		self.setPos(x, y)
		self.setAcceptHoverEvents(True)
		self.setFlags(QtGui.QGraphicsItem.ItemIsMovable | QtGui.QGraphicsItem.ItemIsSelectable)


	def paint(self, painter, option, widget):
		painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform | QtGui.QPainter.HighQualityAntialiasing);

		# mark range and neightbors
		if self.isUnderMouse():
			radius = self.radius()
			painter.setPen(QtGui.QPen(UmeshSimNode.COLOR_RANGE))
			painter.setBrush(QtCore.Qt.NoBrush)
			painter.drawEllipse(QtCore.QRectF(-radius, -radius, radius * 2, radius * 2));

			painter.setPen(QtGui.QPen(UmeshSimNode.COLOR_NB_LINKS))
			for n in self.neighbors():
				painter.drawLine(QtCore.QPointF(0, 0), n.pos() - self.pos())

		# draw node name
		painter.setFont(self._text_font)
		painter.setPen(QtGui.QPen(UmeshSimNode.COLOR_NODE_TEXT_NAME))
		painter.drawText(QtCore.QRectF(-50, 15, 100, 10), QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter, self._name)

		# and draw the node circle
		if self.isUnderMouse():
			painter.setPen(QtGui.QPen(UmeshSimNode.COLOR_NODE_HSTROKE))
			painter.setBrush(QtGui.QBrush(UmeshSimNode.COLOR_NODE_HFILL))
		else:
			painter.setPen(QtGui.QPen(UmeshSimNode.COLOR_NODE_STROKE))
			painter.setBrush(QtGui.QBrush(UmeshSimNode.COLOR_NODE_FILL))
		painter.drawEllipse(QtCore.QRectF(-10, -10, 20, 20));

		if self._data_transmitted:
			painter.setPen(QtGui.QPen(UmeshSimNode.COLOR_ACTIVE))
			painter.setBrush(QtCore.Qt.NoBrush)
			painter.drawEllipse(QtCore.QRectF(-11, -11, 22, 22));

			painter.setPen(QtGui.QPen(UmeshSimNode.COLOR_ACTIVE_BG))
			painter.setBrush(UmeshSimNode.COLOR_ACTIVE_BG)
			radius = self.radius()
			painter.drawEllipse(QtCore.QRectF(-radius, -radius, radius * 2, radius * 2));

		if self.isSelected():
			pen = QtGui.QPen(UmeshSimNode.COLOR_SELECTED)
			pen.setWidth(3)
			pen.setCosmetic(True)
			pen.setStyle(QtCore.Qt.DotLine)
			painter.setPen(pen)
			painter.setBrush(QtCore.Qt.NoBrush)
			painter.drawEllipse(QtCore.QRectF(-13, -13, 26, 26));


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
		self.setCursor(QtCore.Qt.OpenHandCursor)
		super(UmeshSimNode, self).hoverEnterEvent(event)


	def hoverLeaveEvent(self, event):
		self._hover = False
		self.setCursor(QtCore.Qt.ArrowCursor)
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


	def process(self):
		self._impl.process()


	def processOutbox(self):
		# Iteratively pop all messages from the item's outbox and deliver
		# them to all its neighbors.
		tx = False
		while len(self._impl._outbox) > 0:
			tx = True
			msg = self._impl._outbox.pop()
			for nb in self.neighbors():
				nb._impl._inbox.append(msg)
		# Call update to update data transmission indicators.
		if self._data_transmitted != tx:
			self._data_transmitted = tx
			self.update()



class UmeshSimView(QtGui.QGraphicsView):

	def __init__(self):
		super(UmeshSimView, self).__init__()
		self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
		self._is_panning = False
		self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform | QtGui.QPainter.HighQualityAntialiasing);


	def mousePressEvent(self,  event):
		if event.button() == QtCore.Qt.MiddleButton:
			self._is_panning = True
			self.setCursor(QtCore.Qt.ClosedHandCursor)
			self._drag_pos = event.pos()
			event.accept()
		else:
			super(UmeshSimView, self).mousePressEvent(event)


	def mouseMoveEvent(self, event):
		if self._is_panning:
			newPos = event.pos()
			diff = newPos - self._drag_pos
			self._drag_pos = newPos
			self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - diff.x())
			self.verticalScrollBar().setValue(self.verticalScrollBar().value() - diff.y())
			event.accept()
		else:
			super(UmeshSimView, self).mouseMoveEvent(event)


	def mouseReleaseEvent(self, event):
		if event.button() == QtCore.Qt.MiddleButton:
			self._is_panning = False
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

