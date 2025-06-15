""" Misc functions that do not require instances """
import importlib
import json
import logging
import os
import platform
import subprocess
import sys
import tempfile
import traceback
from collections.abc import Mapping
from io import BufferedReader
from pathlib import Path
from typing import Any, Union
from urllib import request
import pandas as pd
from packaging.version import parse as parse_version
from PySide6.QtWidgets import QWidget  # pylint: disable=no-name-in-module
import pasta_eln
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
  hasher.update(b'blob {len(data)}\0')
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


def updateAddOnList(projectGroup:str='') -> dict[str, Any]:
  """
  Rules:
  - each data-type in its own try-except
  - inside try: raise ValueError exception on failure/None
  - except empty: pass
  - all descriptions in type have to be small letters
  - if want to force to skip top datatypes and use one at bottom: if doctype... -> exception

  Args:
    projectGroup (str): project group to scan

  Returns:
    dict: dict with all add-ons
  """
  with open(Path.home()/CONF_FILE_NAME, encoding='utf-8') as f:
    configuration = json.load(f)
  if not projectGroup:
    projectGroup = configuration['defaultProjectGroup']
  directory = Path(configuration['projectGroups'][projectGroup]['addOnDir'])
  sys.path.append(str(directory))  #allow add-ons
  # Add-Ons
  verboseDebug = False
  extractorsAll= {}
  otherAddOns:dict[str,dict[str,str]]  = {'project':{}, 'table':{} ,'definition':{} ,'form':{}, '_ERRORS_':{}}
  for fileName in os.listdir(directory):
    # Extractor
    if fileName.endswith('.py') and fileName.startswith('extractor_'):
      #start with file
      with open(directory/fileName, encoding='utf-8') as fIn:
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
          if 'if' in line and '#:' in line:
            if verboseDebug: print('line', line)
            specialType = line.split('==')[1].split(':')[0].strip(" '"+'"')
            if verboseDebug: print('  special',specialType)
            extractorsThis[specialType] = line.split('#:')[1].strip()
            ifInFile = True
          elif 'else:' in line and '#:' in line:
            print('**ERROR there should not be an else in the code')
          elif 'return' in line and 'recipe' in line and not ifInFile:
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
    # Project, et al.
    if fileName.endswith('.py') and '_' in fileName and fileName.split('_')[0] in ['project','table','definition','form']:
      name        = fileName[:-3]
      try:
        module      = importlib.import_module(name)
        description = module.description
        _ = module.reqParameter  # check if reqParameter exists
        otherAddOns[fileName.split('_')[0]][name] = description
      except Exception as e:
        description = f'** SYNTAX ERROR in add-on **: {e}'
        otherAddOns['_ERRORS_'][name] = description
  #update configuration file
  configuration['projectGroups'][projectGroup]['addOns']['extractors'] = extractorsAll
  configuration['projectGroups'][projectGroup]['addOns'] |= otherAddOns
  with open(Path.home()/CONF_FILE_NAME,'w', encoding='utf-8') as f:
    f.write(json.dumps(configuration, indent=2))
  return {'addon directory':directory} | extractorsAll | otherAddOns


def callAddOn(name:str, backend:Any, content:Any, widget:QWidget) -> Any:
  """ Call add-ons
  Args:
    name (str): name of the add-on
    backend (str): backend to be used
    content (Any): content to be consumed by addon, e.g. projectID, document
    widget: widget to be used

  Returns:
    Any: result of the add-on
  """
  module      = importlib.import_module(name)
  parameter   = backend.configuration.get('addOnParameter', {})
  try:
    subParameter = parameter[name]
  except KeyError:
    print('**Info: No parameter for this add-on')
    subParameter = {}
  return module.main(backend, content, widget, subParameter)


def callDataExtractor(filePath:Path, backend:Any) -> Any:
  """ Call data extractor for a given file path: CALL THE DATA FUNCTION

  Args:
    filePath (Path): path to file
    backend (str): backend

  Returns:
    Any: result of the data extractor
  """
  extension = filePath.suffix[1:]  #cut off initial . of .jpg
  if str(filePath).startswith('http'):
    absFilePath = Path(tempfile.gettempdir())/filePath.name
    with request.urlopen(filePath.as_posix().replace(':/','://'), timeout=60) as urlRequest:
      with open(absFilePath, 'wb') as f:
        try:
          f.write(urlRequest.read())
        except Exception:
          print('Error saving downloaded file to temporary disk')
  else:
    if filePath.is_absolute():
      filePath  = filePath.relative_to(backend.basePath)
    absFilePath = backend.basePath/filePath
  pyFile = f'extractor_{extension.lower()}.py'
  pyPath = backend.addOnPath/pyFile
  if pyPath.is_file():
    # import module and use to get data
    try:
      module = importlib.import_module(pyFile[:-3])
      return module.data(absFilePath, {})
    except Exception as e:
      print('**Warning** CallDataExtractor:',e)
  return None


def isFloat(val:str) -> bool:
  """Check if a value can be converted to float.
  Args:
    val (str): value to check
  Returns:
    bool: True if value can be converted to float, False otherwise
  """
  try:
    float(val)
    return True
  except (ValueError, TypeError):
    return False


def dfConvertColumns(df:pd.DataFrame, ratio:int=10) -> pd.DataFrame:
  """Convert columns in a DataFrame to numeric if a significant
  portion of the column can be converted

  Args:
    df (pd.DataFrame): DataFrame with columns to convert
    ratio (int): threshold ratio to determine if a column should be converted

  Returns:
    pd.DataFrame: DataFrame with converted columns
  """
  for col in df.columns:
    numConvertible = df[col].apply(isFloat).sum()
    if numConvertible > len(df) / ratio:
      df[col] = pd.to_numeric(df[col], errors='coerce')
  return df



def restart() -> None:
  """
  Complete restart: cold restart
  """
  try:
    os.execv('pastaELN',[''])  #installed version
  except Exception:
    os.execv(sys.executable, ['python3','-m','pasta_eln.gui']) #started for programming or debugging
  return


def testNewPastaVersion(update:bool=False) -> bool:
  """ Test if this version is up to date with the latest version on pypi
  - variable largestVersionOnPypi is the latest NON-BETA version on pypi

  Args:
    update (bool): update to latest version

  Returns:
    bool: if up-to-date or if current version is a beta
  """
  if update:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pasta-eln'])
    restart()
  url = 'https://pypi.org/pypi/pasta-eln/json'
  with request.urlopen(url) as response:
    data = json.loads(response.read())
  releases = list(data['releases'].keys())
  largestVersionOnPypi = sorted(releases, key=parse_version)[-1]
  return largestVersionOnPypi == pasta_eln.__version__ or 'b' in pasta_eln.__version__


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
def flatten(d:dict[Any,Any], keepPastaStruct:bool=False) -> dict[object, Any]:
  """Flatten `Mapping` object.

  Args:
    d : dict-like object
        The dict that will be flattened.
    keepPastaStruct : bool
        keep pasta elements from flattening

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
  backup = {'type':d.pop('type',''), 'branch':d.pop('branch',''), 'tags':d.pop('tags',''),
            'gui':d.pop('gui',''), 'qrCodes':d.pop('qrCodes',''), '_ids':d.pop('_ids','')} \
           if keepPastaStruct else {}
  _flatten(d, depth=1)
  return flat_dict | {k:v for k,v in backup.items() if v}


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
    keys = tuple(flat_key.split('.'))
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
