#!/usr/bin/python3
"""
Misc methods and definitions for json, colors
"""
import sys

class bcolors:
  """
  Colors for Command-Line-Interface and output
  """
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

def createDirName(name,docType,thisChildNumber):
  """ create directory-name by using camelCase and a prefix

  Args:
      name (string): name with spaces etc.
      docType (string): document type used for prefix
      thisChildNumber (int): number of myself

  Returns:
    string: directory name with leading number
  """
  from commonTools import commonTools as cT  #not globally imported since confuses translation
  if docType == 'x0':
    return cT.camelCase(name)
  #steps, tasks
  if isinstance(thisChildNumber, str):
    thisChildNumber = int(thisChildNumber)
  return f'{thisChildNumber:03d}'+'_'+cT.camelCase(name)



def generic_hash(path, forceFile=False):
  """
  Hash an object based on its mode.

  inspired by:
  https://github.com/chris3torek/scripts/blob/master/githash.py

  Example implementation:
      result = generic_hash(sys.argv[1])
      print('%s: hash = %s' % (sys.argv[1], result))

  Args:
    path (string): path
    forceFile (bool): force to get shasum of file and not of link (False for gitshasum)

  Returns:
    string: shasum

  Raises:
    ValueError: shasum of directory not supported
  """
  from urllib import request
  if str(path).startswith('http'):                      #Remote file
    with request.urlopen(str(path).replace(':/','://')) as site:
      meta = site.headers
      size = int(meta.get_all('Content-Length')[0])
      return blob_hash(site, size)
  if path.is_dir():
    raise ValueError('This seems to be a directory '+path)
  if forceFile and path.is_symlink():
    path = path.resolve()
  if path.is_symlink():    #if link, hash the link
    shasum = symlink_hash(path)
  elif path.is_file():  #Local file
    with open(path, 'rb') as stream:
      shasum = blob_hash(stream, path.stat().st_size)
  return shasum


def upOut(key):
  """
  key (bool): key
  """
  import keyring as cred
  keys = key.split() if ' ' in key else [key]
  keys_ = []
  for keyI in keys:
    key_ = cred.get_password('pastaDB',keyI)
    if key_ is None:
      key_ = ':'
    else:
      key_ = ':'.join(key_.split('bcA:Maw'))
    keys_.append(key_)
  return keys_

def upIn(key):
  """
  key (bool): key
  """
  import keyring as cred
  from commonTools import commonTools as cT  # don't import globally since it disturbs translation
  key = 'bcA:Maw'.join(key.split(':'))
  id_  = cT.uuidv4()
  cred.set_password('pastaDB',id_,key)
  return id_


def symlink_hash(path):
  """
  Return (as hash instance) the hash of a symlink.
  Caller must use hexdigest() or digest() as needed on
  the result.

  Args:
    path (string): path to symlink

  Returns:
    string: shasum of link, aka short string
  """
  import os
  from hashlib import sha1
  hasher = sha1()
  data = os.readlink(path).encode('utf8', 'surrogateescape')
  hasher.update('blob {len(data)}\0'.encode('ascii'))
  hasher.update(data)
  return hasher.hexdigest()


def blob_hash(stream, size):
  """
  Return (as hash instance) the hash of a blob,
  as read from the given stream.

  Args:
    stream (string): content to be hashed
    size (int): size of the content

  Returns:
    string: shasum

  Raises:
    ValueError: size given is not the size of the stream
  """
  from hashlib import sha1
  hasher = sha1()
  hasher.update(f'blob {size}\0'.encode('ascii'))
  nRead = 0
  while True:
    data = stream.read(65536)     # read 64K at a time for storage requirements
    if data == b'':
      break
    nRead += len(data)
    hasher.update(data)
  if nRead != size:
    raise ValueError(f'{stream.name}: expected {size} bytes, found {nRead} bytes')
  return hasher.hexdigest()


def stringToImage(aString, show=True):
  """
  *DEPRECATED*
  convert a b64-string to png file
  - not really used

  Args:
    aString (string): 64byte string of image
    show (bool): show image

  Returns:
    Image: image of string
  """
  import base64, io
  from PIL import Image
  imgdata = base64.b64decode(aString)
  image = Image.open(io.BytesIO(imgdata))
  if show:
    image.show()
  return image


