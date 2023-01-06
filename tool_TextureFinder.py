#by Durik256
'''
install:
Download Noesis
Download this script or copy as txt and rename to "tool_TextureFinder.py
Drop this script to '..\Noesis\Plugins\Python'
Tools>Display Plugin Tools (once)
Tools>Texture Finder
'''
from inc_noesis import *
import os
from ctypes import *
import noewin

def registerNoesisTypes():
    handle = noesis.registerTool("&Texture Finder", TextureFinderMethod)
    handle = noesis.register("Texture Finder", ".TextureFinder")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)
    noesis.setHandlerWriteRGBA(handle, WriteRGBA)
    return 1

FilePath = ""

def CheckType(data):
    if data[:4] == b'TEX ' or data[:4] == b'TEMP':
        return 1
    return 0
    
def LoadRGBA(data, texList):
    name = rapi.getInputName()
    
    if data[:4] == b'TEX ':
        bs = NoeBitStream(data)
        bs.seek(4)#magic
        w, h = bs.read('2I')
        data = rapi.imageDecodeRaw(data[12:], w, h, 'r8g8b8a8')
    else:
        arg  = data.decode().split(';')
        ofs  = toInt(arg[1], 'offset')
        w    = toInt(arg[4], 'width')
        if arg[5] == 'max': 
            h = 2**32
        else:
            h = toInt(arg[5], 'height')
        fw   = int(arg[9])#9
        fh   = int(arg[10])#10
        fmt  = arg[6]
        skw  = toInt(arg[2], 'skew')
        bits = parseFormat(fmt)
        raw  = bits
        pal  = int(arg[11])#11
        pofs = toInt(arg[3], 'palette ofsset /or/ num MipMap')
        bpp  = toInt(arg[7], 'bpp')
        mip  = int(arg[12])#12
        flg  = int(arg[13])#13
        swzl = int(arg[14])
        pstp = arg[8]
        
        dxt, texFmt = False, noesis.NOESISTEX_DXT1
        if 'dxt' in fmt.lower():
            dxt = True
            if bits == 1:
                bits = 4
            elif bits == 3:
                bits = 8
                texFmt = noesis.NOESISTEX_DXT3
            elif bits == 5:
                bits = 8
                texFmt = noesis.NOESISTEX_DXT5
            else:
                bits = 0
        
        if pal:
            bits = bpp
        
        print('offset:',ofs,'\nsize: %ix%i'%(w,h),'\nformat:',fmt,'\nskew:',skw,'\nbits per pixel:',bits)
        print('flip:\n  Horizontal:',fw,'\n  Vertical:',fh)
        if pal:
            print('palette offset /or/ mipmap:',pofs,'\nbpp: ', bpp,'\nflag:',flg)
        
        with open(FilePath,'rb') as f:
            bs = NoeFileStream(f)
            bs.seek(ofs)
        
            max = ceil((bs.fileSize - ofs)/(w*bits/8))
            if dxt: max = max//4*4
        
            print("max:",max)
            if h > max:
                h = max
            
            size, eof, add = ceil(w*h*bits/8 + (skw*h*8)), bs.fileSize - ofs, 0
            if eof < size:
                add = size - eof
                size = eof
            
            print('size file:',bs.fileSize,'\nsize on prewiev:',size+add)
            
            if not skw:
                data = bs.readBytes(size) + b'\xFF'*add
            else:
                data = b''
                for y in range(h):
                    data += bs.readBytes(ceil(w*bits/8))
                    bs.seek(skw,1)
                data += b'\xFF'*add
            
            if dxt:
                data = rapi.imageDecodeDXT(data, w, h, texFmt)
            elif pal:
                if mip:
                    if pofs:
                        bs.seek((w*h)//(pofs*2),1)
                else:
                    bs.seek(pofs)
                
                size, eof, add = ceil(raw*256/8), bs.fileSize - bs.tell(), 0
                if eof < size:
                    add = size - eof
                    size = eof
                palette = bs.readBytes(size) + b'\xFF'*add
                print('size palette:',len(palette))
                
                if swzl:
                    if pstp == 'PSP':
                        data = rapi.imageUntwiddlePSP(data, w, h, bpp)
                    elif pstp == 'PS2':
                        data = rapi.imageUntwiddlePS2(data, w, h, bpp)
                data = rapi.imageDecodeRawPal(data, palette, w, h, bpp, fmt, flg)
            else:
                data = rapi.imageDecodeRaw(data, w, h, fmt)
        
        if fw or fh:
            data = rapi.imageFlipRGBA32(data, w, h, fh, fw)
        
        #if swizzle:
        
        
    texList.append(NoeTexture(name, w, h, data, noesis.NOESISTEX_RGBA32))
    return 1

def swizzle():
    dest = [width * height]

    destOffset = 0;

    # Incorporate the bpp into the width
    width = (width * 8) >> 3;

    rowblocks = (width / 16);

    for y in range(height):
        for x in range(width):
            blockX = x / 16
            blockY = y / 8

            blockIndex = blockX + ((blockY) * rowblocks)
            blockAddress = blockIndex * 16 * 8

            dest[destOffset] = data[blockAddress + (x - blockX * 16) + ((y - blockY * 8) * 16)]
            destOffset+=1
    # ---- end unswizzling code ---- \\


def ceil(i):
    return int(-1 * (i) // 1 * -1)
    
def parseFormat(fmt):
    try:
        x = ''.join(c if c.isdigit() else ' ' for c in fmt)
        return sum([int(i) for i in x.split()])
    except:
        print('Error parse format', fmt)
        return 0
    
def toInt(s, n='value'):
    try:
        return int(s)
    except:
        print('Error convert', n)
        return 0

def WriteRGBA(data, w, h, writer):
    writer.writeBytes(b'TEX ')
    writer.writeUInt(w)
    writer.writeUInt(h)
    
    #WRITE TEXTURE
    data = rapi.imageEncodeRaw(data, w, h, 'r8g8b8a8')
    writer.writeBytes(data)
    return 1
 
#---------------------------------------------------
def dialogOpenFile(wind, controlId, wParam, lParam):
    FileName = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Open File", "Select any File", noesis.getSelectedFile())
    global FilePath
    
    wind.userControls[18].setText('')
    FilePath = ''
    
    if FileName != None:
        FilePath = str(FileName)
        wind.userControls[18].setText(os.path.basename(FileName))
        OpenTemp(wind, id, wParam, lParam)
        
def OpenTemp(wind, id, wParam, lParam):
    template = 'TEMP;'
    
    for x in [0,4,9]:#textbox
        template += str(wind.userControls[x].getText().strip()) + ';'
        
    for x in [1,2,3,10,30]:#combobox
        x = wind.userControls[x]
        l = noewin.user32.GetWindowTextLengthW(x.hWnd) + 1
        textBuffer = noewin.create_unicode_buffer(l)
        noewin.user32.GetWindowTextW(x.hWnd, textBuffer, l)
        template += textBuffer.value.strip() + ';'
        
    for x in [5,6,7,8,11,29]:#checkbox
        template += ('1' if wind.userControls[x].isChecked() else '0') + ';'
    
    if os.path.exists(FilePath):
        with open('temp_load.TextureFinder', 'w') as w:
            w.write(template)
        noesis.openAndRemoveTempFile('temp_load.TextureFinder')
    else:
        print('Error file exists!', FilePath)
    print(template)
    
def ChekedMethod(wind, id, wParam, lParam):
    checkBox = wind.getControlById(id)
    checkBox.setChecked(noewin.BST_UNCHECKED if checkBox.isChecked() else noewin.BST_CHECKED)
    
    if checkBox == wind.userControls[7]:
        DisablePallete(wind, False)

        if checkBox.isChecked():
            DisablePallete(wind, True)
            
    elif checkBox == wind.userControls[8]:
        wind.userControls[9].setText('0')
        noewin.user32.SetWindowTextW(wind.userControls[20].hWnd, "offset:")
        if checkBox.isChecked():
            noewin.user32.SetWindowTextW(wind.userControls[20].hWnd, "mipMap:")

def DisablePallete(wind, enabled):
    for x in [8,9,10,11,12,13,29,30]:#range(8,14)
        noewin.user32.EnableWindow(wind.userControls[x].hWnd, enabled)
    
def TextureFinderMethod(toolIndex):
    noesis.logPopup()
    
    wind = noewin.NoeUserWindow("TextureFinder by(Durik256)", "TextureFinderClass", 235, 316, noewin.defaultWindowProc)

    rect = noewin.getNoesisWindowRect()
    if rect:
        wind.x = rect[0] + 64
        wind.y = rect[1] + 64
    if not wind.createWindow():
        print("Failed to create window.")
        return 0

    wind.setFont("Arial", 14)
    ctrl = wind.userControls
    
    wind.createEditBox(60, 40, 143, 20, text = '0', isMultiLine = False)                            #0-Offset
    wind.createComboBox(60, 70, 70, 14, None, style = noewin.CBS_DROPDOWN | noewin.CBS_HASSTRINGS)  #1-width
    wind.createComboBox(149, 70, 70, 14, None, style = noewin.CBS_DROPDOWN | noewin.CBS_HASSTRINGS) #2-height
    wind.createComboBox(60, 100, 159, 20, None, style = noewin.CBS_DROPDOWN | noewin.CBS_HASSTRINGS)#3-format
    wind.createEditBox(60, 134, 54, 20, text = '0', isMultiLine = False)                            #4-skew
    wind.createCheckBox("x", 173, 132, 30, 24, ChekedMethod)                                        #5-flipX
    wind.createCheckBox("", 203, 132, 16, 24, ChekedMethod)                                         #6-flipY
    wind.createCheckBox("palette:", 10, 162, 90, 24, ChekedMethod)                                  #7-palette
    wind.createCheckBox("mipMap", 140, 162, 90, 24, ChekedMethod)                                   #8-mipMap
    wind.createEditBox(60, 192, 143, 20, text = '0', isMultiLine = False)                           #9-OffsetPallete
    wind.createComboBox(60, 222, 70, 20, None, style = noewin.CBS_DROPDOWN | noewin.CBS_HASSTRINGS) #10-BBP
    wind.createCheckBox("flag", 140, 221, 90, 24, ChekedMethod)                                     #11-flag
    
    #fix height comboBox
    noewin.user32.SendMessageW(wind.userControls[1].hWnd, noewin.CB_SETITEMHEIGHT, -1, 14)
    noewin.user32.SendMessageW(wind.userControls[2].hWnd, noewin.CB_SETITEMHEIGHT, -1, 14)
    noewin.user32.SendMessageW(wind.userControls[10].hWnd, noewin.CB_SETITEMHEIGHT, -1, 14)
    
    #UpDownNumeric ▲▼▾▴
    wind.createButton('▴', 203, 191, 16, 11, ChangeValue)#12 - pofs
    wind.createButton('▾', 203, 202, 16, 11, ChangeValue)#13 - pofs
    wind.createButton('▴', 114, 133, 16, 11, ChangeValue)#14 - skew
    wind.createButton('▾', 114, 144, 16, 11, ChangeValue)#15 - skew
    wind.createButton('▴', 203, 39, 16, 11, ChangeValue)#16 - gofs
    wind.createButton('▾', 203, 50, 16, 11, ChangeValue)#17 - gofs

    wind.createEditBox(10, 10, 188, 20, isMultiLine = False)#18 - field file
    wind.createButton("...", 198, 9, 22, 22, dialogOpenFile)#19
    
    #static
    wind.createStatic("offset:", 10, 192, 40, 20)#20
    wind.createStatic("offset:", 10, 41, 40, 20)#21
    wind.createStatic("size:", 10, 71, 40, 20)#22
    wind.createStatic("x", 136, 71, 10, 20)#23
    wind.createStatic("format:", 10, 101, 45, 20)#24
    wind.createStatic("skew:", 10, 135, 45, 20)#25
    wind.createStatic("flip:", 140, 135, 45, 20)#26
    wind.createStatic("BPP:", 10, 224, 40, 20)#27
    
    wind.createButton("run", 170, 251, 50, 22, OpenTemp)#28
    
    #add Swizzle
    wind.createCheckBox("swizzle", 10, 249, 65, 24, ChekedMethod)   #29-swizzle
    wind.createComboBox(75, 251, 55, 20, None, style = noewin.CBS_DROPDOWNLIST | noewin.CBS_HASSTRINGS)#30
    noewin.user32.SendMessageW(wind.userControls[30].hWnd, noewin.CB_SETITEMHEIGHT, -1, 14)
    wind.userControls[30].addString('PSP')
    wind.userControls[30].addString('PS2')
    wind.userControls[30].selectString('PSP')
    
    #add items in combobox
    i = 2048
    for x in range(12):
        wind.userControls[1].addString(str(i))
        wind.userControls[2].addString(str(i))
        i //=2
    wind.userControls[2].addString('max')
    wind.userControls[1].selectString('512')
    wind.userControls[2].selectString('512')
    
    formats = ['r16g16b16a16', 'r16g16b16',
               'r8g8b8a8'    , 'r8g8b8',
               'r5g6b5'      , 'r5g5b5a1',
               'r4g4b4a4'    , 'r3g3b2',
               'r2g2b2a2'    , 'DXT1',
               'DXT3'        , 'DXT5']
    
    for x in formats:
        wind.userControls[3].addString(x)
    wind.userControls[3].selectString('r8g8b8a8')
    
    wind.userControls[10].addString('4')
    wind.userControls[10].addString('8')
    wind.userControls[10].selectString('8')
    
    DisablePallete(wind, False)
    return 0

#UpDownNumerick change value
def calc(id, i, wind):
    s = ''.join(c for c in '0'+wind.userControls[id].getText() if c.isdigit())
    s = int(s) + (i)
    if s < 0: s = 0
    wind.userControls[id].setText(str(s))
   
def ChangeValue(wind, id, wParam, lParam):
    btn = wind.getControlById(id)
    if btn == wind.userControls[12]:#12 - pofsUp
        calc(9, 1, wind)
    elif btn == wind.userControls[13]:#13 - pofsDown
        calc(9, -1, wind)
    elif btn == wind.userControls[14]:#14 - skewUp
        calc(4, 1, wind)
    elif btn == wind.userControls[15]:#15 - skewDown
        calc(4, -1, wind)
    elif btn == wind.userControls[16]:#16 - gofsUp
        calc(0, 1, wind)
    elif btn == wind.userControls[17]:#17 - gofsDown
        calc(0, -1, wind)
    OpenTemp(wind, id, wParam, lParam)
