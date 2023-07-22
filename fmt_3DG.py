#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Test Drive Unlimited 1/2", ".3dg")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    if data[12:16] != b'.3DG':
        return 0
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    PRIM = [i for i in findall(b'PRIM', data)]
    
    for x in PRIM:
        bs.seek(x+24)
        ibuf_ofs, vbuf_ofs = bs.read('2I')
        bs.seek(x+48)
        vofs,vnum,iofs,inum = bs.read('4I')
        bs.seek(x+68)
        unk0, unk1 = bs.read('2I')
        
        bs.seek(ibuf_ofs+80)
        ibuf = bs.read(inum*2)
        
        bs.seek(vbuf_ofs+80)
        vbuf = bs.read(vnum*12)
        skip = 0
        if unk0 == 2305: 
            skip += 1
        if unk1 == 513:
            skip += 1
        
        bs.seek(vbuf_ofs+80+(vnum*(12+(skip*4))))
        uvbuf = bs.read(vnum*8)
        
        rapi.rpgSetName('mesh_%i'%x)
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
        rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 8)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE_STRIP)
    
    mdl = rapi.rpgConstructModel()
    mdlList.append(mdl)
    return 1

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)
