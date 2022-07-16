#by Durik256 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("GUILTY GEAR 2 OVERTURE", ".pkm")
    noesis.setHandlerExtractArc(handle, ExtractPKM)
    return 1
    
def ExtractPKM(fileName, fileLen, justChecking):
    if fileLen < 16:
        return 0
        
    if justChecking: #it's valid
        return 1
    
    data = rapi.loadIntoByteArray(fileName)
    result = [(i+4) for i in findall(b'FORM', data)]
    print(result)
    
    if not result:
        print('This [*.PKM] dont have mesh [*.AFB]!')
        return 0
    
    
    fs = NoeBitStream(data)
    
    for x in result:
        fs.seek(x)
        size = fs.readInt()
        fs.seek(-8,1)
        
        export_data = fs.readBytes(size)
        rapi.exportArchiveFile('form_%i.AFB'%x, export_data)
        print('export form_%i.AFB'%x)

    print("Extracting", len(result), "files.")
    return 1

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)