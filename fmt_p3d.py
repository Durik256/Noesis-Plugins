#by Durik256 21.03.2022 for xentax
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Ragnarok Web", ".p3d")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)    
    return 1

def CheckType(data):
    return 1

def LoadModel(data, mdlList):
    data = rapi.decompInflate(data, int(len(data)*6))#decompress
    reader = amf3reader(data[4:])
    data = reader.unpack()[0]#read amf3
    ctx = rapi.rpgCreateContext()
    
    materials = []
    print("num_object:",len(data))
    
    for x0 in data:#>>object
        print("object:",x0)
        type = data[x0]['type']
        name = data[x0]['name']
        print(' >type:',type,'\n >name:',name)
        
        if type == 0:#>>mesh and skeleton
            #>>skeleton
            try:
                skin = data[x0]['skin']
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
            try:
                mesh = data[x0]['meshes']['$def']
                surfaces = mesh['surfaces']
                icount = surfaces[0]['icount']
                ibegin = surfaces[0]['ibegin']
                print(' >numSubmesh:',len(surfaces),'icount:',icount,'ibegin:',ibegin)
                ibuf = bytes(mesh['index'])
                vcount = mesh['numVertices']
                attrib, vbuf = list(mesh['attrib'].items())[0]
                print(' >attrib:[',attrib,']')
                stride, info, size = calcStride(attrib)
                print(' >vcount:',vcount,'stride:',stride,'attrib:',info)
                vbuf = bytes(vbuf)
                #print(mesh['matrix'])#not always
                fixBoneMap = []
                try:
                    renderedBone = list(mesh['renderedBoneArray'].values())
                    boneMap = [GetBoneID(bones, b) for b in renderedBone]
                    fixBoneMap = [0]*(len(boneMap)*3)
                    for idx,b in enumerate(boneMap): fixBoneMap[idx*3] = b
                    print(' >boneMap:',boneMap)
                    print(' >renderedBone:',renderedBone)
                except:
                    print(' >dont have renderedBone!')
                #always null
                #mesh['renderedBoneArray']['SparseAssociative']
                
                rapi.rpgSetName(name)
                data_name = rapi.getLocalFileName(rapi.getInputName()).replace('.p3d','')
                
                mat_name = data_name+'_'+name if data_name != name else name
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
            length = data[x0]['length']
            tracks_bones = data[x0]['tracks']
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
        pass
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
            
#=============AMF3 READER=============
#this is modified amf3reader.py script >> original script:
#https://github.com/gpeacock/telemetry-tools/blob/master/amf3reader.py
class Metric:
    pass

