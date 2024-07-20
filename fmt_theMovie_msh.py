#by Durik256
from inc_noesis import *
import math

def registerNoesisTypes():
    handle = noesis.register("The Movie", ".msh")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1

def noepyCheckType(data):

    return 1   
	
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    tx_dir = os.path.normpath(os.path.join(os.path.dirname(rapi.getInputName()),'..','textures'))

    h = bs.read('6I')
    
    if h[5]:
        bs.seek(36)
    
    n_txs = []
    for x in range(h[1]):
        n_tx = bs.read(32).replace(b'\x00', b'').decode()
        n_txs.append(n_tx)
       
    matList = []
    for x in range(h[2]):
        u = bs.read('24B')
        try:
            tx = os.path.join(tx_dir, n_txs[u[0]])
        except:
            tx = ''
        matList.append(NoeMaterial('mat_%i'%x, tx))
        
    h0 = bs.read('I12f')[0]
    for x in range(h0):
        # 0-u; 1-tnum; 2-vnum
        mh = bs.read('4I17f')
        
        ibuf=bs.read(mh[1]*6)
        bs.seek(myCeil(len(ibuf))-len(ibuf),1)
        vbuf=bs.read(mh[2]*16)
        
        rapi.rpgSetMaterial('mat_%i'%mh[0])
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_USHORT, 16)
        rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_USHORT, 16, 12)
        rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_USHORT,mh[1]*3,noesis.RPGEO_TRIANGLE)
        rapi.rpgClearBufferBinds()
 
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()

    mdl.setModelMaterials(NoeModelMaterials([], matList))
    mdlList.append(mdl)
    rapi.setPreviewOption("setAngOfs", "0 0 0")
    return 1
    
def myCeil(n):
    return int(-1 * (n/4) // 1 * -1)*4
