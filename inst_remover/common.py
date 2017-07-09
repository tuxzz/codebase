import numpy as np
import scipy.io.wavfile as wavfile

def genSegments(data, dbg = False):
    segments = []
    if(data[0] > 0.0):
        segments.append(0)
    if(data.dtype == np.bool):
        for iHop in range(1, len(data)):
            if(data[iHop - 1] == False and data[iHop] == True):
                segments.append(iHop)
            elif(data[iHop] == False and data[iHop - 1] == True):
                segments.append(iHop)
    else:
        for iHop in range(1, len(data)):
            if(data[iHop - 1] <= 0 and data[iHop] > 0):
                segments.append(iHop)
            elif(data[iHop] <= 0 and data[iHop - 1] > 0):
                segments.append(iHop)
    if(len(segments) % 2):
        segments.append(len(data))
    segments = np.array(segments).reshape((len(segments) / 2, 2))
    return segments

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

def getFrame(input, center, size):
    out = np.zeros((size), input.dtype)
    
    outBegin, outEnd, inputBegin, inputEnd = getFrameRange(len(input), center, size)
    
    out[outBegin:outEnd] = input[inputBegin:inputEnd]
    return out

def getNFrame(inputSize, hopSize):
    return int(inputSize / hopSize + 1 if(inputSize % hopSize != 0) else inputSize / hopSize)

def roundUpToPowerOf2(v):
    return int(2 ** np.ceil(np.log2(v)))

def parabolicInterpolation(input, i, val = True):
    lin = len(input)
    
    ret = 0.0
    if(i > 0 and i < lin - 1):
        s0 = float(input[i - 1])
        s1 = float(input[i])
        s2 = float(input[i + 1])
        a = (s0 + s2) / 2.0 - s1
        if(a == 0):
            return (i, input[i])
        b = s2 - s1 - a
        adjustment = -(b / a * 0.5)
        if(abs(adjustment) > 1.0):
            adjustment = 0.0
        x = i + adjustment
        if(val):
            y = a * adjustment * adjustment + b * adjustment + s1
            return (x, y)
        else:
            return x
    else:
        x = i
        if(val):
            y = input[x]
            return (x, y)
        else:
            return x

def lerp(v0, v1, ratio):
    return v0 + (v1 - v0) * ratio