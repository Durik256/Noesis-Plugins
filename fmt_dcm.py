#by Durik256 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Team6",".dcm")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    bs = NoeBitStream(data)
    if noeAsciiFromBytes(bs.readBytes(3)) !='DC2':
        return 0
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(55)
    vnum = bs.readInt()
    bs.seek(5,1)
    stride = bs.readInt()
    vbuf = bs.readBytes(vnum*stride)
    inum = bs.readInt()
    ibuf = bs.readBytes(inum*4)
    
    ctx = rapi.rpgCreateContext()
    
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, stride)
    rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, 12)
    rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, 24) 
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_INT, inum, noesis.RPGEO_TRIANGLE)
    
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default','')]))
    mdlList.append(mdl)
    return 1