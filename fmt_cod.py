#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Screamer 4x4", ".cod")
    noesis.setHandlerExtractArc(handle, ExtractARC)
    return 1
    
def ExtractARC(fileName, fileLen, justChecking):
    if fileLen < 16:
        return 0
        
    if justChecking: #it's valid
        return 1

    with open(fileName ,'rb') as f:
        f.seek(24)# - Header (->Unique Pc HUNGARY<-)
        num = noeUnpack('I', f.read(4))[0]//136

        for x in range(num):
            name = f.read(128).split(b'\x00')[0].decode('ascii', errors='ignore')
            ofs, size = noeUnpack('2I', f.read(8))
        
            cpos = f.tell()
            f.seek(ofs)
            data = f.read(size)
            rapi.exportArchiveFile(name, data)
            print(name)
            f.seek(cpos)

    print("Extracting all files.", num)
    return 1
    

    

        
        
        