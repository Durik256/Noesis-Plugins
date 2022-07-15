#by Durik256 15.03.2022 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Shaiya",".ani")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    header(bs)
    
    numFrame = bs.readInt()
    numBone = bs.readShort()

    bones, frmsData = [], []
    for x in range(numBone):
        parent = bs.readInt()
        mat = NoeMat44.fromBytes(bs.readBytes(64)).toMat43()
        bones.append(NoeBone(x,"bone_"+str(x), mat, None, parent))
        frmsData.append(Data(x))
        
        numRot = bs.readInt()
        for y in range(numRot):
            idKey = bs.readInt()/30
            rot = NoeQuat.fromBytes(bs.readBytes(16)).transpose()
            frmsData[-1].rotKeyList.append(NoeKeyFramedValue(idKey, rot))
        
        numPos = bs.readInt()
        for y in range(numPos):
            idKey = bs.readInt()/30
            pos = NoeVec3.fromBytes(bs.readBytes(12))
            frmsData[-1].posKeyList.append(NoeKeyFramedValue(idKey, pos))
    
    #Animation
    animBones = []
    for x in frmsData:
        b = NoeKeyFramedBone(x.id)
        b.setRotation(x.rotKeyList)
        b.setTranslation(x.posKeyList)
        animBones.append(b)

    anim = NoeKeyFramedAnim("anim", bones, animBones, 30)
    
    mdl = NoeModel()
    mdl.setBones(bones)
    mdl.setAnims([anim])
    mdlList.append(mdl)
    return 1

def header(bs):
    if bs.readInt() > 0:
        bs.seek(10)#ANI_V2 and int 0
    return 1
 
class Data:
    def __init__(self, id):
        self.id = id
        self.posKeyList = []
        self.rotKeyList = []