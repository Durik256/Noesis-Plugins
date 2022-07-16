#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("GUILTY GEAR 2 OVERTURE", ".afb")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    if data.find(b'VRTB') == -1:
        return 0
    return 1
	
def noepyLoadModel(bs, mdlList):
    v_offset = bs.find(b'VRTB') + 4
    i_offset = bs.find(b'PIDX') + 8
    
    bs = NoeBitStream(bs)
    ctx = rapi.rpgCreateContext()
    
    bs.seek(v_offset)
    VBUF = bs.readBytes(bs.readInt())
    
    bs.seek(i_offset)
    IBUF = [bs.readUShort() for x in range (bs.readInt()//2)]
    stride = len(VBUF)//(max(IBUF)+1)
    IBUF = struct.pack('%iH' % len(IBUF), *IBUF)
    
    rapi.rpgBindPositionBuffer(VBUF, noesis.RPGEODATA_FLOAT, stride)
    #rapi.rpgBindUV1BufferOfs(VBUF, noesis.RPGEODATA_FLOAT, stride, stride-12)
    rapi.rpgCommitTriangles(IBUF, noesis.RPGEODATA_USHORT, len(IBUF)//2, noesis.RPGEO_TRIANGLE_STRIP)
    
    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    mdl = rapi.rpgConstructModel()
    mdlList.append(mdl)
    return 1