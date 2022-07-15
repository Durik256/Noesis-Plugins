# (Madoka Magica: The Battle Pentagram)[PS Vita][.mdl][.anm]
# by Durik 08.02.2022 for xentax.com 
# using https://forum.xentax.com/viewtopic.php?f=16&t=17012&p=135953#p135953
# .apk unpack http://aluigi.altervista.org/bms/dragon_ball_z_boz.bms
# =================================================================
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Madoka Magica PS_Vita", ".mdl")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    if len(data) < 0x80:
        return 0
    bs = NoeBitStream(data)
    bs.seek(16, NOESEEK_ABS)
    Tag = noeAsciiFromBytes(bs.readBytes(3))
    if Tag != 'MDL':
        return 0
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    if noeAsciiFromBytes(bs.readBytes(8))!='ENDILTLE':
        bs.setEndian(NOE_BIGENDIAN)
    bs.seek(8, NOESEEK_REL)
    
    file_size = bs.getSize()
    chunks = []
    meshes = []
    
    #read chunks
    while bs.getOffset() < file_size:
        chunks.append(readChunk(bs))
    
    mdl = Model()
    
    #parse
    for c in chunks:
        bs.seek(c.offset)
        if c.name   == "MDL HDET": HDET(mdl,bs)
        elif c.name == "MDL STHB": STHB(mdl,bs)
        elif c.name == "MDL IMGB": IMGB(mdl,bs)
        elif c.name == "MDL MTLB": MTLB(mdl,bs)
        elif c.name == "MDL NDEB": NDEB(mdl,bs)
        elif c.name == "MDL INVB": INVB(mdl,bs)
        elif c.name == "MDL GEOB":
            A=[bs.readInt() for x in range(4)]
            groupCount=A[1]
            
            for geo in c.child:
                if geo.name == "MDL GEO ":
                    bs.seek(geo.offset)
                    A=[bs.readInt() for x in range(4)]
                    group=[]
                    mdl.groupList.append(group)
                    
                    for sgeo in geo.child:
                        if sgeo.name == "MDL SGEO":
                            bs.seek(sgeo.offset)
                            meshList=[]
                            group.append(meshList)
                            vertexInfo=VertexInfo()
                            SGEO(vertexInfo,bs)
                            
                            for geop in sgeo.child:
                                if geop.name =='MDL GEOP':
                                    bs.seek(geop.offset)
                                    mesh=Mesh()
                                    meshList.append(mesh)
                                    mesh.vertexInfo=vertexInfo
                                    GEOP(mesh,bs)

        elif c.name == "MDL IGOB":
            #fix bones
            for bone in mdl.skeleton:
                pIndex = bone.parentIndex
                if pIndex != -1:
                    bone.setMatrix(bone.getMatrix() * mdl.skeleton[pIndex].getMatrix())
            
            for x in range(groupCount):
                A=[bs.readInt() for x in range(4)]
                group=mdl.groupList[A[1]]
                
                for n in range(A[2]):
                    meshList=group[n]
                    
                    for m in meshList:
                        if m.countMat>1:
                            print("mesh SPLIT")
                        matID=bs.readInt()
                        
                        m.createWeight(mdl.boneMap)
                        if not m.VertWeight:
                            boneID = A[0]
                            matBone = mdl.skeleton[boneID].getMatrix()
                            for v in range(len(m.vertPosList)):
                                m.vertPosList[v]=m.vertPosList[v]*matBone
                                m.VertWeight.append(NoeVertWeight([boneID],[1.0]))

                        mesh = NoeMesh(m.indiceList,m.vertPosList, "mesh"+str(len(meshes)))
                        mesh.setUVs(m.vertUVList)
                        mesh.setMaterial(mdl.matList[matID].name)
                        mesh.setWeights(m.VertWeight)
                        meshes.append(mesh)
    
    #ANIMATIONS
    animList = []
    dirPath = rapi.getDirForFilePath(rapi.getInputName())
    """
    #open one anim
    animPath = os.path.abspath(os.path.join(dirPath, "../motion/walk.anm"))
    openAnim(animPath, animList, mdl.skeleton)
    
    #open one anim (open dialog)
    openDialogFile(animList, mdl.skeleton)

    #open all anim from dir (open dialog)
    openDialogFolder(animList, mdl.skeleton)
    """
    #open all anim from dir
    animDir =  os.path.abspath(os.path.join(dirPath, "../motion"))
    openAllAnimFromFolder(animList, mdl.skeleton, animDir)

    modelTest = NoeModel(meshes)
    modelTest.setBones(mdl.skeleton)
    modelTest.setAnims(animList)
    modelTest.setModelMaterials(NoeModelMaterials([], mdl.matList))
    mdlList.append(modelTest)
    return 1  

