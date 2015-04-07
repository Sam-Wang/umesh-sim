from UmeshSimCore import *
import json

class UmeshSimNodeAnt(UmeshSimNodeImpl):

	def __init__(self):
		super(UmeshSimNodeAnt, self).__init__()

		# Time of node start (in steps). Assuming one step in 100ms,
		# start with a range of the whole day.
		self._time = random.randint(0, 864000)

		# Assing random node identifier.
		self._id = random.randint(0, 256 * 256 * 256 * 256)

		self._neighbors = {}

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
