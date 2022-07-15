#powered by Durik256 16.01.2021 for (https://forum.xentax.com)
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Table Top Racing", ".amodel")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1
       
def noepyCheckType(data):
    if len(data) < 0x80:
        return 0
    bs = NoeBitStream(data)
    Tag = noeAsciiFromBytes(bs.readBytes(4))
    if Tag != 'DOMB':
        return 0
    return 1
    
#KTX2 HEADER ETC2 RGB
tx_byte1 = [0xAB, 0x4B, 0x54, 0x58, 0x20, 0x32, 0x30, 0xBB, 0x0D, 0x0A,
            0x1A, 0x0A, 0x94, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00]
tx_byte2 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00,
            0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x68, 0x00, 0x00, 0x00, 0x2C, 0x00, 0x00, 0x00, 0x94, 0x00,
            0x00, 0x00, 0x38, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0xD0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
            0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
            0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2C, 0x00, 0x00, 0x00, 
            0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x28, 0x00, 0xA1, 0x01,
            0x02, 0x00, 0x03, 0x03, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3F, 0x02, 0x00, 0x00, 
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 
            0x12, 0x00, 0x00, 0x00, 0x4B, 0x54, 0x58, 0x6F, 0x72, 0x69,
            0x65, 0x6E, 0x74, 0x61, 0x74, 0x69, 0x6F, 0x6E, 0x00, 0x72,
            0x64, 0x00, 0x00, 0x00, 0x1B, 0x00, 0x00, 0x00, 0x4B, 0x54,
            0x58, 0x77, 0x72, 0x69, 0x74, 0x65, 0x72, 0x00, 0x50, 0x56,
            0x52, 0x54, 0x65, 0x78, 0x4C, 0x69, 0x62, 0x20, 0x76, 0x35,
            0x2E, 0x32, 0x2E, 0x30, 0x00, 0x00]
            
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    head = noeAsciiFromBytes(bs.readBytes(4))
    ver = bs.readInt()#?
    unk0 = bs.readInt()
    count_tx = bs.readInt()
    count_submesh = bs.readInt()
    unk1, unk2 = bs.readInt(), bs.readInt()
    model_start_offset = bs.readInt()
    bs.seek(20, NOESEEK_REL)
    
    #submesh
    meshes = []
    for x in range(count_submesh):
        name = noeAsciiFromBytes(bs.readBytes(64)).split("\0")[0]
        print(x,name)
        
        unk_m0 = bs.readInt()
        bs.seek(0x38, NOESEEK_REL)#color?pos?size?
        start_data_submesh = bs.readInt()#(00 FF 00 FF)
        
        vert_count = bs.readInt()
        indices_count = bs.readInt()
        
        vert_offset = bs.readInt()
        vert_sizeBlock = bs.readInt()
        indices_offset = bs.readInt()
        indices_sizeBlock = bs.readInt()
        unk_m1 = bs.readInt()#(FF FF FF FF) uv from end?
        unk_m2 = bs.readInt()#uv pos from end 

        last_pos = bs.getOffset()

        vert, norm, uvs = [], [], []
        bs.seek(vert_offset, NOESEEK_ABS)
        
        v_size = vert_sizeBlock/vert_count;
        print("v_size",v_size)
        for v in range(vert_count):
            vert.append(NoeVec3.fromBytes(bs.readBytes(12)))
            if v_size > 24:
                norm.append(NoeVec3.fromBytes(bs.readBytes(12)))
                uvs.append(NoeVec3([bs.readFloat(),bs.readFloat()]+[0]))
            else:
                bs.seek(4, NOESEEK_REL)
                uvs.append(NoeVec3([bs.readFloat(),bs.readFloat()]+[0]))
        
        bs.seek(indices_offset, NOESEEK_ABS)
        face = [bs.readShort() for i in range(indices_count)]
        
        mesh = NoeMesh(face, vert , name)
        if norm: mesh.setNormals(norm)
        if uvs: mesh.setUVs(uvs)
        meshes.append(mesh)
        bs.seek(last_pos, NOESEEK_ABS)
        
    #saveTexture/create mat
    dirPath = rapi.getDirForFilePath(rapi.getInputName())
    
    materials = []
    for tx in range(count_tx):
        name = os.path.basename(noeAsciiFromBytes(bs.readBytes(64))).replace(".tga","")
        pathKTX = os.path.join(dirPath, name + '.ktx2')
        pathPNG = os.path.join(dirPath, name + '_Out.png')#PVRTexToolCLI.exe export with '_Out'
        tx_size = bs.readInt()
        offset_tx = bs.readInt()
        tx_slot = bs.readInt()
        cur_pos = bs.getOffset()
        
        if tx_slot == 0:
            meshes[len(materials)].setMaterial(name)
            materials.append(NoeMaterial(name, pathPNG))
            
        if not os.path.exists(pathPNG) and not os.path.exists(pathKTX):
            print(bs.getOffset())
            bs.seek(offset_tx, NOESEEK_ABS)
            bs.seek(7, NOESEEK_REL)#Header PKM
            Width = bs.readShort()
            Height = bs.readShort()
            bs.seek(1, NOESEEK_REL)
            pixelData = bs.readBytes(tx_size-12)
            TexFile = NoeBitStream()
            TexFile.writeBytes(bytes(tx_byte1))
            TexFile.writeInt(Width)
            TexFile.writeInt(Height)
            TexFile.writeBytes(bytes(tx_byte2))
            TexFile.writeBytes(pixelData)
            Tex = open(pathKTX, "wb")
            Tex.write(TexFile.getBuffer())
            Tex.close()
            print("Save texture",pathKTX)
        else:
            print("Exists texture",pathKTX)
        bs.seek(cur_pos, NOESEEK_ABS)

    materials.append(NoeMaterial("default",""))
    mdl = NoeModel(meshes)
    mdl.setModelMaterials(NoeModelMaterials([], materials))
    mdlList.append(mdl)
    return 1