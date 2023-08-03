"""Input and output functions towards the .eln file-format"""
import os, json, shutil, logging, hashlib, re, requests
from typing import Any, Optional
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
from anytree import PreOrderIter, Node
from pasta_eln import __version__
from .backend import Backend
from .miscTools import createDirName

#GENERAL TERMS IN ro-crate-metadata.json (None implies definitely should not be saved)
pasta2json:dict[str,Any] = {
  '_id'         : 'identifier',
  '_rev'        : None,
  '_attachments': None,
  '-attachment' : None,
  '-branch'     : None,
  '-client'     : None,
  '-date'       : 'dateModified',
  '-name'       : 'name',
  '-tags'       : 'keywords',
  'image'       : None,
  'comment'     : 'description',
  'content'     : 'text',
  'links'       : 'mentions',
  'shasum'      : None,
}
json2pasta = {v:k for k,v in pasta2json.items() if v is not None}

# discuss: Always RO-crate names

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
    if f'{dirName}/ro-crate-metadata.json' not in files:
      print('**ERROR: ro-crate does not exist in folder. EXIT')
      return '**ERROR: ro-crate does not exist in folder. EXIT'
    graph = json.loads(elnFile.read(f'{dirName}/ro-crate-metadata.json'))["@graph"]
    #find information from master node
    rocrateNode = [i for i in graph if i["@id"]=="ro-crate-metadata.json"][0]
    if 'sdPublisher' in rocrateNode:
      elnName     = rocrateNode['sdPublisher']['name']
    elnVersion = rocrateNode['version'] if 'version' in rocrateNode else ''
    logging.info('Import %s %s', elnName, elnVersion)
    if elnName=='eLabFTW':
      json2pasta.update(elabFTW)
    logging.info('ELN and translator: %s %s', elnName, str(json2pasta))
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
          print(f'**Warning: could not translate: {key}   from eln:{elnName}')
          output[f'imported_{key}'] = value
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
      # find next node to process
      docS = [i for i in graph if '@id' in i and i['@id']==part['@id']]
      if len(docS)!=1 or backend.cwd is None:
        print('**ERROR zero or multiple nodes with same id', docS,' or cwd is None in '+part['@id'])
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
            doc[f'from {elnName}'] = jsonContent
      elif re.match(r'^metadata_.-\w{32}\.json$', elnID.split('/')[-1]) is None:
        if elnName == 'PASTA ELN':
          if elnID.endswith('datastructure.json'):
            return 0
          metadataPath = Path(dirName)/(elnID.replace('.','_')+'_metadata.json')
          with elnFile.open(metadataPath.as_posix()) as fIn:
            doc.update( json.loads( fIn.read() ) )
        elif elnName == 'eLabFTW' and elnID.endswith('export-elabftw.json'):
          return 0
        else:
          print('**ERROR got a file which I do not understand ',elnID)
          target = open(fullPath, "wb")
          source = elnFile.open(f'{dirName}/{elnID}')
          with source, target:  #extract one file to its target directly
            shutil.copyfileobj(source, target)
      else:
        metadataPath = Path(dirName)/elnID
        with elnFile.open(metadataPath.as_posix()) as fIn:
          doc.update( json.loads( fIn.read() ) )
      # save
      if elnName == 'PASTA ELN':
        backend.db.saveDoc(doc)
        if dataType.lower()=='dataset':
          fullPath.mkdir(exist_ok=True)
          with open(fullPath/'.id_pastaELN.json', 'w', encoding='utf-8') as fOut:
            fOut.write(json.dumps(doc))
        elif re.match(r'^metadata_.-\w{32}\.json$', elnID.split('/')[-1]) is None:
          if not fullPath.parent.exists():
            fullPath.parent.mkdir()
          target = open(fullPath, "wb")
          try:
            source = elnFile.open(f'{dirName}/' + part['@id'])
            with source, target:  #extract one file to its target directly
              shutil.copyfileobj(source, target)
          except Exception:
            logging.warning(
                f'--------- could not read file from zip: {dirName}/' +
                part['@id'])
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
  return f'Success: imported {str(addedDocuments)} documents from file {elnFileName} from ELN {elnName} {elnVersion}'

