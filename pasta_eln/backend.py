#!/usr/bin/python3
""" Python Backend: all operations with the filesystem are here
"""

# TODO_P1 reduce relative_to: self.cwd should be always small

class Pasta:
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
    import json, sys
    from pathlib import Path
    from database import Database
    from miscTools import upIn, upOut
    from commonTools import ontology2Labels
    ## CONFIGURATION FOR DATALAD and GIT: has to move to dictionary
    self.vanillaGit = ['*.md','*.rst','*.org','*.tex','*.py','.id_pastaELN.json'] #tracked but in git;
    #   .id_pastaELN.json has to be tracked by git (if ignored: they don't appear on git-status; they have to change by PASTA)
    self.gitIgnore = ['*.log','.vscode/','*.xcf','*.css'] #misc
    self.gitIgnore+= ['*.bcf','*.run.xml','*.synctex.gz','*.aux']#latex files
    self.gitIgnore+= ['*.pdf','*.png','*.svg','*.jpg']           #result figures
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
    self.softwarePath = Path(configuration['softwareDir'])
    self.extractorPath = Path(configuration['extractorDir']) if 'extractorDir' in configuration else \
                         self.softwarePath/'extractors'
    sys.path.append(str(self.extractorPath))  #allow extractors
    self.basePath     = Path(links[linkDefault]['local']['path'])
    self.cwd          = Path('.')
    # decipher configuration and store
    self.userID   = configuration['userID']
    self.magicTags= configuration['magicTags'] #"P1","P2","P3","TODO","WAIT","DONE"
    self.tableFormat = configuration['tableFormat']
    # start database
    self.db = Database(n,s,databaseName,confirm=self.confirm,softwarePath=self.softwarePath, **kwargs)
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
    import os
    from pathlib import Path
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
    import sys, json, os
    from pathlib import Path
    from urllib import request
    import datalad.api as datalad
    from commonTools import commonTools as cT
    from miscTools import createDirName, generic_hash
    if sys.platform=='win32':
      import win32con, win32api

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
            path = self.cwd/(cT.camelCase(baseName)+extension)
            request.urlretrieve(doc['-name'], self.basePath/path)
            doc['-name'] = cT.camelCase(baseName)+extension
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
    path = None if path is None else str(path)
    doc['-branch'] = {'stack':hierStack,'child':childNum,'path':path, 'op':operation}
    if edit:
      #update document
      keysNone = [key for key in doc if doc[key] is None]
      doc = cT.fillDocBeforeCreate(doc, '--').to_dict()  #store None entries and save back since js2py gets equalizes undefined and null
      for key in keysNone:
        doc[key]=None
      doc = self.db.updateDoc(doc, doc['_id'])
    else:
      # add doc to database
      doc = cT.fillDocBeforeCreate(doc, doc['-type']).to_dict()
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
            win32api.SetFileAttributes(gitPath, win32con.FILE_ATTRIBUTE_HIDDEN)
          gitPath = self.basePath/path/'.gitignore'
          with open(gitPath,'w', encoding='utf-8') as fOut:
            fOut.write(gitIgnore+'\n')
          if sys.platform=='win32':
            win32api.SetFileAttributes(gitPath,win32con.FILE_ATTRIBUTE_HIDDEN)
          dlDataset = datalad.Dataset(self.basePath/path)
          dlDataset.save(path='.',message='changed gitattributes')
        else:
          (self.basePath/path).mkdir(exist_ok=True)   #if exist, create again; moving not necessary since directory moved in changeHierarchy
      projectPath = path.parts[0]
      dataset = datalad.Dataset(self.basePath/projectPath)
      if (self.basePath/path/'.id_pastaELN.json').exists():
        if sys.platform=='win32':
          if win32api.GetFileAttributes(self.basePath/path/'.id_pastaELN.json')==\
              win32con.FILE_ATTRIBUTE_HIDDEN:
            win32api.SetFileAttributes(self.basePath/path/'.id_pastaELN.json',\
              win32con.FILE_ATTRIBUTE_ARCHIVE)
        else:
          dataset.unlock(path=self.basePath/path/'.id_pastaELN.json')
      with open(self.basePath/path/'.id_pastaELN.json','w', encoding='utf-8') as f:  #local path, update in any case
        f.write(json.dumps(doc))
      if sys.platform=='win32':
        win32api.SetFileAttributes(self.basePath/path/'.id_pastaELN.json',\
          win32con.FILE_ATTRIBUTE_HIDDEN)
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
    from pathlib import Path
    if docID is None or (docID[0]=='x' and docID[1]!='-'):  #cd ..: none. close 'project', 'task'
      self.hierStack.pop()
      self.cwd = self.cwd.parent
    else:  # existing ID is given: open that
      self.hierStack.append(docID)
      if dirName is not None:
        self.cwd = dirName.relative_to(self.basePath)
      else:
        doc = self.db.getDoc(docID)
        self.cwd = Path(doc['-branch'][0]['path'])
        self.hierStack = doc['-branch'][0]['stack']+[docID]
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
    import shutil
    import datalad.api as datalad
    from datalad.support import annexrepo
    from miscTools import bcolors, generic_hash
    if len(self.hierStack) == 0:
      print(f'{bcolors.FAIL}**Warning - scan directory: No project selected{bcolors.ENDC}')
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
          view = self.db.getView('viewHierarchy/viewPaths', startKey=str(targetDir.relative_to(self.basePath)))
          for item in view:
            if item['key']==str(targetDir.relative_to(self.basePath)):
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
        view = self.db.getView('viewHierarchy/viewPaths', preciseKey=str((self.cwd/origin).relative_to(self.basePath)) )
        if len(view)==1:
          docID = view[0]['id']
          if target == '':       #delete
            self.db.updateDoc( {'-branch':{'path':  str((self.cwd/origin).relative_to(self.basePath)),\
                                          'oldpath':str((self.cwd/origin).relative_to(self.basePath)),\
                                          'stack':[None],\
                                          'child':-1,\
                                          'op':'d'}}, docID)
          else:                  #update
            self.db.updateDoc( {'-branch':{'path':  str((self.cwd/target).relative_to(self.basePath)),\
                                          'oldpath':str((self.cwd/origin).relative_to(self.basePath)),\
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
    import json, os
    from pathlib import Path
    from datetime import datetime
    from zipfile import ZipFile, ZIP_DEFLATED
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
    import importlib, shutil, urllib, tempfile
    from pathlib import Path
    import datalad.api as datalad
    exitAfterDataLad = kwargs.get('exitAfterDataLad',False)
    extension = filePath.suffix[1:]  #cut off initial . of .jpg
    if str(filePath).startswith('http'):
      absFilePath = Path(tempfile.gettempdir())/filePath.name
      urllib.request.urlretrieve(str(filePath).replace(':/','://'), absFilePath)
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
    from miscTools import upOut
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
    from datalad.support import annexrepo
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
        if str(relPath) in listPaths:
          listPaths.remove(str(relPath))
          continue
        if '_pasta.' in str(relPath) or '.datalad' in relPath.parts or \
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
      output += "These files of database not on filesystem: "+str(listPaths)+'\n'
    if clean:
      output += "** Datalad tree CLEAN **\n"
    else:
      output += "** Datalad tree NOT clean **\n"
    return output


  ######################################################
  ### OUTPUT COMMANDS and those connected to it      ###
  ######################################################
  def output(self, docType, printID=False, **kwargs):
    """
    output view to screen
    - length of output 100 character

    Args:
      docType (string): document type to output
      printID (bool):  include docID in output string
      kwargs (dict): additional parameter

    Returns:
        string: output incl. \n
    """
    outString = []
    widthArray = [25,25,25,25]
    if docType in self.tableFormat and '-default-' in self.tableFormat[docType]:
      widthArray = self.tableFormat[docType]['-default-']
    for idx,item in enumerate(self.db.ontology[docType]):
      if not '-name' in item:    #heading
        continue
      if idx<len(widthArray):
        width = widthArray[idx]
      else:
        width = 0
      if width!=0:
        formatString = '{0: <'+str(abs(width))+'}'
        outString.append(formatString.format(item['-name']) )
    outString = '|'.join(outString)+'\n'
    outString += '-'*104+'\n'
    for lineItem in self.db.getView('viewDocType/'+docType):
      rowString = []
      for idx, item in enumerate(self.db.ontology[docType]):
        if idx<len(widthArray):
          width = widthArray[idx]
        else:
          width = 0
        if width!=0:
          formatString = '{0: <'+str(abs(width))+'}'
          if isinstance(lineItem['value'][idx], str ):
            contentString = lineItem['value'][idx]
          elif isinstance(lineItem['value'][idx], bool) or lineItem['value'][idx] is None or isinstance(lineItem['value'][idx], int):
            contentString = str(lineItem['value'][idx])
          else:
            contentString = ' '.join(lineItem['value'][idx])
          contentString = contentString.replace('\n',' ')
          if width<0:  #test if value as non-trivial length
            if lineItem['value'][idx]=='true' or lineItem['value'][idx]=='false':
              contentString = lineItem['value'][idx]
            elif isinstance(lineItem['value'][idx], bool ) or lineItem['value'][idx] is None:
              contentString = str(lineItem['value'][idx])
            elif len(lineItem['value'][idx])>1 and len(lineItem['value'][idx][0])>3:
              contentString = 'true'
            else:
              contentString = 'false'
            # contentString = True if contentString=='true' else False
          rowString.append(formatString.format(contentString)[:abs(width)] )
      if printID:
        rowString.append(' '+lineItem['id'])
      outString += '|'.join(rowString)+'\n'
    return outString


  def outputTags(self, tag='', **kwargs):
    """
    output view to screen
    - length of output 100 character

    Args:
      tag (string): tag to be listed, if empty: print all
      kwargs (dict): additional parameter

    Returns:
        string: output incl. \n
    """
    outString = []
    outString.append(f'{0: <10}'.format('Tags') )
    outString.append(f'{0: <60}'.format('Name') )
    outString.append(f'{0: <10}'.format('ID') )
    outString = '|'.join(outString)+'\n'
    outString += '-'*106+'\n'
    view = None
    if tag=='':
      view = self.db.getView('viewIdentify/viewTags')
    else:
      view = self.db.getView('viewIdentify/viewTags',preciseKey='#'+tag)
    for lineItem in view:
      rowString = []
      rowString.append(f'{0: <10}'.format(lineItem['key']))
      rowString.append(f'{0: <60}'.format(lineItem['value']))
      rowString.append(f'{0: <10}'.format(lineItem['id']))
      outString += '|'.join(rowString)+'\n'
    return outString


  def outputHierarchy(self, onlyHierarchy=True, addID=False, addTags=None, **kwargs):
    """
    output hierarchical structure in database
    - convert view into native dictionary
    - ignore key since it is always the same

    Args:
       onlyHierarchy (bool): only print project,steps,tasks or print all (incl. measurements...)[default print all]
       addID (bool): add docID to output
       addTags (string): add tags, comments, objective to output ['all','tags',None]
       kwargs (dict): additional parameter, i.e. callback

    Returns:
        string: output incl. \n
    """
    import re
    from commonTools import commonTools as cT
    if len(self.hierStack) == 0:
      return 'Warning: pasta.outputHierarchy No project selected'
    hierString = ' '.join(self.hierStack)
    view = self.db.getView('viewHierarchy/viewHierarchy', startKey=hierString)
    nativeView = {}
    for item in view:
      if onlyHierarchy and not item['id'].startswith('x-'):
        continue
      nativeView[item['id']] = [item['key']]+item['value']
    if addTags=='all':
      outString = cT.hierarchy2String(nativeView, addID, self.getDoc, 'all', self.magicTags)
    elif addTags=='tags':
      outString = cT.hierarchy2String(nativeView, addID, self.getDoc, 'tags', self.magicTags)
    else:
      outString = cT.hierarchy2String(nativeView, addID, None, 'none', None)
    #remove superficial * from head of all lines
    minPrefix = len(re.findall(r'^\*+',outString)[0])
    startLine = r'\n\*{'+str(minPrefix)+'}'
    outString = re.sub(startLine,'\n',outString)[minPrefix+1:] #also remove from head of string
    return outString


  def getEditString(self):
    """
    Return org-mode markdown string of hierarchy tree
      complicated style: this document and all its children and grandchildren...

    Returns:
        string: output incl. \n
    """
    return self.outputHierarchy(True,True,'tags')


  def setEditString(self, text, callback=None):
    """
    Using Org-Mode string, replay the steps to update the database

    Args:
       text (string): org-mode structured text
       callback (function): function to verify database change

    Returns:
       success of function: true/false
    """
    import re
    from pathlib import Path
    import datalad.api as datalad
    from commonTools import commonTools as cT
    from miscTools import createDirName
    # write backup
    verbose = False #debugging only of this function
    if verbose:
      print('===============START SAVE HIERARCHY===============')
      print(text)
      print('---------------End reprint input   ---------------')
    dlDataset = datalad.Dataset(self.basePath/self.cwd.parts[0])
    # add the prefix to org-mode structure lines
    prefix = '*'*len(self.hierStack)
    startLine = r'^\*+\ '
    newText = ''
    for line in text.split('\n'):
      if len(re.findall(startLine,line))>0:  #structure line
        newText += prefix+line+'\n'
      else:                                  #other lines, incl. first
        newText += line+'\n'
    newText = prefix+' '+newText
    docList = cT.editString2Docs(newText, self.magicTags)
    del newText; del text
    # initialize iteration
    levelOld = None
    path      = None
    deletedDocs= []
    for doc in docList:  #iterate through all entries

      # deleted items
      if doc['edit'] == '-delete-':
        doc['-user']   = self.userID
        doc = self.db.updateDoc(doc,doc['_id'])
        deletedDocs.append(doc['_id'])
        thisStack = ' '.join(doc['-branch'][0]['stack']+[doc['_id']])
        view = self.db.getView('viewHierarchy/viewHierarchy', startKey=thisStack)
        for item in view:
          subDoc = {'-user':self.userID, 'edit':'-delete-'}
          _ = self.db.updateDoc(subDoc, item['id'])
          deletedDocs.append(item['id'])
        oldPath = doc['-branch'][0]['path']
        newPath = oldPath.parent/('trash_'+oldPath.name)
        print('Deleted doc: Path',oldPath,newPath)
        _ = self.basePath/oldPath.rename(self.basePath/newPath)
        continue

      # deleted parents
      if doc['_id'] in deletedDocs:
        continue

      # All non-deleted items: identify docType
      docDB    = self.db.getDoc(doc['_id']) if doc['_id']!='' else None
      levelNew = doc['-type']
      if levelOld is None:   #first run-through
        children  = [0]
      else:                   #after first entry
        if levelNew<levelOld:                               #UNCLE, aka SIBLING OF PARENT
          for _ in range(levelOld-levelNew):
            children.pop()
          children[-1] += 1
        elif levelNew>levelOld:                             #CHILD
          children.append(0)
        else:                                               #SIBLING
          children[-1] += 1
      if '_id' not in doc or docDB is None or docDB['-type'][0][0]=='x':
        doc['-type'] = 'x'+str(levelNew)
      else:
        doc['-type'] = docDB['-type']

      # for all non-text types: change children and  childNum in database
      #   and continue with next doc. This makes subsequent code easier
      if doc['-type'][0][0]!='x':
        docDB = dict(docDB)
        docDB.update(doc)
        doc = docDB
        doc['childNum'] = children[-1]
        del doc['edit']
        self.addData('-edit-', doc, self.hierStack)
        levelOld     = levelNew
        continue

      # ONLY TEXT DOCUMENTS
      if doc['edit'] == "-edit-":
        edit = "-edit-"
      else:
        edit = doc['-type']
      del doc['edit']
      # change directories: downward
      if levelOld is None:   #first run-through
        doc['childNum'] = docDB['-branch'][0]['child']
      else:                   #after first entry
        lenPath = len(self.cwd.parts)-1 if len(self.cwd.parts[-1])==0 else len(self.cwd.parts)
        for _ in range(lenPath-levelNew):
          self.changeHierarchy(None)                        #'cd ..'
        #check if directory exists on disk
        #move directory; this is the first point where the non-existence of the folder is seen and can be corrected
        dirName = self.basePath/self.cwd/createDirName(doc['-name'],doc['-type'][0],children[-1])
        if not dirName.exists():                     #if move, deletion or because new
          if doc['_id']=='' or doc['_id']=='undefined':     #if new data
            dirName.mkdir()
          else:                                             #if move
            path = Path(docDB['-branch'][0]['path'])
            if not (self.basePath/path).exists():      #parent was moved: get 'path' from knowledge of parent
              parentID = docDB['-branch'][0]['stack'][-1]
              pathParent = Path(self.db.getDoc(parentID)['-branch'][0]['path'])
              path = pathParent/path.name
            if not (self.basePath/path).exists():        #if still does not exist
              print("**ERROR bse01: doc path was not found and parent path was not found |"+str(doc))
              return False
            if self.confirm is None or self.confirm(None,"Move directory "+path+" -> "+self.cwd+dirName):
              (self.basePath/path).rename(self.basePath/self.cwd/dirName)
              dlDataset.save(path=self.basePath/path, message='SetEditString move directory: origin')
              dlDataset.save(path=self.basePath/self.cwd/dirName, message='SetEditString move dir: target')
        if edit=='-edit-':
          self.changeHierarchy(doc['_id'], dirName)   #'cd directory'
          if path is not None:
            #adopt measurements, samples, etc: change / update path by supplying old path
            view = self.db.getView('viewHierarchy/viewPaths', startKey=str(path))
            for item in view:
              if item['value'][1][0][0]=='x':
                continue  #skip since moved by itself
              self.db.updateDoc( {'-branch':{'path':str(self.cwd), 'oldpath':str(path),\
                                            'stack':self.hierStack,\
                                            'child':item['value'][2],\
                                            'op':'u'}},item['id'])
        doc['childNum'] = children[-1]
      ## FOR DEBUGGING:
      if verbose:
        print(doc['-name'].strip()+'|'+str(doc['-type'])+'||'+doc['_id']+' #:',doc['childNum'])
        print('  children:',children,'   levelNew, levelOld',levelNew,levelOld,'   cwd:',self.cwd,'\n')
      # write change to database
      if edit=='-edit-':
        docDB = dict(docDB)
        docDB.update(doc)
        doc = docDB
      self.addData(edit, doc, self.hierStack)
      #update variables for next iteration
      if edit!="-edit-" and levelOld is not None:
        self.changeHierarchy(self.currentID)   #'cd directory'
      levelOld     = levelNew

    #----------------------------------------------------
    #at end, go down ('cd  ..') number of children-length
    if '-type' in doc and doc['-type'][0][0]!='x':  #remove one child, if last was not an x-element, e.g. a measurement
      children.pop()
    for _ in range(len(children)-1):
      self.changeHierarchy(None)
    dataset = datalad.Dataset(self.basePath/self.cwd.parts[0])
    dataset.save(message='set-edit-string: update the project structure')
    return True


  def getChildren(self, docID):
    """
    Get children from this parent using outputHierarchy

    Args:
        docID (string): id parent document

    Returns:
        list: list of names, list of document-ids
    """
    from commonTools import commonTools as cT
    hierTree = self.outputHierarchy(True,True,False)
    if hierTree is None:
      print('**ERROR bgc01: No hierarchy tree')
      return None, None
    result = cT.getChildren(hierTree,docID)
    return result['names'], result['ids']

  def outputQR(self):
    """
    output list of sample qr-codes

    Returns:
        string: output incl. \n
    """
    outString = f"{'QR': <36}|{'Name': <36}|{'ID': <36}\n"
    outString += '-'*110+'\n'
    for item in self.db.getView('viewIdentify/viewQR'):
      outString += f"{item['key'][:36]: <36}|{item['value'][:36]: <36}|{item['id'][:36]: <36}\n"
    return outString


  def outputSHAsum(self):
    """
    output list of measurement SHA-sums of files

    Returns:
        string: output incl. \n
    """
    outString = f"{'SHAsum': <32}|{'Name': <40}|{'ID': <25}\n"
    outString += '-'*110+'\n'
    for item in self.db.getView('viewIdentify/viewSHAsum'):
      key = item['key'] if item['key'] else '-empty-'
      outString += f"{key[:32]: <32}|{item['value'][:40]: <40}|{item['id']: <25}\n"
    return outString
