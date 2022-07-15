from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("yingxiong model", ".skin")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1
       
def CheckType(data):
    bs = NoeBitStream(data)
    if bs.readInt() != 200:
        return 0
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(4)
    ver = bs.readInt()#count submesh or ver?
    
    ctx = rapi.rpgCreateContext()
    
    matName = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
    unk = bs.readInt()
    txName1 = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
    txName2 = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
    bs.seek(82, NOESEEK_REL)
    
    boneMap = [bs.readInt() for x in range(bs.readInt())]
   
    vCount = bs.readInt()
    data = bs.readBytes(vCount * 26)
    
    fCount = bs.readInt()*3
    faces = bs.readBytes(fCount * 2)
    
    rapi.rpgSetBoneMap(boneMap)
    rapi.rpgSetName(matName)
    rapi.rpgBindPositionBufferOfs(data, noesis.RPGEODATA_HALFFLOAT, 26, 0)
    rapi.rpgBindNormalBufferOfs(data, noesis.RPGEODATA_HALFFLOAT, 26, 6)
    rapi.rpgBindUV1BufferOfs(data, noesis.RPGEODATA_HALFFLOAT, 26, 12)
    rapi.rpgBindBoneIndexBufferOfs(data, noesis.RPGEODATA_UBYTE, 26, 16, 3)
    rapi.rpgBindBoneWeightBufferOfs(data, noesis.RPGEODATA_HALFFLOAT, 26, 20, 3)
    rapi.rpgCommitTriangles(faces, noesis.RPGEODATA_USHORT, fCount, noesis.RPGEO_TRIANGLE)
    
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial(matName, txName1)]))
    mdl.meshes[0].indices = FlipFace(mdl.meshes[0].indices)
    mdl.setBones(LoadSkeleton())
    print(boneMap)
    mdlList.append(mdl)
    return 1
    
def FlipFace(indices):
    flipTriangles = []
    
    for x in range(0, len(indices), 3):
        flipTriangles += indices[x:x+3][::-1]
    
    return flipTriangles
    
def LoadSkeleton():
    path1 = "_".join(rapi.getInputName().split('_')[:-1])+".skel"
    path2 = rapi.getInputName().replace(".skin",".skel")
    skelPath = None
    
    if rapi.checkFileExists(path1):
        skelPath = path1
    elif rapi.checkFileExists(path2):
        skelPath = path2
        
    scriptPath = os.path.join(os.path.dirname(os.path.realpath(__file__)),"fmt_skel.py")
    bones = []
    if skelPath and rapi.checkFileExists(scriptPath):
        import fmt_skel
        data = rapi.loadIntoByteArray(skelPath)
        mdlList = []
        fmt_skel.LoadSkeleton(data, mdlList)
        if mdlList:
            bones = mdlList[0].bones
    return bones