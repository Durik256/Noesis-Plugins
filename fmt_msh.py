#powered by Durik256 for xentax.com
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Warhammer Gladius",".msh")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)	
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data)
    if noeAsciiFromBytes(bs.readBytes(6)) != 'MSH1.0':
        return 0
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(7)
    
    bones = [NoeBone(0, "root", NoeMat43())]
    bcount = bs.readUByte()
    for x in range(bcount):
        name = searchString(bs)
        mat43 = NoeMat44.fromBytes(bs.readBytes(64)).toMat43()
        bones.append(NoeBone(bcount-x, name, mat43))
        print(bones[-1])
    
    print("End name/mat44:",bs.getOffset())
    bs.seek(111,1)

    stride, offset = calcStride([searchString(bs)[1:] for x in range(bs.readUByte())])
    bs.seek(5,1)
    
    vcount = ((bs.getSize()-4)-bs.getOffset())//stride
    print("vcount:",vcount,"stride:",stride)
    if vcount>0:
        ibuf = autoTriangles(vcount)
        vbuf = bs.readBytes((bs.getSize()-4)-bs.getOffset())
        
        ctx = rapi.rpgCreateContext()
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT,stride)
        
        if offset[1]:
            rapi.rpgBindBoneWeightBufferOfs(vbuf, noesis.RPGEODATA_FLOAT,stride,offset[1],4)
        if offset[2]:
            rapi.rpgBindBoneIndexBufferOfs(vbuf, noesis.RPGEODATA_FLOAT,stride,offset[1],4)
        if offset[3]:
            rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT,stride,offset[3])
        if offset[4]:
            rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT,stride,offset[4])
            
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_SHORT, len(ibuf)//2, noesis.RPGEO_TRIANGLE)
        mdl = rapi.rpgConstructModel()
    else:
        mdl = NoeModel()
    
    mdl.setBones(bones)
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 -90 0")
    return 1

def searchString(bs):
    bytes = []
    byte = None
    while byte != 0:
        byte = bs.readUByte()
        bytes.append(byte)
    return noeAsciiFromBytes(bytes)
    
def calcStride(attrib):
    print(attrib)
    stride = 0
    offset = [0,0,0,0,0,0]
    for x in attrib:
        if x in 'ertexPosition':
            stride += 12
        elif x in 'vertexBoneWeights':
            offset[1] = stride
            stride += 16
        elif x in 'vertexBoneIndices':
            offset[2] = stride
            stride += 16
        elif x in 'vertexTextureCoordinate':
            offset[3] = stride
            stride += 8
        elif x in 'vertexNormal':
            offset[4] = stride
            stride += 12
        elif x in 'vertexTangent':
            offset[5] = stride
            stride += 16
    return stride, offset
    
def autoTriangles(vcount):
    ibuf = b''
    for x in range(vcount):
        ibuf +=(x).to_bytes(2, 'little')
    return ibuf