def getExtractorConfig(directory):
  """
  Rules:
  - each data-type in its own try-except
  - inside try: raise ValueError exception on failure/None
  - except empty: pass
  - all descriptions in type have to be small letters
  - if want to force to skip top datatypes and use one at bottom: if doctype... -> exception

  Args:
    directory (string): relative directory to scan

  Returns:
    list: list of [doctype-list, description]
  """
  import os
  configuration = {}
  for fileName in os.listdir(directory):
    if fileName.endswith('.py') and fileName not in ['testExtractor.py','tutorial.py'] :
      #start with file
      with open(directory+os.sep+fileName,'r', encoding='utf-8') as fIn:
        lines = fIn.readlines()
        extractors = []
        baseType = ['measurement', fileName.split('_')[1].split('.')[0]]
        ifInFile, headerState, header = False, True, []
        for idx,line in enumerate(lines):
          line = line.rstrip()
          if idx>0 and '"""' in line:
            headerState = False
          if headerState:
            line = line.replace('"""','')
            header.append(line)
            continue
          if "if" in line and "#:" in line:
            specialType = line.split("endswith('")[1].split("')")[0]
            extractors.append([ baseType+specialType.split('/'), line.split('#:')[1].strip() ])
            ifInFile = True
          elif "else:" in line and "#:" in line:
            extractors.append([ baseType, line.split('#:')[1].strip() ])
          elif "return" in line and not ifInFile:
            try:
              specialType = line.split("+['")[1].split("']")[0]
              extractors.append([ baseType+[specialType], '' ])
            except:
              pass
        configuration[fileName] = {'plots':extractors, 'header':'\n'.join(header)}
  return configuration


def createQRcodeSheet(fileName="../qrCodes.pdf"):
  """
  Documentation QR-codes
  - img = qrcode.make("testString",error_correction=qrcode.constants.ERROR_CORRECT_M)
  - or ERROR-CORRECT_H for better errorcorrection
  Sizes:
  - QR code size 1.5-2cm
  - with frame 2.25-3cm
  - Page size 18x27cm; 6x9 = 54
  """
  import qrcode
  import numpy as np
  from PIL import Image
  from commonTools import commonTools as cT  # don't import globally since it disturbs translation
  img = qrcode.make(cT.uuidv4(),
                    error_correction=qrcode.constants.ERROR_CORRECT_M)
  size = img.size[0]
  hSize = 6*size
  vSize = 9*size
  new_im = Image.new('RGB', (hSize, vSize))
  for i in np.arange(0, hSize, size):
    for j in np.arange(0, vSize, size):
      img = qrcode.make(cT.uuidv4(),
                        error_correction=qrcode.constants.ERROR_CORRECT_M)
      # if j==0:  #make top row yellow
      #   data = np.array(img.convert("RGB"))
      #   red, green, blue = data.T
      #   mask = (red==255) & (green==255) & (blue==255)
      #   data[:,:,:][mask.T]=(255,255,0)
      #   img = Image.fromarray(data)
      new_im.paste(img, (i, j))
  new_im.save(fileName)
  return


