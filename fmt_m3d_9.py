#by Durik256 15.03.2022 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Winter X-Games: Snocross",".m3d")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    bs = NoeBitStream(data)
    if noeAsciiFromBytes(bs.readBytes(3)) != 'M3D':
        return 0
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(64)#HEAD, VBUF
    vSize, unk, vCount = bs.readInt(), bs.readInt(), bs.readInt()
    
    stride = (vSize-8)//vCount
    print(stride)
    vbuf = bs.readBytes(vSize-8)
    
    bs.seek(4,1)#IBUF
    iSize, iCount = bs.readInt(), bs.readInt()
    
    ibuf = bs.readBytes(iSize-4)
    
    ctx = rapi.rpgCreateContext()
    
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, stride)
    if stride > 12:
        rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, 12)
    if stride > 24:
        rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, stride-8) 
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, iCount, noesis.RPGEO_TRIANGLE)
    mdl = rapi.rpgConstructModel()
    
    mdlList.append(mdl)
    #rapi.setPreviewOption("setAngOfs", "0 0 90")
    return 1