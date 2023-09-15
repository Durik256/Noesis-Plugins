#by Durik256
#just fast adaptation for Noesis, orig script:
#https://github.com/Murugo/Misc-Game-Research/blob/main/PS2/Rule%20of%20Rose/mdl2obj.py
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Ape Escape 3", ".i3d;.mdl")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def noepyCheckType(data):
    #if data[:7] != b'I3D_BIN':
    #    return 0
    return 1

def err(msg):
    print("Error: {}".format(msg))
    #sys.exit(1)

def getuint16(b, offs = 0):
    return noeUnpack('<H', b[offs:offs+2])[0]

def getnuint16(b, offs, n):
    return noeUnpack('<' + 'H'*n, b[offs:offs+2*n])

def getuint32(b, offs = 0):
    return noeUnpack('<I', b[offs:offs+4])[0]

def getfloat32(b, offs):
    return noeUnpack('<f', b[offs:offs+4])[0]

def getnfloat32(b, offs, n):
    return noeUnpack('<' + 'f'*n, b[offs:offs+4*n])

class Node:
    def __init__(self, buf, offs):
        self.dataOffs = getuint32(buf, offs)
        self.dataType = buf[offs + 0x7] & 0x7F
        self.children = []
        numChildren = getuint16(buf, offs + 0x4)
        firstChildOffs = getuint32(buf, offs + 0x8)
        for i in range(numChildren):
            self.children.append(Node(buf, firstChildOffs + i * 0x10))
    
    def getChildrenByType(self, dataType):
        result = []
        for child in self.children:
            result += child.getChildrenByType(dataType)
        if self.dataType == dataType:
            result = [self] + result
        return result


def parseName(buf, offs):
    endOffs = offs
    while buf[endOffs] != 0:
        endOffs += 1
    return buf[offs:endOffs].decode(encoding='ascii')


class SubmeshPiece:
    def __init__(self, offs):
        self.offs = offs
        self.vtx = []
        self.vt = []
        self.vn = []
        self.ind = []


class Submesh:
    def __init__(self, offs, materialIndex):
        self.offs = offs
        self.materialIndex = materialIndex
        self.submeshPieces = []


class Mesh:
    def __init__(self, offs):
        self.offs = offs
        self.submeshes = []


class MeshInstance:
    def __init__(self, offs, combinedMeshOffs):
        self.offs = offs
        self.combinedMeshOffs = combinedMeshOffs
        self.meshes = []
        
