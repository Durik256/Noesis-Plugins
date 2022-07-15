#by Durik256 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Bus Derby (iOS)",".obj")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    bs = NoeBitStream(data)
    if noeAsciiFromBytes(bs.readBytes(12)) !='tibberojVER_':
        return 0
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(28)
    ctx = rapi.rpgCreateContext()

    for x in range(bs.readInt()):
        bs.seek(4,1)#MTRL
        offset = bs.readInt() + bs.getOffset()
        
        while bs.getOffset() < offset:
            chunk = noeAsciiFromBytes(bs.readBytes(4))
            size = bs.readInt()
            print(chunk,size)
            if chunk == 'NAME':
                name = noeAsciiFromBytes(bs.readBytes(size))
                rapi.rpgSetName(name)
            elif chunk == 'INDX':
                ibuf = bs.readBytes(size)
            elif chunk == 'VRTX':
                vbuf = bs.readBytes(size)
            elif chunk == 'NORM':
                nbuf = bs.readBytes(size)
            elif chunk == 'TEXB':
                skip = size + bs.getOffset()
                try:
                    bs.seek(28,1)
                    mat = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
                    rapi.rpgSetMaterial(mat)
                    bs.seek(4,1)#TCRD
                    uvbuf = bs.readBytes(bs.readInt())
                except:
                    pass
                bs.seek(skip)
            else:
                bs.seek(size,1)
        
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
        rapi.rpgBindNormalBuffer(nbuf, noesis.RPGEODATA_FLOAT, 12)
        try: 
            rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 8)
        except:
            pass
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_INT, len(ibuf)//4, noesis.RPGEO_TRIANGLE)
    
    bs.seek(8,1)#TXTR, size
    materials = []
    for x in range(bs.readInt()):
        name = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
        materials.append(NoeMaterial(os.path.splitext(name)[0],name))
    
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([], materials))
    mdlList.append(mdl)
    return 1