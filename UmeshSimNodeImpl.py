from UmeshSimCore import *

class UmeshSimNodeImpl(object):

	def __init__(self):
		self._inbox = []
		self._outbox = []


	def process(self):
		pass


	def haveMessages(self):
		return len(self._inbox) > 0


	def receive(self):
		return self._inbox.pop(0)


	def send(self, msg):
		self._outbox.append(msg)
