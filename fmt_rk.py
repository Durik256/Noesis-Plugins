from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("My Little Pony Gameloft", ".rk")#and Ice Age Adventures  
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    #noesis.logPopup()
    return 1
    
def noepyCheckType(data):
    if data[:8] != b'RKFORMAT':
        return 0
    return 1
    
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    bs.seek(80)
    
    h = {}
    #h = bs.read('68I')

    for x in range(17):
        i = bs.read('4I')
        h[i[0]] = i[1:]
            
    bs.seek(h[2][0])
    tn = string(bs)
    m, tx = [NoeMaterial(tn, tn)], []
    loadTx(tn, tx)
    
    #attr - (type,ofs,size)
    bs.seek(h[13][0])
    uo = -1
    for x in range(h[13][1]):
        i = bs.read('H2B')
        if i[0] == 1030:
            uo = i[1]
    
    bs.seek(h[3][0])
    strd = h[3][2]//h[3][1]
    vbuf = bs.read(h[3][2])
    rapi.rpgSetMaterial(m[0].name)
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, strd)
    if uo != -1:
        rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_USHORT, strd, uo)
    rapi.rpgSetUVScaleBias(NoeVec3([2]*3), None)
    
    bones = []
    if h[7][1]:
        bs.seek(h[7][0])
        for x in range(h[7][1]):
            prnt = bs.readInt()
            indx = bs.readInt()
            chld = bs.readInt()
            matx = NoeMat44.fromBytes(bs.read(64)).toMat43()
            name = string(bs)
            bones.append(NoeBone(indx, name, matx, None, prnt))
            
        bs.seek(h[17][0])
        wbuf = bs.read(h[17][2])
        strd = h[17][2]//h[17][1]
        rapi.rpgBindBoneIndexBuffer(wbuf, noesis.RPGEODATA_UBYTE, strd, 2)
        rapi.rpgBindBoneWeightBufferOfs(wbuf, noesis.RPGEODATA_USHORT, strd, 4, 2)
        
    bs.seek(h[4][0])
    ibuf = bs.read(h[4][2])
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, h[4][1], noesis.RPGEO_TRIANGLE)
    
    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)#delete for Ice Age
    mdl = rapi.rpgConstructModel()  
    mdl.setModelMaterials(NoeModelMaterials(tx, m))
    mdl.setBones(bones)
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 -90 -90")#delete for Ice Age
    return 1
    
def string(bs):
    return bs.read(64).split(b'\x00')[0].decode()
    
def loadTx(tn, tx):
    print(tn, tx)
    try:
        data = rapi.loadIntoByteArray(rapi.getDirForFilePath(rapi.getInputName())+tn+'.pvr')
        hd = struct.unpack('8I', data[:32])
        w, h, t = hd[6], hd[7], hd[2]

        if t == 34:
            data = rapi.imageDecodeASTC(data[67:], 8, 8, 1, w, h, 1)
        elif t == 6:
            data = rapi.imageDecodeETC(data[52:], w, h, 'RGB')
        else:
            return 0
        
        tx.append(NoeTexture(tn, w, h, data, noesis.NOESISTEX_RGBA32))
    except:
        print('error load tx!')
