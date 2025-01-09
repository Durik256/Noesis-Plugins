#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Resident Evil Mercenaries", ".mcms") #  VS (iOS)
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    return 1   

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    unk, fOfs, fSize = bs.read('3I')

    
    bs.seek(fOfs)
    bs.read(12) # MCM_, 0, 0
    
    while bs.tell() < bs.getSize():
        numBlock = bs.readUShort()
        print('numBlock:', numBlock)
        
        for x in range(numBlock):
            cpos = bs.tell()
            sizeBlock = bs.readUInt()
            
            # '''
            bs.seek(19,1)
            _ = bs.readUInt()
            if _ == 768:
                print(' vblock?::')
                bs.seek(cpos+21)
                vnum = bs.readUShort()
                bs.seek(cpos+85)
                print('vnum:',vnum, 'vofs:',bs.tell())
                vbuf = bs.read(vnum*12)
                rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
                rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, vnum, noesis.RPGEO_POINTS)
                
            elif _ == 65536:
                print(' iblock?::')
                bs.seek(cpos+37)
                inum = bs.readUShort()
                print('inum:',inum, 'iofs:',bs.tell())
                ibuf = bs.read(inum*2)
            # '''
            
            bs.seek(cpos+sizeBlock)
    
    print('END:', bs.tell())
    
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    
    mdlList.append(mdl)
    return 1
