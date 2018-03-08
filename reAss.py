import os
import re

assM = r'^灼眼的夏娜 S \((\d+)\)\.ass$'
vidM = r'^\[philosophy-raws\]\[Shakugan no Shana S\]\[OVA(\d+)\]\[BDRIP\]\[Hi10P FLAC\]\[1920X1080\]\.mkv$'

assD = r'\\192.168.1.2\Downloads\[philosophy-raws][Shakugan no Shana]\[philosophy-raws][Shakugan no Shana S]'
vidD = r'\\192.168.1.2\Downloads\[philosophy-raws][Shakugan no Shana]\[philosophy-raws][Shakugan no Shana S]'

assM = re.compile(assM)
vidM = re.compile(vidM)

chapter = {}

for r, d, f in os.walk(vidD):
    for fn in f:
        mat = vidM.match(fn)
        if(mat):
            chapter[int(mat.group(1))] = os.path.splitext(fn)[:-1]

nOp = 0

for r, d, f in os.walk(assD):
    for fn in f:
        mat = assM.match(fn)
        if(mat):
            if(int(mat.group(1)) in chapter):
                print(fn, "->", "%s.ass" % (chapter[int(mat.group(1))]))
                nOp += 1
                os.rename(os.path.join(assD, fn), os.path.join(assD, "%s.ass" % (chapter[int(mat.group(1))])))
print("Renamed:", nOp)