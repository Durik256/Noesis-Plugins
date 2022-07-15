#by Durik256 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Diablo Immortal", ".model")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    if data[:4] != b'MODL':
        return 0
    return 1   
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    while bs.getOffset() < bs.getSize():
        label, size, curPos = bs.readBytes(4), bs.readInt(), bs.getOffset()

        if label == b'MESH':
            bs.seek(18, 1)
            submesh, vnum, inum = bs.readUShort(), bs.readUInt(), bs.readUInt()
            
            attrib = [bs.readBytes(bs.readUShort()) for x in range(4)]
            uv_stride = 12 if attrib[1] == b'Q4H_T2H' else 16
                
            bs.seek(40, 1)
            
            for x in range(submesh):
                print([bs.readInt() for x in range(4)])
                    
            ibuf = bs.readBytes(inum*2)
            vbuf = bs.readBytes(vnum*12)
            uvbuf = bs.readBytes(vnum*uv_stride)
                
            rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
            rapi.rpgBindUV1BufferOfs(uvbuf, noesis.RPGEODATA_HALFFLOAT, uv_stride, 8)
            if uv_stride > 12:
                rapi.rpgBindUV2BufferOfs(uvbuf, noesis.RPGEODATA_HALFFLOAT, uv_stride, 12)
            rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
            bs.seek(curPos+size)
        else:
            bs.seek(size, 1)
    
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([],[NoeMaterial('mat0','')]))
    mdlList.append(mdl)
    return 1