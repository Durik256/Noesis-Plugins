from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("train", ".model")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data)
    if bs.readUInt() != 2965044855:
        return 0
    return 1   

def noepyLoadModel(data, mdlList):
    result = [i for i in findall(b'SurfaceData', data)]
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    dir = rapi.getDirForFilePath(rapi.getInputName())
    local_name = rapi.getLocalFileName(rapi.getInputName())
    
    vbuf_file = []
    files = os.listdir(dir)
    for file in files:
        if local_name in file and rapi.checkFileExt(file, '.vbuf'):
            vbuf_file.append(os.path.join(dir, file))
            print("vbuf_file>>",file)
    
    if len(vbuf_file) > 1:
        result = result[:1]
    
    vbuf_data = rapi.loadIntoByteArray(vbuf_file[0])#rapi.getInputName() + '.vb0.vbuf'

    if vbuf_data[0] == 4:
        print('>>>>>>>>>>>>>>>>>')
        stride = struct.unpack('I', vbuf_data[28:32])[0]
        vsize = struct.unpack('I', vbuf_data[32:36])[0]
        vbuf_data = vbuf_data[36:]
    else:
        print('<<<<<<<<<<<<<<<<')
        stride = struct.unpack('I', vbuf_data[40:44])[0]
        vsize = struct.unpack('I', vbuf_data[44:48])[0]
        vbuf_data = vbuf_data[48:]
    
    ibuf_data = rapi.loadIntoByteArray(rapi.getInputName() + '.ib0.ibuf')[5:]
    
    vbs = NoeBitStream(vbuf_data)
    ibs = NoeBitStream(ibuf_data)
    
    for x in result:
        bs.seek(x-37)
        inum = bs.readInt()
        print('inum:',inum)

        rapi.rpgSetName('mesh_%i'%x)
        IBUF = ibs.readBytes(inum*2)
        maxI = max(struct.unpack('%iH'%inum, IBUF))+1
        print('max_value:',maxI)
            
        VBUF = vbs.readBytes(maxI*stride)
        rapi.rpgBindPositionBuffer(VBUF, noesis.RPGEODATA_HALFFLOAT, stride)
        rapi.rpgBindUBufferOfs(VBUF, noesis.RPGEODATA_FLOAT, stride, 20)
        rapi.rpgCommitTriangles(IBUF, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)

        #ibs.seek(inum*2)
    rapi.rpgOptimize()
    mdl = rapi.rpgConstructModel()#NoeModel()
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial("mat_0","")]))
    mdlList.append(mdl)
    return 1
    
def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)
    
