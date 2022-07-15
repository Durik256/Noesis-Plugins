from inc_noesis import *
import math
from ctypes import *
import noewin
window = 0
def registerNoesisTypes():
    handle = noesis.register("driver sf file", ".vehc;.sp")
    window = noesis.registerTool("&DSF importer", ToolMethod)
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    noesis.logPopup()
    return 1

listBox = None

SectArr = []
VEHCarr = []

MATarr = []
SBBHarr = []
VBarr = []
IBarr = []
partsarr = []
texUID = ""

existingMat = False
MARH = 0
dirPath = ""

BitStream = None
modelList = None

def noepyCheckType(data):
    return 1

def noepyLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    global dirPath
    global BitStream
    global modelList
    BitStream = bs
    modelList = mdlList
    dirPath = rapi.getDirForFilePath(rapi.getInputName())
    file_extension = os.path.splitext(rapi.getInputName())[1]
        
    if file_extension==".VEHC":
        importVEHC(bs, False)
    else:
        ToolMethod(window)
        modelList.append(NoeModel())
        loadSP(bs)
    return 1

def frc(src):
    return src - math.floor(src)

def decodeN(enc):
    cosTheta = [0,0]
    cosPhi = [0,0]
        
    enc[0] = frc(enc[0])
    enc[1] = frc(enc[1])
        
    enc[0] = (enc[0]*2 - 1)*math.pi
    enc[1] = (enc[1]*2 - 1)*math.pi
        
    enc[0] = math.degrees(math.radians(enc[0]))
    enc[1] = math.degrees(math.radians(enc[1]))
        
    cosTheta[0] = math.cos(enc[1])
    cosTheta[1] = math.sin(enc[1])
        
    cosPhi[0] = math.cos(enc[0])
    cosPhi[1] = math.sin(enc[0])
        
    x = cosTheta[1] * cosPhi[1]
    z = cosTheta[0] * cosPhi[1]
    y = cosPhi[0]
        
    return [x, y, z]

def bit_set(i1,i2,bool):
    bin = list((bindigits(i1, 32))[::-1])
    bin[i2] = '1' if bool else '0'
    bin = ''.join(bin)[::-1]
    return twos_comp(int(bin,2), len(bin))

def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

def bindigits(n, bits):
    s = bin(n & int("1"*bits, 2))[2:]
    return ("{0:0>%s}" % (bits)).format(s)
    
def bit_get(i1,i2):
    bin = bindigits(i1, 32)[::-1]
    bool = True if bin[i2]=='1' else False
    return bool
    
def bin_to_float(binary):
    return struct.unpack('!f',struct.pack('!I', int(binary, 2)))[0]

def unpackUV(enc): #unpacks half4 UV coordinates from int24_int24_int16
    u = int(enc[0])
    v = int(enc[1])
    w = int(enc[2])
    
    x = 0
    for b in range(16): x = bit_set(x, b, bit_get(u,b))
    y = 0
    for b in range(8): y = bit_set(y, b, bit_get(u, b+16))
    for b in range(8,16): y = bit_set(y, b, bit_get(v, b-8))
    z = 0
    for b in range(16): z = bit_set(z, b, bit_get(v, b+8))

    x = ((x & 0x8000)<<16)+((x & 0x7fff)<<13)+((127 - 15)<<23)
    y = ((y & 0x8000)<<16)+((y & 0x7fff)<<13)+((127 - 15)<<23)
    z = ((z & 0x8000)<<16)+((z & 0x7fff)<<13)+((127 - 15)<<23)
    w = ((w & 0x8000)<<16)+((w & 0x7fff)<<13)+((127 - 15)<<23)
    
    x = bin_to_float(bindigits(x,32))
    y = bin_to_float(bindigits(y,32))
    z = bin_to_float(bindigits(z,32))
    w = bin_to_float(bindigits(w,32))
    return [x, y, z, w]

