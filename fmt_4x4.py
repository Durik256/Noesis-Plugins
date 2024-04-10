#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Screamer 4x4", ".dat")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    #noesis.logPopup()
    return 1

def CheckType(data):
    return 1

def LoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    dir = os.path.dirname(rapi.getInputName())
    
    try:
        data = rapi.loadIntoByteArray(os.path.join(dir, 'verticle.dat'))
        bs = NoeBitStream(data)
        vnum = bs.readUShort()
        vert = []
        for x in range(vnum):
            vert.append(bs.read(12))
    except:
        print('Error load verticle.dat')
        return 0

    faces = []
    try:
        data = rapi.loadIntoByteArray(os.path.join(dir, 'faces.dat'))
        bs = NoeBitStream(data)
        inum = bs.readUShort()
        for x in range(inum):
            faces.append(bs.read('3H'))
    except:
        print('Error load faces.dat')
        return 0
        
    uvs = []
    try:
        data = rapi.loadIntoByteArray(os.path.join(dir, 'mapcoord.dat'))
        bs = NoeBitStream(data)

        for x in range(inum):
            a,b,c = [bs.read(8) for j in range(3)]
            uvs.append(c+b+a)#(bs.read(24))
    except:
        print('Error load mapcoord.dat, generate zero UVs.')
        for x in range(inum):
            uvs.append(b'\x00'*24)
    
    norm = []
    try:
        data = rapi.loadIntoByteArray(os.path.join(dir, 'norms.dat'))
        bs = NoeBitStream(data)

        for x in range(inum):
            norm.append(bs.read(36))
    except:
        print('Error load norms.dat')
    
    matsID = []
    try:
        data = rapi.loadIntoByteArray(os.path.join(dir, 'textures.dat'))
        matsID = noeUnpack(str(inum)+'H', data)
    except:
        print('Error load textures.dat, use 1 material.')
        matsID = [0]*inum
    
    rapi.rpgSetUVScaleBias(NoeVec3([1,-1,1]), None)
    for x in range(inum):
        vbuf = b''
        for j in faces[x]:
            vbuf += vert[j]
        
        uvbuf = uvs[x]
        
        rapi.rpgSetMaterial('mat_%i'%matsID[x])
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
        if norm:
            rapi.rpgBindNormalBuffer(norm[x], noesis.RPGEODATA_FLOAT, 12)
        
        rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 8)
        rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, 3, noesis.RPGEO_TRIANGLE)

    rapi.rpgOptimize()
    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    
    mdlList.append(mdl)
    return 1

'''
def LoadModel(files, mdlList):
    ctx = rapi.rpgCreateContext()
    data = None
    
    dir = os.path.dirname(rapi.getInputName())
    vbuf = rapi.loadIntoByteArray(os.path.join(dir, 'verticle.dat'))
    ibuf = rapi.loadIntoByteArray(os.path.join(dir, 'faces.dat'))
    
    vnum = noeUnpack('H', vbuf[:2])[0]
    inum = noeUnpack('H', ibuf[:2])[0]*3
    
    rapi.rpgBindPositionBuffer(vbuf[2:], noesis.RPGEODATA_FLOAT, 12)
    rapi.rpgCommitTriangles(ibuf[2:], noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)

    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdlList.append(mdl)
    return 1
'''
