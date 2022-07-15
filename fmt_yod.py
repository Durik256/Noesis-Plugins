#by Durik256 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Aerial Strike: The Yager Missions", ".yod")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    if data[:3] != b'YOD':
        return 0
    return 1   
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    bones = parseYSC()
    
    bs.seek(4)#YOD
    file_size, file_unk, num_mesh = bs.readInt(), bs.readInt(), bs.readInt()
    materials = []
    
    
    name_mdl = searchString(bs)
    for x in range(num_mesh):
        bs.seek(4,1)#MESH
        curPos = bs.getOffset() + 4
        size_mesh, vert, lod, mat = [bs.readInt() for x in range(4)]
        name_mesh, boneID = searchString(bs), -1
        
        #mat43 = NoeMat43()
        for ysc in bones:
            if name_mesh == ysc.name:
                boneID = ysc.index
                break
        
        if boneID == -1:
            boneID = len(bones)
            bones.append(NoeBone(boneID, name_mesh, NoeMat43()))
        
        rapi.rpgSetName(name_mesh)
        print('>>MESH',name_mesh)
        bs.seek(4,1)#VERT
        size_vert, vnum, stride, vunk = [bs.readInt() for x in range(4)]
        print('vnum',vnum,'stride',stride)
        
        vbuf = bs.readBytes(vnum * stride)
        
        bs.seek(4,1)#LOD
        lod_size, lodPos, lnum  = bs.readInt(), bs.getOffset(), bs.readInt()
        bs.seek(4,1)#TRIS
        tris_size, tunk, face_num = bs.readInt(), bs.readInt(), bs.readInt()
        print('face_num',face_num)
        
        ibuf = bs.readBytes(face_num * 6)
        
        if bs.readBytes(4) == b'ATTR':
            attr_size, anum = bs.readInt(), bs.readInt()
            for x in range(anum):
                #0-mat_id;1-face_start;2-face_count;3-vert_start;4-vert_count;
                ATTR = [bs.readInt() for x in range(5)]
                #print('ATTR',ATTR)
                
                createMesh('mat_%d_%s' % (x, name_mesh), vbuf, stride, ibuf[(ATTR[1]*6):(ATTR[1]*6)+(ATTR[2]*6)], boneID)
            
            bs.seek(4,1)#BNDV
            bndv_size = bs.readInt()
            bs.seek(bndv_size,1)
        else:
            createMesh('mat_0_%s' % name_mesh, vbuf, stride, ibuf)
            bs.seek(lodPos + lod_size)
        
        if mat:
            tx_dir = os.path.abspath(os.path.join(rapi.getDirForFilePath(rapi.getInputName()), '../texture/'))
            bs.seek(4,1)#MTRL
            mat_size, mnum = bs.readInt(), bs.readInt()
            for x in range(mnum):
                munk = [bs.readInt() for x in range(6)]
                mname = searchString(bs)
                #----find texture----
                for file in os.listdir(tx_dir):
                    if mname in file:
                        mname = file
                        break
                #--------------------
                materials.append(NoeMaterial('mat_%d_%s' % (x, name_mesh), os.path.join(tx_dir, mname)))
        else:
            materials.append(NoeMaterial('mat_0_%s' % name_mesh, ''))
        bs.seek(curPos + size_mesh)

    AnimList = LoadAnimations(bones)
    rapi.rpgSkinPreconstructedVertsToBones(bones)
    mdl = rapi.rpgConstructModel()
    mdl.setBones(bones)
    mdl.setModelMaterials(NoeModelMaterials([], materials))
    mdl.setAnims(AnimList)
    mdlList.append(mdl)
    return 1
    
