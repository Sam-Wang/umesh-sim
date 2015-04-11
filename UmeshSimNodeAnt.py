import json
import random
from PyQt4 import QtGui, QtCore
from UmeshSimCore import *


class UmeshSimNodeAntPheromone(object):

	def __init__(self, origin):
		self._origin = origin
		self._pheromone = {}


	def addPheromone(self, neighbor, ph):
		try:
			self._pheromone[neighbor] += ph
		except KeyError:
			self._pheromone[neighbor] = ph


	def neighbors(self):
		return list(self._pheromone.keys())


	def decrease(self):
		""" This equals to a pheromone evaporating function."""

		k_to_remove = []
		for k in self._pheromone.iterkeys():
			if self._pheromone[k] > 0:
				self._pheromone[k] -= 0.1
			else:
				k_to_remove.append(k)
		for k in k_to_remove:
			del self._pheromone[k]

	def isEmpty(self):
		#~ return False
		return len(self._pheromone) <= 0


	def average(self):
		v = list(self._pheromone.itervalues())
		return sum(v) / len(v)




class UmeshSimNodeAnt(UmeshSimNodeImpl):

	def __init__(self, nid):
		super(UmeshSimNodeAnt, self).__init__(nid)

		# Time of node start (in steps). Assuming one step in 100ms,
		# start with a range of the whole day.
		self._time = random.randint(0, 864000)

		self._neighbors = {}
		self._pheromone = {}

		self._action_set_source = QtGui.QAction("Set as source node", None)
		self._action_set_destination = QtGui.QAction("Set as destination node", None)
		self._action_send_test_ant = QtGui.QAction("Send test ant", None)

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
			if msg["type"] == "ant":
				self._parseAnt(msg)

		nb_to_delete = []
		for k in self._neighbors.iterkeys():
			# Increment time for all neighbors
			self._neighbors[k] += 1
			if self._neighbors[k] > 20:
				# And remove those which are older than 2 seconds
				nb_to_delete.append(k)

		for k in nb_to_delete:
			del self._neighbors[k]

		ph_to_delete = []
		for k in self._pheromone.iterkeys():
			self._pheromone[k].decrease()
			if self._pheromone[k].isEmpty():
				ph_to_delete.append(k)

		for k in ph_to_delete:
			del self._pheromone[k]


	def tooltip(self):
		nb = ""
		for k in self._neighbors.iterkeys():
			nb += "id = %d, time = %d<br>" % (k, self._neighbors[k])

		return "ant<br>time = %d<br><b>neighbors:</b><br>%s" % (self._time, nb)


	def connections(self):
		origins = list(self._pheromone.itervalues())
		links = {}

		for origin in origins:
			for neighbor in origin.neighbors():
				try:
					links[neighbor].append(origin._pheromone[neighbor])
				except:
					links[neighbor] = []
					links[neighbor].append(origin._pheromone[neighbor])

		r = {}
		for neighbor in links.iterkeys():
			v = links[neighbor]
			avg = int(sum(v) / len(v)) * 20
			if avg > 255:
				avg = 255

			r[neighbor] = QtGui.QColor(0, 128, 0, avg)

		return r


	def contextMenu(self):
		menu = QtGui.QMenu()
		menu.addAction(self._action_set_source)
		menu.addAction(self._action_set_destination)
		menu.addSeparator()
		menu.addAction(self._action_send_test_ant)
		return menu


	def contextMenuAction(self, action):
		if action == self._action_set_source:
			self._is_source = True
		if action == self._action_set_destination:
			self._is_destination = True
		if action == self._action_send_test_ant:
			self._forwardAnt(self._id, 20)


	def color(self):
		if self._is_source:
			return QtGui.QColor(138, 226, 52)
		if self._is_destination:
			return QtGui.QColor(252, 175, 62)
		return None


	def _forwardAnt(self, origin, happiness):
		if len(self._neighbors.keys()) == 0:
			# no neighbors, return
			return

		nb = random.choice(list(set(self._neighbors.keys()) - set([self._id])))

		self.send(json.dumps({
			"src": self._id,
			"dst": nb,
			"type": "ant",
			"origin": origin,
			"destination": 0,
			"happiness": happiness
		}))


	def _parseAnt(self, msg):
		# Update the pheromone table
		try:
			o = msg["origin"]
			h = msg["happiness"]
			src = msg["src"]
			dst = msg["dst"]

			# enable this filter for ANT-like message forwarding
			#~ if dst != self._id:
				#~ return

			if h == 0:
				return

			# enable this filter to support same-ant blocking for
			# AODV-like forwarding
			try:
				a = self._pheromone[o].average()
				if h < a + 1:
					return
			except KeyError:
				pass

			try:
				self._pheromone[o].addPheromone(src, h)
			except KeyError:
				self._pheromone[o] = UmeshSimNodeAntPheromone(o)
				self._pheromone[o].addPheromone(src, h)

			self._forwardAnt(o, h - 1)

		except KeyError:
			# No origin found, we are not updating the ptable
			pass



