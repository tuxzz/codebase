import numpy as np
import scipy.interpolate as ipl
import pylab as pl
import BMReader
from scipy.misc import comb
import sys

def bernstein_poly(i, n, t):
    return comb(n, i) * ( t**(n-i) ) * (1 - t)**i


def bezier_curve(points, nTimes=1000):
    nPoints = len(points)
    xPoints = np.array([p[0] for p in points])
    yPoints = np.array([p[1] for p in points])

    t = np.linspace(0.0, 1.0, nTimes)

    polynomial_array = np.array([ bernstein_poly(i, nPoints-1, t) for i in range(0, nPoints)   ])

    xvals = np.dot(xPoints, polynomial_array)
    yvals = np.dot(yPoints, polynomial_array)

    return np.array((xvals, yvals)).T[::-1]

def slove_circle(a, b, c):
    w = c - a
    w /= b - a
    circle = (a - b) * (w - np.abs(w) ** 2) / 2j / w.imag - a
    return -circle.real, -circle.imag, np.abs(circle + a)

def circle_curve(points, nTimes=1000):
    (x0, y0), (x1, y1), (x2, y2) = points
    a, b, c = complex(x0, y0), complex(x1, y1), complex(x2, y2)
    x, y, r = slove_circle(a, b, c)
    circle = complex(x, y)
    phase1 = np.angle(a - circle)
    phase2 = np.angle(b - circle)
    phase3 = np.angle(c - circle)
    phase1, phase2, phase3 = np.unwrap([phase1, phase2, phase3])
    t = np.linspace(0.0, 1.0, nTimes)
    phase = (phase3 - phase1) * t + phase1
    out = np.zeros((2, nTimes), dtype = np.float64)
    out[0] = r * np.cos(phase) + x
    out[1] = r * np.sin(phase) + y
    return out.T

def pointDistance(a, b):
    return np.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2))

def randomizePoint(p, sigma):
    return np.asarray(p) + np.random.uniform(-sigma * 3, sigma * 3, 2)

def randomizeConPointList(conPointList, sigma, first = None):
    if(type(conPointList[0]) == list and type(conPointList[0][0]) in (list, tuple)):
        segments = []
        for segment in conPointList:
            segments.append([randomizePoint(conPoint, sigma) for conPoint in segment])
        if(not first is None):
            segments[0][0] = first
        return segments
    else:
        o = [randomizePoint(conPoint, sigma) for conPoint in conPointList]
        if(not first is None):
            o[0] = first
        return o

def normalizeToUnitCirlce(vec):
    vec = complex(vec[0], vec[1])
    vec /= np.abs(vec)
    return np.array((vec.real, vec.imag))

def pointAngle(p1, p2):
    np0 = normalizeToUnitCirlce(p1)
    np1 = normalizeToUnitCirlce(p2)
    return np.arccos(np.dot(np0, np1))

def stripAngle(conPointList, maxAngle):
    out = conPointList[:]
    iPoint = 1
    while True:
        if(iPoint + 1 >= len(out)):
            break
        if(pointAngle(out[iPoint], out[iPoint + 1]) > maxAngle):
            del out[iPoint]
            iPoint = 1
        else:
            iPoint += 1
    return out

def stripDistance(path, dist):
    path = list(path)
    i = 1
    while(i < len(path) - 1):
        if(pointDistance(path[i], path[i - 1]) < dist):
            del path[i]
        else:
            i += 1
    del i
    return path

def stripDA(path, dist, angle):
    npath = list(path)
    totalLen = 0.0
    for i in range(1, len(path)):
        totalLen += pointDistance(path[i], path[i - 1])
    nowLen = 0.0
    for i in range(1, len(path) - 1):
        nowLen += pointDistance(path[i], path[i - 1])
        if(pointDistance(npath[i], npath[i - 1]) < dist and pointAngle(npath[i], npath[i - 1]) > angle):
            pt = complex(*path[i]) + (complex(*path[-1]) - complex(*path[i])) * nowLen / totalLen
            npath[i] = (pt.real, pt.imag)
    return npath

def shortenLength(path, ballSize):
    path = list(path)
    ap = np.array(path[0])
    bp = np.array(path[1])
    ap += normalizeToUnitCirlce(bp) * ballSize
    path[0] = ap
    ap = np.array(path[-1])
    bp = np.array(path[-2])
    ap -= normalizeToUnitCirlce(bp) * ballSize
    path[-1] = ap
    return path

