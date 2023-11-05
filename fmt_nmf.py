#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("DerClou! 2", ".nmf")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def noepyCheckType(data):
    if data[:4] != b'NMF ':
        return 0
    return 1

def LoadModel (data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()

    while bs.tell() < bs.getSize():
        readChunk(bs)

    mdl =rapi.rpgConstructModel()
    mdlList.append(mdl)
    return 1

def readChunk(bs):
    label = bs.read(4)
    size = bs.read('>I')[0]
    cpos = bs.tell()
    print(label,size)
    if label == b'MESH':
        uo, u1 = bs.read('2I')
        name = readString(bs)
        tnum, vnum = bs.read('2I')
        vbuf = bs.read(vnum*40)
        uvbuf = bs.read(vnum*8)
        inum = bs.readUInt()
        ibuf = bs.read(inum*2)
        rapi.rpgSetName(name)
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 40)
        rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 8)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
        rapi.rpgClearBufferBinds()

    bs.seek(cpos+size)

def readString(bf):
    cpos, s = bf.tell(), b''
    while True:
        s+=bf.read(1)
        if s[-1] == 0:
            break
    bf.seek(cpos+int(-1*(len(s)/4)//1*-1)*4)
    return s.rstrip().decode().replace("\x00", "")