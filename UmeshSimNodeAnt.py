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

	def process(self):
		super(UmeshSimNodeAnt, self).process()
		self._time += 1

		if self._time % 10 == 0:
			self.send(json.dumps({
				"dst": "broadcast",
				"message": "nbdiscovery",
				"id": self._id
			}))


