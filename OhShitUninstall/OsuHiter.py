from PyQt5.QtCore import *
from PyQt5.QtGui import *
import time
import win32api as w32
import win32con as w32c
from LocTransform import *
import Trajectory
import Hit
import sys
import BMReader
import numpy as np

class OHT(QObject):
    keyCode = (0x5A, 0x58)
    def __init__(self, beatMap, parent = None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.checkOutput)
        self.beatMap = beatMap
        self.iNextPoint = 0
        self.iNextHit = 0
        self.beginTime = None
        self.tc = Trajectory.Converter()
        self.ht = Hit.Converter()
        self.timeList, self.pointList = self.tc(beatMap)
        self.eventList = self.ht(beatMap, self.timeList, self.pointList)
        self.started = False

    def checkOutput(self):
        nowTime = time.time() * 1000
        if(self.iNextPoint < len(self.timeList)):
            nextPointTime = self.timeList[self.iNextPoint]
            nextPoint = self.pointList[self.iNextPoint]
            if((nowTime - self.beginTime) >= nextPointTime):
                x, y = transLoc(nextPoint[0], nextPoint[1])
                if(not(np.isnan(x) or np.isnan(y))):
                    x, y = int(round(x)), int(round(y))
                    w32.SetCursorPos((x, y))
                self.iNextPoint += 1
        if(self.iNextHit < len(self.eventList)):
            nextHitTime, nextKey, nextKeyPress = self.eventList[self.iNextHit]
            if((nowTime - self.beginTime) >= nextHitTime):
                if(nextKey in (0, 1)):
                    if(nextKeyPress):
                        w32.keybd_event(self.keyCode[nextKey], 0, 0, 0)
                    else:
                        w32.keybd_event(self.keyCode[nextKey], 0, w32c.KEYEVENTF_KEYUP, 0)
                self.iNextHit += 1
        if(self.iNextPoint >= len(self.timeList) and self.iNextHit >= len(self.eventList)):
            sys.exit()

    def start(self):
        self.iNextPoint = 1
        self.iNextPoint = 0
        if(type(self.beatMap.hitObjects[0]) is BMReader.Slider):
            self.iNextHit = 1
        else:
            self.iNextHit = 2
        self.beginTime = time.time() * 1000 - self.beatMap.hitObjects[0].time
        self.started = True
        self.timer.start(1)

    def stop(self):
        self.timer.stop()
        self.started = False
