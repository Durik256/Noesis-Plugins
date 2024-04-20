#by Durik256
from inc_noesis import *
import zlib

def registerNoesisTypes():
    handle = noesis.register("shumen & Talisman Online previous generation", ".rle")#ru la shen zhang
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    return 1

def CheckType(data):
    return 1
    
def LoadRGBA(data, texList):
    size = noeUnpack('I', data[:4])
    data = zlib.decompress(data[4:])
    u,w,h = noeUnpack('3H', data[:6])

    data = rapi.imageDecodeRaw(data[6:], w, h, 'r8g8b8')
    texFmt = noesis.NOESISTEX_RGBA32
    
    texList.append(NoeTexture(rapi.getInputName(), w, h, data, noesis.NOESISTEX_RGBA32))
    return 1