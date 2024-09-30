""" Misc functions that do not require instances """
import os, logging, traceback, json, sys
from collections.abc import Mapping
from typing import Any, Union
from io import BufferedReader
from urllib import request
from pathlib import Path
import platform
from .fixedStringsJson import CONF_FILE_NAME

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
      logging.error('Could not download content / hashing issue %s \n%s',path.as_posix().replace(':/','://'),traceback.format_exc())
      return ''
  if path.is_dir():
    raise ValueError(f'This seems to be a directory {path.as_posix()}')
  if forceFile and path.is_symlink():
    path = path.resolve()
  shasum = ''
  if path.is_symlink():    #if link, hash the link
    shasum = symlink_hash(path)
  elif path.is_file():  #Local file
    with open(path, 'rb') as stream:
      shasum = blob_hash(stream, path.stat().st_size)
  return shasum


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


def updateExtractorList(directory:Path|None=None) -> dict[str, Any]:
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
    dict: dict with all extractors
  """
  if directory is None:
    with open(Path.home()/CONF_FILE_NAME,'r', encoding='utf-8') as f:
      configuration = json.load(f)
      directory = Path(configuration["extractorDir"])
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
  with open(Path.home()/CONF_FILE_NAME,'r', encoding='utf-8') as f:
    configuration = json.load(f)
  configuration['extractors'] = extractorsAll
  with open(Path.home()/CONF_FILE_NAME,'w', encoding='utf-8') as f:
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
  def setValue(self, value:int) -> int:
    """
    Set value

    Args:
      value (int): value to be set
    """
    return value
  def show(self) -> None:
    """ show progress bar """
    return
  def hide(self) -> None:
    """ hide progress bar """
    return


# adapted from flatten-dict https://github.com/ianlini/flatten-dict
# - reduce dependencies and only have python 3 code
# - add conversion of dict to list if applicable
def flatten(d:Mapping[Any,Any]) -> dict[object, Any]:
  """Flatten `Mapping` object.

  Args:
    d : dict-like object
        The dict that will be flattened.

  Returns:
    flat_dict : dict
  """
  enumerate_types=(list,)
  flatten_types = (Mapping,) + enumerate_types
  flat_dict = {}

  def dot_reducer(k1:object, k2:object) -> Union[str, object]:
    """ Reducer function """
    return k2 if k1 is None else f"{k1}.{k2}"

  def _flatten(_d:Union[Mapping[Any, Any], list[Any]], depth:int, parent:object=None) -> bool:
    """ Recursive function """
    key_value_iterable = (enumerate(_d) if isinstance(_d, enumerate_types) else _d.items())
    has_item = False
    for key, value in key_value_iterable:
      has_item = True
      flat_key = dot_reducer(parent, key)
      if isinstance(value, flatten_types):
        # recursively build the result
        has_child = _flatten(value, depth=depth + 1, parent=flat_key)
        if has_child or not isinstance(value, ()): # ignore the key in this level because it already has child key or its value is empty
          continue
      # add an item to the result
      if flat_key in flat_dict:
        raise ValueError(f"duplicated key '{flat_key}'")
      flat_dict[flat_key] = value
    return has_item

  # start recursive calling
  _flatten(d, depth=1)
  return flat_dict


def hierarchy(d:dict[str,Any]) -> dict[str,Any]:
  """Reverse flattening of dict-like object

  Args:
    d : dict-like object
      The dict that will be reversed

  Returns
    normalDict : dict
  """
  def dot_splitter(flat_key:str) -> tuple[str, ...]:
    """ split using the . symbol """
    keys = tuple(flat_key.split("."))
    return keys

  def nested_set_dict(d:dict[str,Any], keys:tuple[str, ...], value:Any) -> None:
    """Set a value to a sequence of nested keys

    Args:
      d : Mapping
      keys : Sequence[str]
      value : Any
    """
    key = keys[0]
    if len(keys) == 1:
      if key in d:
        raise ValueError(f"duplicated key '{key}'")
      d[key] = value
      return
    d = d.setdefault(key, {})
    nested_set_dict(d, keys[1:], value)
    return

  def dict2list(d:dict[str,Any]) -> Union[list[dict[str,Any]], dict[str,Any]]:
    """ convert a dictionary to list if all keys are numbers """
    for key in d:
      if isinstance(d[key], dict):
        d[key] = dict2list(d[key])
    if all(i.isdigit() for i in d):
      d = list(d.values())                                                           # type: ignore[assignment]
    return d

  # start recursion
  normalDict:dict[str,Any] = {}
  for flat_key, value in d.items():
    key_tuple = dot_splitter(flat_key)
    nested_set_dict(normalDict, key_tuple, value)
  normalDict =  dict2list(normalDict)                                                # type: ignore[assignment]
  return normalDict
