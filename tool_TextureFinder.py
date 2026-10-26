#by Durik256
#Texture Finder - extended Noesis texture decoder support
#
#Install:
#  Drop this script to '..\\Noesis\\Plugins\\Python'
#  Tools > Display Plugin Tools (once)
#  Tools > Texture Finder

from inc_noesis import *
import os
from ctypes import *
import noewin


# -----------------------------------------------------------------------------
# Format presets
# -----------------------------------------------------------------------------
# imageDecodeRaw itself is not limited to these presets. The format combobox is
# editable while RAW is selected, so any valid Noesis raw format string can be
# typed manually (for example: b5g6r5, a1r5g5b5, p1r7p1g7p1b7p1a7, etc.).

RAW_FORMATS = [
    'r8g8b8a8', 'b8g8r8a8', 'a8r8g8b8', 'a8b8g8r8',
    'r8g8b8', 'b8g8r8',
    'r10g10b10a2', 'a2r10g10b10',
    'r5g6b5', 'b5g6r5',
    'r5g5b5a1', 'a1r5g5b5', 'b5g5r5a1', 'a1b5g5r5',
    'r4g4b4a4', 'a4r4g4b4', 'b4g4r4a4', 'a4b4g4r4',
    'r3g3b2', 'b2g3r3',
    'r2g2b2a2', 'a2r2g2b2',
    'r16g16b16a16', 'r16g16b16', 'r16g16', 'r16',
    'r8g8', 'r8', 'a8'
]

# name : (Noesis constant name, blockWidth, blockHeight, blockBytes)
BC_FORMATS = {
    'DXT1':           ('NOESISTEX_DXT1', 4, 4, 8),
    'DXT1_NORMAL':    ('FOURCC_DXT1NORMAL', 4, 4, 8),
    'DXT3':           ('NOESISTEX_DXT3', 4, 4, 16),
    'DXT5':           ('NOESISTEX_DXT5', 4, 4, 16),
    'BC1':            ('FOURCC_BC1', 4, 4, 8),
    'BC2':            ('FOURCC_BC2', 4, 4, 16),
    'BC3':            ('FOURCC_BC3', 4, 4, 16),
    'BC4':            ('FOURCC_BC4', 4, 4, 8),
    'BC5':            ('FOURCC_BC5', 4, 4, 16),
    'BC6H':           ('FOURCC_BC6H', 4, 4, 16),
    'BC6S':           ('FOURCC_BC6S', 4, 4, 16),
    'BC7':            ('FOURCC_BC7', 4, 4, 16),
    'ATI1 / BC4':     ('FOURCC_ATI1', 4, 4, 8),
    'ATI2 / BC5':     ('FOURCC_ATI2', 4, 4, 16)
}

BC_FORMAT_ORDER = [
    'DXT1', 'DXT1_NORMAL', 'DXT3', 'DXT5',
    'BC1', 'BC2', 'BC3', 'BC4', 'BC5', 'BC6H', 'BC6S', 'BC7',
    'ATI1 / BC4', 'ATI2 / BC5'
]

# name : (format string for imageDecodeETC, block bytes)
ETC_FORMATS = {
    'EAC R11':          ('R', 8),
    'EAC RG11':         ('RG', 16),
    'EAC R11 SIGNED':   ('Rs', 8),
    'EAC RG11 SIGNED':  ('RGs', 16),
    'ETC2 RGB8':        ('RGB', 8),
    'ETC1 RGB8':        ('RGB1', 8),
    'ETC2 sRGB8':       ('sRGB', 8),
    'ETC2 RGBA8':       ('RGBA', 16),
    'ETC2 sRGBA8':      ('sRGBA', 16),
    'ETC2 RGB8A1':      ('RGBA1', 8),
    'ETC2 sRGB8A1':     ('sRGBA1', 8)
}

ETC_FORMAT_ORDER = [
    'ETC1 RGB8',
    'ETC2 RGB8', 'ETC2 sRGB8', 'ETC2 RGBA8', 'ETC2 sRGBA8',
    'ETC2 RGB8A1', 'ETC2 sRGB8A1',
    'EAC R11', 'EAC RG11', 'EAC R11 SIGNED', 'EAC RG11 SIGNED'
]

