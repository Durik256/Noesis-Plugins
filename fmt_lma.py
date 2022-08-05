#by Durik256
#orig Blender script https://forum.xentax.com/viewtopic.php?f=16&t=4592#p48184
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Granado Espada", ".lma")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    if data[:4] != b'LMA ':
        return 0
    return 1
    
def noepyLoadModel(bs, mdlList):
    bs = NoeBitStream(bs)
    ctx = rapi.rpgCreateContext()
    
    bs.seek(127)
    back = bs.getOffset()
    offset = 0
    
    groupList=[]
    matList=[]
    texList=[]
    skinList=[]
    skeleton=[]
    while (offset!=bs.getSize()):
        base = [bs.readInt() for x in range(3)]
        offset = bs.getOffset()
        offset+=base[1]
        if base[0]==0: 
            name = noeAsciiFromBytes(bs.readBytes(40))
            parentName = noeAsciiFromBytes(bs.readBytes(40))
            if len(parentName)==0:
                parentName=None
            bs.seek(40,1)
            matrix = NoeMat44.fromBytes(bs.readBytes(64)).toMat43().inverse()
            skeleton.append(NoeBone(len(skeleton),name,matrix,parentName))
            
        if base[0]==6:#material
            matName = noeAsciiFromBytes(bs.readBytes(40))
            matList.append(NoeMaterial(matName, ''))
            
        if base[0]==7:#texture
            imageName = noeAsciiFromBytes(bs.readBytes(40))
            texList.append([imageName,[bs.readUShort(), bs.readUShort()]])
                   
        if base[0]==3:#mesh
            w=[bs.readInt() for x in range(6)]
            meshList=[] 
            for m in range(w[4]):
                mesh=Mesh()
                mesh.skinID=w[0]
                matID,unk=bs.readUShort(), bs.readUShort()
                mesh.matList = matList[matID-1].name
                indiceCount=bs.readInt()
                vertCount = bs.readInt()
                mesh.skinItemIDList=[]
                for m in range(vertCount):
                    mesh.vertPosList += bs.readBytes(12)
                    bs.seek(12,1)
                    mesh.vertUVList += bs.readBytes(8)
                    mesh.skinItemIDList.append(bs.readInt())
                mesh.indiceList=bs.readBytes(indiceCount*4)                    
                meshList.append(mesh)
            groupList.append(meshList)   
      
        if base[0]==4:#weighting
            skin=Skin()
            skin.ID = bs.readInt()
            
            for m in range(w[1]):
                indiceList=[]
                weightList=[]
                count=bs.readByte()
                
                for j in range(count):    
                    A,B=bs.readUShort(), bs.readUShort()        
                    indiceList.append(A)
                    weightList.append(bs.readFloat())          
                skin.indiceList.append(indiceList)
                skin.weightList.append(weightList)
            skinList.append(skin)
                    
        bs.seek(offset) 
    
    for group in groupList:
        for mesh in group:
            for skin in skinList:
                if skin.ID==mesh.skinID:
                    for itemID in mesh.skinItemIDList:
                        mesh.skinIndiceList.append(skin.indiceList[itemID])
                        mesh.skinWeightList.append(skin.weightList[itemID])
            
            mesh.draw()
    
    mdl = rapi.rpgConstructModel()
    mdl.setBones(skeleton)
    mdl.setModelMaterials(NoeModelMaterials([], matList))
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 90 90")
    return 1
    
def searchString(bs):
    bytes = []
    byte = None
    while byte != 0:
        byte = bs.readUByte()
        bytes.append(byte)
    return noeAsciiFromBytes(bytes)
    
class Mesh():
    def __init__(self):
        self.vertPosList = b''
        self.vertUVList = b''
        self.indiceList = b''
        self.skinIndiceList = []
        self.skinWeightList = []
        
    def draw(self):
        self.createWeight()
        rapi.rpgSetMaterial(self.matList)
        rapi.rpgBindPositionBuffer(self.vertPosList, noesis.RPGEODATA_FLOAT, 12)
        rapi.rpgBindUV1Buffer(self.vertUVList, noesis.RPGEODATA_FLOAT, 8)
        if self.skinIndiceList and self.skinWeightList:
            rapi.rpgBindBoneIndexBuffer(self.skinIndiceList, noesis.RPGEODATA_USHORT, 8, 4)
            rapi.rpgBindBoneWeightBuffer(self.skinWeightList, noesis.RPGEODATA_FLOAT, 16, 4)
        rapi.rpgCommitTriangles(self.indiceList, noesis.RPGEODATA_UINT, len(self.indiceList)//4, noesis.RPGEO_TRIANGLE)
    
    def createWeight(self):
        IWBUF, WBUF = b'', b''
        for x in self.skinIndiceList:
            x += [0]*(4-len(x))
            IWBUF += struct.pack('4H',*x)
        for x in self.skinWeightList:
            x += [0]*(4-len(x))
            WBUF += struct.pack('4f',*x)
        
        self.skinIndiceList = IWBUF
        self.skinWeightList = WBUF

class Skin():
    def __init__(self):
        self.indiceList = []
        self.weightList = []