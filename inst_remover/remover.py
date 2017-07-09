import numpy as np
import scipy.signal as sp
import pylab as pl
from common import *

def getMP(s):
    f = np.fft.rfft(s)
    return np.abs(f), np.angle(f)

def cmbMP(m, p):
    f = np.zeros(len(m), dtype = np.complex128)
    f.real = np.cos(p) * m
    f.imag = np.sin(p) * m
    return np.fft.irfft(f)

class Processor:
    def __init__(self, sr):
        self.samprate = sr
        self.hopSize = roundUpToPowerOf2(self.samprate * 0.005)
        self.adjustRadius = 32#roundUpToPowerOf2(self.samprate * 0.005)
        self.adjustWindowRadius = roundUpToPowerOf2(self.samprate * 0.005)
        self.ref = 3.531

    def __call__(self, x, y):
        nX = len(x)
        nHop = getNFrame(nX, self.hopSize)
        ref = [(int(26.0 * self.samprate), 1.0)]
        # adjustment
        frameSize = self.adjustWindowRadius * 2
        bestOffset = 0
        bestRes = np.inf
        if(self.adjustRadius):
            ir = range(-self.adjustRadius, self.adjustRadius)
        else:
            ir = [0]
        for offset in ir:
            resEnergy = 0.0
            for iRef, (iSample, weight) in enumerate(ref):
                xFrame = getFrame(x, iSample, frameSize)
                yFrame = getFrame(y, iSample + offset, frameSize)
                resEnergy += np.sum((xFrame - yFrame) ** 2) * weight
            if(resEnergy < bestRes):
                bestOffset = offset
                bestRes = resEnergy
        del offset, frameSize, iRef, iSample, weight, xFrame, yFrame, resEnergy, ir
        y = getFrame(y, bestOffset, nX * 2)[nX:]
        print("bestOffset =", bestOffset)

        # normalization
        ref = self.ref[0][0] if type(self.ref) is list else self.ref
        iRefCenter = int(ref * self.samprate)
        xFrame = getFrame(x, iRefCenter, self.adjustWindowRadius)
        yFrame = getFrame(y, iRefCenter, self.adjustWindowRadius)
        normFac = np.sqrt(np.sum(xFrame ** 2) / np.sum(yFrame ** 2))
        y *= normFac
        print("NormFac =", normFac)
        # short time subtract
        out = np.zeros(nX)
        frameSize = self.hopSize * 2
        window = np.sqrt(sp.hanning(frameSize))
        olaFac = 4
        for iFrame in range(nHop * olaFac):
            iHop = iFrame / olaFac
            xFrame = getFrame(x, int(iHop * self.hopSize), frameSize) * window
            yFrame = getFrame(y, int(iHop * self.hopSize), frameSize) * window
            xm, xp = getMP(xFrame)
            ym, yp = getMP(yFrame)
            nm = np.clip(xm - ym, 0, np.inf)
            s = cmbMP(nm, xp)
            #s = xFrame - yFrame
            ob, oe, ib, ie = getFrameRange(nX, int(iHop * self.hopSize), frameSize)
            out[ib:ie] += (s * window)[ob:oe]
        out /= olaFac
        saveWav("out.wav", out, self.samprate)