# name : (bits per pixel, PVRTC flags)
# PVRTC2 uses the optional flags argument exposed by current Noesis builds.
PVRTC_FORMATS = {
    'PVRTC1 2bpp': (2, 0),
    'PVRTC1 4bpp': (4, 0),
    'PVRTC2 2bpp': (2, 'PVRTC_DECODE_PVRTC2'),
    'PVRTC2 4bpp': (4, 'PVRTC_DECODE_PVRTC2')
}

PVRTC_FORMAT_ORDER = [
    'PVRTC1 2bpp', 'PVRTC1 4bpp',
    'PVRTC2 2bpp', 'PVRTC2 4bpp'
]

ASTC_BLOCKS = [
    (4, 4), (5, 4), (5, 5), (6, 5), (6, 6),
    (8, 5), (8, 6), (8, 8),
    (10, 5), (10, 6), (10, 8), (10, 10),
    (12, 10), (12, 12)
]
ASTC_FORMAT_ORDER = ['ASTC %ix%i' % (bw, bh) for bw, bh in ASTC_BLOCKS]

SPECIAL_FORMAT_ORDER = [
    'PICA200 ETC1',
    'PICA200 ETC1A4',
    'JAGUAR CRY16'
]

FORMAT_FAMILIES = [
    ('RAW / custom', RAW_FORMATS),
    ('BC / DXT', BC_FORMAT_ORDER),
    ('ETC / EAC', ETC_FORMAT_ORDER),
    ('PVRTC', PVRTC_FORMAT_ORDER),
    ('ASTC 2D', ASTC_FORMAT_ORDER),
    ('PICA / Jaguar', SPECIAL_FORMAT_ORDER)
]


FilePath = ''


def registerNoesisTypes():
    handle = noesis.registerTool('&Texture Finder', TextureFinderMethod)
    handle = noesis.register('Texture Finder', '.TextureFinder')
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    noesis.setHandlerWriteRGBA(handle, WriteRGBA)
    return 1


def CheckType(data):
    if data[:4] == b'TEX ' or data[:4] == b'TEMP':
        return 1
    return 0


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def divCeil(a, b):
    if b <= 0:
        return 0
    return (a + b - 1) // b


def parseFormat(fmt):
    # Raw Noesis format strings contain component bit widths. Padding (p) is
    # counted as well because it occupies source bits too.
    try:
        x = ''.join(c if c.isdigit() else ' ' for c in fmt)
        values = [int(i) for i in x.split()]
        return sum(values)
    except:
        print('[TextureFinder] Error parsing raw format:', fmt)
        return 0


def toInt(s, n='value'):
    try:
        return int(s)
    except:
        print('[TextureFinder] Error converting', n, ':', s)
        return 0


def getNoesisConst(name):
    try:
        return getattr(noesis, name)
    except:
        noesis.doException('This Noesis build does not expose constant: ' + name)
        return 0


def getFormatInfo(fmt):
    # Returns a tuple whose first item is the decoder mode.
    if fmt in BC_FORMATS:
        constName, bw, bh, blockBytes = BC_FORMATS[fmt]
        return ('bc', constName, bw, bh, blockBytes)

    if fmt in ETC_FORMATS:
        etcFmt, blockBytes = ETC_FORMATS[fmt]
        return ('etc', etcFmt, 4, 4, blockBytes)

    if fmt in PVRTC_FORMATS:
        bpp, flagName = PVRTC_FORMATS[fmt]
        return ('pvrtc', bpp, flagName)

    if fmt.startswith('ASTC '):
        try:
            block = fmt[5:].lower().split('x')
            bw = int(block[0])
            bh = int(block[1])
            if (bw, bh) in ASTC_BLOCKS:
                return ('astc', bw, bh, 1)
        except:
            pass

    if fmt == 'PICA200 ETC1':
        return ('pica', 0, 4, 4, 8)
    if fmt == 'PICA200 ETC1A4':
        return ('pica', 1, 4, 4, 16)
    if fmt == 'JAGUAR CRY16':
        return ('jaguarcry', 16)

    # Anything not recognized as a compressed preset is intentionally treated
    # as a raw Noesis format string. This is what keeps custom formats working.
    return ('raw', parseFormat(fmt))


