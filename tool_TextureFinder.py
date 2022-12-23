#by Durik256
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
            
Controls = []
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
        w    = toInt(arg[2], 'width')
        h    = toInt(arg[3], 'height')
        fw   = int(arg[11])
        fh   = int(arg[12])
        fmt  = arg[4]
        skw  = toInt(arg[5], 'skew')
        bits = parseFormat(fmt)
        pal  = int(arg[6])
        pofs = toInt(arg[7])#or num MipMap
        bpp  = toInt(arg[8])
        mip  = int(arg[9])
        flg  = int(arg[10])
        
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
        
        bs = NoeBitStream(rapi.loadIntoByteArray(FilePath))
        bs.seek(ofs)
        size, eof, add = int(-1 * (w*h*bits/8 + (skw*h*8)) // 1 * -1), bs.getSize() - ofs, 0
        if eof < size:
            add = size - eof
            size = eof
        
        print('size file:',bs.getSize(),'\nsize on prewiev:',size+add)
        
        if not skw:
            data = bs.readBytes(size) + b'\xFF'*add
        else:
            data = b''
            for y in range(h):
                data += bs.readBytes(int(-1 * ((w*bits)/8) // 1 * -1))
                bs.seek(skw,1)
            data += b'\xFF'*add
        
        if dxt:
            data = rapi.imageDecodeDXT(data, w, h, texFmt)
        elif pal:
            if mip:
                bs.seek((w*h)//((pofs*2) if pofs else 1))
                palette = bs.readBytes(bpp*128)
            else:
                bs.seek(pofs)
                palette = bs.readBytes(bpp*128)
        
            data = rapi.imageDecodeRawPal(data, palette, w, h, bpp, fmt, flg)
        else:
            data = rapi.imageDecodeRaw(data, w, h, fmt)
    
    if fw or fh:
        data = rapi.imageFlipRGBA32(data, w, h, fh, fw)
    
    texList.append(NoeTexture(name, w, h, data, noesis.NOESISTEX_RGBA32))
    return 1
    
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
    
def TextureFinderProc(hWnd, message, wParam, lParam):
    if message == noewin.WM_PAINT:
        noeWnd = noewin.getNoeWndForHWnd(hWnd)
        ps = noewin.PAINTSTRUCT()
        rect = noewin.RECT()
        hDC = noewin.user32.BeginPaint(hWnd, byref(ps))
        oldFont = None
        if noeWnd.hFont:
            oldFont = noewin.gdi32.SelectObject(hDC, noeWnd.hFont)    
        
        if oldFont:
            noewin.gdi32.SelectObject(hDC, oldFont)
        return 0
    return noewin.defaultWindowProc(hWnd, message, wParam, lParam)
 
#---------------------------------------------------
def dialogOpenFile(noeWnd, controlId, wParam, lParam):
    FileName = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Open File", "Select any File", noesis.getSelectedFile())
    global FilePath
    
    Controls[0].setText('')
    FilePath = ''
    
    if FileName != None:
        FilePath = str(FileName)
        Controls[0].setText(os.path.basename(FileName))
        
def OpenTemp(noeWnd, controlId, wParam, lParam):
    template = 'TEMP;'
    
    for x in range(1,6):
        template += str(Controls[x].getText().strip()) + ';'
        
    template += ('1' if Controls[6].isChecked() else '0') + ';'
        
    for x in range(7,9):
        template += str(noeWnd.getControlByIndex(Controls[x]).getText().strip()) + ';'
        
    for x in range(9,13):
        template += ('1' if noeWnd.getControlByIndex(Controls[x]).isChecked() else '0') + ';'
    
    if os.path.exists(FilePath):
        with open('temp_load.TextureFinder', 'w') as w:
            w.write(template)
        noesis.openAndRemoveTempFile('temp_load.TextureFinder')
    else:
        print('Error file exists!', FilePath)
    print(template)
    
def ChekedMethod(noeWnd, controlId, wParam, lParam):
    checkBox = noeWnd.getControlById(controlId)
    checkBox.setChecked(noewin.BST_CHECKED if checkBox.isChecked() == 0 else noewin.BST_UNCHECKED)
    
    if checkBox == Controls[6]:
        DisablePallete(noeWnd, False)

        if checkBox.isChecked():
            DisablePallete(noeWnd, True)
            
    elif checkBox == noeWnd.getControlByIndex(Controls[9]):
        noewin.user32.SetWindowTextW(Controls[-1].hWnd, "offset")
        if checkBox.isChecked():
            noewin.user32.SetWindowTextW(Controls[-1].hWnd, "mipMap:")

def DisablePallete(noeWnd, enabled):
    for x in range(7,11):
        noeWnd.enableControlByIndex(Controls[x], enabled)
    
def TextureFinderMethod(toolIndex):
    noesis.logPopup()
    
    noeWnd = noewin.NoeUserWindow("TextureFinder by(Durik256)", "TextureFinderClass", 194, 277, TextureFinderProc)
    #offset a bit into the noesis window
    noeWindowRect = noewin.getNoesisWindowRect()
    if noeWindowRect:
        windowMargin = 64
        noeWnd.x = noeWindowRect[0] + windowMargin
        noeWnd.y = noeWindowRect[1] + windowMargin
    if not noeWnd.createWindow():
        print("Failed to create window.")
        return 0

    noeWnd.setFont("Arial", 14)
    
    global Controls
    noeWnd.createStatic("offset:", 10, 35, 58, 20)
    noeWnd.createStatic("size:", 10, 60, 58, 20)
    noeWnd.createStatic("x", 119, 61, 9, 20)
    noeWnd.createStatic("format:", 10, 85, 58, 20)
    noeWnd.createStatic("skew:", 10, 110, 58, 20)
    label = noeWnd.createStatic("offset:", 10, 160, 58, 20)
    noeWnd.createStatic("BPP:", 10, 185, 58, 20)
    noeWnd.createStatic("flip:", 112, 111, 19, 20)
    noeWnd.createStatic("x", 154, 111, 8, 20)
        
    noeWnd.createButton("...", 156, 9,   22, 22, dialogOpenFile)
    noeWnd.createButton("run", 128, 215, 50, 22, OpenTemp)

    field = noeWnd.createEditBox(10,  10,  146, 20, "", None, False, False)        #file
    Controls.append(noeWnd.getControlByIndex(field))                               #0
    field = noeWnd.createEditBox(68,  35,  110, 20, "0", None, False, False)       #offset
    Controls.append(noeWnd.getControlByIndex(field))                               #1
    field = noeWnd.createEditBox(68,  60,  50,  20, "512", None, False, False)     #sizeW
    Controls.append(noeWnd.getControlByIndex(field))                               #2
    field = noeWnd.createEditBox(128, 60,  50,  20, "512", None, False, False)     #sizeH
    Controls.append(noeWnd.getControlByIndex(field))                               #3
    field = noeWnd.createEditBox(68,  85,  110, 20, "r8g8b8a8", None, False, False)#format
    Controls.append(noeWnd.getControlByIndex(field))                               #4
    field = noeWnd.createEditBox(68,  110, 39,  20, "0", None, False, False)       #skew
    Controls.append(noeWnd.getControlByIndex(field))                               #5
    field = noeWnd.createCheckBox("palette:", 10, 135, 90, 24, ChekedMethod)       #CheckBox palette
    Controls.append(noeWnd.getControlByIndex(field))                               #6
    field = noeWnd.createEditBox(68,  160, 110, 20, "0", None, False, False)       #offset palette
    Controls.append(field)                                                         #7
    field = noeWnd.createEditBox(68,  185, 50,  20, "8", None, False, False)       #BPP
    Controls.append(field)                                                         #8
    field = noeWnd.createCheckBox("MipMap", 102, 135, 80, 24, ChekedMethod)        #CheckBox MipMap
    Controls.append(field)                                                         #9
    field = noeWnd.createCheckBox("Flag", 129, 183, 50, 24, ChekedMethod)          #CheckBox Flag
    Controls.append(field)                                                         #10
    field = noeWnd.createCheckBox("", 136, 108, 16, 24, ChekedMethod)              #CheckBox Flip Horizontal
    Controls.append(field)                                                         #11
    field = noeWnd.createCheckBox("", 163, 108, 16, 24, ChekedMethod)              #CheckBox Flip Vertical
    Controls.append(field)                                                         #12
    
    #TEST COMBOBOX
    field = noeWnd.getControlByIndex(noeWnd.createComboBox(194, 60, 60, 14, None, style = 0x0003))
    noewin.user32.SendMessageW(field.hWnd, 0x0153, -1, 14)
    i = 2048
    for x in range(12):
        field.addString(str(i))
        i //=2
    field.selectString('512')
    
    Controls.append(noeWnd.getControlByIndex(label))                                                        #always in the End
    DisablePallete(noeWnd, False)
    return 0