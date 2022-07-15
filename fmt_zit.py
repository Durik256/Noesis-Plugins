#by Durik256 for xentax.com 08.03.2022
from inc_noesis import *
import os

def registerNoesisTypes():
    handle = noesis.register("Aggressive Inline",".zit")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    bs = NoeBitStream(data)
    if noeAsciiFromBytes(bs.readBytes(4)) != 'FMDL': return 0
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(16)# FMDL, MODL
    fSize = bs.getSize()
    
    chunks = []
    while bs.getOffset() < fSize:
        name, size = readChunk(bs)
        if name != 'TGEO':
            bs.seek(size, NOESEEK_REL)
        else:
            offset = bs.getOffset()+size
            while bs.getOffset() < offset:
                name, size = readChunk(bs)
                if name != 'TGPT':
                    bs.seek(size, NOESEEK_REL)
                else:
                    offset = bs.getOffset()+size
                    while bs.getOffset() < offset:
                        name, size = readChunk(bs)
                        chunks.append(chunk(name, size, bs.getOffset()))
                        bs.seek(size, NOESEEK_REL)
                        print(chunks[-1])
                    break
            break

    for x in chunks:
        if x.name == 'TGVP':
            bs.seek(x.offset)
            vbuffer = bs.readBytes(x.size)
        if x.name == 'TGFM':
            bs.seek(x.offset)
            faces = []
            offset = x.offset + x.size
            while bs.getOffset() < offset:
                unk, numIndices = bs.readUShort(), bs.readUShort()
                bs.readInt()
                faces.append(bs.readBytes((numIndices-2)*2))
                if bs.readUShort() != 0: bs.seek(-2, NOESEEK_REL)
        if x.name == 'TGVU':
            bs.seek(x.offset)
            uvbuffer = bs.readBytes(x.size)
        if x.name == 'MOBO':
            bs.seek(x.offset)
            numBone, sizeBl = bs.readShort(), bs.readShort()
            bs.readInt()
            for x in range(numBone):
                id, parent = bs.readShort(), bs.readShort()
                bs.seek(16, NOESEEK_REL)
                name = noeAsciiFromBytes(bs.readBytes(31))
                bs.seek(5, NOESEEK_REL)
                print(id,parent,name)
            
    ctx = rapi.rpgCreateContext()
    for i,x in enumerate(faces):
        rapi.rpgSetName("mesh_"+str(i))
        rapi.rpgBindPositionBuffer(vbuffer, noesis.RPGEODATA_FLOAT,12)
        rapi.rpgBindUV1Buffer(uvbuffer, noesis.RPGEODATA_FLOAT,8)
        rapi.rpgCommitTriangles(x, noesis.RPGEODATA_USHORT, len(x)//2, noesis.RPGEO_TRIANGLE_STRIP)
    
    rapi.rpgOptimize()
    mdl = rapi.rpgConstructModel()
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 -90 -90")
    return 1
    
def readChunk(bs):
    name = noeAsciiFromBytes(bs.readBytes(4))
    size = bs.readUInt()
    return name, size

class chunk:
    def __init__(self, name, size, offset):
        self.name = name
        self.size = size
        self.offset = offset
        
    def __repr__(self):
        return "chunk(" + repr(self.name) + ",size:" + repr(self.size) + ",offset:" + repr(self.offset) + ")"