def printQRcodeSticker(codes={},
                       page={'size':[991,306], 'tiles':2, 'margin': 60, 'font':40},
                       printer={'model':'QL-700', 'dev':'0x04f9:0x2042/3', 'size':'29x90'}):
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
  import qrcode, tempfile, os
  import numpy as np
  from PIL import Image, ImageDraw, ImageFont
  from commonTools import commonTools as cT  # don't import globally since it disturbs translation
  fnt = ImageFont.truetype("arial.ttf", page['font'])
  offset    = int((page['size'][0]+page['margin'])/page['tiles'])
  qrCodeSize= min(offset-page['font']-page['margin'], page['size'][1])
  print("Effective label size",page['size'], "offset",offset, 'qrCodeSize',qrCodeSize)
  cropQRCode  = 40         #created by qrcode library
  numCodes = 0
  image = Image.new('RGBA', page['size'], color=(255,255,255,255) )
  for idx in range(page['tiles']):
    if idx<len(codes):
      codeI, text = codes[idx]
    else:
      codeI, text =  '', ''
    if len(codeI)==0:
      codeI = cT.uuidv4()
    # add text
    width, height = fnt.getsize(text)
    txtImage = Image.new('L', (width, height), color=255)
    d = ImageDraw.Draw(txtImage)
    d.text( (0, 0), text,  font=fnt, fill=0)
    txtImage=txtImage.rotate(90, expand=1)
    if width>page['size'][1]:  #shorten it to fit into height
      txtImage=txtImage.crop((0,width-page['size'][1],height,width))
    image.paste(txtImage, (numCodes*offset+qrCodeSize-4, int((page['size'][1]-txtImage.size[1])/2)   ))
    # add qrcode
    qrCode = qrcode.make(codeI, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qrCode = qrCode.crop((cropQRCode, cropQRCode, qrCode.size[0]-cropQRCode, qrCode.size[0]-cropQRCode))
    qrCode = qrCode.resize((qrCodeSize, qrCodeSize))
    image.paste(qrCode, (numCodes*offset, int((page['size'][1]-qrCodeSize)/2)))
    numCodes += 1
  tmpFileName = tempfile.gettempdir()+os.sep+'tmpQRcode.png'
  print('Create temp-file',tmpFileName)
  image.save(tmpFileName)
  cmd = 'brother_ql -b pyusb -m '+printer['model']+' -p usb://'+printer['dev']+' print -l '+printer['size']+' -r auto '+tmpFileName
  reply = os.system(cmd)
  if reply>0:
    print('**ERROR mpq01: Printing error')
    image.show()
  return



def checkConfiguration(conf=None, repair=False):
  """
    Check configuration file .pastaELN.json for consistencies

  Args:
      conf   (dict): configuration to check
      repair (bool): repair configuration

  Returns:
      string: output incl. \n
  """
  import json, os
  from pathlib import Path
  from cloudant.client import CouchDB
  if conf is None:
    with open(Path.home()/'.pastaELN.json','r', encoding='utf-8') as fConf:
      conf = json.load(fConf)
  output = ''

  illegalNames = [key for key in conf if key.startswith('-')]
  if not 'softwareDir' in conf:
    output += '**ERROR mcc01a: No softwareDir in config file\n'
    if repair:
      conf['softwareDir'] = os.path.dirname(os.path.abspath(__file__))
  if not 'userID' in conf:
    output += '**ERROR mcc01b: No userID in config file\n'
    if repair:
      conf['userID'] = os.getlogin()
  if not 'magicTags' in conf:
    output += '**ERROR mcc01d: No magicTags in config file\n'
    if repair:
      conf['magicTags'] = []
  if not 'qrPrinter' in conf:
    output += '**ERROR mcc01e: No qrPrinter in config file\n'
    if repair:
      conf['qrPrinter'] = {}
  if not 'tableFormat' in conf:
    output += '**ERROR mcc01f: No tableFormat in config file\n'
    if repair:
      conf['tableFormat'] = {}
  if not 'extractors' in conf:
    output += '**ERROR mcc01g: No extractors in config file\n'
    if repair:
      conf['extractors'] = {}
  if not "version" in conf or conf['version']!=1:
    output += '**ERROR mcc01h: No or wrong version in config file\n'
    if repair:
      conf['version'] = 1
  if not "links" in conf:
    output += '**ERROR mcc01j: No links in config file; REPAIR MANUALLY\n'

  if not "default" in conf:
    output += '**ERROR mcc01k: No default links in config file\n'
    if repair and len(illegalNames)==0:
      conf['default'] = list(conf['links'].keys())[0]
  else:
    if not conf['default'] in conf['links']:
      output += '**ERROR mcc01i: default entry '+conf['default']+' not in links\n'
      if repair:
        conf['default'] = list(conf['links'].keys())[0]
  if len(illegalNames)>0:
    output += '**ERROR mcc01l: - type entries '+str(illegalNames)+' in config file\n'
    if repair:
      for key in illegalNames:
        del conf[key]
  if repair:
    with open(os.path.expanduser('~')+'/.pastaELN.json','w', encoding='utf-8') as f:
      f.write(json.dumps(conf,indent=2))
  if output=='':
    output='Verify configuration\nSUCCESS\n'
  else:
    output='Verify configuration\n'+output+'FAILURE\n'
  return output


def translateJS2PY():
  """
  Translate js-code to python-code using js2py lib
  - remove the last export-lines from commonTools.js
  """
  import re, io
  from pathlib import Path
  import js2py
  commonToolsHash = generic_hash(Path('../DOM/src/commonTools.js'))
  with open('./commonTools.py', encoding='utf-8') as fIn:
    stortedHash     = fIn.readlines()[-1]
  stortedHash = stortedHash.split('HASH:')[1].strip()
  if commonToolsHash!=stortedHash:
    with open('./commonTools.js', "r", encoding='utf-8').read() as jsString:
      jsString = re.sub(r"export.+;", "", jsString)
      jsFile = io.StringIO(jsString)
    js2py.translate_file(jsFile, 'commonTools.py')
    with open('./commonTools.py','a', encoding='utf-8') as fOut:
      fOut.write('\n# HASH: '+commonToolsHash)
    print('..success: translated commonTools.js->commonTools.py')
  return


def errorCodes(verbose=False):
  """
  go through all source files and list error codes

  Args:
     verbose (bool): print information about printing statements
  """
  import os, re, json
  ignoreFiles = ['checkAllVersions.py','commonTools.py']
  knownErrcodes = {
    "mcc01":"Click *MAINTENANCE* and *AUTOMATICALLY REPAIR CONFIGURATION*",
    "mcc02":"Repair with configuration-editor",
    "mcc03":"Repair with configuration-editor and restart",
    "mcc04":"Restart software using this local configuration:",
    "mcc05":"Please create path manually",
    ''
    "dit01":"Likely userName / password not correct"
  }
  output = 'automatically created MD file of error codes by miscTools:errorCodesp\n'
  if verbose:
    print('All terminal output')
  for fileName in os.listdir('.'):
    if not fileName.endswith('.py') or fileName in ignoreFiles:
      continue
    with open(fileName,'r', encoding='utf-8') as fIn:
      content = fIn.read().split('\n')
      errors = [' '+i.split('**ERROR')[1] for i in content if '**ERROR' in i and 'if' not in i]   #SKIP ME ErrorCode
      errors = [i for i in errors if '#SKIP ME ErrorCode' not in i]
      errors = [i.replace(")","").replace("\\n'",'').replace("+f'{bcolors.ENDC}","").replace(",'","") for i in errors]
    errorsNew = []
    for err in errors:
      result = re.match(r"^[\w]{3}[\d]{2}\w*:",err.strip())
      if result:
        errCode = result.group()[:-1]
        err = '  - '+errCode+':'+err.strip()[result.end():]
        if errCode[:5] in knownErrcodes:
          err += '\n    '+knownErrcodes[errCode[:5]]
      errorsNew.append(err)
    if len(errorsNew)>0:
      output+='# '+fileName+'\n'+'\n'.join(errorsNew)+'\n\n'
    prints = [i.strip() for i in content if i.strip().startswith('print') and "**ERROR" not in i]  #SKIP ME ErrorCode
    if verbose:
      print('\n\n'+fileName+'\n  '+'\n  '.join(prints))
  with open('../Documentation/errorCodes.md','w', encoding='utf-8') as fOut:
    fOut.write(output)
  jsonString = json.dumps(knownErrcodes).replace('"',"'")
  with open('../Electron/app/renderer/errorCodes.js','w', encoding='utf-8') as fOut:
    fOut.write('export const errorCodes =\n'+jsonString+'; // eslint-disable-line max-len')
  print('..success: assembled error-codes')
  return


###########################################
##### MAIN FUNCTION
###########################################
if __name__ == "__main__":
  translateJS2PY()    # translate js-code to python
  errorCodes()        # create overview of errorCodes
