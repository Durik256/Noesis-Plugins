#by Durik256 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Cars Video Game",".dxg")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(8)
    
    bones = []
    for x in range(bs.readInt()):
        name = noeAsciiFromBytes(bs.readBytes(128))
        bs.seek(92,1)
        parent = bs.readInt()
        #mat = NoeMat44.fromBytes(bs.readBytes(64)).toMat43()
        bones.append(NoeBone(x,name, NoeMat43(), None, parent))
    
    mats = []
    for x in range(bs.readInt()):
        name = noeAsciiFromBytes(bs.readBytes(64))
        mats.append(NoeMaterial(name,name))
    
    ctx = rapi.rpgCreateContext()
    bs.seek(8,1)
    
    for x in range(bs.readInt()):
        id = bs.readInt()
        bs.seek(62,1)
        vnum, inum = bs.readShort(), bs.readShort()
        
        ibuf = bs.readBytes(inum*2)
        vbuf = bs.readBytes(vnum*6)
        nbuf = bs.readBytes(vnum*6)
        uvbuf = bs.readBytes(vnum*4)
        bs.seek(vnum*36,1)
        
        rapi.rpgSetName(mats[x].name)
        rapi.rpgSetMaterial(mats[x].name)
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_SHORT, 6)
        rapi.rpgBindNormalBuffer(nbuf, noesis.RPGEODATA_SHORT, 6)
        rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_SHORT, 4)
        rapi.rpgSetUVScaleBias(NoeVec3([16,16,0]), None, 0)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE_STRIP)
    mdl = rapi.rpgConstructModel()
    
    mdl.setBones(bones)
    mdl.setModelMaterials(NoeModelMaterials([], mats))
    mdlList.append(mdl)
    return 1