#!/usr/bin/python

import sys
import os
import signal
from PyQt4 import QtGui, QtCore

from UmeshSimCore import *

sim = None

def sigterm_handler(signum, frame):
        print ""
        QtGui.qApp.closeAllWindows()


def main():
        global sim

        # monitor signals
        signal.signal(signal.SIGTERM, sigterm_handler)
        signal.signal(signal.SIGINT, sigterm_handler)

        app = QtGui.QApplication(sys.argv)
        sim = UmeshSimApp()

	# this timer needs to be run in order to catch and process
	# sigterm and sigint signals
	tim = QtCore.QTimer()
	tim.timeout.connect(lambda: None)
	tim.start(500)

        sys.exit(app.exec_())


if __name__ == '__main__':
        main()

