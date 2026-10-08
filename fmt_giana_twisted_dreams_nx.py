from inc_noesis import *
import noesis
import rapi
import os
import struct
import math

PLUGIN_NAME = "Giana Sisters: Twisted Dreams NX"


def registerNoesisTypes():
    handle = noesis.register(PLUGIN_NAME, ".nx")
    noesis.setHandlerTypeCheck(handle, gianaCheckType)
    noesis.setHandlerLoadModel(handle, gianaLoadModel)
    return 1


def _u16(data, ofs):
    return data[ofs] | (data[ofs + 1] << 8)


def _half_to_float(data, ofs):
    # Pure Python IEEE-754 binary16 decoder. Avoids depending on struct '<e'
    # support in the embedded Noesis Python runtime.
    h = data[ofs] | (data[ofs + 1] << 8)
    s = -1.0 if (h & 0x8000) else 1.0
    e = (h >> 10) & 0x1F
    m = h & 0x03FF
    if e == 0:
        if m == 0:
            return -0.0 if s < 0.0 else 0.0
        return s * (m / 1024.0) * (2.0 ** -14)
    if e == 31:
        if m == 0:
            return s * float("inf")
        return float("nan")
    return s * (1.0 + m / 1024.0) * (2.0 ** (e - 15))


def _skin_record_valid(data, skinOfs, i):
    p = skinOfs + i * 8
    if p < 0 or p + 8 > len(data):
        return False

    b0 = data[p + 0]
    b1 = data[p + 1]
    b2 = data[p + 2]
    b3 = data[p + 3]
    w0 = data[p + 4]
    w1 = data[p + 5]
    w2 = data[p + 6]
    w3 = data[p + 7]

    if w0 + w1 + w2 + w3 != 255:
        return False

    # 0xFF is valid only as an unused slot.
    if (w0 and b0 == 0xFF) or (w1 and b1 == 0xFF) or \
       (w2 and b2 == 0xFF) or (w3 and b3 == 0xFF):
        return False
    return True


def _infer_mesh_layout(data):
    # The supplied mesh was manually isolated from a larger game resource and
    # has no retained self-describing header. Recover N from the invariant:
    #   N * 32 vertex bytes + N * 8 valid skin bytes + valid u16 triangles.
    size = len(data)
    if size < 256:
        return None

    maxVerts = size // 40
    candidates = []

    for vc in range(16, maxVerts + 1):
        skinOfs = vc * 32
        skinEnd = skinOfs + vc * 8
        if skinEnd + 6 > size:
            break

        probes = (0, 1, 2, 3, vc // 4, vc // 2, (vc * 3) // 4,
                  vc - 4, vc - 3, vc - 2, vc - 1)
        ok = True
        for i in probes:
            if i < 0 or i >= vc:
                continue
            if not _skin_record_valid(data, skinOfs, i):
                ok = False
                break
        if not ok:
            continue

        for i in range(vc):
            if not _skin_record_valid(data, skinOfs, i):
                ok = False
                break
        if not ok:
            continue

        idxOfs = skinEnd
        p = idxOfs
        triCount = 0
        while p + 6 <= size:
            a = _u16(data, p)
            b = _u16(data, p + 2)
            c = _u16(data, p + 4)
            if a >= vc or b >= vc or c >= vc:
                break
            triCount += 1
            p += 6

        if triCount > 0:
            candidates.append((vc, skinOfs, idxOfs, triCount, p))

    if not candidates:
        return None

    # Prefer the split producing the longest coherent triangle list.
    candidates.sort(key=lambda x: (x[3], x[0]), reverse=True)
    return candidates[0]


def gianaCheckType(data):
    layout = _infer_mesh_layout(data)
    if layout is None:
        return 0
    vc, skinOfs, idxOfs, triCount, idxEnd = layout
    return 1 if vc >= 16 and triCount >= 8 else 0


