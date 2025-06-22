#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Pull The Trigger", ".gb3")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    return 1
    
globalMesh = None

    
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    '''
    bs.seek(45) # 0-;1-FileSize;2-...
    
    size = bs.readUInt()
    num = bs.readUInt()
    for x in range(num):
        numElem = bs.readUInt()
        bs.seek(numElem*20,1) # uint, 4 float
        name = bs.readString()
        
    # skip/read
    bs.seek(81,1)
    nameTx = bs.readString()
    bs.seek(48,1)
    nameMat = bs.readString()
    bs.seek(8,1)
    nameParam = bs.readString()
    bs.seek(184,1)
    
    print(nameTx, nameMat, nameParam)
    '''
    
    '''
    bs.seek(4) # magic І±.. [B2 B1 00 00]
    fileSize = bs.readUInt()
    
    while bs.tell() < fileSize:
        cpos = bs.tell()
        blockID = bs.readUInt()
        blockSize = bs.readUInt()
        print(blockID, blockSize, [cpos])
        
        if blockID == 2702245888:
            
        elif blockID == 2769289216:
            
        elif blockID == 2785017856:
            pass # tx
        elif blockID == 2734686208:
            pass # material
        elif blockID == 2702180352:
            pass
        elif blockID == 2718957568:
            pass
            
        bs.seek(cpos+blockSize)
    '''
    readBlock(bs)
        
    print('end:', bs.tell())
    
    if globalMesh:
        globalMesh.createMesh()
    
    rapi.rpgOptimize()
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdl.setModelMaterials(NoeModelMaterials([],[NoeMaterial('default', '')]))
    mdlList.append(mdl)
    return 1


def readBlock(bs, indent=0):
    cpos = bs.tell()
    blockID = bs.readUInt()
    blockSize = bs.readUInt()
    
    print('    '*indent, blockID, blockSize, [cpos])
    
    readChild = False
    
    _ = noeUnpack('4B', noePack('I', blockID))
    if _[-1]:
        readChild = True
    
    if blockID == 45490: # first
        readChild = True
    
    elif blockID == 32784:
        label = bs.readString()
        print('    '*indent,'label:', label)
      
    # state
    elif blockID == 2702245888:
        global globalMesh
        globalMesh = Mesh(bs)
    #elif blockID == 2702180352:
    #    globalState = 'Node1'
    #elif blockID == 2718957568:
    #    globalState = 'Node2'
    # end state

    elif blockID == 45072: # mesh
        #readMesh(bs)
        if globalMesh:
            globalMesh.vertOfs = bs.tell()
    elif blockID == 45168: # uvs
        if globalMesh:
            globalMesh.uvsOfs = bs.tell()
    elif blockID == 45136: # normals
        if globalMesh:
            globalMesh.normOfs = bs.tell()

    if readChild and blockID and blockSize:
        while bs.tell() < cpos + blockSize:
            readBlock(bs, indent+1)

    bs.seek(cpos+blockSize)
    
def readMesh(bs):
    inum = bs.readUInt()
    print('inum:', inum)
    ibuf = bs.readBytes(inum*12)
    
    vnum = bs.readUInt()
    print('vnum:', vnum)
    vbuf = bs.readBytes(vnum*12)
    
    rapi.rpgSetName('mesh_%i'%bs.tell())
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_UINT, inum*3, noesis.RPGEO_TRIANGLE)
    rapi.rpgClearBufferBinds()
    
class Mesh:
    def __init__(self, bs):
        self.bs = bs
        self.vertOfs = 0
        self.uvsOfs = 0
        self.normOfs = 0
        
    def createMesh(self):
        bs = self.bs
        bs.seek(self.vertOfs)
        
        rawVertFace = []
        inum = bs.readUInt()
        for x in range(inum):
            rawVertFace.append(bs.read('3I'))
        
        rawVert = []
        vnum = bs.readUInt()
        for x in range(vnum):
            rawVert.append(bs.read(12))
            
        bs.seek(self.uvsOfs)
        rawUVsFace = []
        for x in range(inum):
            rawUVsFace.append(bs.read('3I'))
            
        rawUVs = []
        uvnum = bs.readUInt()
        for x in range(uvnum):
            rawUVs.append(bs.read(12))
            
        vbuf, uvbuf = b'', b''
        for x in range(inum):
            for i in range(3):
                vbuf += rawVert[rawVertFace[x][i]]
                uvbuf += rawUVs[rawUVsFace[x][i]]
                
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
        rapi.rpgSetUVScaleBias(NoeVec3([1,-1,1]), None)
        rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 12)
        rapi.rpgCommitTriangles(None, noesis.RPGEODATA_UINT, len(vbuf)//12, noesis.RPGEO_TRIANGLE)
        rapi.rpgClearBufferBinds()