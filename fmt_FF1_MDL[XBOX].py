# by Durik for xentax.com 
from inc_noesis import *

def registerNoesisTypes():
   handle = noesis.register("Fatal Frame [XBOX]", ".mdl")
   noesis.setHandlerTypeCheck(handle, CheckType)
   noesis.setHandlerLoadModel(handle, LoadModel)
   return 1

def CheckType(data):
    if data.find(b'\x60\x10\x00\x00') < 0:
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
    print('MDL>>> count:', COUNT_FILE)
  
    for x in range(COUNT_FILE):
        SIZE_FILE = bs.readUInt()
        TYPE_FILE = bs.readUInt()
        bs.seek(8, 1)
        curPos = bs.getOffset()
    
        if TYPE_FILE == 6:
            read_XPR(bs, texList)
        elif TYPE_FILE == 5:
            read_MPX(bs, texList, mdlList)
        elif TYPE_FILE == 0:
            read_MDL(bs, mdlList)
        
        bs.seek(curPos + SIZE_FILE)
    return 1
    
def read_XPR(bs, texList):
    res = [1,2,4,8,16,32,64,128,256,512,1024]
    
    startPos = bs.getOffset()
    bs.seek(4, 1)#XPR
    size, tx_start = bs.readInt(), bs.readInt()
    
    tx_head, tx_info = bs.readInt(), []
    while tx_head != -1:
        #offset,type
        tx_info.append([bs.readUInt64(), bs.readUInt64()])
        tx_head = bs.readInt()

    for x in tx_info:
        bs.seek(startPos+tx_start+x[0])
        w = res[(x[1] & 0x00F00000) >> 20];
        h = res[(x[1] & 0x0F000000) >> 24];

        data = bs.readBytes(w*h)
        texFmt = noesis.NOESISTEX_DXT5
        texList.append(NoeTexture('Texture '+str(len(texList)), w, h, data, texFmt))
    return 1
    
