import numpy as np
import BMReader as bmr

def DT(beatMap):
    for tp in beatMap.timePoints:
        if(tp.mpb > 0):
            tp.mpb /= 1.5
    for obj in beatMap.hitObjects:
        obj.time /= 1.5
        if(type(obj) is bmr.Spinner):
            obj.endTime /= 1.5

def HR(beatMap):
    for obj in beatMap.hitObjects:
        obj.y = 384 - obj.y
        if(type(obj) is bmr.Slider):
            if(obj.sliderType == "B"):
                for segment in obj.curvePointList:
                    for iPoint, point in enumerate(segment):
                        segment[iPoint] = (point[0], 384 - point[1])
            else:
                for iPoint, point in enumerate(obj.curvePointList):
                    obj.curvePointList[iPoint] = (point[0], 384 - point[1])
