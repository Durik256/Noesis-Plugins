#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("NASCAR", ".p3s")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    if data[:4] != b'\x70\x33\x52\x02':
        return 0
    return 1   

def noepyLoadRGBA(data, texList):
    texList.append(rapi.loadTexByHandler(b'DDS '+data[4:], '.DDS'))  
    return 1