#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Reckless Racing", ".sggr")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    if data[:4] != b'\x4D\x3C\x2B\x1A':
        return 0
    return 1   
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    ofs_res = data.find(b'#RES')
    if ofs_res != -1:
        bs.seek(ofs_res+44)
        unk, vnum, zero = bs.read('3I') # if unk == 4368 stride 36, if unk == 4352 stride 24
        skip = 12 if unk == 4368 else 0
        vbuf = b''#bs.read(vnum*24)
        for x in range(vnum):
            bs.seek(2,1)
            vbuf += bs.read(2)
            bs.seek(2,1)
            vbuf += bs.read(2)
            bs.seek(2,1)
            vbuf += bs.read(2)
            bs.seek(12+skip,1)
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_SHORT, 6)
        u0, inum, u1 = bs.read('3I')
        ibuf = bs.read(inum*2)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
    try:
        mdlList.append(rapi.rpgConstructModel())
    except:
        mdlList.append(NoeModel())
    return 1
