#by Durik256 28.01.2022 for xentax.com
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("mount9_a", ".smz")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    if len(data) < 0x80:
        return 0
    bs = NoeBitStream(data)
    bs.seek(2, NOESEEK_ABS)
    if noeAsciiFromBytes(bs.readBytes(bs.readShort())) != 'SMZ_Actor':
        return 0
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(2, NOESEEK_ABS)
    header = noeAsciiFromBytes(bs.readBytes(bs.readShort()))
    unk = bs.readByte()#count object?
    frame_count = bs.readInt()
    bs.seek(8, NOESEEK_REL)
    anim_count = bs.readInt()
    
    for x in range(anim_count):
        name = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
        name2 = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
        start_frame = bs.readInt()
        end_frame = bs.readInt()
        event = bs.readInt()

        for y in range(event):
            name_event = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
            name_event2 = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
            event_frame = bs.readInt()
            bs.readByte()#[01]
        bs.readByte()#[01]
    
    # bones
    boneCount = bs.readInt()
    bones = []
    matList = []
    for i in range(0, boneCount):
        boneName = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
        parentName = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
        frameCount = bs.readInt()
        if frameCount > 0:
            #startFrame = 0 # 0-167
            #bs.seek(startFrame*0xC, NOESEEK_REL)
            Position = NoeVec3.fromBytes(bs.readBytes(12))
            bs.seek((frame_count-1)*0xC, NOESEEK_REL)
            bs.readInt()
            #bs.seek(startFrame*0x10, NOESEEK_REL)
            boneMat = NoeQuat.fromBytes(bs.readBytes(16)).toMat43().transpose()
            boneMat[3] = Position
            bs.seek((frame_count-1)*0x10, NOESEEK_REL)
        else:
            bs.seek(4, NOESEEK_REL)
            boneMat = NoeMat43()
        #bs.seek(10, NOESEEK_REL)
        bs.readShort()
        unk_byte = -1
        
        while unk_byte != 1:
            unk_byte = bs.readByte()
            
        bones.append(NoeBone(i, boneName, boneMat, parentName))
        matList.append(boneMat)

    #SMZ_SkelSkin
    file_count = bs.readInt()

    #=================Open Skin==========================================
    if file_count <= 0:
        path_skin = rapi.getInputName().replace(".smz",".ski")
        if os.path.exists(path_skin):
            with open(path_skin, "rb") as fileStream:
                #fileStream = open(path_skin, "rb")
                bs = NoeBitStream(fileStream.read())
        else:
            print(rapi.getInputName())
            mdl = NoeModel()
            mdl.setBones(bones)
            mdlList.append(mdl)
            return 1
    #=====================================================================
    
    bs.readShort()#[FF FF]
    header = noeAsciiFromBytes(bs.readBytes(bs.readUShort()))
    model_name = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
    bs.readShort()
    mesh_count = bs.readInt()
    
    #SMZ_Faces
    mesh_data = []
    for x in range(mesh_count):
        mat_name = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
        mesh_name = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
        face = [bs.readUShort() for x in range(bs.readInt())]
        bs.seek(1, NOESEEK_REL)
        mesh_data.append([face, mesh_name, mat_name])
    
    #SMZ_Materials
    bs.readShort()#[FF FF]
    bs.seek(bs.readShort(), NOESEEK_REL)
    mat_count = bs.readInt()
    
    materials = []
    for x in range(mat_count):
        bs.readShort()#[FF FF]
        bs.seek(bs.readShort(), NOESEEK_REL)
        mat_name = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
        bs.seek(81, NOESEEK_REL)
        tx_name = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
        bs.seek(51, NOESEEK_REL)
        materials.append(NoeMaterial(mat_name,tx_name))
    
    #SMZ_Mesh
    bs.readInt()#[01 00 01 01]
    vert_count = bs.readInt()
    
    vert, norm, uvs, weights = [], [], [], []
    
    for i in range(vert_count):
        bs.seek(12, NOESEEK_REL)
        uvs.append(NoeVec3([bs.readFloat(), bs.readFloat(), 0.0]))
        wCount = bs.readInt()
        
        boneID = [bs.readUByte()]
        boneW = [bs.readFloat()]
        
        vert.append(NoeVec3.fromBytes(bs.readBytes(12))*bones[boneID[0]].getMatrix())
        rot = NoeMat43(bones[boneID[0]].getMatrix()[:3]+[NoeVec3()])
        norm.append(NoeVec3.fromBytes(bs.readBytes(12))*rot)
        
        if wCount > 1:
            boneID += [bs.readByte()]
            boneW += [bs.readFloat()]
            bs.seek(25, NOESEEK_REL)
        
        bs.readShort()#[01 01]
        weights.append(NoeVertWeight(boneID, boneW))  
    meshes = []
    
    for i in range(mesh_count):
        meshes.append(Optimize(i, vert, norm, uvs, weights, mesh_data))

    mdl = NoeModel(meshes,bones)
    mdl.setModelMaterials(NoeModelMaterials([], materials))
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 -90 0")
    return 1

#remove null vertices
def Optimize(i, vert, norm, uvs, weights, mesh_data):
    v, n, uv, w  = [], [], [], []
    face = mesh_data[i][0]
    
    indices = list(set(face))
    indices.sort()

    for single in indices:
        v.append(vert[single])
        n.append(norm[single])
        uv.append(uvs[single])
        w.append(weights[single])

        for x in range(len(face)):
            if single == face[x]:
                face[x] = indices.index(single)
            
    mesh = NoeMesh(face, v, mesh_data[i][1]+"_"+str(i), mesh_data[i][2])
    mesh.setUVs(uv)
    mesh.setNormals(n)
    mesh.weights = w
    return mesh