#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Diablo Immortal", ".mesh;.model")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    ext = os.path.splitext(rapi.getInputName())[1]
    if ext == '.mesh':
        if data[1:8] != b'MESSIAH':
            return 0
    if ext == '.model':
        if data[:4] != b'MODL':
            return 0
    return 1   
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    if data[:4] == b'MODL':
        bs.seek(56)
        while True:
            chank = bs.read(4)
            if chank == b'MESH':
                bs.seek(4,1)
                break
            else:
                bs.seek(bs.readUInt(),1)
    
    bs.seek(18, 1)
    submesh, vnum, inum = bs.readUShort(), bs.readUInt(), bs.readUInt()
    
    print(bs.tell())
    attrib = []
    for i in range(4):
        attrib.append(bs.read(bs.readUShort()).decode())
        
    bs.seek(40, 1)
    bs.seek(16 * submesh, 1);
        
    if vnum > 65535:
        ibuf = bs.read(inum*4)
        ifmt = noesis.RPGEODATA_UINT
    else:
        ibuf = bs.read(inum*2)
        ifmt = noesis.RPGEODATA_USHORT
    
    vbuf, uvbuf = b'', b''
    vfmt, uvfmt = 0, 0
    haveUVS = False;
    
    for a in attrib:
        if a != 'None':
            subs = a.split('_')
            T = False
            for i in range(vnum):
                for x in range(len(subs)):
                    format = subs[x][0]
                    count = int(subs[x][1])
                    type = subs[x][2]
                    
                    if format == 'P':
                        if type == 'H':
                            vfmt = noesis.RPGEODATA_HALFFLOAT
                            vbuf += bs.read(6)
                        elif type == 'F':
                            vfmt = noesis.RPGEODATA_FLOAT
                            vbuf += bs.read(12)
                            
                    elif format == 'T':
                        T = True
                        if type == 'H':
                            uvfmt = noesis.RPGEODATA_HALFFLOAT
                            uvbuf += bs.read(4)
                        elif type == 'F':
                            uvfmt = noesis.RPGEODATA_FLOAT
                            uvbuf += bs.read(8)
                            
                    else:
                        if type == 'B':
                            bs.seek(count, 1)
                        elif type == 'H':
                            bs.seek(count * 2, 1)
                        elif format == 'F':
                            bs.seek(count * 4, 1)
            if T == True:
                haveUVS = True

    rapi.rpgBindPositionBuffer(vbuf, vfmt, len(vbuf)//vnum)
    rapi.rpgBindUV1Buffer(uvbuf, uvfmt, len(uvbuf)//vnum)
    #if uv_stride > 12:
    #    rapi.rpgBindUV2BufferOfs(uvbuf, noesis.RPGEODATA_HALFFLOAT, uv_stride, 12)
    rapi.rpgCommitTriangles(ibuf, ifmt, inum, noesis.RPGEO_TRIANGLE)
    
    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([],[NoeMaterial('mat0','')]))
    mdlList.append(mdl)
    return 1
    
    