#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Coraline (wii)", ".wii")
    noesis.setHandlerExtractArc(handle, ExtractArc)
    
    handle = noesis.register("Coraline (wii)", ".wii_m")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def ExtractArc(fileName, fileLen, justChecking):
    with open(fileName, "rb") as f:
        bs = NoeBitStream(f.read(),1)
    
    if justChecking:
        return 1

    h = bs.read('>16I')
    bs.seek(h[7])
    for x in range(h[9]):
        cpos = bs.tell()
        size = readMesh(bs)
        bs.seek(cpos)
        data = bs.read(size)
        name = 'file_%i.wii_m'%x
        rapi.exportArchiveFile(name, data)
        print('unpack:', name)
        
    print('unpack All:', h[9])
    return 1

def noepyCheckType(data):
    return 1   

def readMesh(bs, createMesh=False):
    cpos = bs.tell()
    u = bs.read('>7I2HI')

    bs.seek(88,1)
    vnum, inum, numm = u[1], u[5], u[7]
    
    lpos = bs.tell()
    vbuf = bs.read(vnum*12)
    end = bs.tell()
    bs.seek(lpos+myCeil(bs.tell()-lpos,32))
    if bs.tell() == end:
        bs.seek(32,1)
    
    nbuf = b''
    if u[3]:
        lpos = bs.tell()
        nbuf = bs.read(vnum*12)
        end = bs.tell()
        bs.seek(lpos+myCeil(bs.tell()-lpos,32))
        if bs.tell() == end:
            bs.seek(32,1)
    
    lpos = bs.tell()
    uvbuf = bs.read(vnum*8)
    end = bs.tell()
    bs.seek(lpos+myCeil(bs.tell()-lpos,32))
    if bs.tell() == end:
        bs.seek(32,1)
    
    for x in range(numm):
        u0 = bs.read('>8I')
        
    ibuf = bs.read(inum*2)
    bs.seek(cpos+myCeil(bs.tell()-cpos,2048))
    size = bs.tell()-cpos
    
    if createMesh:
        rapi.rpgSetName('mesh_%i'%x)
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
        if nbuf:
            rapi.rpgBindNormalBuffer(nbuf, noesis.RPGEODATA_FLOAT, 12)
        rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 8)
        rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_USHORT,inum,noesis.RPGEO_TRIANGLE_STRIP)
        rapi.rpgClearBufferBinds()
    return size

def myCeil(n,i):
    return int(-1 * (n/i) // 1 * -1)*i

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data,1)
    ctx = rapi.rpgCreateContext()
    rapi.rpgSetEndian(1)
    
    readMesh(bs, True)

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdlList.append(mdl)
    return 1