""" Misc functions that do not require instances """
import os, uuid, logging, traceback, json, sys, re
from typing import Any
from io import BufferedReader
from urllib import request
from pathlib import Path
from re import sub, match
import platform
from .handleDictionaries import dict2ul

class Bcolors:
  """
  Colors for Command-Line-Interface and output
  """
  if platform.system()=='Windows':
    HEADER = ''
    OKBLUE = ''
    OKGREEN = ''
    WARNING = ''
    FAIL = ''
    ENDC = ''
    BOLD = ''
    UNDERLINE = ''
  else:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def outputString(fmt:str='print', level:str='info', message:str='') -> str:
  """ Output a message into different formats:
    - print: print to stdout
    - logging; log to file
    - text: return text string (supersedes html)
    - html: return html string https://doc.qt.io/qtforpython/overviews/richtext-html-subset.html#supported-html-subset
    - else: no output
    - formats can be union ('print,text')
  """
  prefixes = {'h2':f'{Bcolors.UNDERLINE}\n*** ','bold':f'{Bcolors.BOLD}\n*** ', \
              'ok':f'{Bcolors.OKGREEN}', 'okish':f'{Bcolors.OKBLUE}', 'unsure':f'{Bcolors.HEADER}',\
              'warning':f'{Bcolors.WARNING}**Warning','error':f'{Bcolors.FAIL}**ERROR '}
  if level=='info':
    txtOutput = message.strip()+'\n'
  elif level in prefixes:
    txtOutput = prefixes[level]+message
    txtOutput+= ' ***' if '***' in prefixes[level] else ''
    txtOutput+= f'{Bcolors.ENDC}\n'
  else:
    print('ERROR level not in prefixes ',level)
  # depend on format
  if 'print' in fmt:
    print(txtOutput)
  if 'logging' in fmt and level in {'info', 'warning', 'error'}:
    getattr(logging,level)(message)
  if 'text' in fmt:
    return txtOutput
  if fmt=='html':
    colors = {'info':'black','error':'red','warning':'orangered','ok':'green','okish':'blue','unsure':'darkmagenta'}
    if level[0]=='h':
      return f'<{level}>{message}</{level}>'
    if level not in colors:
      print(f'**ERROR: wrong level {level}')
      return ''
    return f'<font color="{colors[level]}">' + message.replace('\n', '<br>') + '</font><br>'
  return ''


def tracebackString(log:bool=False, docID:str='') -> str:
  """ Create a formatted string of traceback

  Args:
    log (bool): write to logging
    docID (str): docID used in comment

  Returns:
    str: | separated string of call functions
  """
  tracebackList = [i for i in traceback.format_stack()[2:-2] if 'pasta_eln' in i] #skip first and last and then filter only things with pasta_eln
  reply = '|'.join([item.split('\n')[1].strip() for item in tracebackList])  #| separated list of stack excluding last
  if log:
    logging.info(' traceback %s %s', docID, reply)
  return reply


def markdownStyler(text:str) -> str:
  """
  Create a markdown that well balanced with regard to font size, etc.

  Args:
    text (str): input string

  Returns:
    str: output str
  """
  return re.sub(r'(^|\n)(#+)', r'\1##\2', text.strip())


def camelCase(text:str) -> str:
  """
  Produce camelCase from normal string
  - file names abcdefg.hij are only replaced spaces

  Args:
     text (str): string

  Returns:
    str: camel case of that string: CamelCaseString
  """
  if match(r"^[\w-]+\.[\w]+$", text):
    return text.replace(' ','_')
  return sub(r"(_|-)+", ' ', text).title().replace(' ','').replace('*','')


def createDirName(name:str, docType:str, thisChildNumber:int) -> str:
  """ create directory-name by using camelCase and a prefix

  Args:
      name (string): name with spaces etc.
      docType (string): document type used for prefix
      thisChildNumber (int): number of myself

  Returns:
    string: directory name with leading number
  """
  if docType == 'x0':
    return camelCase(name)
  #steps, tasks
  return f'{thisChildNumber:03d}_{camelCase(name)}'


def generic_hash(path:Path, forceFile:bool=False) -> str:
  """
  Hash an object based on its mode.

  inspired by:
  https://github.com/chris3torek/scripts/blob/master/githash.py

  Example implementation:
      result = generic_hash(sys.argv[1])
      print('%s: hash = %s' % (sys.argv[1], result))

  Args:
    path (Path): path
    forceFile (bool): force to get shasum of file and not of link (False for gitshasum)

  Returns:
    string: shasum

  Raises:
    ValueError: shasum of directory not supported
  """
  if str(path).startswith('http'):                      #Remote file:
    try:
      with request.urlopen(path.as_posix().replace(':/','://'), timeout=60) as site:
        meta = site.headers
        size = int(meta.get_all('Content-Length')[0])
        return blob_hash(site, size)
    except Exception:
      logging.error('Could not download content / hashing issue '+path.as_posix().replace(':/','://')+'\n'+\
        traceback.format_exc())
      return ''
  if path.is_dir():
    raise ValueError(f'This seems to be a directory {path.as_posix()}')
  if forceFile and path.is_symlink():
    path = path.resolve()
  if path.is_symlink():    #if link, hash the link
    shasum = symlink_hash(path)
  elif path.is_file():  #Local file
    with open(path, 'rb') as stream:
      shasum = blob_hash(stream, path.stat().st_size)
  return shasum


