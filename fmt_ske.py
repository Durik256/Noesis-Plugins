#by Durik256 for xentax.com 07.03.2022
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Battlefield 2 (2005)",".ske")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadSkeleton)	
    return 1
    
def CheckType(data):
    bs = NoeBitStream(data)
    if bs.readInt() != 2:
        return 0
    return 1

def LoadSkeleton(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(4)
    cBones = bs.readUInt()
    
    bones = []
    for x in range(cBones):
        boneName = noeAsciiFromBytes(bs.readBytes(bs.readUShort()))
        parent = bs.readShort()

        rot = NoeQuat.fromBytes(bs.readBytes(16))
        pos = NoeVec3.fromBytes(bs.readBytes(12))
        
        if pos.length() > 999:
            pos = NoeVec3()
            rot = NoeQuat()
        
        mat = rot.toMat43()#.swapHandedness(2)
        mat[3] = pos
        
        bones.append(NoeBone(x, boneName, mat, None, parent))
    
    for x in bones:
        if x.parentIndex != -1:
            x.setMatrix(x.getMatrix()*bones[x.parentIndex].getMatrix())
    
    mdlList.append(NoeModel([],bones))
    return 1