def isRawFormat(fmt):
    return getFormatInfo(fmt)[0] == 'raw'


def getPayloadSize(w, h, fmt, pal, bpp):
    if w <= 0 or h <= 0:
        return 0

    if pal:
        return divCeil(w * h * bpp, 8)

    info = getFormatInfo(fmt)
    mode = info[0]

    if mode == 'raw':
        bits = info[1]
        return divCeil(w * h * bits, 8)

    if mode == 'bc':
        return divCeil(w, info[2]) * divCeil(h, info[3]) * info[4]

    if mode == 'etc':
        return divCeil(w, 4) * divCeil(h, 4) * info[4]

    if mode == 'astc':
        return divCeil(w, info[1]) * divCeil(h, info[2]) * 16

    if mode == 'pica':
        return divCeil(w, 4) * divCeil(h, 4) * info[4]

    if mode == 'pvrtc':
        bits = info[1]
        # PVRTC has a minimum 2x2 block footprint.
        minW = 16 if bits == 2 else 8
        minH = 8
        useW = max(w, minW)
        useH = max(h, minH)
        return divCeil(useW * useH * bits, 8)

    if mode == 'jaguarcry':
        return w * h * 2

    return 0


def getStoredSize(w, h, fmt, pal, bpp, skew):
    payload = getPayloadSize(w, h, fmt, pal, bpp)
    info = getFormatInfo(fmt)

    # Skew is defined as extra bytes after each logical scanline and is useful
    # for linear raw/indexed data. It is not meaningful for block compression.
    if skew > 0 and (pal or info[0] == 'raw'):
        bits = bpp if pal else info[1]
        rowBytes = divCeil(w * bits, 8)
        return (rowBytes + skew) * h

    return payload


def findMaxHeight(available, w, fmt, pal, bpp, skew):
    if available <= 0 or w <= 0:
        return 0

    info = getFormatInfo(fmt)
    if pal or info[0] == 'raw':
        bits = bpp if pal else info[1]
        rowBytes = divCeil(w * bits, 8) + max(skew, 0)
        return available // rowBytes if rowBytes > 0 else 0

    # Generic binary search also works for block formats and PVRTC minimums.
    low = 0
    high = 1
    while high < 0x100000 and getStoredSize(w, high, fmt, pal, bpp, skew) <= available:
        high *= 2

    if high > 0x100000:
        high = 0x100000

    while low + 1 < high:
        mid = (low + high) // 2
        if getStoredSize(w, mid, fmt, pal, bpp, skew) <= available:
            low = mid
        else:
            high = mid
    return low


def readPadded(bs, size, padByte=b'\xFF'):
    if size <= 0:
        return b''
    left = bs.fileSize - bs.tell()
    readSize = size if left >= size else max(left, 0)
    data = bs.readBytes(readSize)
    if len(data) < size:
        data += padByte * (size - len(data))
    return data


def readTexturePayload(bs, w, h, fmt, pal, bpp, skew):
    info = getFormatInfo(fmt)

    if skew > 0 and (pal or info[0] == 'raw'):
        bits = bpp if pal else info[1]
        rowBytes = divCeil(w * bits, 8)
        out = bytearray()
        for y in range(h):
            row = readPadded(bs, rowBytes)
            out += row
            bs.seek(skew, NOESEEK_REL)
        return bytes(out)

    payloadSize = getPayloadSize(w, h, fmt, pal, bpp)
    return readPadded(bs, payloadSize)


def untwiddleLinearData(data, w, h, bits, platform):
    if platform == 'PSP':
        return rapi.imageUntwiddlePSP(data, w, h, bits)
    if platform == 'PS2':
        if bits not in (4, 8, 16, 32):
            print('[TextureFinder] PS2 untwiddle requires 4/8/16/32 bpp; skipped for', bits)
            return data
        return rapi.imageUntwiddlePS2(data, w, h, bits)
    return data


