""" Misc functions that do not require instances """
import importlib
import json
import logging
import os
import platform
import socket
import subprocess
import sys
import tempfile
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Union
from urllib import request
import pandas as pd
from anytree import Node
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from packaging.version import parse as parse_version
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget
import pasta_eln
from .fixedStringsJson import CONF_FILE_NAME, configurationGUI, defaultConfiguration


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
  sys.path.append(str(directory))                                                               #allow add-ons
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
            otherAddOns['_ERRORS_'][fileName] = 'ERROR there should not be an else in the code'
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
                logging.warning('Could not decipher %s. Take shortest!', fileName)
                linePart=sorted(possLines)[0].split('=')[1].strip(" '"+'"')
              else:
                otherAddOns['_ERRORS_'][fileName] = 'ERROR could not decipher code'
                linePart=''
            extractorsThis[linePart]='Default'
            if verboseDebug:
              print('  return', linePart)
        if verboseDebug:
          print('Extractors', extractorsThis)
        ending = fileName.split('_')[1].split('.')[0]
        extractorsAll[ending]=extractorsThis
    # header not used for now
    # Project, et al
    if fileName.endswith('.py') and '_' in fileName and fileName.split('_')[0] in ['project','table','definition','form']:
      name        = fileName[:-3]
      try:
        module      = importlib.import_module(name)
        description = module.description
        _ = module.reqParameter                                                 # check if reqParameter exists
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


def installPythonPackages(directory:str) -> None:
  """Install a Python packages using pip depending on files in add-on folder
  Args:
    directory (str): path to the add-on folder
  """
  allLibs = set()
  for fileName in os.listdir(directory):
    if fileName.endswith('.py'):
      #start with file
      with open(Path(directory)/fileName, encoding='utf-8') as fIn:
        lines = [i.strip() for i in fIn.readlines() if 'import' in i]
        libsList =  [i.split('import')[1].strip().split(',') for i in lines if i.startswith('import')]
        libs =  [i.strip() for j in libsList for i in j]
        libs += [i.split('from')[1].strip().split('import')[0].strip() for i in lines if i.startswith('from')]
        libs = [i.split('.')[0] for i in libs]                                           #only look at package
        libs = [i.split()[0] for i in libs]                                  #get rid of all things at the end
        allLibs.update(libs)
  allLibs = allLibs.difference(sys.stdlib_module_names)        # all libs that are not in the standard library
  allLibs = allLibs.difference([i[:-3] for i in os.listdir(directory) if i.endswith('.py')])#remove all libs that are in the directory
  allLibs = allLibs.difference({i.split('.')[0] for i in sys.modules})# remove libs used by pasta, already in use
  for lib in allLibs:
    try:
      importlib.import_module(lib)                                 # check if the package is already installed
    except ImportError:
      if lib == 'sklearn':
        lib = 'scikit-learn'
      subprocess.check_call([sys.executable, '-m', 'pip', 'install', lib])
  return


def callAddOn(name:str, comm:Any, content:Any, widget:QWidget) -> Any:
  """ Call add-ons
  Args:
    name (str): name of the add-on
    comm (Any): communication object
    content (Any): content to be consumed by addon, e.g. projectID, document
    widget: widget to be used

  Returns:
    Any: result of the add-on
  """
  module      = importlib.import_module(name)
  parameter   = comm.configuration.get('addOnParameter', {})
  try:
    subParameter = parameter[name]
  except KeyError:
    print('**Info: No parameter for this add-on')
    subParameter = {}
  return module.main(comm, content, widget, subParameter)


def callDataExtractor(filePath:Path, backend:Any) -> Any:
  """ Call data extractor for a given file path: CALL THE DATA FUNCTION

  Args:
    filePath (Path): path to file
    backend (str): backend

  Returns:
    Any: result of the data extractor
  """
  if not isinstance(filePath, Path):
    filePath = Path(filePath)
  extension = filePath.suffix[1:]                                                   #cut off initial . of .jpg
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
      logging.warning('CallDataExtractor: %s',e)
  return None


def getHierarchy(comm:Any, docID:str, showAll:bool=True) -> tuple[Node, dict[str, Any]]:
  """ Helper for add-ons: get hierarchy of a project from backend
  Args:
    comm (Communicate): communicate-backend
    docID (str): project ID
    showAll (bool): show all nodes, even hidden ones

  Returns:
    tuple: (hierarchy as anytree, project document as dict)
  """
  hierarchyI = None
  projDoc   = None
  @Slot(Node, dict)
  def receiveData(h:Node, doc:dict[str,Any]) -> None:
    nonlocal hierarchyI
    hierarchyI = h
    nonlocal projDoc
    projDoc   = doc
  comm.backendThread.worker.beSendHierarchy.connect(receiveData)
  comm.uiRequestHierarchy.emit(docID, showAll)
  while hierarchyI is None or projDoc is None:
    time.sleep(0.1)
  return hierarchyI, projDoc


