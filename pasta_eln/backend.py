""" Python Backend: all operations with the filesystem are here """
import json, sys, os, shutil, re, importlib, tempfile
from pathlib import Path
from urllib import request
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
import datalad.api as datalad
from datalad.support import annexrepo
from .mixin_cli import Bcolors, CLI_Mixin
from .database import Database
from .miscTools import upIn, upOut, createDirName, generic_hash, camelCase
from .handleDictionaries import ontology2Labels, fillDocBeforeCreate
if sys.platform=='win32':
  import win32con, win32api

class Pasta(CLI_Mixin):
  """
  PYTHON BACKEND
  """

  def __init__(self, linkDefault=None, confirm=None, **kwargs):
    """
    open server and define database

    Args:
        linkDefault (string): name of configuration/link used; if not given, use the one defined by 'default' in config file
        confirm (function): confirm changes to database and file-tree
        kwargs (dict): additional parameters
          - initViews (bool): initialize views at startup
          - resetOntology (bool): reset ontology on database from one on file
    """
    ## CONFIGURATION FOR DATALAD and GIT: has to move to dictionary
    self.vanillaGit = ['*.md','*.rst','*.org','*.tex','*.py','.id_pastaELN.json'] #tracked but in git;
    #   .id_pastaELN.json has to be tracked by git (if ignored: they don't appear on git-status; they have to change by PASTA)
    self.gitIgnore = ['*.log','.vscode/','*.xcf','*.css'] #misc
    self.gitIgnore+= ['*.bcf','*.run.xml','*.synctex.gz','*.aux']#latex files
    self.gitIgnore+= ['*.pdf','*.svg','*.jpg']           #result figures
    self.gitIgnore+= ['*.hap','*.mss','*.mit','*.mst']   #extractors do not exist yet

    # open configuration file
    self.debug = True
    self.confirm = confirm
    with open(Path.home()/'.pastaELN.json','r', encoding='utf-8') as confFile:
      configuration = json.load(confFile)
    if configuration['version']!=1:
      print('**ERROR Configuration version does not fit')
      raise NameError
    if linkDefault is None:
      linkDefault = configuration['default']
    links = configuration['links']
    if not linkDefault in links:
      return
    if 'user' in links[linkDefault]['local']:
      n,s = links[linkDefault]['local']['user'], links[linkDefault]['local']['password']
    else:
      n,s = upOut(links[linkDefault]['local']['cred'])[0].split(':')
    databaseName = links[linkDefault]['local']['database']
    self.confLinkName= linkDefault
    self.confLink    = links[linkDefault]
    # directories
    #    self.basePath (root of directory tree) is root of all projects
    #    self.cwd changes during program
    self.extractorPath = Path(configuration['extractorDir']) if 'extractorDir' in configuration else \
                         Path(__file__).parent/'Extractors'
    sys.path.append(str(self.extractorPath))  #allow extractors
    self.basePath     = Path(links[linkDefault]['local']['path'])
    self.cwd          = Path('.')
    # decipher configuration and store
    self.userID   = configuration['userID']
    self.magicTags= configuration['magicTags'] #"P1","P2","P3","TODO","WAIT","DONE"
    self.tableFormat = configuration['tableFormat']
    # start database
    self.db = Database(n,s,databaseName,confirm=self.confirm,**kwargs)
    res = ontology2Labels(self.db.ontology,self.tableFormat)
    self.dataLabels      = res['dataDict']
    self.hierarchyLabels = res['hierarchyDict']
    if kwargs.get('initViews', False):
      labels = {}  #one line merging / update does not work
      for i in res['dataDict']:
        labels[i]=res['dataDict'][i]
      for i in res['hierarchyDict']:
        labels[i]=res['hierarchyDict'][i]
      maxTabColumns = configuration['GUI']['maxTabColumns'] \
        if 'GUI' in configuration and 'maxTabColumns' in configuration['GUI'] else 20
      self.db.initViews(labels,self.magicTags, maxTabColumns)
    # internal hierarchy structure
    self.hierStack = []
    self.currentID  = None
    self.alive     = True
    return


  def exit(self, deleteDB=False, **kwargs):
    """
    Shutting down things

    Args:
      deleteDB (bool): remove database
      kwargs (dict): additional parameter
    """
    if deleteDB:
      #uninit / delete everything of git-annex and datalad
      for root, dirs, files in os.walk(self.basePath):
        for momo in dirs:
          try:
            (Path(root)/momo).chmod(0o755)
          except FileNotFoundError:
            print('Could not change-mod',Path(root)/momo)
        for momo in files:
          try:
            (Path(root)/momo).chmod(0o755)
          except FileNotFoundError:
            print('Could not change-mod',Path(root)/momo)
    self.db.exit(deleteDB)
    self.alive     = False
    return


  ######################################################
  ### Change in database
  ######################################################
  def addData(self, docType, doc, hierStack=None, localCopy=False, **kwargs):
    """
    Save doc to database, also after edit

    Args:
        docType (string): docType to be stored, subtypes are / separated
        doc (dict): to be stored
        hierStack (list): hierStack from external functions
        localCopy (bool): copy a remote file to local version
        kwargs (dict): additional parameter, i.e. callback for curation
            forceNewImage (bool): create new image in any case

    Returns:
        bool: success
    """
    if hierStack is None:
      hierStack=[]
    callback = kwargs.get('callback', None)
    forceNewImage=kwargs.get('forceNewImage',False)
    doc['-user']  = self.userID
    childNum     = doc.pop('childNum',None)
    path         = None
    operation    = 'c'  #operation of branch/path
    if docType == '-edit-':
      edit = True
      if '-type' not in doc:
        doc['-type'] = ['x'+str(len(self.hierStack))]
      if len(hierStack) == 0:
        hierStack = self.hierStack
      if '_id' not in doc:
        doc['_id'] = hierStack[-1]
      if len(hierStack)>0 and doc['-type'][0][0]=='x':
        hierStack   = hierStack[:-1]
      elif '-branch' in doc:
        hierStack   = doc['-branch'][0]['stack']
    else:  #new doc
      edit = False
      doc['-type'] = docType.split('/')
      if len(hierStack) == 0:
        hierStack = self.hierStack

    # collect structure-doc and prepare
    if doc['-type'][0][0]=='x' and doc['-type'][0]!='x0' and childNum is None:
      #should not have childnumber in other cases
      thisStack = ' '.join(self.hierStack)
      view = self.db.getView('viewHierarchy/viewHierarchy', startKey=thisStack) #not faster with cT.getChildren
      childNum = 0
      for item in view:
        if item['value'][1][0]=='x0':
          continue
        if thisStack == ' '.join(item['key'].split(' ')[:-1]): #remove last item from string
          childNum += 1

    # find path name on local file system; name can be anything
    if self.cwd is not None and '-name' in doc:
      if (doc['-name'].endswith('_pasta.jpg') or
          doc['-name'].endswith('_pasta.svg') or
          doc['-name'].endswith('.id_pastaELN.json') ):
        print("**Warning DO NOT ADD _pasta. files to database")
        return False
      if doc['-type'][0][0]=='x':
        #project, step, task
        if doc['-type'][0]=='x0':
          childNum = 0
        if edit:      #edit: cwd of the project/step/task: remove last directory from cwd (since cwd contains a / at end: remove two)
          parentDirectory = self.cwd.parent
        else:         #new: below the current project/step/task
          parentDirectory = self.cwd
        path = parentDirectory/createDirName(doc['-name'],doc['-type'][0],childNum) #update,or create (if new doc, update ignored anyhow)
        operation = 'u'
      else:
        #measurement, sample, procedure
        shasum = ''
        if '://' in doc['-name']:                                 #make up name
          if localCopy:
            baseName  = Path(doc['-name']).stem
            extension = Path(doc['-name']).suffix
            path = self.cwd/(camelCase(baseName)+extension)
            request.urlretrieve(doc['-name'], self.basePath/path)
            doc['-name'] = camelCase(baseName)+extension
          else:
            path = Path(doc['-name'])
            try:
              shasum  = generic_hash(path)
            except:
              print('**ERROR bad01: fetch remote content failed. Data not added')
              return False
        elif doc['-name']!='' and (self.basePath/doc['-name']).exists():          #file exists
          path = Path(doc['-name'])
          doc['-name'] = Path(doc['-name']).name
        elif doc['-name']!='' and (self.basePath/self.cwd/doc['-name']).exists(): #file exists
          path = self.cwd/doc['-name']
        else:                                                     #make up name
          shasum  = None
        if shasum is not None: # and doc['-type'][0]=='measurement':         #samples, procedures not added to shasum database, getMeasurement not sensible
          if shasum == '':
            shasum = generic_hash(self.basePath/path, forceFile=True)
          view = self.db.getView('viewIdentify/viewSHAsum',shasum)
          if len(view)==0 or forceNewImage:  #measurement not in database: create doc
            while True:
              self.useExtractors(path,shasum,doc)  #create image/content and add to datalad
              if not 'image' in doc and not 'content' in doc and not 'otherELNName' in doc:  #did not get valuable data: extractor does not exit
                return False
              if callback is None or not callback(doc):
                # if no more iterations of curation
                if 'ignore' in doc:
                  ignore = doc['ignore']; del doc['ignore']
                  if ignore=='dir':
                    projPath = self.basePath.parts[0]
                    dirPath =  path.relative_to(projPath)
                    with open(Path(projPath)/'.gitignore','a', encoding='utf-8') as fOut:
                      fOut.write(dirPath+'/\n')
                    if sys.platform=='win32':
                      win32api.SetFileAttributes(Path(projPath)/'.gitignore',\
                        win32con.FILE_ATTRIBUTE_HIDDEN)
                  if ignore!='none':  #ignored images are added to datalad but not to database
                    return False
                break
          if len(view)==1:  #measurement is already in database
            self.useExtractors(path,shasum,doc,exitAfterDataLad=True)
            doc['_id'] = view[0]['id']
            doc['shasum'] = shasum
            edit = True
    # assemble branch information
    if childNum is None:
      childNum=9999
    if path is not None and path.is_absolute():
      path = path.relative_to(self.basePath)
    path = None if path is None else path.as_posix()
    doc['-branch'] = {'stack':hierStack,'child':childNum,'path':path, 'op':operation}
    if edit:
      #update document
      keysNone = [key for key in doc if doc[key] is None]
      doc = fillDocBeforeCreate(doc, '--')  #store None entries and save back since js2py gets equalizes undefined and null
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
      if not edit:
        if doc['-type'][0]=='x0':
          ## shell command
          # cmd = ['datalad','create','--description','"'+doc['objective']+'"','-c','text2git',path]
          # _ = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
          # datalad api version: produces undesired output
          try:
            description = doc['objective'] if 'objective' in doc else '_'
            datalad.create(self.basePath/path,description=description)
          except:
            print('**ERROR bad02: Tried to create new datalad folder which did already exist')
            raise
          gitAttribute = '\n* annex.backend=SHA1\n**/.git* annex.largefiles=nothing\n'
          for fileI in self.vanillaGit:
            gitAttribute += fileI+' annex.largefiles=nothing\n'
          gitIgnore = '\n'.join(self.gitIgnore)
          gitPath = self.basePath/path/'.gitattributes'
          with open(gitPath,'w', encoding='utf-8') as fOut:
            fOut.write(gitAttribute+'\n')
          if sys.platform=='win32':
            win32api.SetFileAttributes(str(gitPath), win32con.FILE_ATTRIBUTE_HIDDEN)
          gitPath = self.basePath/path/'.gitignore'
          with open(gitPath,'w', encoding='utf-8') as fOut:
            fOut.write(gitIgnore+'\n')
          if sys.platform=='win32':
            win32api.SetFileAttributes(str(gitPath),win32con.FILE_ATTRIBUTE_HIDDEN)
          dlDataset = datalad.Dataset(self.basePath/path)
          dlDataset.save(path='.',message='changed gitattributes')
        else:
          (self.basePath/path).mkdir(exist_ok=True)   #if exist, create again; moving not necessary since directory moved in changeHierarchy
      projectPath = path.parts[0]
      dataset = datalad.Dataset(self.basePath/projectPath)
      if (self.basePath/path/'.id_pastaELN.json').exists():
        if sys.platform=='win32':
          aFile = str(self.basePath/path/'.id_pastaELN.json')
          if win32api.GetFileAttributes(aFile) == win32con.FILE_ATTRIBUTE_HIDDEN:
            win32api.SetFileAttributes(aFile, win32con.FILE_ATTRIBUTE_ARCHIVE)
        else:
          dataset.unlock(path=self.basePath/path/'.id_pastaELN.json')
      with open(self.basePath/path/'.id_pastaELN.json','w', encoding='utf-8') as f:  #local path, update in any case
        f.write(json.dumps(doc))
      if sys.platform=='win32':
        aFile = str(self.basePath/path/'.id_pastaELN.json')
        win32api.SetFileAttributes(aFile, win32con.FILE_ATTRIBUTE_HIDDEN)
      # datalad api version
      dataset.save(path=self.basePath/path/'.id_pastaELN.json', message='Added folder & .id_pastaELN.json')
      ## shell command
      # cmd = ['datalad','save','-m','Added new subfolder with .id_pastaELN.json', '-d', self.basePath+projectPath ,self.basePath+path+/+'.id_pastaELN.json']
      # output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      # print("datalad save",output.stdout.decode('utf-8'))
    self.currentID = doc['_id']
    return True


  ######################################################
  ### Disk directory/folder methods
  ######################################################
  def changeHierarchy(self, docID, dirName=None, **kwargs):
    """
    Change through text hierarchy structure
    change hierarchyStack, change directory, change stored cwd

    Args:
        docID (string): information on how to change
        dirName (string): change into this directory (absolute path given). For if data is moved
        kwargs (dict): additional parameter
    """
    if docID is None or (docID[0]=='x' and docID[1]!='-'):  #cd ..: none. close 'project', 'task'
      self.hierStack.pop()
      self.cwd = self.cwd.parent
    else:  # existing ID is given: open that
      if dirName is None:
        doc = self.db.getDoc(docID)
        self.cwd = Path(doc['-branch'][0]['path'])
        self.hierStack = doc['-branch'][0]['stack']+[docID]
      else:
        self.cwd = dirName.relative_to(self.basePath)
        self.hierStack.append(docID)
    return


  def scanTree(self, **kwargs):
    """ Scan directory tree recursively from project/...
    - find changes on file system and move those changes to DB
    - use .id_pastaELN.json to track changes of directories, aka projects/steps/tasks
    - use shasum to track changes of measurements etc. (one file=one shasum=one entry in DB)
    - create database entries for measurements in directory
    - move/copy/delete allowed as the doc['path'] = list of all copies
      doc['path'] is adopted once changes are observed

    Args:
      kwargs (dict): additional parameter, i.e. callback

    Raises:
      ValueError: could not add new measurement to database
    """
    if len(self.hierStack) == 0:
      print(f'{Bcolors.FAIL}**Warning - scan directory: No project selected{Bcolors.ENDC}')
      return
    callback = kwargs.get('callback', None)
    while len(self.hierStack)>1:
      self.changeHierarchy(None)

    #git-annex lists all the files at once
    #   datalad and git give the directories, if untracked/random; and datalad status produces output
    #   also, git-annex status is empty if nothing has to be done
    #   git-annex output is nice to parse
    fileList = annexrepo.AnnexRepo(self.basePath/self.cwd).status()
    dlDataset = datalad.Dataset(self.basePath/self.cwd)
    #create dictionary that has shasum as key and [origin and target] as value
    shasumDict = {}   #clean ones are omitted
    for posixPath in fileList:
      #Stay absolute fileName = posixPath.relative_to(self.basePath/self.cwd)
      # if fileList[posixPath]['state']=='clean': #for debugging
      #   shasum = generic_hash(fileName)
      #   print(shasum,fileList[posixPath]['prev_gitshasum'],fileList[posixPath]['gitshasum'],fileName)
      if fileList[posixPath]['state']=='untracked':
        shasum = generic_hash(posixPath)
        if shasum in shasumDict:
          shasumDict[shasum] = [shasumDict[shasum][0], posixPath]
        else:
          shasumDict[shasum] = ['', posixPath]
      if fileList[posixPath]['state']=='deleted':
        shasum = fileList[posixPath]['prev_gitshasum']
        if shasum in shasumDict:
          shasumDict[shasum] = [posixPath, shasumDict[shasum][1]]
        else:
          shasumDict[shasum] = [posixPath, '']
      if fileList[posixPath]['state']=='modified':
        shasum = fileList[posixPath]['gitshasum']
        shasumDict[shasum] = ['', posixPath] #new content is same place. No moving necessary, just "new file"

    # loop all entries and separate into moved,new,deleted
    print("Number of changed files:",len(shasumDict))
    for _, (origin, target) in shasumDict.items():
      print("  File changed:",origin,'->',target)
      # originDir, _ = o..s.path.split(self.cwd+origin)
      # find hierStack and parentID of new TARGET location: for new and move
      if target != '':
        targetDir = target.parent
        if not target.exists(): #if dead link
          linkTarget = target.resolve()
          for dirI in self.basePath.glob('*'):
            if (self.basePath/dirI).is_dir():
              path = self.basePath/dirI/linkTarget
              if path.exists():
                target.unlock()
                shutil.copy(path,target)
                break
        parentID = None
        itemTarget = -1
        while parentID is None:
          view = self.db.getView('viewHierarchy/viewPaths', \
            startKey=targetDir.relative_to(self.basePath).as_posix())
          for item in view:
            if item['key']==targetDir.relative_to(self.basePath).as_posix():
              parentID = item['id']
              itemTarget = item
          targetDir = targetDir.parent
        parentDoc = self.db.getDoc(parentID)
        hierStack = parentDoc['-branch'][0]['stack']+[parentID]
      ### separate into two cases
      # newly created file
      if origin == '':
        newDoc    = {'-name':str(target)}
        _ = self.addData('measurement', newDoc, hierStack, callback=callback)  #saved to datalad in here
      # move or delete file
      else:
        #update to datalad
        if target == '':
          dlDataset.save(path=origin, message='Removed file')
        else:
          dlDataset.save(path=origin, message='Moved file from here to '+str(self.cwd/target)   )
          dlDataset.save(path=target, message='Moved file from '+str(self.cwd/origin)+' to here')
        #get docID
        if origin!='' and origin.name == '.id_pastaELN.json':  #if origin has .id_pastaELN.json: parent directory has moved
          origin = origin.parent
        if target!='' and target.name == '.id_pastaELN.json':
          target = target.parent
        view = self.db.getView('viewHierarchy/viewPaths',
                                preciseKey=(self.cwd/origin).relative_to(self.basePath).as_posix())
        if len(view)==1:
          docID = view[0]['id']
          if target == '':       #delete
            self.db.updateDoc( {'-branch':{'path':  (self.cwd/origin).relative_to(self.basePath).as_posix(),\
                                          'oldpath':(self.cwd/origin).relative_to(self.basePath).as_posix(),\
                                          'stack':[None],\
                                          'child':-1,\
                                          'op':'d'}}, docID)
          else:                  #update
            self.db.updateDoc( {'-branch':{'path':  (self.cwd/target).relative_to(self.basePath).as_posix(),\
                                          'oldpath':(self.cwd/origin).relative_to(self.basePath).as_posix(),\
                                          'stack':hierStack,\
                                          'child':itemTarget['value'][2],\
                                          'op':'u'}}, docID)
        else:
          if '_pasta.' not in str(origin):  #TODO_P1 is this really needed
            print("file not in database",self.cwd/origin)
    return

  def backup(self, method='backup', **kwargs):
    """
    backup, verify, restore information from/to database
    - all data is saved to one zip file (NOT ELN file)
    - after restore-to-database, the database changed (new revision)

    Args:
      method (string): backup, restore, compare
      kwargs (dict): additional parameter, i.e. callback

    Returns:
        bool: success
    """
    dirNameProject = 'backup'
    zipFileName = ''
    if self.cwd is None:
      print("**ERROR bbu01: Specify zip file name or database")
      return False
    zipFileName = self.basePath+'../pasta_backup.zip'
    if method=='backup':  mode = 'w'
    else:                 mode = 'r'
    print('  '+method.capitalize()+' to file: '+zipFileName)
    with ZipFile(zipFileName, mode, compression=ZIP_DEFLATED) as zipFile:

      # method backup, iterate through all database entries and save to file
      if method=='backup':
        numAttachments = 0
        #write JSON files
        listDocs = self.db.db
        listFileNames = []
        for doc in listDocs:
          if isinstance(doc, str):
            doc = self.db.getDoc(doc)
          fileName = '__database__/'+doc['_id']+'.json'
          listFileNames.append(fileName)
          zipFile.writestr(Path(dirNameProject)/fileName, json.dumps(doc) )
          # Attachments
          if '_attachments' in doc:
            numAttachments += len(doc['_attachments'])
            for i in range(len(doc['_attachments'])):
              attachmentName = dirNameProject+'/__database__/'+doc['_id']+'/v'+str(i)+'.json'
              zipFile.writestr(attachmentName, json.dumps(doc.get_attachment('v'+str(i)+'.json')))
        #write data-files
        for path, _, files in os.walk(self.basePath):
          if '/.git' in path or '/.datalad' in path:
            continue
          path = Path(path).relative_to(self.basePath)
          for iFile in files:
            if iFile.startswith('.git'):
              continue
            listFileNames.append(path/iFile)
            # print('in',Path().absolute(),': save', path/iFile,' as', Path(dirNameProject)/path/iFile)
            zipFile.write(path/iFile, Path(dirNameProject)/path/iFile)
        #create some fun output
        compressed, fileSize = 0,0
        for doc in zipFile.infolist():
          compressed += doc.compress_size
          fileSize   += doc.file_size
        print(f'  File size: {fileSize:,} byte   Compressed: {compressed:,} byte')
        print(f'  Num. documents (incl. ontology and views): {len(self.db.db):,}\n')#,    num. attachments: {numAttachments:,}\n')
        return True

      # method compare and restore
      if zipFileName.endswith('.eln'):
        print('**ERROR: cannot compare/restore .eln files')
        return False
      # method compare
      if  method=='compare':
        filesInZip = zipFile.namelist()
        print('  Number of documents (incl. ontology and views) in file:',len(filesInZip))
        differenceFound, comparedFiles, comparedAttachments = False, 0, 0
        for doc in self.db.db:
          fileName = doc['_id']+'.json'
          if 'backup/__database__/'+fileName not in filesInZip:
            print("**ERROR bbu02: document not in zip file |",doc['_id'])
            differenceFound = True
          else:
            filesInZip.remove('backup/__database__/'+fileName)
            zipData = json.loads( zipFile.read('backup/__database__/'+fileName) )
            if doc!=zipData:
              print('  Info: data disagrees database, zipfile ',doc['_id'])
              differenceFound = True
            comparedFiles += 1
          if '_attachments' in doc:
            for i in range(len(doc['_attachments'])):
              attachmentName = doc['_id']+'/v'+str(i)+'.json'
              if 'backup/__database__/'+attachmentName not in filesInZip:
                print("**ERROR bbu03: revision not in zip file |",attachmentName)
                differenceFound = True
              else:
                filesInZip.remove('backup/__database__/'+attachmentName)
                zipData = json.loads(zipFile.read('backup/__database__/'+attachmentName) )
                if doc.get_attachment('v'+str(i)+'.json')!=zipData:
                  print('  Info: data disagrees database, zipfile ',attachmentName)
                  differenceFound = True
                comparedAttachments += 1
        filesInZip = [i for i in filesInZip if i.startswith('backup/__database')] #filter out non-db items
        if len(filesInZip)>0:
          differenceFound = True
          print('Files in zipfile not in database',filesInZip)
        if differenceFound: print("  Difference exists between database and zipfile")
        else:               print("  Database and zipfile are identical.",comparedFiles,'files &',comparedAttachments,'attachments were compared\n')
        return not differenceFound

      # method restore: loop through all files in zip and save to database
      #  - skip design and dataDictionary
      if method=='restore':
        beforeLength, restoredFiles = len(self.db.db), 0
        for fileName in zipFile.namelist():
          if fileName.startswith('backup/__database__') and (not \
            (fileName.startswith('backup/__database__/_') or fileName.startswith('backup/__database__/-'))):  #do not restore design documents and ontology
            restoredFiles += 1
            zipData = json.loads( zipFile.read(fileName) )
            fileName = fileName[len('backup/__database__/'):]
            if '/' in fileName:  #attachment
              doc = self.db.getDoc(fileName.split('/')[0])
              doc.put_attachment(fileName.split('/')[1], 'application/json', json.dumps(zipData))
            else:                                                           #normal document
              self.db.saveDoc(zipData)
        print('  Number of documents & revisions in file:',restoredFiles)
        print('  Number of documents before and after restore:',beforeLength, len(self.db.db),'\n')
        return True
    return False


  def useExtractors(self, filePath, shasum, doc, **kwargs):
    """
    get measurements from datafile: central distribution point
    - max image size defined here

    Args:
        filePath (string): path to file
        shasum (string): shasum (git-style hash) to store in database (not used here)
        doc (dict): pass known data/measurement type, can be used to create image; This doc is altered
        kwargs (dict): additional parameter
          - maxSize of image
          - saveToFile: save data to files
    """
    exitAfterDataLad = kwargs.get('exitAfterDataLad',False)
    extension = filePath.suffix[1:]  #cut off initial . of .jpg
    if str(filePath).startswith('http'):
      absFilePath = Path(tempfile.gettempdir())/filePath.name
      request.urlretrieve(str(filePath).replace(':/','://'), absFilePath)
      projectDB = self.cwd.parts[0]
      dataset = datalad.Dataset(self.basePath/projectDB)
    else:
      if filePath.is_absolute():
        filePath = filePath.relative_to(self.basePath)
      parentPath = filePath.parts[0]
      dataset = datalad.Dataset(self.basePath/parentPath)
      if dataset.id:
        dataset.save(path=self.basePath/filePath, message='Added locked document')
      if exitAfterDataLad:
        return
      absFilePath = self.basePath/filePath
    pyFile = 'extractor_'+extension+'.py'
    pyPath = self.extractorPath/pyFile
    if len(doc['-type'])==1:
      doc['-type'] += [extension]
    if pyPath.exists():
      # import module and use to get data
      module  = importlib.import_module(pyFile[:-3])
      content = module.use(absFilePath, '/'.join(doc['-type']) )
      #combine into document
      doc.update(content)
      for meta in ['metaVendor','metaUser']:
        for item in doc[meta]:
          if isinstance(doc[meta][item], tuple):
            doc[meta][item] = list(doc[meta][item])
          if not isinstance(doc[meta][item], (str, int, float, list)) and \
            doc[meta][item] is not None:
            print(' -> simplify ',meta,item, doc[meta][item])
            doc[meta][item] = str(doc[meta][item])
      doc['shasum']    = shasum
      if doc['recipe'].startswith('/'.join(doc['-type'])):
        doc['-type']      = doc['recipe'].split('/')
      else:
        doc['-type']     += doc['recipe'].split('/')
      del doc['recipe']
    else:
      print('  No extractor found',pyFile)
    # FOR EXTRACTOR DEBUGGING
    # import json
    # for item in doc:
    #   try:
    #     _ = json.dumps(doc[item])
    #   except:
    #     print('**ERROR json dumping', item, doc[item])
    # #also make sure that no int64 but normal int
    return


  ######################################################
  ### Wrapper for database functions
  ######################################################
  def getDoc(self, docID):
    """
    Wrapper for getting data from database

    Args:
        docID (string): document id

    Returns:
        dict: json of document
    """
    return self.db.getDoc(docID)


  def replicateDB(self, removeAtStart=False, **kwargs):
    """
    Replicate local database to remote database

    Args:
        removeAtStart (bool): remove remote DB before starting new
        kwargs (dict): additional parameter

    Returns:
        bool: replication success
    """
    remoteConf = dict(self.confLink['remote'])
    if not remoteConf: #empty entry: fails
      print("**ERROR brp01: You tried to replicate although, remote is not defined")
      return False
    remoteConf['user'], remoteConf['password'] = upOut(remoteConf['cred'])[0].split(':')
    success = self.db.replicateDB(remoteConf, removeAtStart)
    return success


  def checkDB(self, verbose=True, **kwargs):
    """
    Wrapper of check database for consistencies by iterating through all documents

    Args:
        verbose (bool): print more or only issues
        kwargs (dict): additional parameter, i.e. callback

    Returns:
        string: output incl. \n
    """
    ### check database itself for consistency
    output = self.db.checkDB(verbose=verbose, **kwargs)
    ### check if datalad status is clean for all projects
    if verbose:
      output += "--- DataLad status ---\n"
    viewProjects   = self.db.getView('viewDocType/x0')
    viewPaths      = self.db.getView('viewHierarchy/viewPaths')
    listPaths = [item['key'] for item in viewPaths]
    clean, count = True, 0
    for item in viewProjects:
      doc = self.db.getDoc(item['id'])
      dirName =doc['-branch'][0]['path']
      fileList = annexrepo.AnnexRepo(self.basePath/dirName).status()
      for posixPath in fileList:
        if fileList[posixPath]['state'] != 'clean':
          output += fileList[posixPath]['state']+' '+fileList[posixPath]['type']+' '+str(posixPath)+'\n'
          clean = False
        #test if file exists
        relPath = posixPath.relative_to(self.basePath)
        if relPath.name=='.id_pastaELN.json': #if project,step,task
          relPath = relPath.parent
        if relPath.as_posix() in listPaths:
          listPaths.remove(relPath.as_posix())
          continue
        if '_pasta.' in relPath.as_posix() or '.datalad' in relPath.parts or \
           relPath.name=='.gitattributes' or (self.basePath/relPath).is_dir() or \
           relPath.name=='.gitignore':
          continue
        extension = '*'+relPath.suffix.lower()
        if extension in self.vanillaGit:
          continue
        count += 1
    output += 'Number of files on disk that are not in database '+str(count)+' (see log for details)\n'
    listPaths = [i for i in listPaths if not "://" in i ]
    listPaths = [i for i in listPaths if not (self.basePath/i).exists()]
    if len(listPaths)>0:
      output += "These files of database not on filesystem: "+listPaths.as_posix()+'\n'
    if clean:
      output += "** Datalad tree CLEAN **\n"
    else:
      output += "** Datalad tree NOT clean **\n"
    return output
