from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("vector unit games", ".dat")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    if len(data) < 0x80:
        return 0
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    fileSize = bs.getSize() - 0x80
    
    bs.seek(0xC, NOESEEK_REL)
    haveBone = True if bs.readByte() == 1 else False
    
    bones = []
    if haveBone:
        #load bones
        cBones = bs.readInt()
        for x in range(cBones):
            bones.append(NoeBone(x, searchString(bs), NoeMat43()))
            skipBoneInfo(bs)
            
        for x in range(cBones):
            bones[x].parentIndex = bs.readInt()

        bs.seek(0x10, NOESEEK_REL)
        for x in range(cBones):
            print([bs.readFloat() for x in range(8)])
        bs.seek(0x8, NOESEEK_REL)
    else:
        bs.readInt()
        
    if bs.readByte() == 1:#multiModel
        while bs.getOffset() < fileSize:
            loadModel(bs, mdlList)
            if bs.readByte() != 1:
                bs.setOffset(bs.getOffset()-1)
    else:
        if not haveBone: bs.readByte()#seek 1 byte
        loadModel(bs, mdlList)

    for model in mdlList:
        if bones:
            model.setBones(bones)
    rapi.setPreviewOption("setAngOfs", "0 180 0") 
    return 1
    
def loadModel(bs, mdlList):
    #load model
    bs.seek(0x18, NOESEEK_REL)
    countMat = bs.readInt()
    Materials = [searchString(bs) for x in range(countMat)]
    unk1 = bs.readInt()

    if unk1 > 0:
        bs.seek(0x28*countMat, NOESEEK_REL)
    else:
        unk2 = bs.readInt()
        bs.setOffset(bs.getOffset()-4)
        for x in range(unk2):
            bs.seek(0x5C, NOESEEK_REL)#mat44(64)
            unk3 = bs.readInt()
            bs.seek(0x28*unk3, NOESEEK_REL)

    bs.readInt()#unk4
    submesh = bs.readInt()

    meshes = []
    for i in range(submesh):
        Positions = []
        TexCoords = []
        #Normals = []
        
        sizeBlock = bs.readInt()
        sizeVertex = bs.readInt()
        cVertex = int(sizeVertex/sizeBlock)

        for x in range(cVertex):
            Positions.append(NoeVec3.fromBytes(bs.readBytes(12)))
            if sizeBlock == 36 or sizeBlock == 28:
                bs.seek(0x8, NOESEEK_REL)
                TexCoords.append(NoeVec3([bs.readFloat(), bs.readFloat(), 0.0]))
                bs.seek(sizeBlock-28, NOESEEK_REL)
            elif sizeBlock >= 24:
                bs.seek(0x4, NOESEEK_REL)
                TexCoords.append(NoeVec3([bs.readFloat(), bs.readFloat(), 0.0]))
                bs.seek(sizeBlock-24, NOESEEK_REL)
            else:
                bs.seek(sizeBlock-12, NOESEEK_REL)

        cIndices = bs.readInt()
        face = [bs.readUShort() for x in range(cIndices)]
        
        meshes.append(NoeMesh(face, Positions, "mesh_"+str(i), "mat_0"))
        meshes[-1].setUVs(TexCoords)

    mdl = NoeModel(meshes)
    materials = []
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial("mat_0","")]))
    mdlList.append(mdl)
    return 1

def searchString(bs): 
    bytes = []
    for x in range(50):#max length string
        byte = bs.readByte()
        if byte != 0:
            bytes.append(byte)
        else:
            break
    return noeAsciiFromBytes(bytes)

def skipBoneInfo(bs): 
    for x in range(50):#max length byte
        if bs.readByte() != 0:
            bs.seek(0x3, NOESEEK_REL)
            break
    return 1