# move metadata-s-aoeuaoe.json to ??
# create pip-line for exporting, testing, Import
# send pasta email

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
  # define initial information
  docProject = backend.db.getDoc(projectID)
  dirNameProject = docProject['-branch'][0]['path']
  fileName = fileName or dirNameProject
  fileName = fileName if fileName.endswith('.eln') else f'{fileName}.eln'
  keysInSupplemental:set[str] = set()
  filesNotInProject = []

  def separate(doc):
    path =  f"{doc['-branch'][0]['path']}/" if doc['-type'][0][0]=='x' else doc['-branch'][0]['path']
    pathUsed = True
    if path is None:
      pathUsed = False
      path = './'+dirNameProject+'/'+doc['-type'][0]+createDirName(doc['-name'], 'x0', 0)
    if not path.startswith(dirNameProject) and not path.startswith('http') and pathUsed:
      filesNotInProject.append(path)
    if not path.startswith('http') and pathUsed:
      path = f'./{path}'
    docMain= {'@id': path}
    if not pathUsed:
      docMain['@type'] = '_metadata_' #TODO_P1 real type
    docSupp = {}
    for key, value in doc.items():
      if key in pasta2json and pasta2json[key] is not None:
        docMain[pasta2json[key]] = value
      else:
        docSupp[key] = value
    # remove personal data
    docMain['author'] = '_'
    del docSupp['-user']
    if 'image' in docSupp:
      del docSupp['image']
    docSupp['_id'] = docMain['identifier'] #ensure id is present in main and supplementary information
    nonlocal keysInSupplemental
    keysInSupplemental = keysInSupplemental.union(docSupp)
    return path, docMain, docSupp


  def append(graph, doc):
    idsInGraph = [i['@id'] for i in graph]
    if doc['@id'] not in idsInGraph:
      graph.append(doc)
    return



  #TODO_P2 Progress bar: , progressBar:Optional[QProgressBar]=None
  # SimStack (matsci.org/c/simstack), PMD Meeting september KIT
  def iterateTree(nodeHier:Node, graph:list[dict[str,Any]]) -> Optional[str]:
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
    path, docMain, docSupp = separate(doc)

    hasPart = []
    for child in nodeHier.children:
      res = iterateTree(child, graph)
      if res is not None:
        hasPart.append( res )
    if nodeHier.id[0]=='x':
      pathMetadata = f'{path}metadata.json'
      docMain['hasPart'] = [{'@id':pathMetadata}]
      if hasPart:
        docMain['hasPart'] += [{'@id':i} for i in hasPart]

      metadata = {'__main__':docSupp}
      hierStack = docSupp['-branch'][0]['stack']+[docSupp['_id']]
      view = backend.db.getView('viewHierarchy/viewHierarchyAll', startKey=' '.join(hierStack))
      view = [i['id'] for i in view if len(i['key'].split())==len(hierStack)+1 and i['value'][1][0][0]!='x']
      for childID in view:
        _, _, docChildSupp = separate(backend.db.getDoc(childID))
        metadata[childID] = docChildSupp
      zipContent = json.dumps(metadata)
      roCrateMetadata = {'@id':pathMetadata,
                         '@type':'File',
                         'name':'export_metadata.json',
                         'description':'JSON export',
                         'encodingFormat':'application/json',
                         'contentSize':str(len(zipContent)),
                         'sha256':hashlib.sha256(zipContent.encode()).hexdigest(),
                         'dateModified': docMain['dateModified']
                         }
      elnFile.writestr(f'{dirNameProject}/{pathMetadata}', zipContent)
      docMain['@type'] = 'Dataset'
      append(graph, roCrateMetadata)

    fullPath = backend.basePath/path
    if path is not None and fullPath.exists() and fullPath.is_file():
      with open(fullPath, 'rb') as fIn:
        fileContent = fIn.read()
        docMain['contentSize'] = str(len(fileContent))
        docMain['sha256']      = hashlib.sha256(fileContent).hexdigest()
      docMain['@type'] = 'File'
    elif path.startswith('http'):
      res = requests.get(path.replace(':/','://'))
      if res.ok:
        docMain['contentSize'] = str(res.headers['content-length'])
        docMain['sha256']      = hashlib.sha256(res.content).hexdigest()
      else:
        print(f'Info: could not get file {path}')
      docMain['@type'] = 'File'

    append(graph, docMain)
    return docMain['@id']

  # == MAIN FUNCTION ==
  logging.info('Create eln file %s',fileName)
  with ZipFile(fileName, 'w', compression=ZIP_DEFLATED) as elnFile:
    # ------- Create main graph -------------------
    listHier = backend.db.getHierarchy(projectID, allItems=False)
    graph: list[dict[str,Any]] = []
    iterateTree(listHier, graph)  # create json object from anytree

    # ------------------- create ro-crate-metadata.json header -----------------------
    index:dict[str,Any] = {}
    index['@context']= 'https://w3id.org/ro/crate/1.1/context'
    # master node ro-crate-metadata.json
    graphMaster:list[dict[str,Any]] = []
    graphMisc:list[dict[str,Any]] = []
    masterNodeInfo = {
        '@id': './ro-crate-metadata.json',
        '@type': 'CreativeWork',
        'about': {
            '@id': './'
        },
        'conformsTo': {
            '@id': 'https://w3id.org/ro/crate/1.1'
        },
        'schemaVersion': 'v1.0',
        'dateCreated': datetime.now().isoformat(),
        'sdPublisher': {
            '@type': 'Organization',
            'name': 'PASTA ELN',
            'logo':
            'https://raw.githubusercontent.com/PASTA-ELN/desktop/main/pasta.png',
            'slogan': 'The favorite ELN for experimental scientists',
            'url': 'https://github.com/PASTA-ELN/',
            'description': f'Version {__version__}',
        },
        'version': '1.0',
        'datePublished':datetime.now().isoformat(),
    }
    graphMaster.append(masterNodeInfo)
    authors = backend.configuration['authors']
    masterNodeRoot = {
        '@id': './',
        '@type': 'Dataset',
        'hasPart': [
            {'@id': f'./{dirNameProject}/'}
        ],
        'name': 'Exported from PASTA ELN',
        'description': 'Exported content from PASTA ELN',
        'license':'CC BY 4.0',
        'author': [{
            'firstName': authors[0]['first'],
            'surname': authors[0]['last'],
            'title': authors[0]['title'],
            'emailAddress': authors[0]['email'],
            'ORCID': authors[0]['orcid'],
            'affiliation': [{
                'organization': authors[0]['organizations'][0]['organization'],
                'RORID': authors[0]['organizations'][0]['rorid'],
            }],
        }],
        'datePublished':datetime.now().isoformat(),
    }
    graphMaster.append(masterNodeRoot)
    zipContent = json.dumps(backend.db.getDoc('-ontology-'))
    dataStructureInfo = {
        '@id':  f'./{dirNameProject}/datastructure.json',
        '@type': 'File',
        'name':  'data structure',
        'description': 'data structure / schema of the stored data',
        'contentSize':str(len(zipContent)),
        'sha256':hashlib.sha256(zipContent.encode()).hexdigest(),
        'datePublished': datetime.now().isoformat()
    }
    graphMisc.append(dataStructureInfo)
    graph[-1]['hasPart'] += [{'@id': f'./{dirNameProject}/datastructure.json'}]
    elnFile.writestr(f'{dirNameProject}/{dirNameProject}/datastructure.json', zipContent)

    # ------------------ copy data-files --------------------------
    # datafiles are already in the graph-graph: only copy and no addition to graph
    for path, _, files in os.walk(backend.basePath/dirNameProject):
      if '/.git' in path:  #if use datalad
        continue
      relPath = os.path.relpath(path, backend.basePath) #path of the folder
      for iFile in files:                         #iterate through all files in folder
        if iFile.startswith('.git') or iFile=='.id_pastaELN.json':
          continue
        elnFile.write(f'{path}/{iFile}', f'{dirNameProject}/{relPath}/{iFile}')
    for path in set(filesNotInProject):  #set ensures that only added once
      elnFile.write(str(backend.basePath/path), f'{dirNameProject}/{path}')

    #finalize file
    index['@graph'] = graphMaster+graph+graphMisc
    elnFile.writestr(f'{dirNameProject}/ro-crate-metadata.json', json.dumps(index))
  # end writing zip file
  # temporary json output
  # with open(fileName[:-3]+'json','w', encoding='utf-8') as fOut:
  #   fOut.write( json.dumps(index, indent=2) )
  keysInSupplemental = {i for i in keysInSupplemental if i not in pasta2json}
  logging.info('Keys in supplemental information'+', '.join(keysInSupplemental))
  return f'Success: exported {len(graph)} graph-nodes into file {fileName}'
