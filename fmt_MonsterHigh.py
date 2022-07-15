#by Durik256 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Monster High Wii",".hnk")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    bs = NoeBitStream(data)
    if bs.readInt() != 592:
        return 0
    return 1

def LoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    rapi.rpgSetEndian(1)
    bs = NoeBitStream(data)

    fsize = bs.getSize()
    while bs.getOffset() < fsize:
        size, type, unk = bs.readInt(), bs.readShort(), bs.readShort()
        offset = bs.getOffset()
        
        if type == 4144: 
            submesh = []
            print('>>>>>>>>>>>>>>>>>>>>>Model_Info')
            bs.seek(4,1)
            
            bs.setEndian(1)
            #0-group; 9?
            info = [bs.readShort() for x in range(10)]
            #print('info:', info)
            
            bs.setEndian(0)
            off = [bs.readInt() for x in range(13)]
            #print('offset:', off)
            
            name = noeAsciiFromBytes(bs.readBytes(72)).replace('\x00', ' ')
            rapi.rpgSetName(name+str(bs.getOffset()))
            print('name:', name)
            
            for x in range(info[0]):
                # 88 bytes
                bs.seek(44,1)
                v_start = bs.readUInt24()
                bs.seek(5,1)
                v_end = bs.readUInt24()
                bs.seek(1,1)
                uv_start = bs.readUInt24()
                bs.seek(5,1)
                stride = bs.readUByte()
                bs.seek(23,1)
                submesh.append([v_start, v_end, uv_start, stride])
                print('v_start:', v_start, 'v_end:', v_end, 'stride:',stride)
            
            bs.setEndian(1)
            for x in range(info[0]):
                #1-size_block;3-face_count
                face_info = [bs.readInt() for x in range(6)]
                submesh[x] += [face_info[1], face_info[3]]
                print('face_block:', face_info[1], 'face_count:', face_info[3])
            
            bs.setEndian(0)
            bs.seek(offset+size)
        
        elif type == 8241: 
            print('>>>>>>>>>>>>>>>>>>>>>Face_buffer')
            curPos = bs.getOffset()
            
            ibufs = []
            for x in submesh:
                ibufs.append(bs.readBytes(x[4]))
            
            bs.seek(offset+size)
        
        elif type == 8242: 
            print('>>>>>>>>>>>>>>>>>>>>>Vert_buffer')
            curPos = bs.getOffset()
            
            for i,x in enumerate(submesh):
                bs.seek(curPos+x[0])
                vbuf = bs.readBytes(x[1] - x[0])
                
                next = submesh[i+1][0] if len(submesh) > i+1 else size
                vcount, uvcount = (x[1]-x[0])//x[3], (next-x[2])//4
                print('vcount:',vcount, 'uvcount:',uvcount, 'face_count', x[-1])

                #rapi.rpgSetName("Mesh_"+str(x[0]))
                #rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, x[3])
                #rapi.rpgCommitTriangles(None, noesis.RPGEODATA_SHORT, len(vbuf)//x[3], noesis.RPGEO_POINTS)
                rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, x[3])
                
                i_bs = NoeBitStream(ibufs[i])
                i_bs.setEndian(1)
                while i_bs.readUByte() == 152:#98
                    ibuf = b''

                    for y in range(i_bs.readUShort()):
                        if vcount > 255:
                            ibuf += (i_bs.readUShort()).to_bytes(2, 'big')
                            t = 2
                        else:
                            ibuf += (i_bs.readUByte()).to_bytes(2, 'big')
                            t = 1

                        i_bs.seek(((1 if info[7] > 0 else 0)+1)*t,1)
                        if uvcount > 255:
                            i_bs.seek(2,1)
                        else:
                            i_bs.seek(1,1)
                    
                    
                    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_SHORT, len(ibuf)//2, noesis.RPGEO_TRIANGLE_STRIP)
            
            bs.seek(offset+size)
        else:
            bs.seek(size,1)
        print(size, type, 'offset:', offset)

    try:
        #rapi.rpgOptimize()
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    mdlList.append(mdl)
    return 1