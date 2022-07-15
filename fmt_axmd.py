#by Durik256 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("The Strongest Hero", ".axmd")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def CheckType(data):
    bs = NoeBitStream(data)
    if bs.readBytes(4) != b'AXMD':
        return 0
    return 1
    
def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    bs.seek(32)#AXMD,4097, 24 bytes unk
    
    attrib, zero = bs.readInt(), bs.readInt()
    model_name = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
    
    attrib = [[noeAsciiFromBytes(bs.readBytes(4)), bs.readInt()] for x in range(attrib)]
    print(attrib)
    
    bones = []
    for name,offset in attrib:
        bs.seek(offset)
        if name == 'MESH':
            submesh = [[noeAsciiFromBytes(bs.readBytes(bs.readInt())), bs.readInt(), bs.readInt()] for x in range(bs.readInt())]
            type = bs.readInt()
            stride = 40 if type > 2 else 36
            print('stride:',stride,'type:',type,submesh)

            boneMap = []
            if len(attrib) > 3:
                for x in range(len(submesh)):
                    boneMap.append([bs.readUByte() for x in range(bs.readInt())])
                    #bs.seek(bs.readInt(),1)
            
            all_v = sum([x[1] for x in submesh])
            vbuf = bs.readBytes(all_v*stride)

            for i,(name,vnum,inum) in enumerate(submesh):
                ibuf = read_ibuf(bs, all_v, inum)#bs.readBytes(inum*2)
                
                rapi.rpgSetName(name)
                rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, stride)
                rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, stride-16)
                if len(attrib) > 3:
                    rapi.rpgSetBoneMap(boneMap[i])
                    rapi.rpgBindBoneWeightBufferOfs(vbuf, noesis.RPGEODATA_UBYTE, stride, 28, 4)
                    rapi.rpgBindBoneIndexBufferOfs(vbuf, noesis.RPGEODATA_UBYTE, stride, 32, 4)
                
                rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
        if name == 'BONE':
            num_bones = bs.readInt()
            for x in range(num_bones):
                id, parent = bs.readUByte(), bs.readUByte()
                name = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
                pos = NoeVec3.fromBytes(bs.readBytes(12))
                mat = NoeQuat.fromBytes(bs.readBytes(16)).toMat43()
                scl = NoeVec3.fromBytes(bs.readBytes(12))
                mat[3] = pos
                print(name, id, parent)
                bones.append(NoeBone(id, name, mat, None, parent))
    
    mdl = rapi.rpgConstructModel()
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1
    
def read_ibuf(bs, all_v, inum):
    ibuf = b''
    for x in range(inum):
        i = bs.readShort()
        if i > all_v: i = 0
        ibuf +=(i).to_bytes(2, 'little')
    return ibuf