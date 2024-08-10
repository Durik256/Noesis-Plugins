from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("3d looney tunes dash", ".fmlb")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data)
    if noeAsciiFromBytes(bs.readBytes(4)) != '_FML':
        return 0
    return 1   
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(16)#_FML + ver?
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

    #mdl = NoeModel(meshes)
    #mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial("mat_0","")]))
    #mdlList.append(mdl)
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