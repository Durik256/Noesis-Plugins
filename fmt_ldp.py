#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Crimson Tears (PS2)", ".ldp")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def CheckType(data):
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    result = [(i+12) for i in findall(b'\x00\x00\x00\x00\x00\x00\x00\x00\x04\x04\x00\x01', data)]

    '''
    bones = []
    bs.seek(515040)#for 'ask0.ldp'
    for x in range(192):
        name = noeAsciiFromBytes(bs.readBytes(64))
        parent = bs.readInt()
        bs.seek(12,1)
        pos = NoeVec3.fromBytes(bs.readBytes(12))
        rot = NoeAngles.fromBytes(bs.readBytes(12)).toMat43()
        rot[3] = pos
        bs.seek(24,1)
        bones.append(NoeBone(x,name,rot,None,parent))
    '''
    
    faces, uvbuf = [], []
    for x in result:
        bs.seek(x)
        b = bs.read('4B')
        if b[0] == 1:
            bs.seek(12,1)
            faces = [bs.readInt()]
            if b[2] > 2:
                faces = [bs.read('16B')[0] for x in range(b[2] - 1)]
        if b[0] == 74:#Vertices
            cur = 0
            for x in faces:
                vbuf = bs.readBytes(x*16)
                rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 16)
                rapi.rpgBindUV1Buffer(uvbuf[cur*8:(cur*8)+(x*8)], noesis.RPGEODATA_SHORT, 8)
                rapi.rpgSetUVScaleBias(NoeVec3([8]*3),None)
                rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, x, noesis.RPGEO_TRIANGLE_STRIP)
                cur += 0
            rapi.rpgClearBufferBinds()
        if b[0] == 26:#UVS
            uvbuf = bs.readBytes(b[2]*8)
            #rapi.rpgBindUV1Buffer(bs.readBytes(b[2]*8), noesis.RPGEODATA_SHORT, 8)
        print(b)
    
    txList = []
    try:
        loadTx(bs, data, txList)
    except:
        pass
    
    #bones = rapi.multiplyBones(bones)
    mdl = rapi.rpgConstructModel()#NoeModel()
    #mdl.setBones(bones)
    mdl.setModelMaterials(NoeModelMaterials(txList, [NoeMaterial('mat_0', '')]))
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 90 90")
    return 1
    
def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)

#TEST 
def loadTx(bs, data, txList):
    curPos = bs.getOffset()
    Lbin = data.find(b'Lbin',bs.getOffset(), bs.getSize())
    bs.seek(Lbin+12)
    curPos = bs.getOffset()-12
    numTx = bs.readInt()
    #ofs [img,palette]
    ofs = [[bs.readInt(),bs.readInt()] for x in range(numTx)]
    bs.seek(Lbin-numTx*32)
    names = [noeAsciiFromBytes(bs.readBytes(32)) for x in range(numTx)]
    
    for x in range(numTx):#numTx
        bs.seek(curPos+ofs[x][0])
        size = bs.readInt()
        w, h = bs.readInt(), bs.readInt()
        type = bs.readInt()
        bit, flag = 8, 1
        if type == 20:
            bit, flag = 4, 0
        
        raw = bs.readBytes(size)
        pinfo = bs.read('4I')
        palette = bs.readBytes(pinfo[0])
        raw = rapi.imageDecodeRawPal(raw, palette, w, h, bit, 'r8g8b8a8', flag)
        txList.append(NoeTexture(names[x], w, h, raw, noesis.NOESISTEX_RGBA32))
        print(names[x],size,[w,h],type)
    print(bs.getOffset())
    
    