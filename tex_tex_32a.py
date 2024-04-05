#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Screamer 4x4", ".tex;.32a;.map;.rgb")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    #noesis.logPopup()
    return 1

def CheckType(data):
    return 1
    
def LoadRGBA(data, texList):
    ext = os.path.splitext(rapi.getInputName())[1].lower()
    wh = 256
    
    if ext == '.tex':
        inf = noeUnpack('5I', data[:20])
        res = {0:256, 1:128, 2:64, 3:32, 4:16, 5:8, 6:4}
        wh = res[inf[1]]
        print(inf, inf[1:4], 'wh:',wh)
        
        if inf[3] == 11:
            fmt = 'b5g5r5a1'
        elif inf[3] == 10:
            fmt = 'b5g6r5'
        elif inf[3] == 8:
            fmt = 'r8a8'#?
        elif inf[3] == 2:
            fmt = 'r8'#L?
        elif inf[3] == 3:
            fmt = 'r8'#L?
        
        data = rapi.imageDecodeRaw(data[20:], wh, wh, fmt)
        
    elif ext == '.32a' or ext == '.map':
        data = rapi.imageDecodeRaw(data, wh, wh, 'r8g8b8a8')
    
    elif ext == '.rgb':
        data = rapi.imageDecodeRaw(data, wh, wh, 'r8g8b8')

    texList.append(NoeTexture(rapi.getInputName(), wh, wh, data, noesis.NOESISTEX_RGBA32))
    return 1
