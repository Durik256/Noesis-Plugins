#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Screamer 4x4", ".spl")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    #noesis.logPopup()
    return 1

def CheckType(data):
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    vnum = noeUnpack('I', data[len(data)-4:len(data)])[0]
    rapi.rpgBindPositionBuffer(data[:-4], noesis.RPGEODATA_FLOAT, 12)
    rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, vnum, noesis.RPGEO_POINTS)

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    
    mdlList.append(mdl)
    return 1