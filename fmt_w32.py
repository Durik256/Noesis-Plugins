#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Disney Princess: Enchanted Journey", ".w32")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    return 1   
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()

    result = [i+4 for i in findall(b'\x0B\x09\x03\x00', data)]
    result_tx = [i+4 for i in findall(b'\x80\x88\x83\x41', data)]

    for x in result:
        try:
            bs.seek(x)
            h = bs.read('6I2H24I')
            vnum, inum, unum = h[0], h[4], h[6]

            vbuf = bs.read(vnum*12)
            skipZero(bs)
            
            bs.seek(vnum*12,1)#nbuf
            skipZero(bs)

            uvbuf = bs.read(vnum*8)
            skipZero(bs)
            
            bs.seek(unum*36,1)

            ibuf = bs.read(inum*2)
            
            rapi.rpgSetName('mesh_%i'%x)
            rapi.rpgBindPositionBuffer(vbuf,noesis.RPGEODATA_FLOAT,12)
            rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 8)
            rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_USHORT,inum,noesis.RPGEO_TRIANGLE_STRIP)
            rapi.rpgClearBufferBinds()
        except:
            rapi.rpgClearBufferBinds()
          
    texList = []
    for x in result_tx:
        try:
            bs.seek(x)
            u0, w, h, u1 = bs.read('4H29I')[:4]
            data = bs.read(w*h*3)
            
            data = rapi.imageDecodeRaw(data, w, h, 'r8g8b8')
            texList.append(NoeTexture('tx_%i'%x, w, h, data, noesis.NOESISTEX_RGBA32))  
        except:
            pass

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    mdl.setModelMaterials(NoeModelMaterials(texList, [NoeMaterial('default', '')]))
    mdlList.append(mdl)
    return 1

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)

def skipZero(bs):
    cpos = bs.tell()
    while True:
        if bs.readByte() != 0:
            bs.seek(-1,1)
            break
    bs.seek(cpos+(((bs.tell()-cpos)//4)*4))