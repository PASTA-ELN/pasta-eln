""" Python Backend: all operations with the filesystem are here """
import json, sys, os, shutil, re, importlib, tempfile, logging, traceback
from pathlib import Path
from urllib import request
from datetime import datetime, timezone
from .mixin_cli import Bcolors, CLI_Mixin
from .database import Database
from .miscTools import upIn, upOut, createDirName, generic_hash, camelCase
from .handleDictionaries import ontology2Labels, fillDocBeforeCreate

#TODO_P4 unprocessed files should be have separate docType

class Backend(CLI_Mixin):
  """
  PYTHON BACKEND
  """

  def __init__(self, defaultProjectGroup='', **kwargs):
    """
    open server and define database

    Args:
        defaultProjectGroup (string): name of configuration / project-group used; if not given, use the one defined by 'defaultProjectGroup' in config file
        kwargs (dict): additional parameters
          - initViews (bool): initialize views at startup
          - resetOntology (bool): reset ontology on database from one on file
    """
    #initialize basic values
    self.hierStack = []
    self.currentID = ""
    self.alive     = True
    self.cwd       = Path('.')
    self.initialize(defaultProjectGroup, **kwargs)


  def initialize(self, defaultProjectGroup="", **kwargs):
    """
    initialize or reinitialize server and define database

    Args:
        defaultProjectGroup (string): name of configuration / project-group used; if not given, use the one defined by 'defaultProjectGroup' in config file
        kwargs (dict): additional parameters
          - initViews (bool): initialize views at startup
          - resetOntology (bool): reset ontology on database from one on file
    """
    configFileName = Path.home()/'.pastaELN.json'
    if not configFileName.exists():
      print('**ERROR Configuration file does not exist')
      return
    with open(configFileName,'r', encoding='utf-8') as confFile:
      self.configuration = json.load(confFile)
    if self.configuration['version']!=2:
      print('**ERROR Configuration version does not fit')
      raise ValueError('VersionError')
    if defaultProjectGroup =="":
      defaultProjectGroup = self.configuration['defaultProjectGroup']
    if not defaultProjectGroup in self.configuration['projectGroups']:
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
    self.basePath     = Path(projectGroup['local']['path'])
    self.cwd          = Path(projectGroup['local']['path'])
    self.extractorPath = Path(self.configuration['extractorDir'])
    sys.path.append(str(self.extractorPath))  #allow extractors
    # decipher miscellaneous configuration and store
    self.userID   = self.configuration['userID']
    # start database
    self.db = Database(n,s,databaseName, self.configuration, **kwargs)
    if not hasattr(self.db, 'databaseName'):  #not successful database creation
      return
    if kwargs.get('initViews', False):
      self.db.initViews(self.configuration)
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
        if item['value'][1][0]=='x0' or item['value'][1][0][0]!='x':
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
            request.urlretrieve(doc['-name'], path)
            doc['-name'] = camelCase(baseName)+extension
          else:
            path = Path(doc['-name'])
            try:
              shasum  = generic_hash(path)
            except:
              print('**ERROR bad01: fetch remote content failed. Data not added')
              return False
        elif doc['-name']!='' and (self.basePath/doc['-name']).exists():          #file exists
          path = self.basePath/doc['-name']
          doc['-name'] = Path(doc['-name']).name
        elif doc['-name']!='' and (self.cwd/doc['-name']).exists():               #file exists
          path = self.cwd/doc['-name']
        else:                                                     #make up name
          shasum  = None
        if shasum is not None: # and doc['-type'][0]=='measurement':         #samples, procedures not added to shasum database, getMeasurement not sensible
          if shasum == '':
            shasum = generic_hash(path, forceFile=True)
          view = self.db.getView('viewIdentify/viewSHAsum',shasum)
          if len(view)==0 or forceNewImage:  #measurement not in database: create doc
            self.useExtractors(path,shasum,doc)  #create image/content
            # All files should appear in database
            # if not 'image' in doc and not 'content' in doc and not 'otherELNName' in doc:  #did not get valuable data: extractor does not exit
            #   return False
          if len(view)==1:  #measurement is already in database
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
        (self.basePath/path).mkdir(exist_ok=True)   #if exist, create again; moving not necessary since directory moved in changeHierarchy
      with open(self.basePath/path/'.id_pastaELN.json','w', encoding='utf-8') as f:  #local path, update in any case
        f.write(json.dumps(doc))
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
    logging.info('changeHierarchy should only be used in CLI mode')
    if docID is None or (docID[0]=='x' and docID[1]!='-'):  #cd ..: none. close 'project', 'task'
      self.hierStack.pop()
      self.cwd = self.cwd.parent
    else:  # existing ID is given: open that
      if dirName is None:
        doc = self.db.getDoc(docID)
        self.cwd = self.basePath/doc['-branch'][0]['path']
        self.hierStack = doc['-branch'][0]['stack']+[docID]
      else:
        self.cwd = dirName
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
    rerunScanTree = False
    startPath = Path(self.cwd)
    #prepare lists and start iterating
    inDB_all = self.db.getView('viewHierarchy/viewPaths')
    #update content between DB and harddisk
    for line in inDB_all:
      if line['value'][1][0][0]=='x':
        continue
      doc = self.db.getDoc(line['id'])
      if 'content' in doc:
        path = self.basePath/line['key']
        doc= {'-type':['procedure']}
        self.useExtractors(path, '', doc)
        self.db.updateDoc(doc, line['id'])
    #TODO_P4 Basic functionality for V1
    #V1: GUI content write-protected; assume one link and no conflicts
    #V2: What happens if you change a file (procedure) on disk / database -> conflicts
    #    Copy of procedure exists on harddisk: one entry in db and links; then change one, but not other, -branch should separate; can they reunite?

    pathsInDB_x    = [i['key'] for i in inDB_all if i['value'][1][0][0]=='x']  #all structure elements: task, subtasts
    pathsInDB_data = [i['key'] for i in inDB_all if i['value'][1][0][0]!='x']
    for root, dirs, files in os.walk(self.cwd, topdown=True):
      #find parent-document
      self.cwd = Path(root).relative_to(self.basePath)
      if self.cwd.name.startswith('trash_'):
        del dirs
        del files
        continue
      parentID = [i for i in inDB_all if i['key']==self.cwd.as_posix()][0]['id']
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
        self.addData('x'+str(len(hierStack)), {'-name':dirName}, hierStack)
        newDir = Path(self.basePath)/self.db.getDoc(self.currentID)['-branch'][0]['path']
        (newDir/'.id_pastaELN.json').rename(Path(self.basePath)/root/dirName/'.id_pastaELN.json') #move index file into old folder
        newDir.rmdir()                     #remove created path
        (Path(self.basePath)/root/dirName).rename(newDir) #move old to new path
        rerunScanTree = True
      # handle files
      for fileName in files:
        if fileName.startswith('.') or fileName.startswith('trash_'):
          continue
        path = (Path(root).relative_to(self.basePath) /fileName).as_posix()
        if path in pathsInDB_data:
          print("File already in DB:",path)
          pathsInDB_data.remove(path)
        else:
          print("Add file to DB:",path)
          _ = self.addData('measurement', {'-name':path}, hierStack, callback=callback)
    #finish method
    self.cwd = startPath
    orphans = [i for i in pathsInDB_data if i.startswith(self.cwd.relative_to(self.basePath).as_posix())]
    print('These files are on DB but not harddisk\n', orphans )
    orphanDirs = [i for i in pathsInDB_x if i==self.cwd.relative_to(self.basePath).as_posix() and \
                                            i!=startPath.relative_to(self.basePath).as_posix()]
    print('These directories are on DB but not harddisk\n', orphanDirs)
    for orphan in orphans+orphanDirs:
      docID = [i for i in inDB_all if i['key']==orphan][0]['id']
      doc   = dict(self.db.getDoc(docID))
      change = None
      for branch in doc['-branch']:
        if branch['path']==orphan:
          change = {'-branch': {'op':'d', 'oldpath':branch['path'], 'path':branch['path'], \
                                'stack':branch['stack'] }}
          break
      if change is None:
        print('**ERROR Tried to remove orphan in database but could not', orphan)
      else:
        self.db.updateDoc(change, docID)
    if rerunScanTree:
      self.scanTree()
    return


  def useExtractors(self, filePath, shasum, doc, **kwargs):
    """
    get measurements from datafile: central distribution point
    - max image size defined here

    Args:
        filePath (string): path to file
        shasum (string): shasum (git-style hash) to store in database (not used here)
        doc (dict): pass known data/measurement type, can be used to create image; This doc is altered
        kwargs (dict): additional parameter
    """
    extension = filePath.suffix[1:]  #cut off initial . of .jpg
    if str(filePath).startswith('http'):
      absFilePath = Path(tempfile.gettempdir())/filePath.name
      request.urlretrieve(filePath.as_posix().replace(':/','://'), absFilePath)
    else:
      if filePath.is_absolute():
        filePath = filePath.relative_to(self.basePath)
      absFilePath = self.basePath/filePath
    pyFile = 'extractor_'+extension.lower()+'.py'
    pyPath = self.extractorPath/pyFile
    if len(doc['-type'])==1:
      doc['-type'] += [extension]
    try:
      if not pyPath.exists():
        raise ValueError('Extractor does not exist')
      # import module and use to get data
      os.environ['QT_API'] = 'pyside2'
      import matplotlib.pyplot as plt  #IMPORTANT: NO PYPLOT OUTSIDE THIS QT_API BLOCK
      plt.clf()
      module  = importlib.import_module(pyFile[:-3])
      content = module.use(absFilePath, '/'.join(doc['-type']) )
      os.environ['QT_API'] = 'pyside6'
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
    except:
      print('  **Error with extractor',pyFile)
      logging.error('ERROR with extractor '+pyFile+'\n'+traceback.format_exc())
      doc['-type'] = ['-']
      doc['metaUser'] = {'filename':absFilePath.name, 'extension':absFilePath.suffix,
        'filesize':absFilePath.stat().st_size,
        'created at':datetime.fromtimestamp(absFilePath.stat().st_ctime, tz=timezone.utc).isoformat(),
        'modified at':datetime.fromtimestamp(absFilePath.stat().st_mtime, tz=timezone.utc).isoformat()}
    # FOR EXTRACTOR DEBUGGING
    # import json
    # for item in doc:
    #   try:
    #     _ = json.dumps(doc[item])
    #   except:
    #     print('**ERROR json dumping', item, doc[item])
    # #also make sure that no int64 but normal int
    return


  def testExtractor(self, filePath, extractorPath=None, recipe='', interactive=True, reportHTML=False):
    """
    Args:
      filePath (Path, str): path to the file to be tested
      extractorPath (Path, None): path to the directory with extractors
      recipe (str): recipe in / separated
      interactive (bool): show image and print report; else only give summary
      reportHTML (bool): return report in qside html style

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

    report = 'ExtractorSuccess'
    htmlStr= 'Please visit <a href="https://pasta-eln.github.io/pasta-eln/extractors.html#'
    success = True
    if isinstance(filePath, str):
      filePath = Path(filePath)
    if reportHTML:
      report = '<h3>Report on extractor test</h3>'
      report +='check file: '+str(filePath)+'<br>'
    extension = filePath.suffix[1:]
    pyFile = 'extractor_'+extension+'.py'
    if extractorPath is None:
      extractorPath = self.extractorPath
    #start testing
    if (extractorPath/pyFile).exists():
      if reportHTML:
        report += 'use extractor: '+str(extractorPath/pyFile)+'<br>'
    else:
      success = False
      if reportHTML:
        report += '<font color="red">No fitting extractor found:'+pyFile+'</font><br>'
      else:
        report = 'NoExtractor'
    if success:
      try:
        module  = importlib.import_module(pyFile[:-3])
        content = module.use(filePath, recipe)
      except:
        success = False
        if reportHTML:
          report += '<font color="red">Python error in extractor</font><br>'
          report += htmlStr+'python-error">website</a><br>'
          report += '\n'+traceback.format_exc()+'\n'
    if success:
      try:
        _ = json.dumps(content)
      except:
        if interactive:
          print("**ERROR: extractor reply not json dumpable.")
        if reportHTML:
          report += '<font color="red">Some json format does not fit</font><br>'
        else:
          report = "ExtractorERROR json dumpable"
    if success:
      try:
        _ = json.dumps(content['metaVendor'])
        report += 'Number of vendor entries: '+str(len(content['metaVendor']))+'<br>'
      except:
        success = False
        if interactive:
          print("  DETAIL metaVendor incorrect")
        if reportHTML:
          report += '<font color="red">Some json format does not fit in metaVendor</font><br>'
          report += htmlStr+'metadata-error">website</a><br>'
        else:
          report = "ExtractorERROR metaVendor"
        #iterate keys
        for key in content['metaVendor']:
          try:
            _ = json.dumps(content['metaVendor'][key])
          except:
            if reportHTML:
              report += '<font color="red">FAIL '+key+' : '+str(content['metaVendor'][key])+' type:'+\
                        str(type(content['metaVendor'][key]))+'</font><br>'
            else:
              print('    FAIL',key, content['metaVendor'][key], type(content['metaVendor'][key]))

    if success:
      try:
        _ = json.dumps(content['metaUser'])
        report += 'Number of user entries: '+str(len(content['metaUser']))+'<br>'
      except:
        if interactive:
          print("  DETAIL metaUser incorrect")
        if reportHTML:
          report += '<font color="red">Some json format does not fit in metaUser</font><br>'
          report += htmlStr+'metadata-error">website</a><br>'
        else:
          report = "ExtractorERROR metaUser"
        #iterate keys
        for key in content['metaUser']:
          try:
            _ = json.dumps(content['metaUser'][key])
          except:
            if reportHTML:
              report += '<font color="red">FAIL '+key+' : '+content['metaUser'][key]+' type:'+\
                        str(type(content['metaVendor'][key]))+'</font><br>'
            else:
              print('    FAIL',key, content['metaUser'][key], type(content['metaUser'][key]))
      #verify image is of correct type
    if success and 'image' not in content:
      success = False
      if interactive:
        print('**Error: image not produced by extractor')
      if reportHTML:
        report += '<font color="red">Image does not exist</font><br>'
      else:
        report = "ExtractorERROR image not exsits"
    if success and isinstance(content['image'],Image.Image):
      success = False
      if interactive:
        content['image'].show()
        print('**Warning: image is a PIL image: not a base64 string')
        print('Encode image via the following: pay attention to jpg/png which is encoded twice\n```')
        print('from io import BytesIO')
        print('figfile = BytesIO()')
        print('image.save(figfile, format="PNG")')
        print('imageData = base64.b64encode(figfile.getvalue()).decode()')
        print('image = "data:image/jpg;base64," + imageData')
        print('```')
      if reportHTML:
        report += '<font color="red">Image is PIL image</font><br>'
        report += htmlStr+'pillow-image">website</a><br>'
      else:
        report = "ExtractorERROR PIL image"
    if success and isinstance(content['image'], mpaxes._subplots.Axes): # pylint: disable=protected-access
      success = False
      if interactive:
        plt.show()
        print('**Warning: image is a matplotlib axis: not a svg string')
        print('  figfile = StringIO()')
        print('plt.savefig(figfile, format="svg")')
        print('image = figfile.getvalue()')
      if reportHTML:
        report += '<font color="red">Image are matplot axis</font><br>'
        report += htmlStr+'matplotlib">website</a><br>'
      else:
        report = "ExtractorERROR Matplot image"
    if success and isinstance(content['image'], str):  #show content
      report += '<b>Additional window shows the image</b><br>'
      if content['image'].startswith('data:image/'):
        #png or jpg encoded base64
        extension = content['image'][11:14]
        i = base64.b64decode(content['image'][22:])
      else:
        #svg data
        i = cairosvg.svg2png(bytestring=content['image'].encode())
      i = BytesIO(i)
      i = Image.open(i)
      if interactive:
        i.show()
      del content['image']
    if interactive and not reportHTML:
      print('Identified metadata',content)
    os.environ['QT_API'] = 'pyside6'
    return report


  ######################################################
  ### Wrapper for database functions
  ######################################################
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
    ### compare with file system
    if verbose:
      output += f'{Bcolors.UNDERLINE}**** File status ****{Bcolors.ENDC}\n'
    viewProjects   = self.db.getView('viewDocType/x0')
    inDB_all = self.db.getView('viewHierarchy/viewPaths')
    pathsInDB_data = [i['key'] for i in inDB_all if i['value'][1][0][0]!='x']
    pathsInDB_folder = [i['key'] for i in inDB_all if i['value'][1][0][0]=='x']
    count = 0
    for projI in viewProjects:
      projDoc = self.db.getDoc(projI['id'])
      for root, dirs, files in os.walk(self.basePath/projDoc['-branch'][0]['path']):
        for fileName in files:
          if fileName.startswith('.') or fileName.startswith('trash_'):
            continue
          path = (Path(root).relative_to(self.basePath) /fileName).as_posix()
          if path not in pathsInDB_data:
            output += '**ERROR File on harddisk but not DB: '+path+'\n'
            count += 1
          else:
            pathsInDB_data.remove(path)
        for dirName in dirs:
          if dirName.startswith('.') or dirName.startswith('trash_'):
            continue
          path = (Path(root).relative_to(self.basePath) /dirName).as_posix()
          if path not in pathsInDB_folder:
            output += '**ERROR Directory on harddisk but not DB:'+path+'\n'
            count += 1
          else:
            pathsInDB_folder.remove(path)
    output += 'Number of files on disk that are not in database '+str(count)+'\n'
    orphans = [i for i in pathsInDB_data   if not (self.basePath/i).exists() and ":/" not in i]
    orphans+= [i for i in pathsInDB_folder if not (self.basePath/i).exists() ]
    if len(orphans)>0:
      output += f'{Bcolors.FAIL}**ERROR bch01: These files of database not on filesystem: '+',\t'.join(orphans)\
               +f'{Bcolors.ENDC}\n'
    if len(orphans)==0 and count==0:
      output += "** File tree CLEAN **\n"
    else:
      output += "** File tree NOT clean **\n"
    return output
