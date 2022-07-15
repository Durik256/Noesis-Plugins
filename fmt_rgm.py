from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Delight3D", ".rgm")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1
       
def noepyCheckType(data):
    if len(data) < 0x80:
        return 0
    bs = NoeBitStream(data)
    Tag = noeAsciiFromBytes(bs.readBytes(30))
    if Tag != 'Delight3D 3D DynamicObjectFile':
        return 0
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(41, NOESEEK_REL)
    
    bones_source = []
    read_bone(bs, bones_source, -1)
    print("bone count",len(bones_source))
    
    if bs.readUInt() == 120:
        print("Animations File Dont Suport!")
        return 0
    
    for x in range(len(bones_source)):
        bs.seek(5, NOESEEK_REL)
        boneID = bs.readShort()
        index = bs.readShort()
        mat = NoeMat43.fromBytes(bs.readBytes(48))
        print(mat)
        bones_source[boneID].mat = mat
        if index == -1:
            break
        
    v_count = bs.readUInt()
    bs.seek(1, NOESEEK_REL)

    vertex, normals, uvs = [], [], []
    
    for x in range(v_count):
        vertex.append(NoeVec3.fromBytes(bs.readBytes(12)))
        normals.append(NoeVec3.fromBytes(bs.readBytes(12)))
        uvs.append(NoeVec3([bs.readFloat(),bs.readFloat()]+[0]))
    
    t_count = bs.readUInt()
    triangles = [bs.readUShort() for x in range(t_count*3)]
    
    bones = []
    for i,bone in enumerate(bones_source):
        bones.append(NoeBone(i, bone.name, bone.mat, None, bone.parent))
    
    mesh = NoeMesh(triangles, vertex ,"mesh_0")
    mesh.setNormals(normals)
    mesh.setUVs(uvs)
    
    mdl = NoeModel([mesh])
    mdl.setBones(bones)
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial("mat_0","")]))
    mdlList.append(mdl)
    return 1
    
def read_bone(bs, arr, pID):
    arr.append(rgm_bones(searchString(bs), bs.readUByte(), pID))
    
    index = len(arr)-1
    for i in range(arr[-1].child):
        read_bone(bs, arr, index)
    return 1
    
def searchString(bs): 
    bytes = []
    for x in range(50):#max length string
        byte = bs.readUByte()
        if byte != 0:
            bytes.append(byte)
        else:
            break
    return noeAsciiFromBytes(bytes)
    
class rgm_bones:
    def __init__(self, name, child, parent):
        self.name = name
        self.child = child
        self.parent = parent
        self.mat = NoeMat43()