#by Durik256 for xentax.com 08.03.2022
from inc_noesis import *
import os

def registerNoesisTypes():
    handle = noesis.register("NKart Racers 2",".dat")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    bs = NoeBitStream(data)
    if bs.readBytes(4) != b'\x00\x00\x80\xBF': return 0
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    haveBone = readHead(bs)
    offset = [0,26,24]
    
    #bones
    bones = []
    if haveBone:
        numBone = bs.readUInt()
        for x in range(numBone):
            name = noeAsciiFromBytes(bs.readBytes(32))
            unk = bs.readInt()
            bones.append(NoeBone(x,name, NoeMat43()))
        
        for x in bones:
            x.parentIndex = bs.readInt()
            
        for x in bones:
            pos = NoeVec3.fromBytes(bs.readBytes(12))
            mat = NoeQuat([bs.readHalfFloat() for x in range(4)]).normalize().toMat43()
            scale = NoeVec3.fromBytes(bs.readBytes(12))
            mat[3] = pos
            x.setMatrix(mat)
        #bs.seek(49, 1)
        offset[0] = 49
    
    for i in range(3 if haveBone else 1):
        bs.seek(offset[i], 1)
        #materials
        numMat = bs.readInt()
        matName = [searchString(bs) for x in range(numMat)]
        num, unk0, unk1 = [bs.readInt() for x in range(3)]
        for x in range(num):
            bs.seek(40, NOESEEK_REL)
        
        #vertices
        stride, vsize = bs.readInt(), bs.readInt()
        print(stride)
        vbuffer = bs.readBytes(vsize)
        #indices
        numIndices = bs.readInt()
        faces = bs.readBytes(numIndices*2)
        
        #create_model
        ctx = rapi.rpgCreateContext()
        rapi.rpgSetName("mesh_0")
        rapi.rpgBindPositionBuffer(vbuffer, noesis.RPGEODATA_FLOAT,stride)
        rapi.rpgBindUV1BufferOfs(vbuffer, noesis.RPGEODATA_HALFFLOAT,stride,20)
        if haveBone:
            rapi.rpgBindBoneWeightBufferOfs(vbuffer, noesis.RPGEODATA_UBYTE,stride,24, 4)
            rapi.rpgBindBoneIndexBufferOfs(vbuffer, noesis.RPGEODATA_BYTE,stride,28, 4)
        rapi.rpgCommitTriangles(faces, noesis.RPGEODATA_USHORT, numIndices, noesis.RPGEO_TRIANGLE)
        
        mdl = rapi.rpgConstructModel()
        rapi.rpgClearBufferBinds()
        if bones: mdl.setBones(bones)
        mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 90 0")
    return 1
    
#------------WARRING_Crutch--------------------------#
def readHead(bs):                                    #
    bs.seek(8)                                       #
    unk = bs.readFloat()                             #
    if unk == 1:                                     #
        unk = bs.readUShort()                        #
        if unk == 0:                                 #
            bs.seek(21, 1)                           #
            unk = bs.readUInt()                      #
            if unk != 0:                             #
                if unk<99: bs.seek(-4,1)             #
        elif unk > 99:                               #
            bs.seek(-2, 1)                           #
            path_model = searchString(bs)            #
            bs.seek(24 if bs.readByte()!=0 else 25,1)#
        else:                                        #
            bs.seek(-2, 1)                           #
            return 1                                 #
    elif unk == 2 or unk == 0:                       #
        path_model = searchString(bs)                #
        bs.seek(24 if bs.readByte() != 0 else 25, 1) #
    return 0                                         #
#----------------------------------------------------#

def searchString(bs):
    bytes = []
    byte = None
    while byte != 0:
        byte = bs.readUByte()
        bytes.append(byte)
    return noeAsciiFromBytes(bytes)
