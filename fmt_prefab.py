#by Durik256
from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Uta no Prince-sama♪ LOVE EMOTION", ".prefab")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadModel(handle, noepyLoadSkel)
	return 1

def noepyCheckType(data):
    return 1
    
def noepyLoadSkel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    vofs = data.find(b'\x09\x00\x00\x00Positions')
    uofs = data.find(b'\x04\x00\x00\x00Uvs3')
    tofs = data.find(b'\x09\x00\x00\x00Triangles')

    if tofs != -1 and vofs != -1:
        bs.seek(tofs+119)
        itype, isize, zero, isize2 = bs.read('4I')
        ibuf = bs.read(isize)
        
        bs.seek(vofs+119)
        vtype, vsize, zero, vsize2 = bs.read('4I')
        vbuf = bs.read(vsize)
        
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
        if uofs != -1:
            bs.seek(uofs+114)
            utype, usize, zero, usize2 = bs.read('4I')
            uvbuf = bs.read(usize)
            rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_USHORT, 4)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, len(ibuf)//2, noesis.RPGEO_TRIANGLE) 
        rapi.rpgClearBufferBinds()

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    mdlList.append(mdl)
    return 1