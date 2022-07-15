#by Durik256 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Winter X-Games: Snocross",".grp")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(32)
    count = (bs.getSize()-40)//96
    
    dir = rapi.getDirForFilePath(rapi.getInputName())
    
    ctx = rapi.rpgCreateContext()

    bones = []
    for x in range(count):
        bs.seek(8,1)#OBJ, size(88)
        id = bs.readInt()
        name = searchString(bs) 
        bs.seek(39-len(name),1)

        bs.seek(8,1)
        parent = bs.readInt()
        pos = NoeVec3.fromBytes(bs.readBytes(12))
        bs.seek(4,1)
        mat = NoeAngles.fromBytes(bs.readBytes(12)).toMat43()
        bs.seek(4,1)
        mat[3] = pos
        bones.append(NoeBone(x,name,mat,None,parent))
            
        path = os.path.join(dir,name+'.M3D')
        if rapi.checkFileExists(path):
            data = rapi.loadIntoByteArray(path)
            LoadMesh(data, name, x)
    
    for bone in bones:
        parent = bone.parentIndex
        if parent != -1:
            bone.setMatrix(bone.getMatrix() * bones[parent].getMatrix())
    
    rapi.rpgSkinPreconstructedVertsToBones(bones)
    mdl = rapi.rpgConstructModel()
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1
    
def searchString(bs):
    bytes = []
    byte = None
    while byte != 0:
        byte = bs.readUByte()
        bytes.append(byte)
    return noeAsciiFromBytes(bytes)
    
def LoadMesh(data, name, bone):
    bs = NoeBitStream(data)
    bs.seek(64)#HEAD, VBUF
    vSize, unk, vCount = bs.readInt(), bs.readInt(), bs.readInt()
    
    stride = (vSize-8)//vCount
    print(stride)
    vbuf = bs.readBytes(vSize-8)
    
    bs.seek(4,1)#IBUF
    iSize, iCount = bs.readInt(), bs.readInt()
    
    ibuf = bs.readBytes(iSize-4)
    
    bbuf = bytes([bone]*vCount)
    wbuf = bytes([255]*vCount)
    
    rapi.rpgSetName(name)
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, stride)
    rapi.rpgBindBoneIndexBuffer(bbuf, noesis.RPGEODATA_BYTE, 1, 1)
    rapi.rpgBindBoneWeightBuffer(wbuf, noesis.RPGEODATA_BYTE, 1, 1)
    if stride > 12:
        rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, 12)
    if stride > 24:
        rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, stride-8) 
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, iCount, noesis.RPGEO_TRIANGLE)
    return 1