def _find_skeleton_file(meshPath):
    folder = os.path.dirname(meshPath)
    preferred = os.path.join(folder, "rendershape.bin.nx")
    if os.path.isfile(preferred):
        return preferred

    try:
        for fn in os.listdir(folder):
            low = fn.lower()
            if low.endswith(".nx") and "rendershape" in low:
                p = os.path.join(folder, fn)
                if os.path.isfile(p):
                    return p
    except:
        pass
    return None


def _is_ascii_name(raw):
    if not raw:
        return False
    for c in raw:
        if c < 0x20 or c > 0x7E:
            return False
    return True


def _quat_norm_ok(q):
    n = q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3]
    return n > 0.90 and n < 1.10 and math.isfinite(n)


def _parse_skeleton_candidate(data, skelTagOfs):
    # LEKS block:
    #   +0x00 'LEKS'
    #   +0x04 u32 blockSize
    #   +0x08 u16 unknown (0 in supplied sets)
    #   +0x0A u16 boneCount
    #   +0x0C records...
    if skelTagOfs < 0 or skelTagOfs + 12 > len(data):
        return None
    if data[skelTagOfs:skelTagOfs + 4] != b"LEKS":
        return None

    blockSize = struct.unpack_from("<I", data, skelTagOfs + 4)[0]
    unk, boneCount = struct.unpack_from("<HH", data, skelTagOfs + 8)
    if boneCount < 1 or boneCount > 4096:
        return None

    p = skelTagOfs + 12
    bones = []

    for boneIndex in range(boneCount):
        if p + 4 > len(data):
            return None
        nameLen = struct.unpack_from("<I", data, p)[0]
        p += 4
        if nameLen < 1 or nameLen > 256 or p + nameLen + 2 + 56 > len(data):
            return None

        rawName = data[p:p + nameLen]
        if not _is_ascii_name(rawName):
            return None
        name = rawName.decode("ascii")
        p += nameLen

        parent = struct.unpack_from("<h", data, p)[0]
        p += 2
        if boneIndex == 0:
            if parent != -1:
                return None
        else:
            if parent < 0 or parent >= boneIndex:
                return None

        vals = struct.unpack_from("<14f", data, p)
        p += 56
        if not all(math.isfinite(v) for v in vals):
            return None
        if not _quat_norm_ok(vals[3:7]) or not _quat_norm_ok(vals[10:14]):
            return None

        bones.append({
            "index": boneIndex,
            "name": name,
            "parent": parent,
            "invPos": vals[0:3],
            "invQuat": vals[3:7],
            "localPos": vals[7:10],
            "localQuat": vals[10:14],
        })

    recordEnd = p

    # The matching BBKS block occurs immediately after the SKEL record block,
    # with only small terminator/alignment data in between. Require exact
    # payload length boneCount * 24 to avoid accidental tag matches.
    bbTag = -1
    searchEnd = min(len(data), recordEnd + 96)
    q = recordEnd
    while True:
        q = data.find(b"BBKS", q, searchEnd)
        if q < 0:
            break
        if q + 8 <= len(data):
            bbSize = struct.unpack_from("<I", data, q + 4)[0]
            if bbSize == boneCount * 24 and q + 8 + bbSize <= len(data):
                bbTag = q
                break
        q += 1

    bboxes = None
    if bbTag >= 0:
        bboxes = []
        pbb = bbTag + 8
        for i in range(boneCount):
            bboxes.append(struct.unpack_from("<6f", data, pbb + i * 24))

    return {
        "tagOfs": skelTagOfs,
        "blockSize": blockSize,
        "unknown": unk,
        "count": boneCount,
        "recordEnd": recordEnd,
        "bones": bones,
        "bbTagOfs": bbTag,
        "bboxes": bboxes,
        "score": -1.0,
        "weightedScore": -1.0,
    }


def _scan_skeleton_candidates(data):
    candidates = []
    pos = 0

    # In the supplied container every real skeleton is introduced by VBIN and
    # its LEKS block begins exactly 12 bytes later. This avoids false positives
    # from ASCII-like bytes inside float payloads.
    while True:
        vb = data.find(b"VBIN", pos)
        if vb < 0:
            break
        skelOfs = vb + 12
        c = _parse_skeleton_candidate(data, skelOfs)
        if c is not None:
            c["vbinOfs"] = vb
            candidates.append(c)
        pos = vb + 1

    return candidates


