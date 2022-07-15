#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("The Hobbit", ".rgeom")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    if data[:4] != b'\xD1\x07\x00\x00':
        return 0
    return 1
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    bs.seek(130)
    
    stride = bs.readInt()
    bs.seek(8,1)
    
    v_size = bs.readInt()
    bs.seek(4,1)
    
    VBUF = bs.readBytes(v_size)
    
    bs.seek(20,1)
    bs.seek(bs.readInt()+4,1)
    
    bs.seek(20,1)
    
    i_num, i_size = bs.readInt(), bs.readInt()
    bs.seek(16,1)
    
    IBUF = bs.readBytes(i_size)
    
    rapi.rpgBindPositionBuffer(VBUF, noesis.RPGEODATA_FLOAT, stride)
    rapi.rpgBindUV1BufferOfs(VBUF, noesis.RPGEODATA_FLOAT, stride, 24)
    rapi.rpgCommitTriangles(IBUF, noesis.RPGEODATA_SHORT, i_num, noesis.RPGEO_TRIANGLE_STRIP)
    
    mdl = rapi.rpgConstructModel()
    mdlList.append(mdl)
    return 1