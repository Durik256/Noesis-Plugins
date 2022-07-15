#by Durik256 28.01.2022 for xentax.com
#only skeleton and anim
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("mount9_a", ".smz")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    if len(data) < 0x80:
        return 0
    bs = NoeBitStream(data)
    bs.seek(2, NOESEEK_ABS)
    if noeAsciiFromBytes(bs.readBytes(bs.readShort())) != 'SMZ_Actor':
        return 0
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(2, NOESEEK_ABS)
    header = noeAsciiFromBytes(bs.readBytes(bs.readShort()))
    unk = bs.readByte()
    frame_count = bs.readInt()
    bs.seek(8, NOESEEK_REL)
    anim_count = bs.readInt()
    
    for x in range(anim_count):
        name = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
        name2 = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
        start_frame = bs.readInt()
        end_frame = bs.readInt()
        event = bs.readInt()

        for y in range(event):
            name_event = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
            name_event2 = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
            event_frame = bs.readInt()
            bs.readByte()#[01]
        bs.readByte()#[01]
    
    # bones
    boneCount = bs.readInt()
    bones = []
    matList = []
    for i in range(0, boneCount):
        boneName = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
        parentName = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
        frame = bs.readInt()
        boneMats = []
        if frame > 0:
            #startFrame = 0 # 0-167
            #bs.seek(startFrame*0xC, NOESEEK_REL)
            boneMat = []
            for x in range(frame_count):
                boneMat.append(NoeVec3.fromBytes(bs.readBytes(12)))
            bs.readInt()
            
            for x in range(frame_count):                
                rot = NoeQuat.fromBytes(bs.readBytes(16)).toMat43().transpose()
                rot[3] = boneMat[x]
                boneMat[x] = rot
            boneMats+=boneMat
        else:
            bs.seek(4, NOESEEK_REL)
            boneMats=[NoeMat43()]*frame_count

        bs.readShort()
        unk_byte = -1
        while unk_byte != 1:
            unk_byte = bs.readByte()   
        
        
        bones.append(NoeBone(i, boneName, boneMats[0], parentName))
        matList.append(boneMats)

    newMotionMatrix = []

    for x in range(frame_count):
        for y in range(len(bones)):
            parentIndex = GetParentIndex(bones[y].parentName,bones)
            if parentIndex != -1:
                newMotionMatrix.append(matList[y][x]*matList[parentIndex][x].inverse())#bones[parentIndex].getMatrix().inverse()
            else:
                newMotionMatrix.append(matList[y][x])
    #newMotionMatrix = []
    #for y in range(len(bones)):
        #parentIndex = GetParentIndex(bones[y].parentName,bones)
        #newMotionMatrix.append(bones[y].getMatrix()*bones[parentIndex].getMatrix().inverse())
        
    anim = NoeAnim("anim", bones, frame_count, newMotionMatrix, 30)
    
    mdl = NoeModel()
    mdl.setBones(bones)
    mdl.setAnims([anim])
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 180 0")
    return 1
    
def GetParentIndex (parentName, arr):
    for i,bone in enumerate(arr):
        if bone.name == parentName:
            return i
    return -1 