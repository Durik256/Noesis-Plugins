#by Durik256 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Blood +: One Night Kiss", ".GM2")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def CheckType(data):
    if data[:4] != b'GMF2':
        return 0
    return 1
    
def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    bs.seek(24)
    bone_num, mesh_num, unk, mat_num = [bs.readUShort() for x in range(4)]
    #0-bone_off;1-tx_off;2-zero;3-mat_off;4-unk;5-submesh_num
    info = [bs.readInt() for x in range(6)]
    
    bs.seek(info[0])
    bones, mesh, off_unk = [], [], []
    
    for x in range(bone_num):
        name = noeAsciiFromBytes(bs.readBytes(8))
        type = bs.readInt64()#1-mesh,17-bone
        b_info = [bs.readInt() for y in range(4)]
        curPos = bs.getOffset()
        for i,off in enumerate(b_info):
            if off != 0:
                bs.seek(off)
                b_info[i] = noeAsciiFromBytes(bs.readBytes(8))
                bs.seek(curPos)
            else:
                b_info[i] = None
        print(x, name, b_info, type)
        
        mesh_off = bs.readInt()
        if mesh_off != 0:
            mesh.append(mesh_off)
            off_unk.append([bs.readInt(),bs.readInt(), name])
            bs.seek(4,1)
        else:
            bs.seek(12,1)
        mat = NoeMat43()
        mat[3] = NoeVec3.fromBytes(bs.readBytes(12))
        bs.seek(68,1)
        bones.append(NoeBone(x, name, mat, b_info[0]))
    
    for bone in bones:
        bone.parentIndex = GetParentIndex(bone.parentName,bones)
        if bone.parentIndex != -1:
            bone.setMatrix(bone.getMatrix() * bones[bone.parentIndex].getMatrix())
    
    for i,x in enumerate(mesh):
        bs.seek(x)
        
        while x != 0:
            bs.seek(4,1)
            x, off_mesh = bs.readInt(), bs.readInt()
            bs.seek(20,1)
        
        end = (off_unk[i+1][1] if off_unk[i+1][1] != 0 else mesh[i+1]) if len(mesh) > i+1 else bs.getSize()
        
        rapi.rpgSetName(off_unk[i][2])
        
        while bs.getOffset() < end:
            bs.seek(16,1)
            count, dir, zero = bs.readUInt(), bs.readUInt(), bs.readInt64()

            if count <= 0: break
            vbuf = bs.readBytes(count*64)
            ibuf = autoTriangles(count)
            
            rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 64)
            rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 64, 48)
            rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, len(ibuf)//2, noesis.RPGEO_TRIANGLE_STRIP)
        
            bs.seek(16,1)
    
    mdl = rapi.rpgConstructModel()
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1
    
def autoTriangles(vcount):
    ibuf = b''
    for x in range(vcount):
        ibuf +=(x).to_bytes(2, 'little')
    return ibuf
        
def GetParentIndex (parentName, arr):
    for i,bone in enumerate(arr):
        if bone.name == parentName:
            return i
    return -1 