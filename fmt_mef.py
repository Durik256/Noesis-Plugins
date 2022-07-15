#powered by Durik256 for xentax.com
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("IGI", ".mef")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1
    
def noepyCheckType(data):
    bs = NoeBitStream(data)
    if noeAsciiFromBytes(bs.readBytes(4)) != 'ILFF':
        return 0
    return 1
    
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    header = bs.readInt()
    filesize = bs.readInt()
    bs.seek(12, 1)#OCEM
    chanks = []
    
    #read chanks
    while bs.getOffset() < filesize:
        offset = bs.getOffset()
        name = noeAsciiFromBytes(bs.readBytes(4))
        size, param, next = bs.readInt(), bs.readInt(), bs.readInt()
        chanks.append(chank(offset, name, size, next))
        print(chanks[-1])
        if next == 0:
            break
        else:
            bs.seek(next-16, 1)
    
    ctx = rapi.rpgCreateContext()
    
    for c in chanks:
        bs.seek(c.offset+16)
        if c.name == "XTVC" and c.size>0:
            rapi.rpgSetName("mesh_"+str(c.offset))
            vbuf = bs.readBytes(c.size)
            rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 16)
        elif c.name == "ECFC" and c.size>0:
            ibuf = b''
            for x in range(c.size//8):
                ibuf += bs.readBytes(6)
                bs.seek(2,1)
            rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_SHORT, (c.size//8)*3, noesis.RPGEO_TRIANGLE)
            
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
        print("temporarily unsupported!")
    mdlList.append(mdl)
    return 1
    
class chank:    
    def __init__(self, offset, name, size, next):
        self.name = name
        self.offset = offset
        self.size = size
        self.next = next
    
    def __repr__(self):
        return "(chank:" + self.name + ", offset: " + repr(self.offset) + ", size: " + repr(self.size)+ ", next: " + repr(self.next) + ")"