#powered by Durik256 21.02.2022 for xentax.com
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Tian Xia 3", ".dat")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1

SWAP = False

def noepyCheckType(data):
    global SWAP
    bs = NoeBitStream(data)
    if bs.readInt() != 1117867621:
        return 0
    SWAP=True if bs.readInt() != 1953720684 else False
    return 1


 
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    
    fSize = bs.getSize()-4
    bs.seek(fSize)
    offset = bs.readInt()
    bs.seek(fSize-offset)
    cMesh = calc(bs, offset)
    print("cont_Mesh:", cMesh)
    
    sMmesh = []
    for x in range(cMesh):
        iSize = bs.readInt()
        bs.seek(16, NOESEEK_REL)
        bs.seek(bs.readInt(), NOESEEK_REL)
        skipZero(bs)
        vSize = bs.readInt()
        bs.seek(16, NOESEEK_REL)
        bs.seek(bs.readInt(), NOESEEK_REL)
        sMmesh.append([iSize, vSize])
        skipZero(bs)
    
    bs.seek(4)
    ctx = rapi.rpgCreateContext()

    offset = 4
    for x in sMmesh:
        if SWAP:
            #VERTEX
            print("SWAP Model")
            offset += findXY(bs)
            bs.seek(64, NOESEEK_REL)
            v_count = bs.readInt()
            stride = int((x[0]-68)/v_count)
            data = bs.readBytes(v_count * stride)
            offset += x[0]
            bs.seek(offset)
            print("end Vert",offset)
            #FACE
            zero(bs)
            bs.seek(64, NOESEEK_REL)
            i_count = bs.readInt()
            unk = bs.readInt()
            faces = bs.readBytes(i_count * 2)
            offset += x[1]
            bs.seek(offset)
            print("end Face",offset)
            print(x,"i_count:", i_count,"v_count:", v_count,"stride:", stride)
            #---------
        else:
            #FACE
            zero(bs)
            bs.seek(64, NOESEEK_REL)
            i_count = bs.readInt()
            unk = bs.readInt()
            faces = bs.readBytes(i_count * 2)
            offset += x[0]
            bs.seek(offset)
            #VERTEX
            offset += findXY(bs)
            bs.seek(64, NOESEEK_REL)
            v_count = bs.readInt()
            stride = int((x[1]-68)/v_count)
            print(x,"i_count:", i_count,"v_count:", v_count,"stride:", stride)
            data = bs.readBytes(v_count * stride)
            offset += x[1]
            bs.seek(offset)
            #---------
        rapi.rpgSetName("Mesh_"+str(bs.getOffset()))
        rapi.rpgBindPositionBufferOfs(data, noesis.RPGEODATA_FLOAT, stride, 0)
        #if stride>=36:
            #rapi.rpgBindNormalBufferOfs(data, noesis.RPGEODATA_FLOAT, stride, 12)
        if stride>=24:
            rapi.rpgBindUV1BufferOfs(data, noesis.RPGEODATA_FLOAT, stride, 16 if stride != 36 else 24)
        rapi.rpgCommitTriangles(faces, noesis.RPGEODATA_USHORT, i_count, noesis.RPGEO_TRIANGLE)
        rapi.rpgClearBufferBinds()
    
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial("default","")]))
    mdlList.append(mdl)
    return 1

def string(bs):
    bytes = []
    byte = None
    while byte != 0:
        byte = bs.readUByte()
        bytes.append(byte)
    return noeAsciiFromBytes(bytes)
    
def zero(bs):
    for x in range(99):
        if bs.readUByte() != 0:
            bs.seek(-1, NOESEEK_REL)
            return 1
    
def findXY(bs):
    offset = 0
    for x in range(99):
        if bs.readShort() != 31096:#xy
            bs.seek(-1, NOESEEK_REL)
            offset += 1
        else:
            bs.seek(-2, NOESEEK_REL)
            return offset

def skipZero(bs):
    fSize = bs.getSize()-4
    for x in range(99):
        if bs.getOffset()+20 < fSize:
            bs.seek(20, NOESEEK_REL)
        else:
            return 1
        if bs.readUByte() != 0:
            bs.seek(-21, NOESEEK_REL)
            return 1
        else:
            bs.seek(-20, NOESEEK_REL)

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)

def calc(bs, offset):
    curPos = bs.getOffset()
    data = bs.readBytes(offset)
    count = [(i+7) for i in findall(b'indices', data)]
    bs.seek(curPos)
    return len(count)

"""
    #checkSWAP
    global SWAP
    bs.seek(20, NOESEEK_REL)
    label = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
    if "vertices" in label:
        SWAP = True
    bs.seek(curPos)
def calc(bs, offset):
    curPos = bs.getOffset()
    fSize = bs.getSize()-4
    count = 0

    while bs.getOffset() < fSize:
        print(">>>>>>>>>>>>>>.",bs.getOffset())
        bs.seek(20, NOESEEK_REL)
        label = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
        zero(bs)
        bs.seek(20, NOESEEK_REL)
        bs.seek(bs.readInt(), NOESEEK_REL)
        zero(bs)
        if "indices" in label or "vertices" in label:
            count += 1
    bs.seek(curPos)
    return count
"""