def decodeTexture(data, w, h, fmt):
    info = getFormatInfo(fmt)
    mode = info[0]

    if mode == 'raw':
        if info[1] <= 0:
            noesis.doException('Invalid raw texture format: ' + fmt)
        return rapi.imageDecodeRaw(data, w, h, fmt)

    if mode == 'bc':
        texFmt = getNoesisConst(info[1])
        return rapi.imageDecodeDXT(data, w, h, texFmt)

    if mode == 'etc':
        return rapi.imageDecodeETC(data, w, h, info[1])

    if mode == 'astc':
        return rapi.imageDecodeASTC(data, info[1], info[2], 1, w, h, 1)

    if mode == 'pvrtc':
        bpp = info[1]
        flagName = info[2]
        if flagName:
            flags = getNoesisConst(flagName)
            try:
                return rapi.imageDecodePVRTC(data, w, h, bpp, flags)
            except TypeError:
                noesis.doException('PVRTC2 requires a Noesis build with PVRTC decode flags support.')
        return rapi.imageDecodePVRTC(data, w, h, bpp)

    if mode == 'pica':
        return rapi.imageDecodePICA200ETC1(data, w, h, info[1])

    if mode == 'jaguarcry':
        return rapi.imageJaguarCRYToRGBA(data, 0)

    noesis.doException('Unsupported Texture Finder decoder: ' + fmt)
    return None


# -----------------------------------------------------------------------------
# Texture loader
# -----------------------------------------------------------------------------

