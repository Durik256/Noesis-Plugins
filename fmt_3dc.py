#by Durik256 15.03.2022 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Shaiya",".3dc")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    
    mdl, bones = ParseFile(bs)
    
    paired_models = findAllFileFromFolder('.3dc')
    for model in paired_models:
        p_bs = NoeBitStream(rapi.loadIntoByteArray(model))
        p_mdl, p_bones = ParseFile(p_bs)
        if len(bones) == len(p_bones):
            mdl.meshes = mdl.meshes + tuple([p_mdl.meshes[0]])
    
    #anims
    animList, animBones = [], []
    #animPath = rapi.getDirForFilePath(rapi.getInputName())#+'vi_05_run.ANI'
    animPath = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Open File", "Select animations", noesis.getSelectedFile())
    openAnim(animList, animBones, animPath)
    
    if animList and len(bones) == len(animBones[0]): 
        mdl.setAnims(animList)
        fixParent(bones, animBones[0])
    
    mdl.setBones(bones)
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 0 90")
    return 1

def ParseFile(bs):
    unk = bs.readInt()
    stride, cWeiht = type(unk)
    
    cBone = bs.readInt()
    
    bones = []
    for x in range(cBone):
        mat = NoeMat44.fromBytes(bs.readBytes(64)).inverse().toMat43()
        bones.append(NoeBone(x,"bone_"+str(x), mat))
    
    cVert = bs.readInt()
    vbuf = bs.readBytes(cVert*stride)
    
    cFace = bs.readInt()
    ibuf = bs.readBytes(cFace*6)
    
    ctx = rapi.rpgCreateContext()
    
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, stride)
    rapi.rpgBindBoneWeightBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, 12, cWeiht)
    rapi.rpgBindBoneIndexBufferOfs(vbuf, noesis.RPGEODATA_BYTE, stride, 12+(cWeiht*4), cWeiht)
    rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, stride-20)
    rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, stride-8) 
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, cFace*3, noesis.RPGEO_TRIANGLE)
    mdl = rapi.rpgConstructModel()
    return mdl, bones
    
def type(unk):
    stride, cWeiht = 40, 1
    if unk != 0:
        stride, cWeiht = 48, 3
    return stride, cWeiht

def fixParent(bones, animBones):
    print(len(animBones))
    for x in range(len(animBones)):
        bones[x].parentIndex = animBones[x].parentIndex

def openAnim(animList, animBones, animPath):
    sciptPath = rapi.getDirForFilePath(os.path.realpath(__file__))+'fmt_ani.py'

    if not animPath:
        return 0
    
    if rapi.checkFileExists(sciptPath) and rapi.checkFileExists(animPath):
        import fmt_ani
        mdlList = []
        fmt_ani.LoadModel(rapi.loadIntoByteArray(animPath), mdlList)
        if mdlList:
            animList.append(mdlList[0].anims[0])
            animBones.append(mdlList[0].bones)

def findAllFileFromFolder(ext):
    Dir = rapi.getDirForFilePath(rapi.getInputName())
    local = rapi.getLocalFileName(rapi.getInputName())
    name = local.split('#')[0]
    
    paths = []
    if Dir and os.path.exists(Dir):
        files = next(os.walk(Dir))[2]
        for file in files:
            if rapi.checkFileExt(file,ext) and name in file and local != file:
                paths.append(os.path.join(Dir,file))
                print(paths[-1])
    return paths