#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("my_Format", ".durik256")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1


def noepyCheckType(data):
    if data[:8] != b'DURIK256':
        return 0
    return 1
    
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    magic = bs.read(8)#DURIK256
    ver_minor = bs.readUInt()
    ver_major = bs.readUInt()

    num_bones = bs.readUInt()
    num_meshes = bs.readUInt()
    print('num_bones:', num_bones, 'num_meshes:', num_meshes)
    
    #read bones
    bones = []
    for x in range(num_bones):
        len_name = bs.readUInt()
        name = noeStrFromBytes(bs.read(len_name))
        matrix = NoeMat44.fromBytes(bs.read(64)).toMat43()
        parent = bs.readInt()
        bones.append(NoeBone(x,name,matrix,None,parent))

    
    #read materials
    materials = []
    if bs.readUInt():
        num_mats = bs.readUInt()
        for x in range(num_mats):
            len_name = bs.readUInt()
            name = noeStrFromBytes(bs.read(len_name))
            mat = NoeMaterial(name,'')
                
            diff = NoeVec4.fromBytes(bs.read(16))
            mat.setDiffuseColor(diff)

            if bs.readUInt():
                len_name = bs.readUInt()
                name = noeStrFromBytes(bs.read(len_name))
                mat.setTexture(name)
        materials.append(mat)
    
    if not materials:
        materials.append(NoeMaterial('default',''))
    
    for x in range(num_meshes):
        len_name = bs.readUInt()
        name = noeStrFromBytes(bs.read(len_name))
        rapi.rpgSetName(name)
        
        #read materials
        if bs.readUInt():
            len_name = bs.readUInt()
            mat_name = noeStrFromBytes(bs.read(len_name))
            rapi.rpgSetMaterial(mat_name)
        
        vnum = bs.readUInt()
        inum = bs.readUInt()
        print('vnum:', vnum, 'inum:', inum)
        
        #read pos vertex
        print('vbuf_ofs:', bs.tell())
        vbuf = bs.read(vnum*12)
        rapi.rpgBindPositionBuffer(vbuf,noesis.RPGEODATA_FLOAT,12)
        
        #read normals
        if bs.readUInt():
            nbuf = bs.read(vnum*12)
            rapi.rpgBindNormalBuffer(nbuf,noesis.RPGEODATA_FLOAT,12)
        
        #read uvs
        if bs.readUInt():
            uvbuf = bs.read(vnum*8)
            rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 8)
        
        #read weights
        if bs.readUInt():
            wbuf = bs.read(vnum*24)
            rapi.rpgBindBoneIndexBuffer(wbuf,noesis.RPGEODATA_USHORT,24,4)
            rapi.rpgBindBoneWeightBufferOfs(wbuf,noesis.RPGEODATA_FLOAT,24,8,4)

        #read traingles
        print('ibuf_ofs:', bs.tell())
        ibuf = bs.read(inum*2)
        rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_USHORT,inum,noesis.RPGEO_TRIANGLE)
        rapi.rpgClearBufferBinds()
    
    #read_Animations
    anims = []
    numAnims = bs.readInt()
    for i in range(0, numAnims):
        len_name = bs.readUInt()
        name = noeStrFromBytes(bs.read(len_name))
        #numAnimBones = bs.readInt()
        #animBones = []
        #for j in range(0, numAnimBones):
        #    animBone = noepyReadBone(bs)
        #    animBones.append(animBone)
        animNumFrames = bs.readInt()
        animFrameRate = bs.readFloat()
        numFrameMats = bs.readInt()
        animFrameMats = []
        for j in range(0, numFrameMats):
            frameMat = NoeMat43.fromBytes(bs.readBytes(48))
            animFrameMats.append(frameMat)
        anim = NoeAnim(name, bones, animNumFrames, animFrameMats, animFrameRate)
        anims.append(anim)

    mdl = rapi.rpgConstructModel()
    mdl.setBones(bones)
    mdl.setAnims(anims)
    mdl.setModelMaterials(NoeModelMaterials([], materials))
    mdlList.append(mdl)
    
    return 1