class amf3reader(dict):
    TYPE_UNDEFINED    = 0
    TYPE_NULL         = 1
    TYPE_BOOL_FALSE   = 2
    TYPE_BOOL_TRUE    = 3
    TYPE_INTEGER      = 4
    TYPE_NUMBER       = 5
    TYPE_STRING       = 6
    TYPE_XML          = 7
    TYPE_DATE         = 8
    TYPE_ARRAY        = 9
    TYPE_OBJECT       = 10
    TYPE_XMLSTRING    = 11
    TYPE_BYTEARRAY    = 12
    TYPE_VECTORINT    = 13
    TYPE_VECTORUINT   = 14
    TYPE_VECTORNUMBER = 15
    TYPE_VECTOROBJECT = 16
    TYPE_DICTOBJECT   = 17

    def __init__(self, data):
        self.data = NoeBitStream(data)      
        self.stringList = []
        self.traitsList = []
        self.objectsList = []
        self.format = None
        self.flash11Mode = False  
                        
    def addString(self, string):
        index = len(self.stringList)
        self.stringList.append(string)
        return index

    def addObject(self, obj):
        self.objectsList.append(obj)
        
    def getObject(self, index):
        if index < len(self.objectsList):
            obj = self.objectsList[index]
            return obj
        
    def clearObjectsList(self):
        self.objectsList = []
        
    def getString(self,index):
        string = b'unknown'
        if index < len(self.stringList):
            string = self.stringList[index]
        return string
            
    def readByte(self):
        return self.data.readUByte()
    
    def readInt(self):
        return self.data.readUInt()

    def readDouble(self):
        #return self.data.readDouble()
        return struct.unpack('>d', self.data.readBytes(8))[0]

    def readBytes(self,length):
        return self.data.readBytes(length)

    def readUint29(self):         
        byte = self.readByte()
        if byte == None: return None
        if byte < 128:
            return byte        
        ref = (byte & 0x7F) << 7
        byte = self.readByte()
        if byte == None: return None
        if byte < 128:
            return (ref | byte)
        ref = (ref | (byte & 0x7F)) << 7
        byte = self.readByte()
        if byte == None: return None
        if byte < 128:
            return (ref | byte)
        ref = (ref | (byte & 0x7F)) << 8
        byte = self.readByte()
        if byte == None: return None
        return (ref | byte)


    def readAmfString(self, stringWithoutMarker, noCache=False):
        ref = self.readUint29()
        if ref == None: return None
        if (ref & 1) == 0:
            return noeAsciiFromBytes(self.getString(ref >> 1))
        length = ref >> 1
        if length == 0: return ""
        s = self.readBytes(length)
        
        if not noCache:  # for flash11 support
            self.addString(s)
        return noeAsciiFromBytes(s)

    def readAmfObject(self) :
        encoding = self.readByte()
        if encoding == None:
            return None

        encoding = encoding & 255
        value = None

        if encoding == self.TYPE_INTEGER:
            value = self.readUint29() 
        elif encoding == self.TYPE_NUMBER:
            value = self.readDouble() 
        elif encoding == self.TYPE_STRING:
            value = self.readAmfString(False, self.flash11Mode) # early format support
        elif encoding == self.TYPE_NULL:
            value = None
        elif encoding == self.TYPE_UNDEFINED:
            value = None
        elif encoding == self.TYPE_BOOL_FALSE:
            value = False 
        elif encoding == self.TYPE_BOOL_TRUE:
            value = True 
        elif encoding == self.TYPE_DATE:
            ref = self.readUint29()
            
            if (ref & 1) == 0:
                value = self.getObject(ref>>1)
            else:
                value = self.readDouble() # dates are written as doubles
                self.addObject(value)
        elif (encoding == self.TYPE_XML or
            encoding == self.TYPE_XMLSTRING ):
            ref = self.readUint29()
            
            if (ref & 1) == 0:
                value = self.getObject(ref>>1)
            else:
                value = self.readBytes(ref >> 1) # return as string for now
                self.addObject(value)
        elif encoding == self.TYPE_DICTOBJECT:
            ref = self.readUint29()
            
            if (ref & 1) == 0:
                value = self.getObject(ref>>1)
            else:
                weakref = self.readByte() == 1
                count = ref >> 1
                value = {}
                self.addObject(value)
                while count > 0:
                    key = self.readAmfObject()
                    val = self.readAmfObject()

                    value[str(key)] = val
                    count -= 1
                    
        elif encoding == self.TYPE_ARRAY:
            value = {}
            ref = self.readUint29()
            
            if (ref & 1) == 0 :
                value = self.getObject(ref>>1)
            else :
                self.addObject(value)
                count = ref >> 1
                # read the non-dense portion
                s = self.readAmfString(True)
                while  s and len(s)>0:
                    v = self.readAmfObject()
                    value[s] = v
                    s = self.readAmfString(True)
                 #now read the dense portion
                i = 0
                while i < count:
                    value[i] = self.readAmfObject()
                    i += 1

        elif ( encoding == self.TYPE_VECTORINT or
            encoding == self.TYPE_VECTORUINT or
            encoding == self.TYPE_VECTORNUMBER or
            encoding == self.TYPE_VECTOROBJECT ):
            ref = self.readUint29()
            
            if (ref & 1) == 0:
                value = self.getObject(ref>>1)
            else:
                count = ref >> 1
                fixed = self.readByte() == 1
                value = []
                self.addObject(value)
                if (encoding == self.TYPE_VECTORINT or encoding == self.TYPE_VECTORUINT):
                    while(count > 0):
                        value.append(self.readInt())
                        count -= 1
                elif encoding == self.TYPE_VECTORNUMBER:
                    while(count > 0):
                        value.append(self.readDouble())
                        count -= 1
                elif encoding == self.TYPE_VECTOROBJECT:
                    className = self.readAmfString(True)
                    while (count > 0):
                        value.append(self.readAmfObject())
                        count -= 1

        elif encoding == self.TYPE_BYTEARRAY:
            ref = self.readUint29()
            
            if (ref & 1) == 0:
                value = self.getObject(ref>>1)
            else:
                value = self.readBytes(ref>>1)
                self.addObject(value)
        elif encoding == self.TYPE_OBJECT:
            ref = self.readUint29()
            if (ref & 1) == 0: 
                value = self.getObject(ref>>1)
            else :
                if ((ref & 3) == 1):
                    traits = self.traitsList[ref >> 2]
                else:
                    traits = {}
                    traits['dynamic'] = ((ref & 8) >> 3)
                    if ref & 4:
                        traits['externalizable'] = True
                    traits['count'] = ref >> 4
                    className = self.readAmfString(True)
                    
                    if className and len(className) > 0:
                        traits['className'] = className
                    else : 
                        traits['className'] = ""
                    slots = []
                    count = traits['count']
                    while (count):
                        slots.append(self.readAmfString(True))
                        count -= 1
                    traits['slots'] = slots
                    self.traitsList.append(traits)
                value = {}
                
                self.addObject(value)
                
                for slot in traits['slots']:
                    value[slot] = self.readAmfObject()
                    
                if (traits['dynamic'] == 1):
                    s = self.readAmfString(True)
                    while  s and len(s)>0:
                        v = self.readAmfObject()
                        value[s] = v
                        s = self.readAmfString(True)
        else:
            print(("invalid data type", encoding))
            value = None
        return value

    # Examine data stream to find its format
    def getFormat(self):
        if (self.data.getSize()<1):
            return None
        firstByte = ord(self.data[0])
        if firstByte == self.TYPE_OBJECT:
            self.format = "amfstream"   # raw stream from player
        elif firstByte == self.TYPE_ARRAY:
            self.format = "amfarray"  # saved array of telemetry data
        else:
            self.format = "oldstyle"  # early format
            self.flash11Mode = True
        return self.format 
    
    def readMetric(self): 
        record = None
        if self.flash11Mode:
            pass
        else:    
            traitsLen = len(self.traitsList)
            stringCount = len(self.stringList) 
            try:
                record = self.readAmfObject()
            except EOFError:
                self.traitsList = self.traitsList[0:traitsLen]
                self.stringList = self.stringList[0:stringCount]
                record = None
            finally:
                self.clearObjectsList()
        return record

    # reads the entire buffer as one array of objects
    def unpack(self):
        output = [] # all the data ends up in this array
        rec = self.readMetric()
        while (rec and self.data.getOffset()+1 < self.data.getSize()):
            output.append(rec)
            rec = self.readMetric()

        if (rec):
            output.append(rec)
        return output