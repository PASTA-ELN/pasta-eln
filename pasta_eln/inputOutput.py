"""Input and output functions towards the .eln file-format"""
import os, io, json, shutil, base64, subprocess
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED

def importELN(backend, database, elnFileName):
  '''
  import .eln file from other ELN or from PASTA

  Args:
    backend (backend): backend
    database (string): name of database
    elnFileName (string): name of file

  Returns:
    bool: success of import
  '''

  def processPart(part):
    """
    recursive function call to process this node

    Args:
      part (dict): dictionary containing this data content

    Returns:
      bool: success of this function
    """
    if not isinstance(part, dict):
      print("**ERROR in part",part)
      return False
    print('\nProcess:',part['@id'])
    # find next node to process
    newNode = [i for i in graph if '@id' in i and i['@id']==part['@id']]
    if len(newNode)>1:
      print('**ERROR multiple nodes with same id')
      return False
    # if node with more subnodes
    if len(newNode)==1:
      newNode = newNode[0]
      subparts = newNode.pop('hasPart') if 'hasPart' in newNode else []
      print('subparts:\n'+'\n'.join(['  '+i['@id'] for i in subparts]))
      #depending on ELN
      if elnName=='Kadi4Mat':
        docType = 'x'+str(len(newNode['@id'].split('/'))-2)
        newNode['pathOnKadi4Mat'] = newNode.pop('@id')
        newNode['-name'] = newNode.pop('name')
        if 'description' in newNode:
          newNode['comment']=newNode.pop('description')
      elif elnName=='PASTA ELN':
        docType = newNode['-type'][0]
        newNode['_id'] = newNode.pop('@id')
        if len(subparts)==1 and subparts[0]['@id'].startswith('__thumbnails__'):
          with elnFile.open(dirName+os.sep+subparts[0]['@id']) as elnFilePointer:
            imgdata = elnFilePointer.read()
            if subparts[0]['@id'].endswith('.png'):
              newNode['image'] = "data:image/png;base64," + base64.b64encode(imgdata).decode()
            elif subparts[0]['@id'].endswith('.svg'):
              newNode['image'] = imgdata.decode("utf-8")
            else:
              print("**ERROR cannot read this thumbnail")
          subparts = []
      else:
        print('**ERROR undefined ELN-Name', elnName)
      #for all ELN
      if '@type' in newNode:
        del newNode['@type']
      if elnVersion is not None:
        newNode['importedFrom'] = elnName+' '+elnVersion
        elnVersion = None
      if elnName=='PASTA ELN' and newNode['-type'][0]!='x0':
        backend.db.saveDoc(newNode)
        if newNode['-type'][0][0]=='x':
          os.makedirs(backend.basePath+newNode['-branch'][0]['path'])
        backend.currentID = newNode['_id']
      else:
        backend.addData(docType,newNode)
      #recursive part
      if len(subparts)>0:  #don't do if no subparts: measurements, ...
        backend.changeHierarchy(backend.currentID)
        for subpart in subparts:
          processPart(subpart)
        backend.changeHierarchy(None)
    # ---
    # if final leaf node described in hasPart
    if len(part)>1:
      #save to file
      source = elnFile.open(dirName+os.sep+part['@id'])
      #do database entry
      if elnName=='Kadi4Mat':
        docType = 'measurement'
        part['otherELNName'] = part.pop('@id')
        part['-name'] = os.path.basename(part['otherELNName'])
        if 'description' in part:
          part['comment']=part.pop('description')
        del part['@type']
        targetFileName = os.path.basename(part['otherELNName'])
      elif elnName=='PASTA ELN':
        targetFileName = part['@id']
      else:
        print('**ERROR undefined ELN-Name', elnName)
      target = open(targetFileName, "wb")
      with source, target:  #extract one file to its target directly
        shutil.copyfileobj(source, target)
      if elnName!='PASTA ELN':
        backend.addData(docType,part)
    return True

  ######################
  #main function
  elnName = None
  elnVersion = None
  with ZipFile(elnFileName, 'r', compression=ZIP_DEFLATED) as elnFile:
    files = elnFile.namelist()
    dirName=files[0].split(os.sep)[0]
    if dirName+'/ro-crate-metadata.json' not in files:
      print('**ERROR: ro-crate does not exist in folder. EXIT')
      return False
    graph = json.loads(elnFile.read(dirName+'/ro-crate-metadata.json'))["@graph"]
    # print(json.dumps(graph,indent=2))
    #find information from master node
    rocrateNode = [i for i in graph if i["@id"]=="ro-crate-metadata.json"][0]
    if 'sdPublisher' in rocrateNode:
      elnName     = rocrateNode['sdPublisher']['name']
    if 'version' in rocrateNode:
      elnVersion  = rocrateNode['version']
    else:
      elnVersion  = ''
    print('Import',elnName,elnVersion)
    mainNode    = [i for i in graph if i["@id"]=="./"][0]
    #iteratively go through list
    for part in mainNode['hasPart']:
      processPart(part) #TODO_P5 first child should get elnName and version
  return True


