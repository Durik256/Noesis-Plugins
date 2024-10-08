#by Durik256
from inc_noesis import *
import os
import zlib

extract_ORIG = False

def registerNoesisTypes():
    handle = noesis.register("Crash Bandicoot Nitro Kart 3D", ".vfs;.zlib;.plzp;.lang") #CBNK2 (iOS)
    noesis.setHandlerExtractArc(handle, Extract)
    return 1
    
def Extract(fileName, fileLen, justChecking):
    if fileLen < 16:
        return 0

    if justChecking: #it's valid
        return 1

    name, ext = os.path.splitext(fileName)
    with open(fileName, 'rb') as f:
        if ext.lower() == '.zlib':
            exportZLIB(os.path.basename(name), f.read())
        
        elif ext.lower() == '.plzp':
            exportPLZP(os.path.basename(name), f.read())
        
        elif ext.lower() == '.lang':
            exportLANG(f.read())
        
        elif ext.lower() == '.vfs':
            magic = f.read(4)
            u0, numFile = noeUnpack('2I', f.read(8))
            for x in range(numFile):
                ofs, h, size = noeUnpack('3I', f.read(12))
                cpos = f.tell()
                f.seek(ofs)
                data = f.read(size)
                name = str(hex(h)).replace('0x', '')
                _ext = getEXT(data[:4]).lower()

                if extract_ORIG:
                    rapi.exportArchiveFile(name+_ext, data)
                else:
                    tryExport(name, _ext, data)
                    
                print(name)
                f.seek(cpos)

    print("Complete")
    return 1
    
def tryExport(name, _ext, data):
    if _ext == '.plzp':
        exportPLZP(name, data)
    elif _ext == '.zlib':
        exportZLIB(name, data)
    elif _ext == '.lang':
        exportLANG(data)
    else:
        rapi.exportArchiveFile(name+_ext, data)
    
def getEXT(magic):
    if magic == b'\x89PNG':
        return '.png'
    elif magic == b'PLZP':
        return '.plzp'
    elif magic == b'LANG':
        return '.lang'
    elif magic == b'PIFF':
        return '.vram'
    elif magic == b'RIFF':
        return '.wav'
    elif magic == b'PFNT':
        return '.pfnt'
    elif magic == b'ID3\x03':
        return '.mp3'
    elif magic == b'FORM':
        return '.form'
    elif magic == b'\x34\x00\x00\x00':
        return '.pvr'
    elif magic == b'\x4D\x3C\x2B\x1A':
        return '.sggr'
    elif magic == b'<!--':
        return '.xml'
    elif magic == b'PSND':
        return '.psnd'
    elif magic[:1] == b'\x78':
        return '.zlib'
    elif magic[:1] == b'3C':
        return '.xml'
    elif magic[:1] == b'0D' and magic[1:2] == b'0A':
        return '.xml'
    else:
        return '.dat'

def exportZLIB(name, data):
    data = zlib.decompress(data)
    tryExport(name, getEXT(data[:4]), data)

def exportPLZP(name, data):
    bs = NoeBitStream(data)
    magic, destSize, comSize = bs.read('3I')
    data = zlib.decompress(bs.read(comSize))
    tryExport(name, getEXT(data[:4]), data)

def exportLANG(data):
    bs = NoeBitStream(data)
    magic, numFile, u0, u1, lenS = bs.read('5I')
    _data = bs.read(lenS)
    if _data[lenS-2:] != b'\x00\x00':
        names = [x.decode('ascii', errors='ignore') for x in _data.split(b'\x00')]
    else:
        names = [x.replace(b'\x00', b'').decode('ascii', errors='ignore') for x in _data.split(b'\x00\x00')]
    print(names)
    for x in range(numFile):
        inf = bs.read('4I')
        cpos = bs.tell()
        bs.seek(inf[0])
        data = zlib.decompress(bs.read(inf[2]))
        rapi.exportArchiveFile(names[x]+'.text', data)
        bs.seek(cpos)
