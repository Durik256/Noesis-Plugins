#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Winx Club [PC]", ".smo")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def CheckType(data):
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
        
    result = [(i+8) for i in findall(b'\xF0\x4C\xC3\x33SBOO', data)]
    
    for x in result:
        bs.seek(x)
        f = bs.readUByte()
        print('f:', f)
        if f == 225:
            bs.seek(21,1)
        elif f == 224:
            bs.seek(4,1)
        
        ih = bs.read('3I')
        print('ih:', ih, [bs.tell()])
        if ih[0] == 3:
            inum, ifmt = (ih[1]), noesis.RPGEO_TRIANGLE_STRIP
            ibuf = bs.read(inum*2)
            add = bs.read('2H')
            if add[0] != 52685 and add[1] != 52685:
                ibuf += noePack('2H', *add)
                inum += 2
        elif ih[0] == 2:
            inum, ifmt = (ih[1]*3), noesis.RPGEO_TRIANGLE
            ibuf = bs.read(inum*2)

        print('iend:', bs.tell())
        vh = bs.read('3I')
        print('vh:', vh, [bs.tell()])
        
        stride, uvOfs = None, 0
        if vh[0] == 2304:
            stride, uvOfs = 24, 16
        elif vh[0] == 2368:
            stride, uvOfs = 36, 28
        elif vh[0] == 2430:
            stride, uvOfs = 56, 48
        elif vh[0] == 6526:
            stride, uvOfs = 64, 48
        vbuf = bs.read(vh[1]*stride)
        
        rapi.rpgSetName('mesh_%i'%x)
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, stride)
        if uvOfs:
            rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, uvOfs)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, ifmt)
    
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 90 90")
    return 1
    
def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)