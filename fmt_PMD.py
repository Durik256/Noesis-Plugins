#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Ace Combat X: Skies of Deception",".PMD")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadSkeleton)	
    return 1
    
def CheckType(data):
    if data[:4] != b'PMD.':
        return 0
    return 1

def LoadSkeleton(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    bs.seek(9)
    num = bs.readUShort()
    bs.seek(32)
    #0-nameOfs;1-matxOfs;2-unk(-1);3-meshOfs;4-unkOfs;5,6,7-zero;
    inf = bs.read('8i')
    print('num:',num,'inf:',inf)
    
    bones = []
    bs.seek(inf[0])
    for x in range(num):
        parent = bs.readByte()#?
        name = noeStrFromBytes(bs.read(11))
        bones.append(NoeBone(x, name, NoeMat43(), None, parent))
    
    bs.seek(inf[1])
    for x in range(num):
        matL = NoeMat44.fromBytes(bs.read(64)).toMat43()
        matW = NoeMat44.fromBytes(bs.read(64)).toMat43()
        bones[x].setMatrix(matL)

    
    bs.seek(inf[3])
    
    #for x in range(num):#20
    while bs.tell() < bs.getSize(): 
        curPos = bs.tell()
        #0-magic;1-sizeHead;2-SizeBlock;3,4-unk,5-vnum(Not),6-unk
        minf = bs.read('3I3H2B')
        if minf[0] != 931:
            break
        
        stride = bs.read('8B')[-1]
        print('minf:',minf,'stride:',stride)
        bs.seek(4,1)#zero
        unks = bs.read('%iH'%((minf[1]-32)//2))#minf[3]*minf[4]// minf[4]*2
        #print('unks:',unks, sum(unks))


        rapi.rpgSetName('mesh_%i'%bs.tell())
        for x in range(0,len(unks),2):
            poly, num = unks[x],unks[x+1]
            #summ += poly*num
            
            for x in range(num):
                vbuf = bs.read(poly*stride)
                rapi.rpgBindPositionBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, 16)
                rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, 4)
                rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, poly, noesis.RPGEO_TRIANGLE_STRIP)
        bs.seek(curPos+minf[2])
    print(bs.tell())
    
    bones = rapi.multiplyBones(bones)
    
    rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default','')]))
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1