def noepyLoadAnim(data, bones, animName="anim"):
    bs = NoeBitStream(data)
    bs.seek(16)
    Tag = noeAsciiFromBytes(bs.readBytes(3))
    if Tag != 'ANM':
        return 0
    bs.seek(0)
    if noeAsciiFromBytes(bs.readBytes(8))!='ENDILTLE':
        bs.setEndian(NOE_BIGENDIAN)
    bs.seek(8, NOESEEK_REL)
        
    file_size = bs.getSize()
    chunks = []
    
    #read chunks
    while bs.getOffset() < file_size:
        chunks.append(readChunk(bs))
        
    anim = Animation()
    
    #parse
    boneList={}
    for c in chunks:
        bs.seek(c.offset)
        if c.name=='ANM ANMB':
            A=[bs.readInt() for x in range(12)]
            groupCount=A[1]
            
            for anmb in c.child:
                bs.seek(anmb.offset)
                if anmb.name=='ANM ANM ':
                    A=[bs.readInt() for x in range(8)]
                    name=anim.idList[A[1]]
                    if name not in boneList:
                        bone=ActionBone()
                        bone.name=name
                        boneList[name]=bone
                    else:
                        bone=boneList[name]
                    if A[3]==2:
                        for m in range(A[7]):
                            time=bs.readFloat()#*33
                            bone.rotKeyList.append(NoeKeyFramedValue(time, NoeQuat.fromBytes(bs.readBytes(16)).transpose()))
                    if A[3]==3:
                        for m in range(A[7]):
                            time=bs.readFloat()#*33
                            pos=[bs.readFloat() for x in range(4)]
                            bone.posKeyList.append(NoeKeyFramedValue(time, NoeVec3(pos[:3])))
        elif c.name=='ANM STHB':STHB(anim,bs)
    
    #Animation
    animBones = []
    for key in boneList:
        b = NoeKeyFramedBone(idBone(key,bones))
        b.setRotation(boneList[key].rotKeyList)
        b.setTranslation(boneList[key].posKeyList)
        animBones.append(b)

    anim = NoeKeyFramedAnim(animName, bones, animBones, 30)
    return anim
    
def HDET(model,bs):
    model.texCount = bs.readInt()
    model.matCount = bs.readInt()
    bs.readInt()
    model.boneCount = bs.readInt()

def STHB(model,bs):
    count = bs.readInt()
    size = bs.readInt()
    size_str = bs.readInt()
    zero = bs.readInt()
    curPos = bs.getOffset()
    
    offList = []
    for m in range(count):
        offList.append([bs.readInt(), bs.readInt()])
    
    bs.seek(curPos+size)    
    curPos = bs.getOffset()
    model.idList={}
    
    for [id,off] in offList:
        bs.seek(curPos+off)    
        name = searchString(bs)
        model.idList[id] = name  

def IMGB(model,bs):
    for tx in range(model.texCount):
        bs.readInt()
        id_tx = bs.readInt()
        model.texList.append(model.idList[id_tx])

