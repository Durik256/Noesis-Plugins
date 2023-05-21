#by Durik256
#fast test parser ogree xml()
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("OGRE", ".mesh;.xml")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def CheckType(data):

    return 1

def LoadModel(data, mdlList):
    data = data.decode().splitlines()
    ctx = rapi.rpgCreateContext()
    
    
    ibuf, vbuf, uvbuf = b'', b'', b''
    i = 0
    while i < len(data):
        line = data[i].strip()
        
        
        
        if line.startswith("<submesh "):
            ibuf, vbuf, uvbuf = b'', b'', b''
        elif line.startswith("<faces "):
            faces =  int(line.split('"')[1])
            for x in range(1,faces+1):
                f = data[i+x].split('"')
                ibuf += noePack('3H', int(f[1]), int(f[3]), int(f[5]))
            i += faces
        elif line.startswith("<vertex>"):
            i += 1
            while True:
                vline = data[i].strip()
                if vline.startswith("<position "):
                    v = vline.split('"')
                    vbuf += noePack('3f', float(v[1]), float(v[3]), float(v[5]))
                    
                elif vline.startswith("<texcoord "):
                    v = vline.split('"')
                    uvbuf += noePack('2f', float(v[1]), float(v[3]))
                elif vline.startswith("</vertex>"):
                    break
                i += 1
        
        elif line.startswith("</submesh>"):
            print(i,line)
            rapi.rpgSetName('submesh_%i'%i)
            rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
            
            rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 8)
            rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, len(ibuf)//2, noesis.RPGEO_TRIANGLE)

            
        i += 1
            

    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default','')]))
    mdlList.append(mdl)
    return 1
