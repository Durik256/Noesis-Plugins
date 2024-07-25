# by Durik256
# change ext in your files in folder AkStaticModelAsset *.dat >> *.smdl and in folder AkAnimatedModelAsset *.dat >> *.amdl
from inc_noesis import *

def registerNoesisTypes():
   handle = noesis.register("Hydro Thunder Hurricane [XB360]", ".dat; .smdl; .amdl")
   noesis.setHandlerTypeCheck(handle, CheckType)
   noesis.setHandlerLoadModel(handle, LoadModel)
   return 1

def CheckType(data):
    #if data.find(b'Generic') == -1: 
        #return 0
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data,1)

    for x in range(bs.readUInt()):
        bs.readString()
        bs.seek(4,1)
    
    curEXT = os.path.splitext(rapi.getInputName())[-1].lower()
    bones = []
    
    # read bones
    if curEXT == '.amdl':
        numBones = bs.readUInt()
        for x in range(numBones):
            name = bs.read(32).replace(b'\x00', b'').decode()
            bones.append(NoeBone(x,name,NoeMat43()))
            
        for x in range(numBones):
            bones[x].parentIndex = bs.readInt()
            
        for x in range(numBones):
            f = bs.read('>12f')
            print(f)
            mat = NoeQuat(f[4:8]).toMat43()#NoeMat43()
            mat[3] = NoeVec3(f[:3])
            bones[x].setMatrix(mat)
        
        for x in range(2):
            print(bs.read('>4f'))
    
    stride, vsize = bs.readUInt(), bs.readUInt()
    vbuf = bs.readBytes(vsize)
    
    isize, itype = bs.readUInt(), bs.readUInt()
    ibuf = bs.readBytes(isize)
    
    #create_model
    ctx = rapi.rpgCreateContext()
    
    rapi.rpgSetEndian(1)
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT,stride)
    rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_HALFFLOAT,stride, 20)
    #createWght(vbuf, stride)
    
    dataType, istride = noesis.RPGEODATA_USHORT, 2
    if itype == 3:
        dataType, istride = noesis.RPGEODATA_UINT, 4
    
    rapi.rpgCommitTriangles(ibuf, dataType, isize//istride, noesis.RPGEO_TRIANGLE)
        
    mdl = rapi.rpgConstructModel()
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1
