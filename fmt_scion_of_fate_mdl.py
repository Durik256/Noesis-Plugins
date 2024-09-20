#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("scion of fate online", ".mdl")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    if data[:4] != b'\xFF\xFF\xFF\xFF':
        return 0
    return 1
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()

    bs.seek(614)
    tx = bs.read(32).rstrip(b'\x00').decode('ascii', errors='ignore')

    bs.seek(654)
    vnum, tnum = bs.read('2I')
    vbuf = bs.read(vnum*32)
    ibuf = bs.read(tnum*6)
    
    rapi.rpgSetMaterial('mat0')
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 32)
    rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 32, 12)
    rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 32, 24)

    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, tnum*3, noesis.RPGEO_TRIANGLE)

    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([],[NoeMaterial('mat0', tx)]))
    mdlList.append(mdl)
    return 1