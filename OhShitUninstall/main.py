# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import BMReader as bmr
import pythoncom as pc
import pyHook as ph
import OsuHiter
import sys
import time
import Modifiers

firstZ = False

def okd(ev):
    global firstZ
    if(ev.Key == 'Escape'):
        firstZ = False
        hiter.stop()
    elif(ev.Key == 'Z'):
        if(not hiter.started):
            hiter.start()
    return ev.KeyID

def oku(ev):
    global firstZ
    if(ev.Key == 'Z'):
        if((not firstZ) and (type(hiter.beatMap.hitObjects[0]) is bmr.Slider or type(hiter.beatMap.hitObjects[0]) is bmr.Spinner)):
            firstZ = True
            return False
    return ev.KeyID

app = QApplication([])
bm = bmr.Beatmap()
bm.load(r"Spawn Of Possession - Apparition (Mazzerin) [Blind Faith].osu")
#Modifiers.HR(bm)
#Modifiers.DT(bm)

hm = ph.HookManager()
hm.KeyDown = okd
hm.KeyUp = oku
hm.HookKeyboard()

hiter = OsuHiter.OHT(bm)

app.exec()
