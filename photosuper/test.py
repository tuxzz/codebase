import numpy as np
import os, cv2

buf = np.zeros((720, 1280, 3), dtype = np.float64)
nPic = 0
for root, dirList, fileList in os.walk("./src"):
    for fileName in fileList:
        print(fileName)
        path = os.path.join(root, fileName)
        img = cv2.imread(path).astype(np.float64)
        buf += img
        nPic += 1
del img
buf /= nPic
cv2.imwrite("out.hdr", buf)
