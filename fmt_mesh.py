#by Durik256 for xentax.com 03.02.2022 (ogre?)
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Tân Thiên Long 3D", ".mesh")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1

offset_mesh = -1
def noepyCheckType(data):
    global offset_mesh
    offset_mesh = data.find('[MeshSerializer'.encode())
    if offset_mesh == -1:
        return 0
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(offset_mesh+35, NOESEEK_ABS)
    file_size = bs.getSize()
    have_skeleton = False
    
    while bs.getOffset() < file_size:
        if bs.readShort() == 10:
            break
        else:
            bs.seek(-1, NOESEEK_REL)
    

    meshes = []
    materials = []
    while bs.getOffset() < file_size:
        id = str(len(meshes))
        mesh = loadMesh(bs)
        mesh.setName("mesh_"+id)
        mesh.setMaterial("mat_"+id)
        materials.append(NoeMaterial("mat_"+id,""))
        print(mesh)
        meshes.append(mesh)

        chunk = bs.readUShort()
        if chunk == 16384:#[00 40]
            size_mesh = bs.readInt()
            mane_mesh = readString(bs)
            bs.readByte()#zero
        elif chunk == 36864:#[00 90]
            break
        elif chunk == 24576:#[00 60]
            have_skeleton = True
            break

    print("Skeleton:",have_skeleton)
    bones = []
    if have_skeleton:
        bs.readInt()
        name_file = rapi.getInputName()
        dir_path = rapi.getDirForFilePath(name_file)
        path_skeleton0 = os.path.join(dir_path,readString(bs))
        path_skeleton1 = name_file.replace(".mesh",".skeleton")
        
        if os.path.exists(path_skeleton0):
            name_file = path_skeleton0
        elif  os.path.exists(path_skeleton1):
            name_file = path_skeleton1
        else:
            name_file = None
            print("Skeleton not found!")
        
        if name_file:
            with open(name_file, 'rb') as f:
                data = f.read()
                bones = LoadSkeleton(data)
    
    mdl = NoeModel(meshes)
    if bones:
        mdl.setBones(bones)
    mdl.setModelMaterials(NoeModelMaterials([], materials))
    mdlList.append(mdl)
    return 1

