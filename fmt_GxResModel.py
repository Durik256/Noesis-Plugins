#by Durik256
#only for "C011.GxResModel"
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Dragon Star Defense", ".GxResModel")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def CheckType(data):
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    bs.seek(44368)
    
    vofs = 50508
    iofs = 1717460
    
    curV = 0
    for x in range(15):#
        #0-mg;1-vnum;2-iofs;3-inum;4-vofs;5-zero;6-zero
        h = bs.read('7I')
        bs.seek(80,1)
        name = noeStrFromBytes(bs.read(260))
        #print(h, name)
        curPos = bs.tell()
        
        #create Mesh
        if not h[2] and not h[4]:
            vofs += curV*68
            curV = 0
        print(name)
        print('vofs:',vofs,'iofs:',iofs,'vnum:',h[1],'inum:',h[3] )#,'curV:',curV
        bs.seek(vofs)
        
        vbuf = bs.read((curV+h[1])*68)
        curV += h[1]
        
        bs.seek(iofs)
        iofs += h[3]*2
        ibuf = bs.read(h[3]*2)
        
        rapi.rpgSetName(name +'_%i'%x)
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 68)
        rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 68, 52)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, h[3], noesis.RPGEO_TRIANGLE)
        rapi.rpgClearBufferBinds()
        
        bs.seek(curPos)

    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default','')]))
    mdlList.append(mdl)
    return 1