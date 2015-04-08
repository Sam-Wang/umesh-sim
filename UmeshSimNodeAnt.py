import json
from PyQt4 import QtGui, QtCore
from UmeshSimCore import *

class UmeshSimNodeAnt(UmeshSimNodeImpl):

	def __init__(self, nid):
		super(UmeshSimNodeAnt, self).__init__(nid)

		# Time of node start (in steps). Assuming one step in 100ms,
		# start with a range of the whole day.
		self._time = random.randint(0, 864000)

		self._neighbors = {}

		self._action_set_source = QtGui.QAction("Set as source node", None)
		self._action_set_destination = QtGui.QAction("Set as destination node", None)

		self._is_source = False
		self._is_destination = False


	def process(self):
		super(UmeshSimNodeAnt, self).process()
		self._time += 1

		# Send route discovery message
		if self._time % 10 == 0:
			self.send(json.dumps({
				"src": self._id,
				"dst": "broadcast",
				"type": "nbdiscovery"
			}))

		while self.haveMessages():
			msg = json.loads(self.receive())
			if msg["type"] == "nbdiscovery":
				# Add the neighbor with zero time
				self._neighbors[msg["src"]] = 0

		nb_to_delete = []
		for k in self._neighbors.iterkeys():
			# Increment time for all neighbors
			self._neighbors[k] += 1
			if self._neighbors[k] > 20:
				# And remove those which are older than 2 seconds
				nb_to_delete.append(k)

		for k in nb_to_delete:
			del self._neighbors[k]


	def tooltip(self):
		nb = ""
		for k in self._neighbors.iterkeys():
			nb += "id = %d, time = %d<br>" % (k, self._neighbors[k])

		return "ant<br>time = %d<br><b>neighbors:</b><br>%s" % (self._time, nb)


	def connections(self):
		r = {}
		for k in self._neighbors.iterkeys():
			r[k] = QtGui.QColor(0, 128, 0)

		return r


	def contextMenu(self):
		menu = QtGui.QMenu()
		menu.addAction(self._action_set_source)
		menu.addAction(self._action_set_destination)
		return menu


	def contextMenuAction(self, action):
		if action == self._action_set_source:
			self._is_source = True
		if action == self._action_set_destination:
			self._is_destination = True


	def color(self):
		if self._is_source:
			return QtGui.QColor(138, 226, 52)
		if self._is_destination:
			return QtGui.QColor(252, 175, 62)
		return None

