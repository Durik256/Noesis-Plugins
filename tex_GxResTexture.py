#bu Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Dragon Star Defense", ".GxResTexture")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    return 1

def CheckType(data):
    return 1
    
def LoadRGBA(data, texList):
    bs = NoeBitStream(data)

    hd = bs.read('6H')
    w,h = hd[:2]

    data = bs.read(w*h//2)
    data = rapi.imageDecodeDXT(data, w, h, noesis.NOESISTEX_DXT1)
        
    texList.append(NoeTexture(rapi.getInputName(), w, h, data, noesis.NOESISTEX_RGBA32))    
    return 1
