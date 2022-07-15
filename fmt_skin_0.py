#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Cabela's outdoor adventures 2006", ".skin")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    if data[:4] != b'FBSF':
        return 0
    return 1
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    bs.seek(51)
    bs.seek(bs.readByte() + 1,1)#path
    print(bs.getOffset())
    
    for x in range(bs.readShort()):#mt
        bs.seek(bs.readByte(),1)
    
    for x in range(bs.readShort()):
        name = bs.readBytes(bs.readByte())

    bs.seek(21,1)
    
    for x in range(bs.readShort()):
        rapi.rpgSetName('mesh_%i' % x)
        bs.seek(bs.readByte() + 6,1)

        num_bones = bs.readShort()
        for x in range(num_bones):
            bname = bs.readBytes(bs.readByte())

        v_num = bs.readShort()
        bs.seek(4,1)
        VBUF = bs.readBytes(v_num*36)

        type = bs.readShort()
        tri_type = noesis.RPGEO_TRIANGLE if type == 4 else noesis.RPGEO_TRIANGLE_STRIP

        i_num = bs.readShort()
        IBUF = bs.readBytes(i_num*2)

        
        bs.seek(num_bones*24,1)
        if num_bones > 1:
            bs.seek(v_num*8,1)
            bs.seek(bs.readShort()*8,1)

        rapi.rpgBindPositionBuffer(VBUF, noesis.RPGEODATA_FLOAT, 36)
        rapi.rpgBindUV1BufferOfs(VBUF, noesis.RPGEODATA_FLOAT, 36, 28)
        rapi.rpgCommitTriangles(IBUF, noesis.RPGEODATA_USHORT, i_num, tri_type)
    
    mdl = rapi.rpgConstructModel()
    mdlList.append(mdl)
    return 1