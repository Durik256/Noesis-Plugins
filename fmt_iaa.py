#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Esel Studio", ".iaa_mesh")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    #noesis.logPopup()
    return 1

def noepyCheckType(data):
    return 1

split_sm = True

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    num_mesh = bs.readUInt()
    for mi in range(num_mesh):
        print(mi,'>>>>>>>>>>>>>>>>')
        cpos = bs.tell()
        u0,u1,msize,u2,u3,numSM = bs.read('HHIHHI')
        print(u0,u1,msize,u2,u3,numSM)
        sm = []
        for x in range(numSM):
            iofs,inum = bs.read('2I')
            sm.append([iofs,inum])
            print(x,'iofs:',iofs,'inum:',inum)
         
        vnum, vsize = bs.read('2I')
        stride = vsize//vnum
        print('vnum:',vnum,'vsize:',vsize,'stride:',stride,'vbuf_start:', bs.tell())
        vbuf = bs.read(vsize)
        inum, itype, isize = bs.read('3I')
        print('inum:',inum,'itype:',itype,'isize:',isize, 'ibuf_start:', bs.tell())
        ibuf_ofs = bs.tell()
        ibuf = bs.read(isize)
        bs.seek(ibuf_ofs + (int(-1 * (isize/4) // 1 * -1)*4))
        print('end_ibuf:',bs.tell())
        num_attr = bs.readUInt()
        
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, stride)
        
        for x in range(num_attr):
            # 0-type(1-vert/5-norm/33-uv); 1-fmt(28-3f/27-2f); 2-ofs; 3-stride
            a = bs.read('4I')
            print('    ',a)
            
            if a[0] == 1:
                #rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, stride)
                pass
            elif a[0] == 5:
                rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, a[2])
            elif a[0] == 33:
                rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, a[2])
        num_attr = bs.readUInt()
        print('end_mesh:',bs.tell())
        
        if split_sm:
            for i,x in enumerate(sm):
                iofs,inum = x
                rapi.rpgSetName('mesh_%i_%i'%(mi,i))
                if itype == 3:
                    bs.seek(ibuf_ofs + iofs*2)
                    ibuf = bs.read(inum*2)
                    rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_USHORT,inum,noesis.RPGEO_TRIANGLE)
                elif itype == 2:
                    bs.seek(ibuf_ofs + iofs)
                    ibuf = bs.read(inum)
                    rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_UBYTE,inum,noesis.RPGEO_TRIANGLE)
        else:
            rapi.rpgSetName('mesh_%i'%mi)
            if itype == 3:
                rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_USHORT,inum,noesis.RPGEO_TRIANGLE)
            elif itype == 2:
                rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_UBYTE,inum,noesis.RPGEO_TRIANGLE)
        rapi.rpgClearBufferBinds()
        bs.seek(cpos+msize)
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default','')]))
    mdlList.append(mdl)
    return 1
