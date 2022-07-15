#by Durik256 13.03.2022 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("chuanshuo OL",".mesh")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    bs = NoeBitStream(data)
    if noeAsciiFromBytes(bs.readBytes(8)) != 'MESH2.00':
        return 0
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    name = rapi.getInputName().replace('.mesh','.obj')
    exportOBJ(bs, name)
    noesis.openAndRemoveTempFile(name)
    return 1
    
def exportOBJ(bs, name):
    with open(name, 'w') as f:
        bs.seek(12)
        vCount = bs.readUInt()
        f.write('mtllib default.mtl\n')
        for x in range(vCount):
            f.write('v %f %f %f \n' % (bs.readFloat(), bs.readFloat(), bs.readFloat()))
        for x in range(vCount):
            f.write('vn %f %f %f \n' % (bs.readFloat(), bs.readFloat(), bs.readFloat()))
        bs.seek(vCount*4, 1)
        uvCount = bs.readUInt()
        for x in range(uvCount):
            f.write('vt %f %f \n' % (bs.readFloat(), bs.readFloat()))
        bs.seek(uvCount*8, 1)
        bs.readUInt()
        fCount = bs.readUInt()
        f.write('usemtl Material\n')
        for x in range(fCount):
            a0, b0, c0 = bs.readInt()+1, bs.readInt()+1, bs.readInt()+1
            a1, b1, c1 = bs.readInt()+1, bs.readInt()+1, bs.readInt()+1
            bs.seek(12, 1)
            f.write('f %d/%d/%d %d/%d/%d %d/%d/%d \n' % (a0,a1,a0, b0,b1,b0, c0,c1,c0))
        return 1