def MTLB(model,bs):
    dirPath = rapi.getDirForFilePath(rapi.getInputName())
    for mt in range(model.matCount):
        A = [bs.readInt() for x in range(12)]
        always=0
        for n in range(A[3]):
            B=[bs.readInt() for x in range(2)]
            value=[]
            if B[1]==14:value=[bs.readInt() for x in range(2)]
            elif B[1]==1:value=[bs.readInt() for x in range(2)]
            elif B[1]==4:value=[bs.readInt() for x in range(6)]
            elif B[1]==3:value=[bs.readInt() for x in range(6)]
            elif B[1]==2:value=[bs.readInt() for x in range(2)]
            elif B[1]==13:value=[bs.readInt() for x in range(18)]
            elif B[1]==14:value=[bs.readInt() for x in range(2)]
            elif B[1]==19:value=[bs.readInt() for x in range(6)]
            elif B[1]==21:value=[bs.readInt() for x in range(6)]
            else:
                print('Warning:',B,bs.getOffset())
                break
            if B[1]==19 and always==0:
                diffTexID=value[0]
                model.matList.append(NoeMaterial("mat_"+str(mt),os.path.abspath(os.path.join(dirPath, model.texList[diffTexID]))))
                always=1       

def NDEB(model,bs):
    boneList = []
    model.skeleton = boneList
    
    for b in range(model.boneCount):
        name = model.idList[bs.readInt()]
        parentID = bs.readInt()
        bs.seek(8, NOESEEK_REL)
        matrix = NoeMat44.fromBytes(bs.readBytes(64)).toMat43().transpose()
        bone = NoeBone(len(boneList), name, matrix, None, parentID)
        boneList.append(bone)

def INVB(model,bs):
    A=[bs.readInt() for x in range(8)] 
    model.boneMap = [bs.readInt() for x in range(A[1])]

def SGEO(vertexInfo,bs):
    B=[bs.readInt() for x in range(4)]
    BB=[bs.readFloat() for x in range(7)]
    A=[bs.readInt() for x in range(5)]
    vertexInfo.posOff=None
    vertexInfo.posType=None
    vertexInfo.uvOff=None
    vertexInfo.uvType=None
    vertexInfo.skinIndiceOff=None
    vertexInfo.skinIndiceType=None
    vertexInfo.skinWeightOff=None
    vertexInfo.skinWeightType=None
    vertexInfo.hash=B[1]
    
    for m in range(A[1]):
        B=[bs.readInt() for x in range(8)]    
        if B[0]==0:
            vertexInfo.posOff=B[4]
            if B[2]==2:    
                vertexInfo.posType='float'
        if B[0]==5 and B[1]==0:
            vertexInfo.uvOff=B[4]
            if B[2]==2:    
                vertexInfo.uvType='float'
            if B[2]==4:    
                vertexInfo.uvType='half'
                
        if B[0]==2 and B[1]==0:
            vertexInfo.skinIndiceOff=B[4]
            if B[2]==11:    
                vertexInfo.skinIndiceType='byteAsInt'
                
        if B[0]==1 and B[1]==0:
            vertexInfo.skinWeightOff=B[4]
            if B[2]==10:    
                vertexInfo.skinWeightType='byteAsFloat'
                
    vertexInfo.stride=A[4]

def GEOP(mesh,bs):
    A=[bs.readInt() for x in range(12)]
    start=bs.tell()
    #mat=Mat()
    mesh.countMat += 1
    for m in range(A[4]):
        t=bs.tell()
        if mesh.vertexInfo.posOff is not None:
            bs.seek(t+mesh.vertexInfo.posOff,NOESEEK_ABS)
            if mesh.vertexInfo.posType=='float':
                mesh.vertPosList.append(NoeVec3([bs.readFloat() for x in range(3)]))
        if mesh.vertexInfo.uvOff is not None:
            bs.seek(t+mesh.vertexInfo.uvOff,NOESEEK_ABS)
            if mesh.vertexInfo.uvType=='half':
                mesh.vertUVList.append(NoeVec3([bs.readHalfFloat() for x in range(2)]+[0]))
                
        if mesh.vertexInfo.skinIndiceOff is not None:
            bs.seek(t+mesh.vertexInfo.skinIndiceOff,NOESEEK_ABS)
            if mesh.vertexInfo.skinIndiceType=='byteAsInt':
                mesh.skinIndiceList.append([bs.readUByte() for x in range(4)])
                
        if mesh.vertexInfo.skinWeightOff is not None:
            bs.seek(t+mesh.vertexInfo.skinWeightOff,NOESEEK_ABS)
            if mesh.vertexInfo.skinWeightType=='byteAsFloat':
                mesh.skinWeightList.append([bs.readUByte()/255 for x in range(4)])
        bs.seek(t+mesh.vertexInfo.stride,NOESEEK_ABS)
    
    bs.seek(start+A[6],NOESEEK_ABS)  
    mesh.indiceList=[bs.readUShort() for x in range(A[8])]
            
