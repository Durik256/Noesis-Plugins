# by Durik for xentax.com 
from inc_noesis import *

def registerNoesisTypes():
   handle = noesis.register("Harley Davidson", ".MDL")
   noesis.setHandlerTypeCheck(handle, CheckType)
   noesis.setHandlerLoadModel(handle, LoadModel)
   return 1

def CheckType(data):
    f = data.find(b'POLYVERTEX')
    if f == -1:
        return 0
    return 1       

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    
    materials, textures = [], []
    for x in range(bs.readInt()):
        f_label = string(bs)
        print('>>', f_label, ':')
        
        if 'MATERIAL' == f_label:
            mat_label = string(bs)
            
            for x in range(bs.readInt()):
            #type - 16(strng), 12(color), 8(float), 7(unk?), 4(int)
                id, type = bs.readInt(), bs.readInt()
                label = string(bs)
                print(label, 'id:', id, 'type:', type)
                
                if 'MATERIALNAME' == label:
                    mat_name = string(bs)
                    print(' -', mat_name)
                elif 'AMBIENT' == label:
                    ambien = NoeVec4.fromBytes(bs.readBytes(bs.readInt()))
                    print(' -', ambien)
                elif 'DIFFUSE' == label:
                    diffuse = NoeVec4.fromBytes(bs.readBytes(bs.readInt()))
                    print(' -', diffuse)
                elif 'EMISSIVE' == label:
                    emissive = NoeVec4.fromBytes(bs.readBytes(bs.readInt()))
                    print(' -', emissive)
                elif 'SPECULAR' == label:
                    specular = NoeVec4.fromBytes(bs.readBytes(bs.readInt()))
                    print(' -', specular)
                elif 'OPACITY' == label:
                    size, opacity = bs.readInt(), bs.readFloat()
                    print(' -', opacity)
                elif 'SHININESS' == label:
                    size, shiniess = bs.readInt(), bs.readFloat()
                    print(' -', shiniess)
                elif 'TRANSLUCENCY' == label:
                    size, transluceny = bs.readInt(), bs.readFloat()
                    print(' -', transluceny)
                else:
                    bs.seek(bs.readInt(),1)
            material = NoeMaterial(mat_label, '')
            
            material.name = mat_name
            material.setDiffuseColor(diffuse)
            material.setSpecularColor(specular)
            material.setAmbientColor(ambien)
            material.setAlphaTest(opacity*-1)
            #materials.append(material)
            
        elif 'TEXTURE' == f_label:
            tx_label = string(bs)
            
            for x in range(bs.readInt()):
                unk, type = bs.readInt(), bs.readInt()
                label = string(bs)
                print(label, 'unk:', unk, 'type:', type)
                
                if 'TEXTURENAME' == label:
                    tx_name = string(bs)
                    print(' -', tx_name)
                elif 'TEXTURELIST' == label:
                    txltype, txlsize, txlnum = [bs.readInt() for x in range(3)]
                    bs.seek(txlsize,1)
                    bs.seek(4,1)#FFFF
                elif 'TEXTURELIST_COUNT' == label:
                    size, tx_count = bs.readInt(), bs.readInt()
                elif 'TIMES' == label:
                    ttype, tsize, tnum = [bs.readInt() for x in range(3)]
                    bs.seek(tsize,1)
                    bs.seek(4,1)#FFFF
                elif 'TEXTUREFILE' == label:
                    tx_path = string(bs)
                    print(' -', tx_path)
                elif 'WRAPS' == label:
                    size, wraps = bs.readInt(), bs.readInt()
                    print(' -', wraps)
                elif 'WRAPT' == label:
                    size, wrapt = bs.readInt(), bs.readInt()
                    print(' -', wrapt)
                else:
                    bs.seek(bs.readInt(),1)
            try: imageDir = os.path.abspath(os.path.join(rapi.getDirForFilePath(rapi.getInputName()), '../images/'+tx_path))
            except: imageDir = ''
            '''
            if rapi.checkFileExists(imageDir):
                try:
                    materials[len(textures)].setTexture(imageDir)
                except:
                    pass
            textures.append(tx_path)
            '''
            materials.append(NoeMaterial(tx_name, imageDir))
            
        elif 'SRMESHMODEL' == f_label:
            mdl_label = string(bs)
            
            for x in range(bs.readInt()):
                count, type = bs.readInt(), bs.readInt()
                label = string(bs)
                print(label, 'count:', count, 'type:', type)
                
                if 'MESHNAME' == label:
                    mesh_name = string(bs)
                    print(' -', mesh_name)
                elif 'SORT' == label:
                    size, sort = bs.readInt(), bs.readInt()
                    print(' -', sort)
                elif 'POLYGONCOUNT' == label:
                    size, polycount = bs.readInt(), bs.readInt()
                    print(' -', polycount)
                elif 'VERTEXCOUNT' == label:
                    size, vertexcount = bs.readInt(), bs.readInt()
                    print(' -', vertexcount)
                elif 'PASSCOUNT' == label:
                    size, passcount = bs.readInt(), bs.readInt()
                    print(' -', passcount)
                elif 'ACTIVEPOLYGONCOUNT' == label:
                    size, activepolycount = bs.readInt(), bs.readInt()
                    print(' -', activepolycount)
                elif 'MATERIAL_PASS_0' == label:
                    mat_pass = string(bs)
                    print(' -', mat_pass)
                elif 'VERTEXMAT_PASS_0' == label:
                    vptype, vpsize, vpnum = [bs.readInt() for x in range(3)]
                    print(' - vptype:', vptype, 'vpsize:', vpsize,'vpnum:', vpnum)
                    VERTEXMAT_PASS_0 = [bs.readInt() for x in range(vpnum)]
                    print(VERTEXMAT_PASS_0)
                    #bs.seek(vpsize,1)#vpbuf
                    bs.seek(4,1)#FFFF
                elif 'SHADER_PASS_0' == label:
                    size, shaderpass = bs.readInt(), bs.readInt()
                    print(' -', shaderpass)
                elif 'NUMPOLYTEXURES' == label:
                    size, numpolytx = bs.readInt(), bs.readInt()
                    print(' -', numpolytx)
                elif 'TEXTURE_PASS_0' == label:
                    txpass = string(bs)
                    print(' -', txpass)
                elif 'POLYTEXTURE_PASS_0' == label:
                    ptptype, ptpsize, ptpnum = [bs.readInt() for x in range(3)]
                    print(' - ptptype:', ptptype, 'ptpsize:', ptpsize,'ptpnum:', ptpnum)
                    POLYTEXTURE_PASS_0 = [bs.readUByte() for x in range(ptpnum)]
                    #bs.seek(ptpsize,1)#ptpbuf
                    bs.seek(4,1)#FFFF
                elif 'POLYSHADER_PASS_0' == label:
                    psptype, pspsize, pspnum = [bs.readInt() for x in range(3)]
                    print(' - psptype:', psptype, 'pspsize:', pspsize,'pspnum:', pspnum)
                    bs.seek(pspsize,1)#pspbuf
                    bs.seek(4,1)#FFFF
                elif 'POLYSHADER_PASS_1' == label:
                    psptype, pspsize, pspnum = [bs.readInt() for x in range(3)]
                    print(' - psptype:', psptype, 'pspsize:', pspsize,'pspnum:', pspnum)
                    bs.seek(pspsize,1)#pspbuf
                    bs.seek(4,1)#FFFF
                elif 'POLYVERTEX' == label:
                    itype, isize, inum = [bs.readInt() for x in range(3)]
                    print(' - itype:', itype, 'isize:', isize,'inum:', inum)
                    ibuf = bs.readBytes(isize)
                    #ibuf = []
                    #for x in range(inum):
                    #    ibuf.append(bs.readBytes(itype))
                    bs.seek(4,1)#FFFF
                elif 'VERTEXLOC' == label:
                    vtype, vsize, vnum = [bs.readInt() for x in range(3)]
                    print(' - vtype:', vtype, 'vsize:', vsize,'vnum:', vnum)
                    vbuf = bs.readBytes(vsize)
                    bs.seek(4,1)#FFFF
                elif 'UVCOUNT' == label:
                    size, uvcount = bs.readInt(), bs.readInt()
                    print(' -', uvcount)
                elif 'TEXCOORDS_PASS_0' == label:
                    uvtype, uvsize, uvnum = [bs.readInt() for x in range(3)]
                    print(' - uvtype:', uvtype, 'uvsize:', uvsize,'uvnum:', uvnum)
                    uvbuf = bs.readBytes(uvsize)
                    bs.seek(4,1)#FFFF
                elif 'SHADEINDEX' == label:
                    size, shaderindex = bs.readInt(), bs.readInt()
                    print(' -', shaderindex)
                elif 'SHADEARRAY' == label:
                    satype, sasize, sanum = [bs.readInt() for x in range(3)]
                    print(' - satype:', sasize, 'sasize:', sasize,'sanum:', sanum)
                    sabuf = bs.readBytes(sasize)
                    bs.seek(4,1)#FFFF
                elif 'MORPHTARGETS' == label:
                    mttype, mtsize, mtnum = [bs.readInt() for x in range(3)]
                    bs.seek(mtsize,1)
                    bs.seek(4,1)#FFFF
                elif 'MORPHKEYS' == label:
                    mktype, mksize, mknum = [bs.readInt() for x in range(3)]
                    bs.seek(mksize,1)
                    bs.seek(4,1)#FFFF
                else:
                    bs.seek(bs.readInt(),1)
        
    ctx = rapi.rpgCreateContext()
            
    try: 
        if len(POLYTEXTURE_PASS_0)>0: pass
    except: POLYTEXTURE_PASS_0 = []
    #print('>>>>>>>>', tx_pass)
    
    if len(POLYTEXTURE_PASS_0)>0:
        for i,x in enumerate(POLYTEXTURE_PASS_0):
            rapi.rpgSetMaterial(materials[x].name)
            rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, vtype)
            try:rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, uvtype)
            except:pass
            rapi.rpgCommitTriangles(ibuf[i*12:i*12+12], noesis.RPGEODATA_INT, 3, noesis.RPGEO_TRIANGLE)
    else:
        rapi.rpgSetMaterial(materials[0].name)
        rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, vtype)
        try:rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, uvtype)
        except:pass
        rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_INT, len(ibuf)//4, noesis.RPGEO_TRIANGLE)
    
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials([], materials))
    mdlList.append(mdl)
    return 1

def string(bs):
    return noeAsciiFromBytes(bs.readBytes(bs.readInt()))