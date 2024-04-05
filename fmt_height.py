#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Screamer 4x4", ".height")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    noesis.logPopup()
    return 1

def CheckType(data):
    return 1

def LoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    bs = NoeBitStream(data)
    
    w,h = 256, 256
    
    vbuf, uvbuf = b'', b''
    for y in range(h):
        for x in range(w):
            vbuf += NoeVec3([x,bs.readUByte()/16,y]).toBytes()
            uvbuf += NoeVec3([x/w,y/h,0]).toBytes()
            
    ibuf = b''
    for y in range(h-1):
        for x in range(w-1):
            ibuf += noePack('4I', x+(y*w), (x+1)+(y*w), x+((y+1)*w), (x+1)+((y+1)*w))
            
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
    rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 12)
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_UINT, len(ibuf)//4, noesis.RPGEO_QUAD)

    rapi.rpgOptimize()
    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default','')]))
    mdlList.append(mdl)
    return 1