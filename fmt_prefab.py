#by Durik256
from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Uta no Prince-sama♪ LOVE EMOTION", ".prefab")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadModel(handle, noepyLoadModel)
	return 1

def noepyCheckType(data):
    return 1
    
    
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
  
    o = [i for i in findall(b'\x09\x00\x00\x00Triangles', data)]
    
    for x in o:
        bs.seek(x - 4)
        rapi.rpgSetName('m_%i'%x)
        #bs.seek(x + 131)
        #l = bs.read(bs.readUInt()).decode().replace('MAT__','').replace('__CGFX','')
        #rapi.rpgSetName(l)
        #bs.seek(40,1)
        
        b0, b1, b2 = b'', b'', b''
        while True:
            u, sl = bs.read('2I')
            if not sl:
                break
            l = bs.read(sl)
            bs.seek(118,1)
            s = bs.readUInt()
            cp = bs.tell()
            
            if l == b'Positions':
                b0 = bs.read(s)
            elif l == b'Triangles':
                b2 = bs.read(s)
            elif l == b'Uvs3':
                b1 = bs.read(s)
            bs.seek(cp+s)
                
        rapi.rpgBindPositionBuffer(b0, noesis.RPGEODATA_FLOAT, 12)
        if b1:
            rapi.rpgBindUV1Buffer(b1, noesis.RPGEODATA_USHORT, 4)
        rapi.rpgCommitTriangles(b2, noesis.RPGEODATA_USHORT, len(b2)//2, noesis.RPGEO_TRIANGLE)
        rapi.rpgClearBufferBinds()

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    mdlList.append(mdl)
    return 1

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)
    
'''
def noepyLoadModel_OLD(data, mdlList):
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
'''
