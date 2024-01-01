#by Durik256
from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Darkened Skye", ".skg")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadModel(handle, noepyLoadModel)
	return 1

def noepyCheckType(data):
    return 1
    
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    bs.seek(8)#SKG
    fsize = bs.readUInt()
    fname = bs.read(32)
    #0-animNum?; 1-animOfs; 2-unkOfs; 3-unkNum(64bytes); 4-anim2Ofs?; 5-meshNum; 6-meshOfs; 7-numTx; 8-ofsTx; 9-unkNum; 10-unkOfs; 11...unk_float
    inf = bs.read('11I6f')
    print(inf)
    
    
    bs.seek(inf[8])
    texList = []
    for x in range(inf[7]):
        id = bs.readUInt()
        name = noeStrFromBytes(bs.read(16))
        print('tx_name:', name)
        #0-width; 1-height; ... ;6-ofs
        tx_inf = bs.read('7I')
        print('    tx_inf:', tx_inf)
        cpos = bs.tell()
        bs.seek(tx_inf[6])
        data = bs.read(tx_inf[0]*tx_inf[1]*3)
        data = rapi.imageDecodeRaw(data, tx_inf[0], tx_inf[1], 'b8g8r8')
        texList.append(NoeTexture('tx_%i'%x, tx_inf[0], tx_inf[1], data, noesis.NOESISTEX_RGBA32))
        bs.seek(cpos)
        
    bs.seek(inf[6])
    for x in range(inf[5]):
        #220 bytes
        name = bs.read(52).replace(b'\x00',b'').decode('ascii', errors='ignore')
        print('mesh_name:', name)
        #0-vnum; 3-vertSize; 4-vertOfs; 5-zero; 6-norNum;7-triNormOfs; 8-normOfs; 11-numUV; 12-ofsUV; (-2)-matId?; (-1)-EndBlock
        msh_inf = bs.read('42i')
        print('    msh_inf:', msh_inf)
        cpos = bs.tell()
        bs.seek(msh_inf[4])
        vbuf = b''
        for i in range(msh_inf[0]):
            num = bs.readUInt()
            for j in range(num):
                v = bs.read(12)
                vbuf += (v)
                boneId = bs.readInt()
                weight = bs.readFloat()
        
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
        rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, len(vbuf)//12, noesis.RPGEO_POINTS)
        #rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
        bs.seek(cpos)

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    mdl.setModelMaterials(NoeModelMaterials(texList, [NoeMaterial('default','')]))
    mdlList.append(mdl)
    return 1