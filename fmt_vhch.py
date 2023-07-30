#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Ridge Racer",".vhcl")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    if data[:4] != b'vhcl':
        return 0
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data, 1)
    ctx = rapi.rpgCreateContext()
    rapi.rpgSetEndian(1)
    
    result = [(i+8) for i in findall(b'\x76\x65\x72\x74\x00\x00\x00\x03', data)]
    
    for x in result:
        bs.seek(x)
        vnum = bs.readUInt()
        print('vnum:',vnum,'vofs:',bs.tell())
        vbuf = bs.read(vnum*16)
        
        if bs.read(8) != b'\x74\x72\x69\x61\x00\x00\x00\x00':
            continue
            
        inum = bs.readUInt()
        print('inum:',inum,'iofs:',bs.tell())
        ibuf = bs.read(inum*6)
        

        rapi.rpgSetName('mesh_%i'%x)
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_SHORT, 16)
        rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_SHORT, 16, 12)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum*3, noesis.RPGEO_TRIANGLE)

    
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('dflt', '')]))
    mdlList.append(mdl)
    return 1

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)