def _row_quat_transform_point(p, q, t):
    # Matches the row-vector convention used by Noesis NoeMat43 and by the
    # inverse-bind transform stored in this file.
    x, y, z = p
    qx, qy, qz, qw = q

    m00 = 1.0 - 2.0 * (qy * qy + qz * qz)
    m01 = 2.0 * (qx * qy - qz * qw)
    m02 = 2.0 * (qx * qz + qy * qw)

    m10 = 2.0 * (qx * qy + qz * qw)
    m11 = 1.0 - 2.0 * (qx * qx + qz * qz)
    m12 = 2.0 * (qy * qz - qx * qw)

    m20 = 2.0 * (qx * qz - qy * qw)
    m21 = 2.0 * (qy * qz + qx * qw)
    m22 = 1.0 - 2.0 * (qx * qx + qy * qy)

    return (
        x * m00 + y * m10 + z * m20 + t[0],
        x * m01 + y * m11 + z * m21 + t[1],
        x * m02 + y * m12 + z * m22 + t[2],
    )



def _read_cstr(data, ofs):
    if ofs < 0 or ofs >= len(data):
        return None
    end = data.find(b"\x00", ofs)
    if end < 0:
        end = len(data)
    raw = data[ofs:end]
    try:
        return raw.decode("ascii")
    except:
        return None


def _parse_type_directory(data):
    # File header:
    #   u32 stringBase
    #   u32 typeCount
    #   typeCount * {
    #       u32 typeNameOffset;   // relative to stringBase
    #       u32 sectionOffset;
    #       u32 typeHash;
    #   }
    if len(data) < 8:
        return None

    stringBase, typeCount = struct.unpack_from("<II", data, 0)
    if typeCount < 1 or typeCount > 256:
        return None
    if stringBase < 8 + typeCount * 12 or stringBase >= len(data):
        return None

    sections = {}
    ordered = []

    for i in range(typeCount):
        p = 8 + i * 12
        if p + 12 > len(data):
            return None

        nameRel, sectionOfs, typeHash = struct.unpack_from("<III", data, p)
        name = _read_cstr(data, stringBase + nameRel)
        if not name or sectionOfs >= len(data):
            return None

        item = {
            "name": name,
            "nameRel": nameRel,
            "offset": sectionOfs,
            "hash": typeHash,
        }
        sections[name] = item
        ordered.append(item)

    ordered.sort(key=lambda x: x["offset"])
    for i in range(len(ordered)):
        ordered[i]["end"] = ordered[i + 1]["offset"] if i + 1 < len(ordered) else len(data)

    return {
        "stringBase": stringBase,
        "sections": sections,
        "ordered": ordered,
    }


def _parse_ref_record_section(data, directory, name, expectedRecordSize):
    sec = directory["sections"].get(name)
    if sec is None:
        return None

    s = sec["offset"]
    e = sec["end"]
    if s + 16 > e:
        return None

    count, unk, dataRel, headerSize = struct.unpack_from("<IIII", data, s)
    dataStart = s + dataRel

    if count < 0 or dataStart < s + 16 or dataStart > e:
        return None
    if (dataRel - 16) < 0 or ((dataRel - 16) & 7) != 0:
        return None

    refCount = (dataRel - 16) // 8
    refs = []
    p = s + 16
    for i in range(refCount):
        refs.append(struct.unpack_from("<Q", data, p + i * 8)[0])

    if count == 0:
        recordSize = expectedRecordSize
        records = []
    else:
        dataBytes = e - dataStart
        if dataBytes % count != 0:
            return None
        recordSize = dataBytes // count
        if recordSize != expectedRecordSize:
            return None

        records = []
        for i in range(count):
            records.append(data[dataStart + i * recordSize:dataStart + (i + 1) * recordSize])

    return {
        "name": name,
        "offset": s,
        "end": e,
        "count": count,
        "unknown": unk,
        "dataRel": dataRel,
        "headerSize": headerSize,
        "refs": refs,
        "recordSize": recordSize,
        "dataStart": dataStart,
        "records": records,
    }