def LoadRGBA(data, texList):
    global FilePath
    name = rapi.getInputName()

    try:
        if data[:4] == b'TEX ':
            bs = NoeBitStream(data)
            bs.seek(4)
            w, h = bs.read('2I')
            rgba = rapi.imageDecodeRaw(data[12:], w, h, 'r8g8b8a8')
            texList.append(NoeTexture(name, w, h, rgba, noesis.NOESISTEX_RGBA32))
            return 1

        arg = data.decode().split(';')
        if len(arg) < 15:
            print('[TextureFinder] Invalid TEMP descriptor.')
            return 0

        ofs = toInt(arg[1], 'offset')
        skw = toInt(arg[2], 'skew')
        pofs = toInt(arg[3], 'palette offset / mipMap')
        w = toInt(arg[4], 'width')
        requestedH = arg[5]
        fmt = arg[6]
        bpp = toInt(arg[7], 'palette bpp')
        pstp = arg[8]
        fw = toInt(arg[9], 'flip X')
        fh = toInt(arg[10], 'flip Y')
        pal = toInt(arg[11], 'palette')
        mip = toInt(arg[12], 'mipMap')
        flg = toInt(arg[13], 'decode flag')
        swzl = toInt(arg[14], 'swizzle')

        if not os.path.exists(FilePath):
            print('[TextureFinder] Source file not found:', FilePath)
            return 0
        if w <= 0:
            print('[TextureFinder] Width must be > 0.')
            return 0

        info = getFormatInfo(fmt)
        if pal and info[0] != 'raw':
            print('[TextureFinder] Palette mode requires a RAW palette color format.')
            return 0

        with open(FilePath, 'rb') as f:
            bs = NoeFileStream(f)
            if ofs < 0 or ofs >= bs.fileSize:
                print('[TextureFinder] Offset is outside the file:', ofs)
                return 0
            bs.seek(ofs)

            available = bs.fileSize - ofs
            if requestedH.lower() == 'max':
                h = findMaxHeight(available, w, fmt, pal, bpp, skw)
            else:
                h = toInt(requestedH, 'height')
                maxH = findMaxHeight(available, w, fmt, pal, bpp, skw)
                if maxH > 0 and h > maxH:
                    print('[TextureFinder] Height clipped:', h, '->', maxH)
                    h = maxH

            if h <= 0:
                print('[TextureFinder] Height must be > 0 / not enough source data.')
                return 0

            payloadSize = getPayloadSize(w, h, fmt, pal, bpp)
            storedSize = getStoredSize(w, h, fmt, pal, bpp, skw)

            print('============================================================')
            print('[TextureFinder] file   :', FilePath)
            print('[TextureFinder] offset :', ofs)
            print('[TextureFinder] size   : %ix%i' % (w, h))
            print('[TextureFinder] format :', fmt)
            print('[TextureFinder] decoder:', info[0])
            print('[TextureFinder] payload:', payloadSize, 'bytes')
            if storedSize != payloadSize:
                print('[TextureFinder] stored :', storedSize, 'bytes (with skew)')
            print('[TextureFinder] flip X/Y:', fw, fh)

            texData = readTexturePayload(bs, w, h, fmt, pal, bpp, skw)

            if pal:
                rawBits = parseFormat(fmt)
                if rawBits <= 0:
                    print('[TextureFinder] Invalid palette color format:', fmt)
                    return 0

                if mip:
                    # Preserve the original Texture Finder behavior.
                    if pofs:
                        bs.seek((w * h) // (pofs * 2), NOESEEK_REL)
                else:
                    bs.seek(pofs)

                paletteEntries = 16 if bpp == 4 else (1 << bpp)
                paletteSize = divCeil(rawBits * paletteEntries, 8)
                palette = readPadded(bs, paletteSize)

                print('[TextureFinder] palette offset/mip:', pofs)
                print('[TextureFinder] palette bpp       :', bpp)
                print('[TextureFinder] palette entries   :', paletteEntries)
                print('[TextureFinder] palette bytes     :', paletteSize)

                if swzl:
                    texData = untwiddleLinearData(texData, w, h, bpp, pstp)

                rgba = rapi.imageDecodeRawPal(texData, palette, w, h, bpp, fmt, flg)
            else:
                if swzl:
                    if info[0] == 'raw':
                        texData = untwiddleLinearData(texData, w, h, info[1], pstp)
                    else:
                        print('[TextureFinder] PSP/PS2 swizzle is only applied to RAW/indexed data; ignored.')

                rgba = decodeTexture(texData, w, h, fmt)

        if rgba is None:
            print('[TextureFinder] Decoder returned None.')
            return 0

        if fw or fh:
            # Noesis order is horizontal, vertical.
            rgba = rapi.imageFlipRGBA32(rgba, w, h, fw, fh)

        texList.append(NoeTexture(name, w, h, rgba, noesis.NOESISTEX_RGBA32))
        return 1

    except Exception as e:
        print('[TextureFinder] ERROR:', e)
        return 0


# -----------------------------------------------------------------------------
# Tiny internal TextureFinder image writer (unchanged behavior)
# -----------------------------------------------------------------------------

def WriteRGBA(data, w, h, writer):
    writer.writeBytes(b'TEX ')
    writer.writeUInt(w)
    writer.writeUInt(h)
    data = rapi.imageEncodeRaw(data, w, h, 'r8g8b8a8')
    writer.writeBytes(data)
    return 1


# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------

def getComboText(combo):
    l = noewin.user32.GetWindowTextLengthW(combo.hWnd) + 1
    textBuffer = noewin.create_unicode_buffer(l)
    noewin.user32.GetWindowTextW(combo.hWnd, textBuffer, l)
    return textBuffer.value.strip()


def setComboItems(combo, items, selected=None):
    combo.resetContent()
    for item in items:
        combo.addString(item)
    if selected is None and len(items) > 0:
        selected = items[0]
    if selected is not None:
        combo.selectString(selected)


def getFamilyFormats(familyName):
    for name, formats in FORMAT_FAMILIES:
        if name == familyName:
            return formats
    return RAW_FORMATS


def updateFormatUi(wind):
    fmt = getComboText(wind.tfFormat)
    raw = isRawFormat(fmt)

    # Palette mode treats the selected RAW format as the palette color format.
    noewin.user32.EnableWindow(wind.tfPalette.hWnd, raw)
    if not raw and wind.tfPalette.isChecked():
        wind.tfPalette.setChecked(noewin.BST_UNCHECKED)

    updatePaletteUi(wind)


def updatePaletteUi(wind):
    fmt = getComboText(wind.tfFormat)
    enabled = wind.tfPalette.isChecked() and isRawFormat(fmt)

    controls = [
        wind.tfMip, wind.tfPalOffset, wind.tfBpp, wind.tfPs2Shift,
        wind.tfPalUp, wind.tfPalDown
    ]
    for ctrl in controls:
        noewin.user32.EnableWindow(ctrl.hWnd, enabled)

    noewin.user32.SetWindowTextW(wind.tfPalOffsetLabel.hWnd, 'mipMap:' if wind.tfMip.isChecked() else 'offset:')


def FamilyChanged(wind, controlId, wParam, lParam):
    notificationId = (wParam >> 16)
    if notificationId == noewin.CBN_SELCHANGE:
        family = getComboText(wind.tfFamily)
        items = getFamilyFormats(family)
        defaultFormat = 'r8g8b8a8' if family == 'RAW / custom' else (items[0] if len(items) else '')
        setComboItems(wind.tfFormat, items, defaultFormat)
        updateFormatUi(wind)
    return False


def FormatChanged(wind, controlId, wParam, lParam):
    notificationId = (wParam >> 16)
    # CBN_SELCHANGE=1, CBN_EDITCHANGE=5. Avoid depending on whether older
    # noewin exposes the CBN_EDITCHANGE symbolic constant.
    if notificationId == noewin.CBN_SELCHANGE or notificationId == 5:
        updateFormatUi(wind)
    return False


def dialogOpenFile(wind, controlId, wParam, lParam):
    global FilePath
    fileName = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, 'Open File', 'Select any File', noesis.getSelectedFile())

    wind.tfFile.setText('')
    FilePath = ''

    if fileName is not None:
        FilePath = str(fileName)
        wind.tfFile.setText(os.path.basename(fileName))
        OpenTemp(wind, controlId, wParam, lParam)