def read_MPX(bs, texList, mdlList):
    MATERIALS, BONES = [], []
    NUM_OBJ = bs.readUInt()
    bs.seek(12, 1)
    
    for x in range(NUM_OBJ):
        OBJ_SIZE, curPos = bs.readUInt(), bs.getOffset() + 12
        bs.seek(24, 1)

        (MAT_NUM,
        OFFSET_VERT,
        SIZE_VERT,
        OFFSET_BONE,
        OFFSET_MAT,
        OFFSET_VERT0,
        NUM_BONE) = [bs.readUInt() for x in range(7)]
        
        OFFSET_MESH = [bs.readUInt() for x in range(NUM_BONE)]
        
        if OFFSET_BONE:
            bs.seek(curPos + OFFSET_BONE)
            
            for x in range(NUM_BONE - 1):
                MATRIX = NoeMat44.fromBytes(bs.readBytes(64)).toMat43()
                #fix scale
                MAT = MATRIX.toQuat().toMat43()
                MAT[3] = MATRIX[3]
                bs.seek(128, 1)

                UNK = NoeVec4.fromBytes(bs.readBytes(16))
                PARENT = bs.readInt()
                bs.seek(16, 1)
                BONES.append(NoeBone(x, "bone_"+str(x), MAT, None, PARENT))
                
        if OFFSET_MAT:
            bs.seek(curPos + OFFSET_MAT)
                    
            for x in range(MAT_NUM):
                DIFFUSE = NoeVec4.fromBytes(bs.readBytes(16))
                SPEC = NoeVec4.fromBytes(bs.readBytes(16))
                bs.seek(32, 1)
                UNK_FLOAT = bs.readFloat()
                bs.seek(4, 1)
                ID_TX = bs.readInt()
                NAME_TX = noeAsciiFromBytes(bs.readBytes(64))
                UNK_INT = bs.readUInt()
                if ID_TX >= len(texList): ID_TX = 0
                nameTx = 'Texture ' + str(ID_TX) if ID_TX != -1 else ''
                MATERIALS.append(NoeMaterial('mat_%d_%d' % (x, OFFSET_VERT), nameTx))
        
        
        #--------------------------------------------------------------
        bs.seek(curPos+OFFSET_VERT0)
        print('>>>>>>>>-------------START_VERT', bs.getOffset())
        #first-(one_bone);second-(unk,always zero);third-(two_bone)
        for x in range(bs.readInt()):
            #0-unk(always 4);1-off_vert;2-off_norm;3-zero(last off_info)
            unk = [bs.readInt() for x in range(4)]
            print(unk)
        
        #vert_weight_boneIndex
        VERT = []
        if unk[3]:
            bs.seek(curPos + unk[3])
            inf_v = [[bs.readShort(),bs.readShort(),bs.readInt()] for x in range(bs.readInt())]
            bs.seek(curPos + unk[1])
            for x in inf_v:
                for y in range(x[2]):
                    v0 = bs.readBytes(12)
                    w = int(bs.readFloat()*255)
                    v1 = bs.readBytes(12)
                    bs.seek(4, 1)
                    VERT.append([v0,x[0],x[1],w, v1])
        
        #--------------------------------------------------------------
        
        for OFFSET in OFFSET_MESH: 
            if OFFSET:
                bs.seek(curPos + OFFSET)
                HEAD, UNK, BONE_ID, FLAG = [bs.readUInt() for x in range(4)]
                print('***HEAD:',HEAD, 'UNK:',UNK ,'BONE_ID:',BONE_ID, 'FLAG:',FLAG)
                
                if not FLAG:
                    bs.seek(bs.readUInt() - 4, 1)
                
                while not 0:
                    pos = bs.getOffset() 
                    M_INFO = [bs.readUInt() for x in range(16)]
                    
                    if not M_INFO[0]: 
                        break

                    print('BONE_ID:',BONE_ID, 'M_INFO:',M_INFO ,bs.getOffset())
                    
                    bs.seek(curPos + M_INFO[10])
                    IBUF = bs.readBytes(M_INFO[12] * 2)
                    
                    bs.seek(curPos + OFFSET_VERT + M_INFO[6])
                    
                    STRIDE = 32 if M_INFO[14] == 1 or M_INFO[14] == 5 else 24
                    print('>>>' ,bs.getOffset())
                    #VBUF = bs.readBytes(M_INFO[8] * STRIDE)
                    
                    if FLAG:
                        VBUF, WBUF, WIBUF, BNUM = SkinPreconstructedVertsToBones(bs, STRIDE, M_INFO[8], -1, BONES, VERT)
                    else:
                        VBUF, WBUF, WIBUF, BNUM = SkinPreconstructedVertsToBones(bs, STRIDE, M_INFO[8], BONE_ID, BONES)
                        
                    
                    print('IBUF_OFFSET',curPos + M_INFO[10],'INUM', M_INFO[12], 'STRIDE', STRIDE)
                    print('VBUF_OFFSET',curPos + OFFSET_VERT + M_INFO[6],'VNUM', M_INFO[8])
                    

                    
                    rapi.rpgSetName('mesh_%d_%d' % (M_INFO[2], bs.getOffset()))
                    rapi.rpgSetMaterial('mat_%d_%d' % (M_INFO[2], OFFSET_VERT))
            
                    rapi.rpgBindPositionBuffer(VBUF, noesis.RPGEODATA_FLOAT, STRIDE)
                    rapi.rpgBindUV1BufferOfs(VBUF, noesis.RPGEODATA_FLOAT, STRIDE, STRIDE-8)
                    rapi.rpgBindBoneIndexBuffer(WIBUF, noesis.RPGEODATA_UBYTE, BNUM, BNUM)
                    rapi.rpgBindBoneWeightBuffer(WBUF, noesis.RPGEODATA_UBYTE, BNUM, BNUM)

                    rapi.rpgCommitTriangles(IBUF, noesis.RPGEODATA_SHORT, M_INFO[12], noesis.RPGEO_TRIANGLE_STRIP)
                    bs.seek(pos + M_INFO[3] + 12)

        bs.seek(curPos + OBJ_SIZE)
        print('---------------------------------END_OBJ---------------------------------')

    #rapi.rpgSkinPreconstructedVertsToBones(BONES)
    rapi.rpgOptimize()
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials(texList, MATERIALS))
    mdl.setBones(BONES)
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 90 90")
    return 1
    
def SkinPreconstructedVertsToBones(bs, STRIDE, COUNT, BONE_ID, BONES, VERT = None):
    VBUF, WBUF, WIBUF = b'', b'', b''
    
    if BONE_ID < 0:
        for x in range(COUNT):
            v = bs.readBytes(12)
            
            for y in VERT:
                if v == y[0]:
                    #v = BONES[y[1]].getMatrix().transformPoint(NoeVec3.fromBytes(v))
                    v0 = NoeVec3.fromBytes(y[0])
                    v1 = NoeVec3.fromBytes(y[-1])

                    v0 = BONES[y[1]].getMatrix().transformPoint(v0)
                    v1 = BONES[y[2]].getMatrix().transformPoint(v1)

                    v = (v0 * (y[3]/255)) + (v1 * ((255 - y[3])/255))
                    
                    v = struct.pack('3f', *[v[0], v[1], v[2]])
                    
                    WBUF += ((y[3]).to_bytes(1, 'little')) + ((255 - y[3]).to_bytes(1, 'little'))
                    WIBUF += ((y[1]).to_bytes(1, 'little')) + ((y[2]).to_bytes(1, 'little'))
                    break
                    
            VBUF += v
            VBUF += bs.readBytes(STRIDE - 12)
        
        BNUM = 2  
    
    else:
        for x in range(COUNT):
            v = BONES[BONE_ID].getMatrix().transformPoint(NoeVec3.fromBytes(bs.readBytes(12)))
            VBUF += struct.pack('3f', *[v[0], v[1], v[2]])
            VBUF += bs.readBytes(STRIDE - 12)
        
        WBUF, WIBUF, BNUM = ((255).to_bytes(1, 'little'))*COUNT, ((BONE_ID).to_bytes(1, 'little'))*COUNT, 1
    
    return VBUF, WBUF, WIBUF, BNUM