#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("3d looney tunes dash", ".fmlb")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    if data[:4] != b'_FML':
        return 0
    return 1   
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    bs.seek(4)#_FML

    # 0,1,2-ver(0,8,3); 3-numFile; 4-dataOfs; 5-dataSize(+4);
    h = bs.read('6I')
    print(h)
    
    bs.seek(4,1)#END>
    bs.seek(16,1) #zero

    subMeshes = []
    for x in range(h[3]):
        #102 - hier; 103 - txload; 104 - material; 107 - geo; 108 - prim; 113 - clip; 114 - aniplug; 123 - colorset
        
        # 0-type, 1,2 - zero
        fh = bs.read('3I')
        print('    ', fh)
        name = bs.read(64).split(b'\x00')[0]
        print('    ', name)
        # 0-data_ofs, 1-size, 2-index; 3-ender
        inf = bs.read('=2I2H')
        print('    ', inf)

        if fh[0]==107:
            subMeshes.append(SubMesh(name, inf[0]+h[4]))

    if not len(subMeshes):
        print("Dont have mesh")
        return 0

    for x in subMeshes:
        bs.seek(x.offset)
        name = bs.read(70).split(b'\x00')[0].decode()

        inum = bs.readInt()
        vnum = bs.readInt()
        unk1 =  bs.readInt()
        unk2 =  bs.readInt()
        bs.seek(126,1)#seek212
        print(name,"inum:",inum,"vnum:",vnum,unk1,unk2)


        ibuf = bs.read(inum*2)
        if bs.readShort():
            bs.seek(-2,1)
        vbuf = bs.read(vnum*12)

        rapi.rpgSetName(name)
        rapi.rpgBindPositionBuffer(vbuf , noesis.RPGEODATA_FLOAT, 12)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
        rapi.rpgClearBufferBinds()
    
    print(bs.tell())

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    #mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial("default","")]))
    mdlList.append(mdl)
    return 1

class SubMesh:
    def __init__(self, name, offset):
        self.name=name
        self.offset=offset