def OpenTemp(wind, controlId, wParam, lParam):
    # Keep the original TEMP field order for compatibility with the old loader:
    # TEMP;offset;skew;palOffset;width;height;format;bpp;platform;
    #      flipX;flipY;palette;mipmap;flag;swizzle;
    template = 'TEMP;'
    template += wind.tfOffset.getText().strip() + ';'
    template += wind.tfSkew.getText().strip() + ';'
    template += wind.tfPalOffset.getText().strip() + ';'
    template += getComboText(wind.tfWidth) + ';'
    template += getComboText(wind.tfHeight) + ';'
    template += getComboText(wind.tfFormat) + ';'
    template += getComboText(wind.tfBpp) + ';'
    template += getComboText(wind.tfSwizzlePlatform) + ';'
    template += ('1' if wind.tfFlipX.isChecked() else '0') + ';'
    template += ('1' if wind.tfFlipY.isChecked() else '0') + ';'
    template += ('1' if wind.tfPalette.isChecked() else '0') + ';'
    template += ('1' if wind.tfMip.isChecked() else '0') + ';'
    template += ('1' if wind.tfPs2Shift.isChecked() else '0') + ';'
    template += ('1' if wind.tfSwizzle.isChecked() else '0') + ';'

    if os.path.exists(FilePath):
        tempPath = 'temp_load.TextureFinder'
        with open(tempPath, 'w') as outFile:
            outFile.write(template)
        noesis.openAndRemoveTempFile(tempPath)
    else:
        print('[TextureFinder] Error file exists!', FilePath)

    print('[TextureFinder] TEMP:', template)
    return True


def CheckedMethod(wind, controlId, wParam, lParam):
    checkBox = wind.getControlById(controlId)
    checkBox.setChecked(noewin.BST_UNCHECKED if checkBox.isChecked() else noewin.BST_CHECKED)

    if checkBox == wind.tfPalette or checkBox == wind.tfMip:
        if checkBox == wind.tfMip:
            wind.tfPalOffset.setText('0')
        updatePaletteUi(wind)
    return True


