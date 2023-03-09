from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("AFK Arena", ".lzap")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    return 1

def CheckType(data):
    if data[:6] != b'LZ4PNG':
        return 0
    return 1
    
def LoadRGBA(data, texList):
    bs = NoeBitStream(data, 1)
    bs.seek(6)
    
    while bs.tell() < bs.getSize():
        size = bs.readUInt() - 4
        dest = bs.read('I')[0]
        if bs.tell() >= bs.getSize():
            break
        data = rapi.decompLZ4(bs.read(size), dest)
        
        tx = rapi.loadTexByHandler(data, '.pkm')
        texList.append(tx)
    return 1
