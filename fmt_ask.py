#by Durik256
from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("PES19/21", ".ask")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadModel(handle, noepyLoadSkel)
	return 1

def noepyCheckType(data):
    return 1
    
def noepyLoadSkel(data, mdlList):
    bs = NoeBitStream(data)
    
    bs.seek(4)#1
    bnum = bs.readUInt()

    bones = []
    for x in range(bnum):
        bs.seek(4,1)
        nofs = bs.readUInt()
        parent = bs.readInt()
        
        cpos = bs.tell()
        bs.seek(cpos + nofs - 8)
        name = bs.readString()
        bs.seek(cpos)
        
        pos = NoeVec3.fromBytes(bs.read(12))
        #rot = NoeQuat.fromBytes(bs.read(16))
        bs.seek(20,1)
        mat = NoeMat43()
        mat[3] = pos
        bones.append(NoeBone(x,name,mat,None,parent))
    
    if bones:
        bones = rapi.multiplyBones(bones)
    
    mdl = NoeModel()
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1