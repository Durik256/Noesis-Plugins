#by Durik 256
#change or add extension 'tx0' to your files
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("White Album 2 (PS3)", ".tx0")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    return 1

def CheckType(data):
    if data[:4] != b'\x02\x01\x01\xFF':
        return 0
    return 1
    
def LoadRGBA(data, texList):
    bs = NoeBitStream(data,1)
    bs.seek(4)
    size = bs.readUInt()
    bs.seek(24)
    type = bs.readUInt()
    bs.seek(32)
    w, h = bs.read('>2H')
    
    bs.seek(128)
    data = bs.read(size)
    
    if type == 2248212992:
        #DXT1
        data = rapi.imageDecodeDXT(data, w, h, noesis.NOESISTEX_DXT1)
        
    elif type == 2768306688:
        #RGBA8
        data = rapi.imageDecodeRaw(data, w, h, 'a8r8g8b8')
    
    elif type == 2231435776:
        #RGBA8 Morton
        data = rapi.imageDecodeRaw(data, w, h, 'a8r8g8b8')
        data = rapi.imageFromMortonOrder(data, w, h, 4)

    else:
        print('Error unknow type!')
        return 0
    
    texList.append(NoeTexture(rapi.getInputName(), w, h, data, noesis.NOESISTEX_RGBA32))
    return 1