from inc_noesis import *
import noesis

def registerNoesisTypes():
   handle = noesis.register("Port Royale 3", ".ibuf")
   noesis.setHandlerTypeCheck(handle, noepyCheckType)
   noesis.setHandlerLoadModel(handle, noepyLoadModel)
   return 1

def noepyCheckType(data):
    if len(data) < 0x80:
        return 0
    return 1       

def HalfFloat(val):
    return noesis.getFloat16(val)

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    fileVbuf = rapi.getExtensionlessName(rapi.getInputName())+".vbuf"
    bs.seek(0xA, NOESEEK_REL)
    Icount = bs.readInt()
    bs.seek(0x16, NOESEEK_ABS)
    Itype = bs.readInt()
    bs.seek(0x20, NOESEEK_ABS)
    
    if Itype == 2:
        indices = [bs.readShort() for x in range(Icount)]
    elif Itype == 4:
        indices = [bs.readInt() for x in range(Icount)]

    if rapi.checkFileExists(fileVbuf):
        f =  open(fileVbuf,"rb")
    else:
        return 0
        
    vbuf = NoeFileStream(f)
    vbuf.seek(0x16, NOESEEK_ABS)
    sizeBlock = vbuf.readInt()
    vbuf.seek(0xA, NOESEEK_ABS)
    Vsize = vbuf.readInt()
    Vcount = int(Vsize/sizeBlock)
    
    offsetData = vbuf.fileSize - Vsize
    
    vbuf.seek(offsetData, NOESEEK_ABS)
    Positions = []
    Normals = []
    TexCoords = []
    for x in range(Vcount):
        if sizeBlock == 80:
            Positions.append(NoeVec3.fromBytes(vbuf.readBytes(12)))
            vbuf.seek(0x10, NOESEEK_REL)
            Normals.append(NoeVec3.fromBytes(vbuf.readBytes(12)))
            vbuf.seek(0x18, NOESEEK_REL)
            TexCoords.append(NoeVec3([vbuf.readFloat(), vbuf.readFloat(), 0.0]))
            vbuf.seek(0x8, NOESEEK_REL)
        elif sizeBlock == 16:
            Positions.append(NoeVec3([HalfFloat(vbuf.readUShort()),HalfFloat(vbuf.readUShort()),HalfFloat(vbuf.readUShort())]))
            #Normals.append(NoeVec3([HalfFloat(vbuf.readUShort()),HalfFloat(vbuf.readUShort()),HalfFloat(vbuf.readUShort())]))
            vbuf.seek(0x6, NOESEEK_REL)
            TexCoords.append(NoeVec3([HalfFloat(vbuf.readUShort()),HalfFloat(vbuf.readUShort()), 0.0]))
  
    mesh = NoeMesh(indices, Positions, "mesh_0", "mat_0")
    if Normals: mesh.setNormals(Normals)
    if TexCoords: mesh.setUVs(TexCoords)
    mdl = NoeModel([mesh])
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial("mat_0","")]))
    mdlList.append(mdl)
    return 1
