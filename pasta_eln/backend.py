""" Python Backend: all operations with the filesystem are here """
import json, sys, os, importlib, tempfile, logging, traceback
from pathlib import Path
from typing import Any, Optional, Union
from urllib import request
from datetime import datetime, timezone
from PySide6.QtWidgets import QProgressBar  # pylint: disable=no-name-in-module
from .mixin_cli import CLI_Mixin
from .database import Database
from .miscTools import upOut, createDirName, generic_hash, camelCase, DummyProgressBar
from .handleDictionaries import fillDocBeforeCreate, diffDicts
from .miscTools import outputString
from .fixedStringsJson import defaultConfiguration, configurationGUI

class Backend(CLI_Mixin):
  """
  PYTHON BACKEND
  """

  def __init__(self, defaultProjectGroup:str='', **kwargs:int):
    """
    open server and define database

    Args:
        defaultProjectGroup (string): name of configuration / project-group used; if not given, use the one defined by 'defaultProjectGroup' in config file
        **kwargs (dict): additional parameters
          - initViews (bool): initialize views at startup
          - resetDataHierarchy (bool): reset dataHierarchy on database from one on file
    """
    #initialize basic values
    self.hierStack:list[str] = []
    self.alive               = True
    self.cwd:Optional[Path]  = Path('.')
    self.initialize(defaultProjectGroup, **kwargs)


  def initialize(self, defaultProjectGroup:str="", **kwargs:int) -> None:
    """
    initialize or reinitialize server and define database

    Args:
        defaultProjectGroup (string): name of configuration / project-group used; if not given, use the one defined by 'defaultProjectGroup' in config file
        **kwargs (dict): additional parameters
          - initViews (bool): initialize views at startup
          - resetDataHierarchy (bool): reset dataHierarchy on database from one on file
    """
    configFileName = Path.home()/'.pastaELN.json'
    self.configuration = defaultConfiguration
    if configFileName.exists():
      with open(configFileName,'r', encoding='utf-8') as confFile:
        self.configuration |= json.load(confFile)
    for _, items in configurationGUI.items():
      for k,v in items.items():
        if k not in self.configuration['GUI']:
          self.configuration['GUI'][k] = v[1]
    if self.configuration['version']!=2:
      print('**ERROR Configuration file does not exist or version is not 2')
      return
    if not defaultProjectGroup:
      defaultProjectGroup = self.configuration['defaultProjectGroup']
    if defaultProjectGroup not in self.configuration['projectGroups']:
      raise ValueError('BadConfigurationFileError')
    projectGroup = self.configuration['projectGroups'][defaultProjectGroup]
    if 'user' in projectGroup['local']:
      n,s = projectGroup['local']['user'], projectGroup['local']['password']
    else:
      n,s = upOut(projectGroup['local']['cred'])[0].split(':')
    databaseName = projectGroup['local']['database']
    # directories
    #    self.basePath (root of directory tree) is root of all projects
    #    self.cwd changes during program but is similarly the full path from root
    self.basePath      = Path(projectGroup['local']['path'])
    self.cwd           = Path(projectGroup['local']['path'])
    self.extractorPath = Path(self.configuration['extractorDir'])
    sys.path.append(str(self.extractorPath))  #allow extractors
    # decipher miscellaneous configuration and store
    self.userID   = self.configuration['userID']
    # start database
    self.db = Database(n,s,databaseName, self.configuration, basePath=self.basePath)
    if not hasattr(self.db, 'databaseName'):  #not successful database creation
      return
    if kwargs.get('initViews', False):
      self.db.initDocTypeViews(self.configuration['tableColumnsMax'])
    # internal hierarchy structure
    self.hierStack = []
    self.alive     = True
    return


  def exit(self, deleteDB:bool=False) -> None:
    """
    Shutting down things

    Args:
      deleteDB (bool): remove database
    """
    self.db.exit(deleteDB)
    self.alive     = False
    return


  ######################################################
  ### Change in database
  ######################################################
  def editData(self, doc:dict[str,Any]) -> None:
    """
    Edit data from version 2 information flow by wrapping addData

    Args:
      doc (dict): dict to save
    """
    doc = dict(doc)
    if doc['-branch'][0]['path'] is None:
      self.cwd     = None
    else:
      self.cwd     = self.basePath/doc['-branch'][0]['path']
    self.hierStack = doc['-branch'][0]['stack']+[doc['_id']]
    doc['childNum']= doc['-branch'][0]['child']
    # change content
    self.addData('-edit-', doc)
    # change folder-name in database of all children
    if doc['-type'][0][0]=='x' and self.cwd is not None:
      items = self.db.getView(
          'viewHierarchy/viewPaths',
          startKey=f'{self.cwd.relative_to(self.basePath).as_posix()}/',
      )
      for item in items:
        oldPathparts = item['key'].split('/')
        newPathParts = doc['-branch']['path'].split('/')
        newPath = '/'.join(newPathParts+oldPathparts[len(newPathParts):]  )
        # print(item['id']+'  old='+item['key']+'  branch='+str(item['value'][-1])+\
        #      '  child='+str(item['value'][-3])+'  new='+newPath)
        self.db.updateBranch(item['id'], item['value'][-1], item['value'][-3], path=newPath)
    self.cwd = self.basePath #reset to sensible before continuing
    self.hierStack = []
    return


  def addData(self, docType:str, doc:dict[str,Any], hierStack:list[str]=[], localCopy:bool=False,
              forceNewImage:bool=False) -> str:
    """
    Save doc to database, also after edit

    Args:
        docType (string): docType to be stored, subtypes are / separated; or '-edit-'
        doc (dict): to be stored
        hierStack (list): hierStack from external functions
        localCopy (bool): copy a remote file to local version
        forceNewImage (bool): create new image in any case

    Returns:
        str: docID, empty string if failure
    """
    doc['-user']  = self.userID
    childNum     = doc.pop('childNum',None)
    path         = None
    oldPath      = None
    operation    = 'c'  #operation of branch/path
    if docType == '-edit-':
      edit = True
      if '-type' not in doc:
        doc['-type'] = [f'x{len(self.hierStack)}']
      if not hierStack:
        hierStack = self.hierStack
      if '_id' not in doc:
        doc['_id'] = hierStack[-1]
      if len(hierStack)>0 and doc['-type'][0][0]=='x':
        hierStack  = hierStack[:-1]
        oldPath    =  doc['-branch'][0]['path']
      elif '-branch' in doc:
        hierStack   = doc['-branch'][0]['stack']
    else:  #new doc
      edit = False
      doc['-type'] = docType.split('/')
      if len(hierStack) == 0:
        hierStack = self.hierStack
    logging.debug((((
        f'Add/edit data in cwd:{str(self.cwd)} with stack:{str(hierStack)} and name: '
        + doc['-name']) + ' type:') + str(doc['-type']) + ' and edit: ') +
                  str(edit))

    # collect structure-doc and prepare
    if doc['-type'][0][0]=='x' and doc['-type'][0]!='x0' and childNum is None:
      #should not have childnumber in other cases
      thisStack = ' '.join(hierStack)
      view = self.db.getView('viewHierarchy/viewHierarchy', startKey=thisStack) #not faster with cT.getChildren
      childNum = 0
      for item in view:
        if item['value'][1][0]=='x0' or item['value'][1][0][0]!='x':
          continue
        if thisStack == ' '.join(item['key'].split(' ')[:-1]): #remove last item from string
          childNum += 1

    # find path name on local file system; name can be anything
    if self.cwd is not None and '-name' in doc:
      if doc['-type'][0][0]=='x':
        #project, step, task
        if doc['-type'][0]=='x0':
          childNum = 0
        #parentDir
        #  edit: cwd of the project/step/task: remove last directory from cwd (since cwd contains a / at end: remove two)
        #  new: below the current project/step/task
        parentDirectory = self.cwd.parent if edit else self.cwd
        path = parentDirectory/createDirName(doc['-name'],doc['-type'][0],childNum) #update,or create (if new doc, update ignored anyhow)
        operation = 'u'
      else:
        #measurement, sample, procedure
        shasum = ''
        if '://' in doc['-name']:                           #make up name
          if localCopy:
            baseName  = Path(doc['-name']).stem
            extension = Path(doc['-name']).suffix
            path = self.cwd/(camelCase(baseName)+extension)
            request.urlretrieve(doc['-name'], path)
            doc['-name'] = camelCase(baseName)+extension
          else:
            path = Path(doc['-name'])
            try:
              shasum  = generic_hash(path)
            except Exception:
              print('**ERROR bad01: fetch remote content failed. Data not added')
              return ''
        elif doc['-name']!='' and (self.basePath/doc['-name']).exists():          #file exists
          path = self.basePath/doc['-name']
          doc['-name'] = Path(doc['-name']).name
        elif doc['-name']!='' and (self.cwd/doc['-name']).exists():               #file exists
          path = self.cwd/doc['-name']
        elif '-branch' in doc:
          if len(doc['-branch'])==1:
            if doc['-branch'][0]['path'] is not None and (self.basePath/doc['-branch'][0]['path']).exists():
              path = self.basePath/doc['-branch'][0]['path']
          else:
            logging.warning('backend: add document with multiple branches'+str(doc['-branch']) )
        else:                                                                     #make up name
          shasum  = '-'
        if shasum!='-' and path is not None:
          if shasum == '':
            shasum = generic_hash(path, forceFile=True)
          view = self.db.getView('viewIdentify/viewSHAsum',shasum)
          if len(view)==0 or forceNewImage:  #measurement not in database: create doc
            self.useExtractors(path,shasum,doc)  #create image/content
            # All files should appear in database
            # if not 'image' in doc and not 'content' in doc and not 'otherELNName' in doc:  #did not get valuable data: extractor does not exit
            #   return ''
          if len(view)==1:  #measurement is already in database
            doc['_id'] = view[0]['id']
            doc['shasum'] = shasum
            if doc['-type'] == ['-']:  #don't overwrite identified type, without going through extractor
              del doc['-type']
            edit = True
    # assemble branch information
    if childNum is None:
      childNum=9999
    if path is not None and path.is_absolute():
      path = path.relative_to(self.basePath)
    pathStr = None if path is None else path.as_posix()
    show = [True]*(len(hierStack)+1)
    if '-branch' in doc and len(hierStack)+1==len(doc['-branch'][0]['show']):
      show = doc['-branch'][0]['show']
    doc['-branch'] = {'stack':hierStack,'child':childNum,'path':pathStr, 'show':show, 'op':operation}
    if edit:
      #update document
      keysNone = [key for key in doc if doc[key] is None]
      doc = fillDocBeforeCreate(doc, ['--'])  #store None entries and save back since js2py gets equalizes undefined and null
      for key in keysNone:
        doc[key]=None
      doc = self.db.updateDoc(doc, doc['_id'])
    else:
      # add doc to database
      doc = fillDocBeforeCreate(doc, doc['-type'])
      doc = self.db.saveDoc(doc)

    ## adaptation of directory tree, information on disk: documentID is required
    if self.cwd is not None and doc['-type'][0][0]=='x':
      #project, step, task
      path = Path(doc['-branch'][0]['path'])
      if edit and oldPath is not None:
        if not (self.basePath/oldPath).exists():
          print(
              f'**WARNING: addData edit of folder should have oldPath and that should exist:{oldPath}'
              + '\n This can be triggered if user moved the folder.')
          return ''
        (self.basePath/oldPath).rename(self.basePath/path)
      else:
        (self.basePath/path).mkdir(exist_ok=True)   #if exist, create again; moving not necessary since directory moved in changeHierarchy
      with open(self.basePath/path/'.id_pastaELN.json','w', encoding='utf-8') as f:  #local path, update in any case
        f.write(json.dumps(doc))
    return doc['_id']


  ######################################################
  ### Disk directory/folder methods
  ######################################################
  def changeHierarchy(self, docID:Optional[str], dirName:Optional[Path]=None) -> None:
    """
    Change through text hierarchy structure
    change hierarchyStack, change directory, change stored cwd

    Args:
        docID (string): information on how to change
        dirName (string): change into this directory (absolute path given). For if data is moved
    """
    logging.debug('changeHierarchy should only be used in CLI mode')
    if self.cwd is None:
      return
    if docID is None or (docID[0]=='x' and docID[1]!='-'):  #cd ..: none. close 'project', 'task'
      self.hierStack.pop()
      self.cwd = self.cwd.parent
    elif dirName is None:  # existing ID is given: open that
      doc = self.db.getDoc(docID)
      self.cwd = self.basePath/doc['-branch'][0]['path']
      self.hierStack = doc['-branch'][0]['stack']+[docID]
    else:
      self.cwd = dirName
      self.hierStack.append(docID)
    return


  def scanProject(self, progressBar:Union[QProgressBar,DummyProgressBar] , projID:str, projPath:str='') -> None:
    """ Scan directory tree recursively from project/...
    - find changes on file system and move those changes to DB
    - use .id_pastaELN.json to track changes of directories, aka projects/steps/tasks
    - use shasum to track changes of measurements etc. (one file=one shasum=one entry in DB)
    - create database entries for measurements in directory
    - move/copy/delete allowed as the doc['path'] = list of all copies
      doc['path'] is adopted once changes are observed

    Args:
      progressBar (QProgressBar): gui - qt progress bar
      projID (str): project's docID
      projPath (str): project's path from basePath; if not given, will be determined

    Raises:
      ValueError: could not add new measurement to database
    """
    progressBar.show()
    self.hierStack = [projID]
    if not projPath:
      projPath = self.db.getDoc(projID)['-branch'][0]['path']
    self.cwd = self.basePath/projPath
    rerunScanTree = False
    #prepare lists and start iterating
    inDB_all = self.db.getView('viewHierarchy/viewPaths')
    pathsInDB_x    = [i['key'] for i in inDB_all if i['value'][1][0][0]=='x']  #all structure elements: task, subtasts
    pathsInDB_data = [i['key'] for i in inDB_all if i['value'][1][0][0]!='x']
    filesCountSum = sum(len(files) for (r, d, files) in os.walk(self.cwd))
    filesCount = 0
    for root, dirs, files in os.walk(self.cwd, topdown=True):
      #find parent-document
      self.cwd = Path(root).relative_to(self.basePath)
      if self.cwd.name.startswith('trash_'):
        del dirs
        del files
        continue
      parentIDs = [i for i in inDB_all if i['key']==self.cwd.as_posix()]
      if not parentIDs: #skip newly moved folder, will be scanned upon re-scanning
        continue
      parentID = parentIDs[0]['id']
      parentDoc = self.db.getDoc(parentID)
      hierStack = parentDoc['-branch'][0]['stack']+[parentID]
      # handle directories
      for dirName in dirs[::-1]: #sorted forward in Linux
        if dirName.startswith('.') or dirName.startswith('trash_'):
          continue
        path = (Path(root)/dirName).relative_to(self.basePath).as_posix()
        if path in pathsInDB_x: #path already in database
          pathsInDB_x.remove(path)
          continue
        if (self.basePath/path/'.id_pastaELN.json').exists(): # update branch: path and stack
          with open(self.basePath/path/'.id_pastaELN.json', 'r', encoding='utf-8') as fIn:
            doc = json.loads(fIn.read())
          if (self.basePath/doc['-branch'][0]['path']).parent.as_posix()  == root and \
               doc['-branch'][0]['stack']==hierStack:
            # special case: user wants to have a different directory name in same folder: then the child-number should not change
            childNum = doc['-branch'][0]['child']
            newPath = path
          else:
            #determine childNumber
            thisStack = ' '.join(hierStack)
            view = self.db.getView('viewHierarchy/viewHierarchy', startKey=thisStack)
            childNum = 0
            for item in view:
              if item['value'][1][0]=='x0' or item['value'][1][0][0]!='x':
                continue
              if thisStack == ' '.join(item['key'].split(' ')[:-1]): #remove last item from string
                childNum += 1
            newPath = '/'.join(path.split('/')[:-1])+'/'+createDirName(doc['-name'],doc['-type'][0],childNum) #update,or create (if new doc, update ignored anyhow)
            if (self.basePath/newPath).exists():
              print("**ERROR new path should not exist",newPath)
            else:
              (self.basePath/path).rename(self.basePath/newPath)
          self.db.updateBranch(doc['_id'], 0, childNum, hierStack, newPath)
        else:
          currentID = self.addData(f'x{len(hierStack)}', {'-name': dirName}, hierStack)
          newDir = self.basePath/self.db.getDoc(currentID)['-branch'][0]['path']
          (newDir/'.id_pastaELN.json').rename(self.basePath/root/dirName/'.id_pastaELN.json') #move index file into old folder
          newDir.rmdir()                     #remove created path
          (self.basePath/root/dirName).rename(newDir) #move old to new path
        rerunScanTree = True
      # handle files
      for fileName in files:
        filesCount += 1
        progressBar.setValue(int(100*filesCount/filesCountSum))
        if fileName.startswith('.') or fileName.startswith('trash_') or '_PastaExport' in fileName:
          continue
        path = (Path(root).relative_to(self.basePath) /fileName).as_posix()
        if path in pathsInDB_data:
          logging.info('Scan: file already in DB: %s',path)
          pathsInDB_data.remove(path)
        else:
          logging.info('Scan: add file to DB: %s',path)
          self.addData('-', {'-name':path}, hierStack)
    #finish method
    self.cwd = self.basePath/projPath
    orphans = [
        i for i in pathsInDB_data
        if i.startswith(f'{self.cwd.relative_to(self.basePath).as_posix()}/')
    ]
    logging.info('Scan: these files are on DB but not hard disk\n'+'\n  '.join(orphans))
    orphanDirs = [
        i for i in pathsInDB_x
        if i.startswith(f'{self.cwd.relative_to(self.basePath).as_posix()}/')
        and i != projPath
    ]
    logging.info('Scan: these directories are on DB but not hard disk\n'+'\n  '.join(orphanDirs))
    for orphan in orphans+orphanDirs:
      docID = [i for i in inDB_all if i['key']==orphan][0]['id']
      doc   = dict(self.db.getDoc(docID))
      change = None
      for branch in doc['-branch']:
        if branch['path']==orphan:
          change = {'-branch': {'op':'d', 'oldpath':branch['path'], 'path':branch['path'], 'stack':branch['stack'] }}
          break
      if change is None:
        logging.warning('Tried to remove orphan in database but could not; that can happen if user renames folder: %s', orphan)
      else:
        self.db.updateDoc(change, docID)
    #reset to initial values
    self.hierStack = []
    self.cwd = Path(self.basePath)
    if rerunScanTree:
      self.scanProject(progressBar, projID, projPath)
    progressBar.hide()
    return


  def useExtractors(self, filePath:Path, shasum:str, doc:dict[str,Any]) -> None:
    """
    get measurements from datafile: central distribution point
    - max image size defined here

    Args:
        filePath (Path): path to file
        shasum (string): shasum (git-style hash) to store in database (not used here)
        doc (dict): pass known data/measurement type, can be used to create image; This doc is altered
    """
    extension = filePath.suffix[1:]  #cut off initial . of .jpg
    if str(filePath).startswith('http'):
      absFilePath = Path(tempfile.gettempdir())/filePath.name
      with request.urlopen(filePath.as_posix().replace(':/','://'), timeout=60) as urlRequest:
        with open(absFilePath, 'wb') as f:
          try:
            f.write(urlRequest.read())
          except Exception:
            print("Error saving downloaded file to temporary disk")
    else:
      if filePath.is_absolute():
        filePath = filePath.relative_to(self.basePath)
      absFilePath = self.basePath/filePath
    pyFile = f'extractor_{extension.lower()}.py'
    pyPath = self.extractorPath/pyFile
    success = False
    if pyPath.exists():
      success = True
      # import module and use to get data
      os.environ['QT_API'] = 'pyside2'
      import matplotlib.pyplot as plt  #IMPORTANT: NO PYPLOT OUTSIDE THIS QT_API BLOCK
      plt.clf()
      try:
        module  = importlib.import_module(pyFile[:-3])
        content = module.use(absFilePath, '/'.join(doc['-type']) )
      except Exception:
        logging.error(f'ERROR with extractor {pyFile}' + '\n' + traceback.format_exc())
        success = False
      os.environ['QT_API'] = 'pyside6'
      #combine into document
      if success:
        doc |= content
        for meta in ['metaVendor','metaUser']:
          if meta not in doc:
            doc[meta] = {}
          for item in doc[meta]:
            if isinstance(doc[meta][item], tuple):
              doc[meta][item] = list(doc[meta][item])
            if not isinstance(doc[meta][item], (str, int, float, list)) and \
                    doc[meta][item] is not None:
              print(' -> simplify ',meta,item, doc[meta][item])
              doc[meta][item] = str(doc[meta][item])
        if doc['-type'][0] in [doc['recipe'].split('/')[0], '-']:
          doc['-type']     = doc['recipe'].split('/')
        else:
          #user has strange wish: trust him/her
          logging.info('user has strange wish: trust him/her: '+'/'.join(doc['-type'])+'  '+doc['recipe'])
        del doc['recipe']
        if 'fileExtension' not in doc['metaVendor']:
          doc['metaVendor']['fileExtension'] = extension.lower()
        if 'links' in doc and len(doc['links'])==0:
          del doc['links']
    if not success:
      print('  **Warning, issue with extractor', pyFile)
      logging.warning('Issue with extractor %s', pyFile)
      doc['metaUser'] = {'filename':absFilePath.name, 'extension':absFilePath.suffix,
        'filesize':absFilePath.stat().st_size,
        'created at':datetime.fromtimestamp(absFilePath.stat().st_ctime, tz=timezone.utc).isoformat(),
        'modified at':datetime.fromtimestamp(absFilePath.stat().st_mtime, tz=timezone.utc).isoformat()}
    doc['shasum']=shasum  #essential for logic, always save, unlike image
    return


  def testExtractor(self, filePath:Union[Path,str], extractorPath:Optional[Path]=None, recipe:str='',
                    outputStyle:str='text', saveFig:str='') -> str:
    """
    Args:
      filePath (Path, str): path to the file to be tested
      extractorPath (Path, None): path to the directory with extractors
      recipe (str): recipe in / separated
      outputStyle (str): report in ['print','text','html'] including show images
      saveFig (str): save figure to...; if given stop testing after generating image

    Returns:
      str: short summary or long report
    """
    import base64
    from io import BytesIO
    from PIL import Image
    import cairosvg
    os.environ['QT_API'] = 'pyside2'
    import matplotlib.pyplot as plt
    import matplotlib.axes as mpaxes

    htmlStr= 'Please visit <a href="https://pasta-eln.github.io/pasta-eln/extractors.html#'
    success = True
    if isinstance(filePath, str):
      filePath = Path(filePath)
    if filePath.as_posix().startswith('http'):
      tempFilePath = Path(tempfile.gettempdir())/filePath.name
      request.urlretrieve(filePath.as_posix().replace(':/','://'), tempFilePath)
      filePath = tempFilePath
    report = outputString(outputStyle, 'h2', 'Report on extractor test')
    report += outputString(outputStyle, 'info', f'check file: {str(filePath)}')
    extension = filePath.suffix[1:]
    pyFile = f'extractor_{extension.lower()}.py'
    if extractorPath is None:
      extractorPath = self.extractorPath
    #start testing
    if (extractorPath/pyFile).exists():
      report += outputString(outputStyle, 'info', f'use extractor: {str(extractorPath / pyFile)}')
    else:
      success = False
      report += outputString(outputStyle, 'error', f'No fitting extractor found:{pyFile}')
    if success:
      try:
        module  = importlib.import_module(pyFile[:-3])
        plt.clf()
        content = module.use(filePath, recipe, saveFig or None)
        if saveFig:
          return report
      except Exception:
        success = False
        report += outputString(outputStyle, 'error', 'Python error in extractor')
        report += outputString(outputStyle, 'error', f'{htmlStr}python-error">website</a>')
        report += outputString(outputStyle, 'error', traceback.format_exc(limit=3))
    if success:
      if 'recipe' in content:
        possibleDocTypes = [i for i in self.db.dataLabels.keys() if i[0]!='x']
        matches = [i for i in possibleDocTypes if content['recipe'].startswith(i)]
        if matches or content['recipe'] == '' or content['recipe'] == '-':
          report += outputString(outputStyle, 'info', 'Recipe is good: '+content['recipe'])
          size = len(str(content))
          report += outputString(outputStyle, 'info', f'Entire extracted size: {size // 1024}kB')
        else:
          report += outputString(outputStyle, 'error', 'Recipe does not follow doctype in dataHierarchy.')
      else:
        report += outputString(outputStyle,'error','Recipe not included in extractor.')
    if success:
      try:
        _ = json.dumps(content)
      except Exception:
        report += outputString(outputStyle,'error','Extractor reply not json dumpable.')
    if success:
      try:
        _ = json.dumps(content['metaVendor'])
        report += outputString(outputStyle,'info','Number of vendor entries: '+str(len(content['metaVendor'])))
      except Exception:
        # possible cause of failure: make sure that no int64 but normal int
        success = False
        report += outputString(outputStyle,'error', 'Some json format does not fit in metaVendor')
        report += outputString(outputStyle, 'error', f'{htmlStr}metadata-error">website</a>')
        #iterate keys
        for key in content['metaVendor']:
          try:
            _ = json.dumps(content['metaVendor'][key])
          except Exception:
            report += outputString(outputStyle,'error',f'FAIL {key}:'+str(content['metaVendor'][key])+' type:')+str(type(content['metaVendor'][key]))
    if success:
      try:
        _ = json.dumps(content['metaUser'])
        report += 'Number of user entries: '+str(len(content['metaUser']))+'<br>'
      except Exception:
        report += outputString(outputStyle,'error', 'Some json format does not fit in metaUser')
        report += outputString(outputStyle, 'error', f'{htmlStr}metadata-error">website</a>')
        #iterate keys
        for key in content['metaUser']:
          try:
            _ = json.dumps(content['metaUser'][key])
          except Exception:
            report += outputString(outputStyle,'error',f'FAIL {key}:'+str(content['metaUser'][key])+' type:') + str(type(content['metaUser'][key]))
      if 'image' not in content:
        success = False
        report += outputString(outputStyle,'error','Image does not exist')
    if success and isinstance(content['image'],Image.Image):
      success = False
      report += outputString(outputStyle,'error','Image is a PIL image: not a base64 string')
      report += outputString(outputStyle, 'error', f'{htmlStr}pillow-image">website</a>')
        # print('Encode image via the following: pay attention to jpg/png which is encoded twice\n```')
        # print('from io import BytesIO')
        # print('figfile = BytesIO()')
        # print('image.save(figfile, format="PNG")')
        # print('imageData = base64.b64encode(figfile.getvalue()).decode()')
        # print('image = "data:image/jpg;base64," + imageData')
    if success and isinstance(content['image'], mpaxes._axes.Axes): # pylint: disable=protected-access
      success = False
      report += outputString(outputStyle,'error','Image is a matplotlib axis: not a base64 string')
      report += outputString(outputStyle, 'error', f'{htmlStr}matplotlib">website</a>')
        # print('**Warning: image is a matplotlib axis: not a svg string')
        # print('  figfile = StringIO()')
        # print('plt.savefig(figfile, format="svg")')
        # print('image = figfile.getvalue()')
    if success and isinstance(content['image'], str):#show content
      size = len(content['image'])
      report += outputString(outputStyle, 'info', f'Image size {str(size // 1024)}kB')
      if outputStyle!='text':
        report += outputString(outputStyle,'h2','Additional window shows the image')
      if len(content['image'])>20:
        if content['image'].startswith('data:image/'):
          #png or jpg encoded base64
          extension = content['image'][11:14]
          img = base64.b64decode(content['image'][22:])
        else:
          #svg data
          img = cairosvg.svg2png(bytestring=content['image'].encode())
        i = BytesIO(img)
        image = Image.open(i)
        if outputStyle!='text':
          image.show()
      del content['image']
    if outputStyle=='print':
      print('Identified metadata',content)
    os.environ['QT_API'] = 'pyside6'
    return report


  ######################################################
  ### Wrapper for database functions
  ######################################################
  def replicateDB(self, progressBar:Union[QProgressBar,DummyProgressBar], removeAtStart:bool=False) -> str:
    """
    Replicate local database to remote database

    Args:
        removeAtStart (bool): remove remote DB before starting new
        progressBar (QProgressBar): gui - qt progress bar

    Returns:
        str: replication report
    """
    defaultProjectGroup = self.configuration['defaultProjectGroup']
    remoteConf = self.configuration['projectGroups'][defaultProjectGroup]['remote']
    if not remoteConf: #empty entry: fails
      print("**ERROR brp01: You tried to replicate although, remote is not defined")
      return 'ERROR'
    if 'cred' in remoteConf:
      remoteConf['user'], remoteConf['password'] = upOut(remoteConf['cred'])[0].split(':')
    return self.db.replicateDB(remoteConf, progressBar, removeAtStart)


  def checkDB(self, outputStyle:str='text', repair:bool=False, minimal:bool=False) -> str:
    """
    Wrapper of check database for consistencies by iterating through all documents

    Args:
        outputStyle (str): output using a given style: see outputString
        repair (bool): repair database
        minimal (bool): true=only show warnings and errors; else=also show information

    Returns:
        string: output incl. \n
    """
    ### check database itself for consistency
    output = self.db.checkDB(outputStyle=outputStyle, repair=repair, minimal=minimal)
    ### compare with file system
    output += outputString(outputStyle,'h2','File status')
    viewProjects   = self.db.getView('viewDocType/x0All')
    inDB_all = self.db.getView('viewHierarchy/viewPathsAll')
    pathsInDB_data = [i['key'] for i in inDB_all if i['value'][1][0][0]!='x']
    pathsInDB_folder = [i['key'] for i in inDB_all if i['value'][1][0][0]=='x']
    count = 0
    for projI in viewProjects:
      projDoc = self.db.getDoc(projI['id'])
      if len(projDoc['-branch'])==0:
        output += outputString(outputStyle,'error','project view got screwed up')
        continue
      for root, dirs, files in os.walk(self.basePath/projDoc['-branch'][0]['path']):
        if Path(root).name[0]=='.' or Path(root).name.startswith('trash_'):
          del dirs
          continue
        for fileName in files:
          if fileName.startswith('.') or fileName.startswith('trash_') or '_PastaExport' in fileName:
            continue
          path = (Path(root).relative_to(self.basePath) /fileName).as_posix()
          if path not in pathsInDB_data:
            output += outputString(outputStyle, 'error', f'File on harddisk but not DB: {path}')
            count += 1
          else:
            pathsInDB_data.remove(path)
        for dirName in dirs:
          if dirName.startswith('.') or dirName.startswith('trash_'):
            continue
          path = (Path(root).relative_to(self.basePath) /dirName).as_posix()
          if path not in pathsInDB_folder:
            output += outputString(outputStyle, 'error', f'Directory on harddisk but not DB:{path}')
            count += 1
          else:
            pathsInDB_folder.remove(path)
            if (self.basePath/root/dirName/'.id_pastaELN.json').exists():
              with open(self.basePath/root/dirName/'.id_pastaELN.json','r',encoding='utf-8') as fIn:
                docDisk = json.loads(fIn.read())
                listDocs = self.db.getView('viewHierarchy/viewPathsAll', preciseKey=path)
                if len(listDocs)!=1:
                  output += outputString(outputStyle, 'error', f'Path of folder is non-unique: {path}')
                docDB   = self.db.getDoc(listDocs[0]['id'])
                difference = diffDicts(docDisk,docDB)
                if len(difference)>1:
                  output += outputString(outputStyle,'error','disk(1) and db(2) content do not match:'+docDisk['_id'])
                  output += outputString(outputStyle,'error',difference)
                  # #use only for resetting the content in the .id_pastaELN.json
                  # with open(self.basePath/root/dirName/'.id_pastaELN.json','w',encoding='utf-8') as fOut:
                  #   json.dump(docDB, fOut)
            else:
              output += outputString(outputStyle, 'error', f'Folder has no .id_pastaELN.json:{path}')
              count += 1
              # if True:  #use only for resetting the content in the .id_pastaELN.json
              #   with open(self.basePath/root/dirName/'.id_pastaELN.json','w',encoding='utf-8') as fOut:
              #     docDB   = self.db.getDoc( docDisk['_id'] )
              #     json.dump(docDB, fOut)
    output += outputString(outputStyle, 'info', f'Number of files on disk that are not in database {str(count)}')
    orphans = [i for i in pathsInDB_data   if not (self.basePath/i).exists() and ":/" not in i]
    orphans+= [i for i in pathsInDB_folder if not (self.basePath/i).exists() ]
    if orphans:
      output += outputString(outputStyle,'error','bch01: These files of database not on filesystem:\n- '+'\n- '.join(orphans))
    output += outputString(outputStyle,'h2','File summary')
    if outputStyle == 'text':
      output += "Success\n" if not orphans and count==0 else "Failure\n"
    return output
