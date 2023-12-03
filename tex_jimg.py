from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Dragon ball", ".jimg")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    if data[:4] != b'jIMG': 
        return 0
    return 1
    
def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    bs.seek(8)

    imgWidth = bs.readUShort()
    imgHeight = bs.readUShort()
    bit = bs.readUByte()
    
    bs.seek(0)
    print([bs.readUByte() for x in range(128)])
    bs.seek(128)
    
    if bit == 11:
        data = bs.readBytes(imgWidth*imgHeight) 
        data = rapi.imageDecodePICA200ETC1(data, imgWidth, imgHeight, 1)
    if bit == 8:
        data = bs.readBytes(imgWidth*imgHeight//2) 
        data = rapi.imageDecodePICA200ETC1(data, imgWidth, imgHeight, 0)

    texFmt = noesis.NOESISTEX_RGBA32
        
    texList.append(NoeTexture(rapi.getInputName(), imgWidth, imgHeight, data, texFmt))
    return 1
    