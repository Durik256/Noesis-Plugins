# by Durik for xentax.com 
from inc_noesis import *

def registerNoesisTypes():
   handle = noesis.register("Hydro Thunder Hurricane [XB360]", ".dat")
   noesis.setHandlerTypeCheck(handle, CheckType)
   noesis.setHandlerLoadModel(handle, LoadModel)
   return 1

def CheckType(data):
    #if data.find(b'Generic') == -1: 
        #return 0
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.setEndian(1)
    
    for x in range(bs.readUInt()):
        searchString(bs)
        bs.seek(4,1)
    
    stride, vsize = bs.readUInt(), bs.readUInt()
    vbuf = bs.readBytes(vsize)
    
    isize, itype = bs.readUInt(), bs.readUInt()
    ibuf = bs.readBytes(isize)
    
    #create_model
    ctx = rapi.rpgCreateContext()
    
    rapi.rpgSetEndian(1)
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT,stride)
    rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_HALFFLOAT,stride, 20)
    
    dataType, istride = noesis.RPGEODATA_USHORT, 2
    if itype == 3:
        dataType, istride = noesis.RPGEODATA_UINT, 4
    
    rapi.rpgCommitTriangles(ibuf, dataType, isize//istride, noesis.RPGEO_TRIANGLE)
        
    mdl = rapi.rpgConstructModel()
    mdlList.append(mdl)
    return 1
    
def searchString(bs):
    byte = None
    while byte != 0:
        byte = bs.readUByte()