#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Bolt (PC)", ".oct")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def noepyCheckType(data):
    return 1

txtFlag = False

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    dir = rapi.getDirForFilePath(rapi.getInputName())
    nodeList=[]
    w = [bs.readInt() for x in range(6)]
    bs.seek(60)
    t = bs.getOffset()
    strings = [""]

    s = ""
    bs.seek(1,1)
    while bs.getOffset() < w[3]+60:
        s = searchString(bs)
        strings.append(s)
    bs.seek(t+w[3])

    parentIDList={}
    parentIDList[str(-1)]=-1

    nodeID=0
    while(True): 
        if bs.getOffset()==bs.getSize():break
        flag = bs.readUShort()
        ID=bs.readUShort()
        name = strings[ID]
        node=Node()
        node.name=name

        indent,format = divmod(flag,0x400)
        if txtFlag==True:
            print("\t"*(indent) + name + "[%04x]"%format, 'flag:', flag)
        data=None
        node.ID=nodeID
        parentIDList[str(indent)]=nodeID
        node.parentID=parentIDList[str(indent-1)]

        if format == 0x01:
            data='TREE'
            
        elif format == 0x05:
            ID=bs.readShort()
            data = strings[ID]
        elif format == 0x0A:
            count = bs.readByte()
            data = []
            for i in range(count):
                data.append(strings[bs.readShort()])
        elif format == 0x0B:
            data = strings[bs.readShort()]
        elif format == 0x12:
            count = bs.readByte()
            data = []
            for i in range(count):
                data.append(bs.readFloat())
        elif format == 0x13:
            data = bs.readFloat()
        elif format == 0x1A:
            count = bs.readUByte()
            data = []
            for i in range(count):
                data.append(bs.readByte())
        elif format == 0x1B:
            data = bs.readUByte()
        elif format == 0x23:
            count = bs.readUByte()
            data = []
            for i in range(count):
                data.append(bs.readByte())
        elif format == 0x4A:
            count = bs.readShort()
            data = []
            for i in range(count):
                data.append(strings[bs.readShort()])
        elif format == 0x5A:
            count = bs.readUShort()
            data = []
            for i in range(count):
                data.append(bs.readByte())
        elif format == 0x63: # binary data
            count = bs.readUShort()
            data = bs.readBytes(count)
        elif format == 0x11A:
            count = bs.readUByte()
            data = []
            for i in range(count):
                data.append(bs.readShort())
        elif format == 0x11B:
            data = bs.readShort()
        elif format == 0x15A:
            count = bs.readShort()
            data = []
            for i in range(count):
                data.append(bs.readShort())
        elif format == 0x21A:
            count = bs.readByte()
            data = []
            for i in range(count):
                data.append(bs.readUInt24())
        elif format == 0x21B:
            data = bs.readUInt24()
        elif format == 0x31B:
            data = bs.readInt()
        elif format == 0xa3:#DDS DX5
            size = bs.readUInt24()
            data=bs.readBytes(size)
        else:
            print("unknown format: %x offset: %i"%(flag,bs.getOffset()))
            break
        if txtFlag==True:
            print("\t"*(indent) +str(data))
        node.data=data
        nodeList.append(node)
        nodeID+=1
        
    for ID in range(len(nodeList)):
        node=nodeList[ID]
        if node.parentID!=-1:
            parent=nodeList[node.parentID]
            parent.childList.append(node)
    
    #DRAW
    rootNode=nodeList[0]
    
    #CREATE_TEXTURE------------------------
    texList = []
    TexturePool = getNode(rootNode,'TexturePool')
    for i,texture in enumerate(TexturePool.childList):
        name = getNode(texture,'Name').data
        path = getNode(texture,'SourceFilePath').data
        type = getNode(texture,'Type').data
        texList.append(rapi.loadTexByHandler(getNode(texture,'Data').data, '.dds'))
        texList[-1].name = name
    
    #CREATE_MATERIAL------------------------
    materials = []
    MaterialPool = getNode(rootNode,'MaterialPool')
    for i,material in enumerate(MaterialPool.childList):
        name, tx = getNode(material,'Name').data, ''
        for prop in material.childList:
            if prop.name == 'TextureEntries':
                for entries in prop.childList:
                    usage = getNode(entries,'Usage').data
                    if usage == 'diffuseMapA1':
                        TxID = getNode(entries,'TextureReference').data
                        try:
                            tx = texList[int(TxID)].name
                        except:
                            print('Error, no texture with index [%i]!'%TxID)
        materials.append(NoeMaterial(name, tx))
    
    #OPEN_BUFFER------------------------
    VertexBufferPool = getNode(rootNode,'VertexBufferPool')
    IndexBufferPool = getNode(rootNode,'IndexBufferPool')
    
    for VertexBuffer in VertexBufferPool.childList:
        if getNode(VertexBuffer,'FileName'):
            VertexBufferPool = os.path.join(dir, getNode(VertexBuffer,'FileName').data)
            break
            
    for IndexBuffer in IndexBufferPool.childList:
        if getNode(IndexBuffer,'FileName'):
            IndexBufferPool = os.path.join(dir, getNode(IndexBuffer,'FileName').data)
            break
    
    haveBuff = True
    
    if rapi.checkFileExists(VertexBufferPool):
        vbuf_stream = NoeBitStream(rapi.loadIntoByteArray(VertexBufferPool))
        pass
    else:
        haveBuff = False
        print('Error, no Vertex Buffer File [%s]!'%str(VertexBufferPool))
    
    if rapi.checkFileExists(IndexBufferPool):
        ibuf_stream = NoeBitStream(rapi.loadIntoByteArray(IndexBufferPool))
        pass
    else:
        haveBuff = False
        print('Error, no Index Buffer File [%s]!'%str(IndexBufferPool))
    
    #FIND_SUBMESH_AND_BONE------------------------
    subMeshes, bones = [], []
    SceneTreeNodePool = getNode(rootNode,'SceneTreeNodePool')
    for node in SceneTreeNodePool.childList:
        if getNode(node,'Type').data == 'SubGeometry':
            Technique = 'ShellBase'
            if getNode(node,'Technique'):
                Technique = getNode(node,'Technique').data
            if Technique == 'ShellBase':
                name = getNode(node,'NodeName').data
                matID = getNode(node,'MaterialReference').data
                vstream = getNode(node,'VertexStreamReferences').data[0]
                istream = getNode(node,'IndexStreamReference').data
                bmap = getNode(node,'SceneComponentReferences').data[0]
                subMeshes.append(subMesh(name, matID, vstream, istream, bmap))
                #print(subMeshes[-1])
        elif getNode(node,'Type').data == 'Bone':
            name = getNode(node,'NodeName').data
            BoneID = getNode(node,'BoneID').data
            mat44 = getNode(node,'BoneToStandardMatrix').data
            mat43 = NoeMat44([NoeVec4(mat44[:4]),NoeVec4(mat44[4:8]),NoeVec4(mat44[8:12]),NoeVec4(mat44[12:])]).toMat43().inverse()
            parent = getNode(node,'ParentNodeReferences').data[0]
            parent = getNode(SceneTreeNodePool.childList[parent],'BoneID')
            if parent:
                parent = parent.data
            else:
                parent = -1
            bones.append(NoeBone(BoneID, name, mat43, None, parent))
    
    #CREATE_MESH------------------------
    if haveBuff:
        #BONEMAP------------------------
        boneMap = []
        SceneComponentPool = getNode(rootNode,'SceneComponentPool')
        for SceneComponent in SceneComponentPool.childList:
            RemapData = getNode(SceneComponent,'RemapData').data
            boneMap.append(RemapData)

       #INDICES_STREAM------------------------
        istreams = []
        IndexStreamPool = getNode(rootNode,'IndexStreamPool')
        for IndexStream in IndexStreamPool.childList:
            length = getNode(IndexStream,'Length').data
            offset = getNode(IndexStream,'IndexBufferOffset').data
            istreams.append([length,offset])

        #VERTEX_STREAM------------------------
        VertexStreamPool = getNode(rootNode,'VertexStreamPool')
        for i,VertexStream in enumerate(VertexStreamPool.childList):
            Length = getNode(VertexStream,'Length').data
            Width = getNode(VertexStream,'Width').data
            VertexBufferOffset = getNode(VertexStream,'VertexBufferOffset').data
            Elements = getNode(VertexStream,'Elements')
            #Position,Uv1,Tangent,Binormal,Normal,BoneIndices,BlendWeights
            attr = [0,0,0,0,0,0,0]
            #parse Elements...
            for Element in Elements.childList:
                ename = getNode(Element,'Name').data
                eofs = getNode(Element,'Offset').data
                '''
                type:2-[3]float;44-[2]HalfFloat;45-[4]HalfFloat;24-[4]bytes(asInt);25-[4]bytes(asFloat)
                '''
                if ename == 'Position':
                    attr[0] = eofs
                elif ename == 'Uv1':
                    attr[1] = eofs
                elif ename == 'Tangent':
                    attr[2] = eofs
                elif ename == 'Binormal':
                    attr[3] = eofs
                elif ename == 'Normal':
                    attr[4] = eofs
                elif ename == 'BoneIndices':
                    attr[5] = eofs
                elif ename == 'BlendWeights':
                    attr[6] = eofs
                
            vbuf_stream.seek(VertexBufferOffset)
            VBUF = vbuf_stream.readBytes(Length*Width)
            rapi.rpgBindPositionBuffer(VBUF, noesis.RPGEODATA_FLOAT, Width)
            if attr[1]:
                rapi.rpgBindUV1BufferOfs(VBUF, noesis.RPGEODATA_HALFFLOAT, Width, attr[1])
            if attr[5] and attr[6]:
                rapi.rpgBindBoneIndexBufferOfs(VBUF, noesis.RPGEODATA_UBYTE, Width, attr[5], 4)
                rapi.rpgBindBoneWeightBufferOfs(VBUF, noesis.RPGEODATA_UBYTE, Width, attr[6], 4)
            
            for sMesh in subMeshes:
                if i == sMesh.vstream:
                    rapi.rpgSetBoneMap(boneMap[sMesh.bmap])
                    rapi.rpgSetName(sMesh.name)
                    rapi.rpgSetMaterial(materials[sMesh.mat].name)
                    iLength, offset = istreams[sMesh.istream]
                    ibuf_stream.seek(offset)
                    IBUF = ibuf_stream.readBytes(iLength*2)
                    rapi.rpgCommitTriangles(IBUF, noesis.RPGEODATA_USHORT, iLength, noesis.RPGEO_TRIANGLE)

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    
    mdl.setBones(bones)
    mdl.setModelMaterials(NoeModelMaterials(texList, materials))
    mdlList.append(mdl)
    return 1
    
def searchString(bs):
    bytes = []
    byte = None
    while byte != 0:
        byte = bs.readUByte()
        bytes.append(byte)
    return noeAsciiFromBytes(bytes)
    
def getNode(parentnode,name):
    for child in parentnode.childList:
        if name==child.name:
            return child     
    return None
    
class Node:
    def __init__(self):
        self.ID=None
        self.name=''
        self.parentID=None
        self.data=None
        self.childList=[]
    
    def __repr__(self):
        return "Node(ID:" + repr(self.ID) + ",name:" + repr(self.name) + ",parentID:" + repr(self.parentID) + ",data:" + repr(self.data) + ",childs:" + repr(len(self.childList))+ ")"
       
class subMesh:
    def __init__(self, name, mat, vstream, istream, bmap):
        self.name=name
        self.mat=mat
        self.vstream=vstream
        self.istream=istream
        self.bmap=bmap
    
    def __repr__(self):
        return "subMesh(name:" + repr(self.name) + ",matID:" + repr(self.mat) + ",vstream:" + repr(self.vstream) + ",istream:" + repr(self.istream) +  ")"