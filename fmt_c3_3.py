from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Eudemons M", ".c3")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    if data[:16] != b'MAXFILE C3 00001':
        return 0
    return 1
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    bs.seek(16)
    
    while bs.getOffset() < bs.getSize():
        label = bs.readBytes(4)
        size = bs.readInt()
        curPos = bs.getOffset()
        
        if label == b'PHY4':
            name = noeAsciiFromBytes(bs.readBytes(bs.readInt()))
            unk = bs.readInt()

            rapi.rpgSetName(name)
                
            v_num = bs.readInt() + bs.readInt()
            VBUF = bs.readBytes(v_num*40)

            i_num = bs.readInt() + bs.readInt()
            IBUF = bs.readBytes(i_num*6)
                
            rapi.rpgBindPositionBuffer(VBUF, noesis.RPGEODATA_FLOAT, 40)
            rapi.rpgBindUV1BufferOfs(VBUF, noesis.RPGEODATA_FLOAT, 40, 12)
            rapi.rpgCommitTriangles(IBUF, noesis.RPGEODATA_SHORT, len(IBUF)//2, noesis.RPGEO_TRIANGLE)
            
            '''
            name_tx = bs.readBytes(bs.readInt())
            bs.seek(24,1)
            mat44 = NoeMat44.fromBytes(bs.readBytes(64))
            '''
        
        print(label, curPos)
        bs.seek(curPos + size)
    
    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
        print('File dont have mesh!')
    
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 90 -180")
    return 1