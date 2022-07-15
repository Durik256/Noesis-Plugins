#by Durik256 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Liberation Maiden",".gm3")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    bs = NoeBitStream(data)
    if bs.readBytes(4) != b'GMD\x00':
        return 0
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(8)
    
    #0-tx;1-mat;2-num_bone;3-unk
    info = [bs.readShort() for x in range(4)]
    print('texture:',info[0],'materials:',info[1],'bones:',info[2],'unk:',info[3])
    
    #0-off_tx;1-off_mesh;2-off_bone
    offset = [bs.readInt() for x in range(3)]
    print('offset>> texture:',offset[0],'materials:',offset[1],'bones:',offset[2])
    
    bs.seek(offset[0])
    #32 bytes >> Texture
    for x in range(info[0]):
        name = noeAsciiFromBytes(bs.readBytes(16))
        #0-off_preview;1-off_next;2-offset;3-size
        bs.seek(16,1)
        print('%x texture: "%s"' % (x,name))
    
    #52 bytes >> Material
    materials = []
    for x in range(info[1]):
        name = noeAsciiFromBytes(bs.readBytes(16))
        #0-off_preview,1-off_next;2-zero;3-unk;4,5-zero,6-num?,7-offset;8-zero
        bs.seek(36,1)
        materials.append(NoeMaterial(name, ''))
        print('%x material: "%s"' % (x,name))
    
    #bs.seek(mat_inf[7])
    #20 bytes >> info
    #0,1-unk;2-off_tx;3-id;4-unk?
    
    #92 bytes >> bones
    bones, mesh = [], []
    for x in range(info[2]):
        name = noeAsciiFromBytes(bs.readBytes(16))
        #0-preview;1-next;2-parent;3-child?;4-id
        bone_inf = [bs.readInt() for x in range(5)]
        
        curPos = bs.getOffset()
        if bone_inf[2]:
            bs.seek(bone_inf[2])
            parentName = noeAsciiFromBytes(bs.readBytes(16))
            bs.seek(curPos)
        else:
            parentName = None
        #bs.seek(36,1)#76
        pos = NoeVec3.fromBytes(bs.readBytes(12))
        rot = NoeAngles.fromBytes(bs.readBytes(12))
        mat = rot.toMat43()
        scale = NoeVec3.fromBytes(bs.readBytes(12))
        print(x,pos,rot,scale)
        mat[3] = pos
        mesh_offset = bs.readInt()
        if mesh_offset:
            mesh.append([mesh_offset, name])
        bs.seek(16,1)
        bones.append(NoeBone(x,name,mat,parentName))
        print('%d bone: "%s" mesh: %s' % (x,name,str(mesh_offset) if mesh_offset else 'False'))
    
    for bone in bones:
        pIndex = GetParentIndex(bone.parentName, bones)
        if pIndex != -1:
            bone.setMatrix((bone.getMatrix() * bones[pIndex].getMatrix()))
    
    #create model
    ctx = rapi.rpgCreateContext()
    bs.seek(bs.getSize())#-52
    for x in mesh:
        bs.seek(x[0])
        num_submesh = bs.readInt()
        bs.seek(bs.readInt())
        
        #0,1-unk;2-count_vert;3-off_vert;4-count_indices;5-off_indices;6-unk'1';7,8,9-zero;10-unk
        mesh_inf = [[bs.readInt() for x in range(11)] for x in range(num_submesh)]
        
        for inf in mesh_inf:
            bs.seek(inf[5])
            ibuf = bs.readBytes(inf[4]*2)
            bs.seek(inf[3])
            stride = (inf[5] - inf[3])//inf[2]
            print('>>submesh: (indices:%d,  vert:%d, stride:%d)' % (inf[4],inf[3],stride))
            vbuf = bs.readBytes(inf[2]*stride)
            
            rapi.rpgSetName(x[1])
            rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, stride)
            rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, stride-8)
            rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_SHORT, inf[4], noesis.RPGEO_TRIANGLE)
        
    mdl = rapi.rpgConstructModel()
    mdl.setBones(bones)
    mdl.setModelMaterials(NoeModelMaterials([], materials))
    mdlList.append(mdl)
    return 1
    
def GetParentIndex(parentName, arr):
    for i,bone in enumerate(arr):
        if bone.name == parentName:
            return i
    return -1 