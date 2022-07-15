from inc_noesis import *

def registerNoesisTypes():
   handle = noesis.register("Age Of Wulin boness", ".xskt")
   noesis.setHandlerTypeCheck(handle, noepyCheckType)
   noesis.setHandlerLoadModel(handle, noepyLoadModel)
   #noesis.logPopup()
   return 1

def noepyCheckType(data):
    if len(data) < 0x80:
        return 0
    bs = NoeBitStream(data)
    if noeAsciiFromBytes(bs.readBytes(4)) != 'XSAM':
        return 0
    return 1       

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    EndFile = bs.getSize()-4
    Header = noeAsciiFromBytes(bs.readBytes(4))
    Ver = bs.readInt()
    Unk1 = bs.readInt()
    FileNameSize = bs.readInt()
    FileName = noeAsciiFromBytes(bs.readBytes(FileNameSize))
    Unk2 = bs.readInt()
    AnimCount = bs.readInt()
    FPS = bs.readFloat()
    bs.seek(0x18, NOESEEK_REL)

    bones = []    
    BNArr = []
    BId = bs.readInt()
    
    while bs.getOffset() < EndFile:
        bonesNameSize = bs.readInt()
        bonesName = noeAsciiFromBytes(bs.readBytes(bonesNameSize))
        bonesType = bs.readInt()
        if bonesType == 4:
            AnimType = bs.readInt()
            AnimId = bs.readInt()
            bonesposition = NoeVec3.fromBytes(bs.readBytes(12))
            bonesRotation = NoeQuat.fromBytes(bs.readBytes(16)).toMat43()
            bonesscale = NoeVec3.fromBytes(bs.readBytes(12))
            if AnimType == 0:
                for x in range(AnimCount):
                    rx1 = bs.readShort()
                    ry1 = bs.readShort()
                    rz1 = bs.readShort()

            if AnimType == 1:
                for x in range(1, AnimCount):
                    rx = bs.readShort()
                    ry = bs.readShort()
                    rz = bs.readShort()
                    a11 = bs.readFloat() 
                    a12 = bs.readFloat()
                    a13 = bs.readFloat()

            if AnimType == 2:
                for x in range(AnimCount):
                    rx1 = bs.readShort()
                    ry1 = bs.readShort()
                    rz1	= bs.readShort()
                    a11 = bs.readFloat()
                    a12 = bs.readFloat()
                    a13 = bs.readFloat()

            if AnimType == 8:
                for x in range(3):
                    rx = bs.readShort()
                    ry = bs.readShort()
                    rz = bs.readShort()

            if AnimType == 10:
                for x in range(3):
                    rx = bs.readShort()
                    ry = bs.readShort()
                    rz = bs.readShort()
                    a11 = bs.readFloat()
                    a12 = bs.readFloat()
                    a13 = bs.readFloat()

        if bonesType == 3:
            AnimId = bs.readInt()  
            bonesposition = NoeVec3.fromBytes(bs.readBytes(12))
            bonesRotation =  NoeQuat.fromBytes(bs.readBytes(16)).toMat43()
            bonesscale = NoeVec3.fromBytes(bs.readBytes(12))

            if AnimId == 6:
                bs.seek(0x36, NOESEEK_REL) 

        num_child = bs.readInt() 
        bonesMat = bonesRotation.transpose()
        bonesMat[3] = bonesposition
        bone = NoeBone(len(bones), bonesName, bonesMat, None,-1)
        bones.append(bone)
        
        if BNArr:
            bone.parentName = BNArr[-1].name
            bone.setMatrix(bone.getMatrix()* BNArr[-1].getMatrix())
            BNArr.pop()

        for j in range(num_child): BNArr.append(bone)
    
    mdl = NoeModel()
    mdl.setBones(bones)
    mdlList.append(mdl)

    return 1