def recurCHNK(binstr): #GOLDEN
    CHNKoffset = binstr.getOffset()
    CHNKhead = noeAsciiFromBytes(binstr.readBytes(4))
    if CHNKhead == "CHNK": #children
        CHNKsize = binstr.readUInt() #data chunk size, excluding end name>>>
        CHNKsections = binstr.readUInt() #number of chunk data sections
        CHNKparams = binstr.readUInt() #number of 4-byte parameters for each section
            
        for i in range(CHNKsections):
            global sectName 
            sectName = noeAsciiFromBytes(binstr.readBytes(4))
            sectOffset = binstr.readUInt() + CHNKoffset
            binstr.seek(4, NOESEEK_REL)
            global sectSize
            sectSize = binstr.readUInt()
            binstr.seek((CHNKparams - 3)*4, NOESEEK_REL)
                
            currentoffset = binstr.getOffset()
            binstr.seek(sectOffset, NOESEEK_ABS)
            recurCHNK(binstr)
            binstr.seek(currentoffset, NOESEEK_ABS)

    else: #read the data
        global existingMat
        global texUID
        binstr.seek(-4, NOESEEK_REL)
        if sectName == "UIDC": 
            #print("texture Unique ID")
            texUID = ""
            for w in range(sectSize): 
                texUID += hex(binstr.readUByte())[2:]
            #print("texUID",texUID)
        elif sectName == "DXTC": 
            #print("DDS texture")
            path = os.path.join(dirPath,texUID+".dds")
            #print(path)
            if not os.path.exists(path):
                pixelData = binstr.readBytes(sectSize)
                Tex = open(path, "wb")
                Tex.write(pixelData)
                Tex.close()
        elif sectName == "MAHE": 
            #print("Material Header")
            existingMat = False
            aMAT.matHash = binstr.readInt64()
            binstr.seek(8, NOESEEK_REL)
            
            for eMAT in MATarr:
                if eMAT.matHash == aMAT.matHash:
                    existingMat = True
                    break
        elif sectName == "MATX": 
            #Material MatXML
            aMAT.material = NoeMaterial(noeAsciiFromBytes(binstr.readBytes(sectSize)),"")
        elif sectName == "MARH":
            global MARH
            MARH = binstr.readInt()
        elif sectName == "MARP":
            if not existingMat:
                global MARP
                MARP = "marp"#readstring binstr
                binstr.seek(32, NOESEEK_REL)# - MARP.count - 1)
                if MARH == 1315969474 and MARP == "g_texDiffuseMap":
                    texUID = ""
                    for w in range(8): texUID += hex(binstr.readUByte())[2:]
                    aTex = os.path.join(dirPath,texUID+".dds")
                    if texUID == "0122b7bf7fa1227" or texUID == "0122b71c1fa1227" or texUID == "0122b73d1fa1227" or texUID == "0122b77dffa1227" or texUID == "012622143a4c428" or texUID == "012622354a4c428":
                        aMAT.setTexture(aTex)
                    else:
                        aMAT.setTexture(aTex)
                        if texUID == "0122b79effa1227":
                            aMAT.setTexture(aTex)
                        else:
                            aMAT.setTexture(aTex)
                    MATarr.append(copy.copy(aMAT))
                    binstr.seek(-8, NOESEEK_REL)
        elif sectName == "SBBH": 
            #Submodel header
            dpHash = binstr.readInt64()
            matHash = binstr.readInt64()
            vxHash = binstr.readInt64()
            binstr.seek(8, NOESEEK_REL)
            padding = binstr.readUInt()
            binstr.seek(12, NOESEEK_REL)
            ixHash = binstr.readInt64()
            IBoffset = binstr.readUInt()
            Icount = binstr.readUInt()
            SBBHarr.append(SBBH(dpHash, matHash, vxHash, padding, ixHash, IBoffset, Icount))
        elif sectName == "VXHD": 
            #Pooled vertex header
            aVB.vxHash = binstr.readInt64()
            aVB.numverts = binstr.readUInt()
            aVB.stride = binstr.readUInt()
        elif sectName == "VXDP": 
            #Pooled vertex dependencies
            aVB.dpHasharr = []
            for j in range(int(sectSize/8)):
                aVB.dpHasharr.append(binstr.readInt64())
        elif sectName == "VXDT":
            #Pooled vertex buffer
            aVB.offset = binstr.getOffset()
        elif sectName == "VDCL": 
            #Pooled vertex declaration
            aVB.vproparr = []
            aVP = vprop()
            numprops = binstr.readUInt()
            for j in range(numprops):
                aVP.type = binstr.readUInt() #type? 0= vpos, 8=UV, 9=unk, 5=normal, 12=damage morph
                aVP.elmts = binstr.readUInt() #number of shorts, halves, bytes etc
                aVP.eltype = binstr.readUInt() #1=shorts, 8=halves, 2=unk, 6=4bytes as normals
                aVP.hash = binstr.readInt()

                aVB.vproparr.append(copy.copy(aVP))
            VBarr.append(copy.copy(aVB))

        elif sectName == "IXHD": 
            #Pooled index header
            aIB.ixHash = binstr.readInt64()
            aIB.numinds = binstr.readUInt()
            aIB.indsize = binstr.readUInt() #one index in bytes
            binstr.seek(8, NOESEEK_REL) #unknown
        elif sectName == "IXDT": 
            #Pooled index buffer
            aIB.offset = binstr.getOffset()
            IBarr.append(copy.copy(aIB))
        elif sectName == "MODL": 
            #Model Container                   
            numSets1 = binstr.readUInt()
            numSets2 = binstr.readUInt()
            num3 = binstr.readUInt()
            num4 = binstr.readUInt()
            for i in range(numSets1):
                vec1 = [binstr.readFloat() for x in range(4)]
                vec2 = [binstr.readFloat() for x in range(4)]
                vec3 = [binstr.readFloat() for x in range(4)]
                vec4 = [binstr.readFloat() for x in range(4)]
                parthash = binstr.readInt64()
                LODcount = binstr.readUInt()
                offset = binstr.readUInt() #??
                n5 = binstr.readUInt()
                n6 = binstr.readUInt()
                n7 = binstr.readUInt()
                n8 = binstr.readUInt()

                partsarr.append(Part(parthash, LODcount,[]))
            for part in partsarr:
                for j in range(part.LODs):
                    part.LODarr.append(LODgroup(binstr.readUInt(), binstr.readUInt(),[]))
                    offset1 = binstr.readUInt()
                    offset2 = binstr.readUInt()
            for part in partsarr:
                for LODgr in part.LODarr:
                    for j in range(LODgr.meshCount):
                        LODgr.dpHasharr.append(binstr.readInt64())

            for j in range(len(SBBHarr)):
                along = binstr.readUInt()
    return 1

