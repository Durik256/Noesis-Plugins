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
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    bs.seek(4)
    ver = bs.readInt()#ver 562 static and 578 skeletal
    name = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
    print(name)
    bones = []

    if ver == 578:
        bnum = bs.readInt()
        for x in range(bnum):
            bname = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
            print(bname)
            mat = NoeQuat.fromBytes(bs.readBytes(16)).toMat43()
            mat[3] = NoeVec3.fromBytes(bs.readBytes(12))
            scale = NoeVec3.fromBytes(bs.readBytes(12))
            unk, parent, unkF = bs.readInt(), bs.readInt(), bs.readFloat()
            print(unk, parent, unkF)
            bones.append(NoeBone(x, bname, mat, None, parent))
        print(bs.getOffset())
        bs.seek(268,1)
        
        bones = rapi.multiplyBones(bones)
    
        unk = bs.readInt()
        print(unk)
        for x in range(unk):
            while True:
                if not bs.readInt():
                    break
                print(bs.readBytes(bs.readInt()))#bs.seek(bs.readInt(),1)
                print(bs.readBytes(bs.readInt()))#bs.seek(bs.readInt(),1)
            bs.seek(32,1)    
    
    numMDL = bs.readInt()
    for x in range(1):
        #rapi.rpgSetName('mesh_%i'%(x))
        unk = bs.readInt()#1
        nameOBJ = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
        bs.seek(bs.readInt(),1)#unk
        #u0, u1 = bs.readInt(), bs.readInt()
        #if not u0: 
        #    bs.seek(4, 1) 
        numMesh = bs.readInt()
        print("numMesh:",numMesh)
        for x in range(numMesh):
            numSubMesh = bs.readInt()
            print("numSubMesh:",numSubMesh, bs.getOffset())
            for y in range(numSubMesh):
                rapi.rpgSetName('mesh_%i_%i'%(x,y))
                print('mesh_%i_%i'%(x,y), bs.getOffset())
                bs.seek(bs.readInt() * 4,1)
                
                inum = bs.readInt()
                ibuf = bs.readBytes(inum*2)
                
                vnum = bs.readInt()
                vbuf = bs.readBytes(vnum*52)
                
                rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 52)
                rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
            bs.seek(4,1)
        bs.seek(4,1)
    print(bs.getOffset())
    '''
    
    
    
    vbuf = bs.readBytes(vnum*stride)
    
    numUVS = bs.readInt()
    uvbufs = []
    for x in range(numUVS):
        uvnum = bs.readInt()
        uvbufs.append(bs.readBytes(uvnum*8))
    
    inum = bs.readInt()
    ibuf = bs.readBytes(inum*2)
    
    ctx = rapi.rpgCreateContext()
    
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, stride)
    rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, 12)
    
    if len(uvbufs) > 0:
        rapi.rpgBindUV1Buffer(uvbufs[0], noesis.RPGEODATA_FLOAT, 8) 
    if len(uvbufs) > 1:
        rapi.rpgBindUV2Buffer(uvbufs[1], noesis.RPGEODATA_FLOAT, 8)
    
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
    '''
    mdl = rapi.rpgConstructModel()#NoeModel()#
    #mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default', '')]))
    mdl.setBones(bones)
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 90 0")
    return 1