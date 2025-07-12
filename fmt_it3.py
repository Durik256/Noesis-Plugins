#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("unk_game", ".it3")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)

    noesis.logPopup()
    return 1

def noepyCheckType(data):
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()

    readChunk(bs, bs.getSize())

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdlList.append(mdl)
    return 1

def readFixedString(bs, i):
    return bs.read(i).rstrip(b'\x00').decode('ascii', 'ignore')

def printWithIndent(indent, value):
    print('    '*indent, value)

def readChunk(bs, eof, indent=0):

    while bs.tell() < eof:
        label = bs.read(4)
        size = bs.readUInt()
        cpos = bs.tell()
        print('    '*indent, label, cpos, size)
        
        if label == b'INFO':
            name = readFixedString(bs, 64)
            printWithIndent(indent+1, name)
            mat = NoeMat44.fromBytes(bs.read(64)).toMat43()
            unk = NoeVec3.fromBytes(bs.read(12))

        if label == b'INFZ':
            _ = bs.read('4I')
            printWithIndent(indent+1, _)
        
        elif label == b'LIG3':
            _ = bs.read('=4fB5f')
            printWithIndent(indent+1, _)
        
        elif label == b'CHID':
            name = readFixedString(bs, 64)
            printWithIndent(indent+1, name)
            for x in range(bs.readUInt()):
                name = readFixedString(bs, 64)
                printWithIndent(indent+2, name)
        
        elif label == b'TEX2':
            name = bs.read(bs.readUInt())

            if bs.read(4) == b'\x49\x54\x50\xFF':
                readChunk(bs, cpos + size, indent+1)
            
        
        bs.seek(cpos + size)