def _parse_skeleton_entry_section(data, directory):
    sec = directory["sections"].get("SkeletonEntry")
    skd = directory["sections"].get("SkeletonData")
    if sec is None or skd is None:
        return None

    s = sec["offset"]
    e = sec["end"]
    if s + 12 > e:
        return None

    count, unk, pairRel = struct.unpack_from("<III", data, s)
    if count < 1 or count > 4096:
        return None
    if pairRel < 12 or s + pairRel + count * 8 > e:
        return None

    # SkeletonEntry offsets are relative to the SkeletonData payload base.
    # SkeletonData's fourth u32 is the payload offset (0x10 in this file).
    sd = skd["offset"]
    if sd + 16 > len(data):
        return None
    sdCount, sdUnk, sdSize, sdPayloadRel = struct.unpack_from("<IIII", data, sd)
    payloadBase = sd + sdPayloadRel
    if payloadBase < sd or payloadBase > skd["end"]:
        return None

    entries = []
    for i in range(count):
        relOfs, size = struct.unpack_from("<II", data, s + pairRel + i * 8)
        absOfs = payloadBase + relOfs
        if absOfs < payloadBase or absOfs + size > len(data):
            return None

        # Every entry in the supplied file starts with a 12-byte VBIN wrapper,
        # then LEKS.
        leksOfs = absOfs + 12
        c = _parse_skeleton_candidate(data, leksOfs)
        if c is None:
            return None

        c["entryIndex"] = i
        c["vbinOfs"] = absOfs
        c["entryRelOfs"] = relOfs
        c["entrySize"] = size
        entries.append(c)

    return {
        "count": count,
        "entries": entries,
        "payloadBase": payloadBase,
        "sectionOffset": s,
    }


def _parse_render_metadata(data):
    directory = _parse_type_directory(data)
    if directory is None:
        return None

    # These fixed record sizes are derived from section boundaries in the raw
    # file, not from the old STMF template.
    shape = _parse_ref_record_section(data, directory, "ShapeEntry", 76)
    lod = _parse_ref_record_section(data, directory, "LodEntry", 12)
    layer = _parse_ref_record_section(data, directory, "LayerEntry", 16)
    surface = _parse_ref_record_section(data, directory, "SurfaceEntry", 52)
    skeleton = _parse_skeleton_entry_section(data, directory)

    if shape is None or lod is None or layer is None or surface is None or skeleton is None:
        return None

    return {
        "directory": directory,
        "shape": shape,
        "lod": lod,
        "layer": layer,
        "surface": surface,
        "skeleton": skeleton,
    }


def _ref_slice(refs, byteOfs, count):
    if byteOfs & 7:
        return None
    first = byteOfs // 8
    if first < 0 or count < 0 or first + count > len(refs):
        return None
    return refs[first:first + count]