def importVEHC(binstr, tempFile):
    del SBBHarr[:]
    del VBarr[:]
    del IBarr[:]
    del partsarr[:]

    recurCHNK(binstr)

    positions = []
    normals = []
    texCoord = []

    for vb in VBarr:
        binstr.seek(vb.offset, NOESEEK_ABS)
        if vb.stride == 32:
            for v in range(vb.numverts):
                vx = float(binstr.readShort()/4096)
                vy = float(binstr.readShort()/4096)
                vz = float(binstr.readShort()/4096)
                vw = float(binstr.readShort()/4096)
                positions.append(NoeVec3([vx,vy,vz]))
                
                u = binstr.readInt()
                for x in range(24,32): u = bit_set(u,x,False)#convert to 24bit for storing as float
                binstr.seek(-1, NOESEEK_REL)
                v = binstr.readInt()
                for x in range(24,32): v = bit_set(v,x,False)
                binstr.seek(-1, NOESEEK_REL)
                w = binstr.readShort()
                uv = unpackUV([u,v,w])
                texCoord.append(NoeVec3([uv[0],uv[1],0]))
                        
                binstr.seek(4, NOESEEK_REL) #bone indices?
                        
                nx = float(binstr.readUByte()/255)
                ny = float(binstr.readUByte()/255)
                nz = binstr.readUByte()
                nw = binstr.readUByte()
                n = decodeN ([nx, ny])
                normals.append(NoeVec3([n[0],n[1],n[2]]))
                        
                binstr.seek(8, NOESEEK_REL) #damage positions
                
        elif vb.stride == 28:
            for v in range(vb.numverts):
                vx = float(binstr.readShort()/4096)
                vy = float(binstr.readShort()/4096)
                vz = float(binstr.readShort()/4096)
                vw = float(binstr.readShort()/4096)
                positions.append(NoeVec3([vx,vy,vz]))
                
                u = binstr.readInt()
                for x in range(24,32): u = bit_set(u,x,False)
                binstr.seek(-1, NOESEEK_REL)
                v = binstr.readByte()
                uv = unpackUV([u,v,0])
                texCoord.append(NoeVec3([uv[0],uv[1],0]))
                        
                binstr.seek(4, NOESEEK_REL) #bone indices?
                        
                nx = float(binstr.readUByte()/255)
                ny = float(binstr.readUByte()/255)
                nz = binstr.readUByte()
                nw = binstr.readUByte()
                n = decodeN ([nx, ny])
                normals.append(NoeVec3([n[0],n[1],n[2]]))
                        
                binstr.seek(8, NOESEEK_REL) #damage positions
                
        elif vb.stride == 20: #wheels (no damage)
            for v in range(vb.numverts):
                vx = float(binstr.readShort()/4096)
                vy = float(binstr.readShort()/4096)
                vz = float(binstr.readShort()/4096)
                vw = float(binstr.readShort()/4096)
                positions.append(NoeVec3([vx,vy,vz]))
                
                u = binstr.readInt()
                for x in range(24,32): u = bit_set(u,x,False)
                binstr.seek(-1, NOESEEK_REL)
                v = binstr.readByte()
                uv = unpackUV([u,v,0])
                texCoord.append(NoeVec3([uv[0],uv[1],0]))
                        
                binstr.seek(4, NOESEEK_REL)#bone indices?
                        
                nx = float(binstr.readUByte()/255)
                ny = float(binstr.readUByte()/255)
                nz = binstr.readUByte()
                nw = binstr.readUByte()
                n = decodeN ([nx, ny])
                normals.append(NoeVec3([n[0],n[1],n[2]]))
                
        elif vb.stride == 16:
            for v in range(vb.numverts):
                vx = float(binstr.readShort()/4096)
                vy = float(binstr.readShort()/4096)
                vz = float(binstr.readShort()/4096)
                vw = float(binstr.readShort()/4096)
                positions.append(NoeVec3([vx,vy,vz]))
                
                u = binstr.readInt()
                for x in range(24,32): u = bit_set(u,x,False)#convert to 24bit for storing as float
                binstr.seek(-1, NOESEEK_REL)
                v = binstr.readInt()
                for x in range(24,32): v = bit_set(v,x,False)
                binstr.seek(-1, NOESEEK_REL)
                w = binstr.readShort()
                uv = unpackUV([u,v,w])
                texCoord.append(NoeVec3([uv[0],uv[1],0]))
                        
                normals.append(NoeVec3([0,0,-1]))
        else: print ("Unknown vertex stride: " + str(vb.stride))

    meshes = []
    for sb in SBBHarr: 
        name = hex(sb.dpHash)[2:]
        print(name)
        face = []
        
        vpad = 0
        for vb in range(1,len(VBarr)):
            if VBarr[vb].vxHash == sb.vxHash:
                while vb > 0:
                    vb -= 1
                    vpad += VBarr[vb].numverts
                    
                break #no need to test the other VBs

        for ib in range(len(IBarr)):
            if IBarr[ib].ixHash == sb.ixHash:
                binstr.seek(IBarr[ib].offset + sb.offset*IBarr[ib].indsize, NOESEEK_ABS)
                if IBarr[ib].indsize == 2: 
                    for i in range(int(sb.count/3)):
                        ind1 = binstr.readUShort() + vpad + sb.padding
                        ind2 = binstr.readUShort() + vpad + sb.padding
                        ind3 = binstr.readUShort() + vpad + sb.padding

                        face += [ind1,ind2,ind3]

                elif IBarr[ib].indsize == 4: 
                    for i in range(sb.count):
                        ind1 = binstr.readUInt()  + vpad + sb.padding
                        ind2 = binstr.readUInt() + vpad + sb.padding
                        ind3 = binstr.readUInt()  + vpad + sb.padding

                        face += [ind1,ind2,ind3]
                break
        mesh = createMesh(face,positions,name,normals,texCoord)
        meshes.append(mesh)        
    mdl = NoeModel(meshes)
    modelList.append(mdl)
    return 1

