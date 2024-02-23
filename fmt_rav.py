#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("FIFA 2001 (PC)", ".rav")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def CheckType(data):
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    hd = bs.read('9I')
    print(hd)
    
    bs.seek(hd[2])
    for x in range(hd[1]):
        ofs = bs.readUInt()
        cpos = bs.tell()
        bs.seek(ofs)
        label = bs.readString()
        bs.seek(cpos)
        print('    ',label)
    
    bs.seek(hd[4])
    unks = bs.read('%iI'%hd[3])
    print('unks:',unks)
        
    bs.seek(hd[6])
    for x in range(hd[5]):
        vec4 = NoeVec4.fromBytes(bs.read(16))
        print('    vec4:',vec4)

    bs.seek(hd[8])
    for x in range(hd[7]):
        print('0-labelOfs;1-type?;2-ofs')
        inf = bs.read('3I')
        print(inf)
        cpos = bs.tell()
        bs.seek(inf[0])
        label = bs.readString()
        print('    ',label)
        
        if inf[1]:
            bs.seek(inf[2])
            # 0-numM?;1-mOfs;2-unkOfs3-zero;4-unkOfs;5-numSM;6-ofsSM;7,12-boundBox;13-numUnks1?;14-ofsUnks1;15-zero
            inf0 = bs.read('7I6f3I')
            print('inf0:',inf0[:7]+inf0[13:])
            
            bs.seek(inf0[2])
            u0 = bs.read('8B')
            print('u0:',u0)
            
            bs.seek(inf0[1])
            #for x in range(inf0[0]):
            #0-vnum;1-vof;2-nnum;3-nofs;4-(allVert/allUv);5-ncol?;6-colOfs;7-numUvs;8-ofsUVs
            m_inf = bs.read('9I')
            print('    m_inf:',m_inf)
            
            bs.seek(m_inf[1])
            print('        vnum:', m_inf[0],'vOfs:',m_inf[1])
            vbuf = bs.read(m_inf[0]*12)
            vbuf += b'\x00'*(m_inf[4]-m_inf[0])*12
            rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
            rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, m_inf[0], noesis.RPGEO_POINTS)
            
            bs.seek(m_inf[3])
            print('        nnum:', m_inf[2],'nOfs:',m_inf[3])
            nbuf = bs.read(m_inf[2]*12)
            
            bs.seek(m_inf[8])
            uvbufs = []
            for x in range(m_inf[7]):
                uvnum, uvOfs = bs.read('2I')
                print('        uvnum:', uvnum,'uvOfs:',uvOfs)
                uv_cpos = bs.tell()
                bs.seek(uvOfs)
                uvbuf = bs.read(uvnum*8)
                uvbufs.append(uvbuf)
                bs.seek(uv_cpos)
            
            bs.seek(inf0[14])
            unks1 = bs.read('%iH'%inf0[13])
            print('    unks1?:',unks1)
                
            bs.seek(inf0[6])
            for x in range(inf0[5]):
                #0-matId;1-inum;2-ofs;3-unk
                sm_inf = bs.read('4I')
                print('    %i infSM:'%x,sm_inf)
                
                sm_cpos = bs.tell()
                bs.seek(sm_inf[2])
                ibuf=bs.read(sm_inf[1]*2)
                #rapi.rpgSetName('mesh_%i'%x)
                #rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, sm_inf[1], noesis.RPGEO_TRIANGLE)
                bs.seek(sm_cpos)

        bs.seek(cpos)

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdlList.append(mdl)
    return 1