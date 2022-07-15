#by Durik256 for xentax
from inc_noesis import *
import math

def registerNoesisTypes():
    handle = noesis.register("Aerial Strike: The Yager Missions", ".ylm")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    if data[:3] != b'YLM':
        return 0
    return 1   
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    rapi.rpgSetMaterial('mat_0')

    bs.seek(4)#YML
    
    file_size, unk, num_file = bs.readInt(), bs.readInt(), bs.readInt()

    bs.seek(4, 1)#MAP
    
    (size, unk, unk, x_terrain, y_terrain, x_chunk, y_chunk, uvXY, height) = [bs.readInt() for x in range(9)]

    bs.seek((x_terrain*y_terrain)*4, 1)
    
    start_chunk = bs.getOffset() + (x_terrain*y_terrain)*4 + 4
    
    for yT in range(y_terrain):
        for xT in range(x_terrain):

            offset, curPos = bs.readInt(), bs.getOffset()
            if offset != -1:
                bs.seek(offset + start_chunk)
                raw_vert = []#17x17
                for y in range(17):
                    raw_vert.append([VD(bs) for x in range(17)])

                rapi.rpgSetName('chunk_%d_%d' % (xT, yT))
                for y in range(16):
                    for x in range(16):
                        quad(raw_vert, 1, x, y, xT*16, yT*16)
                
                bs.seek(curPos)
    
    bs.seek(start_chunk - 4)
    num_chunk = bs.readInt()
    bs.seek(start_chunk + (num_chunk * 1156))
    print(bs.getOffset())
    

    bs.seek(4, 1)#NRML
    n_size, n_num = bs.readInt(), bs.readInt()
    bs.seek(n_num*12, 1)
        
    bs.seek(4, 1)#TEX
    tx_size, tx_num = bs.readInt(), bs.readInt()
    for x in range(tx_num):
        tx_name = searchString(bs)

    #----find texture----
    tx_dir = os.path.abspath(os.path.join(rapi.getDirForFilePath(rapi.getInputName()), '../texture/'))
    
    for file in os.listdir(tx_dir):
        if tx_name in file:
            tx_name = os.path.join(tx_dir,file)
            break
    #--------------------
    
    #rapi.rpgOptimize()
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('mat_0',tx_name)]))
    mdlList.append(mdl)
    return 1
    
def quad(raw_vert, size, x, y, offX, offY):
    R, G, B, A = raw_vert[y][x].get()
    
    B = hex(B).replace("0x","")
    B, rot = int(B[-1], 16), int(B[0], 16) if len(B)>1 else 0
    
    ibuf = struct.pack('6H', *[0, 2, 1, 2, 3, 1])
    vbuf = struct.pack('12f', *[0+x+offX, R, 0+y+offY, size+x+offX, raw_vert[y][x+1].R, 0+y+offY, 0+x+offX, raw_vert[y+1][x].R, size+y+offY, size+x+offX, raw_vert[y+1][x+1].R, size+y+offY])
    
    uv1X, uv1Y = ((B*64)/1024), ((G*8)/2048)
    uv2X, uv2Y = (((B+1)*64)/1024), (((G+8)*8)/2048)
    
    if rot == 0:#default
        uvbuf = struct.pack('8f', *[uv1X, uv2Y, uv2X, uv2Y, uv1X, uv1Y, uv2X, uv1Y])
    elif rot == 2:#flip_Y
        uvbuf = struct.pack('8f', *[uv1X, uv1Y, uv2X, uv1Y, uv1X, uv2Y, uv2X, uv2Y])
    elif rot == 4:#flip_X
        uvbuf = struct.pack('8f', *[uv2X, uv2Y, uv1X, uv2Y, uv2X, uv1Y, uv1X, uv1Y])
    elif rot == 6:#rot -> 180
        uvbuf = struct.pack('8f', *[uv2X, uv1Y, uv1X, uv1Y, uv2X, uv2Y, uv1X, uv2Y])
    elif rot == 8:#rot -> 90
        uvbuf = struct.pack('8f', *[uv2X, uv2Y, uv2X, uv1Y, uv1X, uv2Y, uv1X, uv1Y])
    elif rot == 10:#rot <- 90 and flip_Y
        uvbuf = struct.pack('8f', *[uv2X, uv1Y, uv2X, uv2Y, uv1X, uv1Y, uv1X, uv2Y])
    elif rot == 12:#rot -> 90 and flip_Y
        uvbuf = struct.pack('8f', *[uv1X, uv2Y, uv1X, uv1Y, uv2X, uv2Y, uv2X, uv1Y])
    elif rot == 14:#rot <- 90
        uvbuf = struct.pack('8f', *[uv1X, uv1Y, uv1X, uv2Y, uv2X, uv1Y, uv2X, uv2Y])
    

    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
    rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 8)
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, 6, noesis.RPGEO_TRIANGLE)
    return 1

def searchString(bs):
    bytes = []
    byte = None
    while byte != 0:
        byte = bs.readUByte()
        bytes.append(byte)
    return noeAsciiFromBytes(bytes)

class VD:
    def __init__(self, bs):
        self.R = bs.readUByte()
        self.G = bs.readUByte()
        self.B = bs.readUByte()
        self.A = bs.readUByte()
        
        self.calc()
        
    def calc(self):
        mul = 0
        if self.G % 8 != 0:
            mul = abs(self.G//8*8-self.G)
            self.G -= mul
        
        self.R = self.R/6 + ((255/6)*mul)
    
    def get(self):
        return [self.R, self.G, self.B, self.A]
    
    def __repr__(self):
        return "(VD:" + " R:" + repr(self.R) + " G:" + repr(self.G) + " B:" + repr(self.B) + " A:" + repr(self.A) + ")"