def _shape_info(meta, shapeIndex):
    shapeSec = meta["shape"]
    if shapeIndex < 0 or shapeIndex >= shapeSec["count"]:
        return None

    rec = shapeSec["records"][shapeIndex]
    v = struct.unpack_from("<19I", rec, 0)

    # ShapeEntry:
    #   +0x00 u32 entryIndex
    #   +0x04 u32 nameOffset (relative to global stringBase)
    #   +0x08 u32 0
    #   +0x0C u32 flags/type
    #   +0x10 u32 lodRefOffset (byte offset in LodEntry ref table)
    #   +0x14 u32 0
    #   +0x18 u32 lodCount
    #   +0x1C float3 bboxMin
    #   +0x28 float3 bboxMax
    #   +0x34 i32 skeletonEntryIndex (-1 if none)
    #   remaining fields are currently not required here.
    data = meta["_data"]
    name = _read_cstr(data, meta["directory"]["stringBase"] + v[1])

    bbox = struct.unpack_from("<6f", rec, 7 * 4)
    skeletonIndex = struct.unpack_from("<i", rec, 13 * 4)[0]

    lodRefs = _ref_slice(meta["lod"]["refs"], v[4], v[6])
    if lodRefs is None:
        return None

    lodIndices = []
    layerIndices = []
    surfaceIndices = []

    for lodIndex64 in lodRefs:
        lodIndex = int(lodIndex64)
        if lodIndex < 0 or lodIndex >= meta["lod"]["count"]:
            return None
        lodIndices.append(lodIndex)

        lr = struct.unpack_from("<III", meta["lod"]["records"][lodIndex], 0)
        layerRefs = _ref_slice(meta["layer"]["refs"], lr[0], lr[2])
        if layerRefs is None:
            return None

        for layerIndex64 in layerRefs:
            layerIndex = int(layerIndex64)
            if layerIndex < 0 or layerIndex >= meta["layer"]["count"]:
                return None
            layerIndices.append(layerIndex)

            lay = struct.unpack_from("<IIII", meta["layer"]["records"][layerIndex], 0)
            surfRefs = _ref_slice(meta["surface"]["refs"], lay[1], lay[3])
            if surfRefs is None:
                return None

            for surfaceIndex64 in surfRefs:
                surfaceIndex = int(surfaceIndex64)
                if surfaceIndex < 0 or surfaceIndex >= meta["surface"]["count"]:
                    return None
                surfaceIndices.append(surfaceIndex)

    surfaces = []
    for surfaceIndex in surfaceIndices:
        sv = struct.unpack_from("<13I", meta["surface"]["records"][surfaceIndex], 0)
        surfaces.append({
            "index": surfaceIndex,
            "firstIndex": sv[8],
            "triangleCount": sv[9],
            "raw": sv,
        })

    return {
        "index": shapeIndex,
        "name": name,
        "flags": v[3],
        "lodRefOffset": v[4],
        "lodCount": v[6],
        "bbox": bbox,
        "skeletonIndex": skeletonIndex,
        "lodIndices": lodIndices,
        "layerIndices": layerIndices,
        "surfaceIndices": surfaceIndices,
        "surfaces": surfaces,
        "raw": v,
    }


def _mesh_bbox(data, vc):
    mn = [1.0e30, 1.0e30, 1.0e30]
    mx = [-1.0e30, -1.0e30, -1.0e30]

    for i in range(vc):
        p = i * 32
        x = _half_to_float(data, p + 0)
        y = _half_to_float(data, p + 2)
        z = _half_to_float(data, p + 4)

        if x < mn[0]: mn[0] = x
        if y < mn[1]: mn[1] = y
        if z < mn[2]: mn[2] = z
        if x > mx[0]: mx[0] = x
        if y > mx[1]: mx[1] = y
        if z > mx[2]: mx[2] = z

    return (mn[0], mn[1], mn[2], mx[0], mx[1], mx[2])


def _surface_layout_matches(shape, triCount):
    if not shape["surfaces"]:
        return False

    # SurfaceEntry.firstIndex is measured in u16 index elements, not bytes.
    # Surfaces belonging to one LOD cover one contiguous triangle list.
    expected = 0
    for s in shape["surfaces"]:
        if s["firstIndex"] != expected:
            return False
        expected += s["triangleCount"] * 3

    return expected == triCount * 3


def _bbox_matches(meshBBox, shapeBBox):
    # ShapeEntry bbox is stored in float32 while vertex positions are half.
    # A small absolute tolerance accounts for half-float quantization and the
    # slightly expanded authored bounds. This is an equality check, not a
    # skeleton quality score.
    eps = 0.10
    for i in range(6):
        if abs(meshBBox[i] - shapeBBox[i]) > eps:
            return False
    return True


