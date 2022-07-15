#by Durik256 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("omega zodiac", ".out")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1
       
def noepyCheckType(data):
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.setEndian(1)
    
    count = bs.readShort()#count mdl?
    name = noeAsciiFromBytes(bs.readBytes(bs.readShort()))
    
    submesh, cbW = bs.readShort(), bs.readShort()#count_submesh?
    cV, sizeVbuf = bs.readInt(), bs.readInt()#count_float
    vbuf = bs.readBytes(sizeVbuf)

    cFace, sizeIbuf = bs.readInt(), bs.readInt()
    ibuf = bs.readBytes(sizeIbuf)

    cW, sizeWbuf = bs.readInt(), bs.readInt()
    wbuf = bs.readBytes(sizeWbuf)

    cBW = bs.readInt()
    wibuf = b''#bs.readBytes(sizeWbuf)
    
    for x in range(cBW):
        wibuf += (bs.readInt()//300).to_bytes(2, 'little')
    
    cBone = bs.readShort()

    bones = []
    for x in range(cBone):
        bname = noeAsciiFromBytes(bs.readBytes(bs.readShort()))
        bones.append(NoeBone(x,bname,NoeMat43()))
        #bs.seek(26,1)
        print(bname,[bs.readUByte() for i in range(26)])
  
    #Create model
    ctx = rapi.rpgCreateContext()
    
    rapi.rpgSetName(name)
    rapi.rpgBindPositionBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 52, 0)
    rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 52, 12)
    rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 52, 44)
    rapi.rpgBindBoneWeightBufferOfs(wbuf, noesis.RPGEODATA_FLOAT, cbW*4, 0, cbW)
    rapi.rpgBindBoneIndexBufferOfs(wibuf, noesis.RPGEODATA_SHORT, cbW*2, 0, cbW)
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, len(ibuf)//2, noesis.RPGEO_TRIANGLE)

    mdl = rapi.rpgConstructModel()
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1