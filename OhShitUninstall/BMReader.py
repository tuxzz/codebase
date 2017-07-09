# -*- coding: utf-8 -*-
import re
import sys

headerMatcher = re.compile(r'^osu file format v(\d*)$')
sectionMatcher = re.compile(r'^\[(\w*)\]$')
propertyMatcher = re.compile(r'^(\w*)\s?:\s?(.*)$')

class TypedList(list):
    def __init__(self, v, t):
        super().__init__(v)
        self.valueType = t

class TimePoint:
    typeOrder = (float, float, int, int, int, int, int, int)

    def __init__(self):
        self.offset = 0
        self.mpb = 0.0
        self.meter = 4
        self.sampleType = 2
        self.sampleSet = 0
        self.volume = 60
        self.inherited = False
        self.kiaiMode = False

    def __str__(self):
        return "%d,%f,%d,%d,%d,%d,%d,%d" % (self.offset, self.mpb, self.meter, self.sampleType, self.sampleSet, self.volume, self.inherited, self.kiaiMode)

    def fromStr(self, v):
        self.offset, self.mpb, self.meter, self.sampleType, self.sampleSet, self.volume, self.inherited, self.kiaiMode = [self.typeOrder[i](item.strip()) for i, item in enumerate(v.split(','))]
        self.inherited = bool(self.inherited)
        self.kiaiMode = bool(self.kiaiMode)

def loadsHitObject(hitObjectStr):
    spl = hitObjectStr.split(',')
    tp = int(spl[3])
    if(tp & 1):
        obj = HitCircle()
    elif(tp & 2):
        obj = Slider()
    elif(tp & 8):
        obj = Spinner()
    else:
        raise ValueError("Bad HitObject type.")
    obj.fromStr(hitObjectStr)
    return obj

class HitCircle:
    typeOrder = (int, int, int, int, int, str)

    def __init__(self):
        self.x = 0
        self.y = 0
        self.time = 0
        self.newCombo = False
        self.hitSound = 0
        self.addition = "0:0:0:0:"

    def __str__(self):
        return "%d,%d,%d,%d,%d,%s" % (self.x, self.y, self.time, 1 | (4 if(self.newCombo) else 0), self.hitSound, self.addition)

    def fromStr(self, v):
        spl = v.split(',')
        if(len(spl) == 6):
            self.x, self.y, self.time, tp, self.hitSound, self.addition = [self.typeOrder[i](item.strip()) for i, item in enumerate(spl)]
        elif(len(spl) == 5):
            self.x, self.y, self.time, tp, self.hitSound = [self.typeOrder[i](item.strip()) for i, item in enumerate(spl)]
            self.addition = "0:0:0:0:"
        else:
            raise ValueError("Wrong HitCircle str(Bad length)")
        if(not (tp & 1)):
            raise ValueError("Wrong HitCircle str(Not a HitCircle?)")
        self.newCombo = bool(tp & 4)

