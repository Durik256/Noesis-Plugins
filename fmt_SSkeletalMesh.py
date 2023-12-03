#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Dawn light",".SSkeletalMesh")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    if data[:4] == 'SATN':
        return 0
    return 1
    
def LoadModel(data, mdlList):
    x = [i for i in findall(b'SSkeletalMesh', data)]
    data = data[x[0]:x[1]]
    submesh = [(i-4) for i in findall(b'\x00\x00\x01\x00\x02\x00', data)]
    
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()

    for x in submesh:
        bs.seek(x)
        inum = bs.readInt()
        ibuf = bs.readBytes(inum*2)
        
        vnum = bs.readInt()
        vbuf = bs.readBytes(vnum*52)
        
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 52)
        rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 52, 24)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
    
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default', '')]))
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 90 0")
    return 1

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)
