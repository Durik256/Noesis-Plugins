#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Black Desert Online", ".pam")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    if data[:4] != b'PAR ':
        return 0
    return 1
    
def noepyLoadModel(bs, mdlList):
    bs = NoeBitStream(bs)
    ctx = rapi.rpgCreateContext()
    bs.seek(16)
    
    numMesh = bs.readUInt()
    bs.seek(1040)
    
    minf, mat = [], []
    for m in range(numMesh):
        curPos = bs.getOffset()
        info = [bs.readUInt() for x in range(4)]
        tx = searchString(bs)
        bs.seek(curPos+272)
        minf.append(info)
        mat.append(NoeMaterial('mat_%i'%m, tx))
    
    vofs = bs.getOffset()
    iofs = vofs + sum([x[0] for x in minf])*32
    
    for i,x in enumerate(minf):
        bs.seek(vofs+(x[2]*32))
        rapi.rpgSetMaterial(mat[i].name)
        
        VBUF = bs.readBytes(x[0]*32)
        rapi.rpgBindPositionBuffer(VBUF, noesis.RPGEODATA_FLOAT, 32)
        rapi.rpgBindUV1BufferOfs(VBUF, noesis.RPGEODATA_HALFFLOAT, 32, 16)
		
        bs.seek(iofs+(x[3]*2))
        IBUF = bs.readBytes(x[1]*2)
        rapi.rpgCommitTriangles(IBUF, noesis.RPGEODATA_USHORT, x[1], noesis.RPGEO_TRIANGLE)
    
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([], mat))
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 90 90")
    return 1
    
def searchString(bs):
    bytes = []
    byte = None
    while byte != 0:
        byte = bs.readUByte()
        bytes.append(byte)
    return noeAsciiFromBytes(bytes)