def searchString(bs):
    bytes = []
    byte = None
    while byte != 0:
        byte = bs.readUByte()
        bytes.append(byte)
    return noeAsciiFromBytes(bytes)

def readChunk(bs):
    name = noeStrFromBytes(bs.readBytes(8))
    size = bs.readInt()
    child_offset = bs.readInt()
    offset = bs.getOffset()
    child = []
    
    if child_offset != 0:
        while bs.getOffset() < offset+size:
            if not child:
                bs.seek(child_offset-16, NOESEEK_REL)
            child.append(readChunk(bs))
    else:
        bs.seek(size, NOESEEK_REL)
    return chunk(name, size, offset, child)

def idBone(name,bones):
    for i,bone in enumerate(bones):
        if name == bone.name:
            return i
    return -1
    
class chunk:
    def __init__(self, name, size, offset, child):
        self.name = name
        self.size = size
        self.offset = offset
        self.child = child

class Model:
    def __init__(self):
        self.texList = []
        self.matList = []
        self.groupList = []
        self.boneMap = []

class Animation:
    def __init__(self):
        self.idList=[]

class ActionBone:
    def __init__(self):
        self.name=None
        self.posKeyList=[]
        self.rotKeyList=[]

class VertexInfo:
    pass 

class Mesh:
    def __init__(self):
        self.vertPosList = []
        self.vertNormList=[]
        self.vertUVList = []
        self.skinIndiceList = []
        self.skinWeightList = []
        self.VertWeight = []
        self.indiceList = []
        self.countMat = 0
        
    def createWeight(self, boneMap):
        if self.skinIndiceList and self.skinWeightList:
            for i in range(len(self.vertPosList)):
                self.skinIndiceList[i] = [boneMap[x] for x in self.skinIndiceList[i]]
                self.VertWeight.append(NoeVertWeight(self.skinIndiceList[i],self.skinWeightList[i]))
            self.skinIndiceList = None
            self.skinWeightList = None

#========ANIMATIONS_OPEN_FUNC========
def openAllAnimFromFolder(animList, bones, animDir):
    animPaths = []
    if animDir and os.path.exists(animDir):
        for root, dirs, files in os.walk(animDir):
            for fileName in files:
                lowerName = fileName.lower()
                if lowerName.endswith(".anm"):
                    fullPath = os.path.join(root, fileName)
                    animPaths.append(fullPath)
        
        for animPath in animPaths:
            openAnim(animPath, animList, bones)

def openAnim(animPath, animList, bones):
    with open(animPath, "rb") as animStream:
        animName = os.path.basename(animPath)[:-4]
        animList.append(noepyLoadAnim(animStream.read(), bones, animName))
        
def openDialogFolder(animList, bones):
    animDir = noesis.userPrompt(noesis.NOEUSERVAL_FOLDERPATH, "Open Folder", "Select the folder to get the animations from", noesis.getSelectedDirectory())
    openAllAnimFromFolder(animList, bones, animDir)
    
def openDialogFile(animList, bones):
    animPath = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Open File", "Select animations", noesis.getSelectedFile())
    if animPath and os.path.exists(animPath):
        openAnim(animPath, animList, bones)