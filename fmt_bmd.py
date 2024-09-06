#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("The Nightmare Before Christmas: Oogie's Revenge", ".bmd")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def CheckType(data):
    return 1

def LoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    bs = NoeBitStream(data)
    h = bs.read('8I')
    uOfs = bs.read('%iI'%myCeil(h[3]))
    mgOfs = bs.read('%iI'%myCeil(h[4]))
    bones = []
    for x in range(h[2]):
        bi = bs.read('8h')
        mat = NoeMat44.fromBytes(bs.read(64)).toMat43()
        bones.append(NoeBone(x,'bone_%i'%x,mat,None,bi[0]))
    
    bonemaps = []
    for x in range(h[3]):
        bs.seek(uOfs[x])
        i = bs.read('2I')
        bonemaps.append(bs.read('%iI'%i[0]))
        
        
    for x in range(h[4]):#
        bs.seek(mgOfs[x])
        mi = bs.read('24I')
        for j in range(mi[0]):#
            smi = bs.read('4i')

            ifmt = noesis.RPGEO_TRIANGLE_STRIP
            if smi[-1] == -1:
                ifmt = noesis.RPGEO_TRIANGLE

            rapi.rpgSetBoneMap(bonemaps[smi[2]])
            rapi.rpgSetName('mesh_%i_%i'%(x,j))
            rapi.rpgBindPositionBuffer(readBuf(smi[0],bs), noesis.RPGEODATA_FLOAT, 16)
            rapi.rpgBindBoneIndexBuffer(readWIBuf(smi[0],bs), noesis.RPGEODATA_UINT, 16, 4)
            rapi.rpgBindBoneWeightBuffer(readBuf(smi[0],bs), noesis.RPGEODATA_FLOAT, 16, 4)
            rapi.rpgBindNormalBuffer(readBuf(smi[0],bs), noesis.RPGEODATA_FLOAT, 16)
            rapi.rpgBindUV1Buffer(readBuf(smi[0],bs), noesis.RPGEODATA_FLOAT, 16)

            rapi.rpgCommitTriangles(None, noesis.RPGEODATA_UINT, smi[0], ifmt)
            rapi.rpgClearBufferBinds()

            print('>>>>END_SM:',bs.tell())

    if bones:
        bones = rapi.multiplyBones(bones)

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1
    
def myCeil(n):
    return int(-1 * (n/4) // 1 * -1)*4
    
def readBuf(n,bs):
    return bs.read(n*16)
    
def readWIBuf(n,bs):
    buf = b''
    for x in range(n):
        buf+=noePack('4I', *[x//8 for x in noeUnpack('4i', bs.read(16).replace(b'\xFF', b'\x00'))])
    return buf