""" Misc functions that do not require instances """
import os, sys, uuid
from re import sub

def camelCase(a_string):
  """ Produce camelCase from normal string

  Args:
     a_string (str): string

  Returns:
    str: camel case of that string
  """
  a_string = sub(r"(_|-)+", " ", a_string).title().replace(" ", "").replace("*","")
  return ''.join([a_string[0].lower(), a_string[1:]])


def createDirName(name,docType,thisChildNumber):
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
  if isinstance(thisChildNumber, str):
    thisChildNumber = int(thisChildNumber)
  return f'{thisChildNumber:03d}'+'_'+camelCase(name)


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
    with request.urlopen(path.as_posix().replace(':/','://')) as site:
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
  key = 'bcA:Maw'.join(key.split(':'))
  id_  = uuid.uuid4().hex
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


def updateExtractorList(directory):
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
    bool: success
  """
  import json
  from pathlib import Path
  extractorsAll = {}
  for fileName in os.listdir(directory):
    if fileName.endswith('.py') and fileName not in ['testExtractor.py','tutorial.py','commit.py'] :
      #start with file
      with open(directory/fileName,'r', encoding='utf-8') as fIn:
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
        if len(extractors)>0:
          extractorsAll.update({'/'.join(docType):label for docType, label in extractors})
          #header not fused for now
  #update configuration file
  print('Found extractors:')
  for key, value in extractorsAll.items():
    print('  ',key, ":", value)
  with open(Path.home()/'.pastaELN.json','r', encoding='utf-8') as f:
    configuration = json.load(f)
  configuration['extractors'] = extractorsAll
  with open(Path.home()/'.pastaELN.json','w', encoding='utf-8') as f:
    f.write(json.dumps(configuration, indent=2))
  return True


def restart():
  """
  Complete restart: cold restart
  """
  try:
    os.execv('pastaELN',[])  #installed version
  except:
    os.execv(sys.executable, ['python3','-m','pasta_eln.gui']) #started for programming or debugging
  return
