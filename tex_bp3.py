#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("GOS2", ".bp3")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    noesis.setHandlerWriteRGBA(handle, WriteRGBA)
    #noesis.logPopup()
    return 1

def CheckType(data):
    bs = NoeBitStream(data)
    if bs.readBytes(4) != b'\x88\x88\x88\x88':
        return 0
    return 1
    
def LoadRGBA(data, texList):
    bs = NoeBitStream(data)
    bs.seek(4)
    
    width = bs.readInt()
    height = bs.readInt()
    sizeBMP = bs.readInt()
    bs.seek(26)

    sizeHeader = bs.readInt()
    bs.seek(16)
    bmpHeader = bs.readBytes(sizeHeader)

    wt = calc(width, 8)
    ht = calc(height, 8)
    
    Size = ht * wt // 64
    
    lpMem = [bs.readUByte() for x in range(Size)]
    #print('>>>>>>>>>>>>>>>>>>>',set(lpMem))
    cmMem = [bs.readUByte() for x in range(Size*3)]
    
    pixelData = [255]*Size*192
    
    for i in range(Size):
        chunkY = 8
        if (8 * (i // (wt // 8)) + 8 >= height):
            chunkY = height + 8 - ht

        chunkX = 8;
        if (8 * (i % (wt // 8)) + 8 >= width):
            chunkX = width + 8 - wt
            
        v17 = lpMem[i]
        
        if v17 == 1:
            bitCount = 8
        elif v17 == 2:
            bitCount = 8
        elif v17 == 3:
            bitCount = 8
        elif v17 == 4:
            bitCount = 4
        elif v17 == 5:
            bitCount = 8
        elif v17 == 6:
            bitCount = 16
        elif v17 == 7:
            bitCount = 24
        else:
            bitCount = 0

        v24 = bitCount * chunkX // 8
        chunkPixel = b''
        if (bitCount > 0):
            curPos = bs.getOffset()
            for cY in range(chunkY):
                chunkPixel += bs.readBytes((bitCount * chunkX) // 8)
                chunkPixel += b'\xFF'* (bitCount - (bitCount * chunkX) // 8)
            chunkPixel += b'\xFF'* ((bitCount * 8) - (len(chunkPixel)))
            bs.seek(curPos + (bitCount*chunkX*chunkY)//8)
        
        v20 = 3 * wt
        v23 = 3 * wt * 8 * (i // (wt // 8))
        v51 = 24 * (i % (wt // 8))
        v61 = bitCount // 8
        v26 = 0
        for e in range(8):
            v48 = v51 + v23
            v56 = v26
            r,g,b = 0,0,0
            for m in range(8):
                if lpMem[i] == 0:
                    b = cmMem[3 * i]
                    g = cmMem[3 * i + 1]
                    r = cmMem[3 * i + 2]
                elif lpMem[i] == 1:
                    b = (chunkPixel[v56] & 7) + cmMem[3 * i]
                    g = ((chunkPixel[v56] >> 3) & 7) + cmMem[3 * i + 1]
                    r = ((chunkPixel[v56] >> 6) & 3) + cmMem[3 * i + 2]
                elif lpMem[i] == 2:
                    b = (chunkPixel[v56] & 3) + cmMem[3 * i]
                    g = ((chunkPixel[v56] >> 2) & 7) + cmMem[3 * i + 1]
                    r = ((chunkPixel[v56] >> 5) & 7) + cmMem[3 * i + 2]
                elif lpMem[i] == 3:
                    b = (chunkPixel[v56] & 7) + cmMem[3 * i]
                    g = ((chunkPixel[v56] >> 3) & 3) + cmMem[3 * i + 1]
                    r = ((chunkPixel[v56] >> 5) & 7) + cmMem[3 * i + 2]
                elif lpMem[i] == 4:
                    if (m % 2 > 0):
                        b = ((chunkPixel[v56] >> 4) & 0xF) + cmMem[3 * i]
                        g = ((chunkPixel[v56] >> 4) & 0xF) + cmMem[3 * i + 1]
                        r = ((chunkPixel[v56] >> 4) & 0xF) + cmMem[3 * i + 2]
                    else:
                        b = (chunkPixel[v56] & 0xF) + cmMem[3 * i]
                        g = (chunkPixel[v56] & 0xF) + cmMem[3 * i + 1]
                        r = (chunkPixel[v56] & 0xF) + cmMem[3 * i + 2]
                elif lpMem[i] == 5:
                    b = chunkPixel[v56];
                    g = chunkPixel[v56];
                    r = chunkPixel[v56];
                elif lpMem[i] == 6:
                    b = ((chunkPixel[v56] & 0x1F) + cmMem[3 * i])
                    g = (((chunkPixel[v56] & 0xE0) >> 5) + 8 * (chunkPixel[v56 + 1] & 3) + cmMem[3 * i + 1])
                    r = (((chunkPixel[v56 + 1] & 0x7C) >> 2) + cmMem[3 * i + 2])
                elif lpMem[i] == 7:
                    r = chunkPixel[v56 + 2]
                    g = chunkPixel[v56 + 1]
                    b = chunkPixel[v56]
                    
                pixelData[v48] = r&0xFF
                pixelData[v48 + 1] = g&0xFF
                pixelData[v48 + 2] = b&0xFF

                v56 += v61
                v48 += 3

            v26 += bitCount
            v23 += v20
    
    pixelData = bytes(pixelData)
    
    v20 = 3 * wt
    data = b''
    ElementSizea = calc(3 * width, 4) - 3 * width
    for n in range(height):
        data += pixelData[v20 * n:(v20 * n) + 3 * width]
    
    data = rapi.imageDecodeRaw(data, width, height, 'r8g8b8')
    data = rapi.imageFlipRGBA32(data, width, height, 0, 1)
    texList.append(NoeTexture('tx', width, height, data, noesis.NOESISTEX_RGBA32))
    return 1

def WriteRGBA(data, w, h, bw):
    data = rapi.imageFlipRGBA32(data, w, h, 0, 1)
    data = rapi.imageEncodeRaw(data, w, h, 'b8g8r8')
    inFile = NoeBitStream(data)

    #HEADER BP3
    bw.writeBytes(b'\x88'*4)#bpType
    bw.writeInt(w)#bpWidth
    bw.writeInt(h)#bpHeight
    bw.writeInt(len(data))#bpSize

    #HEADER BMP
    bw.writeBytes(b'BM')#bmType
    bw.writeInt(len(data))#bmSize
    bw.writeBytes(b'\x00'*4)#bmReserved1/2
    bw.writeInt(54)#bmOffBits
    bw.writeInt(40)#bmSize
    bw.writeInt(w)#bmWidth
    bw.writeInt(h)#bmHeight
    bw.writeShort(1)#bmPlanes
    bw.writeShort(24)#bmBitCount
    bw.writeInt(0)#bmCompression
    bw.writeInt(0)#bmSizeImage
    bw.writeInt(2834)#bmXPelsPerMeter
    bw.writeInt(2834)#bmYPelsPerMeter
    bw.writeInt(0)#bmClrUsed
    bw.writeInt(0)#bmClrImportant

    #INFO BP3
    wt = calc(w, 8)
    ht = calc(h, 8)
    Size = ht * wt // 64

    bw.writeBytes(b'\x07'*Size)#CompressType
    bw.writeBytes(b'\x00'*Size*3)#forCompress
    
    #DATA BP3
    pixelData = b''
    
    v12 = 3 * wt;
    v14 = wt // 8;
    
    v8 = calc(3 * w, 4)
    for i in range(h):
        pixelData += inFile.readBytes(v8)
        pixelData += b'\x00' *(v12-v8)
    
    for j in range(Size):
        if (8*(j//(wt//8))+8>=h):
            v34 = h + 8 - ht
        else:
            v34 = 8

        if (8*(j%(wt//8))+8>=w):
            v36 = w + 8 - wt
        else:
            v36 = 8

        v13 = v12*8*(j//v14)
        v37 = 24*(j%v14)
        v41 = b''
        for k in range(8):
            v35 = v37 + v13;
            
            for m in range(8):
                if (k<v34 and m<v36):
                    v41 += pixelData[v35:v35+3]

                v35 += 3
            v13 += v12
        bw.writeBytes(v41)

    return 1  
    
def calc(a1, a2):
    if ( a1 % a2 ):
        return a2 + a1 - a1 % a2
    else:
        return a1
