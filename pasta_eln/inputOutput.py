"""Input and output functions towards the .eln file-format"""
import os, json, shutil, logging, hashlib, re
from typing import Any
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
from anytree import PreOrderIter, Node
from pasta_eln import __version__
from .backend import Backend

#GENERAL TERMS IN ro-crate-metadata.json (None implies definitely should not be saved)
pasta2json:dict[str,Any] = {
  '_id'         : 'identifier',
  '_rev'        : None,
  '_attachments': None,
  '-attachment' : None,
  '-branch'     : None,
  '-client'     : None,
  '-date'       : 'dateModified',
  '-name'       : 'title',
  '-tags'       : 'keywords',
  'image'       : None,
  'comment'     : 'description',
  'content'     : 'text',
  'links'       : 'mentions',
  'shasum'      : None,
}
json2pasta = {v:k for k,v in pasta2json.items() if v is not None}

# Special terms in other ELNs: only add the ones that are required for function for PASTA
elabFTW = {
  'elabid':'_id',
  'title':'-name',
  'tags':'-tags',
  'lastchange':'-date',
  'userid':'-user',
  'metadata':'metaUser',
  'id':'_id',
  'category': '-type',
  'dateCreated': '-date'
}


def importELN(backend:Backend, elnFileName:str) -> str:
  '''
  import .eln file from other ELN or from PASTA

  Args:
    backend (backend): backend
    elnFileName (str): name of file

  Returns:
    str: success message
  '''
  elnName = ''
  elnVersion = ''
  with ZipFile(elnFileName, 'r', compression=ZIP_DEFLATED) as elnFile:
    files = elnFile.namelist()
    logging.info('All files '+', '.join(files))
    dirName=Path(files[0]).parts[0]
    if dirName+'/ro-crate-metadata.json' not in files:
      print('**ERROR: ro-crate does not exist in folder. EXIT')
      return '**ERROR: ro-crate does not exist in folder. EXIT'
    graph = json.loads(elnFile.read(dirName+'/ro-crate-metadata.json'))["@graph"] #list
    #find information from master node
    rocrateNode = [i for i in graph if i["@id"]=="ro-crate-metadata.json"][0]
    if 'sdPublisher' in rocrateNode:
      elnName     = rocrateNode['sdPublisher']['name']
    if 'version' in rocrateNode:
      elnVersion  = rocrateNode['version']
    else:
      elnVersion  = ''
    logging.info('Import '+elnName+' '+elnVersion)
    if elnName=='eLabFTW':
      json2pasta.update(elabFTW)
    print('ELN and translator:', elnName, json2pasta,'\n---------------------------')
    mainNode    = [i for i in graph if i["@id"]=="./"][0]

    ################
    # subfunctions #
    ################
    def json2pastaFunction(inputData:dict[str,Any]) -> tuple[dict[str,Any], str, list[Any], str]:
      """
      convert json data to pastaStyle

      Args:
        inputData (dict): input data in document

      Returns:
        dict: output data as document
        str: id in eln=path in zip file
        list: list of children
        str: data or dataset
      """
      output = {}
      elnID = inputData['@id'][2:] if inputData['@id'][:2]=='./' else inputData['@id']
      children = inputData.pop('hasPart') if 'hasPart' in inputData else []
      dataType = inputData['@type']
      for key, value in inputData.items():
        if key in ['@id','@type','hasPart','author','contentSize', 'sha256']:
          continue
        if key in json2pasta:
          output[json2pasta[key]] = value
        else:
          print('**Warning: could not translate: '+key+'   from eln:'+elnName)
          output['imported_'+key] = value
      return output, elnID, children, dataType

    def processPart(part:dict[str,str]) -> int:
      """
      recursive function call to process this node

      Args:
        part (dict): dictionary containing this data content

      Returns:
        bool: success of this function
      """
      addedDocs = 1
      if not isinstance(part, dict): #leave these tests in since other .elns might do funky stuff
        print("**ERROR in part",part)
        return False
      logging.info('Process: '+part['@id'])
      print('Process: '+part['@id'])
      # find next node to process
      docS = [i for i in graph if '@id' in i and i['@id']==part['@id']]
      if len(docS)!=1:
        print('**ERROR zero or multiple nodes with same id', docS)
        return -1
      doc, elnID, children, dataType = json2pastaFunction(docS[0])
      if elnName == 'PASTA ELN':
        fullPath = backend.basePath/elnID
      else:
        fullPath = backend.basePath/backend.cwd/elnID.split('/')[-1]
      if dataType.lower()=='dataset':
        if elnName == 'PASTA ELN':
          supplementalInfo = Path(dirName)/elnID/'metadata.json'
        elif elnName == 'eLabFTW':
          supplementalInfo = Path(dirName)/elnID/'export-elabftw.json'
        else:
          print('**ERROR could not identify elnName', elnName)
          return -1
        with elnFile.open(supplementalInfo.as_posix()) as fIn:
          jsonContent = json.loads( fIn.read() )
          if isinstance(jsonContent, list):
            jsonContent = jsonContent[0]
          if elnName == 'PASTA ELN':
            doc.update( jsonContent )
          else:
            doc['from '+elnName] = jsonContent
      elif re.match(r'^metadata_.-\w{32}\.json$', elnID.split('/')[-1]) is None:
        if elnName == 'PASTA ELN':
          metadataPath = Path(dirName)/(elnID.replace('.','_')+'_metadata.json')
          with elnFile.open(metadataPath.as_posix()) as fIn:
            doc.update( json.loads( fIn.read() ) )
        elif elnName == 'eLabFTW' and elnID.endswith('export-elabftw.json'):
          return 0
        else:
          print('**ERROR got a file which I do not understand ',elnID)
          target = open(fullPath, "wb")
          source = elnFile.open(dirName+'/'+elnID)
          with source, target:  #extract one file to its target directly
            shutil.copyfileobj(source, target)
      else:
        metadataPath = Path(dirName)/elnID
        with elnFile.open(metadataPath.as_posix()) as fIn:
          doc.update( json.loads( fIn.read() ) )
      # save
      if elnName == 'PASTA ELN':
        backend.db.saveDoc(doc)
        if dataType=='dataset':
          fullPath.mkdir(exist_ok=True)
          with open(fullPath/'.id_pastaELN.json', 'w', encoding='utf-8') as fOut:
            fOut.write(json.dumps(doc))
        elif re.match(r'^metadata_.-\w{32}\.json$', elnID.split('/')[-1]) is None:
          if not fullPath.parent.exists():
            fullPath.parent.mkdir()
          target = open(fullPath, "wb")
          try:
            source = elnFile.open(dirName+'/'+part['@id'])
            with source, target:  #extract one file to its target directly
              shutil.copyfileobj(source, target)
          except:
            print('--------- could not read file from zip', dirName+'/'+part['@id'])
          # print('\nIn eln\n  '+'\n  '.join([k+': '+str(v) for k,v in doc.items()]))
          # print('   ',fullPath)
      else:  # OTHER VENDORS
        if dataType.lower()=='dataset':
          docType = 'x'+str(len(elnID.split('/')) - 1)
          backend.cwd = backend.basePath / Path(elnID).parent
        else:
          docType = '-'
        if docType=='x0':
          backend.hierStack = []
        if '_id' in doc:
          doc['externalID'] = doc.pop('_id')
        docID = backend.addData(docType, doc)
        if elnName != 'PASTA ELN' and docID[0]=='x':
          backend.hierStack += [docID]
          backend.cwd        = backend.basePath/ backend.db.getDoc(docID)['-branch'][0]['path']

      # children, aka recursive part
      logging.info('subparts:'+', '.join(['  '+i['@id'] for i in children]))
      for child in children:
        if child['@id'].endswith('/metadata.json') or child['@id'].endswith('_metadata.json'):  #skip own metadata
          continue
        addedDocs += processPart(child)

        # backend.changeHierarchy(backend.currentID)
        # backend.changeHierarchy(None)
        # if newNode['@id'].endswith('.json'):                    #read json content into DB
        #   with elnFile.open( (Path(dirName)/newNode['@id']).as_posix() ) as fIn:
        #     jsonContent = fIn.read()
        #     for dataJson in json.loads(jsonContent):
        #       #Transcribe and save content
        #       dataPasta = {}
        #       for key, value in dataJson.items():
        #         if key in json2pasta:
        #           dataPasta[json2pasta[key]] = value
        #         else:
        #           dataPasta[key] = value
        #           keysNotInDict.add(key)
        #       dataPasta['-client'] = 'Imported from '+elnName+' '+elnVersion
        #       addedDocs += 1
        #       for reqKey in requiredKeys:
        #         if reqKey not in dataPasta:
        #           print('**ERROR key not in doc', reqKey)
        #       backend.db.saveDoc(dataPasta)
      return addedDocs

    ######################
    #main function
    #iteratively go through list
    addedDocuments = 0
    for part in mainNode['hasPart']:
      if not part['@id'].endswith('ro-crate-metadata.json'):
        addedDocuments += processPart(part)
  return 'Success: imported '+str(addedDocuments)+' documents from file '+elnFileName+' from ELN '+elnName+' '+elnVersion



