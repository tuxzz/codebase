import numpy as np
import scipy.signal as sp
import pylab as pl
import remover
from common import *

sr, x = loadWav("x.wav")
sr, y = loadWav("y.wav")
rm = remover.Processor(sr)
x, y = x.T[0], y.T[0]
rm(x, y)
