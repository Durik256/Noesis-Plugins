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
    ext = '.wii_m' if os.path.splitext(fileName)[0].lower().endswith('_d') else '.dat'
    
    unks = list(bs.read('>%iI'%h[8]))+[h[9]]

    bs.seek(h[11]+h[10])
    finf = []
    for x in range(h[9]):
        u = bs.read('>3I')
        finf.append(u)
        
    #counter = 0
    #for j in range(h[8]):
    #    u = unks[j+1] - unks[j]
    #    for x in range(u):
    #        x = finf[counter]
    #        bs.seek(h[7]+x[2])
    #        data = bs.read(x[1])
    #        name = 'file_%i_%i%s'%(unks[j],x[0],ext)
    #        rapi.exportArchiveFile(name, data)
    #        print('unpack:', name)
    #        counter+=1
    
    for x in finf:
        bs.seek(h[7]+x[2])
        data = bs.read(x[1])
        name = 'file_%i%s'%(x[0],ext)
        rapi.exportArchiveFile(name, data)
        print('unpack:', name)

    print('unpack All:', h[9])
    return 1

def noepyCheckType(data):
    return 1  
    
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data,1)
    ctx = rapi.rpgCreateContext()
    rapi.rpgSetEndian(1)
    
    readMesh(bs)

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdlList.append(mdl)
    return 1

def readMesh(bs):
    u = bs.read('>7I2HI')
    bs.seek(88,1)
    
    lpos = bs.tell()
    vbuf = bs.read(u[1]*12)
    end = bs.tell()
    bs.seek(lpos+myCeil(bs.tell()-lpos,32))
    if bs.tell() == end:
        bs.seek(32,1)
    
    nbuf = b''
    if u[3]:
        lpos = bs.tell()
        nbuf = bs.read(u[1]*12)
        end = bs.tell()
        bs.seek(lpos+myCeil(bs.tell()-lpos,32))
        if bs.tell() == end:
            bs.seek(32,1)
    
    lpos = bs.tell()
    uvbuf = bs.read(u[1]*8)
    end = bs.tell()
    bs.seek(lpos+myCeil(bs.tell()-lpos,32))
    if bs.tell() == end:
        bs.seek(32,1)
    
    sm = []
    for x in range(u[7]):
        sm.append(bs.read('!IfIIHHIfBBBB'))
        
    ibuf_ofs = bs.tell()
    #ibuf = bs.read(u[5]*2)

    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
    if nbuf:
        rapi.rpgBindNormalBuffer(nbuf, noesis.RPGEODATA_FLOAT, 12)
    rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 8)

    for x in sm:
        bs.seek(ibuf_ofs+x[4]*2)
        ibuf = bs.read(x[5]*2)
        rapi.rpgSetName('mesh_%i'%x[8])
        rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_USHORT,x[5],noesis.RPGEO_TRIANGLE_STRIP)
    rapi.rpgClearBufferBinds()

''' OLD
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
    '''
