"""This file implements the graphical version of program"""
import sys
import logging


LOGGER = logging.getLogger("guiBMP")
logging.basicConfig(filename="guiBMP.log", level=logging.INFO)


try:
    from core import *
except Exception as exception:
    LOGGER.error('Program modules not found: {}'.format(exception))
    sys.exit('Program modules not found: {}'.format(exception))

try:
    from PyQt5 import QtWidgets, QtGui, QtCore
except Exception as exception:
    LOGGER.error('PyQT5 module not found: {}'.format(exception))
    sys.exit('PyQt5 not found: {}'.format(exception))


class Window(QtWidgets.QWidget):
    """Main window"""

    def __init__(self, picture_name=None):
        super().__init__()
        self.picture_name = picture_name
