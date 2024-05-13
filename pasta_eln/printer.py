""" Misc PRINTER functions that do not require instances """
import os, uuid
from typing import Any

def createQRcodeSheet(fileName:str="../qrCodes.pdf") -> None:
  """
  Documentation QR-codes
  - img = qrcode.make("testString",error_correction=qrcode.constants.ERROR_CORRECT_M)
  - or ERROR-CORRECT_H for better errorcorrection
  Sizes:
  - QR code size 1.5-2cm
  - with frame 2.25-3cm
  - Page size 18x27cm; 6x9 = 54
  """
  # this code currently does not work, but not used anyhow. Have to fix it in the future

  # import qrcode
  # import numpy as np
  # from PIL import Image
  # #from commonTools import commonTools as cT  # don't import globally since it disturbs translation
  # #img = qrcode.make(cT.uuidv4(), error_correction=qrcode.constants.ERROR_CORRECT_M)
  # size = -1 # img.size[0]
  # hSize = 6*size
  # vSize = 9*size
  # new_im = Image.new('RGB', (hSize, vSize))
  # for i in np.arange(0, hSize, size):
  #   for j in np.arange(0, vSize, size):
  #     #img = qrcode.make(cT.uuidv4(), error_correction=qrcode.constants.ERROR_CORRECT_M)
  #     # if j==0:  #make top row yellow
  #     #   data = np.array(img.convert("RGB"))
  #     #   red, green, blue = data.T
  #     #   mask = (red==255) & (green==255) & (blue==255)
  #     #   data[:,:,:][mask.T]=(255,255,0)
  #     #   img = Image.fromarray(data)
  #     # new_im.paste(img, (i, j))
  #     print(i,j)
  # new_im.save(fileName)
  return


def printQRcodeSticker(codes:list[list[str]]=[],
                       page:dict[str,Any]={'size':[991,306], 'tiles':2, 'margin': 60, 'font':40},
                       printer:dict[str,str]={'model':'QL-700', 'dev':'0x04f9:0x2042/3', 'size':'29x90'}) -> None:
  """
  Codes: key-value pairs of qr-code and label
   - filled to achieve tiles

  Sticker:
   - size: 90.3x29 mm => [991,306] px
   - tiles: number of items on the sticker
   - margin: margin between tiles
   - font: font size in px

  Printer:
   - model: brother label printer QL-700
   - dev: device in idVendor:idProduct/iSerial
     execute 'lsusb -v'; find printer
   - size: label size in mm
  """
  # this code currently does not work, but not used anyhow. Have to fix it in the future

  # import qrcode, tempfile
  # import numpy as np
  # from PIL import Image, ImageDraw, ImageFont
  # # fnt = ImageFont.truetype("arial.ttf", page['font'])
  # offset    = int((page['size'][0]+page['margin'])/page['tiles'])
  # qrCodeSize= min(offset-page['font']-page['margin'], page['size'][1])
  # print("Effective label size",page['size'], "offset",offset, 'qrCodeSize',qrCodeSize)
  # cropQRCode  = 40         #created by qrcode library
  # image = Image.new('RGBA', page['size'], color=(255,255,255,255) )
  # for numCodes, idx in enumerate(range(page['tiles'])):
  #   codeI, text = codes[idx] if idx<len(codes) else ('', '')
  #   print(text)
  #   if len(codeI)==0:
  #     codeI = uuid.uuid4().hex
  #   # add text: temporary comment out since library updated and functions changed
  #   # width, height = fnt.getsize(text)
  #   # txtImage = Image.new('L', (width, height), color=255)
  #   # d = ImageDraw.Draw(txtImage)
  #   # d.text( (0, 0), text,  font=fnt, fill=0)
  #   # txtImage=txtImage.rotate(90, expand=1)
  #   # if width>page['size'][1]:  #shorten it to fit into height
  #   #   txtImage=txtImage.crop((0,width-page['size'][1],height,width))
  #   # image.paste(txtImage, (numCodes*offset+qrCodeSize-4, int((page['size'][1]-txtImage.size[1])/2)   ))
  #   # add qrcode
  #   qrCode = qrcode.make(codeI, error_correction=qrcode.constants.ERROR_CORRECT_M)
  #   qrCode = qrCode.crop((cropQRCode, cropQRCode, qrCode.size[0]-cropQRCode, qrCode.size[0]-cropQRCode))
  #   qrCode = qrCode.resize((qrCodeSize, qrCodeSize))
  #   image.paste(qrCode, (numCodes*offset, int((page['size'][1]-qrCodeSize)/2)))
  # tmpFileName = tempfile.gettempdir()+os.sep+'tmpQRcode.png'
  # print('Create temp-file',tmpFileName)
  # image.save(tmpFileName)
  # cmd = 'brother_ql -b pyusb -m '+printer['model']+' -p usb://'+printer['dev']+' print -l '+printer['size']+' -r auto '+tmpFileName
  # reply = os.system(cmd)
  # if reply>0:
  #   print('**ERROR mpq01: Printing error')
  #   image.show()
  return
