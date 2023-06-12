#bu Durik256
#DDS textures only
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("overlord 2", ".prp")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    noesis.logPopup()
    return 1

def CheckType(data):
    return 1
    
def LoadRGBA(data, texList):
    bs = NoeBitStream(data)
    
    offsets = [(i+4) for i in findall(b'.dds', data)]
    
    for x in offsets:
        bs.seek(x + 138)

        w, h, type = bs.read('3I')
        print(w, h, type)
        
        if type == 7:
            fmt = noesis.NOESISTEX_DXT1
            print('offset:',bs.tell(), 'width:',w, 'height:',h, 'format: DXT1')
            data = bs.read(w*h//2)
        
        elif type == 11:
            fmt = noesis.NOESISTEX_DXT5
            print('offset:',bs.tell(), 'width:',w, 'height:',h, 'format: DXT5')
            data = bs.read(w*h*4)

        data = rapi.imageDecodeDXT(data, w, h, fmt)
        texList.append(NoeTexture(rapi.getInputName(), w, h, data, noesis.NOESISTEX_RGBA32))    
    
    return 1

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)