#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Winter X-Games: Snocross", ".UIMG")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    return 1

def CheckType(data):
    return 1
    
def LoadRGBA(data, texList):
    bs = NoeBitStream(data)
    w, h, type = bs.read('3I')
    data = data[12:]
    
    if type == 25:
        fmt = 'b5g5r5p1'
    if type == 21:
        fmt = 'b8g8r8p8'
    
    data = rapi.imageDecodeRaw(data, w, h, fmt)
    texList.append(NoeTexture(rapi.getInputName(), w, h, data, noesis.NOESISTEX_RGBA32))    
    return 1
    
#script for qbms for unpack *.IMG, (save as *.bms)
'''
# by Durik256
# Game: Winter X-Games: Snocross
# fmt: *.IMG
# script for QuickBMS http://quickbms.aluigi.org

print "by Durik256"
idstring "IMG "
get NAME filename
comtype TDCB_lzw15v
log MEMORY_FILE 0 0

goto 0x4
get CHUNK_OFS long
get WIDTH long
get HEIGHT long
get PIX_TYPE long

goto CHUNK_OFS
get NUM_MIP long
get CHUNKNAME longlong
get CHUNK_SIZE long

get ZSIZE long
set SIZE long = 0
math SIZE = ZSIZE
math SIZE *= 20
string NAME += ".UIMG"
savepos OFFSET

clog MEMORY_FILE OFFSET ZSIZE SIZE

put WIDTH long MEMORY_FILE
put HEIGHT long MEMORY_FILE
put PIX_TYPE long MEMORY_FILE

get OUT_SIZE asize MEMORY_FILE
log NAME 0 OUT_SIZE MEMORY_FILE
'''