def getDoc(comm:Any, docID:str) -> dict[str, Any]:
  """ Helper for add-ons: get document from backend

  Args:
    comm (Communicate): communicate-backend
    docID (str): document ID

  Returns:
    dict: document as dict
  """
  doc = None
  @Slot(dict)
  def receiveData(iDoc:dict[str,Any]) -> None:
    """ Slot to receive data
    Args:
      iDoc (dict): document
    """
    nonlocal doc
    doc = iDoc
  comm.backendThread.worker.beSendDoc.connect(receiveData)
  comm.uiRequestDoc.emit(docID)
  while doc is None:
    time.sleep(0.1)
  return doc


def isFloat(val:str) -> bool:
  """Check if a value can be converted to float
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


class MplCanvas(FigureCanvas):
  """ Canvas to draw upon """
  def __init__(self, _:Any=None, width:float=5, height:float=4, dpi:int=100):
    """
    Args:
      _ (Any): figure
      width (float): width in inch
      height (float): height in inch
      dpi (int): dots per inch
    """
    self.figure = Figure(figsize=(width, height), dpi=dpi)
    self.axes   = self.figure.add_subplot(111)
    super().__init__(self.figure)


def getConfiguration(defaultProjectGroup:str='') -> tuple[dict[str, Any],str]:
  """ Get configuration from home directory
  Args:
    defaultProjectGroup (str): project group to use, if not given, use default
  Returns:
    tuple: configuration dict and default project group
  """
  configuration = defaultConfiguration
  configFileName = Path.home() / CONF_FILE_NAME
  if configFileName.is_file():
    with open(configFileName, encoding='utf-8') as confFile:
      configuration |= json.load(confFile)
  for _, items in configurationGUI.items():
    for k,v in items.items():
      if k not in configuration['GUI']:
        configuration['GUI'][k] = v[1]
  if configuration['version'] != 3:
    print('**Info: configuration file does not exist or version is != 3')
    return {},''
  defaultProjectGroup = defaultProjectGroup or configuration['defaultProjectGroup']
  if defaultProjectGroup not in configuration['projectGroups']:
    raise ValueError(f'BadConfigurationFileError: {defaultProjectGroup} not in projectGroups')
  return configuration, defaultProjectGroup


def hardRestart() -> None:
  """
  Complete restart: cold restart
  """
  try:
    os.execv('pastaELN',[''])                                                               #installed version
  except Exception:
    os.execv(sys.executable, [sys.executable,'-m','pasta_eln.gui'])      #started for programming or debugging
  return


def isConnectedToInternet() -> bool:
  """Check if the system is connected to the internet

  Returns:
    bool: True if connected, False otherwise
  """
  try:
    socket.setdefaulttimeout(3)
    socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('8.8.8.8', 53))
    return True
  except OSError:
    pass
  return False


def testNewPastaVersion(update:bool=False) -> bool:
  """ Test if this version is up to date with the latest version on pypi
  - variable largestVersionOnPypi is the latest NON-BETA version on pypi

  Args:
    update (bool): update to latest version

  Returns:
    bool: if up-to-date or if current version is a beta
  """
  if not isConnectedToInternet():
    return True
  if update:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pasta-eln'])
    hardRestart()
  url = 'https://pypi.org/pypi/pasta-eln/json'
  with request.urlopen(url) as response:
    data = json.loads(response.read())
  releases = [i for i in list(data['releases'].keys()) if 'b' not in i]                 # remove beta versions
  largestVersionOnPypi = sorted(releases, key=parse_version)[-1]
  return largestVersionOnPypi == pasta_eln.__version__ or 'b' in pasta_eln.__version__


# adapted from flatten-dict https://github.com/ianlini/flatten-dict
# - reduce dependencies and only have python 3 code
# - add conversion of dict to list if applicable
def flatten(d:dict[Any,Any], keepPastaStruct:bool=False) -> dict[object, Any]:
  """Flatten `Mapping` object

  Args:
    d : dict-like object
        The dict that will be flattened
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
    key_value_iterable = enumerate(_d) if isinstance(_d, enumerate_types) else _d.items()
    has_item = False
    for key, value in key_value_iterable:
      has_item = True
      flat_key = dot_reducer(parent, key)
      if isinstance(value, flatten_types):
        # recursively build the result
        has_child = _flatten(value, depth=depth + 1, parent=flat_key)
        if has_child or not isinstance(value, ()):# ignore key in this level because it already has child key or its value is empty
          continue
      if flat_key in flat_dict and parent is not None:
        continue  # skip if key already exists and if data comes from database after merging with changed data
      # add an item to the result
      flat_dict[flat_key] = value
    return has_item

  # start recursive calling
  backup = {'type':d.pop('type',None), 'branch':d.pop('branch',None),   'tags':d.pop('tags',None),
            'gui':d.pop('gui',None),   'qrCodes':d.pop('qrCodes',None), '_ids':d.pop('_ids',None)} \
           if keepPastaStruct else {}
  _flatten(d, depth=1)
  return flat_dict | {k:v for k,v in backup.items() if v is not None}


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
      d = list(d.values())                                                          # type: ignore[assignment]
    return d

  # start recursion
  normalDict:dict[str,Any] = {}
  for flat_key, value in d.items():
    key_tuple = dot_splitter(flat_key)
    nested_set_dict(normalDict, key_tuple, value)
  normalDict =  dict2list(normalDict)                                               # type: ignore[assignment]
  return normalDict