def createMesh(mat_name, vbuf, stride, ibuf, boneID=0):
    rapi.rpgSetMaterial(mat_name)
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, stride)
    if stride > 24:
        rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, stride-8)
    
    rapi.rpgBindBoneIndexBuffer(((boneID).to_bytes(1, 'little'))*(len(vbuf)//stride), noesis.RPGEODATA_UBYTE, 1, 1)
    rapi.rpgBindBoneWeightBuffer(((255).to_bytes(1, 'little'))*(len(vbuf)//stride), noesis.RPGEODATA_UBYTE, 1, 1)
    
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, len(ibuf)//2, noesis.RPGEO_TRIANGLE)
    
def searchString(bs):
    bytes = []
    byte = None
    while byte != 0:
        byte = bs.readUByte()
        bytes.append(byte)
    return noeAsciiFromBytes(bytes)
    
def getBoneID(bones, name):
    for i,x in enumerate(bones):
        if x.name == name:
            return i
    return -1

def parseYSC():
    script_dir = os.path.abspath(os.path.join(rapi.getDirForFilePath(rapi.getInputName()), '../script/'))
    localName = rapi.getLocalFileName(rapi.getInputName()).split('.')[0]
    
    data = []
    for file in os.listdir(script_dir):
        if file.endswith(".ysc") and localName == file.split('.')[0]:
            with open(os.path.join(script_dir, file)) as f:
                data = f.readlines()
    
    mdl_name = data[0].split()[-1]+'_'
    data[0] = 'create ' + mdl_name
    
    bones,parents = [], [-1]
    for i,line in enumerate(data):
        
        if 'create' in line: #or '# class' in line
            parentID = parents[-1]
            parents.append(len(bones))
            name = line.split()[-1]
            
            matrix = NoeMat43()
            for x in range(i+1,len(data)):
                if 'setpos' in data[x]:
                    matrix[3] = NoeVec3([float(q) for q in data[x].split()[1:]])
                if 'setrot' in data[x]:
                    pos = matrix[3]
                    matrix = NoeQuat([float(q) for q in data[x].split()[1:]] ).toMat43().transpose()
                    matrix[3] = pos
                if 'setscale' in data[x]:
                    scale = NoeVec3([float(data[x].split()[-1])]*3)
                if 'setyod' in data[x]:
                    name = data[x].split()[-1].replace(mdl_name, '')
                if 'with ..' in data[x]:
                    parents = parents[:-1]
                if 'create' in data[x]:
                    break
            bones.append(NoeBone(len(bones), name, matrix, None, parentID))
    return bones
    
def LoadAnimations(bones):
    anims_dir = os.path.abspath(os.path.join(rapi.getDirForFilePath(rapi.getInputName()), '../anims/'))
    localName = rapi.getLocalFileName(rapi.getInputName()).split('.')[0]
    
    AnimList = []
    for file in os.listdir(anims_dir):
        if file.endswith(".yan") and localName in file.split('.')[0]:
            AnimList.append(LoadAnim(bones, os.path.join(anims_dir, file)))
    return AnimList

   
def LoadAnim(bones, path):
    data = rapi.loadIntoByteArray(path)
    bs = NoeBitStream(data)
    
    bs.seek(4)#YOD
    file_size, file_type, num_anim = bs.readInt(), bs.readInt(), bs.readInt()
    animBones, meshes = [], []
    
    name_mdl = searchString(bs)
    for x in range(num_anim):
        bs.seek(4,1)#ANIM
        curPos = bs.getOffset() + 4
        size_anim, unk = bs.readInt(), bs.readInt()
        name_anim = searchString(bs).split('/')[-1]
        
        boneID = getBoneID(bones, name_anim)
        print(boneID, name_anim)

        b = NoeKeyFramedBone(boneID)
        
        rotKeyList, posKeyList, sclKeyList = [], [], []
        
        label = bs.readBytes(4)
        size, num = bs.readInt(), bs.readInt()
        if label == b'ROTS':
            for x in range(num):
                time = bs.readFloat()
                rot = NoeQuat.fromBytes(bs.readBytes(16)).transpose()
                rotKeyList.append(NoeKeyFramedValue(time, rot))
                
        elif label == b'POSS':
            for x in range(num):
                time = bs.readFloat()
                pos = NoeVec3.fromBytes(bs.readBytes(12))
                posKeyList.append(NoeKeyFramedValue(time, pos))
        elif label == b'SCLS':
            for x in range(num):
                time = bs.readFloat()
                scale = bs.readFloat()
                scale_vec = NoeVec3([scale,scale,scale])
                sclKeyList.append(NoeKeyFramedValue(time, scale))
        
        bs.seek(curPos + size_anim)
        
        if rotKeyList:
            b.setRotation(rotKeyList)
        if posKeyList:
            b.setTranslation(posKeyList)
        if sclKeyList:
            b.setScale(sclKeyList)
        if boneID != -1:
            animBones.append(b)

    anim = NoeKeyFramedAnim('anim_' + name_mdl, bones, animBones, 30)
    return anim