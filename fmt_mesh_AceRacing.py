#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Ace Racing", ".mesh")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    return 1

def noepyCheckType(data):
    if data[:8] != b'.MESSIAH':  # Modified to check the first 8 bytes
        return 0
    return 1   

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()

    bs.seek(18, 1)
    numSM, vnum, inum = bs.read('=H2I')
    if bs.readUByte():
        bs.seek(-1,1)

    a = []
    for _ in range(4):
        str_len = bs.readUShort()
        str_data = bs.readBytes(str_len).decode()# Changed to readBytes
        a.append(parseA(str_data))
    
    bs.seek(40, 1)
    sm = [bs.read('4I') for x in range(numSM)]

    if vnum > 65535:
        ibuf = bs.readBytes(inum*4)  # Changed to readBytes
        ifmt = noesis.RPGEODATA_UINT
    else:
        ibuf = bs.readBytes(inum*2)  # Changed to readBytes
        ifmt = noesis.RPGEODATA_USHORT

    u = 0
    for _ in a:
        buf = bs.readBytes(_[0]*vnum)  # Changed to readBytes
        if _[1]:
            rapi.rpgBindPositionBufferOfs(buf, _[1][1], _[0], _[1][0])
        for x in _[2]:
            rapi.rpgBindUV1BufferOfs(buf, x[1], _[0], x[0])  # Corrected to rpgBindUV1BufferOfs
            u += 1

    rapi.rpgCommitTriangles(ibuf, ifmt, inum, noesis.RPGEO_TRIANGLE)
    
    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    mdl = rapi.rpgConstructModel()
    mdlList.append(mdl)
    return 1

def parseA(a):
    ts = {'B':[1,8],'H':[2,5],'F':[4,0] }
    st = [0,[],[]]
    if a != 'None':
        s = a.split('_')
        if s[0] != "Compressed":
            for _ in s:
                f,c,t = _[0], int(_[1]), _[2]
                if f == 'P':
                    st[1] = [st[0],ts[t][1]]
                elif f == 'T':
                    st[2].append([st[0],ts[t][1]])
                st[0] += ts[t][0]*c
        else:
            for _ in s[1:]:
                if _ == 'P':
                    st[1] = [st[0],ts['F'][1]]
                    st[0] += 12
                elif _ == 'C':
                    st[0] += 4
                elif _ == 'N':
                    st[0] += 4
                elif _ == 'TB':
                    st[0] += 8
                elif _[0] == 'U' and _[1] == 'V':
                    for __ in range(int(_[2:])):
                        st[2].append([st[0],ts['H'][1]])
                        st[0] += 4
    return st
