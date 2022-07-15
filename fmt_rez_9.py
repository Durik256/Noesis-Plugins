#by Durik256 for xentax.com
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Winter X-Games: Snocross", ".rez")
    noesis.setHandlerExtractArc(handle, spExtractArc)
    return 1

def spExtractArc(fileName, fileLen, justChecking):
    if fileLen < 16:
        return 0
        
    if justChecking: #it's valid
            return 1

    f = open(fileName, "rb")
    data = NoeFileStream(f)

    count, unk, offset = data.readInt(), data.readInt(), data.readInt()
    data.seek(offset)
    
    items = []#name, offset
    for x in range(count):
        name = noeAsciiFromBytes(data.readBytes(32))
        #type 3-GRP; 2-M3D; 1-IMG
        type, indx = data.readShort(), data.readShort()
        off, size = data.readInt(), data.readInt()
        items.append([name, off])
    
    for x in range(count):
        if x+1 < count:
            size = items[x+1][1]-items[x][1]-8
        else:
            size = offset-items[x][1]-8
            
        data.seek(items[x][1])
        name = items[x][0]+'.'+noeAsciiFromBytes(data.readBytes(4))[:-1]
        data.seek(4,1)#size

        export_data = data.readBytes(size)
        rapi.exportArchiveFile(name, export_data)
        print("export", name)

    print("Extracting", count, "files.")
    return 1