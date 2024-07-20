#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Ice Age", ".rk")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    if len(data) < 0x80:
        return 0
    bs = NoeBitStream(data)
    Tag = noeAsciiFromBytes(bs.readBytes(8))
    if Tag != 'RKFORMAT':
        return 0
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    header = bs.readInt64()
    ver = bs.readInt64()
    master = noeAsciiFromBytes(bs.readBytes(64))
    #vertex info
    v_unk = bs.readInt()
    v_offset = bs.readInt()
    v_count = bs.readInt()
    v_size = bs.readInt()
    #face info
    f_unk = bs.readInt()
    f_offset = bs.readInt()
    f_count = bs.readInt()
    f_size = bs.readInt()
    #bone info
    bs.seek(0x50, NOESEEK_REL)
    b_unk = bs.readInt()
    b_offset = bs.readInt()
    b_count = bs.readInt()
    b_size = bs.readInt()
    #weight info
    bs.seek(0x80, NOESEEK_REL)
    w_unk = bs.readInt()
    w_offset = bs.readInt()
    w_count = bs.readInt()
    w_size = bs.readInt()

    #bones read
    bones = []
    bs.seek(b_offset, NOESEEK_ABS)
    for x in range(b_count):
        parent = bs.readInt()
        id = bs.readInt()
        child = bs.readInt()
        mat = NoeMat44.fromBytes(bs.readBytes(64)).toMat43()
        name = noeAsciiFromBytes(bs.readBytes(64)).strip()
        bones.append(NoeBone(id,name,mat,None,parent))

    #weight read
    weight = []
    bs.seek(w_offset, NOESEEK_ABS)
    for x in range(w_count):
        boneID = [bs.readUByte() for b in range(4)]
        boneW = [bs.readUByte()/255 for b in range(4)]
        weight.append(NoeVertWeight(boneID,boneW))

    #face read
    face = []
    bs.seek(f_offset, NOESEEK_ABS)
    face += [bs.readShort() for x in range(f_count)]

    #vertex/uv read
    vert, uv = [], []
    bs.seek(v_offset, NOESEEK_ABS)
    for x in range(v_count):
        vert.append(NoeVec3.fromBytes(bs.readBytes(12)))
        #print(x,"ver",vert[-1])
        bs.seek(12, NOESEEK_REL)
        uv.append(NoeVec3([bs.readShort()/32768, bs.readShort()/32768]+[0]))

    #open 1 anim
    animList = []
    animPath =  os.path.join(rapi.getDirForFilePath(rapi.getInputName()),"a_sid_run_01.anim")
    with open(animPath, "rb") as animStream:
        animList.append(LoadAnim(animStream.read(),bones))
    #end open 1 anim
    """
    #open all anim from dir
    animDir =  rapi.getDirForFilePath(rapi.getInputName())
    animPaths = []
    for root, dirs, files in os.walk(animDir):
        for fileName in files:
            lowerName = fileName.lower()
            if lowerName.endswith(".anim"):
                fullPath = os.path.join(root, fileName)
                animPaths.append(fullPath)
    for animPath in animPaths:
        with open(animPath, "rb") as animStream:
            animList.append(LoadAnim(animStream.read(),bones))
    """

    mesh = NoeMesh(face, vert , "mesh_0")
    mesh.setUVs(uv)
    mesh.setWeights(weight)
    mdl = NoeModel([mesh])
    mdl.setBones(bones)
    #mdl.setAnims(animList)
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial("default","")]))
    mdlList.append(mdl)
    return 1

def LoadAnim(data,bones):    
    bs = NoeBitStream(data)

    header = bs.readInt64()
    ver = bs.readInt64()
    name = noeAsciiFromBytes(bs.readBytes(64))
    #anim info
    bone_count = bs.readInt()
    frame_count = bs.readInt()
    unk = bs.readInt()#alweys 4
    framerate = bs.readInt()#?

    frame_matrix = []
    if bone_count > len(bones):
        return NoeAnim(name, bones, 1, [NoeMat43()]*len(bones), 1)

    for f in range(frame_count):
        for x in range(bone_count):
            pos = NoeVec3([bs.readShort()/32 for y in range(3)])
            unk = bs.readUByte()#/255#scale???
            mat = NoeQuat([bs.readByte()/127 for y in range(4)])
            mat = mat.toMat43()
            mat[3] = pos

            frame_matrix.append(mat)

    anim = NoeAnim(name, bones, frame_count, frame_matrix, framerate)
    print(len(frame_matrix))
    return anim