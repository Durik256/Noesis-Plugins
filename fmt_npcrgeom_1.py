#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("The Hobbit", ".npcgeom")
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
    
    bs.seek(32)
    num_mdl = bs.readInt()
    bs.seek(20 + num_mdl*24,1)
    print(bs.getOffset())
    i_inf = []
    v_inf = []
    
    for x in range(num_mdl):
        bs.seek(28,1)
        i_size = bs.readInt()
        i_inf.append([bs.getOffset(), i_size])
        bs.seek(i_size,1)
    print(i_inf)
    bs.seek(8,1)
    print(bs.getOffset())
    for x in range(num_mdl):
        bs.seek(8,1)
        stride, skip = bs.readInt(), bs.readInt64()
        v_size, zero = bs.readInt(), bs.readInt()
        v_inf.append([bs.getOffset(), v_size, stride])
        bs.seek(v_size,1)
        
    
    print(v_inf)
    
    for x in range(num_mdl):
        v_offset, v_size, stride = v_inf[x]
        i_offset, i_size = i_inf[x]
    
        bs.seek(v_offset)
        VBUF = bs.readBytes(v_size)
        
        bs.seek(i_offset)
        IBUF = bs.readBytes(i_size)
    
    
        rapi.rpgBindPositionBuffer(VBUF, noesis.RPGEODATA_FLOAT, stride)
        rapi.rpgBindUV1BufferOfs(VBUF, noesis.RPGEODATA_FLOAT, stride, stride-8)
        rapi.rpgCommitTriangles(IBUF, noesis.RPGEODATA_SHORT, i_size//2, noesis.RPGEO_TRIANGLE_STRIP)

        mdl = rapi.rpgConstructModel()
        mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 90 90")
    return 1