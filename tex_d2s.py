#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("scion of fate online", ".d2s")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    return 1
    
def CheckType(data):
    return 1
    
def LoadRGBA(data, texList):
    bs = NoeBitStream(data)
    data = bs.readBytes(size)
    texList.append(rapi.loadTexByHandler(data, '.DDS'))  
    return 1