def calcControl(control, amount):
    s = ''.join(c for c in ('0' + control.getText()) if c.isdigit())
    value = int(s) + amount
    if value < 0:
        value = 0
    control.setText(str(value))


def ChangeValue(wind, controlId, wParam, lParam):
    btn = wind.getControlById(controlId)

    if btn == wind.tfPalUp:
        calcControl(wind.tfPalOffset, 1)
    elif btn == wind.tfPalDown:
        calcControl(wind.tfPalOffset, -1)
    elif btn == wind.tfSkewUp:
        calcControl(wind.tfSkew, 1)
    elif btn == wind.tfSkewDown:
        calcControl(wind.tfSkew, -1)
    elif btn == wind.tfOffsetUp:
        calcControl(wind.tfOffset, 1)
    elif btn == wind.tfOffsetDown:
        calcControl(wind.tfOffset, -1)

    OpenTemp(wind, controlId, wParam, lParam)
    return True


def TextureFinderMethod(toolIndex):
    noesis.logPopup()

    wind = noewin.NoeUserWindow(
        'TextureFinder by(Durik256) - extended formats',
        'TextureFinderClassEx',
        455, 270,
        noewin.defaultWindowProc
    )

    rect = noewin.getNoesisWindowRect()
    if rect:
        wind.x = rect[0] + 64
        wind.y = rect[1] + 64

    if not wind.createWindow():
        print('Failed to create Texture Finder window.')
        return 0

    wind.setFont('Arial', 14)

    # File
    i = wind.createEditBox(10, 10, 395, 22, isMultiLine=False)
    wind.tfFile = wind.getControlByIndex(i)
    i = wind.createButton('...', 410, 9, 30, 24, dialogOpenFile)
    wind.tfOpen = wind.getControlByIndex(i)

    # Offset + size
    wind.createStatic('offset:', 10, 48, 50, 20)
    i = wind.createEditBox(65, 46, 105, 22, text='0', isMultiLine=False)
    wind.tfOffset = wind.getControlByIndex(i)
    i = wind.createButton('▴', 172, 45, 18, 12, ChangeValue)
    wind.tfOffsetUp = wind.getControlByIndex(i)
    i = wind.createButton('▾', 172, 57, 18, 12, ChangeValue)
    wind.tfOffsetDown = wind.getControlByIndex(i)

    wind.createStatic('size:', 205, 48, 35, 20)
    i = wind.createComboBox(242, 46, 82, 20, None, style=noewin.CBS_DROPDOWN | noewin.CBS_HASSTRINGS)
    wind.tfWidth = wind.getControlByIndex(i)
    wind.createStatic('x', 329, 48, 10, 20)
    i = wind.createComboBox(342, 46, 98, 20, None, style=noewin.CBS_DROPDOWN | noewin.CBS_HASSTRINGS)
    wind.tfHeight = wind.getControlByIndex(i)

    # Decoder family + format
    wind.createStatic('family:', 10, 82, 50, 20)
    i = wind.createComboBox(65, 80, 125, 20, FamilyChanged, style=noewin.CBS_DROPDOWNLIST | noewin.CBS_HASSTRINGS)
    wind.tfFamily = wind.getControlByIndex(i)

    wind.createStatic('format:', 205, 82, 50, 20)
    i = wind.createComboBox(260, 80, 180, 20, FormatChanged, style=noewin.CBS_DROPDOWN | noewin.CBS_HASSTRINGS)
    wind.tfFormat = wind.getControlByIndex(i)

    wind.createStatic('RAW format is editable (Noesis imageDecodeRaw syntax).', 65, 107, 365, 18)

    # Skew + flips
    wind.createStatic('skew:', 10, 136, 45, 20)
    i = wind.createEditBox(65, 134, 70, 22, text='0', isMultiLine=False)
    wind.tfSkew = wind.getControlByIndex(i)
    i = wind.createButton('▴', 137, 133, 18, 12, ChangeValue)
    wind.tfSkewUp = wind.getControlByIndex(i)
    i = wind.createButton('▾', 137, 145, 18, 12, ChangeValue)
    wind.tfSkewDown = wind.getControlByIndex(i)

    wind.createStatic('flip:', 185, 136, 35, 20)
    i = wind.createCheckBox('X', 225, 132, 45, 26, CheckedMethod)
    wind.tfFlipX = wind.getControlByIndex(i)
    i = wind.createCheckBox('Y', 275, 132, 45, 26, CheckedMethod)
    wind.tfFlipY = wind.getControlByIndex(i)

    # Palette row
    i = wind.createCheckBox('palette', 10, 174, 80, 26, CheckedMethod)
    wind.tfPalette = wind.getControlByIndex(i)
    i = wind.createCheckBox('mipMap', 95, 174, 80, 26, CheckedMethod)
    wind.tfMip = wind.getControlByIndex(i)

    i = wind.createStatic('offset:', 182, 177, 45, 20)
    wind.tfPalOffsetLabel = wind.getControlByIndex(i)
    i = wind.createEditBox(230, 174, 70, 22, text='0', isMultiLine=False)
    wind.tfPalOffset = wind.getControlByIndex(i)
    i = wind.createButton('▴', 302, 173, 18, 12, ChangeValue)
    wind.tfPalUp = wind.getControlByIndex(i)
    i = wind.createButton('▾', 302, 185, 18, 12, ChangeValue)
    wind.tfPalDown = wind.getControlByIndex(i)

    wind.createStatic('BPP:', 328, 177, 35, 20)
    i = wind.createComboBox(365, 174, 45, 20, None, style=noewin.CBS_DROPDOWNLIST | noewin.CBS_HASSTRINGS)
    wind.tfBpp = wind.getControlByIndex(i)
    i = wind.createCheckBox('PS2 shift', 10, 202, 90, 26, CheckedMethod)
    wind.tfPs2Shift = wind.getControlByIndex(i)

    # Swizzle row
    i = wind.createCheckBox('swizzle', 110, 202, 75, 26, CheckedMethod)
    wind.tfSwizzle = wind.getControlByIndex(i)
    i = wind.createComboBox(185, 204, 70, 20, None, style=noewin.CBS_DROPDOWNLIST | noewin.CBS_HASSTRINGS)
    wind.tfSwizzlePlatform = wind.getControlByIndex(i)

    i = wind.createButton('RUN', 350, 203, 90, 26, OpenTemp, True)
    wind.tfRun = wind.getControlByIndex(i)

    # Info
    wind.createStatic('BC1-BC7 / DXT / ATI | ETC1/ETC2/EAC | PVRTC1/2 | ASTC 2D', 10, 245, 430, 20)
    wind.createStatic('PICA200 ETC1/A4 | Jaguar CRY16 | indexed 4/8bpp + PSP/PS2 untwiddle', 10, 267, 430, 20)
    wind.createStatic('Custom RAW strings remain supported; compressed formats use native Noesis decoders.', 10, 289, 430, 20)

    # Combo contents / item heights
    for combo in [wind.tfWidth, wind.tfHeight, wind.tfFamily, wind.tfFormat, wind.tfBpp, wind.tfSwizzlePlatform]:
        noewin.user32.SendMessageW(combo.hWnd, noewin.CB_SETITEMHEIGHT, -1, 14)

    value = 4096
    for x in range(14):
        wind.tfWidth.addString(str(value))
        wind.tfHeight.addString(str(value))
        value //= 2
        if value <= 0:
            break
    wind.tfHeight.addString('max')
    wind.tfWidth.selectString('512')
    wind.tfHeight.selectString('512')

    for familyName, formats in FORMAT_FAMILIES:
        wind.tfFamily.addString(familyName)
    wind.tfFamily.selectString('RAW / custom')
    setComboItems(wind.tfFormat, RAW_FORMATS, 'r8g8b8a8')

    wind.tfBpp.addString('4')
    wind.tfBpp.addString('8')
    wind.tfBpp.selectString('8')

    wind.tfSwizzlePlatform.addString('PSP')
    wind.tfSwizzlePlatform.addString('PS2')
    wind.tfSwizzlePlatform.selectString('PSP')

    updateFormatUi(wind)
    return 0
