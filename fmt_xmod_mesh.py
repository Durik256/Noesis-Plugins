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

def noepyLoadModel(data, mdlList):
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

                #if skeleton:
                BoneMap = noeAsciiFromBytes(bs.readBytes(BoneMapSize)).split('\0')
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
                            weights[0].append(Bone1)
                            weights[1].append(w1)

                          if bone2Off != -1:
                            w2 = float(weight2)
                            weights[0].append(Bone2)
                            weights[1].append(w2)

                          if bone3Off != -1:
                            w3 = float(weight3)
                            weights[0].append(Bone3)
                            weights[1].append(w3)

                          if bone4Off != -1:
                            w4 = float(weight4)
                            weights[0].append(Bone4)
                            weights[1].append(w4)
                    Weight_array.append(NoeVertWeight(weights[0],weights[1]))
                bs.seek(bs.readInt(), NOESEEK_REL)

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
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 90 90")
    return 1