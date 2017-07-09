import core
from common import *

wX, sr = loadWav("x.wav")
wY, sr = loadWav("y.wav")

out = None

for iChannel in range(wX.shape[1]):
    print("Ch", iChannel)
    x = wX.T[iChannel]
    y = wY.T[iChannel]

    processor = core.Processor(sr, [(0.208, 0.509), (14.579, 15.031)], method = "simple")
    o = processor(x, y)
    if(out is None):
        out = np.zeros((wX.shape[1], o.shape[0]))
    out[iChannel] = o

saveWav("out.wav", out.T, sr)
