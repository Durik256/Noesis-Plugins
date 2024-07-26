#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Crash Bandicoot Nitro Kart 3D", ".vram")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    if data[:4] != b'PIFF':
        return 0
    return 1   
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    bs.seek(4) # PIFF
    PIFF_size = bs.readUInt() + 8
    print('PIFF_size:',PIFF_size)
    
    while bs.tell() < PIFF_size:
        label = bs.read(4)
        if label == b'SCEN' or label == b'3DOB':
            label += bs.read(4)
        size = bs.readUInt()
        cpos = bs.tell()
        print(label, size, [cpos])
        
        if label == b'MESH':
            vbuf = bs.read(size)
            rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_INT, 12)

        elif label == b'TXUV':
            uvbuf = bs.read(size)
            rapi.rpgSetUVScaleBias(NoeVec3([0.0000153,-0.0000153,0.0000153]),None)
            rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_UINT, 8)

        elif label == b'COLR':
            cbuf = bs.read(size)
            rapi.rpgBindColorBuffer(cbuf,noesis.RPGEODATA_UBYTE,3,3)

        elif label == b'POLY':
            iinf = bs.read('4I')
            ibuf = bs.read(size-16)
            rapi.rpgSetName('mesh_%i'%iinf[2])
            type = noesis.RPGEODATA_UBYTE # 5121
            if iinf[3] == 5123:
                type = noesis.RPGEODATA_USHORT
            rapi.rpgCommitTriangles(ibuf,type,iinf[1],noesis.RPGEO_TRIANGLE)
        
        bs.seek(cpos+size)

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdlList.append(mdl)
    return 1
