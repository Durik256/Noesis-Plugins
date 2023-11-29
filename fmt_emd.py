#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Kamen Rider SummonRide", ".emd")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    noesis.logPopup()
    return 1

def CheckType(data):
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data,1)
    ctx = rapi.rpgCreateContext()
    rapi.rpgSetEndian(1)
    inf = bs.read('>28I')
    
    bones = []
    bs.seek(inf[21])
    for x in range(inf[9]):
        cpos = bs.tell()
        unk = bs.read('>2h2If')
        name = bs.read(256).replace(b'\x00', b'').decode('ascii', errors='ignore')
        unks = bs.read('>4i')
        matrix0 = NoeMat44.fromBytes(bs.read(64),1).toMat43()
        matrix1 = NoeMat44.fromBytes(bs.read(64),1).toMat43()
        bones.append(NoeBone(x,name,matrix1,None,unks[0]))
        bs.seek(cpos+unk[2])

    bs.seek(inf[19])
    for x in range(inf[11]):
        cpos = bs.tell()
        unk = bs.read('>2h2If')
        name = bs.read(256).replace(b'\x00', b'').decode('ascii', errors='ignore')
        bs.read('>8f4I')
        cpos2 = bs.tell()
        unk0 = bs.read('>34I')
        vnum, inum = bs.read('>2H')
        
        bs.seek(cpos2+unk0[0])
        ibuf = bs.read(inum*2)
        bs.seek(cpos2+unk0[2])
        vbuf = bs.read(vnum*12)
        
        bs.seek(inf[23]+unk0[7])
        uvbuf = bs.read(vnum*8)#unk0[8]

        try:
            rapi.rpgSetName(name)
            rapi.rpgBindPositionBuffer(vbuf,noesis.RPGEODATA_FLOAT,12)
            rapi.rpgBindUV1BufferOfs(uvbuf, noesis.RPGEODATA_HALFFLOAT, 8, 4)
            rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_USHORT,inum,noesis.RPGEO_TRIANGLE)
        except:
            print(x,'ERROR>>>>>>>>>>>>>>>>>>>>>>>>>>>>_ofs:',bs.tell())
        rapi.rpgClearBufferBinds()
        
        bs.seek(cpos+unk[2])
    
    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdl.setBones(bones)
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default','')]))
    mdlList.append(mdl)
    return 1