class Slider:
    typeOrder = (int, int, int, int, int, str)

    def __init__(self):
        self.x = 0
        self.y = 0
        self.time = 0
        self.newCombo = False
        self.hitSound = 0
        self.sliderType = "B"
        self.curvePointList = []
        self.repeat = 0
        self.pixelLength = 0
        self.addition = "0:0:0:0:"

    def __str__(self):
        sect0 = "%d,%d,%d,%d,%d,%s" % (self.x, self.y, self.time, 2 | (4 if(self.newCombo) else 0), self.hitSound, self.sliderType)
        sect1 = ""
        if(self.sliderType == "B"):
            flatItem = [item for seg in self.curvePointList for item in seg][1:]
        else:
            flatItem = self.curvePointList[1:]
        for iCurve, curve in enumerate(flatItem):
            sect1 += "%d:%d" % (curve[0], curve[1])
            if(iCurve < len(flatItem) - 1):
                sect1 += "|"
        sect2 = "%d,%d" % (self.repeat, self.pixelLength)
        return "%s|%s,%s" % (sect0, sect1, sect2)

    def fromStr(self, v):
        spl = v.split('|')
        self.x, self.y, self.time, tp, self.hitSound, self.sliderType = [self.typeOrder[i](item.strip()) for i, item in enumerate(spl[0].split(','))]
        if(not (tp & 2)):
            raise ValueError("Wrong Slider str(Not a Slider?)")
        spl = spl[1:]
        self.curvePointList = [(self.x, self.y)]
        for i, item in enumerate(spl):
            s = item.split(",")
            pt = s[0].split(":")
            self.curvePointList.append((int(pt[0]), int(pt[1])))
            if(len(s) > 1):
                self.repeat = int(s[1])
                try:
                    self.pixelLength = int(s[2])
                except ValueError:
                    self.pixelLength = int(round(float(s[2])))
                break
        if(self.sliderType == "B"):
            segments = []
            segment = []
            for iItem, item in enumerate(self.curvePointList):
                if(iItem != 0 and item == self.curvePointList[iItem - 1]):
                    segments.append(segment)
                    segment = []
                segment.append(item)
            segments.append(segment)
            self.curvePointList = segments
        elif(self.sliderType == "P"):
            if(len(self.curvePointList) != 3):
                print("Passthrough curve error %d/3. Degeneration to linear." % (len(self.curvePointList)))
                self.sliderType = "L"

class Spinner:
    typeOrder = (int, int, int, int, int, int, str)

    def __init__(self):
        self.x = 0
        self.y = 0
        self.time = 0
        self.newCombo = False
        self.hitSound = 0
        self.endTime = 0
        self.addition = "0:0:0:0:"

    def __str__(self):
        return "%d,%d,%d,%d,%d,%d,%s" % (self.x, self.y, self.time, 8 | (4 if(self.newCombo) else 0), self.hitSound, self.endTime, self.addition)

    def fromStr(self, v):
        spl = v.split(',')
        if(len(spl) == 7):
            self.x, self.y, self.time, tp, self.hitSound, self.endTime, self.addition = [self.typeOrder[i](item.strip()) for i, item in enumerate(spl)]
        elif(len(spl) == 6):
            self.x, self.y, self.time, tp, self.hitSound, self.endTime = [self.typeOrder[i](item.strip()) for i, item in enumerate(spl)]
            self.addition = "0:0:0:0:"
        else:
            raise ValueError("Wrong Spinner str(Bad length)")
        if(not (tp & 8)):
            raise ValueError("Wrong Spinner str(Not a spinner?)")
        self.newCombo = bool(tp & 4)

