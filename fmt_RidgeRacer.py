#by Durik256
#you need add ext *.brs for you file
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Ridge Racer series", ".brs")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def noepyCheckType(data):
    if data[:3] != b'R7C':
        return 0
    return 1

def LoadModel (data, mdlList):
    bs = NoeBitStream(data,1)
    ctx = rapi.rpgCreateContext()
    rapi.rpgSetEndian(1)
        
    result = [i for i in findall(b'R7O', data)]
    for x in result:
        bs.seek(x)
        unk = bs.read('>6I')
        bs.seek(x+unk[4])
        _unk = bs.read('>5I')
        stride = (unk[5] - (unk[4]+20))//_unk[4]
        vbuf = bs.read(_unk[4]*stride)
        bs.seek(x+unk[5])
        __unk = bs.read('>4I')
        ibuf = bs.read(__unk[3]*2)

        rapi.rpgSetName('mesh_%i'%bs.tell())
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_HALFFLOAT, stride)
        #rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_HALFFLOAT, stride, stride-4)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, __unk[3], noesis.RPGEO_TRIANGLE_STRIP)
        rapi.rpgClearBufferBinds()
        
    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    try:
        mdl =rapi.rpgConstructModel()
    except:
        mdl =NoeModel()

    mdlList.append(mdl)
    return 1

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)
