#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("World Of Goo 2", ".ktx")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    return 1

def CheckType(data):
    if data[:8] != b"\xABKTX 11\xBB":
        return 0 
    return 1
    
def LoadRGBA(data, texList):
    bs = NoeBitStream(data)
    h = bs.read('17I')
    w, h, s = h[9], h[10], h[16]

    data = bs.read(s)
    texList.append(NoeTexture(rapi.getInputName(), w, h, data, noesis.NOESISTEX_RGBA32))
    return 1