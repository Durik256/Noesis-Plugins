#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("sims 1", ".s_msh")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    return 1
    
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    bs.seek(6)
    label = bs.readString()
    bs.seek(52,1)
    
    numSM = bs.readUInt()
    print('numSM:',numSM)
    multi_weight = False
    for x in range(numSM):#
        u = bs.read('5B')
        if u[0] == 2:
            multi_weight = True
            print('multi_weight = True')
            bs.seek(-4,1)
            u = bs.read('5B')
        print(x,'u:',u, [bs.tell()])
        
        if multi_weight:
            b0, b1, b2 = bs.read('H'), (), ()
            _ = bs.read('2B')
            if _[1]:
                b1 = bs.read('H')
                _ = bs.read('2B')
                if _[1]:
                    b2 = bs.read('2H')
            print('    b0:',b0,'b1:',b1,'b2:',b2)

        vnum = bs.readUInt()
        print('    vnum:',vnum)
        vbuf = bs.read(vnum*8)
        tbuf = bs.read(vnum*4)
        nbuf = bs.read(vnum*3) #?
        if multi_weight:
            wbuf = bs.read(vnum*4)
        #print('END::', bs.tell())
        
        ibuf = createFaces(vbuf, vnum)
        
        #rapi.rpgSetName("mesh_%i"%x)
        rapi.rpgBindPositionBuffer(vbuf,noesis.RPGEODATA_SHORT,8)
        rapi.rpgBindNormalBuffer(nbuf,noesis.RPGEODATA_BYTE,3)
        rapi.rpgSetUVScaleBias(NoeVec3([8]*3),None)
        rapi.rpgBindUV1Buffer(tbuf,noesis.RPGEODATA_SHORT,4)
        
        #rapi.rpgCommitTriangles(None,noesis.RPGEODATA_USHORT,vnum,noesis.RPGEO_POINTS)
        rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_USHORT,len(ibuf)//2,noesis.RPGEO_TRIANGLE_STRIP)

    #rapi.rpgOptimize()
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 -90 0")
    return 1
    
def createFaces(buf, vnum):
    bs = NoeBitStream(buf)
    ibuf = b''
    temp = False
    for x in range(vnum):
        bs.seek(x*8)
        bs.read(6)
        _ = bs.read('2B')
        #print(x,_)
        
        if _[1]:
            if temp:
                temp = False
            else:
                temp = True
                ibuf += noePack('h', -1)
        ibuf += noePack('H', x)
            
    return ibuf
        