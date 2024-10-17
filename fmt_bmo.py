#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Barbie as The Island Princess (PC)", ".bmo")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    if data[:4] != b'BMO ':
        return 0
    return 1
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    bs.seek(4)
    v0, v1 = bs.read('2B')
    
    mdl_name = bs.readString()
    numBones, bflag = bs.read('2I') if v0 == 3 else bs.read('=2B')
    tempParent = [-1]*numBones
    bones = []
    for x in range(numBones):
        parent = tempParent.pop()
        b_name = bs.readString()
        pos = NoeVec3.fromBytes(bs.read(12))
        bs.seek(1,1)
        childs = bs.readUInt() if v0 == 3 else bs.readUByte()
        tempParent += [x]*childs
        mat = NoeMat43()
        mat[3] = pos
        bones.append(NoeBone(x,b_name,mat,None,parent))
        
    numMat = bs.readUShort()
    sm = []
    for x in range(numMat):
        label = bs.readString()
        u_inf = []
        if v0 == 3: 
            unk = bs.read('=4B')
            for x in range(unk[0]):
                u = bs.read('=2BH')
                u_inf.append(u)
        elif v0 == 2: 
            unk = bs.read('=2B')
            for x in range(unk[0]-1):
                u = bs.readUByte()
                u_inf.append([0,u,0])
            u_inf.append([0,bs.readUByte(),bs.readUShort()])
        sm.append([label, unk, u_inf])
        
    for i,x in enumerate(sm):
        mat_name, u0, u1 = x
        rapi.rpgSetMaterial(mat_name)
        
        bi = [u0[1]]*4
        if u0[0] > 1:
            for q in range(len(u1)-1):
                bi[q+1] = u1[q][1]

        x = u1[-1]
        vbuf = bs.read(x[2]*36)
        
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 36)
        rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 36,12)
        rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 36,24)
        
        rapi.rpgBindBoneIndexBuffer(noePack('4H', *bi)*x[2], noesis.RPGEODATA_USHORT, 8, 4)
        rapi.rpgBindBoneWeightBufferOfs(vbuf, noesis.RPGEODATA_UBYTE, 36, 32, 4)

        rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, x[2], noesis.RPGEO_TRIANGLE)
        rapi.rpgClearBufferBinds()
                
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    
    mdl.setBones(bones)
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 -90 0")
    return 1
