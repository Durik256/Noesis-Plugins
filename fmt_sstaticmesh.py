#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Dawn light",".sstaticmesh")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    if data[:4] == 'SATN':
        return 0
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(8)
    name = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
    
    vnum = bs.readInt()
    
    vbuf = bs.readBytes(vnum*24)
    
    numUVS = bs.readInt()
    uvbufs = []
    for x in range(numUVS):
        uvnum = bs.readInt()
        uvbufs.append(bs.readBytes(uvnum*8))
    
    inum = bs.readInt()
    ibuf = bs.readBytes(inum*2)
    
    ctx = rapi.rpgCreateContext()
    
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 24)
    rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 24, 12)
    
    if len(uvbufs) > 0:
        rapi.rpgBindUV1Buffer(uvbufs[0], noesis.RPGEODATA_FLOAT, 8) 
    if len(uvbufs) > 1:
        rapi.rpgBindUV2Buffer(uvbufs[1], noesis.RPGEODATA_FLOAT, 8)
    
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
    
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default', '')]))
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 90 90")
    return 1