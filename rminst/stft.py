import numpy as np
import scipy.signal as sp

from common import *

class Processor:
    def __init__(self, sr, **kwargs):
        self.samprate = float(sr)
        self.hopSize = kwargs.get("hopSize", roundUpToPowerOf2(self.samprate * 0.005))
        self.olaFac = int(kwargs.get("olaFac", 2))

    def analyze(self, x):
        assert(self.olaFac > 0)
        # constant
        nX = len(x)
        nHop = getNFrame(nX, self.hopSize)
        nFrame = nHop * self.olaFac
        nBin = self.hopSize + 1
        windowFunc, B, windowMean = getWindow("hanning")

        windowSize = 2 * self.hopSize
        halfWindowSize = self.hopSize
        window = np.sqrt(windowFunc(windowSize))
        windowNormFac = 2.0 / (windowMean * windowSize)

        # do calculate
        magnList = np.zeros((nFrame, nBin), dtype = np.float64)
        phaseList = np.zeros((nFrame, nBin), dtype = np.float64)
        for iFrame in range(nFrame):
            frame = getFrame(x, iFrame * self.hopSize // self.olaFac, windowSize)
            frame *= window

            tSig = np.zeros(windowSize, dtype = np.float64)
            tSig[:halfWindowSize] = frame[halfWindowSize:]
            tSig[-halfWindowSize:] = frame[:halfWindowSize]
            fSig = np.fft.rfft(tSig)
            magnList[iFrame] = np.abs(fSig) * windowNormFac
            phaseList[iFrame] = np.unwrap(np.angle(fSig))
        return magnList, phaseList

    def synth(self, *args):
        # constant
        nFrame, nBin = args[0].shape
        nHop = nFrame // self.olaFac
        nOut = nHop * self.hopSize

        windowFunc, B, windowMean = getWindow("hanning")
        windowSize = 2 * self.hopSize
        halfWindowSize = self.hopSize
        window = np.sqrt(windowFunc(windowSize))

        # check input
        assert(nBin == self.hopSize + 1)

        # synth
        out = np.zeros(nOut, dtype = np.float64)
        if(len(args) == 1):
            fSigList = args[0]
        elif(len(args) == 2):
            fSigList = magnPhaseToFSig(*args)
        else:
            raise ValueError("Bad input.")

        fSigList *= halfWindowSize
        for iFrame in range(nFrame):
            tSig = np.fft.irfft(fSigList[iFrame])
            ob, oe, ib, ie = getFrameRange(nOut, iFrame * self.hopSize // self.olaFac, windowSize)
            out[ib:ie] += (tSig * window)[ob:oe]
        out /= self.olaFac
        return out