def exportELN(backend, docID):
  """
  export eln to file

  Args:
    backend (backend): PASTA backend instance
    docID (string): docId of project

  Returns:
    bool: success of this export
  """
  docProject = backend.db.getDoc(docID)
  dirNameProject = docProject['-branch'][0]['path']
  zipFileName = dirNameProject+'.eln'
  print('Create eln file '+zipFileName)
  with ZipFile(zipFileName, 'w', compression=ZIP_DEFLATED) as zipFile:
    # numAttachments = 0
    graph = []

    #1 ------- write JSON files -------------------
    listDocs = backend.db.getView('viewHierarchy/viewHierarchy', startKey=docID)
    #create tree of hierarchical data
    treedata = {}

    def listChildren(idString, level):
      """
      List all children

      Args:
        idString (string): id of this part
        level (int): hierarchical level starting from 0

      Returns:
        list: list of children ids
      """
      items = [i for i in listDocs if len(i['key'].split(' '))==level]
      if idString is not None:
        items = [i for i in items if i['key'].startswith(idString)]
      #sort by child
      keys = [i['key'] for i in items]
      childNums = [i['value'][0] for i in items]
      items = [x for _, x in sorted(zip(childNums, keys))]
      #create sub-children
      for item in items:
        children = listChildren(item,level+1)
        treedata[item.split(' ')[-1]] = children
        if level == 1:
          treedata['__masterID__'] = item
      return [i.split(' ')[-1] for i in items]

    listChildren(idString=None, level=1)
    masterID = treedata.pop('__masterID__')
    # print(treedata)
    for doc in treedata:
      doc = backend.db.getDoc(doc)
      doc['@id']   = doc.pop('_id')
      doc['@type'] = "DigitalDocument"
      if len(treedata[doc['@id']])>0:
        doc['hasPart'] = [{'@id':i} for i in treedata[doc['@id']]]
      if 'image' in doc:
        fileName = '__thumbnails__'+os.sep+doc['@id']
        if doc['image'].startswith('data:image/png'):
          fileName += '.png'
          imgdata = doc['image'][22:]
          imgdata = base64.b64decode(imgdata)
          imgdata = io.BytesIO(imgdata)
          target = zipFile.open(dirNameProject+os.sep+fileName,'w')
          with imgdata, target:  #extract one file to its target directly
            shutil.copyfileobj(imgdata, target)
        elif doc['image'].startswith('<?xml'):
          fileName += '.svg'
          zipFile.writestr(dirNameProject+os.sep+fileName, doc['image'])
        else:
          print('image type not implemented')
        del doc['image']
        doc['hasPart'] = [{'@id':fileName}]
        graph.append({'@id':fileName, '@type':'File'})
      graph.append(doc)
      # Attachments are not saved

    #2 ------------------ write data-files --------------------------
    masterChildren = [{'@id':masterID}]
    for path, _, files in os.walk(dirNameProject):
      if '/.git' in path:
        continue
      path = os.path.relpath(path, backend.basePath)
      for iFile in files:
        if iFile.startswith('.git') or iFile=='.id_pastaELN.json':
          continue
        masterChildren.append({'@id':path+os.sep+iFile})
        graph.append({'@id':path+os.sep+iFile, '@type':'File'})
        zipFile.write(path+os.sep+iFile, dirNameProject+os.sep+path+os.sep+iFile)

    #3 ------------------- write index.json ---------------------------
    index = {}
    index['@context']= 'https://w3id.org/ro/crate/1.1/context'
    # master node ro-crate-metadata.json
    graphMaster = []
    cwd = backend.cwd
    os.chdir(backend.softwarePath)
    cmd = ['git','tag']
    output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    os.chdir(backend.basePath/cwd)
    masterNode  = {\
      '@id':'ro-crate-metadata.json',\
      '@type':'CreativeWork',\
      'about': {'@id': './'},\
      'conformsTo': {'@id': 'https://w3id.org/ro/crate/1.1'},\
      'schemaVersion': 'v1.0',\
      'dateCreated': datetime.now().isoformat(),\
      'sdPublisher': {'@type':'Organization', 'name': 'PASTA ELN',\
        'logo': 'https://raw.githubusercontent.com/PASTA-ELN/desktop/main/pasta.png',\
        'slogan': 'The favorite ELN for experimental scientists',\
        'url': 'https://github.com/PASTA-ELN/',\
        'description':'Version '+output.stdout.decode('utf-8').split()[-1]},\
      'version': '1.0'}
    graphMaster.append(masterNode)
    masterNode  = {'@id':'./', '@type':['Dataset'], 'hasPart': masterChildren}
    graphMaster.append(masterNode)
    #finalize file
    index['@graph'] = graphMaster+graph
    zipFile.writestr(dirNameProject+os.sep+'ro-crate-metadata.json', json.dumps(index, indent=2))
  return True