##########################################
###               EXPORT               ###
##########################################
def exportELN(backend:Backend, projectID:str, fileName:str='') -> str:
  """
  export eln to file

  Args:
    backend (backend): PASTA backend instance
    projectID (str): docId of project
    fileName (str): fileName which to use for saving; default='' saves in local folder

  Returns:
    str: report of exportation
  """
  print('>>', projectID)
  # define initial information
  keysInSupplemental:set[str] = set()
  docProject = backend.db.getDoc(projectID)
  dirNameProject = docProject['-branch'][0]['path']
  fileName = dirNameProject+'.eln' if fileName=='' else fileName

  def iterateTree(nodeHier:Node, graph:list[dict[str,Any]]) -> str:
    """
    Recursive function to translate the hierarchical node into a tree-node

    Args:
      nodeHier (Anytree.Node): anytree node
      graph    (list): list of nodes

    Returns:
      str: tree node
    """
    # separate into main and supplemental information
    doc = backend.db.getDoc(nodeHier.id)
    path = doc['-branch'][0]['path']
    fileAttached = True
    if path is None or path.startswith('https:'):
      parentID = doc['-branch'][0]['stack'][-1]
      path = backend.db.getDoc(parentID)['-branch'][0]['path']
      path += '/metadata_'+nodeHier.id+'.json'
      fileAttached = False
    docMain= {'@id': path}
    docSupp = {}
    for key, value in doc.items():
      if key in pasta2json and pasta2json[key] is not None:
        docMain[pasta2json[key]] = value
      else:
        docSupp[key] = value
    # remove personal data
    docMain['author'] = '_'
    del docSupp['-user']
    # get path to metadata file
    if fileAttached:
      if nodeHier.id[0]=='x':
        pathMetadata = path+'/metadata.json'
      else:
        pathArray = list(Path(path).as_posix().split('/'))
        pathArray[-1] = pathArray[-1].replace('.','_')+'_metadata.json'
        pathMetadata = '/'.join(pathArray)
    # add structural information: dataset, hasPart
    if nodeHier.id[0]=='x':
      hasPart = []
      for child in nodeHier.children:
        res = iterateTree(child, graph)
        if res is not None:
          hasPart.append( res )
      docMain['hasPart'] = [{'@id':pathMetadata}]
      if len(hasPart)>0:
        docMain['hasPart'] += [{'@id':i} for i in hasPart]
      docMain['@type'] = 'dataset'
    else:
      docMain['@type'] = 'data'
    # prepare the supplemental
    nonlocal keysInSupplemental
    keysInSupplemental = keysInSupplemental.union(docSupp)
    zipContent = json.dumps(docSupp, indent=2)
    if fileAttached:
      roCrateMetadata = {'description':'JSON export',
                         'contentType':'application/json',
                         'contentSize':str(len(zipContent)),
                         'sha256':hashlib.sha256(zipContent.encode()).hexdigest(),
                         '@id':pathMetadata,
                         docMain['@type']:'data'}
      graph.append(roCrateMetadata)
      elnFile.writestr(dirNameProject+'/'+pathMetadata, zipContent)
    else:
      if (backend.basePath/path).exists():
        with open(backend.basePath/path, 'rb') as fIn:
          fileContent = fIn.read()
          docMain['contentSize'] = str(len(fileContent))
          docMain['sha256']      = hashlib.sha256(fileContent).hexdigest()
      else:
        docMain['contentSize'] = str(len(zipContent))
        docMain['sha256']      = hashlib.sha256(zipContent.encode()).hexdigest()
      elnFile.writestr(dirNameProject+'/'+path, zipContent)
    # write data file
    graph.append(docMain)
    return docMain['@id']
  #
  #
  # == MAIN FUNCTION ==
  logging.info('Create eln file '+fileName)
  with ZipFile(fileName, 'w', compression=ZIP_DEFLATED) as elnFile:
    # ------- Create main graph -------------------
    listHier = backend.db.getHierarchy(projectID, allItems=False)
    graph:list[dict[str,Any]] = []
    iterateTree(listHier, graph)  # create json object from anytree

    # ------------------- create ro-crate-metadata.json header -----------------------
    index:dict[str,Any] = {}
    index['@context']= 'https://w3id.org/ro/crate/1.1/context'
    # master node ro-crate-metadata.json
    graphMaster:list[dict[str,Any]] = []
    masterNodeInfo  = {\
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
        'description':'Version '+__version__},\
      'version': '1.0'}
    graphMaster.append(masterNodeInfo)
    authors = backend.configuration['authors']
    masterNodeRoot  = {'@id':'./', '@type':['Dataset'],
                       'hasPart': [{'@id':dirNameProject},
                                   {'@id':dirNameProject+'/ro-crate-metadata.json'},
                                   {'@id':dirNameProject+'/'+dirNameProject+'/datastructure.json'}],
                        # default items mwo-ontology
                       'context': [{'mwo': 'http://purls.helmholtz-metadaten.de/mwo'},{'nfdicore': 'https://nfdi.fiz-karlsruhe.de/ontology'}],
                       'type': 'mwo:ExperimentalWorkflow',
                       'license': 'CC BY 4.0',
                       'format':  [{'fileExtension': '.json'}],
                        # publisher information
                       'authors': [
                         {'firstName':authors[0]['first'], 'surname':authors[0]['last'], 'title':authors[0]['title'],
                          'emailAddress':authors[0]['email'], 'ORCID': authors[0]['orcid'],
                          'affiliation': [{'organization': authors[0]['organizations'][0]['organization'],
                                           'RORID':        authors[0]['organizations'][0]['rorid']}] }
                       ],
                       'datePublished': datetime.now().isoformat()
                      }
    elnFile.writestr(dirNameProject+'/'+dirNameProject+'/datastructure.json',
                     json.dumps(backend.db.getDoc('-ontology-')))
    graphMaster.append(masterNodeRoot)

    # ------------------ copy data-files --------------------------
    # datafiles are already in the graph-graph: only copy and no addition to graph
    for path, _, files in os.walk(backend.basePath/dirNameProject):
      if '/.git' in path:  #if use datalad
        continue
      relPath = os.path.relpath(path, backend.basePath) #path of the folder
      for iFile in files:                               #iterate through all files in folder
        if iFile.startswith('.git') or iFile=='.id_pastaELN.json':
          continue
        elnFile.write(path+'/'+iFile, dirNameProject+'/'+relPath+'/'+iFile)   #zip file

    #finalize file
    index['@graph'] = graphMaster+graph
    elnFile.writestr(dirNameProject+'/'+'ro-crate-metadata.json', json.dumps(index, indent=2))
    # temporary json output
    with open(fileName[:-3]+'json','w', encoding='utf-8') as fOut:
      fOut.write( json.dumps(index, indent=2) )
  keysInSupplemental = {i for i in keysInSupplemental if i not in pasta2json}
  print('Keys in supplemental information', keysInSupplemental)
  return 'Success: exported '+str(len(graph))+' documents into file '+fileName

# SimStack (matsci.org/c/simstack), PMD Meeting september KIT
