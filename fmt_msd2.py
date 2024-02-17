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
    
    bs.seek(23)
    
    mats = []
    num_mat = bs.readUInt()
    for x in range(num_mat):
        bs.seek(5,1)#zero
    
        mat_name = readString(bs)
        mat = NoeMaterial(mat_name.replace(".fx",str(x)), "")
        num_color = bs.readUInt()
        for x in range(num_color):
            col_name = readString(bs)
            color = bs.read(bs.readUByte())
            if col_name == "materialSpecular" and len(color) == 16:
                mat.setSpecularColor(NoeVec4.fromBytes(color))
            if col_name == "materialDiffuse" and len(color) == 16:
                mat.setDiffuseColor(NoeVec4.fromBytes(color))
            if col_name == "materialAmbient" and len(color) == 16:
                mat.setAmbientColor(NoeVec4.fromBytes(color))
        
        unk = bs.readUInt()
        num_tx = bs.readUInt()
        for x in range(num_tx):
            tx_name = readString(bs)
            path_name = readString(bs)
            if tx_name == "diffuseTexture":
                mat.setTexture(path_name)
            if tx_name == "normalTexture":
                mat.setNormalTexture(path_name)
        mats.append(mat)

    inum = bs.readUInt()
    iofs = bs.tell()
    bs.seek(inum*2,1)

    num_submesh = bs.readUInt()

    inum = bs.read('%iI'%num_submesh)
    vnum = bs.readUInt()
    vbuf = bs.read(vnum*12)
    
    uvnum  = bs.readUInt()
    uvbuf = bs.read(uvnum*8)
    
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
    rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 8)
    
    curi = 0
    for i in range(num_submesh):
        bs.seek(iofs+(curi*2))
        _inum = inum[i] - curi
        print(inum[i],curi,_inum)
        ibuf = bs.read(_inum*2)
        rapi.rpgSetMaterial(mats[i].name)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, _inum, noesis.RPGEO_TRIANGLE)
        curi = inum[i]
    

    '''
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
    '''
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    
    mdl.setModelMaterials(NoeModelMaterials([], mats))
    mdlList.append(mdl)
    return 1
    
def readString(bs):
    return bs.read(bs.readUByte()).replace(b'\x00', b'').decode('ascii', errors='ignore')
