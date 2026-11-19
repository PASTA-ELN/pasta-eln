"""Helpers for discovering, loading, and using PASTA-ELN add-ons"""
import hashlib
import importlib
import importlib.util
from inspect import signature
import logging
import os
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path
from types import ModuleType
from typing import Any
from urllib import request
import pandas as pd
from anytree import Node
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget
from .configuration_file import loadConfiguration, saveConfiguration


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
  configuration = loadConfiguration()
  if not projectGroup:
    projectGroup = configuration['defaultProjectGroup']
  directory = Path(configuration['projectGroups'][projectGroup]['addOnDir'])
  if str(directory) not in sys.path:
    sys.path.insert(0, str(directory))                                                         # allow add-ons
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
        try:
          module = loadNamedModule(directory, fileName[:-3])
          apiVersion = getattr(module, 'PASTA_ELN_EXTRACTOR_API', None)
          parameters = tuple(signature(module.use).parameters)
        except Exception as error:
          errors[fileName] = f'ERROR loading extractor: {error}'
        else:
          if apiVersion != 2 or parameters != ('filePath', 'style', 'saveFigure'):
            errors[fileName] = ('LEGACY EXTRACTOR: content-only mode. Update to PASTA_ELN_EXTRACTOR_API = 2 and '
                                'use(filePath, style, saveFigure).')
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
        linesWithUse = [i for i in lines if i.lstrip().startswith('def use(')]
        if len(linesWithUse)>1:
          extractorsThis = {}
          errors[fileName] = 'ERROR two use() definitions in the code'
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
  saveConfiguration(configuration)
  return {'addon folder':str(directory)} | errors | extractorsAll | otherAddOns


def _moduleKey(modulePath:Path) -> str:
  """Create a deterministic private module name for a file path
  Args:
    modulePath (Path): path to the module
  Returns:
    str: module name for this file path
  """
  resolved = modulePath.resolve()
  digest = hashlib.sha256(str(resolved).encode('utf-8')).hexdigest()[:16]
  return f'_pasta_add_on_{resolved.stem}_{digest}'


def loadNamedModule(directory:Path, moduleName:str) -> ModuleType:
  """Load a Python module directly from the configured file path
  Args:
    directory (Path): path to the add-on folder
    moduleName (str): name of the module
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


def installPythonPackages(directory:str) -> dict[str, Any]:
  """Install a Python packages using pip depending on files in add-on folder
  Args:
    directory (str): path to the add-on folder
  Returns:
    dict: errors of each package
  """
  packages = {'sklearn': 'scikit-learn',
              'fitz':'PyMuPDF'}
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
  errors:dict[str,Any] = {}
  for lib in allLibs:
    try:
      importlib.import_module(lib)                                 # check if the package is already installed
    except ImportError:
      lib = packages.get(lib, lib)
      result = subprocess.run([sys.executable, '-m', 'pip', 'install', lib], capture_output=True, text=True, check=False)
      if result.returncode != 0:
        errors[lib] = result.stderr.strip() + '\n' + result.stdout.strip()
  return errors


def callAddOn(name:str, comm:Any, content:Any, widget:QWidget) -> Any:
  """ Call add-ons
  Args:
    name (str): name of the add-on
    comm (Any): Shared communication object
    content (Any): content to be consumed by addon, e.g. projectID, document
    widget (QWidget): widget to be used

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
  try:
    content = module.main(comm, content, widget, subParameter)
  except Exception:
    traceback.print_exc()
    content = {}
  return content


def callDataExtractor(docID:str, comm:Any) -> Any:
  """ Call data extractor for a given file path: CALL THE DATA FUNCTION

  Args:
    docID (str): docID
    comm (Communication): Shared communication object

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
    comm (Communicate): Shared communication object
    docID (str): project ID
    showAll (bool): show all nodes, even hidden ones

  Returns:
    tuple: (hierarchy as anytree, project document as dict)
  """
  hierarchyI = None
  projDoc   = None
  @Slot(Node, dict)
  def receiveData(h:Node, doc:dict[str,Any]) -> None:
    """Callback: store the hierarchy and project document returned by the backend signal

    Args:
      h (Node): Root node of the requested project hierarchy
      doc (dict[str, Any]): Project document associated with that hierarchy
    """
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
    comm (Communicate): Shared communication object
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
  def __init__(self, width:float=5, height:float=4, dpi:int=100):
    """
    Args:
      width (float): width in inch
      height (float): height in inch
      dpi (int): dots per inch
    """
    self.figure = Figure(figsize=(width, height), dpi=dpi)
    self.axes   = self.figure.add_subplot(111)
    super().__init__(self.figure)
