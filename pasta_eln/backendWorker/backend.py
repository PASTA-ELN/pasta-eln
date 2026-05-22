""" Python Backend: all operations with the filesystem are here """
import json
import logging
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional, Union
from urllib import request
from ..miscTools import getConfiguration
from ..textTools.handleDictionaries import diffDicts, fillDocBeforeCreate
from ..textTools.stringChanges import camelCase, createDirName, outputString
from .extractor import ExtractorManager
from .hashTools import genericHash
from .mixin_cli import CLI_Mixin
from .sqlite import SqlLiteDB


class Backend(CLI_Mixin):
  """
  PYTHON BACKEND
  """

  def __init__(self, projectGroupName:str|None='') -> None:
    """
    open server and define database

    Args:
        defaultProjectGroup (string): name of configuration / project-group used; if not given, use the one defined by 'defaultProjectGroup' in config file
    """
    #initialize basic values
    self.configuration: dict[str, Any] = {}
    self.projectGroup        = ''
    self.hierStack:list[str] = []
    self.basePath            = Path()
    self.cwd:Path | None  = Path('.')
    self.addOnPath           = Path()
    self.userID              = ''
    self.db: SqlLiteDB|None  = None
    if projectGroupName is not None:
      configuration, projectGroupName = getConfiguration(projectGroupName) # get default configuration from file
      self.initialize(configuration, projectGroupName)


  def initialize(self, configuration:dict[str,Any]={}, projectGroupName:str='') -> None:
    """
    initialize or reinitialize server and define database

    Args:
        configuration (dict): configuration dictionary with database and other settings
        projectGroupName (string): name of configuration / project-group used; if not given, use the one defined by 'defaultProjectGroup' in config file
    """
    self.configuration = configuration
    self.projectGroup = projectGroupName
    confProjectGroup = self.configuration['projectGroups'][self.projectGroup]
    # directories
    #    self.basePath (root of directory tree) is root of all projects
    #    self.cwd changes during program but is similarly the full path from root
    self.basePath   = Path(confProjectGroup['local']['path'])
    self.cwd        = Path(confProjectGroup['local']['path'])
    self.addOnPath  = Path(confProjectGroup['addOnDir'])
    if str(self.addOnPath) not in sys.path:
      sys.path.insert(0, str(self.addOnPath))                                       # allow add-ons to backend
    # decipher miscellaneous configuration and store
    self.userID   = self.configuration['userID']
    # start database
    self.db = SqlLiteDB(basePath=self.basePath)
    self.extractors = ExtractorManager(self.basePath, self.addOnPath, self.configuration['GUI']['maxExtractionDuration'],
                                       self.db.dataHierarchy)
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
              forceNewImage:bool=False, runExtractors:bool=True) -> dict[str,Any]:
    """
    Save doc to database, also after edit

    Args:
        docType (string): docType to be stored, subtypes are / separated; or '-edit-'
        doc (dict): to be stored
        hierStack (list): hierStack from external functions
        localCopy (bool): copy a remote file to local version
        forceNewImage (bool): create new image in any case
        runExtractors (bool): run extractor unless doc already contains extractor output

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
              shasum  = genericHash(path)
            except Exception:
              logging.error('bad01: fetch remote content failed. Data not added', exc_info=True)
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
            shasum = genericHash(path, forceFile=True)
          view = self.db.getView('viewIdentify/viewSHAsum',shasum)
          if (len(view)==0 or forceNewImage) and runExtractors:       #measurement not in database: create doc
            self.extractors.use(path,shasum,doc)                                         #create image/content
            # All files should appear in database
            # if not 'image' in doc and not 'content' in doc and not 'otherELNName' in doc:  #did not get valuable data: extractor does not exit
            #   return ''
          else:
            doc['shasum'] = shasum
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
        if oldPath != path.as_posix():
          (self.basePath/oldPath).rename(self.basePath/path)
      else:
        (self.basePath/path).mkdir(exist_ok=True)#if exist, create again; moving not necessary since directory moved in changeHierarchy
      with open(self.basePath/path/'.id_pastaELN.json','w', encoding='utf-8') as f:#local path, update in any case
        f.write(json.dumps(doc))
    return doc


  ######################################################
  ### Disk directory/folder methods
  ######################################################
  def changeHierarchy(self, docID:str | None, dirName:Path | None=None) -> None:
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


  def scanProject(self, progressBar:Callable[...,None]|None, projID:str, projPath:Path|None=None) -> str:
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

    Returns:
      str: statement if item was found in database and link was created. Default new item added

    Raises:
      ValueError: could not add new measurement to database
    """
    rerunScanTree = False
    reply = ''
    self.hierStack = [projID]
    if projPath is None:
      pathPosix:str = self.db.getDoc(projID)['branch'][0]['path']
      self.cwd      = self.basePath/pathPosix
      projPath      = self.cwd.relative_to(self.basePath)
    else:
      self.cwd = self.basePath/projPath
    #prepare lists and start iterating
    inSqliteAll = self.db.getView('viewHierarchy/viewPathsAll', startKey=projPath.as_posix())
    pathsInSqliteX    = [i['key'] for i in inSqliteAll if i['value'][1][0][0]=='x']#all structure elements: folders
    pathsInSqliteData = [i['key'] for i in inSqliteAll if i['value'][1][0][0]!='x']
    filesCountSum = sum(len(files) for (_, _, files) in os.walk(self.cwd))
    filesCount = 0
    ignoredFolders = []
    extractorJobs:list[dict[str,Any]] = []
    for root, dirs, files in os.walk(self.cwd, topdown=True):
      #find parent-document
      self.cwd = Path(root).relative_to(self.basePath)
      if self.cwd.name.startswith('trash_') or (Path(root)/'.pastaELN_ignore').is_file():
        if (Path(root)/'.pastaELN_ignore').is_file():
          ignoredFolders.append(self.cwd.as_posix())
        dirs[:] = []
        continue
      parentIDs = [i for i in inSqliteAll if i['key']==self.cwd.as_posix()]             #parent of this folder
      if not parentIDs:                             #skip newly moved folder, will be scanned upon re-scanning
        continue
      parentID = parentIDs[0]['id']
      parentDoc = self.db.getDoc(parentID)
      hierStack = parentDoc['branch'][0]['stack']+[parentID]
      # handle directories and prevent going into them if they should be ignored.
      ignoredFolders += [(Path(root)/i).relative_to(self.basePath).as_posix()
                         for i in dirs if (Path(root)/i/'.pastaELN_ignore').is_file()]
      dirs[:] = [i for i in dirs if not i.startswith(('.','trash_')) and i not in ('__pycache__')
                 and not (Path(root)/i/'pyvenv.cfg').is_file()
                 and not (Path(root)/i/'.pastaELN_ignore').is_file()]
      for dirName in dirs[::-1]:                                                     # sorted forward in Linux
        path = (Path(root)/dirName).relative_to(self.basePath).as_posix()
        if path in pathsInSqliteX:                                                  # path already in database
          pathsInSqliteX.remove(path)
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
              logging.error('New path should not exist %s',newPath, exc_info=True)
            elif path != newPath:
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
        if path in pathsInSqliteData:
          logging.info('Scan: file already in DB: %s',path)
          pathsInSqliteData.remove(path)
        else:
          logging.info('Scan: add file to DB: %s',path)
          shasum = genericHash(self.basePath/path, forceFile=True)
          if not shasum:
            raise NameError(f'Filepath does not exist {self.basePath/path}')
          view = self.db.getView('viewIdentify/viewSHAsum',shasum)
          if len(view)==0:                                                        #not in database: create doc
            job = self.extractors.prepareJob(self.basePath/path, jobID=len(extractorJobs))
            if job is None:                                                # if no suitable extractor is there
              self.addData('', {'name':path, 'type':['']}, hierStack, runExtractors=False)
            else:
              job |= {'path':path, 'hierStack':hierStack, 'shasum':shasum}
              extractorJobs.append(job)
          else:
            self.db.updateBranch(view[0]['id'], -1, 9999, hierStack, path)
            reply = 'Create a link to existing entry instead of new entry.'
    for job, doc in self.extractors.applyResults(self.extractors.runJobs(extractorJobs), extractorJobs):
      view = self.db.getView('viewIdentify/viewSHAsum', job['shasum'])
      if len(view)==0:
        self.addData('/'.join(doc['type']), doc, job['hierStack'], runExtractors=False)
      else:
        self.db.updateBranch(view[0]['id'], -1, 9999, job['hierStack'], job['path'])
        reply = 'Create a link to existing entry instead of new entry.'
    #finish method
    self.cwd = self.basePath/projPath
    pathsInSqliteData = [i for i in pathsInSqliteData
                         if not any(i == j or i.startswith(f'{j}/') for j in ignoredFolders)]
    pathsInSqliteX = [i for i in pathsInSqliteX
                      if not any(i == j or i.startswith(f'{j}/') for j in ignoredFolders)]
    orphans = [
        i for i in pathsInSqliteData
        if i.startswith(f'{self.cwd.relative_to(self.basePath).as_posix()}/')
    ]
    logging.info('Scan: these files are on DB but not hard disk\n%s','\n  '.join(orphans))
    orphanDirs = [
        i for i in pathsInSqliteX
        if i.startswith(f'{self.cwd.relative_to(self.basePath).as_posix()}/')
        and i != projPath
    ]
    logging.info('Scan: these directories are on DB but not hard disk\n%s','\n  '.join(orphanDirs))
    for orphan in orphans+orphanDirs:
      docID = [i for i in inSqliteAll if i['key']==orphan][0]['id']
      self.db.updateBranch(docID, -2, 9999, [], orphan)
    #reset to initial values
    self.hierStack = []
    self.cwd = Path(self.basePath)
    if rerunScanTree:
      reply += self.scanProject(progressBar, projID, projPath)
    return reply


  ######################################################
  ### Wrapper for database functions
  ######################################################
  def checkDB(self, outputStyle:str='text', repair:None |Callable[[str],bool]=None,
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
    inSqliteAll = self.db.getView('viewHierarchy/viewPathsAll')
    pathsInSqliteData = [i['key'] for i in inSqliteAll if i['value'][1][0][0]!='x']
    pathsInSqliteFolder = [i['key'] for i in inSqliteAll if i['value'][1][0][0]=='x']
    count = 0
    ignoredFolders:list[str] = []
    for projI in viewProjects['id']:
      projDoc = self.db.getDoc(projI)
      if len(projDoc['branch'])==0:
        output += outputString(outputStyle,'error','project view got screwed up')
        continue
      for root, dirs, files in os.walk(self.basePath/projDoc['branch'][0]['path']):
        ignoreFolder = (Path(root)/'.pastaELN_ignore').is_file()
        if Path(root).name[0]=='.' or Path(root).name.startswith('trash_') or ignoreFolder:
          if ignoreFolder:
            ignoredFolders.append(Path(root).relative_to(self.basePath).as_posix())
          dirs[:] = []
          continue
        for fileName in files:
          if fileName.startswith('.') or fileName.startswith('trash_') or '_PastaExport' in fileName:
            continue
          path = (Path(root).relative_to(self.basePath) /fileName).as_posix()
          if path not in pathsInSqliteData:
            output += outputString(outputStyle, 'error', f'File   on disk but not DB (2): {path}')
            count += 1
          else:
            pathsInSqliteData.remove(path)
        ignoredFolders += [(Path(root)/i).relative_to(self.basePath).as_posix()
                           for i in dirs if (Path(root)/i/'.pastaELN_ignore').is_file()]
        dirs[:] = [i for i in dirs if not i.startswith(('.','trash_')) and i not in ('__pycache__')
                  and not (Path(root)/i/'pyvenv.cfg').is_file()
                  and not (Path(root)/i/'.pastaELN_ignore').is_file()]
        for dirName in dirs:
          path = (Path(root).relative_to(self.basePath) /dirName).as_posix()
          if path not in pathsInSqliteFolder:
            output += outputString(outputStyle, 'error', f'Folder on disk but not DB    : {path}')
            count += 1
          else:
            pathsInSqliteFolder.remove(path)
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
    pathsInSqliteData = [i for i in pathsInSqliteData
                         if not any(i == j or i.startswith(f'{j}/') for j in ignoredFolders)]
    pathsInSqliteFolder = [i for i in pathsInSqliteFolder
                           if not any(i == j or i.startswith(f'{j}/') for j in ignoredFolders)]
    orphans = [i for i in pathsInSqliteData   if not (self.basePath/i).exists() and ':/' not in i and i!='*']#paths can be files or directories
    orphans+= [i for i in pathsInSqliteFolder if not (self.basePath/i).exists()]
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
    # identify trash_ files and trash_folders
    projLevelFolders = os.listdir(self.basePath)
    self.db.cursor.execute("SELECT branches.path FROM main JOIN branches USING(id) WHERE type=='x0'")
    projFolders = self.db.cursor.fetchall()
    if nonUsedFolders := set(projLevelFolders).difference([i[0] for i in projFolders]+['pastaELN.db']):
      output += outputString(outputStyle,'warning','These files/folders in data folder are not used for projects:'+
                            '\n  - '.join(['']+list(nonUsedFolders)) )
    for projFolder in projFolders:
      numTrash = sum(len([i for i in dirs + files if i.startswith('trash_')])
                     for _, dirs, files in os.walk(self.basePath/projFolder[0]))
    if numTrash>0:
      output += outputString(outputStyle,'warning',f'There are {numTrash} trash_files and trash_folders')
    # final summary
    if not minimal:
      output += outputString(outputStyle,'h2','File summary')
    if outputStyle == 'text':
      output += 'Success\n' if not orphans and count==0 else 'Failure (* can be auto-repaired)\n'
    return output
