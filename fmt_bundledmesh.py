from inc_noesis import *

def registerNoesisTypes():
   handle = noesis.register("Battlefield 2 (2005)", ".bundledMesh")
   noesis.setHandlerTypeCheck(handle, CheckType)
   noesis.setHandlerLoadModel(handle, LoadModel)
   return 1

def CheckType(data):
    if len(data) < 0x80:
        return 0
    return 1       

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    
    
    header = Header(bs)
    geometry = Geometry(bs)
    u6 = bs.readUInt()
    lods = [Lod(bs) for x in range(sum(geometry.numLods))]
    geomMaterials = [Model(bs) for x in range(sum(geometry.numLods))]
    
    #create Models
    curMesh = 0
    for i in range(geometry.numGeom):
        print("Geom_" + str(i))
        
        materials = {}
        ctx = rapi.rpgCreateContext()
        stride = geometry.vertexStride
        
        for j in range(geometry.numLods[i]):
            print(" -Lod_" + str(j))
            
            for id,mat in enumerate(geomMaterials[curMesh].materials):
                bs.seek(geometry.indices + mat.indicesStartIndex*2)
                faces = bs.readBytes(mat.numIndices*2)
                
                bs.seek(geometry.vertices + mat.verticesStartIndex*stride)
                vbuffer = bs.readBytes(mat.numVertices*stride)
                
                rapi.rpgSetName("   Lod  " + str(j)+"_"+str(id))
                
                nameTexture = rapi.getLocalFileName(mat.textureMapFiles[0])
                nameMat = os.path.splitext(nameTexture)[0]
                materials[nameMat] = NoeMaterial(nameMat, nameTexture)
                
                rapi.rpgSetMaterial(nameMat)
                rapi.rpgBindPositionBuffer(vbuffer, noesis.RPGEODATA_FLOAT, stride)
                
                for el in geometry.vertexElements:
                    print("stride",stride,"flag",el.flag,"varType",el.varType,"offset",el.offset,"usage",el.usage)
                    #varType: 0-(Float1); 1-(Float2); 2-(Float3); 3-(unk);  4-(DWORD);
                    if el.flag == 0:
                        if el.usage == 3:#Normals
                            rapi.rpgBindNormalBufferOfs(vbuffer, noesis.RPGEODATA_FLOAT, stride, el.offset)
                        if el.usage == 5:#Uvs
                            rapi.rpgBindUV1BufferOfs(vbuffer, noesis.RPGEODATA_FLOAT, stride, el.offset)
                        if el.usage == 1:#blend Weight
                            rapi.rpgBindBoneWeightBufferOfs(vbuffer, noesis.RPGEODATA_FLOAT, stride, el.offset, 1)
                        if el.usage == 2:#blend Indices
                            rapi.rpgBindBoneIndexBufferOfs(vbuffer, noesis.RPGEODATA_UINT, stride, el.offset, 1)
                        if el.usage == 6:#tangent
                            rapi.rpgFeedMorphTargetNormalsOfs(vbuffer, noesis.RPGEODATA_FLOAT, stride, el.offset)
                            
                rapi.rpgCommitTriangles(faces, noesis.RPGEODATA_USHORT, mat.numIndices, noesis.RPGEO_TRIANGLE)
                rapi.rpgClearBufferBinds()
            curMesh += 1
        
        materials = [x[1] for x in list(materials.items())]
        
        mdl = rapi.rpgConstructModel()
        mdl.setModelMaterials(NoeModelMaterials([], materials))
        mdlList.append(mdl)
    return 1
    
class Header:
    def __init__(self, bs):
        self.u1 = bs.readUInt()
        self.version = bs.readUInt()
        self.u2 = bs.readUInt()
        self.u3 = bs.readUInt()
        self.u5 = bs.readUInt()
        self.u6 = bs.readByte()

class VertexElement:
    def __init__(self, bs):
        self.flag = bs.readUShort()
        self.offset = bs.readUShort()
        self.varType = bs.readUShort()
        self.usage = bs.readUShort()

class Geometry:
    def __init__(self, bs):
        self.numGeom = bs.readUInt()
        self.numLods = [bs.readUInt() for x in range(self.numGeom)]
        self.numVertexElements = bs.readUInt()
        self.vertexElements = [VertexElement(bs) for x in range(self.numVertexElements)]
        self.vertexFormat = bs.readUInt()
        self.vertexStride = bs.readUInt()
        self.numVertices = bs.readUInt()
        self.vertices =bs.getOffset()
        bs.seek(self.numVertices*self.vertexStride, NOESEEK_REL)
        #self.vertices = [numVertices * (vertexStride / vertexFormat)
        self.numIndices = bs.readUInt()
        self.indices = bs.getOffset()
        bs.seek(self.numIndices*2, NOESEEK_REL)
        #self.indices = [numIndices]

class Lod:
    def __init__(self, bs):
        self.u1 = NoeVec3.fromBytes(bs.readBytes(12))
        self.u2 = NoeVec3.fromBytes(bs.readBytes(12))
        self.numNodes = bs.readUInt()
    
class Material:
    def __init__(self, bs):
        self.alphaMode = bs.readUInt()#opaque = 0, blend = 1, alphatest = 2
        self.shaderFile = noeAsciiFromBytes(bs.readBytes(bs.readUInt()))
        self.technique = noeAsciiFromBytes(bs.readBytes(bs.readUInt()))
        self.numTextureMaps = bs.readUInt()
        self.textureMapFiles = [noeAsciiFromBytes(bs.readBytes(bs.readUInt())) for x in range(self.numTextureMaps)]
        self.verticesStartIndex = bs.readUInt()
        self.indicesStartIndex = bs.readUInt()
        self.numIndices = bs.readUInt()
        self.numVertices = bs.readUInt()
        self.u1 = bs.readUInt()
        self.u2 = bs.readUShort()
        self.u3 = bs.readUShort()
    
class Model:
    def __init__(self, bs):
        self.numMaterials = bs.readUInt()
        self.materials = [Material(bs) for x in range(self.numMaterials)]