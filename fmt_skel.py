from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("yingxiong skeleton",".skel")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadSkeleton)	
    return 1
    
def CheckType(data):
    bs = NoeBitStream(data)
    magic = bs.readInt()
    if magic != 100 and magic != 1:
        return 0
    return 1

def LoadSkeleton(data, mdlList):
    bs = NoeBitStream(data)
    type = bs.readInt()
    #bs.seek(4)
    cBones = bs.readUInt()
    
    bones = []
    for i in range(cBones):
        boneName = noeAsciiFromBytes(bs.readBytes(bs.readUInt()))
        parent = bs.readInt()
        if type == 100:
            position = NoeVec3([bs.readHalfFloat() for x in range(3)])
            mat = NoeQuat([bs.readHalfFloat() for x in range(4)]).toMat43()
        else:
            position = NoeVec3.fromBytes(bs.readBytes(12))
            mat = NoeQuat.fromBytes(bs.readBytes(16)).toMat43()
        mat[3] = position
        bones.append(NoeBone(i, boneName, mat, None, parent))
    
    mdlList.append(NoeModel([],bones))
    return 1
    
    