#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Monsters vs Aliens", ".pak")
    noesis.setHandlerExtractArc(handle, Extract)
    return 1
    
def Extract(fileName, fileLen, justChecking):
    if fileLen < 16:
        return 0
        
    if justChecking: #it's valid
            return 1
    
    data = rapi.loadIntoByteArray(fileName)
    bs = NoeBitStream(data)

    result = [i for i in findall(b'\x26\x00\x00\x00\x01\x00\x01\x00', data)]
    
    for x in result:
        bs.seek(x+8)

        h = bs.read('10I')
        name = bs.read(64).rstrip(b'\x00').decode()
        unk = list(bs.read('4I'))
        
        
        if unk[0] == 405:
            unk[0] = 'dds'
            exportData = bs.read(unk[2]-4)
        else:
            if unk[0] == 805:
                unk[0] = '_mesh'
            elif unk[0] == 1201:
                unk[0] = '_anim'
            elif unk[0] == 1025:
                unk[0] = '_audio'
            
            bs.seek(x)
            exportData = bs.read(h[0]+12)

        name = name+'.'+str(unk[0])
        rapi.exportArchiveFile(name, exportData)
        print(name)

    print("Complete", len(result), "Files!")
    return 1

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)
