#by Durik256 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Pacific rim", ".jboy")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def CheckType(data):
    if data[:4] != b'JBOY':
        return 0
    return 1
    
def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    rapi.rpgSetEndian(1)
    bs.setEndian(1)
    
    bs.seek(26)
    mcount = bs.readShort()
    bs.seek(34)
    bcount = bs.readShort()
    
    bs.seek(72)
    submesh = []
    for x in range(mcount):
        vcount, unk = bs.readInt(), bs.readInt()
        print('vcount:', vcount,'unk:', unk)
        num = bs.readInt()
        print(num,'bonemap?>>>',[bs.readInt() for x in range(num)])
        bs.seek(80-(num*4),1)
        print('?:',[bs.readInt() for x in range(3)])
        #0-voff;1-woff?;2-uoff;3-ioff;4-zero (all +8)
        off_info = [bs.readInt() for x in range(5)]
        print('off_info:',off_info)
        print('name:',noeAsciiFromBytes(bs.readBytes(16)))
        #0,1-unk?;2-name_num;3-name_off;4-vert_size/end?;5-vert_num;6-zero
        mesh_info = [bs.readInt() for x in range(7)]
        print('mesh_info:', mesh_info)
        #[0-voff;1-woff?;2-uoff;3-ioff;4-vnum]
        submesh.append(off_info[:-2]+[mesh_info[4]]+[vcount])
        bs.seek(16,1)
        #bs.seek(184,1)
    
    materials = []
    for x in submesh:
        bs.seek(x[0]+12)
        stride = (x[1]-x[0]-4)//x[4]
        vbuf = bs.readBytes(x[4]*stride)
        
        bs.seek(x[2]+8)
        uvbuf = bs.readBytes(x[4]*8)
        
        bs.seek(x[3]+8)
        itype, fnum, ioff = [bs.readInt() for x in range(3)]
        ibuf = bs.readBytes(fnum*2)
        
        print('submesh>>>: indx_num: %d; vert_num: %d; stride: %d;' % (fnum, x[4], stride))
        
        name = 'mesh_'+str(x[0])
        rapi.rpgSetName(name)
        materials.append(NoeMaterial(name,''))
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, stride)
        rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 8)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, len(ibuf)//2, noesis.RPGEO_TRIANGLE_STRIP)

    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([], materials))
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 -90 -90")
    return 1
