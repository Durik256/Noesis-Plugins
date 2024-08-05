# edit >> Durik256 (add weights and bones)
# orig script https://reshax.com/topic/944-nhl-21-mcd-models-ps4/
# ...

#Noesis python importer - EA NHL 21 .mcd models - 0.2 by Beedy
from inc_noesis import *
import noesis
#rapi methods should only be used during handler callbacks
import rapi

#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
	handle = noesis.register("NHL 21 (PS4)", ".mcd")
	noesis.setHandlerTypeCheck(handle, noetexCheckType)
	noesis.setHandlerLoadModel(handle, noepyLoadModel)
	
	noesis.logPopup()
	#print("The log can be useful for catching debug prints from preview loads.\nBut don't leave it on when you release your script, or it will probably annoy people.")
	return 1
#check if it's this type based on the data
def noetexCheckType(data):
    bs = NoeBitStream(data)
    Magic = bs.readBytes(4)
    if Magic != b'\x52\x53\x46\x00':
        return 0
    return 1  

readSkel = False
#load the model
def noepyLoadModel(data, mdlList):
   texList = []
   #matList = []
   baseName = rapi.getExtensionlessName(rapi.getLocalFileName(rapi.getLastCheckedName()))
   ctx = rapi.rpgCreateContext()
   bs = NoeBitStream(data, NOE_LITTLEENDIAN)
   
   bones = []
   if readSkel:
   		try:
   			import fmt_skel_nhl21 as skel
   			#data = rapi.loadIntoByteArray(os.path.join(os.path.dirname(rapi.getInputName()),'skeleton_player.skel'))
   			dir = os.path.dirname(rapi.getInputName())
   			for x in os.listdir(dir):
   				name, ext = os.path.splitext(x)
   				if ext.lower() == '.skel':
   					data = rapi.loadIntoByteArray(os.path.join(dir,x))
   					break
   		     
   			_mdlList = []
   			skel.noepyLoadModel(data, _mdlList)
   			bones = _mdlList[0].bones
   		except:
   			print('Error load skeleton!')
   wbufs = myRead(bs)
   
   file_size = os.path.getsize(noesis.getSelectedFile())
   bs.seek(0x10, NOESEEK_ABS)
   chunk_type = bs.readUInt()
   chunk_objects = bs.readUInt()
   chunk_size = bs.readUInt()
   while chunk_type != 1195724621:
   		if chunk_type != 1195724621:
   			bs.seek(chunk_size -12, NOESEEK_REL)
   			chunk_type = bs.readUInt()
   			print('chunk_type:', noePack('I',chunk_type))
   			chunk_objects = bs.readUInt()
   			chunk_size = bs.readUInt()
   unkn = bs.readUInt()
   vfmtCount = bs.readUInt()
   vfmtString = bs.readUInt()
   vfmtSize = bs.readUInt()
   VFMT = []
   for i in range(0, vfmtCount):
   		VFMT.append(["vpos", "postype", "uvpos", "uvtype", "uv2pos", "uv2type"])
   for i in range(0, vfmtCount):
   		vfmt = bs.readString()
   		x = vfmt.split(" ")
   		for j in range (0, len(x)):
   			y = x[j].split(":")
   			if y[0] == "p0":
   				VFMT[i][0] = y[1]
   				VFMT[i][1] = y[6]
   				
   			if y[0] == "t0":
   				VFMT[i][2] = y[1]
   				VFMT[i][3] = y[6]
   			if y[0] == "t1":
   				VFMT[i][4] = y[1]
   				VFMT[i][5] = y[6]

   		bs.seek(8, NOESEEK_REL)

   
   bs.seek(-8, NOESEEK_REL)
   MRTSCount = bs.readUInt()
   bs.seek(9, NOESEEK_REL)
   vCount = []
   VBsize = []
   vBufferSize = []
   VOff = []
   fCount = []
   fOff = []
   fIndex = []
   vIndex = []
   vIndex2 = []
   Index1 = []
   Index2 = []
   Index3 = []
   for i in range(0, MRTSCount):
   		vCount.append(bs.read("<i"))
   		VBsize.append(bs.read("<i"))
   		vBufferSize.append(vCount[i][0]*VBsize[i][0])
   		bs.seek(4, NOESEEK_REL)
   		VOff.append(bs.tell())
   		bs.seek(VOff[i] + vBufferSize[i] + 9, NOESEEK_ABS)

   bs.seek(-9, NOESEEK_REL)
   indexCount = bs.read("<i")

   for i in range(0, indexCount[0]):
   		bs.seek(9, NOESEEK_REL)
   		fBuff = (bs.read("<i"))
   		fCount.append(fBuff[0])
   		fBufferSize = (fBuff[0] * 2)
   		bs.seek(4, NOESEEK_REL)
   		fOff.append(bs.tell())
   		bs.seek(fBufferSize, NOESEEK_REL)
   		meshOffset = bs.tell()

   				  				
 #Construct Models
		  			   	
   bs.seek(meshOffset, NOESEEK_ABS)
   meshCount = (bs.read("<i"))
   bs.seek(4, NOESEEK_REL)
   meshTableSize = []
   for i in range(0, meshCount[0]):
   		table = bs.read("<iiiiiiiiiii")
   		if table[10] != 1296388936:
   			t2 = bs.read("<i")
   			if t2[0] == 1296388936:
   				meshTableSize.append(48)
   			elif t2[0] == 1195724621:
   				meshTableSize.append(44)
   			else:
   				t3 = bs.read("<i")
   				if t3[0] == 1296388936 or t3[0]== 1195724621:
   					meshTableSize.append(48)
   		else:
   			meshTableSize.append(44)				
   bs.seek(meshOffset, NOESEEK_ABS)
   meshCount = (bs.read("<i"))
   for i in range(0, meshCount[0]):
   		bs.seek(24, NOESEEK_REL)
   		I1 = bs.read("<i")
   		Index1.append(I1[0])
   		I2 = bs.read("<i")
   		Index2.append(I2[0])
   		I3 = bs.read("<i")
   		Index3.append(I3[0])
   		vI = bs.read("<i")
   		fI = bs.read("<i")
   		vI2 = bs.read("<i")

   		if meshTableSize[i] == 44:
   			bs.seek(-4, NOESEEK_REL)
   			vIndex.append(vI[0])
   			fIndex.append(fI[0])
   			vIndex2.append(-1)
   		else:
   			vIndex.append(vI[0])
   			fIndex.append(vI2[0])
   			vIndex2.append(fI[0])
   		
   for i in range(0, meshCount[0]):


		   		
   		bs.seek(VOff[vIndex[i]], NOESEEK_ABS) #Seek to Vertices Start
   		VertBuff = bs.readBytes(vBufferSize[vIndex[i]])
   		if vIndex2[i] != -1:
   			bs.seek(VOff[vIndex2[i]], NOESEEK_ABS) #Seek to Vertices Start
   			UvBuff = bs.readBytes(vBufferSize[vIndex2[i]])
   		
   		rapi.rpgSetName("mesh_" + str(i))
   		
   		rapi.rpgBindPositionBufferOfs(VertBuff , noesis.RPGEODATA_FLOAT, VBsize[vIndex[i]][0], 0)
   		
   		
   		if VFMT[Index1[i]][3] == "2f16":
   		
   			if vIndex2[i] == -1:
   				rapi.rpgBindUV1BufferOfs(VertBuff, noesis.RPGEODATA_HALFFLOAT, VBsize[vIndex[i]][0], int(VFMT[Index1[i]][2], 16))
   				#if VFMT[Index1[i]][4] != "uv2pos":
   					#print(VFMT[Index1[i]][4])
   					#rapi.rpgBindUV2BufferOfs(VertBuff, noesis.RPGEODATA_HALFFLOAT, VBsize[vIndex[i]][0], int(VFMT[Index1[i]][4], 16))
   					#rapi.rpgBindUVXBufferOfs(VertBuff, noesis.RPGEODATA_HALFFLOAT, VBsize[vIndex[i]][0], 3, 3, int(VFMT[Index1[i]][4], 16))
   			else:

   				rapi.rpgBindUV1BufferOfs(UvBuff, noesis.RPGEODATA_HALFFLOAT, VBsize[vIndex2[i]][0], int(VFMT[Index1[i]][2], 16))	
   		
   		try:
   			index, bonePerVert, numElem, wbuf, iwbuf = wbufs[i]
   			rapi.rpgBindBoneIndexBuffer(iwbuf, noesis.RPGEODATA_USHORT, bonePerVert*2, bonePerVert)
   			rapi.rpgBindBoneWeightBuffer(wbuf, noesis.RPGEODATA_FLOAT, bonePerVert*4, bonePerVert)
   		except:
   			pass
   		
   		bs.seek(fOff[fIndex[i]], NOESEEK_ABS) #Seek to Faces Start
   		FaceBuff = bs.readBytes(fCount[fIndex[i]]*2)
   		rapi.rpgCommitTriangles(FaceBuff, noesis.RPGEODATA_USHORT, (fCount[fIndex[i]]), noesis.RPGEO_TRIANGLE, 1)
   		rapi.rpgClearBufferBinds()

   mdl = rapi.rpgConstructModel()
   mdl.setBones(bones)
   mdlList.append(mdl)
   rapi.rpgReset() 
   return 1

def myRead(bs):
    bs.seek(16)
    wbufs = []
    while bs.tell() < bs.getSize():
        readChunk(bs, wbufs)
    bs.seek(0)
    return wbufs

def readChunk(bs, wbufs):
    cpos = bs.tell()
    label = bs.read(4)
    unk, size, ofs = bs.read('3I')
    print(label, unk, size, ofs)
    if label == b'TIEW':
        numBLock = bs.readUInt()
        for x in range(numBLock):
            index, bonePerVert, numElem = bs.read('3I')
            wbuf = bs.read(numElem*bonePerVert*4)
            iwbuf = bs.read(numElem*bonePerVert*2)
            wbufs.append([index, bonePerVert, numElem, wbuf, iwbuf])

    bs.seek(cpos+size)