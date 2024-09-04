#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Cyber Hunter", ".mesh")
    noesis.setHandlerTypeCheck(handle, animCheckType)
    noesis.setHandlerLoadModel(handle, animLoadModel)
    return 1

def animCheckType(data):
    return 1

def animLoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    bs = NoeBitStream(data)
    bs.seek(88)
    
    x = bs.read('25I')
    print(x)
    bs.seek(x[17])
    buf = bs.read(x[14]*12)
    rapi.rpgBindPositionBuffer(buf, noesis.RPGEODATA_FLOAT, 12)

    if x[20]:
        bs.seek(x[20])
        buf = bs.read(x[14]*8)
        rapi.rpgBindUV1Buffer(buf, noesis.RPGEODATA_FLOAT, 8)
    
    bs.seek(x[23])
    buf = bs.read(x[15]*12)
    rapi.rpgCommitTriangles(buf, noesis.RPGEODATA_UINT, x[15]*3, noesis.RPGEO_TRIANGLE)
    
    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    try:
        mdlList.append(rapi.rpgConstructModel())
    except:
        mdlList.append(NoeModel())
    return 1