def backup(backend, method='backup', **kwargs):
  """
  backup, verify, restore information from/to database
  - all data is saved to one zip file (NOT ELN file)
  - after restore-to-database, the database changed (new revision)

  Args:
    backend (Pasta): pasta-backend
    method (string): backup, restore, compare
    kwargs (dict): additional parameter, i.e. callback

  Returns:
      bool: success
  """
  dirNameProject = 'backup'
  zipFileName = ''
  if backend.cwd is None:
    print("**ERROR bbu01: Specify zip file name or database")
    return False
  zipFileName = backend.basePath.parent/'pasta_backup.zip'
  if method=='backup':  mode = 'w'
  else:                 mode = 'r'
  print('  '+method.capitalize()+' to file: '+zipFileName.as_posix())
  with ZipFile(zipFileName, mode, compression=ZIP_DEFLATED) as zipFile:

    # method backup, iterate through all database entries and save to file
    if method=='backup':
      numAttachments = 0
      #write JSON files
      listDocs = backend.db.db
      listFileNames = []
      for doc in listDocs:
        if isinstance(doc, str):
          doc = backend.db.getDoc(doc)
        fileName = '__database__/'+doc['_id']+'.json'
        listFileNames.append(fileName)
        zipFile.writestr((Path(dirNameProject)/fileName).as_posix(), json.dumps(doc) )
        # Attachments
        if '_attachments' in doc:
          numAttachments += len(doc['_attachments'])
          for i in range(len(doc['_attachments'])):
            attachmentName = Path(dirNameProject)/'__database__'/doc['_id']/('v'+str(i)+'.json')
            zipFile.writestr(attachmentName.as_posix(), json.dumps(doc.get_attachment('v'+str(i)+'.json')))
      #write data-files
      for path, _, files in os.walk(backend.basePath):
        path = Path(path).relative_to(backend.basePath)
        for iFile in files:
          listFileNames.append(path/iFile)
          # print('in',Path().absolute(),': save', path/iFile,' as', Path(dirNameProject)/path/iFile)
          zipFile.write(backend.basePath/path/iFile, Path(dirNameProject)/path/iFile)
      #create some fun output
      compressed, fileSize = 0,0
      for doc in zipFile.infolist():
        compressed += doc.compress_size
        fileSize   += doc.file_size
      print(f'  File size: {fileSize:,} byte   Compressed: {compressed:,} byte')
      print(f'  Num. documents (incl. ontology and views): {len(backend.db.db):,}\n')#,    num. attachments: {numAttachments:,}\n')
      return True

    # method compare and restore
    if zipFileName.as_posix().endswith('.eln'):
      print('**ERROR: cannot compare/restore .eln files')
      return False
    # method compare
    if  method=='compare':
      filesInZip = zipFile.namelist()
      print('  Number of documents (incl. ontology and views) in file:',len(filesInZip))
      differenceFound, comparedFiles, comparedAttachments = False, 0, 0
      for doc in backend.db.db:
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
      beforeLength, restoredFiles = len(backend.db.db), 0
      for fileName in zipFile.namelist():
        if fileName.startswith('backup/__database__') and (not \
          (fileName.startswith('backup/__database__/_') or fileName.startswith('backup/__database__/-'))):  #do not restore design documents and ontology
          restoredFiles += 1
          zipData = json.loads( zipFile.read(fileName) )
          fileName = fileName[len('backup/__database__/'):]
          if '/' in fileName:  #attachment
            doc = backend.db.getDoc(fileName.split('/')[0])
            doc.put_attachment(fileName.split('/')[1], 'application/json', json.dumps(zipData))
          else:                                                           #normal document
            backend.db.saveDoc(zipData)
      print('  Number of documents & revisions in file:',restoredFiles)
      print('  Number of documents before and after restore:',beforeLength, len(backend.db.db),'\n')
      return True
  return False
