#by Durik256
#link on boosty for other format: *.vpp (game archive), *.rxm (static model), *.rxc (character model), *.ceg (texture container)
#https://boosty.to/durik256/posts/a29c9a1a-5f17-41b4-b6af-107786a34360?share=post_link
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("The Punisher (2005)", ".rxm")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def CheckType(data):
    if data[:4] != b'\x13\x87\x12\x87':
        return 0
    return 1
    
def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    bs.seek(4)
    info = [bs.readInt() for y in range(21)]
    print(info)

    bs.seek(info[16]*96,1)#bone
    bs.seek(info[13]*76,1)#mat
    bs.seek(bs.readInt()*28,1)#tx
    
    bs.seek(152,1)
    
    #inf_block
    bs.seek(12,1)
    lnum = bs.readShort()
    bs.seek(6,1)
    strip_num = bs.readShort()
    bs.seek(34,1)

    vbuf_sz, ibuf_sz = bs.readInt(), bs.readInt()
    bs.seek(12,1)
    unk_num = bs.readInt()
    bs.seek(152,1)
    
    unk_sz = []
    for x in range(unk_num):
        bs.seek(24,1)
        unk_sz.append(bs.readInt())
        bs.seek(12,1)

    #ibuf = bs.readBytes(ibuf_sz)
    ibuf_ofs = bs.getOffset()
    bs.seek(ibuf_sz,1)

    skipA(bs)

    for x in unk_sz:
        bs.seek(x,1)
    
        if bs.readInt() != 0:
            bs.seek(-4,1)

    vbuf = bs.readBytes(vbuf_sz)
    skipA(bs)

    bs.seek(lnum*20,1)
    if bs.readUInt() != 3772834016: 
        bs.seek(-4,1)
    strip_inf = [[bs.readInt(), bs.readInt(),bs.readInt()][1] for x in range(strip_num)]
    print(strip_inf)
    
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 32)
    rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 32, 12)
    rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 32, 24)
    #rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, len(ibuf)//2, noesis.RPGEO_TRIANGLE_STRIP)
    
    bs.seek(ibuf_ofs)
    for i,x in enumerate(strip_inf):
        ibuf = bs.readBytes(x*2)
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, x, noesis.RPGEO_TRIANGLE_STRIP)
    
    rapi.rpgOptimize()
    mdl = rapi.rpgConstructModel()
    mdlList.append(mdl)
    return 1
    
def skipA(bs):
    while bs.readUByte() == 224:
        pass
    bs.seek(-1,1)
