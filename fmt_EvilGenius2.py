#by Durik256
#change ext to *.EG2WD in your file
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Evil Genius 2: World Domination", ".EG2WD")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    return 1   

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    h = bs.read('14I6f')
    vbuf = bs.read(h[1]*48)
    ibuf = bs.read(h[3]*6)
        
    rapi.rpgSetPosScaleBias(NoeVec3(h[14:17]),None)
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_USHORT, 48)
    rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_HALFFLOAT, 48, 24)
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, h[3]*3, noesis.RPGEO_TRIANGLE)
    
    mdl = rapi.rpgConstructModel()
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 -90 -90")
    return 1
