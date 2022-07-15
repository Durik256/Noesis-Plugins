from inc_noesis import *
import rapi

def registerNoesisTypes():
   handle = noesis.register("mesh", ".xmod")
   noesis.setHandlerTypeCheck(handle, noepyCheckType)
   noesis.setHandlerLoadModel(handle, noepyLoadModel)
   noesis.logPopup()
   return 1

def noepyCheckType(data):
    if len(data) < 0x80:
        return 0
    bs = NoeBitStream(data)
    if noeAsciiFromBytes(bs.readBytes(4)) != 'XVAM':
        return 0
    return 1
    
def IDfromName(arr,name):
    for i,b in enumerate(arr):
        if b.name == name:
            return i
    return -1

def noepyLoadModel(data, mdlList):
    bones = []
    dirPath = rapi.getDirForFilePath(rapi.getInputName())
    if(rapi.checkFileExists(dirPath+"tpose.xskt")):
        xsktData = rapi.loadIntoByteArray(dirPath+"tpose.xskt")
        xsktData = NoeBitStream(xsktData)
        bones = LoadSkeleton(xsktData)
        
    bs = NoeBitStream(data)
    EndFile = bs.getSize()
    MHeader = noeAsciiFromBytes(bs.readBytes(4))
    Version = bs.readInt()
    Unk1 = bs.readInt()
    NumObj = bs.readInt()
    FnameSize = bs.readInt()
    Fname = noeAsciiFromBytes(bs.readBytes(FnameSize))
    Unk3 = bs.readInt()
    Num1 = bs.readInt()
    bs.seek(0x1C, NOESEEK_REL)
    Unk2 = bs.readInt()
    
    mesh = []
    
    for obj in range(NumObj):
        ModelNameSize = bs.readInt()
        ModelName = noeAsciiFromBytes(bs.readBytes(ModelNameSize))
        Num2 = bs.readInt()
        Type1 = bs.readShort()
        Type2 = bs.readShort()
        
        bs.seek(0x44, NOESEEK_REL)
        SubCount = bs.readInt()
        
        for sub in range(SubCount):
            vertArray = []
            normArray = []
            Facearray = []
            UV_array = []
            Weight_array = []
            BoneMap = []
            BoneNamePosArray = []
            TexArray = []
            MNameSize = bs.readInt()
            MName = noeAsciiFromBytes(bs.readBytes(MNameSize))
            ModelId = bs.readInt()
            Unk4 = bs.readInt()
            VertexCount = bs.readInt()

            #mesh type 1
            if Type1 == 4101:
                curOffSet = bs.getOffset()
                bs.seek(VertexCount*32, NOESEEK_REL)
                uv = True
                if bs.readInt() > 65000:
                    uv = False
                bs.setOffset(curOffSet)
                    
                for x in range(VertexCount):
                    vertArray.append(NoeVec3.fromBytes(bs.readBytes(12)))
                    normArray.append(NoeVec3.fromBytes(bs.readBytes(12)))
                    if uv:
                        UV_array.append(NoeVec3([bs.readFloat(), bs.readFloat(), 0.0]))
            #mesh type 2
            if Type1 == 5381:
                for x in range(VertexCount):
                    getPos = bs.getOffset() + 56

                    vertArray.append(NoeVec3.fromBytes(bs.readBytes(12)))
                    normArray.append(NoeVec3.fromBytes(bs.readBytes(12)))

                    bi = NoeVec3.fromBytes(bs.readBytes(12))
                    t = NoeVec3.fromBytes(bs.readBytes(12))

                    UV_array.append(NoeVec3([bs.readFloat(), bs.readFloat(), 0.0]))

                    unk =  bs.readFloat()
                    bs.seek(getPos, NOESEEK_ABS)
            #mesh type 3
            if Type1 == 5397:
                for x in range(VertexCount):
                    getPos = bs.getOffset() + 60
                    vertArray.append(NoeVec3.fromBytes(bs.readBytes(12)))
                    normArray.append(NoeVec3.fromBytes(bs.readBytes(12)))

                    bi = NoeVec3.fromBytes(bs.readBytes(12))
                    t = NoeVec3.fromBytes(bs.readBytes(12))

                    UV_array.append(NoeVec3([bs.readFloat(), bs.readFloat(), 0.0]))
                        
                    bs.seek(getPos, NOESEEK_ABS)
            #face
            FaceCount = bs.readInt()
            Facearray = [bs.readUShort() for x in range(FaceCount)]
            
            #weight
            if EndFile-bs.getOffset() > VertexCount*32:
                WeightsStart = bs.getOffset()
                bs.seek(VertexCount*32, NOESEEK_REL)
                BoneMapSize = bs.readInt()
                BoneMap = noeAsciiFromBytes(bs.readBytes(BoneMapSize)).split('\0')
                if bones:
                    BoneNamePosArray = [0]
                    
                    for x in BoneMap[:-1]:
                        offset = BoneNamePosArray[-1] if BoneNamePosArray else 0
                        BoneNamePosArray.append(len(x) + offset+1)

                    bs.seek(WeightsStart, NOESEEK_ABS)
                    
                    for i in range(VertexCount):
                        bone1Off = bs.readInt()
                        B1Offset = (bone1Off)
                        for i in range(len(BoneNamePosArray)):
                            if BoneNamePosArray[i] == B1Offset:
                                B1Offset = i
                    
                        Bone1 = B1Offset
                        weight1 = bs.readFloat()
                        
                        bone2Off = bs.readInt()
                        B2Offset = (bone2Off)
                        for i in range(len(BoneNamePosArray)):
                            if BoneNamePosArray[i] == B2Offset:
                                B2Offset = i
                        
                        Bone2 = int(B2Offset)
                        weight2 = bs.readFloat()
                            
                        bone3Off = bs.readInt()
                        B3Offset = (bone3Off)
                        for i in range(len(BoneNamePosArray)):
                            if BoneNamePosArray[i] == B3Offset:
                                B3Offset = i
                        
                        Bone3 = int(B3Offset)
                        weight3 = bs.readFloat()
                        
                        bone4Off = bs.readInt()
                        B4Offset = (bone4Off)
                        for i in range(len(BoneNamePosArray)):
                            if BoneNamePosArray[i] == B4Offset:
                                B4Offset = i
                                
                        Bone4 = int(B4Offset)
                        weight4 = bs.readFloat()
                        
                        weights = ([],[])
                        maxweight = 0
                        
                        if weight1 != 0:
                            maxweight = maxweight + weight1
                        if weight2 != 0:
                            maxweight = maxweight + weight2
                        if weight3 != 0:
                            maxweight = maxweight + weight3
                        if weight4 != 0:
                            maxweight = maxweight + weight4

                        if maxweight != 0:
                              if bone1Off != -1:
                                w1 = float(weight1)
                                if len(BoneMap) < len(bones):
                                    weights[0].append(IDfromName(bones,BoneMap[Bone1]))
                                else:
                                    weights[0].append(Bone1)
                                weights[1].append(w1)

                              if bone2Off != -1:
                                w2 = float(weight2)
                                if len(BoneMap) < len(bones):
                                    weights[0].append(IDfromName(bones,BoneMap[Bone2]))
                                else:
                                    weights[0].append(Bone2)
                                weights[1].append(w2)

                              if bone3Off != -1:
                                w3 = float(weight3)
                                if len(BoneMap) < len(bones):
                                    weights[0].append(IDfromName(bones,BoneMap[Bone3]))
                                else:
                                    weights[0].append(Bone3)
                                weights[1].append(w3)

                              if bone4Off != -1:
                                w4 = float(weight4)
                                if len(BoneMap) < len(bones):
                                    weights[0].append(IDfromName(bones,BoneMap[Bone4]))
                                else:
                                    weights[0].append(Bone4)
                                weights[1].append(w4)
                        Weight_array.append(NoeVertWeight(weights[0],weights[1]))

            if SubCount > 1:
                bs.seek(0x18, NOESEEK_REL)
                bs.seek(bs.readInt(), NOESEEK_REL)
                bs.seek(bs.readInt(), NOESEEK_REL)
            msh = NoeMesh(Facearray, vertArray, ModelName, "mat_0")
            msh.setUVs(UV_array)
            msh.setNormals(normArray)
            msh.setWeights(Weight_array)
            mesh.append(msh)
            
    
    mdl = NoeModel(mesh)
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial("mat_0","")]))
    mdl.setBones(bones)
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 90 90")
    return 1
    
def LoadSkeleton(bs):
    #bs = NoeBitStream(data)
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
    
    #mdl = NoeModel()
    #mdl.setBones(bones)
    #mdlList.append(mdl)

    return bones