# by Durik 05.03.2022 for xentax.com 
from inc_noesis import *

def registerNoesisTypes():
   handle = noesis.register("NovaLogic", ".3di")
   noesis.setHandlerTypeCheck(handle, CheckType)
   noesis.setHandlerLoadModel(handle, LoadModel)
   return 1

def CheckType(data):
    bs = NoeBitStream(data)
    if noeAsciiFromBytes(bs.readBytes(3)) != '3DI':
        return 0
    return 1       

def LoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    bs = NoeBitStream(data)
    fSize = bs.getSize()
    bs.seek(3)
    count = bs.readByte()
    bs.seek(8)#ROOT unk
    
    names = []
    meshes = []
    for x in range(count):
        name = noeAsciiFromBytes(bs.readBytes(4))
        size = bs.readInt()
        print(x, name, size, bs.getOffset())
        if name == 'USRP': 
            smCount, unk = bs.readInt(), bs.readInt()
            print('USRP', smCount)
            for y in range(smCount):
                bs.seek(32, NOESEEK_REL)
                name_mesh = noeAsciiFromBytes(bs.readBytes(16))
                names.append(name_mesh)
                
        elif name == 'VERT': 
            v_info = [bs.readInt(), bs.readInt(), bs.readInt()]
            meshes.append(Mesh(len(meshes), v_info[0], v_info[1], bs.getOffset()))
            bs.seek(size-12, NOESEEK_REL)
        
        elif name == 'INDX':
            meshes[-1].iCount = bs.readInt()
            bs.readInt()
            meshes[-1].iOffset = bs.getOffset()
            bs.seek(size-8, NOESEEK_REL)
        
        elif name == 'STRP':
            num = bs.readInt()
            bsize = bs.readInt()
            for y in range(num):
                id = bs.readInt()
                start_indx = bs.readInt()
                num_indx = bs.readShort()
                num_face = bs.readShort()
                bs.readInt()
                strat_vert = bs.readInt()
                num_vert = bs.readInt()
                bs.seek(24, NOESEEK_REL)
                meshes[-1].submesh.append(subMesh(id, start_indx, num_indx, num_face, strat_vert, num_vert))
        else: 
            bs.seek(size if size > 0 else 0, NOESEEK_REL)
    
    for x in meshes[:1]:
        try: rapi.rpgSetName('LOD_'+str(x.id))
        except: pass
        
        for subm in x.submesh:  
            bs.seek(x.vOffset+subm.strat_vert*x.stride)
            vbuffer = bs.readBytes(subm.num_vert*x.stride)
            
            bs.seek(x.iOffset+subm.start_indx*2)
            ibuffer = bs.readBytes(subm.num_indx*2)
            
            rapi.rpgBindPositionBuffer(vbuffer, noesis.RPGEODATA_FLOAT, x.stride)
            rapi.rpgCommitTriangles(ibuffer, noesis.RPGEODATA_USHORT, subm.num_indx, noesis.RPGEO_TRIANGLE)
            rapi.rpgClearBufferBinds()
        
    mdl = rapi.rpgConstructModel()
    mdlList.append(mdl)
    return 1
    
class Mesh:
    def __init__(self, id, vCount, stride, vOffset):
        self.id = id
        #vert
        self.vCount = vCount
        self.stride = stride
        self.vOffset = vOffset
        #face
        self.iCount = None
        self.iOffset = None
        #submesh
        self.submesh = []
        
class subMesh:
    def __init__(self, id, start_indx, num_indx, num_face, strat_vert, num_vert):
        self.id = id
        self.start_indx = start_indx
        self.num_indx = num_indx
        self.num_face = num_face
        self.strat_vert = strat_vert
        self.num_vert = num_vert