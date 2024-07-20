#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("My Om Nom", ".msh")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    return 1   

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()

    for x in range(5):
        u = bs.readUShort()
        if not u:
            break
        bs.seek(-2,1)
        
        stride, type, buf = getBuf(bs)
        if u == 513:
            rapi.rpgBindPositionBuffer(buf, type, stride)
        elif u == 1:
            rapi.rpgBindUV1Buffer(buf, type, stride)
        elif u == 257:
            rapi.rpgBindNormalBuffer(buf, type, stride)

    numSM = bs.readUInt24()
    for _ in range(numSM):
        stride, type, buf = getBuf(bs)
        u = bs.read('=IHB')
        fmt = 10 if u[0] else 2

        rapi.rpgSetName('mesh_%i'%_)
        rapi.rpgCommitTriangles(buf,type,len(buf)//stride, fmt)

    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 -90 0")
    return 1

types = {6150:0, 4102:0, 6146:3, 2051:4 }
def getBuf(bs):
    u = bs.read('=HB2H2I')
    try:
        t = types[u[-3]]
    except:
        t = None
    return u[-1]//u[-2],t, bs.read(u[-1])

# 6150 - vec3 float
# 4102 - vec2 float
# 2051 - scalar short 
# 6146 - vec3 short