def _select_shape_direct(meshData, vc, triCount, renderData):
    meta = _parse_render_metadata(renderData)
    if meta is None:
        print("Giana NX: failed to parse render metadata graph.")
        return None, None

    meta["_data"] = renderData
    bbox = _mesh_bbox(meshData, vc)

    byIndexLayout = []
    exact = []

    for i in range(meta["shape"]["count"]):
        sh = _shape_info(meta, i)
        if sh is None:
            continue
        if sh["skeletonIndex"] < 0:
            continue
        if sh["skeletonIndex"] >= meta["skeleton"]["count"]:
            continue
        if not _surface_layout_matches(sh, triCount):
            continue

        byIndexLayout.append(sh)
        if _bbox_matches(bbox, sh["bbox"]):
            exact.append(sh)

    candidates = exact if exact else byIndexLayout
    if not candidates:
        print("Giana NX: no ShapeEntry matches mesh index layout.")
        return meta, None

    # The isolated raw mesh has lost its original owning ShapeEntry ID.
    # Aliases may therefore remain (in this sample: giana and maria), but they
    # describe identical geometry and point to the same SkeletonEntry. We only
    # accept the direct metadata path if all remaining aliases agree.
    skelSet = {}
    for sh in candidates:
        skelSet[sh["skeletonIndex"]] = 1

    print("Giana NX: metadata ShapeEntry candidates:")
    for sh in candidates:
        surfText = ",".join(
            ["%d:%d@%d" % (s["index"], s["triangleCount"], s["firstIndex"])
             for s in sh["surfaces"]])
        print("  Shape[%d] '%s' skel=%d lod=%s layer=%s surfaces=%s" %
              (sh["index"], sh["name"], sh["skeletonIndex"],
               str(sh["lodIndices"]), str(sh["layerIndices"]), surfText))

    if len(skelSet) != 1:
        print("Giana NX: isolated mesh matches multiple ShapeEntries with different skeleton refs.")
        return meta, None

    selectedSkel = list(skelSet.keys())[0]
    # Prefer the first exact metadata alias only for naming/logging. Skeleton
    # selection itself comes from the shared explicit skeletonEntryIndex.
    selectedShape = candidates[0]

    print("Giana NX: direct metadata selection -> SkeletonEntry[%d]" % selectedSkel)
    return meta, selectedShape


def _load_matching_skeleton(meshData, vc, skinOfs, triCount, meshPath):
    skelPath = _find_skeleton_file(meshPath)
    if skelPath is None:
        print("Giana NX: rendershape.bin.nx not found; mesh will be unskinned.")
        return [], None

    try:
        renderData = open(skelPath, "rb").read()
    except Exception as e:
        print("Giana NX: failed to read rendershape file:", e)
        return [], None

    meta, shape = _select_shape_direct(meshData, vc, triCount, renderData)
    if meta is None or shape is None:
        print("Giana NX: direct ShapeEntry -> SkeletonEntry resolution failed.")
        return [], None

    skelIndex = shape["skeletonIndex"]
    c = meta["skeleton"]["entries"][skelIndex]

    print("Giana NX: ShapeEntry[%d] '%s' -> SkeletonEntry[%d]" %
          (shape["index"], shape["name"], skelIndex))
    print("Giana NX: SkeletonEntry[%d] relOfs=0x%X size=0x%X -> VBIN@0x%X LEKS@0x%X bones=%d" %
          (skelIndex, c["entryRelOfs"], c["entrySize"],
           c["vbinOfs"], c["tagOfs"], c["count"]))

    bones = _candidate_to_noesis_bones(c)
    return bones, shape


def _candidate_to_noesis_bones(c):
    # Preferred path: pair A is stored inverse GLOBAL bind. Invert it directly
    # and avoid any hierarchy/multiplication ambiguity.
    try:
        out = []
        for b in c["bones"]:
            invMat = NoeQuat(b["invQuat"]).toMat43()
            invMat[3] = NoeVec3(b["invPos"])
            globalBind = invMat.inverse()
            out.append(NoeBone(b["index"], b["name"], globalBind, None, b["parent"]))
        return out
    except Exception as e:
        print("Giana NX: direct inverse-bind construction failed; using local-bind fallback:", e)

    # Fallback for unusual Noesis runtimes: pair B is verified local bind.
    localBones = []
    for b in c["bones"]:
        localMat = NoeQuat(b["localQuat"]).toMat43()
        localMat[3] = NoeVec3(b["localPos"])
        localBones.append(NoeBone(b["index"], b["name"], localMat, None, b["parent"]))
    try:
        return rapi.multiplyBones(localBones)
    except Exception as e:
        print("Giana NX: multiplyBones fallback failed; returning local matrices:", e)
        return localBones


