#by Durik256
from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("twelvesky", ".mesh")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadModel(handle, noepyLoadModel)
	#noesis.logPopup()
	return 1

def noepyCheckType(data):
    return 1
    
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()

    while bs.tell() < bs.getSize():
        if bs.tell() + 12 >= bs.getSize():
            break
        
        unks = bs.read('3I')
        print('unks:', unks)
        if not unks[0] and not unks[1] and not unks[2]:
            break
        if not unks[2]:
            bs.seek(368,1)
            numLOD = bs.readInt()
            print('numLOD:', numLOD)
            for x in range(numLOD):
                print('    LOD:', x)
                vnum = bs.readInt()
                print('        vnum:', vnum, "[%i]"%bs.tell())
                vbuf = bs.read(vnum*76)

                inum = bs.readInt()
                print('        inum:', inum, "[%i]"%bs.tell())
                ibuf = bs.read(inum*6)

                bs.seek(32*vnum+inum*6+inum*6,1)
                print('        end:', bs.tell())

                if (x == 0):# only firs LOD
                    name = 'mesh_%i'%bs.tell()
                    rapi.rpgSetName(name)
                    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 76)
                    rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, 76, 68)
                    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum*3, noesis.RPGEO_TRIANGLE)
        else:
            bs.seek(unks[2],1)

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default','')]))
    mdlList.append(mdl)
    return 1
