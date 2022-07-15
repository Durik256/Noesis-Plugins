#by Durik 256 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("NFSU", ".bin")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    
    #noesis.logPopup()
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data)
    if bs.readBytes(4) != b'\x00@\x13\x80':
        return 0
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    fSize = header(bs)
    chanks = readChunks(bs, fSize)
    
    print('>>>>model')
    ctx = rapi.rpgCreateContext()
    
    for i,x in enumerate(chanks):
        if x.type == 16400:#mesh
            for x in x.childs:
                if x.type == 16640:#sub_mesh
                    print('>>mesh'+str(i))
                    for x in x.childs:
                        bs.seek(x.offset)
                        if x.type == 18688:#sub_mesh_info
                            count = skip(bs, 17)
                            info = [bs.readInt() for x in range((x.size-count)//4)]
                            icount, vcount = info[-7]*3, info[-3]
                            #print('>>debug:>> icount:', icount, 'vcount:', vcount,info)
                        if x.type == 19201:#sub_mesh_vbuf
                            count = skip(bs, 17)
                            vbuf = bs.readBytes(x.size-count)
                        if x.type == 19203:#sub_mesh_ibuf
                            count = skip(bs, 17)
                            ibuf = bs.readBytes(x.size-count)
                    
                    try:
                        stride = len(vbuf)//vcount
                        print(' icount:', icount, 'vcount:', vcount, 'stride:', stride)
                        
                        rapi.rpgSetName('mesh_'+str(i))
                        rapi.rpgSetMaterial('default')
                        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, stride)
                        if stride > 24:
                            rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, 12)
                            rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, 28)
                        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_SHORT, icount, noesis.RPGEO_TRIANGLE)
                    except:
                        print('Error mesh_'+str(i)+'!')
            
    try:
        mdl = rapi.rpgConstructModel()
        mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default','')]))
        mdlList.append(mdl)
    except:    
        mdlList.append(NoeModel())
        print('Error dont have mesh!')
        
    rapi.setPreviewOption("setAngOfs", "0 -90 0")
    return 1
    
def header(bs):
    bs.seek(8)#root, size
    bs.seek(bs.readUInt(),1)
    bs.seek(bs.readUInt(),1)
    return bs.getSize()
    
def readChunks(bs, end):
    chanks = []

    while bs.getOffset() < end:
        type, child = bs.readUShort(), bs.readUShort()
        size = bs.readUInt()
        offset = bs.getOffset()
        chanks.append(chunk(type,offset,size))
        #print('/type:', type, '/child:', False if child == 19 else True, '/size:', size, '/offset:', offset)
        if child == 32787 and size > 0:
            chanks[-1].childs = readChunks(bs, offset+size)
        else:
            #print('seek',size)
            bs.seek(size, 1)
    return chanks

def skip(bs, val):
    count, byte = 0, val
    
    while byte == val:
        byte = bs.readUByte()
        if byte == val: count += 1
    bs.seek(-1,1)
    return count
    
class chunk:
    def __init__(self, type, offset, size):
        self.type = type
        self.offset = offset
        self.size = size
        self.childs = []
        
    def __repr__(self):
        return "chunk(type:" + repr(self.type) + ",offset:" + repr(self.offset)+ ",size:" + repr(self.size)  + ",childs:" + repr(len(self.childs)) + ")"