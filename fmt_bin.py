#by Durik256
#just test
#topic on forum
#https://reshax.com/topic/513-silent-hill-4-xbox-models-bin/#comment-1854
from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Silent Hill 4 XBOX", ".bin")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadModel(handle, noepyLoadModel)
	return 1

def noepyCheckType(data):
    return 1
    
#usePreSkin = True  
    
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    global bones
    bones = []
    
    n = bs.readUInt()
    ofs = bs.read('%iI'%n)
    print('ofs:',ofs)
    
    for x in ofs:
        bs.seek(x)
        magic = bs.read(4)
        if magic == b'\x03\x00\xFF\xFF':
            readMesh(bs)

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1
    
def readMesh(bs):
    global bones
    cpos = bs.tell() - 4
    hd = bs.read('15I')
    print(hd)
    
    bs.seek(cpos+hd[3])
    pi = bs.read('%ib'%hd[2])
    
    bs.seek(cpos+hd[1])
    for x in range(hd[2]):
        mat = NoeMat44.fromBytes(bs.read(64)).toMat43()
        bones.append(NoeBone(x,'bone_%i'%x,mat,None,pi[x]))
        
    bs.seek(cpos+hd[5])
    _pi = bs.read('%ib'%hd[4])
        
    #just added because the scales have more indices than bones
    #bs.seek(cpos+hd[6])
    #for x in range(hd[4]):
    #    mat = NoeMat44.fromBytes(bs.read(64)).toMat43()
    #    bones.append(NoeBone(len(bones),'bone_%i'%len(bones),mat))

    bs.seek(cpos+hd[8])
    for x in range(hd[7]):
        readSM(bs,x)
        
    bs.seek(cpos+hd[10])
    for x in range(hd[9]):
        readSM(bs,x)

def readSM(bs,x):
    m_start = bs.tell()
    inf = bs.read('16I')
    print(x,'m_inf:', inf)
    
    bs.seek(m_start+inf[6])
    #bi = bs.read('%iH'%inf[5])??
    #print('    bi:', bi)??
    bs.seek(m_start+inf[8])
    bi0 = bs.read('%iH'%inf[7])
    print('    bi0:', bi0)
    bs.seek(m_start+inf[10])
    bi1 = bs.read('%iH'%inf[9])
    print('    bi1:', bi1)
    bonemap = bi0+bi1

    
    bs.seek(m_start+inf[2])
    v_hd_ofs = bs.tell()
    v_hd = bs.read('4I')
    print('    v_hd:', v_hd, [v_hd_ofs])
    i_hd_ofs = bs.tell()
    i_hd = bs.read('4I')
    print('    i_hd:', i_hd, [i_hd_ofs])
    
    bs.seek(v_hd_ofs+v_hd[1])
    vbuf = bs.read(v_hd[3]*64)
    #test(vbuf)
    bi_buf = fixW(vbuf)
    
    bs.seek(i_hd_ofs+i_hd[1])
    ibuf = bs.read(i_hd[3]*2)
    bs.seek(m_start+inf[0])

    rapi.rpgSetBoneMap(bonemap)
    rapi.rpgSetName("g1_mesh_"+str(x))
    #if usePreSkin:
    #    _vbuf = toskin(vbuf, bones, bonemap)
    #    rapi.rpgBindPositionBuffer(_vbuf, noesis.RPGEODATA_FLOAT, 12)
    #else:
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 64)

    rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 64, 12)
    rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 64, 24)
    #rapi.rpgBindBoneIndexBuffer(bi_buf,noesis.RPGEODATA_USHORT,8,4)
    #rapi.rpgBindBoneWeightBufferOfs(vbuf,noesis.RPGEODATA_FLOAT,64,48,4)
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, i_hd[3], noesis.RPGEO_TRIANGLE_STRIP)

def fixW(vbuf):
    bi_buf = b''
    bs = NoeBitStream(vbuf)
    for x in range(len(vbuf)//64):
        bs.seek(32,1)
        bi = [int((i+60)//3) for i in bs.read('4f')]
        #print(bi)
        bi_buf += noePack('4H', *bi)
        bs.seek(16,1)
    return bi_buf
    
    all = set(all)
    print(all)

def test(vbuf):
    all = []
    bs = NoeBitStream(vbuf)
    for x in range(len(vbuf)//64):
        bs.seek(32,1)
        all += list(bs.read('4f'))
        bs.seek(16,1)
    
    all = set(all)
    print(all)
    