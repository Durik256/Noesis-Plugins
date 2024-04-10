#by Durik256
from inc_noesis import *
import csv
import io

def registerNoesisTypes():
    handle = noesis.register("PIX CSV", ".csv")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def CheckType(data):
    return 1

def LoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    data = io.StringIO(data.decode('utf-8'))
    reader = csv.reader(data)
    p, n, u, vX, vY, vZ, nX, nY, nZ, tU, tV = parse_header(next(reader))
    if not p:
        return 0

    vbuf, nbuf, uvbuf = b'', b'', b''
    for row in reader:
        vbuf += noePack('3f', float(row[vX]), float(row[vY]), float(row[vZ]))
        if n:
            nbuf += noePack('3f', float(row[nX]), float(row[nY]), float(row[nZ]))
        if u:
            uvbuf += noePack('2f', float(row[tU]), float(row[tV]))

    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
    if n:
        rapi.rpgBindNormalBuffer(nbuf, noesis.RPGEODATA_FLOAT, 12)
    if u:
        rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 8)
    rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, len(vbuf)//12, noesis.RPGEO_TRIANGLE)

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    mdlList.append(mdl)
    return 1

def parse_header(header):
    vX, vY, vZ, nX, nY, nZ, tU, tV = [-1]*8
    for i,line in enumerate(header):
        line = line.strip()
        if line.startswith('in_POSITION0'):
            if line.endswith('.x'):
                vX = i
            elif line.endswith('.y'):
                vY = i
            elif line.endswith('.z'):
                vZ = i
        elif line.startswith('in_NORMAL0'):
            if line.endswith('.x'):
                nX = i
            elif line.endswith('.y'):
                nY = i
            elif line.endswith('.z'):
                nZ = i
        elif line.startswith('in_TEXCOORD0'):
            if line.endswith('.x'):
                tU = i
            elif line.endswith('.y'):
                tV = i
    p = True
    if -1 in [vX, vY, vZ]:
        p = False
    n = True
    if -1 in [nX, nY, nZ]:
        n = False
    u = True
    if -1 in [tU, tV]:
        u = False
    return [p, n, u, vX, vY, vZ, nX, nY, nZ, tU, tV]