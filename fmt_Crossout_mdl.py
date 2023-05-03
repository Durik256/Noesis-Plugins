#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Crossout",".mdl")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)	
    return 1
    
def CheckType(data):
    if data[:9] != b'TCF MODEL':
        return 0
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    bs.seek(16)
    h = bs.read('4I')
    bs.seek(h[2])
    
    bones, LOD0 = [], False
    for x in range(h[1]):
        type, size, ofs, unk = bs.read('4I')
        print((type, size, ofs, unk))
        
        curPos = bs.tell()
        bs.seek(ofs)
        
        #type:13=unk
        #      0=mesh
        #      1=bones
        #      6=slots
        
        if type == 0 and LOD0 == False:#mesh >> if you want all LOD replace to "if type == 0:"
            LOD0 = True
            bs.seek(68,1)
            vnum, inum = bs.read('2I')
            bs.seek(100,1)
            
            vbuf = bs.read(vnum*24)
            ibuf = bs.read(inum*2)
            
            print('vnum:',vnum,'inum:',inum)
                    
            rapi.rpgSetName('mesh_%i'%bs.tell())
            rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_HALFFLOAT, 24)
            rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_HALFFLOAT, 24, 16)
            rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
        
        elif type == 6:#slots
            num = bs.readUInt()
            for x in range(num):
                name = noeStrFromBytes(bs.read(32))
                mat = NoeMat44.fromBytes(bs.read(64)).toMat43().transpose()
                bones.append(NoeBone(x,name,mat))
        
        bs.seek(curPos)
            
    mdl = rapi.rpgConstructModel()#
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1