#by Durik256
#not complete
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Mortal Kombat: Shaolin Monks (PS2)", ".mk")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    return 1
    
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    result = [i for i in findall(b'\x04\x04\x00\x01', data)]
    if result:
        result += [bs.getSize()]
    
    for i,x in enumerate(result[:-1]):
        bs.seek(x)
        vnum = bs.read('56B')
        print(vnum)
        vnum = vnum[40]
        end_vbuf = data.rfind(b'\x00\x00\x00\x17', bs.tell(), result[i+1])
        stride = min((end_vbuf - bs.tell()) // vnum, 48)
        print(i, [x], 'vnum:',vnum, 'stride:', stride)

        vbuf = bs.read(stride*vnum)

        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, stride)
        rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, 16)
        if stride == 48:
            rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, vnum, noesis.RPGEO_TRIANGLE_STRIP)
        else:
            ibuf = createFaces(vbuf, vnum, stride)
            rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, len(ibuf)//2, noesis.RPGEO_TRIANGLE_STRIP)
        rapi.rpgClearBufferBinds()
    
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default','')]))
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 -90 -90")
    return 1

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)
      
def createFaces(buf, vnum, stride):
    bs = NoeBitStream(buf)
    ibuf, temp = b'', False
    for x in range(vnum):
        bs.seek(x*stride+12)
        if bs.readUShort() & 0x8000:
            if not temp:
                ibuf += noePack('h', -1)
            temp = not temp
        ibuf += noePack('H', x)
    return ibuf