def createMesh(face,positions,name,normals,texCoord):
    myPos = []
    myNorm = []
    myUV = []
    myFace = face
    alone = list(set(myFace))
    for j in range(len(alone)):
        for i in range(len(myFace)):
            if alone[j] == myFace[i]:
                myFace[i] = j
    for m in alone: 
        myPos.append(positions[int(m)])
        myNorm.append(normals[int(m)])
        myUV.append(texCoord[int(m)])
    mesh = NoeMesh(myFace,myPos,name)
    mesh.setNormals(myNorm)
    mesh.setUVs(myUV)
    return mesh

def loadSP(bs):
    listBox.resetContent()
    VEHCarr = []
    readCHNK(bs)
        
    VEHCarr.append(VEHC(0,"Shared_Resources.SSIC",0,0))
    listBox.addString("000_Shared_Resources.SSIC")
    
    for s in SectArr:
        if s.name == "VEHC":
            VEHCarr.append(VEHC(0,None,s.offset,s.size))
        elif s.name == "SSIC":
            VEHCarr[1].name = "000_Shared_Resources.SSIC"
            VEHCarr[1].offset = s.offset
            VEHCarr[1].size = s.size
            bs.seek(s.offset, NOESEEK_ABS)
            readCHNK(bs)
            bs.seek(s.offset, NOESEEK_ABS)
            recurCHNK(bs)
        elif s.name == "MDXN": 
            #save common textures and materials
            pass
        elif s.name == "NONR": 
            #go deeper t oget file names
            bs.seek(s.offset, NOESEEK_ABS)
            readCHNK(bs)
        elif s.name == "VSCT":
            #short names
            bs.seek(s.offset, NOESEEK_ABS)

            bs.seek(4, NOESEEK_REL) #VSCT
            one = bs.readUShort()
            numcars = bs.readUShort()
            for j in range(int(numcars/3 - 1)):
                VEHCarr[j*3+2].id = bs.readUShort()
                bs.seek(4, NOESEEK_REL)
                VEHCarr[j*3+2].name = noeAsciiFromBytes(bs.readBytes(16)) + "_LOD2_5.VEHC"
                bs.seek(6, NOESEEK_REL)

                VEHCarr[j*3+3].id = bs.readUShort()
                bs.seek(4, NOESEEK_REL)
                VEHCarr[j*3+3].name = noeAsciiFromBytes(bs.readBytes(16)) + "_cockpit.VEHC"
                bs.seek(6, NOESEEK_REL)
                                        
                VEHCarr[j*3+4].id = bs.readUShort()
                bs.seek(4, NOESEEK_REL)
                VEHCarr[j*3+4].name = noeAsciiFromBytes(bs.readBytes(16)) + "_LOD1.VEHC"
                bs.seek(6, NOESEEK_REL)

                listBox.addString(str(VEHCarr[j*3+2].id)+ "_" + VEHCarr[j*3+2].name)
                listBox.addString(str(VEHCarr[j*3+3].id)+ "_" + VEHCarr[j*3+3].name)
                listBox.addString(str(VEHCarr[j*3+4].id)+ "_" + VEHCarr[j*3+4].name)
        elif s.name == "BINF":
            pass
    return 1

