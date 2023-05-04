#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Sword and Romance",".bmesh")#天剑奇缘
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadSkeleton)	
    return 1
    
def CheckType(data):
    #if data[:4] != b'\x01\x20\x00\x00':
    #    return 0
    return 1

def LoadSkeleton(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    #bs.seek(8)
    bones = []
    type = noesis.RPGEODATA_FLOAT
    
    while bs.tell() < bs.getSize():
        t = bs.read(2)
        print('t:',t,[bs.tell()])
            
        if t == b'\x01\x20':
            #pass
            type = noesis.RPGEODATA_HALFFLOAT
            
        elif t == b'\x00\x00':
            size = bs.readUInt()
                
        elif t == b'\x00\x02':
            size = bs.readUInt()
                
        elif t == b'\x01\x02':
            size = bs.readUInt()
        
            bnum = bs.readUShort()
            print('bnum:',bnum)
                
            parents = bs.read('%ib'%bnum)
            names = [noeStrFromBytes(bs.read(bs.readUShort())) for x in range(bnum)]
                
            for x in range(bnum):
                mat = NoeMat44.fromBytes(bs.read(64)).toMat43().inverse()
                bones.append(NoeBone(x,names[x],mat,None,parents[x]-1))
            
        elif t == b'\x02\x02':
            size = bs.readUInt()
            bs.seek(size,1)
        
        elif t == b'\x00\x01':
            size = bs.readUInt()
            
        elif t == b'\x01\x01':
            size = bs.readUInt()
            
        elif t == b'\x01\x00':
            #pass
            readMesh(bs, type)
        
        #elif t == b'\x06\x03':
        #    readMesh(bs)
            
        else:
            print('Error Unk "t"!')
            break
            
    mdl = rapi.rpgConstructModel()
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1
    
def readMesh(bs, type):
    t2 = bs.read(2)
    print('t2:', t2)
    hf = 1
    if type == noesis.RPGEODATA_FLOAT:
        hf = 2
    
    if t2 == b'\x06\x03':
        stride, uvofs, wofs, wiofs = 22*hf, 6*hf, 10*hf, 16*hf
    elif t2 == b'\x02\x00':
        stride, uvofs = 10*hf, 6*hf
    
    vnum = bs.readUInt()
    vbuf = bs.read(vnum*stride)
    
    inum = bs.readUInt()
    ibuf = bs.read(inum*2)
    print('vnum:',vnum,'inum:',inum)
            
    rapi.rpgSetName('mesh_%i'%bs.tell())
    rapi.rpgBindPositionBuffer(vbuf, type, stride)
    rapi.rpgBindUV1BufferOfs(vbuf, type, stride, uvofs)
    
    if stride > 10*hf: 
        rapi.rpgBindBoneWeightBufferOfs(vbuf, type, stride, wofs, 3)
        rapi.rpgBindBoneIndexBufferOfs(vbuf, type, stride, wiofs, 3)
    
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
