""" Misc functions that do not require instances """
import hashlib
import importlib
import json
import logging
import os
import platform
import re
import socket
import subprocess
import sys
import tempfile
import time
from collections.abc import Mapping
from pathlib import Path
from types import ModuleType
from typing import Any, Union
from urllib import request
import pandas as pd
import requests
from anytree import Node
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from packaging.version import parse as parse_version
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget
import pasta_eln
from .fixed_strings_json import confFileName, configurationGUI, defaultConfiguration


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
  with open(Path.home()/confFileName, encoding='utf-8') as f:
    configuration = json.load(f)
  if not projectGroup:
    projectGroup = configuration['defaultProjectGroup']
  directory = Path(configuration['projectGroups'][projectGroup]['addOnDir'])
  if str(directory) not in sys.path:
    sys.path.insert(0, str(directory))                                                          # allow add-ons
  # Add-Ons
  verboseDebug = False
  extractorsAll= {}
  otherAddOns:dict[str,dict[str,str]]  = {'project':{}, 'table':{} ,'definition':{} ,'form':{}}
  errors:dict[str,str] = {}
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
            errors[fileName] = 'ERROR there should not be an else in the code'
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
                errors[fileName] = 'ERROR could not decipher code'
                linePart=''
            extractorsThis[linePart]='Default'
            if verboseDebug:
              print('  return', linePart)
        linesWithUse = [i for i in lines if 'use(' in i]
        if len(linesWithUse)>1:
          extractorsThis = {}
          errors[fileName] = 'ERROR two use( in the code'
        if verboseDebug:
          print('Extractors', extractorsThis)
        ending = fileName.split('_')[1].split('.')[0]
        extractorsAll[ending]=extractorsThis
    # header not used for now
    # Project, et al
    if fileName.endswith('.py') and '_' in fileName and fileName.split('_')[0] in ['project','table','definition','form']:
      name        = fileName[:-3]
      try:
        module      = loadNamedModule(directory, name)
        description = module.description
        _ = module.reqParameter                                                 # check if reqParameter exists
        otherAddOns[fileName.split('_')[0]][name] = description
      except Exception as e:
        errors[name] = f'** SYNTAX ERROR in add-on **: {e}'
  #update configuration file
  configuration['projectGroups'][projectGroup]['addOns']['extractors'] = extractorsAll
  configuration['projectGroups'][projectGroup]['addOns'] |= otherAddOns
  with open(Path.home()/confFileName,'w', encoding='utf-8') as f:
    f.write(json.dumps(configuration, indent=2))
  return {'addon directory':directory} | errors | extractorsAll | otherAddOns


def _moduleKey(modulePath:Path) -> str:
  """Create a deterministic private module name for a file path.
  Args:
    modulePath (Path): path to the module
  Returns:
    str: module name for this file path
  """
  resolved = modulePath.resolve()
  digest = hashlib.sha256(str(resolved).encode('utf-8')).hexdigest()[:16]
  return f'_pasta_add_on_{resolved.stem}_{digest}'


def loadNamedModule(directory:Path, moduleName:str) -> ModuleType:
  """Load a Python module directly from the configured file path.
  Args:
    modulePath (Path): path to the module
  Returns:
    Module Type: module
  """
  modulePath = directory/f'{moduleName}.py'
  resolved = modulePath.resolve()
  if not resolved.is_file():
    raise FileNotFoundError(resolved)
  moduleName = _moduleKey(resolved)
  spec = importlib.util.spec_from_file_location(moduleName, resolved)
  if spec is None or spec.loader is None:
    raise ImportError(f'Could not create loader for {resolved}')
  module = importlib.util.module_from_spec(spec)
  sys.modules[moduleName] = module
  spec.loader.exec_module(module)
  return module


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
  module      = loadNamedModule(Path(comm.addOnPath), name)
  parameter   = comm.configuration.get('addOnParameter', {})
  try:
    subParameter = parameter[name]
  except KeyError:
    print('**Info: No parameter for this add-on')
    subParameter = {}
  return module.main(comm, content, widget, subParameter)


def callDataExtractor(docID:str, comm:Any) -> Any:
  """ Call data extractor for a given file path: CALL THE DATA FUNCTION

  Args:
    docID (str): docID
    comm (Communication): communication layer

  Returns:
    Any: result of the data extractor
  """
  doc = getDoc(comm, docID)
  filePath = comm.basePath/doc['branch'][0]['path']
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
      filePath  = filePath.relative_to(comm.basePath)
    absFilePath = comm.basePath/filePath
  pyFile = f'extractor_{extension.lower()}.py'
  pyPath = Path(comm.addOnPath)/pyFile
  if pyPath.is_file():
    # import module and use to get data
    try:
      module = loadNamedModule(Path(comm.addOnPath), pyFile[:-3])
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


