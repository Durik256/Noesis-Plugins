from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Ridge Racer Unbounded", ".bmap")#45_pre_order
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    return 1

def CheckType(data):
    if data[:4] != b'bmap':
        return 0
    return 1
    
def LoadRGBA(data, texList):
    bs = NoeBitStream(data,1)
    hd = bs.read('>4I')
    print(hd)
    bs.seek(hd[3],1)#path
    hd = bs.read('>3I')
    
    
    tx = rapi.loadTexByHandler(bs.read(hd[2]), '.dds')
    texList.append(tx)
    return 1