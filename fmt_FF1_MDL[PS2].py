# by Durik for xentax.com 
from inc_noesis import *

def registerNoesisTypes():
   handle = noesis.register("Fatal Frame [PS2]", ".mdl")
   noesis.setHandlerTypeCheck(handle, CheckType)
   noesis.setHandlerLoadModel(handle, LoadModel)
   return 1

def CheckType(data):
    if data.find(b'\x50\x10\x00\x00') < 0:
        return 0
    return 1     

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    read_MDL(bs, mdlList)
    return 1
    
def read_MDL(bs, mdlList):
    texList = []
    
    COUNT_FILE = bs.readUInt()
    bs.seek(12,1)
    #print('MDL>>> count:', COUNT_FILE)
  
    for x in range(COUNT_FILE):
        SIZE_FILE = bs.readUInt()
        TYPE_FILE = bs.readUInt()
        bs.seek(8, 1)
        curPos = bs.getOffset()
    
        if TYPE_FILE == 6:
            read_PK2(bs, texList)
        elif TYPE_FILE == 5:
            read_MPK(bs, texList, mdlList)
        elif TYPE_FILE == 0:
            read_MDL(bs, mdlList)
        
        bs.seek(curPos + SIZE_FILE)
    return 1
    
def read_PK2(bs, texList):
    startPos = bs.getOffset()
    num_tx = bs.readInt()
    bs.seek(12, 1)
    
    for x in range(num_tx):
        size = bs.readInt()
        bs.seek(12, 1)

        data = bs.readBytes(size)
        texList.append(rapi.loadTexByHandler(data, '.tm2'))
    return 1
    
