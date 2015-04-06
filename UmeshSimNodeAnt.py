from UmeshSimCore import *

class UmeshSimNodeAnt(UmeshSimNodeImpl):

	def __init__(self, ):
		super(UmeshSimNodeAnt, self).__init__()
		#~ self.sendBroadcast()

	def sendBroadcast(self):
		# schedule next broadcast
		timer = threading.Timer(1, self.sendBroadcast)
		timer.daemon = True
		timer.start()


