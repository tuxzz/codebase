import numpy as np
import scipy.signal as sp
import scipy.interpolate as ipl
import stft
import pylab as pl
from common import *

class Processor:
    def __init__(self, sr, instrumentalRange, **kwargs):
        self.samprate = sr
        self.instrumentalRange = list(instrumentalRange)

        self.hopSize = kwargs.get("hopSize", roundUpToPowerOf2(self.samprate * 0.005))
        self.olaFac = kwargs.get("olaFac", 2)

        self.alignmentSearchRange = kwargs.get("alignmentSearchRange", int(self.samprate * 3))
        self.alignmentCompareRange = kwargs.get("alignmentCompareRange", roundUpToPowerOf2(self.samprate * 0.1))
        self.method = kwargs.get("method", "stft-magn")

    def __call__(self, x, y):
        assert(self.alignmentSearchRange >= 0)
        assert(self.alignmentCompareRange >= 0)
        assert(len(self.instrumentalRange) > 0)

        nX = len(x)
        nHop = getNFrame(nX, self.hopSize)
        nFrame = nHop * self.olaFac
        nBin = self.hopSize + 1

        print("Phase 1: Align...")
        if(self.alignmentSearchRange > 0):
            bestOffset = 0
            bestResidualEnergy = np.inf
            refPoints = [int((begin + end) / 2 * self.samprate) for begin, end in self.instrumentalRange]
            for offset in range(-self.alignmentSearchRange, self.alignmentSearchRange + 1):
                residualEnergy = 0.0
                for iRef, iSample in enumerate(refPoints):
                    xFrame = getFrame(x, iSample, self.alignmentCompareRange)
                    yFrame = getFrame(y, iSample + offset, self.alignmentCompareRange)
                    residualEnergy += np.sum((xFrame - yFrame) ** 2)
                if(residualEnergy < bestResidualEnergy or (abs(residualEnergy - bestResidualEnergy) < 1e-6 and abs(offset) < abs(bestOffset))):
                    bestOffset = offset
                    bestResidualEnergy = residualEnergy
            y = getFrame(y, bestOffset, nX * 2)[nX:]
            print("bestOffset = %d" % (bestOffset,))

        print("Simple normalization...")
        instrumentalSamples = [(int(v * self.samprate) for v in r) for r in self.instrumentalRange]
        meanNormFac = 0.0
        for begin, end in instrumentalSamples:
            need = y[begin:end] != 0
            meanNormFac += np.mean(x[begin:end][need] / y[begin:end][need])
        meanNormFac /= len(instrumentalSamples)
        y *= meanNormFac
        print("meanNormFac = %f" % (meanNormFac,))

        if(self.method == "simple"):
            return x - y
        
        if(len(self.method) > 4 and self.method[:4] == "stft"):
            print("Do STFT...")
            stftProcessor = stft.Processor(self.samprate, hopSize = self.hopSize, olaFac = self.olaFac)
            xMagnList, xPhaseList = stftProcessor.analyze(x)
            yMagnList, yPhaseList = stftProcessor.analyze(y)
            xMagnList, yMagnList = np.log(np.clip(xMagnList, 1e-8, np.inf)), np.log(np.clip(yMagnList, 1e-8, np.inf))

            print("Phase 2: Gen inverse-filter...")
            xEnvList = np.zeros((nFrame, nBin), dtype = np.float64)
            yEnvList = np.zeros((nFrame, nBin), dtype = np.float64)
            filterList = np.zeros((nFrame, nBin), dtype = np.float64)
            instrumentalFrames = [tuple(int(v * self.samprate / self.hopSize * self.olaFac) for v in r) for r in self.instrumentalRange]
            for iSegment, (begin, end) in enumerate(instrumentalFrames):
                need = yMagnList[begin:end] != 0
                for iFrame in range(begin, end):
                    xEnvList[iFrame] = calcTrueEnvelope(xMagnList[iFrame], int(round(48 / 44100 * self.samprate)))
                    yEnvList[iFrame] = calcTrueEnvelope(yMagnList[iFrame], int(round(48 / 44100 * self.samprate)))
                filterList[begin:end] = xEnvList[begin:end] - yEnvList[begin:end]
                if(iSegment == 0):
                    filterList[:begin] = filterList[begin]
                elif(iSegment == len(instrumentalFrames) - 1):
                    filterList[end:] = filterList[end - 1]
                if(iSegment != 0):
                    lastBegin, lastEnd = instrumentalFrames[iSegment - 1]
                    iplRange = (np.arange(begin - lastEnd) + 1) / (begin - lastEnd + 1)
                    filterList[lastEnd:begin] = ipl.interp1d((0, 1), (filterList[lastEnd - 1], filterList[begin]), kind = "linear", axis = 0)(iplRange)
            del xEnvList, yEnvList

            print("Phase 3: Subtract and ISTFT...")
            xMagnList, yMagnList = np.exp(xMagnList), np.exp(yMagnList)
            if(self.method == "stft-fsig"):
                need = yMagnList > xMagnList
                yMagnList[need] = xMagnList[need]
                subtractFSigList = magnPhaseToFSig(xMagnList, xPhaseList) - magnPhaseToFSig(yMagnList, yPhaseList)
                return stftProcessor.synth(xMagnList, xPhaseList)
            elif(self.method == "stft-magn"):
                return stftProcessor.synth(np.clip(xMagnList - yMagnList, 0.0, np.inf), xPhaseList)
        elif(method == "simple"):
            return x - y
        raise ValueError("Bad method")
