#by Durik256 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("barbie DP (PC)",".hnk")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    bs = NoeBitStream(data)
    if bs.readInt() != 592:
        return 0
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    rapi.rpgSetEndian(1)
    fsize = bs.getSize()
    
    ibuf, vbuf, names = [], [], []
    #114-end_Block;2-unk;28-unk;29-vbuf;30-ibuf;112-header;113-name;4101-anim;4123-mdl_info;4432-mat?;8529-tx
    while bs.getOffset() < fsize:
        size, type, unk = bs.readInt(), bs.readShort(), bs.readShort()
        curPos = bs.getOffset()
        print(size, type, 'offset:',curPos)
        if type == 4123:
            bs.seek(5,1)
            cmat = bs.readByte()
            print('>>>count_submesh:',cmat)
            #bs.seek(16,1);vbuf_count=bs.readShort();ibuf_count=bs.readShort()
            #bs.seek(138+(68*cmat),1)
            #---
            bs.seek(138,1)
            id = []
            for x in range(cmat):
                bs.seek(51,1)
                id.append(bs.readByte())
                bs.seek(16,1)
            print('>>>id:',id)
            #---
            bs.setEndian(1)
            #print([bs.readInt() for x in range((cmat*20)//4)])
            submesh = []
            for x in range(cmat):
                bs.readInt()#4
                submesh.append([bs.readInt() for i in range(4)])
            if bs.readInt() == 4:
                #submesh[-1] = [bs.readInt() for i in range(4)]
                submesh.append([bs.readInt() for i in range(4)])
                id.append(id[-1])
            print('>>>submesh_info:',submesh)
            #print([bs.readInt() for i in range(5)])
            bs.setEndian(0)
            bs.seek(curPos+size)
        elif type == 29:
            print('vbuf>>>>>>>>>>>+++')
            vbuf.append(bs.readBytes(size))
        elif type == 30:
            print('ibuf>>>>>>>>>>>+++')
            ibuf.append(bs.readBytes(size))
        elif type == 4432:
            bs.seek(40,1)
            names.append(noeAsciiFromBytes(bs.readBytes(32)))
            bs.seek(curPos+size)
        else:
            bs.seek(size,1)
    
    if len(vbuf)>0 and len(vbuf)==len(ibuf):
        stride, materials = [], []
        for x in range(len(vbuf)):
            vcount = 0
            for q in range(len(submesh)):#cmat
                if x == id[q]: #vcount+= submesh[q][2]
                    vcount = submesh[q][1]+submesh[q][2] if submesh[q][1]+submesh[q][2]>vcount else vcount
            stride.append(len(vbuf[x])//vcount)
        print('>>>stride:', stride, '>>>vcount:', vcount)
        for x in range(len(submesh)):#cmat
            msh_name = names[x] if len(names)>=x+1 else 'mesh_'+str(x)
            materials.append(NoeMaterial(msh_name,''))
            print(msh_name)
            
            _vbuf = vbuf[id[x]][submesh[x][1]*stride[id[x]]:(submesh[x][1]*stride[id[x]])+(submesh[x][2]*stride[id[x]])]
            
            rapi.rpgSetName(msh_name)
            rapi.rpgBindPositionBuffer(_vbuf, noesis.RPGEODATA_FLOAT, stride[id[x]])
            rapi.rpgBindUV1BufferOfs(_vbuf, noesis.RPGEODATA_FLOAT, stride[id[x]], 44 if stride[id[x]]==72 else 28) 
            rapi.rpgCommitTriangles(ibuf[id[x]][submesh[x][0]*2:submesh[x][0]*2+submesh[x][3]*2], noesis.RPGEODATA_SHORT, submesh[x][3], noesis.RPGEO_TRIANGLE)

    try:
        mdl = rapi.rpgConstructModel()
        mdl.setModelMaterials(NoeModelMaterials([], materials))
    except:
        mdl = NoeModel()
        
    mdlList.append(mdl)
    return 1