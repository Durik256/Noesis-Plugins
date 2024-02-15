#by Durik256
from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("xiuxian chuan", ".msd2")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadModel(handle, noepyLoadModel)
	#noesis.logPopup()
	return 1

def noepyCheckType(data):
    return 1
    
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    bs.seek(32)
    mat_name = readString(bs)
    num_color = bs.readUInt()
    for x in range(num_color):
        col_name = readString(bs)
        color = bs.read(bs.readUByte())
        
    unk = bs.readUInt()
    num_tx = bs.readUInt()
    for x in range(num_tx):
        tx_name = readString(bs)
        path_name = readString(bs)
    
    inum = bs.readUInt()
    iofs = bs.tell()
    bs.seek(inum*2,1)
    
    num_submesh = bs.readUInt()
    for x in range(num_submesh):
        inum = bs.readUInt()
        vnum = bs.readUInt()
        vbuf = bs.read(vnum*12)
        
        uvnum  = bs.readUInt()
        uvbuf = bs.read(uvnum*8)
        
        cpos = bs.tell()
        bs.seek(iofs)
        ibuf = bs.read(inum*2)
        iofs = bs.tell()
        bs.seek(cpos)
        
        nnum  = bs.readUInt()
        bs.seek(nnum*12,1)
        
        num  = bs.readUInt()
        bs.seek(num*16,1)
        bs.seek(8,1)
        bnum = bs.readUInt()
        names = []
        for x in range(bnum):
            names.append(readString(bs))
            
        wnum  = bs.readUInt()
        bs.seek(wnum*20,1)
        print(bs.tell())

        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
        rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 8)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default','')]))
    mdlList.append(mdl)
    return 1
    
def readString(bs):
    return bs.read(bs.readUByte()).replace(b'\x00', b'').decode('ascii', errors='ignore')
