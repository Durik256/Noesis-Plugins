#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Unreal Engine", ".tfc")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def CheckType(data):
    return 1
    
res = [256, 512, 1024, 2048]#128, 
    
def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    result = [i for i in findall(b'\xC1\x83\x2A\x9E', data)]
    
    for i in result:
        bs.seek(i)
        #0-magic; 1-chunkSize; 2-zipSize; 3-Size
        hd = bs.read('4I')
        if hd[3] < 32768:#8192
            continue
        
        fmt, w, h = getRes1(hd[3])
        print(hd, 'res:', [w, h])
        
        c = []
        t = 0
        while t != hd[2]:
            c.append(bs.read('2I'))
            t += c[-1][0]
            print('    ',c[-1])
            
        pix = b''
        for x in c:
            data = bs.read(x[0])
            pix += rapi.decompLZO(data, x[1])

        data = rapi.imageDecodeDXT(pix, w, h, fmt) 
        texList.append(NoeTexture('tx_%i'%len(texList), w, h, data, noesis.NOESISTEX_RGBA32))
    return 1

def getRes1(fsize):
    for x in range(len(res)):
        if fsize == (res[x]*res[x]//2):
            return [noesis.NOESISTEX_DXT1, res[x], res[x]]
    return getRes2(fsize)#[4, 4]
    
def getRes2(fsize):
    for x in range(len(res)):
        if fsize == (res[x]*res[x]):
            return [noesis.NOESISTEX_DXT5, res[x], res[x]]
    return getRes3(fsize)
    
def getRes3(fsize):
    for x in range(1, len(res)):
        w, h = res[x], res[x]//2
        if fsize == (w*h//2):
            return [noesis.NOESISTEX_DXT1, w, h]
    return getRes4(fsize)
    
def getRes4(fsize):
    for x in range(1, len(res)):
        w, h = res[x], res[x]//2
        if fsize == (w*h):
            return [noesis.NOESISTEX_DXT5, w, h]
    return [0, 4, 4]

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)
