from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Onigiri Online", ".dat")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data, NOE_BIGENDIAN)
    if noeAsciiFromBytes(bs.readBytes(bs.readShort())) != 'KGLMesh1.1:':
        return 0
    return 1   
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data, NOE_BIGENDIAN)
    header = noeAsciiFromBytes(bs.readBytes(bs.readShort()))
    bs.seek(11 ,NOESEEK_REL)
    vCount = int(bs.readShort()/6);
    
    vert = []
    for i in range(vCount):
        vert.append(NoeVec3([bs.readHalfFloat(),bs.readHalfFloat(),bs.readHalfFloat()]))
    
    bs.seek(9 ,NOESEEK_REL)
    nCount = int(bs.readShort()/3);
    
    normal = []
    for i in range(nCount):
        normal.append(NoeVec3([bs.readByte(),bs.readByte(),bs.readByte()]).normalize())
        print(normal[-1])
        
    bs.seek(11 ,NOESEEK_REL)
    uCount = int(bs.readShort()/4);
    
    uv = []
    for i in range(vCount):
        uv.append(NoeVec3([bs.readHalfFloat(),bs.readHalfFloat(),0]))
    
    bs.seek(14 ,NOESEEK_REL)
    iCount = int(bs.readShort()/2);
    
    indices = [bs.readShort() for x in range(iCount)]
    
    bs.seek(4 ,NOESEEK_REL)
    
    matName = noeAsciiFromBytes(bs.readBytes(bs.readShort()))
    print(bs.getOffset())
    
    mesh = NoeMesh(indices, vert, "mesh_0", matName)
    mesh.setUVs(uv)
    mesh.setNormals(normal)
    
    mdl = NoeModel([mesh])
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial(matName,"")]))
    mdlList.append(mdl)
    return 1