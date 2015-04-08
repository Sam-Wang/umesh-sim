from UmeshSimCore import *

class UmeshSimNodeImpl(object):

	def __init__(self, nid):
		self._inbox = []
		self._outbox = []
		self._id = nid

	def process(self):
		pass


	def haveMessages(self):
		return len(self._inbox) > 0


	def receive(self):
		return self._inbox.pop(0)


	def send(self, msg):
		self._outbox.append(msg)


	def tooltip(self):
		return ""


	def connections(self):
		return {}


	def contextMenu(self):
		return None


	def contextMenuAction(self, action):
		pass


	def color(self):
		return None
