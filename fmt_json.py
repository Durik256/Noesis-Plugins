from inc_noesis import *

def registerNoesisTypes():
   handle = noesis.register("mesh from json", ".json")
   noesis.setHandlerTypeCheck(handle, noepyCheckType)
   noesis.setHandlerLoadModel(handle, noepyLoadModel)
   return 1

def noepyCheckType(data):
   return 1    
   
def slice(l, n):
    n = max(1, n)
    return [l[i:i+n] for i in range(0, len(l), n)]
        
def noepyLoadModel(data, mdlList):
    file = data.decode().split('[')
    file = [file[x].split(']')[0] for x in range(1,4)]
    file = [x.split(',') for x in file]

    Positions = []
    TexCoords = []
    Normals = []
    Face = []
    mesh = []
    for v in slice(file[0], 3):
        Positions.append(NoeVec3([float(x) for x in v]))
    for uv in slice(file[1], 2):
        TexCoords.append(NoeVec3([float(x) for x in uv]+[0.0]))
    for n in slice(file[2], 3):
        Normals.append(NoeVec3([float(x) for x in n]))
    if len(Positions)>64980:
        Face = [x for x in range(64980)]
        mesh.append(NoeMesh(Face, Positions[:64980], "mesh_0", "mat_0"))
        mesh[-1].setNormals(Normals[:64980])
        mesh[-1].setUVs(TexCoords[:64980])
        
        Face = [x for x in range(0,len(Positions)-64980)]
        mesh.append(NoeMesh(Face, Positions[64980:], "mesh_1", "mat_0"))
        mesh[-1].setNormals(Normals[64980:])
        mesh[-1].setUVs(TexCoords[64980:])
    else:
        Face = [x for x in range(len(Positions))]
        mesh.append(NoeMesh(Face, Positions, "mesh_0", "mat_0"))
        mesh[-1].setNormals(Normals)
        mesh[-1].setUVs(TexCoords)
    
    mdl = NoeModel(mesh)
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial("mat_0","")]))
    mdlList.append(mdl)
    return 1