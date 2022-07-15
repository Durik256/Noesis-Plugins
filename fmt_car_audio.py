#by Durik256 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("car audio",".bin")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    if data[1:7] != b'models':
        return 0
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    bs.seek(bs.readByte() + 25)

    count = bs.readByte()
    for x in range(count):
        print(x,noeAsciiFromBytes(bs.readBytes(bs.readByte())))
        bs.seek(48,1)
        for x in range(bs.readByte()):
            bs.seek(1,1)
            print('>>',noeAsciiFromBytes(bs.readBytes(bs.readByte())))
    
    bs.seek(292+(count*8),1)

    for x in range(bs.readByte()):
        vnum, inum = bs.readShort(), bs.readShort()
        vbuf = bs.readBytes(vnum*36)
        ibuf = bs.readBytes(inum*2)
        
        rapi.rpgSetName('mesh_'+str(x))
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 36)
        rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 36, 12)
        rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 36, 24)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_SHORT, inum, noesis.RPGEO_TRIANGLE)

    mdl = rapi.rpgConstructModel()
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 90 0")
    return 1