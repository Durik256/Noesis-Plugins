#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("ben 10 omniverse", ".et_decomp")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data,1)
    ctx = rapi.rpgCreateContext()
    rapi.rpgSetEndian(1)
    
    result = [i for i in findall(b'\x00\x00\x00\x01\x00\x02', data)]
    for x in result:
        bs.seek(x+6)
        f = bs.readUByte()
        print('f::', f)
        if f:
            print('skip result::', x)
            continue
        bs.seek(-11,1)
        if bs.readUShort():
            print('skip result::', x)
            continue
        print('cur result::', x)
        bs.seek(-2,1)
        cpos = bs.tell()
        inum = bs.readUInt()
        if not inum:
            continue
        print('inum:',[inum],[bs.tell()])
        ibuf = bs.read(inum*2)
        vnum = max(noeUnpack('>%iH'%inum, ibuf))+1
        print('vnum:',[vnum],[bs.tell()])
        bs.seek(cpos)
        vstride, uvstride = 8, 20
        bs.seek(-(vnum*(vstride+uvstride)+4),1)
        real_vnum = bs.readUInt()
        print('real_vnum:',[real_vnum],[bs.tell()])
        if vnum != real_vnum:
            print('bad firs vnum::', x)
            vstride, uvstride = 24, 8
            bs.seek(cpos)
            bs.seek(-(vnum*(vstride+uvstride)+4),1)
            real_vnum = bs.readUInt()
            if vnum != real_vnum:
                print('bad vnum, skip result::', x)
                continue
        
        vbuf = bs.read(vnum*vstride)
        uvbuf = bs.read(vnum*uvstride)
        
        try:
            rapi.rpgSetName('mesh_%i'%x)
            rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_SHORT, vstride)
            rapi.rpgBindUV1BufferOfs(uvbuf, noesis.RPGEODATA_SHORT, uvstride, 0)
            rapi.rpgBindUV2BufferOfs(uvbuf, noesis.RPGEODATA_SHORT, uvstride, 4)
            rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_USHORT,inum,noesis.RPGEO_TRIANGLE)
        except:
            rapi.rpgClearBufferBinds()
            print('ERROR::', x)

    texList = []
    LoadTexture(data, bs, texList)

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    
    mdl.setModelMaterials(NoeModelMaterials(texList, [NoeMaterial('default','')]))
    mdlList.append(mdl)
    return 1
    
def LoadTexture(data, bs, texList):
    result = [i for i in findall(b'\x00\x01\x00\x00\x00\x00\x00\x00\xBB\xBB\xBB\xBB', data)]
    print('tx_result:', result)
    for x in result:
        bs.seek(x+16)
        if not bs.readUByte() and 257 == bs.readUInt():
            width, height, fmt, size = bs.read('>4I')
            print('tx::', width, height, fmt, size)
            data = bs.read(size)
            bs.seek(x-72)
            name = bs.read(36).replace(b'\x00',b'').decode('ascii','ignore')
            if fmt == 11:
                fmt = noesis.NOESISTEX_DXT1
                if size >= (width * height):
                    fmt = noesis.NOESISTEX_DXT5
            elif fmt == 10:
                if size >= (width * height):
                    data = rapi.imageDecodeDXT(data, width, height, noesis.FOURCC_DXT5)
                else:
                    data = rapi.imageDecodeDXT(data, width, height, noesis.FOURCC_DXT1)
                fmt = noesis.NOESISTEX_RGBA32
            elif fmt == 9:
                #FOURCC_BC5
                data = rapi.imageDecodeDXT(data, width, height, noesis.FOURCC_BC3)
                fmt = noesis.NOESISTEX_RGBA32
            else:
                print('unknow fmt', fmt)
                continue

            texList.append(NoeTexture(name, width, height, data, fmt))

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)
