#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Unreal Engine", ".tfc")
    noesis.setHandlerExtractArc(handle, Extract)
    return 1
	
res = [128, 256, 512, 1024, 2048]#
DDS_HEADER = [b'\x44\x44\x53\x20\x7C\x00\x00\x00\x07\x10\x00\x00', b'\x00\x80\x00\x00\x00\x00\x00\x00\x01', b'\x20\x00\x00\x00\x04\x00\x00\x00']
    
def Extract(fileName, fileLen, justChecking):
    if justChecking: #it's valid
            return 1
    
    data = rapi.loadIntoByteArray(fileName)
    bs = NoeBitStream(data)
    result = [i for i in findall(b'\xC1\x83\x2A\x9E', data)]

    counter = 0
    for i in result:
        bs.seek(i)
        #0-magic; 1-chunkSize; 2-zipSize; 3-Size
        hd = bs.read('4I')
        if hd[3] < 8192:##32768
            continue
        
        fmt, w, h = getRes1(hd[3])
        print(hd, 'res:', [w, h])
        
        c = []
        t = 0
        while t != hd[2]:
            c.append(bs.read('2I'))
            t += c[-1][0]
            print('    ',c[-1])
            
        pix = DDS_HEADER[0]+noePack('2I', w, h)+DDS_HEADER[1]+(b'\x00'*47)+DDS_HEADER[2]+fmt+(b'\x00'*40)
        for x in c:
            data = bs.read(x[0])
            pix += rapi.decompLZO(data, x[1])
 
        name = ('tx_%i'%counter) + '.dds'
        rapi.exportArchiveFile(name, pix)
        counter+=1
        print("export", name)

    print("Extracting", counter+1, "files.")
    return 1
    
def getRes1(fsize):
    for x in range(len(res)):
        if fsize == (res[x]*res[x]//2):
            return [b'DXT1', res[x], res[x]]
    return getRes2(fsize)#[4, 4]
    
def getRes2(fsize):
    for x in range(len(res)):
        if fsize == (res[x]*res[x]):
            return [b'DXT5', res[x], res[x]]
    return [b'DXT1', 4, 4]
    
def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)

#Old as plugin
'''
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
    return [0, 4, 4]

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)
'''