def upOut(key:str) -> list[str]:
  """
  key (str): key
  """
  import keyring as cred
  keys = key.split() if ' ' in key else [key]
  keys_ = []
  for keyI in keys:
    key_ = cred.get_password('pastaDB',keyI)
    key_ = ':' if key_ is None else ':'.join(key_.split('bcA:Maw'))
    keys_.append(key_)
  return keys_


def upIn(key:str) -> str:
  """
  key (str): key
  """
  import keyring as cred
  key = 'bcA:Maw'.join(key.split(':'))
  id_  = uuid.uuid4().hex
  cred.set_password('pastaDB',id_,key)
  return id_


def symlink_hash(path:Path) -> str:
  """
  Return (as hash instance) the hash of a symlink.
  Caller must use hexdigest() or digest() as needed on
  the result.

  Args:
    path (string): path to symlink

  Returns:
    string: shasum of link, aka short string
  """
  from hashlib import sha1
  hasher = sha1()
  data = os.readlink(path).encode('utf8', 'surrogateescape')
  hasher.update('blob {len(data)}\0'.encode('ascii'))
  hasher.update(data)
  return hasher.hexdigest()


def blob_hash(stream:BufferedReader, size:int) -> str:
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


def updateExtractorList(directory:Path) -> dict[str, Any]:
  """
  Rules:
  - each data-type in its own try-except
  - inside try: raise ValueError exception on failure/None
  - except empty: pass
  - all descriptions in type have to be small letters
  - if want to force to skip top datatypes and use one at bottom: if doctype... -> exception

  Args:
    directory (str): relative directory to scan

  Returns:
    bool: success
  """
  verboseDebug = False
  extractorsAll = {}
  for fileName in os.listdir(directory):
    if fileName.endswith('.py') and fileName not in {'testExtractor.py','tutorial.py','commit.py'}:
      #start with file
      with open(directory/fileName,'r', encoding='utf-8') as fIn:
        if verboseDebug: print('\n'+fileName)
        lines = fIn.readlines()
        extractorsThis = {}
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
            if verboseDebug: print('line', line)
            specialType = line.split("==")[1].split(":")[0].strip(" '"+'"')
            if verboseDebug: print('  special',specialType)
            extractorsThis[specialType] = line.split('#:')[1].strip()
            ifInFile = True
          elif "else:" in line and "#:" in line:
            print('**ERROR there should not be an else in the code')
          elif "return" in line and 'recipe' in line and not ifInFile:
            if verboseDebug: print('line', line)
            if line.count('recipe')==1:
              linePart = line.split('recipe')[1].strip()
              linePart = linePart.split(':')[1].split(',')[0].strip(" '"+'"')
            elif line.count('recipe')==2:
              possLines = [i.strip() for i in lines if ('recipe' in i and '=' in i and 'def' not in i)]
              if len(possLines)==1:
                linePart=possLines[0].split('=')[1].strip(" '"+'"')
              elif len(possLines)>1:
                print(f'**Warning: Could not decipher {fileName} Take shortest!')
                linePart=sorted(possLines)[0].split('=')[1].strip(" '"+'"')
              else:
                print(f'**ERROR: Could not decipher {fileName} File does not work!')
                linePart=''
            extractorsThis[linePart]='Default'
            if verboseDebug:
              print('  return', linePart)
        if verboseDebug:
          print('Extractors', extractorsThis)
        ending = fileName.split('_')[1].split('.')[0]
        extractorsAll[ending]=extractorsThis
                    #header not used for now
  #update configuration file
  with open(Path.home()/'.pastaELN.json','r', encoding='utf-8') as f:
    configuration = json.load(f)
  configuration['extractors'] = extractorsAll
  with open(Path.home()/'.pastaELN.json','w', encoding='utf-8') as f:
    f.write(json.dumps(configuration, indent=2))
  return extractorsAll


def restart() -> None:
  """
  Complete restart: cold restart
  """
  try:
    os.execv('pastaELN',[''])  #installed version
  except Exception:
    os.execv(sys.executable, ['python3','-m','pasta_eln.gui']) #started for programming or debugging
  return


class DummyProgressBar():
  """ Class representing a progressbar that does not do anything
  """
  def setValue(self, value:int) -> None:
    """
    Set value

    Args:
      value (int): value to be set
    """
    return
  def show(self) -> None:
    """ show progress bar """
    return
  def hide(self) -> None:
    """ hide progress bar """
    return
