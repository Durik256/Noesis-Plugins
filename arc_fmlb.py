#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("3d looney tunes dash", ".fmlb")# as unpacker
    noesis.setHandlerExtractArc(handle, Extract)
    return 1
    
def Extract(fileName, fileLen, justChecking):
    if fileLen < 16:
        return 0

    if justChecking: #it's valid
        return 1

    bs = NoeBitStream(rapi.loadIntoByteArray(fileName))
    bs.seek(4)#_FML

    h = bs.read('6I')
    print(h)
    
    bs.seek(4,1)#END>
    bs.seek(16,1)#zero
    
    
    for x in range(h[3]):
        fh = bs.read('3I')
        name = bs.read(64).split(b'\x00')[0].decode()
        inf = bs.read('=2I2H')

        cpos = bs.tell()
        bs.seek(inf[0]+h[4])
        data = bs.read(inf[1])
        rapi.exportArchiveFile(name+'.'+str(fh[0]), data)
        print(name)
        bs.seek(cpos)

    print("Complete")
    return 1