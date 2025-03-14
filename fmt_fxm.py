#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("FBI Hostage Rescue", ".fxm")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    return 1
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    h = bs.read('3I')

    bones = []
    for x in range(h[2]):
        bs.seek(8, 1) # zero
        b_name = readLabel(bs)
        parent = bs.readInt()
        mat = NoeMat44.fromBytes(bs.read(64)).toMat43().inverse()
        bones.append(NoeBone(x,b_name,mat,None,parent))
        
    bs.seek(44 if h[2] else 32, 1)
        
    numSM = bs.readUInt()    
    for x in range(numSM):
        m_name = readLabel(bs)
        h1 = bs.read('8I')
        
        ibuf = bs.read(h1[6]*6)
        vbuf = bs.read(h1[7]*h1[4])
        
        rapi.rpgSetName(m_name)
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, h1[4])
        rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, h1[4],12)
        rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, h1[4],24)
        if h1[4] > 32:
            rapi.rpgBindUV2BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, h1[4],32)
        if h[2]:
            fixWeight(bs, h1[7])

        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, h1[6]*3, noesis.RPGEO_TRIANGLE)
        rapi.rpgClearBufferBinds()

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    
    mdl.setBones(bones)
    mdlList.append(mdl)

    rapi.setPreviewOption("setAngOfs", "0 90 90")
    return 1

def fixWeight(bs, vnum):
    wbuf = b''
    for x in range(vnum):
        bs.seek(12,1)
        num = bs.read('4B')[0]
        if not num: num = 1
        w = bs.read('4f')
        i = bs.read('4B')
        bs.seek(20,1)
        
        _w, _i = [0]*4, [0]*4
        for x in range(num):
            _w[x] = w[x]
            _i[x] = i[x]
        wbuf += noePack('4f', *_w)
        wbuf += noePack('4B', *_i)
    rapi.rpgBindBoneWeightBuffer(wbuf, noesis.RPGEODATA_FLOAT, 20, 4)
    rapi.rpgBindBoneIndexBufferOfs(wbuf, noesis.RPGEODATA_UBYTE, 20, 16, 4)

def readLabel(bs):
    return bs.read(bs.readUInt()).decode('ascii', errors='ignore')