def readCHNK (binstr):
    CHNKoffset = binstr.getOffset()
    CHNKhead = noeAsciiFromBytes(binstr.readBytes(4))
    CHNKsize = binstr.readUInt() #data chunk size, excluding end name>>>
    CHNKsections = binstr.readUInt() #number of chunk data sections
    CHNKparams = binstr.readUInt() #number of 4-byte parameters for each section
        
    for i in range(CHNKsections):
        sectName = noeAsciiFromBytes(binstr.readBytes(4))
        sectOffset = binstr.readUInt()
        binstr.seek(4, NOESEEK_REL)
        sectSize = binstr.readUInt()
        binstr.seek((CHNKparams - 3)*4, NOESEEK_REL)
        SectArr.append(Sect(sectName, (sectOffset + CHNKoffset), sectSize))
    return 1

def exportVEHC(index):
    if not os.path.exists(os.path.join(dirPath,str(VEHCarr[index].id) + "_" + VEHCarr[index].name)):
        f = open(os.path.join(dirPath,str(VEHCarr[index].id) + "_" + VEHCarr[index].name), "wb")
        BitStream.seek(VEHCarr[index].offset, NOESEEK_ABS)
        Data = BitStream.readBytes(VEHCarr[index].size)
        f.write(Data)
        f.close()
    return 1
   