def read_MPK(bs, texList, mdlList):
    startPos = bs.getOffset()
    
    NUM_OBJ = bs.readUInt()
    bs.seek(12, 1)
    
    BONES, MATERIALS = [], []
    for x in range(NUM_OBJ):
        #print(x, '---------------------------------START_OBJ---------------------------------', bs.getOffset())
        OBJ_SIZE, curPos = bs.readUInt(), bs.getOffset() + 12
        bs.seek(12, 1)
    
        #curPos = bs.getOffset()
        bs.seek(6,1)#[50 10 00 00 00 00]
        mat_num = bs.readShort()

        bone_ofs, mat_ofs, vert_ofs, num_bone = [bs.readInt() for x in range(4)]
        mesh_ofs = [bs.readInt() for x in range(num_bone)]
        #print("mesh_ofs:", mesh_ofs)
        
        
        if bone_ofs:
            bs.seek(curPos + bone_ofs)
                
            for x in range(num_bone - 1):
                MATRIX = NoeMat44.fromBytes(bs.readBytes(64)).toMat43()
                #fix scale
                MAT = MATRIX.toQuat().toMat43()
                MAT[3] = MATRIX[3]
                bs.seek(128, 1)

                UNK = NoeVec4.fromBytes(bs.readBytes(16))
                PARENT = bs.readInt()
                bs.seek(12, 1)
                BONES.append(NoeBone(x, "bone_"+str(x), MAT, None, PARENT))
        
        matID = []
        if mat_ofs:
            bs.seek(curPos + mat_ofs)
                    
            for x in range(mat_num):
                if bs.readInt():
                    NAME_TX = noeAsciiFromBytes(bs.readBytes(12).replace(b'\x00', b''))
                else:
                    NAME_TX = 'Mat_' + str(len(MATERIALS))
                    bs.seek(12, 1)
                #NAME_TX = 'Mat_' + str(len(MATERIALS))

                DIFFUSE = NoeVec4.fromBytes(bs.readBytes(16))
                bs.seek(144, 1)

                matID.append(len(MATERIALS))
                MATERIALS.append(NoeMaterial(NAME_TX, ''))
        
        bs.seek(curPos + vert_ofs)
        v_inf = [[bs.readInt() for x in range(4)] for x in range(bs.readInt())]
        #print('***v_inf:',v_inf)
        
        VBUF_ONE = []
        if v_inf[0][1]:
            #calc count:
            if v_inf[2][1]:
                num = (v_inf[2][1] - v_inf[0][1])//16
            else:
                num = (v_inf[0][2] - v_inf[0][1])//16
            #------------
            
            bs.seek(curPos + v_inf[0][1])
            for x in range(num):
                VBUF_ONE.append(bs.readBytes(12))
                bs.seek(4,1)
            
        VBUF_TWO = []
        if v_inf[2][1]:
            #calc count:
            if v_inf[0][2]:
                num = (v_inf[0][2] - v_inf[2][1])//32
            elif not v_inf[0][2] and not v_inf[2][3]:
                num = (v_inf[2][2] - v_inf[2][1])//32
            elif v_inf[2][3]:
                bs.seek(curPos + v_inf[2][3])
                num = sum([((bs.readInt()*0) + bs.readInt()) for x in range(bs.readInt())])
            #------------
            
            bs.seek(curPos + v_inf[2][1])
            for x in range(num):
                v0 = bs.readBytes(12)
                w0 = int(bs.readFloat()*255)
                w1 = 255-w0
                v1 = bs.readBytes(12)
                i0, i1 = bs.readByte(), bs.readByte()
                bs.seek(2,1)
                VBUF_TWO.append([v0, i0, i1, w0, w1, v1])
            
        
        
        for x in mesh_ofs:
            if x:
                bs.seek(curPos + x)
                
                head = [bs.readInt() for x in range(4)]#[16,3,BoneID,Flag]
                #print('head:', head, bs.getOffset())
                
                if not head[3]:
                    bs.seek(144,1)#dummy cube
                
                rapi.rpgSetName('mesh_'+ str(curPos + x))
                
                while not 0:
                    hd = [bs.readInt() for x in range(4)]#[16,2,matID?,Flag]

                    if not hd[0]: 
                        break
                    
                    #print('hd:', hd, bs.getOffset())
                    #print(MATERIALS[matID[hd[2]]].name)
                    rapi.rpgSetMaterial(MATERIALS[matID[hd[2]]].name)
                    
                    while not 0:
                        cur = bs.getOffset()
                        size, zero = bs.readInt(), bs.readInt()
                        
                        if size == 16 and zero == 2 or size == 0 and zero == 0: 
                            bs.seek(-8, 1)
                            break
                        
                        
                        num_vert, num_norm, num_unk, type = [bs.readShort() for x in range(4)]
                        
                        if type == 6:
                            bs.seek(32,1)
                            #print('<<<<',type,[bs.readInt() for x in range(8)], 'OFFSET:',bs.getOffset())
                            cpos = bs.getOffset()
                            bs.seek(cur + size)
                            tri_inf, UVBUF = readUV(bs)
                            bs.seek(cpos)

                            for i,x in enumerate(tri_inf):
                                VBUF = b''
                                if head[3]:
                                    stride, b_num = 16, 2
                                    for q in range(x):
                                        index = bs.readInt() + bs.readInt()*0
                                        
                                        v0 = NoeVec3.fromBytes(VBUF_TWO[index][0])
                                        v1 = NoeVec3.fromBytes(VBUF_TWO[index][-1])

                                        v0 = (BONES[VBUF_TWO[index][1]].getMatrix()).transformPoint(v0)
                                        v1 = (BONES[VBUF_TWO[index][2]].getMatrix()).transformPoint(v1)

                                        v = (v0 * ((VBUF_TWO[index][3])/255)) + (v1 * ((VBUF_TWO[index][4])/255))

                                        VBUF += struct.pack('3f', *[v[0],v[1],v[2]])+struct.pack('4B', *VBUF_TWO[index][1:-1])
                                else:
                                    stride, b_num = 14, 1
                                    for q in range(x):
                                        index = bs.readInt() + bs.readInt()*0
                                        v = BONES[head[2]].getMatrix().transformPoint(NoeVec3.fromBytes(VBUF_ONE[index]))
                                        VBUF += struct.pack('3f', *[v[0],v[1],v[2]])+(head[2]).to_bytes(1, 'little')+(255).to_bytes(1, 'little')
                                
                                IBUF = autoTriangles(x)
                                
                                rapi.rpgBindPositionBuffer(VBUF, noesis.RPGEODATA_FLOAT, stride)
                                rapi.rpgBindUV1Buffer(UVBUF[i], noesis.RPGEODATA_FLOAT, 8)
                                
                                rapi.rpgBindBoneIndexBufferOfs(VBUF, noesis.RPGEODATA_UBYTE, stride, 12, b_num)
                                rapi.rpgBindBoneWeightBufferOfs(VBUF, noesis.RPGEODATA_UBYTE, stride, 12+b_num, b_num)
                                
                                rapi.rpgCommitTriangles(IBUF, noesis.RPGEODATA_SHORT, len(IBUF)//2, noesis.RPGEO_TRIANGLE_STRIP)
                                
                        elif type == 5:
                            bs.seek(40,1)
                            #print('<<<<',type,[bs.readInt() for x in range(10)], 'OFFSET:',bs.getOffset())
                            
                            cpos = bs.getOffset()
                            bs.seek(cur + size)
                            tri_inf, UVBUF = readUV(bs)
                            bs.seek(cpos)

                            for i,x in enumerate(tri_inf):
                                #VBUF = bs.readBytes(24*x)
                                VBUF = b''
                                for q in range(x):
                                    v = BONES[head[2]].getMatrix().transformPoint(NoeVec3.fromBytes(bs.readBytes(12)))
                                    bs.seek(12, 1)
                                    VBUF += struct.pack('3f', *[v[0],v[1],v[2]])+(head[2]).to_bytes(1, 'little')+(255).to_bytes(1, 'little')
                                
                                IBUF = autoTriangles(x)
                                
                                rapi.rpgBindPositionBuffer(VBUF, noesis.RPGEODATA_FLOAT, 14)
                                rapi.rpgBindUV1Buffer(UVBUF[i], noesis.RPGEODATA_FLOAT, 8)
                                
                                rapi.rpgBindBoneIndexBufferOfs(VBUF, noesis.RPGEODATA_UBYTE, 14, 12, 1)
                                rapi.rpgBindBoneWeightBufferOfs(VBUF, noesis.RPGEODATA_UBYTE, 14, 13, 1)
                                
                                rapi.rpgCommitTriangles(IBUF, noesis.RPGEODATA_SHORT, len(IBUF)//2, noesis.RPGEO_TRIANGLE_STRIP)
                            
                        bs.seek(cur + size)
                        bs.seek(bs.readInt() - 4,1)#skip UV
        bs.seek(curPos + OBJ_SIZE)
        #print('---------------------------------END_OBJ---------------------------------')

    mdl = rapi.rpgConstructModel()
    mdl.setBones(BONES)
    mdl.setModelMaterials(NoeModelMaterials(texList, MATERIALS))
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 90 90")
    return 1
    
def autoTriangles(vcount):
    ibuf = b''
    for x in range(vcount):
        ibuf +=(x).to_bytes(2, 'little')
    return ibuf
    
    
def readUV(bs):
    cur = bs.getOffset()
    size = bs.readInt()
    unk0 = bs.readInt()#always 1
    unk1 = bs.readInt()#num?
    #print('>>>', unk0, unk1)
    unk2 = bs.readUShort()#have mat (33280-true or 32768-false)
    numTI = bs.readShort()
    #print("unk2_start:", unk2,bs.getOffset())
    if unk2 == 33280 or unk2 == 512 or unk2 == 2560:
        matID = bs.readBytes(40)#mat id?
    
    bs.seek(8, 1)#[00 00 00 20 FC FC FC FC]
    
    #0-tx_id?; 1-num_uv
    #print("tri_inf_start:", bs.getOffset())
    tri_inf = [bs.readInt()*0 + bs.readInt() for x in range(numTI)]
    
    unkByte = bs.readBytes(12)#[00 00 00 20 D0 D0 D0 D0 03 01 00 01]
    
    UVBUF = []
    if bs.getOffset() < (cur + size):
        for x in tri_inf:
            unk = bs.readInt()#unk_id?
            UVBUF.append(bs.readBytes(x*8))
    else:
        for x in tri_inf:
            UVBUF.append(b'\x00'*8*x)
    
    bs.seek(cur + size)
    return tri_inf, UVBUF