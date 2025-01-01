#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Scooby Doo! & Looney Tunes Cartoon", ".data")
    noesis.setHandlerExtractArc(handle, Extract)
    return 1
  
def noepyCheckType(data):
    return 1
  
def Extract(fileName, fileLen, justChecking):
    if fileLen < 16:
        return 0
        
    if justChecking: #it's valid
            return 1
    
    data = rapi.loadIntoByteArray(fileName)
    bs = NoeBitStream(data)
    
    h = bs.read('8I')
    print('h:',h) # 3-num; 4-strOfs; 5-infOfs(24b); 6-ofsOfs(8b); 7-dataOfs
    
    strings = []
    bs.seek(h[4])
    for x in bs.read('%iI'%h[3]):
        bs.seek(x)
        strings.append(bs.readString())
        
    bs.seek(h[5])
    infs = []
    for x in range(h[3]):
        infs.append(bs.read('3Q'))

    bs.seek(h[6])
    ofs = []
    for x in range(h[3]):
        ofs.append(bs.read('Q')[0])

    
    for i in range(h[3]):
        print(strings[i],ofs[i],infs[i][1:])
        bs.seek(ofs[i])
        export_data = rapi.decompInflate(bs.read(infs[i][1]), infs[i][2], -15)
        rapi.exportArchiveFile(strings[i], export_data)
        
    print("Complete", h[3], "Files")
    return 1
