#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Screamer 4x4", ".dat")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    noesis.logPopup()
    return 1

def CheckType(data):
    return 1

def LoadModel(files, mdlList):
    ctx = rapi.rpgCreateContext()
    data = None
    
    dir = os.path.dirname(rapi.getInputName())
    vbuf = rapi.loadIntoByteArray(os.path.join(dir, 'verticle.dat'))
    ibuf = rapi.loadIntoByteArray(os.path.join(dir, 'faces.dat'))
    
    vnum = noeUnpack('H', vbuf[:2])[0]
    inum = noeUnpack('H', ibuf[:2])[0]*3
    
    rapi.rpgBindPositionBuffer(vbuf[2:], noesis.RPGEODATA_FLOAT, 12)
    rapi.rpgCommitTriangles(ibuf[2:], noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)

    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdlList.append(mdl)
    return 1