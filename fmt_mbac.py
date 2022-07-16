from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("MascotCapsule model", ".mbac")
    noesis.setHandlerTypeCheck(handle, mbacCheckType)
    noesis.setHandlerLoadModel(handle, mbacLoadModel)
    noesis.logPopup()
    return 1

MBAC_HEADER = 0x424D
MAGNITUDE = [8, 10, 13, 16]
DIRECTION = [[1,0,0],[0,1,0],[0,0,1],[-1,0,0],[0,-1,0],[0,0,-1]]

def mbacCheckType(data):
    bs = NoeBitStream(data)
    if bs.readUShort() != MBAC_HEADER:
        return 0
    return 1

def mbacLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    vertices, faces, normals, bones, uvs = [], [], [], [], []

    magic, ver = bs.readUShort(), bs.readUShort()
    vformat, nformat, pformat, bformat = [bs.readUByte() for x in range(4)]
    num_vertices, num_polyt3, num_polyt4, num_bones = [bs.readUShort() for x in range(4)]
    num_polyf3, num_polyf4, matcnt, unk21, num_color = [bs.readUShort() for x in range(5)]

    for i in range(unk21):
        unk1, unk2 = bs.readUShort(), bs.readUShort()
        
        for j in range(matcnt):
            unk3, unk4 = bs.readUShort(), bs.readUShort()

    # decode vertices
    unp = Unpacker(bs)
    
    while len(vertices) < num_vertices:
        header = unp.UBit(8)
        magnitude = MAGNITUDE[header >> 6]
        count = (header & 0x3F) + 1

        for i in range(count):
            vertices.append(NoeVec3([unp.Bit(magnitude) for x in range(3)]))
    
    # decode normals
    if nformat:
        unp = Unpacker(bs)
        
        have_normals = 0
        while have_normals < num_vertices:
            x = unp.Bit(7)
            
            if x == -64:
                direction = unp.UBit(3)
                #print('  direction', direction)
                normals.append(NoeVec3(DIRECTION[direction]))
            else:
                x = x / 64
                y = unp.Bit(7) / 64
                z_negative = unp.UBit(1)
                
                if 1 - x * x - y * y >= 0:
                    z = sqrt(1 - x * x - y * y) * (-1 if z_negative else 1)
                else:
                    z = 0
                normals.append(NoeVec3([x, y, z]))
            have_normals += 1
            
    # decode polygons
    unp = Unpacker(bs)
    
    if num_polyf3 + num_polyf4 > 0:
        unk_bits = unp.UBit(8)
        vertex_index_bits = unp.UBit(8)
        color_bits = unp.UBit(8)
        color_id_bits = unp.UBit(8)
        unp.UBit(8)
        
        for i in range(num_color):
            rgb = [unp.UBit(color_bits) for x in range(3)]
            
        for i in range(num_polyf3):
            unknown = unp.UBit(unk_bits)
            a, b, c = [unp.UBit(vertex_index_bits) for x in range(3)]
            color_id = unp.UBit(color_id_bits)
            
            faces += [c, b, a]
            
        for i in range(num_polyf4):
            unknown = unp.UBit(unk_bits)
            a, b, c, d = [unp.UBit(vertex_index_bits) for x in range(4)]
            color_id = unp.UBit(color_id_bits)
            
            faces += [c, b, a, d, b, c]
            
    if num_polyt3 + num_polyt4 > 0:
        uvs = [None]*num_vertices
        unk_bits = unp.UBit(8)
        vertex_index_bits = unp.UBit(8)
        uv_bits = unp.UBit(8)
        somedata = unp.UBit(8)
    
        for i in range(num_polyt3):
            unknown = unp.UBit(unk_bits)
            a, b, c = [unp.UBit(vertex_index_bits) for x in range(3)]
            uv = [unp.UBit(uv_bits) for x in range(6)]
            
            for i,x in enumerate([a, b, c]):
                uvs[x]=(NoeVec3(uv[i*2:i*2+2]+[0]))
            faces += [c, b, a]
            
        for i in range(num_polyt4):
            unknown = unp.UBit(unk_bits)
            a, b, c, d = [unp.UBit(vertex_index_bits) for x in range(4)]
            uv = [unp.UBit(uv_bits) for x in range(8)]
            
            for i,x in enumerate([a, b, c, d]):
                uvs[x]=(NoeVec3(uv[i*2:i*2+2]+[0]))
            faces += [c, b, a, d, b, c]

    # decode bones
    bWeList = []
    bone_vertices_sum = 0
    have_root = False
    
    for i in range(num_bones):
        bone_vertices, parent = bs.readUShort(), bs.readShort()
    
        m = [bs.readShort() for x in range(12)]
        
        vec1 = NoeVec3([x/4096 for x in m[:3]])
        vec2 = NoeVec3([x/4096 for x in m[4:7]])
        vec3 = NoeVec3([x/4096 for x in m[8:11]])
        pos = NoeVec3([m[x] for x in range(3,12,4)])
        
        mtx = NoeMat43([vec1, vec2, vec3, pos])
        
        if parent != -1:
            mtx = mtx*bones[parent].getMatrix()
            
        bones.append(NoeBone(i, "bone_"+str(i), mtx,None,parent))
        #weight
        for x in range(bone_vertices_sum, bone_vertices_sum + bone_vertices):
            vertices[x] = vertices[x]*mtx
            bWeList.append(NoeVertWeight([i], [1.0]))
            
        bone_vertices_sum += bone_vertices
    
    mesh = NoeMesh(faces, vertices, "mesh_0")
    mesh.setWeights(bWeList)
    if uvs: mesh.setUVs(uvs)
    if normals: mesh.setNormals(normals)
    mdl = NoeModel([mesh])
    mdl.setBones(bones)
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial("default","")]))
    mdlList.append(mdl)
    return 1

#square root without math
def sqrt(val):
    return val**(1/2)

#Unpacker
class Unpacker:
    def __init__(self, bs):
        self.bs = bs
        self.havebits = 0
        self.data = 0

    def UBit(self, nbits):
        while nbits > self.havebits:
            self.addbits()

        bits = self.data & ((1 << nbits) - 1)
        self.havebits -= nbits
        self.data >>= nbits
        return bits

    def Bit(self, nbits):
        value = self.UBit(nbits)
        sign = value & (1 << (nbits - 1))

        if sign:
            value -= (1 << nbits)
        return value

    def addbits(self):
        self.data |= self.bs.readUByte() << self.havebits
        self.havebits += 8