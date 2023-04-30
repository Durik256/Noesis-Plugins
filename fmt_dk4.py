#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("GP500",".dk4")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)	
    return 1
    
def CheckType(data):
    if data[:4] != b'RDEH':
        return 0
    return 1

def LoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    bs = NoeBitStream(data)

    result = [i for i in findall(b'PMOC', data)]

    for x in result[:1]:
        #PMOC
        bs.seek(x+8)
        name = noeStrFromBytes(bs.read(32))
        h = bs.read('17i')#2-inum; 4-vnum
        vnum, inum = h[4], h[2]
        print('vnum:',vnum, 'inum:',inum)
        
        #RDHV
        label = bs.read(8)
        print('label:',label)
        if label[:4] != b'RDHV':
            continue
        
        vbuf = bs.read(vnum*32)
        
        #RDHT
        label = bs.read(8)
        print('label:',label)
        if label[:4] != b'RDHT':
            continue

        ibuf = b''
        for x in range(inum):
            ibuf += bs.read(6)
            bs.seek(14,1)
            
        rapi.rpgSetName(name+'_'+str(bs.tell()))
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 32)
        rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 32, 24)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, len(ibuf)//2, noesis.RPGEO_TRIANGLE)
        rapi.rpgClearBufferBinds()
    
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default','')]))
    mdlList.append(mdl)
    return 1

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)
