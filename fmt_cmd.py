#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Racing Game 3D [PSP]", ".cmd")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1

def noepyCheckType(data):

    return 1   
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    bs.read(4)#cmd 
    _ = bs.read('2I2H4I')#0-u0; 1-zero; 2-u_count1?; 3-u_count2?;  4-u_ofs; 5-mtrx_ofs; 6-msh_ofs; 7-eof
    
    #?
    #bs.seek(_[4])
    #for x in range(_[2]):
    #    bs.read('8I')
    #
    
    bs.seek(_[5])

    #_[1] - msh count?
    #for x in range(_[1]):
    mtrx = bs.read(48)
    m_indx = bs.readUShort()
    bs.seek(10,1)
    m_ofs = bs.readUInt()
    #    m_inf.append()
    
    #for x in range(m_inf):
    bs.seek(m_ofs)
    sm_inf = bs.read('12I') #0-block_size; 1-vnum; 2,3-zero; 4-uv_num; 5-polygon_num; 6-u0; 7-u1; 8,9,10,11-zero

    vbuf = bs.read(sm_inf[1]*16)
    uvbuf_size = sm_inf[4]*8
    uvbuf = bs.read(uvbuf_size)
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 16)
    
    bs.seek(align16(uvbuf_size)-uvbuf_size,1)

    for x in range(sm_inf[5]):
        _ = bs.read('16H') #0-zero; 1-num_index; index -> [0-uv_index; 1-v_index]
        print(_)

        ibuf = b'' 
        for i in range(_[1]): 
            ibuf += noePack('H', _[3+i*2])
            
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, len(ibuf)//2, noesis.RPGEO_TRIANGLE_STRIP)

    mdl = rapi.rpgConstructModel()
    mdlList.append(mdl)
    return 1
    
def align16(value):
    return (value + 15) & ~15
