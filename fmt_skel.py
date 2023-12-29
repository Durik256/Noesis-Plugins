#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Lost Saga", ".skl")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    if data[:3] != b'SKL':
        return 0
    return 1   
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(8)#SKL, unk

    bones = []
    for x in range(bs.readUInt()):
        name = readFixedString(bs)
        bs.seek(56,1)
        #m_vLocal = NoeVec3.fromBytes(bs.read(12))
        #m_qtLocal = NoeQuat.fromBytes(bs.read(16))
        #m_vBipedSpace = NoeVec3.fromBytes(bs.read(12))
        #m_qtBipedSpace = NoeQuat.fromBytes(bs.read(16))
        m_matObjectTM = NoeMat44.fromBytes(bs.read(64)).toMat43()
        parent = readFixedString(bs)
        for y in range(bs.readUInt()):
            child = readFixedString(bs)
        bones.append(NoeBone(x,name,m_matObjectTM,parent))

    mdl = NoeModel()
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1
    
def readFixedString(bs):
    return bs.readBytes(bs.readUInt()).decode()
