#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Ace Racer [lzma]", ".4") #Messiah Engine
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    return 1

def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    basename = os.path.splitext(os.path.basename(rapi.getInputName()))[0]
    
    # ... 5-ASTC_type?; 6-numChunk;
    h = bs.read('12B')
    gWidth, gHeight = bs.read('2H')
    bs.seek(16,1)#zero
    
    fSize = bs.readUInt()
    unk = bs.readUShort() # ASTC_type?
    numChunk = bs.readUShort()
    
    '''
    DKDave — Yesterday, at 23:49
    Some more info on the image types from the .4 file header: 0x24 = ASTC 4x4, 0x26 = ASTC 5x5, 0x28 = ASTC 6x6, 0x2B = ASTC 8x8
    '''
    ASTC_type = {0x24:[4,4,1,1],0x26:[5,5,1,1],0x28:[6,6,1,1],0x2B:[8,8,1,1]}
    blockvwidth, blockvheight, block_depth, depth = ASTC_type.get(h[5], [8,8,1,1])

    for x in range(numChunk):
        cpos = bs.tell()
        # 0-blockSize; 1-width; 2-height; 3-unk; decSize;
        _ = bs.read('IHHII')
        label = bs.read(4)
        
        if label == b'NNNN':
            pass
        elif label == b'LZMA':
            decSize = bs.readUInt()
            data = bs.readBytes(_[0]-24)
            data = rapi.decompLZMA(data[5:], decSize, data[:5])
            data = rapi.imageDecodeASTC(data, blockvwidth, blockvheight, block_depth, _[1], _[2], depth)
            texList.append(NoeTexture(basename+str(x), _[1], _[2], data, noesis.NOESISTEX_RGBA32))            
        bs.seek(cpos+_[0])
    return 1