def _build_skin_buffers(data, vc, skinOfs, boneCount):
    # Direct mapping is verified from raw data:
    #   raw skin index N -> skeleton bone N
    # No bone map/remap is applied.
    idxOut = bytearray(vc * 8)       # 4 * u16
    weightOut = bytearray(vc * 16)  # 4 * float32

    ffFixed = 0
    activeOutOfRange = 0

    for i in range(vc):
        p = skinOfs + i * 8
        for k in range(4):
            bi = data[p + k]
            bw = data[p + 4 + k]

            if bi == 0xFF and bw == 0:
                bi = 0
                ffFixed += 1

            if bw != 0 and boneCount > 0 and bi >= boneCount:
                activeOutOfRange += 1
                bi = 0
                bw = 0

            struct.pack_into("<H", idxOut, i * 8 + k * 2, bi)
            struct.pack_into("<f", weightOut, i * 16 + k * 4,
                             float(bw) / 255.0)

    print("Giana NX: direct skin mapping; sanitized unused FF slots=%d, active out-of-range=%d" %
          (ffFixed, activeOutOfRange))
    return bytes(idxOut), bytes(weightOut)


def gianaLoadModel(data, mdlList):
    layout = _infer_mesh_layout(data)
    if layout is None:
        return 0

    vc, skinOfs, idxOfs, triCount, idxEnd = layout
    idxCount = triCount * 3

    print("Giana NX: vertices=%d stride=32 skinOfs=0x%X indexOfs=0x%X triangles=%d indexEnd=0x%X trailer=%d" %
          (vc, skinOfs, idxOfs, triCount, idxEnd, len(data) - idxEnd))

    meshPath = rapi.getInputName()
    bones, shapeInfo = _load_matching_skeleton(data, vc, skinOfs, triCount, meshPath)

    vbuf = data[:skinOfs]
    ibuf = data[idxOfs:idxEnd]
    boneIdx, boneWgt = _build_skin_buffers(data, vc, skinOfs, len(bones))

    ctx = rapi.rpgCreateContext()

    rapi.rpgBindPositionBufferOfs(vbuf, noesis.RPGEODATA_HALFFLOAT, 32, 0)
    rapi.rpgBindNormalBufferOfs(vbuf, noesis.RPGEODATA_HALFFLOAT, 32, 8)
    rapi.rpgBindUV1BufferOfs(vbuf, noesis.RPGEODATA_HALFFLOAT, 32, 16)

    # The second UV pair is byte-for-byte identical to UV0 in the supplied
    # sample, but bind it as UV2 because the raw layout clearly contains it.
    try:
        rapi.rpgBindUV2BufferOfs(vbuf, noesis.RPGEODATA_HALFFLOAT, 32, 20)
    except:
        pass

    if bones:
        # IMPORTANT: no rpgSetBoneMap here. Raw skin indices have been proven
        # against inverse-bind matrices + per-bone local BBKS to address the
        # selected skeleton directly.
        rapi.rpgBindBoneIndexBuffer(boneIdx, noesis.RPGEODATA_USHORT, 8, 4)
        rapi.rpgBindBoneWeightBuffer(boneWgt, noesis.RPGEODATA_FLOAT, 16, 4)

    rapi.rpgSetName(shapeInfo["name"] if shapeInfo is not None and shapeInfo["name"] else "giana_mesh")
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, idxCount,
                            noesis.RPGEO_TRIANGLE, 1)

    mdl = rapi.rpgConstructModel()
    if bones:
        mdl.setBones(bones)
    mdlList.append(mdl)

    rapi.rpgClearBufferBinds()
    return 1