def noepyLoadModel3(data, mdlList):
    result = [i for i in findall(b'SurfaceData', data)]
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    vbuf_data = rapi.loadIntoByteArray(rapi.getInputName() + '.vb0.vbuf')
    print('00000',vbuf_data[0])
    if vbuf_data[0] == 4:
        print('>>>>>>>>>>>>>>>>>>>>')
        stride = struct.unpack('I', vbuf_data[28:32])[0]
        vsize = struct.unpack('I', vbuf_data[32:36])[0]
        vbuf_data = vbuf_data[36:]
    else:
        print('<<<<<<<<<<<<<<<<')
        stride = struct.unpack('I', vbuf_data[40:44])[0]
        vsize = struct.unpack('I', vbuf_data[44:48])[0]
        vbuf_data = vbuf_data[48:]
    
    for x in result:
        bs.seek(x-37)
        inum = bs.readInt()
        print(inum)
    
    ibuf_data = rapi.loadIntoByteArray(rapi.getInputName() + '.ib0.ibuf')[5:]
    
    vbs = NoeBitStream(vbuf_data)
    ibs = NoeBitStream(ibuf_data)
    
    #rapi.rpgBindPositionBuffer(vbuf_data, noesis.RPGEODATA_HALFFLOAT, stride)
    bs.seek(x-24)
    one_hash = bs.readBytes(4)
    
    for x in result:
        bs.seek(x-24)
        hash = bs.readBytes(4)
        print(hash)
        bs.seek(x-37)
        inum = bs.readInt()
        if one_hash == hash:
            rapi.rpgSetName('mesh_%i'%x)
            IBUF = ibs.readBytes(inum*2)
            maxI = max(struct.unpack('%iH'%inum, IBUF))+1
            print('maxI',maxI)
            
            VBUF = vbs.readBytes(maxI*stride)
            rapi.rpgBindPositionBuffer(VBUF, noesis.RPGEODATA_HALFFLOAT, stride)
            rapi.rpgBindUV1BufferOfs(VBUF, noesis.RPGEODATA_HALFFLOAT, stride, 20)
            rapi.rpgCommitTriangles(IBUF, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
        else:
            ibs.seek(inum*2)
    mdl = rapi.rpgConstructModel()#NoeModel()
    
    mdlList.append(mdl)
    return 1
def noepyLoadModel2(data, mdlList):
    bs = NoeBitStream(data)
    head = [bs.readUInt() for x in range(3)]
    print(head)
    bs.readByte()
    bones = []
    print('start bone:',bs.getOffset())
    for x in range(head[2]):
        name = noeAsciiFromBytes(bs.readBytes(bs.readUInt()+1)).split('|')[-1]
        bones.append(NoeBone(x,name,NoeMat43()))
        print(x,name)
    
    parent = bs.readUInt()
    for x in range(parent):
        bones[x].parentIndex = bs.readInt()
    bs.readByte()
    child = bs.readUInt()
    for x in range(child):
        bs.readInt()
    bs.readByte()
    mat = bs.readUInt()
    print('start mat:',bs.getOffset())
    for x in range(mat):
        bs.seek(5, 1)
        pos = NoeVec3([bs.readFloat() for x in range(3)])
        
        print(pos)
        bs.seek(35, 1)
        '''
        bs.seek(6, NOESEEK_REL)
        pos = NoeVec3.fromBytes(bs.readBytes(12))
        bs.readByte()
        mat = NoeQuat.fromBytes(bs.readBytes(16)).toMat43()
        mat[3] = pos
        bs.readByte()
        scl = NoeVec3.fromBytes(bs.readBytes(12))
        bs.seek(4, NOESEEK_REL)
        '''
        #print([bs.readFloat() for x in range(13)])
        #mat = NoeMat43.fromBytes(bs.readBytes(48)).transpose()
        #bs.seek(4, NOESEEK_REL)
        #print(mat)
        mat = NoeMat43()
        mat[3] = pos
        bones[x].setMatrix(mat)
        
    print(bs.getOffset())
    '''
    name = searchString(bs)
    indices = [x for x in searchString(bs).split(' ')]
    print(name,indices)
    bs.seek(70)
    iCount = bs.readInt()
    vCount = bs.readInt()
    unk1 =  bs.readInt()
    unk2 =  bs.readInt()
    print(name,"iCount:",iCount,"vCount:",vCount,unk1,unk2)
    print("iSize:",iCount*2,"vSize:",vCount*12,"Face Count:",iCount/3)
    bs.seek(6, NOESEEK_REL)
    rotModel = NoeQuat.fromBytes(bs.readBytes(16))
    print("rotModel:",rotModel)
    bs.seek(8, NOESEEK_REL)#2* -1
    #bs.seek(28, NOESEEK_REL)#unk'
    print([bs.readFloat() for x in range(7)])
    print([bs.readUShort() for x in range(34)])
    print("Start Indices:",bs.getOffset())
    indices = [bs.readUShort() for x in range(iCount)]
    print("Start Vertex:",bs.getOffset())
    vert = []
    for v in range(vCount):
        vert.append(NoeVec3.fromBytes(bs.readBytes(12)))
    print("End Vertex:",bs.getOffset())
    norm = []
    for n in range(vCount):
        norm.append(NoeVec3([bs.readHalfFloat(), bs.readHalfFloat(), bs.readHalfFloat()]))
    print("End Normal:",bs.getOffset())
    bs.seek(4, NOESEEK_REL)
    uv = []
    print("Start UVs:",bs.getOffset())
    for u in range(vCount):
        uv.append(NoeVec3([bs.readHalfFloat(), bs.readHalfFloat(), 0]))
    print("End UVs:",bs.getOffset())
    mesh = NoeMesh(indices, vert, name, "mat_0")
    mesh.setUVs(uv)
    mesh.setNormals(norm)

    count = bs.readInt()
    data_offset = bs.readInt()
    unk = bs.readInt()
    bs.seek(20,NOESEEK_REL)#END> + 16bytes unk
    
    print("count:",count,"offset:",data_offset,"unk:",unk)
    
    subMeshes = []
    for x in range(count):
        #type: f(102)-file?; g(103)-texture; h(104)-material; k(107)-geometry; z(122)-sound; r(114)-array?
        #q(113)-anim; 
        type = bs.readUByte()
        bs.seek(11 ,NOESEEK_REL)#zero
        name = searchString(bs)
        bs.seek(19-len(name) ,NOESEEK_REL)
        bs.seek(44 ,NOESEEK_REL)#unk
        offset = bs.readInt()+data_offset
        bs.seek(8 ,NOESEEK_REL)#unk + >>
        print("type",type,name,offset)
        if type==107:
            subMeshes.append(SubMesh(name, offset))
    
    if not len(subMeshes):
        print("Dont have mesh")
        return 0
    
    #bs.seek(data_offset) 
    
    meshes = []
    for x in subMeshes:
        bs.seek(x.offset)
        print(bs.getOffset())
        name = searchString(bs)
        bs.seek(69-len(name),NOESEEK_REL)#seek 70
        iCount = bs.readInt()
        vCount = bs.readInt()
        unk1 =  bs.readInt()
        unk2 =  bs.readInt()
        bs.seek(126,NOESEEK_REL)#seek212
        print(name,"iCount",iCount,"vCount",vCount,unk1,unk2)
        indices = [bs.readUShort() for x in range(iCount)]
        vert = []
        if(bs.readShort() != 0):
            bs.seek(-2,NOESEEK_REL)
        for v in range(vCount):
            vert.append(NoeVec3.fromBytes(bs.readBytes(12)))
        
        mesh = NoeMesh(indices, vert, name, "mat_0")
        #meshes.append(mesh)
        mdlList.append(NoeModel([mesh]))
   
    print(bs.getOffset())

    mdl = NoeModel([mesh])
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial("mat_0","")]))
    mdlList.append(mdl)
    '''
    mdl = NoeModel()
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1
    
def searchString(bs):
    bytes = []
    byte = None
    while byte != 0:
        byte = bs.readUByte()
        bytes.append(byte)
    return noeAsciiFromBytes(bytes)
    
class SubMesh:
    def __init__(self, name, offset):
        self.name=name
        self.offset=offset