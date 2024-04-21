#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Moorhuhn Kart Extra", ".obj")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    handle = noesis.register("Moorhuhn Kart Extra", ".clu")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel_CLU)
    #noesis.logPopup()
    return 1

def noepyCheckType(data):
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    iofs = data.find(b'\x07\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00')
    if iofs == -1:
        return 0
    
    try:
        bs.seek(iofs+12)
        inum = bs.readUInt()//2
        print('inum:',[inum],[bs.tell()])
        ibuf = bs.read(inum*2)
        vnum = max(noeUnpack('%iH'%inum, ibuf))+1
        bs.seek(iofs-4-(vnum*36))
        print('vnum:',[vnum],[bs.tell()])
        vbuf = bs.read(vnum*36)

        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 36)
        rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 36, 28)
        rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_USHORT,inum,noesis.RPGEO_TRIANGLE)
    except:
        print('ERROR::', iofs)

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdlList.append(mdl)
    return 1
    
def noepyLoadModel_CLU(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()

    result = [i for i in findall(b'\x07\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00', data)]
    if not result:
        return 0
    
    for iofs in result:
        try:
            bs.seek(iofs+12)
            inum = bs.readUInt()//2
            print('inum:',[inum],[bs.tell()])
            ibuf = bs.read(inum*2)
            vnum = max(noeUnpack('%iH'%inum, ibuf))+1
            bs.seek(iofs-4-(vnum*36))
            print('vnum:',[vnum],[bs.tell()])
            vbuf = bs.read(vnum*36)

            rapi.rpgSetName('mesh_%i'%iofs)
            rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 36)
            rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 36, 28)
            rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_USHORT,inum,noesis.RPGEO_TRIANGLE)
        except:
            rapi.rpgClearBufferBinds()
            print('ERROR::', iofs)

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
