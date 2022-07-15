#Driver SF .sp extraction
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Driver SF Archive", ".sp")
    noesis.setHandlerExtractArc(handle, spExtractArc)
    return 1

def spExtractArc(fileName, fileLen, justChecking):
    if fileLen < 16:
        return 0
        
    if justChecking: #it's valid
            return 1
    
    name = []
    
    f = open(fileName, "rb")
    byteStream = f.read()
    data = NoeFileStream(f)
    offsetVEHC = [i+4 for i in findall(b'VEHC', byteStream)]
    offsetVSCT = [i+4 for i in findall(b'VSCT', byteStream)]
    byteStream = None

    for offset in offsetVSCT:
        data.seek(offset, NOESEEK_ABS)
        if data.readUShort() == 1:
            numcar = data.readUShort()

            for i in range(numcar):
                s = str(data.readUShort())+"_"
                data.seek(4, NOESEEK_REL)
                s += noeAsciiFromBytes(data.readBytes(16))
                data.seek(6, NOESEEK_REL)
                name.append(s)
    
    for n in range(0,len(name),3):
        name[n] += "_LOD2_5.VEHC"
        name[n+1] += "_cockpit.VEHC"
        name[n+2] += "_LOD1.VEHC"
        
    for i,offset in enumerate(offsetVEHC):
        data.seek(offset, NOESEEK_ABS)
        offset_car = data.readUInt()
        data.seek(4, NOESEEK_REL)
        size_car = data.readUInt()
        data.seek(offset_car, NOESEEK_ABS)
        export_data = data.readBytes(size_car)
        rapi.exportArchiveFile(name[i], export_data)
        print("export", name[i] )

    print("Extracting", len(offsetVEHC), "files.")
    return 1

def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)