vumem = [NoeVec4([0, 0, 0, 0]) for _ in range(0x1000)]  # VU1 memory is 16K bytes
def parseVif(buf, offs):
    endoffs = offs + (buf[offs + 0x4] << 4) + 0x10
    offs += 0x10
    vif_r = [0, 0, 0, 0]  # Can I assume this?
    vif_c = [1, 1, 1, 1]  # Pretty sure I can assume this at least
    cl = 1
    wl = 1
    mask = [0 for _ in range(16)]

    def maybe_mask_value(val, index, cycle, use_mask):
        if not use_mask or mask[index] == 0b00:
            return val
        if mask[index + min(cycle, 3) * 4] == 0b01:
            return vif_r[index]
        if mask[index + min(cycle, 3) * 4] == 0b10:
            return vif_c[min(3, cycle)]
        return 0

    while offs < endoffs:
        imm, qwd, cmd = struct.unpack('<HBB', buf[offs:offs+4])
        cmd &= 0x7F
        offs += 4
        if cmd == 0b00000000:  # NOP
            continue
        elif cmd == 0b00000001:  # STCYCLE
            cl = imm & 0xFF
            wl = (imm >> 8) & 0xFF
        elif cmd == 0b00110000:  # STROW
            vif_r = getnfloat32(buf, offs, 4)
            offs += 0x10
        elif cmd == 0b00110001:  # STCOL
            vif_c = getnfloat32(buf, offs, 4)
            offs += 0x10
        elif cmd == 0b00100000:  # STMASK
            m = getuint32(buf, offs)
            mask = [((m >> (i << 1)) & 0x3) for i in range(16)]
            offs += 4
        elif cmd >> 5 == 0b11:  # UNPACK
            # NOTE: This has to handle both skipping writes (cl >= wl) and filling writes (cl < wl)!
            addr = imm & 0x3FF
            vnvl = cmd & 0xF
            m = (cmd & 0x10) > 0
            j = 0
            if vnvl == 0b0000:  # S-32
                width = 4
                for i in range(qwd):
                    val = 0
                    if cl >= wl or (i % wl) < cl:
                        val = getfloat32(buf, width * j + offs)
                        j += 1
                    addroffs = cl * (i // wl) + (i % wl) if cl >= wl else 0
                    vumem[addr + addroffs] = NoeVec4([
                        maybe_mask_value(val, 0, i, m),
                        maybe_mask_value(val, 1, i, m),
                        maybe_mask_value(val, 2, i, m),
                        maybe_mask_value(val, 3, i, m),
                    ])
            elif vnvl == 0b0100:  # V2-32
                width = 8
                for i in range(qwd):
                    val = [0, 0]
                    if cl >= wl or (i % wl) < cl:
                        val = getnfloat32(buf, width * j + offs, 2)
                        j += 1
                    addroffs = cl * (i // wl) + (i % wl) if cl >= wl else 0
                    vumem[addr + addroffs] = NoeVec4([
                        maybe_mask_value(val[0], 0, i, m),
                        maybe_mask_value(val[1], 1, i, m),
                        maybe_mask_value(0, 2, i, m),
                        maybe_mask_value(0, 3, i, m),
                    ])
            elif vnvl == 0b1000:  # V3-32
                width = 12
                for i in range(qwd):
                    val = [0, 0, 0]
                    if cl >= wl or (i % wl) < cl:
                        val = getnfloat32(buf, width * j + offs, 3)
                        j += 1
                    addroffs = cl * (i // wl) + (i % wl) if cl >= wl else 0
                    vumem[addr + addroffs] = NoeVec4([
                        maybe_mask_value(val[0], 0, i, m),
                        maybe_mask_value(val[1], 1, i, m),
                        maybe_mask_value(val[2], 2, i, m),
                        maybe_mask_value(0, 3, i, m),
                    ])
            elif vnvl == 0b1100:  # V4-32
                width = 16
                for i in range(qwd):
                    val = [0, 0, 0, 0]
                    if cl >= wl or (i % wl) < cl:
                        val = getnfloat32(buf, width * j + offs, 4)
                        j += 1
                    addroffs = cl * (i // wl) + (i % wl) if cl >= wl else 0
                    vumem[addr + addroffs] = NoeVec4([
                        maybe_mask_value(val[0], 0, i, m),
                        maybe_mask_value(val[1], 1, i, m),
                        maybe_mask_value(val[2], 2, i, m),
                        maybe_mask_value(val[3], 3, i, m),
                    ])
            else:
                err('Unsupported unpack vnvl {} at offset {}'.format(hex(vnvl), hex(offs)))
            offs += j * width
        else:
            err('Unrecognized vifcmd {} at offset {}'.format(hex(cmd), hex(offs)))

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()

    basepath = os.path.splitext(rapi.getInputName())[0]
    basename = os.path.splitext(os.path.basename(rapi.getInputName()))[0]

    # Construct the entire node tree recursively.
    startFile = data.find(b'I3D_BIN')
    if startFile == -1:
        return 0
    buf = data[startFile+0x10:]
    rootNode = Node(buf, 0)

    # Traverse node tree and find all nodes of interest.
    materialNodes = rootNode.getChildrenByType(0x25)
    combinedMeshNodes = rootNode.getChildrenByType(0x2D)
    boneNodes = rootNode.getChildrenByType(0x2A)

    # Get all material names. Assume these are the same as texture names.
    materialNames = []
    for materialNode in materialNodes:
        materialOffs = materialNode.children[0].children[0].dataOffs
        nameOffs = getuint32(buf, materialOffs + 0x18) + materialOffs
        materialNames.append(parseName(buf, nameOffs))
    
    # Parse mesh instances attached to bones.
    meshInstances = []
    for boneIndex in range(len(boneNodes)):
        meshInstanceNodes = boneNodes[boneIndex].getChildrenByType(0x59)
        if len(meshInstanceNodes) == 0:
            continue

        def getTransform(buf, offs, ind):
            transformOffs = offs + ind * 0x40
            matrix = NoeMat44()
            for i in range(4):
                matrix[i] = NoeVec4([getfloat32(buf, transformOffs + i * 0x10 + j * 0x4) for j in range(4)])
            #print(matrix)
            return matrix.transpose()#np.matrix(matrix).transpose()

        # Get global transform of current bone.
        transformTableOffs = getuint32(buf, rootNode.dataOffs + 0x14) + rootNode.dataOffs
        baseTransform = getTransform(buf, transformTableOffs, boneIndex)

        for meshInstanceNode in meshInstanceNodes:
            # Parse mesh instance data.
            boneListOffs = getuint32(buf, meshInstanceNode.dataOffs) + meshInstanceNode.dataOffs
            combinedMeshIndex = getuint16(buf, meshInstanceNode.dataOffs + 0x4)
            boneListCount = getuint16(buf, meshInstanceNode.dataOffs + 0x6)
            boneList = getnuint16(buf, boneListOffs, boneListCount)

            combinedMeshNode = combinedMeshNodes[combinedMeshIndex]
            meshInstance = MeshInstance(meshInstanceNode.dataOffs, combinedMeshNode.dataOffs)
            meshInstances.append(meshInstance)

            bindPoseTableOffs = 0
            if combinedMeshNode.children[0].dataOffs > 0:  # Node type 0x46
                # Sadly I can't compute a single transform for the entire combined mesh
                # since different meshes may have different relative bind poses.
                bindPoseTableOffs = getuint32(buf, combinedMeshNode.children[0].dataOffs) + combinedMeshNode.children[0].dataOffs
            
            meshNodes = combinedMeshNode.getChildrenByType(0x4B)
            meshNodes += combinedMeshNode.getChildrenByType(0x4C)
            for meshNode in meshNodes:
                mesh = Mesh(meshNode.dataOffs)
                meshInstance.meshes.append(mesh)
                transform = baseTransform
                if meshNode.dataType == 0x4C and (buf[meshNode.dataOffs + 0x5] & 0x8) > 0:
                    # Use global transform of bone assigned to the instance.
                    boneListIndex = getuint16(buf, meshNode.dataOffs + 0x8)
                    transform = getTransform(buf, transformTableOffs, boneList[boneListIndex])
                
                for submeshNode in meshNode.getChildrenByType(0x4D):
                    materialIndex = buf[submeshNode.dataOffs + 0xC]
                    submesh = Submesh(submeshNode.dataOffs, materialIndex)
                    mesh.submeshes.append(submesh)

                    for submeshPieceNode in submeshNode.getChildrenByType(0x56):
                        submeshPiece = SubmeshPiece(submeshPieceNode.dataOffs)
                        submesh.submeshPieces.append(submeshPiece)

                        vertexWeightNodes = submeshPieceNode.getChildrenByType(0x31)
                        if vertexWeightNodes and bindPoseTableOffs > 0:
                            boneIndex = getuint16(buf, vertexWeightNodes[0].dataOffs + 0x4)
                            # Theoretically, the entire submesh should have the same relative bind pose.
                            # We do this at the submesh level rather than the vertex level since this
                            # is cheaper.
                            # TODO: This does not work for all models, e.g. pcdoll.
                            inverseBindPose = getTransform(buf, bindPoseTableOffs, boneIndex)
                            boneTransform = getTransform(buf, transformTableOffs, boneList[boneIndex])
                            transform = boneTransform * inverseBindPose

                        vertexNode = submeshPieceNode.children[4].children[0]
                        vertexCount = buf[vertexNode.dataOffs + 0x6]
                        if buf[vertexNode.dataOffs + 0x8] == 1:
                            parseVif(buf, vertexNode.dataOffs)
                            for i in range(vertexCount):
                                v = transform * vumem[i]
                                submeshPiece.vtx.append(v)
                        else:
                            for i in range(vertexCount):
                                v = transform * NoeVec4((getnfloat32(buf, vertexNode.dataOffs + i * 0x10 + 0x10, 4)))
                                submeshPiece.vtx.append(v)

                        ind = []
                        # Join indices and texture coordinates across all sub-pieces. There is far too much indentation here.
                        for indexListNode in submeshPieceNode.getChildrenByType(0x47):
                            uvBufferNode = indexListNode.children[1].children[0]
                            uvCount = buf[uvBufferNode.dataOffs + 0x6]
                            if buf[uvBufferNode.dataOffs + 0x8] == 1:
                                parseVif(buf, uvBufferNode.dataOffs)
                                submeshPiece.vt.extend(vumem[:uvCount])
                            else:
                                for i in range(uvCount):
                                    submeshPiece.vt.append(getnfloat32(buf, uvBufferNode.dataOffs + i * 0x10 + 0x10, 4))
                            
                            indOffs = indexListNode.dataOffs
                            indCount = buf[indOffs + 0x5]
                            indOffs += 0x10
                            for i in range(indCount):
                                ind.append(struct.unpack('BBBB', buf[indOffs + i * 4: indOffs + i * 4 + 4]))
                        
                        for i in range(len(ind)):
                            _, ctrl, _, reverse = ind[i]
                            if ctrl == 0x80:
                                continue
                            if reverse:
                                submeshPiece.ind.append([ (ind[i-2][0], i-2), (ind[i-1][0], i-1), (ind[i][0], i) ])
                            else:
                                submeshPiece.ind.append([ (ind[i][0], i), (ind[i-1][0], i-1), (ind[i-2][0], i-2) ])
            

    # Create Mesh
    for meshInstance in meshInstances:
        for mesh in meshInstance.meshes:
            for submesh in mesh.submeshes:
                groupName = '{}_{}_{}_{}'.format(hex(meshInstance.offs)[2:], hex(meshInstance.combinedMeshOffs)[2:], hex(mesh.offs)[2:], hex(submesh.offs)[2:])
                rapi.rpgSetName(groupName)
                if submesh.materialIndex >= 0:
                    rapi.rpgSetMaterial(materialNames[submesh.materialIndex])
                for submeshPiece in submesh.submeshPieces:
                    vbuf, uvbuf = b'', b''
                    
                    for ind in submeshPiece.ind:
                        for i in range(3):
                            vbuf += submeshPiece.vtx[ind[i][0]].toBytes()
                            uvbuf += submeshPiece.vt[ind[i][1]].toBytes()
                    
                    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 16)
                    rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 16)
                    rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, len(vbuf)//16, noesis.RPGEO_TRIANGLE)
            
    mdl = rapi.rpgConstructModel()#NoeModel()#
    mdlList.append(mdl)
    #rapi.setPreviewOption("setAngOfs", "0 -90 0")
    return 1