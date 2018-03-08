#-*- coding: utf-8 -*-
import cv2 as cv
import numpy as np
import scipy.signal as sp
import scipy.interpolate as ipl
import scipy.io.wavfile as wavfile

def loadWav(filename): # -> samprate, wave in float64
    samprate, w = wavfile.read(filename)
    if(w.dtype == np.int8):
        w = w.astype(np.float64) / 128.0
    elif(w.dtype == np.short):
        w = w.astype(np.float64) / 32768.0
    elif(w.dtype == np.int32):
        w = w.astype(np.float64) / 2147483648.0
    elif(w.dtype == np.float32):
        w = w.astype(np.float64)
    elif(w.dtype == np.float64):
        pass
    else:
        raise ValueError("Unsupported sample format: %s" % (str(w.dtype)))
    return samprate, w

def saveWav(filename, data, samprate):
    wavfile.write(filename, samprate, data)

def getFrameRange(inputLen, center, size):
    leftSize = int(size / 2)
    rightSize = size - leftSize # for odd size

    inputBegin = min(inputLen, max(center - leftSize, 0))
    inputEnd = max(0, min(center + rightSize, inputLen))

    outBegin = max(leftSize - center, 0)
    outEnd = outBegin + (inputEnd - inputBegin)

    return outBegin, outEnd, inputBegin, inputEnd

fftSize = 2048
sr = 48000
magnMin = -80.0
magnMax = 0.0

b, g, r = cv.imread("ts.jpg").transpose(2, 0, 1)
v = 0.299 * r + 0.587 * g + 0.114 * b
v = v.T
v /= 255.0
w, h = v.shape
del b, g ,r

fftSize = h if(fftSize is None) else fftSize
x = np.arange(h) / (h - 1)
fftRange = np.arange(fftSize // 2 + 1) / fftSize

out = np.zeros(fftSize * w // 2)
window = np.hanning(fftSize)
basePhase = 0.0
for i in range(w):
    print("%d / %d" % (i, w))
    ob, oe, ib, ie = getFrameRange(len(out), i * (fftSize / 2), fftSize)
    magn = 1.0 - ipl.interp1d(x, v[i], kind='linear')(fftRange[::-1])
    magn = np.power(10, (magn * (magnMax - magnMin) + magnMin) / 20.0)
    magn *= fftSize // 2
    phase = np.linspace(0, 2 * np.pi, fftSize // 2 + 1)
    ffted = np.zeros(fftSize // 2 + 1, dtype = np.complex128)
    ffted.real = magn * np.cos(phase)
    ffted.imag = magn * np.sin(phase)
    out[ib:ie] += (np.fft.irfft(ffted) * window)[ob:oe]

saveWav("out.wav", out, sr)
