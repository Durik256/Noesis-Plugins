#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Ridge Racer Slipstream ", ".SCX")
    noesis.setHandlerExtractArc(handle, Extract)
    return 1

def Extract(fileName, fileLen, justChecking):
    if justChecking: #it's valid
        return 1

    export_data = b''
    with open(fileName, "rb") as f:
        f.seek(4) # TEPK
        num = noeUnpack('I', f.read(4))[0]
        print('num:',num)

        for x in range(num):
            offset, decSize, comSize = noeUnpack('3I', f.read(12))
            print(offset,decSize,comSize)
            cpos = f.tell()
            
            f.seek(offset)
            data = f.read(comSize)
            export_data += rapi.decompInflate(data, decSize)
            f.seek(cpos)

    name = os.path.splitext(os.path.basename(rapi.getInputName()))[0] + '.invo'
    rapi.exportArchiveFile(name, export_data)
    print("Export ", name)
    return 1