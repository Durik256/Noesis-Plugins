#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Dawn light", ".stexture")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    return 1
    
def CheckType(data):
    if data[:4] == 'SATN':
        return 0
    return 1
    
def LoadRGBA(data, texList):
    bs = NoeBitStream(data)
    bs.seek(8)
    name = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
    bs.seek(100,1)
    w, h = bs.readInt(), bs.readInt()
    size = bs.readInt()
    
    data = rapi.imageDecodeETC(bs.readBytes(size), w, h, 'RGB')
    
    texList.append(NoeTexture(name, w, h, data, noesis.NOESISTEX_RGBA32))
    return 1