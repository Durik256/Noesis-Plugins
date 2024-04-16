#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("ben 10 omniverse", ".et_decomp")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data,1)
    ctx = rapi.rpgCreateContext()
    rapi.rpgSetEndian(1)
    
    result = [i for i in findall(b'\x00\x00\x00\x01\x00\x02', data)]
    for x in result:
        bs.seek(x+6)
        f = bs.readUByte()
        print('f::', f)
        if f:
            print('skip result::', x)
            continue
        bs.seek(-11,1)
        if bs.readUShort():
            print('skip result::', x)
            continue
        print('cur result::', x)
        bs.seek(-2,1)
        cpos = bs.tell()
        inum = bs.readUInt()
        if not inum:
            continue
        print('inum:',[inum],[bs.tell()])
        ibuf = bs.read(inum*2)
        vnum = max(noeUnpack('>%iH'%inum, ibuf))+1
        print('vnum:',[vnum],[bs.tell()])
        bs.seek(cpos)
        bs.seek(-(vnum*28+4),1)
        real_vnum = bs.readUInt()
        print('real_vnum:',[real_vnum],[bs.tell()])
        if vnum != real_vnum:
            print('bad vnum, skip result::', x)
            continue
        vbuf = bs.read(vnum*8)
        uvbuf = bs.read(vnum*20)
        
        try:
            rapi.rpgSetName('mesh_%i'%x)
            rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_SHORT, 8)
            rapi.rpgBindUV1BufferOfs(uvbuf, noesis.RPGEODATA_SHORT, 20, 8)
            rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_USHORT,inum,noesis.RPGEO_TRIANGLE)
        except:
            rapi.rpgClearBufferBinds()
            print('ERROR::', x)

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdlList.append(mdl)
    return 1

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)