#MESH
def loadMesh(bs):
    face_count = bs.readInt()
    bs.seek(1, NOESEEK_REL)
    
    if face_count>65000:
        return 0
    face = [bs.readShort() for x in range(face_count)]
    
    #info mesh
    bs.readShort()#[00 50]
    size_FVF = bs.readInt()
    vert_count = bs.readInt()
    bs.readShort()#[00 51]
    this_count = bs.readInt()#54

    #vertex info
    bs.readShort()#[10 51]
    #0-size(16), 1-unk, 2-!inFVF?, 3-unk, 4-unk, 5-offset, 6-unk
    v_info = [bs.readShort() for x in range(7)]

    #normal info
    bs.readShort()#[10 51]
    n_info = [bs.readShort() for x in range(7)]

    param_count = int((this_count-6)/16)
    if param_count > 3:
        if param_count > 5:
            return 0
        for x in range(param_count-3):
            #unk0 info
            bs.readShort()#[10 51]
            unk_info = [bs.readShort() for x in range(7)]

    #uvs info
    bs.readShort()#[10 51]
    uv_info = [bs.readShort() for x in range(7)]
    bs.readShort()#[00 52]
    
    uv_start = bs.readInt()
    unk0 = bs.readShort()
    size_bl = bs.readShort()
    bs.readShort()#[10 52]
    v_size = bs.readInt()
    
    vert, norm, uv = [], [], []
    #read vertex/normals,uvs
    if vert_count>65000:
        return 0
    for x in range(vert_count):
        vert.append(NoeVec3.fromBytes(bs.readBytes(12)))
        if size_bl>12:
            norm.append(NoeVec3.fromBytes(bs.readBytes(12)))
        if size_bl > 24 and uv_info[2] == 0:
            bs.seek((uv_info[5]-24), NOESEEK_REL)
            uv.append(NoeVec3([bs.readFloat(), bs.readFloat()]+[0]))
 
    #read uvs
    if uv_info[2] > 0:
        for x in range(uv_info[2]-1):
            bs.readShort()#[00 52]
            count_seek = bs.readInt()-6
            bs.seek(count_seek,NOESEEK_REL)
        
        bs.readShort()#[00 52]
        end_uv = bs.readInt()
        
        unk_uv = bs.readShort()
        size_bl_uv = bs.readShort()
        bs.readShort()#[10 52]
        size_uv = bs.readInt()
        for x in range(vert_count):
            bs.seek(uv_info[5], NOESEEK_REL)
            uv.append(NoeVec3([bs.readFloat(), bs.readFloat()]+[0]))

    #read weight
    bs.readShort()#[10 40]
    unk_size = bs.readInt()#[08 00 00 00]
    unk_end = bs.readShort()#[04 00]
    has_weight = bs.readUShort()#need [00 41]
    
    VertexWeigts = []
    if has_weight == 16640:
        weight = [[[],[]] for x in range(vert_count)]
        cunk = has_weight#[00 41]
        while cunk == has_weight:
            size = bs.readInt()
            v_id = bs.readInt()
            weight[v_id][0].append(bs.readShort())#b_id
            weight[v_id][1].append(bs.readFloat())#b_we
            cunk = bs.readShort()
        bs.seek(-2, NOESEEK_REL)
    
        for w in weight:
            VertexWeigts.append(NoeVertWeight(w[0],w[1]))
    else:
        bs.seek(-2, NOESEEK_REL)

    mesh = NoeMesh(face, vert , "mesh_0")
    mesh.setNormals(norm)
    mesh.setUVs(uv)
    if VertexWeigts:
        mesh.setWeights(VertexWeigts)
    return mesh

#SKELETON
def skeletonCheckType(data):
    offset_skeleton = data.find('[Serializer_v1.10]'.encode())
    return offset_skeleton

def LoadSkeleton(data):
    offset_skeleton = skeletonCheckType(data)
    if offset_skeleton == -1:
        return 0
    bs = NoeBitStream(data)
    bs.seek(offset_skeleton+19, NOESEEK_ABS)
    
    file_size = bs.getSize()
    
    bones = []
    while bs.getOffset() < file_size:
        if bs.readShort() == 8192:
            bs.seek(4, NOESEEK_REL)
            name_bone = str(len(bones))+"_"+readString(bs)
            id_bone = bs.readUByte()
            bs.seek(1, NOESEEK_REL)
            pos = NoeVec3.fromBytes(bs.readBytes(12))
            mat = NoeQuat.fromBytes(bs.readBytes(16)).toMat43().transpose()
            mat[3] = pos
            bones.append(NoeBone(id_bone,name_bone,mat))
        else:
            bs.seek(-2, NOESEEK_REL)
            break

    for x in range(len(bones)-1):
        bs.readShort()#[00 30]
        bs.readInt()#[A0 00 00 00]
        bone_index = bs.readUShort()
        parent_index = bs.readUShort()
        bones[bone_index].parentIndex = parent_index
    
    for bone in bones:
        pIndex = bone.parentIndex
        if pIndex != -1:
            bone.setMatrix(bone.getMatrix() * bones[pIndex].getMatrix())
    
    bs.readShort()#[00 40]
    size_anim = bs.readInt()
    name_anim = "0_"+readString(bs)
    
    #Animations
    """
    print("count_bone", len(bones))
    print(size_anim, name_anim)
    print([bs.readByte() for x in range(4)])
    print("end", bs.getOffset())
    """
    return bones
 
def readString(bs):
    bytes = []
    for x in range(50):#max length string
        byte = bs.readUByte()
        if byte != 10:
            bytes.append(byte)
        else:
            break
    return noeAsciiFromBytes(bytes)