class Beatmap:
    def __init__(self):
        self.fileVersion = 12
        self.epilepsyWarning = False
        self.audioFileName = ""
        self.audioLeadIn = 2000
        self.previewTime = 10013
        self.countDown = False
        self.sampleSet = "Soft"
        self.stackLeniency = 0.7
        self.mode = 0
        self.letterboxInBreaks = False
        self.widescreenStoryboard = False
        self.bookMarks = TypedList([], int)
        self.distanceSpacing = 1.22
        self.beatDivisor = 4
        self.gridSize = 4
        self.timelineZoom = 1
        self.title = "artcore JINJA"
        self.titleUnicode = "アートコア神社"
        self.artist = "An"
        self.artistUnicode = "An"
        self.creator = "Flower"
        self.version = "Hard"
        self.source = "Touhou"
        self.tags = TypedList([], str)
        self.beatmapID = 297410
        self.beatmapSetID = 114987
        self.hpDrainRate = 5.0
        self.circleSize = 4.0
        self.overallDifficulty = 6.0
        self.approachRate = 7.0
        self.sliderMultiplier = 1.3
        self.sliderTickRate = 1.0
        self.timePoints = []
        self.colours = {}
        self.hitObjects = []
        self.unknownProperties = []

    def svmAt(self, ms):
        for iTP, tp in enumerate(self.timePoints):
            if(iTP + 1 == len(self.timePoints) or (ms >= tp.offset and ms < self.timePoints[iTP + 1].offset)):
                return 1.0 if(tp.mpb > 0) else -100 / tp.mpb
        raise ValueError("Cannot calculate svm.")

    def mpbAt(self, ms):
        mpb = self.timePoints[0].mpb
        for iTP, tp in enumerate(self.timePoints):
            if(iTP + 1 == len(self.timePoints)):
                return mpb if(tp.mpb <= 0) else tp.mpb
            elif(ms >= tp.offset and ms < self.timePoints[iTP + 1].offset):
                return mpb if(tp.mpb <= 0) else tp.mpb
            if(tp.mpb > 0):
                mpb = tp.mpb
        raise ValueError("Cannot calculate mpb.")

    def load(self, path):
        f = open(path, 'rt', encoding='utf8')
        self.loads(f.read())

    def loads(self, s):
        s = s.splitlines()
        header = False
        ignoreEventWarning = False
        section = ""
        sDict = dict(self.__dict__)
        sKeys = list(sDict.keys())
        caseKeys = [k.lower() for k in sKeys]
        for lineNumber, line in enumerate(s):
            if(not line): continue
            if(not header):
                r = headerMatcher.match(line)
                if(not r): raise ValueError("Expect a file header @ line %d" % (lineNumber))
                v = int(r.groups()[0])
                if(v < 0): raise ValueError("Expect a positive integer @ line %d" % (lineNumber))
                self.fileVersion = v
                del v
                header = True
            elif(not section):
                r = sectionMatcher.match(line)
                if(not r): raise ValueError("Expect a section @ line %d" % (lineNumber))
                section = r.groups()[0]
            else:
                r = sectionMatcher.match(line)
                if(r):
                    section = r.groups()[0]
                elif(section == "Events"):
                    if(not ignoreEventWarning): print("WARNING: Ignored Event section(Only show first time). @ line %d" % (lineNumber), file = sys.stderr)
                    ignoreEventWarning = True
                elif(section == "TimingPoints"):
                    tp = TimePoint()
                    tp.fromStr(line)
                    self.timePoints.append(tp)
                elif(section == "Colours"):
                    r = propertyMatcher.match(line)
                    if(not r): raise ValueError("Expect a colour property @ line %d" % (lineNumber))
                    self.colours[r.groups()[0]] = tuple([int(item) for item in r.groups()[1].split(',')])
                elif(section == "HitObjects"):
                    self.hitObjects.append(loadsHitObject(line))
                else:
                    r = propertyMatcher.match(line)
                    if(not r): raise ValueError("Expect a property @ line %d" % (lineNumber))
                    propName = r.groups()[0]
                    propValue = r.groups()[1]
                    try:
                        iProp = caseKeys.index(propName.lower())
                    except ValueError:
                        self.unknownProperties.append((section, propName, propValue))
                        continue
                    propName = sKeys[iProp]
                    origProp = getattr(self, propName)
                    propType = type(origProp)
                    if(propType is TypedList):
                        if(propName.lower() == "tags"):
                            propValue = propValue.split(' ')
                        elif(propName.lower() == "bookmarks"):
                            propValue = propValue.split(',')
                        setattr(self, propName, [origProp.valueType(item.strip()) for item in propValue])
                    elif(propType is int):
                        try:
                            setattr(self, propName, propType(propValue))
                        except ValueError:
                            setattr(self, propName, int(round(float(propValue))))
                    elif(propType is bool):
                        setattr(self, propName, bool(int(propValue)))
                    else:
                        setattr(self, propName, propType(propValue))
        if(self.unknownProperties):
            print("Unknown properties are listed below: ")
            for section, propName, propValue in self.unknownProperties:
                print("[%s]%s: %s" % (section, propName, propValue))
        self.hitObjects.sort(key = lambda x:x.time)
