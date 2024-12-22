#by Durik256
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Dead Rising 4", ".mdl")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    
    #noesis.logPopup()
    return 1

def noepyCheckType(data):
    return 1
    
def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()

    bigInfo=readbig(bs)        
    bs.seek(bigInfo[0][1])
    
    names=[]
    for x in range (len(bigInfo)):
        names.append(bs.readString())
    
    bs.seek(bigInfo[getElem(names,"SceneHeader")][2])
    sh_ukn01=bs.readUInt()
    str(bs.readUInt())    
    mesh_count=bs.readUInt()
    mesh_count2=bs.readUInt()
    msh_count=bs.readUInt()
    mat_count=bs.readUInt()
    
    bs.seek(0)
    mshInfo=bigInfo
    names2=names
    geoInfo = renderStrip()

    BoneStart=[]    
    mesh_info_array2=[]
    
    Vertex32Array=[]	
    Vertex36Array=[]	
    Vertex40Array=[]	
    Vertex44Array=[]	
    Vertex48Array=[]	
    Vertex52Array=[]	
    Vertex56Array=[]
    
    BNArr = []
    for i in range(len(names2)):
        vertex_count = []

        fullName = names2[i]

        parts = fullName.split(" ")

        baseName = parts[0]
        compName = parts[1] if len(parts) > 1 else ""
        
        bs.seek(mshInfo[i][2])
        
        if fullName == "_ANIMLIB_SKELETON_":
            BoneDataArray = []
            BonePos=bs.tell()
            BoneStart.append(BonePos)
            print("Skeleton Start @ ", bs.tell())
            
            file_version=bs.readUInt()
            bone_count=bs.readUInt()
            bone_flag=bs.readUShort()
            bone_flag2=bs.readUShort()    
            null01=bs.readUShort()
            null02=bs.readUShort()
            null2=bs.readUInt()
            
            print ("This is Null01: ",null01)    
            boneNames=[]
            boneMat=[]
            boneIdx=[]
            
            for i in range(bone_count):
                mat = NoeQuat.fromBytes(bs.read(16)).transpose().toMat43()
                mat[3] = NoeVec3.fromBytes(bs.read(16))
                
                pA=bs.readUShort()
                pB=bs.readUShort()
                
                boneMat.append(mat)
                
            for i in range(bone_count):
                boneIdx.append(bs.readUByte())
                
            print("BoneNames Start @ ", bs.tell())
            
            for i in range(13):
                bs.seek(24, 1)
                
            if null01:
                for i in range(bone_count):
                    boneNames.append(bs.readstring())
            else:
                for i in range(bone_count):
                    boneNames.append(str(i))
                    
            for i in range(bone_count):
                BNArr.append(NoeBone(i,boneNames[i],boneMat[i],None,boneIdx[i]))
            
        elif fullName == "Combined_IBHeader":
            print ("FaceBuff Start @ ", bs.tell())
            ukn=bs.readUInt()
            null=bs.readUInt()
            ffff=bs.readUInt()		
            face_count=bs.readUInt()
            ukn01=bs.readUInt()
            ukn02=bs.readUInt()
            total_face=bs.readUInt()
            ukn02=bs.readUInt()
            
        elif fullName == "Combined_VBHeader":
            print ("VertInfo Start @ ", bs.tell())	
            for i in range(msh_count):
                ukn=bs.readUInt()
                null=bs.readUInt()
                ffff=bs.readUInt()	
                vertex_count.append(bs.readUInt())
                vertex_size=bs.readUInt()
                ukn02=bs.readUInt()
            print ("VertInfo End @ ", bs.tell())
            
        elif compName == "MaskRenderStrip":
            print ("RenderStrip @ ", bs.tell())
            geoInfo.count=bs.readUInt();print(geoInfo.count)
            geoInfo.count2=bs.readUInt();print(geoInfo.count2)
            geoInfo.mesh_id=bs.readUInt();print(geoInfo.mesh_id)
            bs.seek(0x3,1)	
            geoInfo.unk00=bs.readUByte();print(geoInfo.unk00)	
            bs.seek(0x3,1)		
            geoInfo.unk01=bs.readUByte();print(geoInfo.unk01)
            geoInfo.type=bs.readUInt();print(geoInfo.type)
            geoInfo.BoneCount=bs.readUInt();print(geoInfo.BoneCount)
            geoInfo.unk=bs.readUInt();print(geoInfo.unk)
            geoInfo.UsedBones=bs.readUInt();print(geoInfo.UsedBones)
            
        elif compName == "CommandBuffer":
            print ("Geo CommandBuffer @ ", bs.tell())
            Id=bs.readUInt()

            bs.seek(0x34,1)
            checkbyte = bs.readUShort()
            
            while checkbyte != 37:
                PosB=bs.tell()
                bs.readUByte()
                bs.seek(PosB)	
                
                checkbyte = bs.readUShort()
            
            if checkbyte==37:
                bs.seek(-0x2,1)	
                VertId=bs.readUShort()
                print("This is Check Short: ", VertId)		
                VertSize=bs.readUByte()
                Null=bs.readUByte()	
                VertOff=bs.readUInt()
                bs.readUInt()
                FaceOff=bs.readUInt()
                VertAdd=bs.readUInt()
                bs.seek(0x8,1)
                    
                VertCount=bs.readUInt()
                FaceOff2=bs.readUInt()
                FaceCount=bs.readUInt()	
                UvMap=bs.readUInt()	
                mesh_info_array2.append(mesh_info(VertSize, VertCount, VertOff, FaceOff, FaceCount, UvMap, VertAdd))
                
    ShOpaqueComBuffArray=[]	
    try:
        bs.seek(bigInfo[getElem(names,"SharedOpaqueCommandBuffer")][2])
        PosBuff=bs.tell()
        ShOpaqueComBuffArray.append(PosBuff)
    except:
        print("There's no SharedOpaqueCommandBuffer!\n")

    print("This is --- ShOpaqueComBuffArray --- ", len(ShOpaqueComBuffArray))
    
    mesh_info_array=[]
    if ShOpaqueComBuffArray:
        bs.seek(bigInfo[getElem(names,"SharedZPassCommandBuffer")][2])	
        print ("SharedZPassCommandBuffer @ ", bs.tell())
        ShaderPos=bs.tell()	
        bs.seek(bigInfo[getElem(names,"SharedOpaqueCommandBuffer")][2])
        print ("SharedOpaqueCommandBuffer @ ", bs.tell())

        mesh_info_array1=[]	
        while bs.tell() < ShaderPos:	
            checkbyte = bs.readUShort()
            while checkbyte != 37:
                PosB=bs.tell()
                bs.readUByte()
                bs.seek(PosB)
                checkbyte = bs.readUShort()
            	
            if checkbyte==37:
                print ("!!!!!!!!!!!!!!!!!!!!!!!!!!@ ", bs.tell())	
                bs.seek(-0x2,1)
                VertId=bs.readUShort()
                print ("This is Check Short: ",VertId)		
                VertSize=bs.readUByte()
                Null=bs.readUByte()	
                VertOff=bs.readUInt()
                bs.seek(0x14,1)
                    
                VertCount=bs.readUInt()
                FaceOff=bs.readUInt()
                FaceCount=bs.readUInt()
                UvMap=1	
                mesh_info_array1.append(mesh_info(VertSize, VertCount, VertOff, FaceOff, FaceCount, UvMap, None))


        print ("SharedZPassCommandBuffer End@ ", bs.tell())
        mesh_info_array = mesh_info_array1 + mesh_info_array2

    if not ShOpaqueComBuffArray: 
        mesh_info_array = mesh_info_array2
        
    print(mesh_info_array)
    for i in range(len(mesh_info_array)):
        if mesh_info_array[i].VertSize==32: Vertex32Array.append(mesh_info_array[i])	
        if mesh_info_array[i].VertSize==36: Vertex36Array.append(mesh_info_array[i])	
        if mesh_info_array[i].VertSize==40: Vertex40Array.append(mesh_info_array[i])	
        if mesh_info_array[i].VertSize==44: Vertex44Array.append(mesh_info_array[i])	
        if mesh_info_array[i].VertSize==48: Vertex48Array.append(mesh_info_array[i])	
        if mesh_info_array[i].VertSize==52: Vertex52Array.append(mesh_info_array[i])		
        if mesh_info_array[i].VertSize==56: Vertex56Array.append(mesh_info_array[i])			

    Vertices32=(getElem(names,"Combined Vertices 32"))
    print('Combined Vertices 32::',Vertices32)
    
    Vertices36=(getElem(names,"Combined Vertices 36"))
    print('Combined Vertices 36::',Vertices36)
    
    Vertices40=(getElem(names,"Combined Vertices 40"))
    print('Combined Vertices 40::',Vertices40)
    if Vertices40:
        for i in range(len(Vertex40Array)):
            FacesOff=((bigInfo[getElem(names,"Combined Indices 2")][2])+(Vertex40Array[i].FaceOff*2))
            bs.seek(FacesOff)
            ibuf = bs.read(Vertex40Array[i].FaceCount*2)
            VertexCount = sorted(list(noeUnpack('%iH' % (len(ibuf) // 2), ibuf)))[-1] + 1
            print('VertexCount:',VertexCount)
            
            VertOff40=(bigInfo[getElem(names,"Combined Vertices 40")][2]+(Vertex40Array[i].VertOff*40))		
            bs.seek(VertOff40)
            vbuf = bs.read(VertexCount*40)
            
            rapi.rpgSetBoneMap([i+geoInfo.type for i in range(len(BNArr))])
            rapi.rpgSetName('mesh_%i'%VertOff40)
            rapi.rpgBindPositionBuffer(vbuf,noesis.RPGEODATA_FLOAT,40)
            rapi.rpgBindUV1BufferOfs(vbuf,noesis.RPGEODATA_USHORT,40,12)
            rapi.rpgBindBoneWeightBufferOfs(vbuf, noesis.RPGEODATA_UBYTE, 40, 16, 4)
            rapi.rpgBindBoneIndexBufferOfs(vbuf, noesis.RPGEODATA_UBYTE, 40, 20, 4)
            rapi.rpgCommitTriangles(ibuf,noesis.RPGEODATA_USHORT,len(ibuf)//2,noesis.RPGEO_TRIANGLE)
            rapi.rpgClearBufferBinds()
    
    Vertices44=(getElem(names,"Combined Vertices 44"))
    print('Combined Vertices 44::',Vertices44)
    
    Vertices48=(getElem(names,"Combined Vertices 48"))
    print('Combined Vertices 48::',Vertices48)
    
    Vertices52=(getElem(names,"Combined Vertices 52"))
    print('Combined Vertices 52::',Vertices52)
    
    Vertices56=(getElem(names,"Combined Vertices 56"))
    print('Combined Vertices 56::',Vertices56)
    

    if(BNArr):
        BNArr = rapi.multiplyBones(BNArr)
    
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel(meshes)

    mdl.setBones(BNArr)
    mdlList.append(mdl)
    return 1

def getElem(arr,e):
    try:
        return arr.index(e)
    except ValueError:
        return None

class mesh_info:
    def __init__(self, VertSize, VertCount, VertOff, FaceOff, FaceCount, UvMap, VertAdd):
        self.VertSize = VertSize
        self.VertCount = VertCount
        self.VertOff = VertOff
        self.FaceOff = FaceOff
        self.FaceCount = FaceCount
        self.UvMap = UvMap
        self.VertAdd = VertAdd
    
class renderStrip:
    def __init__(self):
        self.count = []
        self.count2 = []
        self.mesh_id = []
        self.unk00 = []
        self.unk01 = []
        self.type = []
        self.BoneCount = []
        self.unk = []
        self.unk = []
    
def readbig(bs):
    startpos = bs.tell()
    _ = bs.read('6I') #unk01; unk02; fsize; files; unk04; names_offset

    info_array = []
    for i in range(_[3]):
        _ = bs.read('7I') #name_offset; unk05; zsize; size; offset; file_type; zip_flag;
        info_array.append([_[5], _[0]+startpos, _[4]+startpos, _[3]])

    return info_array
        