#by Durik256
#only for "..\Kay\00000000.dat
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Legend of Kay Anniversary", ".dat")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1


def noepyCheckType(data):
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    #Textures
    txList, matList, txInf = [], [], [[952176,1024,1024,3],[1651232,256,128,3],[1673072,256,256,5],[1978904,256,256,3],[2023296,512,512,3],[2198064,512,512,3]]
    
    for x in range(len(txInf)):
        bs.seek(txInf[x][0])
        data = bs.read(txInf[x][1]*txInf[x][2]//(2 if txInf[x][3] == 3 else 1))
        data = rapi.imageDecodeDXT(data, txInf[x][1], txInf[x][2], txInf[x][3])
        txList.append(NoeTexture('tx_%i'%x, txInf[x][1], txInf[x][2], data, noesis.NOESISTEX_RGBA32))
        matList.append(NoeMaterial('mat_%i'%x, 'tx_%i'%x))
    
    #Bones
    bs.seek(12)
    bnum = bs.readUInt()
    bs.seek(bnum*4,1)
    parent = bs.read('%ih'%(bnum+1))
    bones = []
    for x in range(bnum):
        mat = NoeMat43.fromBytes(bs.read(48)).transpose().inverse()
        bones.append(NoeBone(x,'bone_%i'%x,mat,None,parent[x]))
    
    #Mesh
    bs.seek(951784)
    sm = []
    for x in range(9):
        bs.seek(20,1)
        sm.append(bs.read('2I'))
        print('vnum:', sm[-1][0], 'inum:', sm[-1][1])
        bs.seek(16,1)
    
    bs.seek(7744)
    u, mat_id = [0,1,5], [0,0,1,2,5,4,0,0,4]
    for x in range(9):
        inf = bs.read('5I')
        vnum, inum = sm[x]
        wbuf = bs.read(32*vnum)
        vbuf = bs.read(12*vnum)
        bs.seek(12*vnum,1)#nbuf
        
        if x in u:
            unk = bs.read('3I')
            bs.seek(unk[0]-12,1)
        
        uvbuf = bs.read(4*vnum)
        ibuf = bs.read(2*inum)

        rapi.rpgSetName('mesh_%i'%x)
        rapi.rpgSetMaterial('mat_%i'%mat_id[x])
        rapi.rpgBindPositionBuffer(vbuf,noesis.RPGEODATA_FLOAT,12)
        rapi.rpgBindBoneIndexBuffer(wbuf,noesis.RPGEODATA_INT,32,4)
        rapi.rpgBindBoneWeightBufferOfs(wbuf,noesis.RPGEODATA_FLOAT,32,16,4)
        rapi.rpgBindUV1Buffer(uvbuf,noesis.RPGEODATA_HALFFLOAT,4)

        rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_USHORT,inum,noesis.RPGEO_TRIANGLE)
        rapi.rpgClearBufferBinds()
    
    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    mdl.setBones(bones)
    mdl.setModelMaterials(NoeModelMaterials(txList, matList))
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 90 90")
    return 1