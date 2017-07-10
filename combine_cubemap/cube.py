import numpy as np
import png
import os

w, h = 1024, 1024
nPlane = 3
bitDepth = 16
nFrame = 60
srcDir = "./work/img"
outDir = "./work/out"
digit = 4

assert(digit > 0 and digit < 10)
fStr = "%s_%0" + str(digit) + "d.png"

orderList = (
    ("NADIR", "ZENITH", "SOUTH"),
    ("WEST", "NORTH", "EAST"),
)
orderListShapeW, orderListShapeH = 3, 2

if(bitDepth == 16):
    dtype = np.uint16
elif(bitDepth == 8):
    dtype = np.uint8
else:
    assert False, "Unsupported bitDepth."

def loadPng(path):
    reader = png.Reader(path)
    pngData = reader.read()
    w, h = pngData[0], pngData[1]
    pixelData = np.vstack(map(dtype, pngData[2]))
    nPlane = pngData[3]["planes"]
    return pixelData.reshape(pixelData.shape[0], pixelData.shape[1] // nPlane, nPlane), pngData[3]

def savePng(data, info, path):
    d = data.reshape(data.shape[0], data.shape[1] * info["planes"])
    with open(path, "wb") as f:
        size = info["size"]
        writer = png.Writer(**info)
        writer.write(f, d)

out = np.zeros((h * orderListShapeH, w * orderListShapeW, nPlane), dtype = dtype)
print("Output shape = %s" % str(out.shape))
outInfo = {
    'greyscale': True if(nPlane == 1) else False, 
    'alpha': False, 
    'planes': nPlane, 
    'bitdepth': bitDepth, 
    'interlace': 0, 
    'size': (orderListShapeW * w, orderListShapeH * h)
}
for iFrame in range(1, nFrame + 1):
    print("Frame %d" % iFrame)
    for iLine, lineList in enumerate(orderList):
        for iElem, elem in enumerate(lineList):
            print("  =>%s" % str(elem))
            if(elem is None):
                continue
            elif(isinstance(elem, str)):
                data, info = loadPng(os.path.join(srcDir, fStr % (elem, iFrame)))
                out[iLine * h:(iLine + 1) * h, iElem * w:(iElem + 1) * w,:] = data
            else:
                assert False, "Invalid orderList element."
    del data
    print("  Output...")
    savePng(out, outInfo, "%s/%d.png" % (outDir, iFrame))