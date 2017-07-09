from PyQt5.QtCore import *
from PyQt5.QtGui import *

def transLoc(x, y, screenSize = None):
    if(screenSize is None):
        screen = QGuiApplication.primaryScreen()
        screenSize = screen.size()
        sw, sh = screenSize.width(), screenSize.height()
    else:
        sw, sh = screenSize
    if(sw * 3 > sh * 4):
        nsw = sh * 4 / 3
        nsh = sh
    else:
        nsh = sw * 3 / 4
        nsw = sw
    leftPad = (sw - nsw) / 2
    topPad = (sh - nsh) / 2
    return (leftPad + (x + (640 - 512) / 2) / 640 * nsw, topPad + (y + (480 - 384) / 2) / 480 * nsh)