def isDocID(val:str) -> bool:
  """Check if a value is a docID
  Args:
    val (str): value to check
  Returns:
    bool: True if value is a docID, False otherwise
  """
  return re.match(r'^[a-z\-]-[a-z0-9]{32}$', val) is not None


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
  configFileName = Path.home() / confFileName
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
    listPossible = list(configuration['projectGroups'].keys())
    raise ValueError(f'BadProjectGroup: {defaultProjectGroup}. Possible: {listPossible}')
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


def getRORIDLabel(idString:str) -> str :
  """ Get label from RORID
  Args:
    idString (str): RORID
  Returns:
    str: label of the RORID
  """
  reply = requests.get(f'https://api.ror.org/organizations/{idString}', timeout=10)
  labels = [i for i in reply.json()['names'] if 'ror_display' in i['types']]
  labels = labels or [i for i in reply.json()['names'] if 'acronym' not in i['types']]
  labels = labels or reply.json()['names']
  return labels[0]['value'] if labels else ''


def getORCIDName(idString:str) -> tuple[str, str]:
  """ Get name from ORCID
  Args:
    idString (str): ORCID
  Returns:
    tuple: (first name, last name)
  """
  reply = requests.get(f'https://pub.orcid.org/v3.0/{idString}', timeout=10)
  text = reply.content.decode()
  first = text.split('<personal-details:given-names>')[1].split('</personal-details:given-names>')[0]
  last = text.split('<personal-details:family-name>')[1].split('</personal-details:family-name>')[0]
  return first, last


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
  try:
    url = 'https://pypi.org/pypi/pasta-eln/json'
    with request.urlopen(url) as response:
      data = json.loads(response.read())
  except Exception:
    return True
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
  enumerateTypes=(list,)
  flattenTypes = (Mapping,) + enumerateTypes
  flatDict = {}

  def dotReducer(k1:object, k2:object) -> Union[str, object]:
    """ Reducer function """
    return k2 if k1 is None else f"{k1}.{k2}"

  def _flatten(_d:Union[Mapping[Any, Any], list[Any]], depth:int, parent:object=None) -> bool:
    """ Recursive function """
    keyValueIterable = enumerate(_d) if isinstance(_d, enumerateTypes) else _d.items()
    hasItem = False
    for key, value in keyValueIterable:
      hasItem = True
      flatKey = dotReducer(parent, key)
      if isinstance(value, flattenTypes):
        # recursively build the result
        hasChild = _flatten(value, depth=depth + 1, parent=flatKey)
        if hasChild or not isinstance(value, ()):# ignore key in this level because it already has child key or its value is empty
          continue
      if flatKey in flatDict and parent is not None:
        continue  # skip if key already exists and if data comes from database after merging with changed data
      # add an item to the result
      flatDict[flatKey] = value
    return hasItem

  # start recursive calling
  backup = {'type':d.pop('type',None), 'branch':d.pop('branch',None),   'tags':d.pop('tags',None),
            'gui':d.pop('gui',None),   'qrCodes':d.pop('qrCodes',None), '_ids':d.pop('_ids',None)} \
           if keepPastaStruct else {}
  _flatten(d, depth=1)
  return flatDict | {k:v for k,v in backup.items() if v is not None}


def hierarchy(d:dict[str,Any]) -> dict[str,Any]:
  """Reverse flattening of dict-like object

  Args:
    d : dict-like object
      The dict that will be reversed

  Returns
    normalDict : dict
  """
  def dotSplitter(flatKey:str) -> tuple[str, ...]:
    """ split using the . symbol """
    keys = tuple(flatKey.split('.'))
    return keys

  def nestedSetDict(d:dict[str,Any], keys:tuple[str, ...], value:Any) -> None:
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
      try:
        d[key] = value
      except TypeError as e:
        print('TypeError:', type(d), d, type(key), key, type(value), value)
        raise e
      return
    d = d.setdefault(key, {})
    nestedSetDict(d, keys[1:], value)
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
  for flatKey, value in d.items():
    keyTuple = dotSplitter(flatKey)
    nestedSetDict(normalDict, keyTuple, value)
  normalDict =  dict2list(normalDict)                                               # type: ignore[assignment]
  return normalDict
