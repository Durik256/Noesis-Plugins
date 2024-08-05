#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("NHL 21 (PS4)", ".skel")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1

def noepyCheckType(data):
    if data[:4] != b'RSF\x00':
        return 0
    return 1   

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(32)
    
    global bones
    bones = []
    
    readNode(bs)
    
    mdl = NoeModel()
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1
        
def readNode(bs, parent=None):
    global bones
    
    label = bs.read(bs.readUInt()+1)
    print(label)
    unk = bs.readUInt()#4
    name = bs.read(bs.readUInt()).decode()
    print(name)
    flag = bs.read('6B')[-1]
    print('flag:',flag)

    if flag:
        unk = bs.readUInt()#2
        numItem = bs.readUInt()
        for x in range(numItem):
            unk = bs.readUInt()#30259
            unk = bs.readUInt()#1
            item_label = bs.read(bs.readUInt()+1)
            item = NoeVec3.fromBytes(bs.read(12))

    unk = bs.readUInt()#2
    unk = bs.readUByte()#1
    
    world_mat = NoeMat43()
    
    if label.startswith(b'SGNodeGroup'):
        pass

    elif label.startswith(b'SGNodeLocator'):
        unk = bs.readUInt()#1
        unk_vec = NoeVec3.fromBytes(bs.read(12))
    
    elif label.startswith(b'SGNodeTransform'):
        unk = bs.readUInt()#1
        world_mat = NoeMat44.fromBytes(bs.read(64)).toMat43()
    
    elif label.startswith(b'SGNodeJoint'):
        unk = bs.readUInt()#1
        local_mat = NoeMat44.fromBytes(bs.read(64)).toMat43()
        unk = bs.readUInt()#2
        unk_mat = NoeMat44.fromBytes(bs.read(64)).toMat43()
        world_mat = NoeMat44.fromBytes(bs.read(64)).toMat43()
        unk_mat = NoeMat44.fromBytes(bs.read(64)).toMat43()
        unk = bs.readUInt()#0
    
    numChild = bs.readUInt()
    bones.append(NoeBone(len(bones), name, world_mat, parent))
    
    for x in range(numChild):
        readNode(bs, name)