import numpy as np
import BMReader

def pointInCircle(p, c, r):
    return np.abs(complex(p[0], p[1]) - complex(c[0], c[1])) < r

class Converter:
    def __init__(self):
        self.maxError = 22.0
        self.maxErrorCenter = 10.0
        self.circleHitTime = 40.0
        self.sliderReleaseTime = 50.0
        self.maxCircleHitTimeError = 8.0
        self.maxSliderReleaseTimeError = 8.0

    def __call__(self, beatMap, timeList, pointList):
        beginTime = beatMap.hitObjects[0].time
        endTime = beatMap.hitObjects[-1].time + 1000
        perfect = 0
        good = 0
        miss = 0
        events = []
        key = 0
        for iObj, obj in enumerate(beatMap.hitObjects):
            errorCenter = np.random.uniform(-self.maxErrorCenter, self.maxErrorCenter)
            pressError, releaseError = np.random.normal(errorCenter, self.maxError / 3, 2)
            pressTime = obj.time + pressError
            center = (obj.x, obj.y)
            radius = 36 / beatMap.circleSize
            # get best time
            i = np.searchsorted(timeList, pressTime, side='left')
            perfect += 1
            events.append((pressTime, key, True))
            key = 0 if(key == 1) else 1
            if(type(obj) is BMReader.HitCircle):
                circleHitTime = np.random.normal(self.circleHitTime, self.maxCircleHitTimeError / 3)
                events.append((events[-1][0] + circleHitTime, 0 if(key == 1) else 1, False))
            elif(type(obj) is BMReader.Slider):
                sliderReleaseTime = np.random.normal(self.sliderReleaseTime, self.maxSliderReleaseTimeError / 3)
                totalTime = obj.pixelLength / (100 * beatMap.sliderMultiplier * beatMap.svmAt(obj.time)) * beatMap.mpbAt(obj.time) * obj.repeat
                events.append((events[-1][0] + totalTime + releaseError + sliderReleaseTime, 0 if(key == 1) else 1, False))
            elif(type(obj) is BMReader.Spinner):
                if(iObj + 1 == len(beatMap.hitObjects)):
                    endTime = obj.endTime + 1200
                else:
                    endTime = obj.endTime
                events.append((endTime + releaseError, 0 if(key == 1) else 1, False))
        print("Prefect: %d\nGood: %d\nMiss: %d" % (perfect, good, miss))
        return events
