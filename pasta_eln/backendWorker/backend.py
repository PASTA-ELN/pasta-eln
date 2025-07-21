""" Python Backend: all operations with the filesystem are here """
import importlib
import json
import logging
import os
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional, Union
from urllib import request
import matplotlib.axes as mpaxes
import matplotlib.pyplot as plt
from PIL import Image
# from .miscTools import generic_hash, getConfiguration
# from .mixin_cli import CLI_Mixin
from .sqlite import SqlLiteDB
# from .textTools.handleDictionaries import diffDicts, fillDocBeforeCreate
# from .textTools.stringChanges import camelCase, createDirName, outputString


class Backend():#TODO CLI_Mixin):
  """
  PYTHON BACKEND
  """


  def __init__(self, configuration:dict[str,Any]={}, projectGroupName:str='') -> None:
    """
    open server and define database

    Args:
        defaultProjectGroup (string): name of configuration / project-group used; if not given, use the one defined by 'defaultProjectGroup' in config file
    """
    #initialize basic values
    self.configuration: dict[str, Any] = {}
    self.hierStack:list[str] = []
    self.cwd:Optional[Path]  = Path('.')
    self.initialize(configuration, projectGroupName)


  def initialize(self, configuration:dict[str,Any]={}, projectGroupName:str='') -> None:
    """
    initialize or reinitialize server and define database

    Args:
        defaultProjectGroup (string): name of configuration / project-group used; if not given, use the one defined by 'defaultProjectGroup' in config file
    """
    self.configuration = configuration
    self.configurationProjectGroup = projectGroupName
    confProjectGroup = self.configuration['projectGroups'][self.configurationProjectGroup]
    # directories
    #    self.basePath (root of directory tree) is root of all projects
    #    self.cwd changes during program but is similarly the full path from root
    self.basePath   = Path(confProjectGroup['local']['path'])
    self.cwd        = Path(confProjectGroup['local']['path'])
    self.addOnPath  = Path(confProjectGroup['addOnDir'])
    sys.path.append(str(self.addOnPath))                                                                                                              #allow add-ons
    # decipher miscellaneous configuration and store
    self.userID   = self.configuration['userID']
    # start database
    self.db = SqlLiteDB(basePath=self.basePath)
    # internal hierarchy structure
    self.hierStack = []
    return


  def exit(self) -> None:
    """
    Shutting down things
    """
    self.db.exit()
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
    if doc['branch'][0]['path'] is None:
      self.cwd     = None
    else:
      self.cwd     = self.basePath/doc['branch'][0]['path']
    self.hierStack = doc['branch'][0]['stack']+[doc['id']]
    doc['childNum']= doc['branch'][0]['child']
    # change content
    doc = self.addData('-edit-', doc)
    if doc['id'].startswith('x'):
      pathStr = '' if self.cwd is None else str(self.cwd.relative_to(self.basePath))
      self.db.updateChildrenOfParentsChanges(pathStr, doc['branch'][0]['path'], '/'.join(self.hierStack),'')
    self.cwd = self.basePath                                              #reset to sensible before continuing
    self.hierStack = []
    return


  def addData(self, docType:str, doc:dict[str,Any], hierStack:list[str]=[], localCopy:bool=False,
              forceNewImage:bool=False) -> dict[str,Any]:
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
    doc['user']  = self.userID
    childNum     = doc.pop('childNum',None)
    path         = None
    oldPath      = None
    operation    = 'c'                                                               #operation of branch/path
    if docType == '-edit-':
      edit = True
      if 'type' not in doc:
        doc['type'] = [f'x{len(self.hierStack)}']
      if not hierStack:
        hierStack = self.hierStack
      if 'id' not in doc:
        doc['id'] = hierStack[-1]
      if len(hierStack)>0 and doc['type'][0][0]=='x':
        hierStack  = hierStack[:-1]
        oldPath    =  doc['branch'][0]['path']
      elif 'branch' in doc:
        hierStack   = doc['branch'][0]['stack']
    else:                                                                                             #new doc
      edit = False
      doc['type'] = docType.split('/')
      if len(hierStack) == 0:
        hierStack = self.hierStack
    logging.debug('Add/edit data in cwd:%s with stack:%s and name: %s and type: %s and edit: %s',self.cwd, hierStack, doc['name'], doc['type'], edit)
    # collect structure-doc and prepare
    if doc['type'][0] and doc['type'][0][0]=='x' and doc['type'][0]!='x0' and childNum is None:
      #should not have childnumber in other cases
      thisStack = '/'.join(hierStack)+'/'
      view = self.db.getView('viewHierarchy/viewHierarchy', startKey=thisStack)#not faster with cT.getChildren
      childNum = 0
      for item in view:
        if item['value'][1][0][0]!='x':
          continue
        if thisStack == '/'.join(item['key'].split('/')[:-1])+'/':               #remove last item from string
          childNum += 1

    # find path name on local file system; name can be anything
    if self.cwd is not None and 'name' in doc:
      if doc['type'][0] and doc['type'][0][0]=='x':
        #project, step, task
        if doc['type'][0]=='x0':
          childNum = 0
        #parentDir
        #  edit: cwd of the project/step/task: remove last directory from cwd (since cwd contains a / at end: remove two)
        #  new: below the current project/step/task
        parentDirectory = self.cwd.parent if edit else self.cwd
        operation = 'u'
        path = parentDirectory/createDirName(doc, childNum, self.cwd)#update,or create (if new doc, update ignored anyhow)
      else:
        #measurement, sample, procedure
        shasum = ''
        if '://' in doc['name']:                                                                 #make up name
          if localCopy:
            baseName  = Path(doc['name']).stem
            extension = Path(doc['name']).suffix
            path = self.cwd/(camelCase(baseName)+extension)
            try:
              request.urlretrieve(doc['name'], path)
              doc['name'] = camelCase(baseName)+extension
            except Exception:
              path = Path(doc['name'])
          else:
            path = Path(doc['name'])
            try:
              shasum  = generic_hash(path)
            except Exception:
              logging.error('bad01: fetch remote content failed. Data not added')
              return {'id':''}
        elif doc['name']!='' and (self.basePath/doc['name']).is_file():                          # file exists
          path = self.basePath/doc['name']
          doc['name'] = Path(doc['name']).name
        elif doc['name']!='' and (self.cwd/doc['name']).is_file():                               # file exists
          path = self.cwd/doc['name']
        elif 'branch' in doc:
          if len(doc['branch'])==1:
            if doc['branch'][0]['path'] is not None and (self.basePath/doc['branch'][0]['path']).is_file():
              path = self.basePath/doc['branch'][0]['path']
          else:
            logging.warning('backend - known issue: add/edit document with multiple branches %s.', doc['id'])
            # I might change the wrong one if I change the branch, but there is nothing in table that can distinguish which branch to change
        else:                                                                                   # make up name
          shasum  = '-'
        if shasum!='-' and path is not None:
          if shasum == '':
            shasum = generic_hash(path, forceFile=True)
          view = self.db.getView('viewIdentify/viewSHAsum',shasum)
          if len(view)==0 or forceNewImage:                           #measurement not in database: create doc
            self.useExtractors(path,shasum,doc)                                          #create image/content
            # All files should appear in database
            # if not 'image' in doc and not 'content' in doc and not 'otherELNName' in doc:  #did not get valuable data: extractor does not exit
            #   return ''
          if len(view)==1:                                                 #measurement is already in database
            doc['id'] = view[0]['id']
            doc['shasum'] = shasum
            edit = True
    # assemble branch information
    if childNum is None:
      childNum=9999
    if path is not None and path.is_absolute():
      path = path.relative_to(self.basePath)
    pathStr = None if path is None else path.as_posix().replace(':/','://') if path.as_posix().startswith('http') else path.as_posix()
    show = [True]*(len(hierStack)+1)
    if 'branch' in doc and len(hierStack)+1==len(doc['branch'][0]['show']):
      show = doc['branch'][0]['show']
    doc['branch'] = {'stack':hierStack,'child':childNum,'path':pathStr, 'show':show, 'op':operation}
    if edit:
      #update document
      keysNone = [key for key in doc if doc[key] is None]
      doc = fillDocBeforeCreate(doc, ['--'])
      for key in keysNone:
        doc[key]=None
      doc = self.db.updateDoc(doc, doc['id'])
    else:
      # add doc to database
      doc = fillDocBeforeCreate(doc, doc['type'])
      doc = self.db.saveDoc(doc)
    ## adaptation of directory tree, information on disk: documentID is required
    if self.cwd is not None and doc['type'][0][0]=='x':
      #project, step, task
      path = Path(doc['branch'][0]['path'])
      if edit and oldPath is not None:
        if not (self.basePath/oldPath).is_dir():
          logging.warning('AddData edit of folder should have oldPath and that should exist: %s\n This can be '\
            'triggered if user moved the folder.',oldPath)
          return  {'id':''}
        (self.basePath/oldPath).rename(self.basePath/path)
      else:
        (self.basePath/path).mkdir(exist_ok=True)#if exist, create again; moving not necessary since directory moved in changeHierarchy
      with open(self.basePath/path/'.id_pastaELN.json','w', encoding='utf-8') as f:#local path, update in any case
        f.write(json.dumps(doc))
    return doc


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
    if docID is None or (docID[0]=='x' and docID[1]!='-'):               #cd ..: none. close 'project', 'task'
      self.hierStack.pop()
      self.cwd = self.cwd.parent
    elif dirName is None:                                                    # existing ID is given: open that
      doc = self.db.getDoc(docID)
      self.cwd = self.basePath/doc['branch'][0]['path']
      self.hierStack = doc['branch'][0]['stack']+[docID]
    else:
      self.cwd = dirName
      self.hierStack.append(docID)
    return


  def scanProject(self, progressBar:Callable[...,None]|None, projID:str, projPath:Path|None=None) -> None:
    """ Scan directory tree recursively from project/... or project/task/...
    - find changes on file system and move those changes to DB
    - use .id_pastaELN.json to track changes of directories, aka projects/steps/tasks
    - use shasum to track changes of measurements etc. (one file=one shasum=one entry in DB)
    - create database entries for measurements in directory
    - move/copy/delete allowed as the doc['path'] = list of all copies
      doc['path'] is adopted once changes are observed

    Args:
      progressBar (func): progress bar
      projID (str): project's docID
      projPath (str): project's path from basePath; if not given, will be determined

    Raises:
      ValueError: could not add new measurement to database
    """
    rerunScanTree = False
    self.hierStack = [projID]
    if projPath is None:
      pathPosix:str = self.db.getDoc(projID)['branch'][0]['path']
      self.cwd      = self.basePath/pathPosix
      projPath      = self.cwd.relative_to(self.basePath)
    else:
      self.cwd = self.basePath/projPath
    #prepare lists and start iterating
    inDB_all = self.db.getView('viewHierarchy/viewPathsAll', startKey=projPath.as_posix())
    pathsInDB_x    = [i['key'] for i in inDB_all if i['value'][1][0][0]=='x'] #all structure elements: folders
    pathsInDB_data = [i['key'] for i in inDB_all if i['value'][1][0][0]!='x']
    filesCountSum = sum(len(files) for (_, _, files) in os.walk(self.cwd))
    filesCount = 0
    for root, dirs, files in os.walk(self.cwd, topdown=True):
      #find parent-document
      self.cwd = Path(root).relative_to(self.basePath)
      if self.cwd.name.startswith('trash_'):
        del dirs
        del files
        continue
      parentIDs = [i for i in inDB_all if i['key']==self.cwd.as_posix()]                #parent of this folder
      if not parentIDs:                             #skip newly moved folder, will be scanned upon re-scanning
        continue
      parentID = parentIDs[0]['id']
      parentDoc = self.db.getDoc(parentID)
      hierStack = parentDoc['branch'][0]['stack']+[parentID]
      # handle directories
      dirs[:] = [i for i in dirs if not i.startswith(('.','trash_')) and i not in ('__pycache__')
                 and not (Path(root)/i/'pyvenv.cfg').is_file()]
      for dirName in dirs[::-1]:                                                     # sorted forward in Linux
        path = (Path(root)/dirName).relative_to(self.basePath).as_posix()
        if path in pathsInDB_x:                                                     # path already in database
          pathsInDB_x.remove(path)
          continue
        if (self.basePath/path/'.id_pastaELN.json').is_file():                 # update branch: path and stack
          with open(self.basePath/path/'.id_pastaELN.json', encoding='utf-8') as fIn:
            doc = json.loads(fIn.read())
            doc = self.db.getDoc(doc['id'])
          if len(doc)==0:
            (self.basePath/path/'.id_pastaELN.json').unlink()
            rerunScanTree = True
            continue
          if (self.basePath/doc['branch'][0]['path']).parent.as_posix()  == root and \
               doc['branch'][0]['stack']==hierStack:
            # special case: user wants to have a different directory name in same folder: then the child-number should not change
            childNum = doc['branch'][0]['child']
            newPath = path
          else:
            #determine childNumber
            thisStack = '/'.join(hierStack)
            view = self.db.getView('viewHierarchy/viewHierarchy', startKey=thisStack)
            childNum = 0
            for item in view:
              if item['value'][1][0]=='x0' or item['value'][1][0][0]!='x':
                continue
              if thisStack == ' '.join(item['key'].split(' ')[:-1]):            # remove last item from string
                childNum += 1
            parentPath = Path(path).parent
            newPath = str(parentPath/createDirName(doc, childNum, parentPath))#update,or create (if new doc, update ignored anyhow)
            if (self.basePath/newPath).exists():                             # can be either file or directory
              logging.error('New path should not exist %s',newPath)
            else:
              (self.basePath/path).rename(self.basePath/newPath)
          self.db.updateBranch(doc['id'], 0, childNum, hierStack, newPath)
        else:
          currentID = self.addData('x1', {'name': dirName}, hierStack)['id']
          newDir = self.basePath/self.db.getDoc(currentID)['branch'][0]['path']
          (newDir/'.id_pastaELN.json').rename(self.basePath/root/dirName/'.id_pastaELN.json')#move index file into old folder
          newDir.rmdir()                                                                  #remove created path
          (self.basePath/root/dirName).rename(newDir)                                    #move old to new path
        rerunScanTree = True
      # handle files
      for fileName in files:
        filesCount += 1
        if progressBar is not None:
          progressBar(int(100*filesCount/filesCountSum))
        if fileName.startswith(('.', 'trash_')) or '_PastaExport' in fileName:                   #ignore files
          continue
        path = (Path(root).relative_to(self.basePath) /fileName).as_posix()
        if path in pathsInDB_data:
          logging.info('Scan: file already in DB: %s',path)
          pathsInDB_data.remove(path)
        else:
          logging.info('Scan: add file to DB: %s',path)
          shasum = generic_hash(self.basePath/path, forceFile=True)
          if not shasum:
            raise NameError(f'Filepath does not exist {self.basePath/path}')
          view = self.db.getView('viewIdentify/viewSHAsum',shasum)
          if len(view)==0:                                                        #not in database: create doc
            self.addData('', {'name':path}, hierStack)
          else:
            self.db.updateBranch(view[0]['id'], -1, 9999, hierStack, path)
    #finish method
    self.cwd = self.basePath/projPath
    orphans = [
        i for i in pathsInDB_data
        if i.startswith(f'{self.cwd.relative_to(self.basePath).as_posix()}/')
    ]
    logging.info('Scan: these files are on DB but not hard disk\n%s','\n  '.join(orphans))
    orphanDirs = [
        i for i in pathsInDB_x
        if i.startswith(f'{self.cwd.relative_to(self.basePath).as_posix()}/')
        and i != projPath
    ]
    logging.info('Scan: these directories are on DB but not hard disk\n%s','\n  '.join(orphanDirs))
    for orphan in orphans+orphanDirs:
      docID = [i for i in inDB_all if i['key']==orphan][0]['id']
      self.db.updateBranch(docID, -2, 9999, [], orphan)
    #reset to initial values
    self.hierStack = []
    self.cwd = Path(self.basePath)
    if rerunScanTree:
      self.scanProject(progressBar, projID, projPath)
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
    extension = filePath.suffix[1:]                                                 #cut off initial . of .jpg
    if str(filePath).startswith('http'):
      absFilePath = Path(tempfile.gettempdir())/filePath.name
      try:
        with request.urlopen(filePath.as_posix().replace(':/','://'), timeout=60) as urlRequest:
          with open(absFilePath, 'wb') as f:
            try:
              f.write(urlRequest.read())
            except Exception:
              logging.error('Saving downloaded file to temporary disk')
              return
      except Exception:
        logging.error('Could not download file from internet %s', filePath.as_posix())
        return
    else:
      if filePath.is_absolute():
        filePath = filePath.relative_to(self.basePath)
      absFilePath = self.basePath/filePath
    pyFile = f'extractor_{extension.lower()}.py'
    pyPath = self.addOnPath/pyFile
    if pyPath.is_file():
      plt.clf()
      try:
        module  = importlib.import_module(pyFile[:-3])
        content = module.use(absFilePath, {'main':'/'.join(doc['type'])} )
        for key in [i for i in content if i not in ['metaVendor','metaUser','image','content','links','style']]:#only allow accepted keys
          del content[key]
        doc |= content
        for meta in ['metaVendor','metaUser']:
          if meta not in doc:
            doc[meta] = {}
          if isinstance(doc[meta], dict):                                                     #convenient type
            for item in doc[meta]:
              if isinstance(doc[meta][item], tuple):
                doc[meta][item] = list(doc[meta][item])
              try:
                _ = json.dumps(doc[meta][item])
              except (ValueError, TypeError):
                doc[meta][item] = str(doc[meta][item])
                logging.warning('stringified  %s %s',meta, item)
          else:
            for item in doc[meta]:
              if not (isinstance(item, dict) and 'key' in item and 'value' in item and 'unit' in item):
                logging.error('Complicated extractor return wrong')
                print('Complicated extractor return wrong')
        if doc['style']['main'].startswith(doc['type'][0]):
          doc['type']     = doc['style']['main'].split('/')
        else:
          #user has strange wish: trust him/her
          logging.info('user has strange wish: trust him/her: %s  %s','/'.join(doc['type']),'  '+doc['style']['main'])
        del doc['style']
        if 'fileExtension' not in doc['metaVendor']:
          doc['metaVendor']['fileExtension'] = extension.lower()
        if 'links' in doc and len(doc['links'])==0:
          del doc['links']
      except Exception:
        logging.warning('Issue with extractor %s\n %s', pyFile, traceback.format_exc())
        doc['metaUser'] = {'filename':absFilePath.name, 'extension':absFilePath.suffix,
          'filesize':absFilePath.stat().st_size,
          'created at':datetime.fromtimestamp(absFilePath.stat().st_ctime, tz=timezone.utc).isoformat(),
          'modified at':datetime.fromtimestamp(absFilePath.stat().st_mtime, tz=timezone.utc).isoformat()}
      plt.close('all')
    #combine into document
    doc['shasum']=shasum                                       #essential for logic, always save, unlike image
    return


  def testExtractor(self, filePath:Union[Path,str], extractorPath:Optional[Path]=None, style:dict[str,Any]={'main':''},
                    outputStyle:str='text', saveFig:str='') -> tuple[str, str]:
    """
    Args:
      filePath (Path, str): path to the file to be tested
      extractorPath (Path, None): path to the directory with extractors
      style (dict): style with a main-key that is / separated
      outputStyle (str): report in ['print','text','html'] including show images
      saveFig (str): save figure to...; if given stop testing after generating image

    Returns:
      str, str: short summary or long report and image (as svg or base64 string)
    """
    content = {}
    report = outputString(outputStyle, 'h2', 'Report on extractor test')
    htmlStr= 'Please visit <a href="https://pasta-eln.github.io/pasta-eln/extractors.html#'
    success = True
    if isinstance(filePath, str):
      filePath = Path(filePath)
    if filePath.as_posix().startswith('http'):
      tempFilePath = Path(tempfile.gettempdir())/filePath.name
      try:
        request.urlretrieve(filePath.as_posix().replace(':/','://'), tempFilePath)
      except Exception:
        success = False
        report += outputString(outputStyle, 'error', 'Could not download file from internet')
        report += outputString(outputStyle, 'error', f'{htmlStr}download-error">website</a>')
        return report, ''
      filePath = tempFilePath
    report += outputString(outputStyle, 'info', f'check file: {str(filePath)}')
    extension = filePath.suffix[1:]
    pyFile = f'extractor_{extension.lower()}.py'
    if extractorPath is None:
      extractorPath = self.addOnPath
    #start testing
    if (extractorPath/pyFile).is_file():
      report += outputString(outputStyle, 'info', f'use extractor: {str(extractorPath / pyFile)}')
    else:
      success = False
      report += outputString(outputStyle, 'error', f'No fitting extractor found:{pyFile}')
    if success:
      try:
        module  = importlib.import_module(pyFile[:-3])
        plt.clf()
        content = module.use(filePath, style, saveFig or None )
        if saveFig:
          return report, content.get('image','')
      except Exception:
        success = False
        report += outputString(outputStyle, 'error', 'Python error in extractor')
        report += outputString(outputStyle, 'error', f'{htmlStr}python-error">website</a>')
        report += outputString(outputStyle, 'error', traceback.format_exc(limit=3))
    if success:
      if 'style' in content:
        possibleDocTypes = [i for i in self.db.dataHierarchy('', '') if i[0]!='x']
        matches = [i for i in possibleDocTypes if content['style']['main'].startswith(i)]
        if matches or content['style']['main'] in {'', '-'}:
          report += outputString(outputStyle, 'info', 'Style is good: '+content['style']['main'])
          size = len(str(content))
          report += outputString(outputStyle, 'info', f'Entire extracted size: {size // 1024}kB')
        else:
          report += outputString(outputStyle, 'error', 'Style does not follow doctype in dataHierarchy.')
      else:
        report += outputString(outputStyle,'error','Style not included in extractor.')
    if success:
      try:
        _ = json.dumps(content)
      except Exception:
        report += outputString(outputStyle,'error','Extractor reply not json dumpable.')
    if success:
      try:
        _ = json.dumps(content['metaVendor'])
        if not isinstance(content['metaVendor'], (dict,list)):
          raise TypeError(' Meta vendor: wrong type')
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
        if not isinstance(content['metaUser'], (dict,list)):
          raise TypeError(' Meta user: wrong type')
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
    if success and isinstance(content.get('image',''),Image.Image):
      success = False
      report += outputString(outputStyle,'error','Image is a PIL image: not a base64 string')
      report += outputString(outputStyle, 'error', f'{htmlStr}pillow-image">website</a>')
      # print('Encode image via the following: pay attention to jpg/png which is encoded twice\n```')
      # print('from io import BytesIO')
      # print('figfile = BytesIO()')
      # print('image.save(figfile, format="PNG")')
      # print('imageData = base64.b64encode(figfile.getvalue()).decode()')
      # print('image = "data:image/jpg;base64," + imageData')
    if success and isinstance(content.get('image',''), mpaxes._axes.Axes):  # pylint: disable=protected-access
      success = False
      report += outputString(outputStyle,'error','Image is a matplotlib axis: not a base64 string')
      report += outputString(outputStyle, 'error', f'{htmlStr}matplotlib">website</a>')
      # print('**Warning: image is a matplotlib axis: not a svg string')
      # print('  figfile = StringIO()')
      # print('plt.savefig(figfile, format="svg")')
      # print('image = figfile.getvalue()')
    if success and isinstance(content.get('image',''), str):#show content
      size = len(content['image'])
      report += outputString(outputStyle, 'info', f'Image size {str(size // 1024)}kB')
    if outputStyle=='print':
      logging.info('Identified metadata %s',content)
    return report, content.get('image','')


  ######################################################
  ### Wrapper for database functions
  ######################################################
  def checkDB(self, outputStyle:str='text', repair:Union[None,Callable[[str],bool]]=None,
              minimal:bool=False) -> str:
    """
    Wrapper of check database for consistencies by iterating through all documents

    Args:
        outputStyle (str): output using a given style: see outputString
        repair (function): repair errors automatically; function that has user interaction
        minimal (bool): true=only show warnings and errors; else=also show information

    Returns:
        string: output incl. \n
    """
    # check database itself for consistency
    output = self.db.checkDB(outputStyle=outputStyle, minimal=minimal, repair=repair)
    # compare with file system
    if not minimal:
      output += outputString(outputStyle,'h2','File status')
    viewProjects   = self.db.getView('viewDocType/x0All')
    inDB_all = self.db.getView('viewHierarchy/viewPathsAll')
    pathsInDB_data = [i['key'] for i in inDB_all if i['value'][1][0][0]!='x']
    pathsInDB_folder = [i['key'] for i in inDB_all if i['value'][1][0][0]=='x']
    count = 0
    for projI in viewProjects['id']:
      projDoc = self.db.getDoc(projI)
      if len(projDoc['branch'])==0:
        output += outputString(outputStyle,'error','project view got screwed up')
        continue
      for root, dirs, files in os.walk(self.basePath/projDoc['branch'][0]['path']):
        if Path(root).name[0]=='.' or Path(root).name.startswith('trash_'):
          del dirs
          continue
        for fileName in files:
          if fileName.startswith('.') or fileName.startswith('trash_') or '_PastaExport' in fileName:
            continue
          path = (Path(root).relative_to(self.basePath) /fileName).as_posix()
          if path not in pathsInDB_data:
            output += outputString(outputStyle, 'error', f'File   on disk but not DB (2): {path}')
            count += 1
          else:
            pathsInDB_data.remove(path)
        dirs[:] = [i for i in dirs if not i.startswith(('.','trash_')) and i not in ('__pycache__')
                  and not (Path(root)/i/'pyvenv.cfg').is_file()]
        for dirName in dirs:
          path = (Path(root).relative_to(self.basePath) /dirName).as_posix()
          if path not in pathsInDB_folder:
            output += outputString(outputStyle, 'error', f'Folder on disk but not DB    : {path}')
            count += 1
          else:
            pathsInDB_folder.remove(path)
            listDocs = self.db.getView('viewHierarchy/viewPathsAll', preciseKey=path)
            if len(listDocs)!=1:
              output += outputString(outputStyle, 'error', f'Path of folder is non-unique (1): {path} in '\
                                      f'{" ".join([i["id"] for i in listDocs])}')
            docDB   = self.db.getDoc(listDocs[0]['id'])
            if (self.basePath/root/dirName/'.id_pastaELN.json').is_file():
              with open(self.basePath/root/dirName/'.id_pastaELN.json',encoding='utf-8') as fIn:
                docDisk = json.loads(fIn.read())
                difference = diffDicts(docDisk,docDB)
                if len(difference)>1:
                  errorStr = outputString(outputStyle,'error',f'disk(1) and db(2) content do not match*: {docDB["id"]}\n{difference}')
                  if repair is None:
                    output += errorStr
                  elif repair(errorStr):
                    with open(self.basePath/root/dirName/'.id_pastaELN.json','w',encoding='utf-8') as fOut:
                      json.dump(docDB, fOut)
                  #use only for resetting the content in the .id_pastaELN.json
            else:
              count += 1
              errorStr = outputString(outputStyle, 'error', f'Folder has no .id_pastaELN.json:{path}')
              if repair is None:
                output += errorStr
              elif repair(errorStr):
                with open(self.basePath/root/dirName/'.id_pastaELN.json','w',encoding='utf-8') as fOut:
                  json.dump({'id':docDB['id']}, fOut)
    orphans = [i for i in pathsInDB_data   if not (self.basePath/i).exists() and ':/' not in i and i!='*']#paths can be files or directories
    orphans+= [i for i in pathsInDB_folder if not (self.basePath/i).exists() ]
    if orphans:
      if repair is None:
        output += outputString(outputStyle,'error','bch01: These paths of database not on filesystem(3):\n  - '+'\n  - '.join(orphans))
      else:
        for orphan in sorted(orphans):
          self.db.cursor.execute(f'SELECT main.name, main.type, branches.path, main.id, main.comment FROM main JOIN branches USING(id) WHERE branches.path == "{orphan}"')
          res = self.db.cursor.fetchall()
          resString = '\n  '.join(str(i) for i in res)
          if repair(f'Path of database not on filesystem:\n  {resString}. Repair: file-remove path; folder-create folder and .id_pastaELN'):
            if res[0][1].startswith('x'):
              (self.basePath/orphan).mkdir(parents=True)
              with open(self.basePath/orphan/'.id_pastaELN.json','w',encoding='utf-8') as fOut:
                json.dump({'id':res[0][3]}, fOut)
            else:
              self.db.cursor.execute(f"UPDATE branches SET path='*' WHERE id == '{res[0][3]}' and path == '{orphan}'")
              self.db.connection.commit()
    if not minimal:
      output += outputString(outputStyle,'h2','File summary')
    if outputStyle == 'text':
      output += 'Success\n' if not orphans and count==0 else 'Failure (* can be auto-repaired)\n'
    return output
