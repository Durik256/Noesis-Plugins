from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Dead Space 2 PS3", ".geo")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data,1)
    if noeAsciiFromBytes(bs.readBytes(4)) != "EAGM": 
        return 0
    return 1   

def noepyLoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()        
    bs = NoeBitStream(data, 1)
    bs.seek(62)
    submesh =  bs.readShort()
    print("count submesh:", submesh)
    bs.seek(104) 
    tableOff = bs.readUInt() 
    bs.seek(tableOff)
    
    #vertex
    VBsize = bs.readUInt()
    VCount = bs.readUInt()
    Vstride = bs.readShort()
    unk, Vflag = bs.readByte(), bs.readByte()
    VStart = bs.readInt()     
    print("Vsize:", VBsize,"Vcount:", VCount, "Vstride:",Vstride,"unk:",unk,"Vflag:",Vflag)
    #uvs
    bs.seek(16,1)
    #face
    FBsize = bs.readUInt()
    FCount = bs.readUInt()
    Fstride = bs.readShort()
    unk, Fflag = bs.readByte(), bs.readByte()
    FStart = bs.readInt()     
    print("FBsize:", FBsize,"FCount:", FCount, "Fstride:",Fstride,"unk:",unk,"Fflag:",Fflag)
    
    stride = Vstride if Vflag==0 else Vstride + 12
    print("stride:",stride)
    
    if VStart != 0:
        bs.seek(VStart)                        
    else:    
        bs.seek(80, 1)
    
    VBuf = bs.readBytes(VCount * stride)
    bs.seek(FStart)
    IBuf = bs.readBytes(FBsize)

    rapi.rpgSetEndian(1)
    rapi.rpgBindPositionBuffer(VBuf, noesis.RPGEODATA_FLOAT, stride)
    uvPath = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Open File", "Select UVs from 'MeshVolatile'", noesis.getSelectedFile())
    if uvPath and rapi.checkFileExists(uvPath):
        uvbuf = rapi.loadIntoByteArray(uvPath)
        rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 8) 
    rapi.rpgSetPosScaleBias(NoeVec3([174, 174, 174]), None)
    
    if unk != 1:                                     
        rapi.rpgCommitTriangles(IBuf, noesis.RPGEODATA_SHORT, FCount, noesis.RPGEO_TRIANGLE_STRIP, 1)
    else:
        rapi.rpgCommitTriangles(IBuf, noesis.RPGEODATA_SHORT, FCount, noesis.RPGEO_TRIANGLE, 1)
    mdl = rapi.rpgConstructModel()                                                          
    mdlList.append(mdl)
    rapi.rpgClearBufferBinds()
    return 1