#window method
def ExportCar(noeWnd, controlId, wParam, lParam):
    button = noeWnd.getControlById(controlId)
    listIndex = listBox.getSelectionIndex()+1
    
    exportVEHC(listIndex)
    return True
    
def ExportAll(noeWnd, controlId, wParam, lParam):
    button = noeWnd.getControlById(controlId)
    carCount = len(VEHCarr)

    for x in range(1, carCount):
        if VEHCarr[x].name:
            exportVEHC(x)
            print(VEHCarr[x].name+" save")
    return True
    
def LoadModel(noeWnd, controlId, wParam, lParam):
    button = noeWnd.getControlById(controlId)
    listIndex = listBox.getSelectionIndex()+1
    print(VEHCarr[listIndex].id, VEHCarr[listIndex].name) 
    """
    global BitStream
    BitStream.seek(VEHCarr[listIndex].offset, NOESEEK_ABS)
    importVEHC(BitStream)
    """
    exportVEHC(listIndex)
    tempPath = os.path.join(dirPath,str(VEHCarr[listIndex].id) + "_" + VEHCarr[listIndex].name)
    noesis.openAndRemoveTempFile(tempPath)
    
    return True

def ToolMethod(toolIndex):
    noeWnd = noewin.NoeUserWindow("Driver San Francisco Importer", "convert", 500, 300)

    noeWindowRect = noewin.getNoesisWindowRect()
    if noeWindowRect:
        windowMargin = 64
        noeWnd.x = noeWindowRect[0] + windowMargin
        noeWnd.y = noeWindowRect[1] + windowMargin
    if not noeWnd.createWindow():
        print("Failed to create window.")
        return 0

    noeWnd.setFont("Arial", 14)
    
    buttonExportCar = noeWnd.createButton("Export .VEHC", 10, 225, 96, 32, ExportCar)
    buttonExport = noeWnd.getControlByIndex(buttonExportCar)
    
    buttonLoadModel = noeWnd.createButton("Load Selected", 252, 225, 126, 32, LoadModel)
    buttonLoad = noeWnd.getControlByIndex(buttonLoadModel)
    
    buttonExportAll = noeWnd.createButton("Export All", 116, 225, 126, 32, ExportAll)
    buttonAll = noeWnd.getControlByIndex(buttonExportAll)
    
    global listBox 
    listIndex = noeWnd.createListBox(10, 22, 480, 220, None, noewin.LBS_NOTIFY)
    listBox = noeWnd.getControlByIndex(listIndex)
    return 0

#all class
class VEHC:
    def __init__(self, id, name, offset, size):
        self.id = id
        self.name = name
        self.offset = offset
        self.size = size
        
class Sect:
    def __init__(self, name, offset, size):
        self.name = name
        self.offset = offset
        self.size = size
        
class SBBH:
    def __init__(self, dpHash, matHash, vxHash, padding, ixHash, offset, count):
        self.dpHash = dpHash
        self.matHash = matHash
        self.vxHash = vxHash
        self.padding = padding
        self.ixHash = ixHash
        self.offset = offset
        self.count = count
        
class vprop:
    def __init__(self, type=0, elmts=0, eltype=0, hash=0):
        self.type = type
        self.elmts = elmts
        self.eltype = eltype
        self.hash = hash
        
class MAT:
    def __init__(self, matHash=0, material=None):
        self.matHash = matHash
        self.material = material
        
class VB:
    def __init__(self, vxHash=0, numverts=0, stride=0, dpHasharr=[], offset=0, vproparr=[]):
        self.vxHash = vxHash
        self.numverts = numverts
        self.stride = stride
        self.dpHasharr = dpHasharr
        self.offset = offset
        self.vproparr = vproparr
        
class IB:
    def __init__(self, ixHash=0, numinds=0, indsize=0, offset=0):
        self.ixHash = ixHash
        self.numinds = numinds
        self.indsize = indsize
        self.offset = offset
        
aMAT = MAT()
aVB = VB()
aIB = IB()       

class Part:
    def __init__(self, hash, LODs, LODarr):
        self.hash = hash
        self.LODs = LODs
        self.LODarr = LODarr
        
class LODgroup:
    def __init__(self, type, meshCount, dpHasharr):
        self.type = type
        self.meshCount = meshCount
        self.dpHasharr = dpHasharr