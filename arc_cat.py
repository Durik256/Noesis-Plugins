#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Ikki Tousen - Xross Impact", ".cat")
    noesis.setHandlerExtractArc(handle, Extract)
    return 1

def Extract(fileName, fileLen, justChecking):
    if justChecking: #it's valid
        return 1

    bs = NoeBitStream(rapi.loadIntoByteArray(fileName))
    ofs = []
    while bs.tell() < bs.getSize():
        _ = bs.readUInt()
        if _ == 4294967295: # -1
            break
        ofs.append(_)
    
    if ofs:
        ofs.append(bs.getSize())
    
    print('ofs:', ofs)

    for x in range(len(ofs)-1):
        bs.seek(ofs[x])
        export_data = bs.read(ofs[x+1]-ofs[x])
        name = 'file_%i.'%(x) + getExt(export_data[:3])
        print(name)
        rapi.exportArchiveFile(name, export_data)
    print("Complete ")
    return 1

def getExt(byte_string):
    if b'\x00' in byte_string:
        return 'dat'

    for byte in byte_string:
        if not (65 <= byte <= 90 or 97 <= byte <= 122):
            return 'dat'

    try:
        return byte_string.decode('utf-8')[::-1]
    except UnicodeDecodeError:
        return 'dat'