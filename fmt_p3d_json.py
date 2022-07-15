#by Durik256 19.03.2022 for xentax
from inc_noesis import *
import json
import base64

def registerNoesisTypes():
    handle = noesis.register("Ragnarok Web",".json")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1
    
def CheckType(data):
    if data.decode()[0] != '{':
        return 0
    return 1

def LoadModel(data, mdlList):
    data = data.decode()
    file = json.loads(data)

    ctx = rapi.rpgCreateContext()
    
    materials = []
    print("num_object:",len(file))
    
    for x0 in file:#>>object
        print("object:",x0)
        type = file[x0]['type']
        name = file[x0]['name']
        print(' >type:',type,'\n >name:',name)
        
        if type == 0:#>>mesh and skeleton
            #>>skeleton
            try:
                skin = file[x0]['skin']
                print(' >numBone:' ,len(skin))
                bones = []
                for i,bone in enumerate(skin):
                    parent = skin[bone]['p']
                    smat = skin[bone]['s']
                    smat = NoeMat44([NoeVec4(smat[x:x+4]) for x in range(0,len(smat),4)]).toMat43()
                    mat = skin[bone]['m']
                    mat = NoeMat44([NoeVec4(mat[x:x+4]) for x in range(0,len(mat),4)]).toMat43()
                    bones.append(NoeBone(i, bone, smat.inverse(), parent))
            except:
                print(" >dont have skin!")
            #>>mesh
            print(">>>>>>>>",file[x0]['meshes']['$def']['surfaces'])
            try:
                mesh = file[x0]['meshes']['$def']
                surfaces = mesh['surfaces']
                icount = surfaces[0]['icount']
                ibegin = surfaces[0]['ibegin']
                print(' >numSubmesh:',len(surfaces),'icount:',icount,'ibegin:',ibegin)
                ibuf = base64.b64decode(mesh['index'].encode(encoding = 'UTF-8'))
                vcount = mesh['numVertices']
                attrib, vbuf = list(mesh['attrib'].items())[0]
                print(' >attrib:[',attrib,']')
                stride, info, size = calcStride(attrib)
                print(' >vcount:',vcount,'stride:',stride,'attrib:',info)
                vbuf = base64.b64decode(vbuf.encode(encoding = 'UTF-8'))
                #print(mesh['matrix'])#not always
                fixBoneMap = []
                try:
                    renderedBone = mesh['renderedBoneArray']
                    boneMap = [GetBoneID(bones, b) for b in renderedBone]
                    fixBoneMap = [0]*(len(boneMap)*3)
                    for idx,b in enumerate(boneMap): fixBoneMap[idx*3] = b
                    print(' >boneMap:',boneMap)
                    print(' >renderedBone:',renderedBone)
                except:
                    print(" >dont have renderedBone!")
                #always null
                #mesh['renderedBoneArray']['SparseAssociative']
                
                rapi.rpgSetName(name)
                file_name = rapi.getLocalFileName(rapi.getInputName()).replace('.p3d','').replace('.json','')
                
                mat_name = file_name+'_'+name if file_name != name else name
                materials.append(NoeMaterial(mat_name,""))
                rapi.rpgSetMaterial(mat_name)
                rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, stride)
                
                off = 12
                if info[1]:
                    #rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, off)
                    off += size[1]
                if info[2]:
                    rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, off)
                    off += size[2]
                if info[3]:
                    rapi.rpgBindUV2BufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, off)
                    off += size[3]
                if info[4]:
                    rapi.rpgBindBoneIndexBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, off, 4)
                    off += size[4]
                if info[5]:
                    rapi.rpgBindBoneWeightBufferOfs(vbuf, noesis.RPGEODATA_FLOAT, stride, off, 4)
                    off += size[4]
                if fixBoneMap: rapi.rpgSetBoneMap(fixBoneMap)
                rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_SHORT, icount, noesis.RPGEO_TRIANGLE)
                rapi.rpgClearBufferBinds()
            except:
                print(" >dont have mesh [$def]!")
        elif type == 1:
            length = file[x0]['length']
            tracks_bones = file[x0]['tracks']
            print(' >length:',length)
            print(' >tracks_bones:',len(tracks_bones))
            #for x2 in tracks_bones:
                #frm = base64.b64decode(tracks_bones[x2].encode(encoding = 'UTF-8'))
                #frm_bs = NoeBitStream(frm)
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
        print("Empty model, dont have mesh!")
    try:
        mdl.setBones(bones)
    except:
        print("Dont have bones!")
    mdl.setModelMaterials(NoeModelMaterials([], materials))
    mdlList.append(mdl)

    rapi.setPreviewOption("setAngOfs", "0 -90 0")
    return 1

def calcStride(vstr):
    #vstr = searchString(bs)
    label = ['Position','Normal','Texcoord1', 'Texcoord2', 'BoneIndex','BoneWeight']
    info, size = [0,0,0,0,0,0], [12,12,8,8,16,16]
    size[3] = UV(vstr)
    stride = 0
    for i,x in enumerate(label):
        if x in vstr:
            info[i] = 1
            stride += size[i]
    return stride, info, size

def UV(attrib):
    attrib = attrib.split('/')
    i = -8
    for x in attrib:
        if 'Texcoord' in x:
            i += 8
    return i

def GetBoneID(bones, name):
    if not name: return -1
    for i, bone in enumerate(bones):
        if name == bone.name:
            return i