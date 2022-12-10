#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Legacy Of Discord",".msh")
    noesis.setHandlerTypeCheck(handle, bcCheckType)
    noesis.setHandlerLoadModel(handle, bcLoadModel)
    return 1

def bcCheckType(data):
    if data[:3] != b'PSR':
        return 0
    return 1

def bcLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()

    bs.seek(20)
    name = bs.readBytes(bs.readInt() * 2).decode("utf-16")
    bs.readShort()
    vtype = bs.readInt()
    bs.seek(8,1)
    vnum = bs.readInt()
    fnum = bs.readInt()
    bs.seek(32,1)

    if vtype == 14:
        stride = 32
    if vtype == 19:
        stride = 36
    if vtype == 23:
        stride = 40

    vbuf = bs.readBytes(vnum*stride)
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, stride)
    rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, 12)
    rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, stride-8)
    ibuf = bs.readBytes(fnum * 6)

    rapi.rpgSetName(name)
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, fnum * 3, noesis.RPGEO_TRIANGLE)

    mdl = rapi.rpgConstructModel()
    mdlList.append(mdl)
    return 1