def shortenLengthS(path, ballSize):
    path = list(path)
    ap = np.array(path[0][0])
    bp = np.array(path[0][1])
    ap += normalizeToUnitCirlce(bp) * ballSize
    path[0][0] = ap
    ap = np.array(path[-1][-1])
    bp = np.array(path[-1][-2])
    ap -= normalizeToUnitCirlce(bp) * ballSize
    path[-1][-1] = ap
    return path

class Converter:
    def __init__(self):
        self.reportRate = 10.0
        self.spinMagn = 48
        self.spinPhaseSpeed = 190
        self.spinPhaseAcceleration = 1
        self.spinPhaseUnstable = 25
        self.spinMagnNoise = 32
        self.spinShapeNoise = 0.3
        self.locNoiseSigmaFac = 1.00
        self.dropDistance = 16
        self.dropSpeed = 2 / 3
        self.longSpaceHitTime = 600
        self.transHelixMagn = 24
        self.globalDitherSigma = 0.3
        self.stopSliderLength = 64
        self.stripDistance = 48
        self.stripAngle = 120 / 360 * 2 * np.pi
        self.stripDADist = 64
        self.stripDAAngle = 45 / 360 * 2 * np.pi
        self.ballSize = 12

    def __call__(self, beatMap):
        beginTime = beatMap.hitObjects[0].time
        endTime = beatMap.hitObjects[-1].time + 1000
        if(type(beatMap.hitObjects[-1]) is BMReader.Spinner):
            endTime += beatMap.hitObjects[-1].endTime
        elif(type(beatMap.hitObjects[-1]) is BMReader.Slider):
            endTime += beatMap.hitObjects[-1].pixelLength / (100 * beatMap.sliderMultiplier * beatMap.svmAt(beatMap.hitObjects[-1].time)) * beatMap.mpbAt(beatMap.hitObjects[-1].time)
        timeList = []
        pointList = []
        for iObj, obj in enumerate(beatMap.hitObjects):
            timeList.append(obj.time)
            if(self.locNoiseSigmaFac == 0.0):
                realObjLoc = (obj.x, obj.y)
                pointList.append(realObjLoc)
            else:
                realObjLoc = randomizePoint((obj.x, obj.y), 32 / beatMap.circleSize / 3 * self.locNoiseSigmaFac)
                pointList.append(realObjLoc)
            if(type(obj) is BMReader.Slider):
                totalTime = obj.pixelLength / (100 * beatMap.sliderMultiplier * beatMap.svmAt(obj.time)) * beatMap.mpbAt(obj.time) * obj.repeat
                if(self.locNoiseSigmaFac == 0.0):
                    curvePointList = obj.curvePointList
                else:
                    curvePointList = randomizeConPointList(obj.curvePointList, 32 / beatMap.circleSize / 3 * self.locNoiseSigmaFac * 0.25, first = realObjLoc)
                if(obj.pixelLength < self.stopSliderLength):
                    path = [realObjLoc, realObjLoc]
                elif(obj.sliderType == "B"):
                    path = []
                    totalConPointLength = 0.0
                    conPointLengthList = []
                    for iSegment, segment in enumerate(curvePointList):
                        conPointLength = 0.0
                        for iPoint, point in enumerate(segment[:-1]):
                            conPointLength += pointDistance(point, segment[iPoint + 1])
                        totalConPointLength += conPointLength
                        conPointLengthList.append(conPointLength)
                    iSegment = 0
                    while(iSegment < len(curvePointList) - 1):
                        if(pointDistance(curvePointList[iSegment][0], curvePointList[iSegment][-1]) < self.stripDADist):
                            del curvePointList[iSegment][-1]
                            curvePointList[iSegment] += curvePointList[iSegment + 1][1:]
                            del curvePointList[iSegment + 1]
                        else:
                            iSegment += 1
                    for iSegment, segment in enumerate(curvePointList):
                        curvePointList[iSegment] = stripAngle(segment, maxAngle = self.stripAngle)
                        curvePointList[iSegment] = stripDistance(segment, self.stripDistance)
                        curvePointList[iSegment] = stripDA(segment, self.stripDADist, self.stripDAAngle)
                    try:
                        curvePointList = shortenLengthS(curvePointList, self.ballSize)
                    except IndexError:
                        print("OOR x 1")
                    for iSegment, segment in enumerate(curvePointList):
                        path += list(bezier_curve(segment, int(np.ceil(conPointLengthList[iSegment] / totalConPointLength * totalTime / 24.0))))
                        if(iSegment + 1 != len(curvePointList)):
                            del path[-1]
                    path = stripAngle(path, maxAngle = self.stripAngle)
                elif(obj.sliderType == "P"):
                    cPoints = curvePointList
                    cPoints = shortenLength(cPoints, self.ballSize)
                    path = circle_curve(cPoints, int(np.ceil(totalTime / 24.0)))
                elif(obj.sliderType == "L"):
                    path = curvePointList
                    cPoints = shortenLength(path, self.ballSize)
                    path = stripAngle(path, maxAngle = self.stripAngle)
                    path = stripDistance(path, self.stripDistance)
                    path = stripDA(path, self.stripDADist, self.stripDAAngle)
                    ap = np.array((path[0][0], path[0][1]))
                    bp = np.array((path[1][0], path[1][1]))
                else:
                    raise TypeError("Unsupported slider type '%s'" % (obj.sliderType))
                pathLength = 0.0
                rPath = []
                for iRepeat in range(obj.repeat):
                    if(iRepeat % 2 == 0):
                        rPath += list(path[1:])
                        for iCPoint, cPoint in enumerate(path[:-1]):
                            pathLength += pointDistance(cPoint, path[iCPoint + 1])
                    else:
                        rPath += list(path[::-1][1:])
                        for iCPoint, cPoint in enumerate(path[::-1][:-1]):
                            pathLength += pointDistance(cPoint, path[::-1][iCPoint + 1])
                pathDeltaTime = []
                pathTime = pathLength / (100 * beatMap.sliderMultiplier * beatMap.svmAt(obj.time)) * beatMap.mpbAt(obj.time)
                if(iObj + 1 != len(beatMap.hitObjects)):
                    totalTime = np.min((totalTime, beatMap.hitObjects[iObj + 1].time - obj.time - 2))
                for iRepeat in range(obj.repeat):
                    if(iRepeat % 2 == 0):
                        for iCPoint, cPoint in enumerate(path[0:-1]):
                            if(obj.pixelLength >= self.stopSliderLength):
                                pathDeltaTime.append(pointDistance(cPoint, path[iCPoint + 1]) / pathLength * totalTime)
                            else:
                                pathDeltaTime.append(totalTime / obj.repeat / 2)
                    else:
                        for iCPoint, cPoint in enumerate(path[::-1][0:-1]):
                            if(obj.pixelLength >= self.stopSliderLength):
                                pathDeltaTime.append(pointDistance(cPoint, path[::-1][iCPoint + 1]) / pathLength * totalTime)
                            else:
                                pathDeltaTime.append(totalTime / obj.repeat / 2)
                for time in pathDeltaTime:
                    timeList.append(timeList[-1] + time)
                pointList += rPath
                if(obj.pixelLength < self.stopSliderLength):
                    timeList.append(obj.time + totalTime)
                    pointList.append(randomizePoint((obj.x, obj.y), 32 / beatMap.circleSize * self.locNoiseSigmaFac))
            elif(type(obj) is BMReader.Spinner):
                if(iObj + 1 == len(beatMap.hitObjects)):
                    oEndTime = obj.endTime + 500
                else:
                    oEndTime = obj.endTime
                timeRange = np.linspace(obj.time, oEndTime, int(round((oEndTime - obj.time) / 10)))
                cplxPoint = complex(*pointList[-1])
                beginMagn = np.abs(cplxPoint)
                beginPhase = np.angle(cplxPoint)
                accDoneTime = obj.time + self.spinPhaseSpeed / self.spinPhaseAcceleration
                deAccBeginTime = oEndTime - self.spinPhaseSpeed / (self.spinPhaseAcceleration * 0.8)
                if(accDoneTime >= (obj.time + oEndTime) / 2):
                    accDoneTime = obj.time + (oEndTime - obj.time) * 0.4
                if(deAccBeginTime <= (obj.time + oEndTime) / 2):
                    deAccBeginTime = obj.time + (oEndTime - obj.time) * 0.3
                if(len(pointList) >= 2):
                    lastSpeed = (timeList[-1] - timeList[-2]) / pointDistance(pointList[-1], pointList[-2])
                else:
                    lastSpeed = 10
                sqx = [obj.time, accDoneTime, deAccBeginTime, oEndTime]
                sqy = [lastSpeed * 2 * np.pi * self.spinMagn, self.spinPhaseSpeed, self.spinPhaseSpeed, self.spinPhaseSpeed * 0.8]
                speedQuery = ipl.PchipInterpolator(sqx, sqy)
                phase = np.zeros(timeRange.shape)
                phase[0] = beginPhase
                for iTime in range(len(timeRange[1:])):
                    iTime += 1
                    speed = speedQuery(timeRange[iTime]) + np.random.normal(0, self.spinPhaseUnstable)
                    phase[iTime] = phase[iTime - 1] - (timeRange[iTime] - timeRange[iTime - 1]) / speed * 2 * np.pi
                if(len(phase) > 32):
                    noise = np.random.normal(0, self.spinMagnNoise / 3, int(len(phase) / 8))
                    noise = ipl.interp1d(np.linspace(obj.time, oEndTime, len(phase) / 8), noise, fill_value = noise[-1], kind = 'cubic')(timeRange)
                    x = (self.spinMagn + noise) * np.cos(phase)
                    y = (self.spinMagn + noise) * np.sin(phase)
                else:
                    x = self.spinMagn * np.cos(phase)
                    y = self.spinMagn * np.sin(phase)
                x *= np.random.uniform(1.0 - self.spinShapeNoise, 1.0 + self.spinShapeNoise)
                y *= np.random.uniform(1.0 - self.spinShapeNoise, 1.0 + self.spinShapeNoise)
                for iPoint in range(1, len(phase)):
                    timeList.append(timeRange[iPoint])
                    pointList.append((realObjLoc[0] + x[iPoint], realObjLoc[1] + y[iPoint]))
            # long space hit
            if(iObj + 1 != len(beatMap.hitObjects)):
                nextObj = beatMap.hitObjects[iObj + 1]
                nLoc = complex(nextObj.x, nextObj.y)
                cLoc = complex(realObjLoc[0], realObjLoc[1])
                tVec = nLoc - cLoc
                if(nextObj.time - timeList[-1] > self.longSpaceHitTime):
                    transHelix = abs(np.random.normal(0.0, 1.0)) > 3.0
                    if(transHelix):
                        totalTime = min(600, ((nextObj.time - timeList[-1]) + self.longSpaceHitTime) * 0.25)
                        t = np.arange(1, 17) / 16
                        timeRange = timeList[-1] + t * totalTime
                        loc = cLoc + t * tVec * 0.5
                        beginPhase = np.angle(tVec)
                        phase = beginPhase - t * 2 * np.pi
                        x = loc.real + self.transHelixMagn * np.cos(phase)
                        y = loc.imag + self.transHelixMagn * np.sin(phase)
                        for iPoint in range(len(x)):
                            timeList.append(timeRange[iPoint])
                            pointList.append((x[iPoint], y[iPoint]))
                        print("Helix Applied")
                if(nextObj.time - timeList[-1] > self.longSpaceHitTime * 0.75):
                    timeList.append(nextObj.time - self.longSpaceHitTime * 0.6)
                    pointList.append(randomizePoint((nLoc.real, nLoc.imag), 32 / beatMap.circleSize * 1.6 * self.locNoiseSigmaFac))
        i = 1
        while(i < len(timeList)):
            if(timeList[i] - timeList[i - 1] <= 0.0):
                del timeList[i]
                del pointList[i]
            else:
                i += 1

        if((np.diff(timeList) <= 0).any()):
            print("!!!!!!!!!!!!! %d" % (iObj))
            print(type(obj))
            print("Prev:", type(beatMap.hitObjects[iObj - 1]))
            print(obj)
            pl.plot(timeList)
            pl.show()
            sys.exit()
        # short drop
        iPoint = 1
        nDropped = 0
        while True:
            if(iPoint >= len(pointList)):
                break
            pDist = pointDistance(pointList[iPoint], pointList[iPoint - 1])
            tDist = timeList[iPoint] - timeList[iPoint - 1]
            if((pDist < self.dropDistance) and (pDist / tDist > self.dropSpeed)):
                del pointList[iPoint]
                del timeList[iPoint]
                nDropped += 1
                iPoint = 1
            iPoint += 1
        print("Dropped %d, Now %d" % (nDropped, len(pointList)))
        timeList = np.asarray(timeList)
        pointList = np.asarray(pointList)
        need = np.concatenate((np.diff(timeList) > 0, (True,)))
        timeList = timeList[need]
        pointList = np.asarray((pointList.T[0][need], pointList.T[1][need])).T
        print(np.min(np.diff(timeList)))
        timeRange = np.arange(beginTime, endTime, self.reportRate)
        #o = ipl.interp1d(timeList, pointList, axis = 0, kind='linear', bounds_error = False, fill_value = pointList[0])(timeRange)
        o = ipl.Akima1DInterpolator(timeList, pointList, axis = 0)(timeRange)
        nGDither = int(len(o) / 128)
        gDither = np.random.normal(0.0, 32 / beatMap.circleSize / 3 * self.globalDitherSigma, (nGDither, 2))
        gDither = ipl.Akima1DInterpolator(np.arange(nGDither) / (nGDither - 1), gDither, axis = 0)(np.arange(len(o)) / (len(o) - 1))
        o += gDither
        return timeRange, o
