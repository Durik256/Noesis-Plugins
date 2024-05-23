#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Crimson Skies (2003)", ".x")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    return 1

def noepyLoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    bs = NoeBitStream(data)
    rapi.rpgSetOption(noesis.RPGOPT_SWAPHANDEDNESS, 1)
    
    global nodes, materials
    nodes, materials = [], []
    
    bs.seek(32)
    readNode(bs)
    
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    
    #if nodes:
    #    nodes = rapi.multiplyBones(nodes)
    
    mdl.setBones(nodes)
    mdl.setModelMaterials(NoeModelMaterials([], materials))
    mdlList.append(mdl)
    return 1
    
def readNode(bs,parent=None,ptrfm=None):
    name = readString(bs)
    trfm = NoeMat43.fromBytes(bs.read(48)).transpose()
    if ptrfm:
        trfm *= ptrfm
    bbox = bs.read('6f')
    bs.read(4)# 3
    
    rapi.rpgSetName(name)
    rapi.rpgSetTransform(trfm) 
    for x in range(bs.readUInt()):
        readMesh(bs)
    
    nodes.append(NoeBone(len(nodes),name,trfm,parent))
    
    for x in range(bs.readUInt()):
        readNode(bs,name,trfm)
    
def readMesh(bs):
    global counter
    u0 = bs.readUInt()
    clr = bs.read('4B')
    u1 = bs.readUInt()
    u2 = bs.read('>i')[0]

    mat_name = 'mat_%i'%len(materials)
    mat = NoeMaterial(mat_name, '')
    mat.setDiffuseColor(NoeVec4([clr[0]/255,clr[1]/255,clr[2]/255,clr[3]/255]))

    dict = {0:0, 1:1, 3:2, 7:3, 17:2, 15:4, 19:3, 23:4, 31:5}
    numTx = dict[u2]
    
    for x in range(numTx):
        tx_name = readString(bs)
        if not x: mat.setTexture(tx_name)
    
    materials.append(mat)

    vnum = bs.readShort()
    vbuf = bs.read(vnum*32)

    #bs.read('16B')
    _f = bs.read('4f')
    if bs.readUByte():
        bs.seek(bs.readShort() * 12 * 4, 1)
       
    inum = bs.readShort()
    ibuf = bs.read(inum*2)
    
    rapi.rpgSetMaterial(mat_name)
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 32)
    #rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_USHORT, 32, 16)
    fixUVs(vbuf, _f[0])
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
    rapi.rpgClearBufferBinds()

    bs.seek(2, 1) #FF
    strip = bs.readUShort()
    bs.seek(strip*2, 1)

    if bs.readByte() == 1:
        size=16
        numUnk= bs.readInt()
    else:
        size=28
        numUnk= bs.readShort()
    bs.seek(numUnk*size, 1)
   
def fixUVs(vbuf, uvScale):
    bs = NoeBitStream(vbuf)
    uvbuf = b''
    for x in range(len(vbuf)//32):
        bs.seek(16,1)
        u,v = bs.read('2h')
        bs.seek(12,1)
        uvbuf += noePack('2f', u*uvScale, v*uvScale)
        
    rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 8)
   
def readString(bs):
    return bs.read(bs.readUInt()).split(b'\x00')[0].decode('ascii', 'ignore')
