"""Input and output functions towards the .eln file-format"""
import os, json, shutil, logging, hashlib, copy, uuid
from typing import Any, Optional
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
import requests
from anytree import Node
from pasta_eln import __version__, minisign
from .backend import Backend
from .miscTools import createDirName, generic_hash, flatten, hierarchy
# to discuss
# - genre:docType, simulation, experiment/measurement;  status = Done, finished
# - category: project
# - root entry: authors list, single: @id; multiple authors
#    - add several authors
#    - one creator, multiple authors
# - where to store additional metadata, not in ro-crate-metadata, separate files for each entry?
#    - https://github.com/TheELNConsortium/TheELNFileFormat/issues/58
# - how to store different versions?
#    - history: last version
#    - is based based on, ro-crate id OR update action
# - how should the folder structure be? kadi4mat, sampleDB, does-not-matter:
# - sampleDB ro-crate.json: @type:comment!
#   - ??
# - in "ro-crate-metadata.json" / "sdPublisher": "@id": or name
# - how to verify the import
#   - import - export = the same

# Always use RO-crate names
# GENERAL TERMS IN ro-crate-metadata.json (None implies definitely should not be saved)
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
  '-type'       : 'genre',
  'image'       : None,
  'comment'     : 'description',
  'content'     : 'text',
  'links'       : 'mentions',
  'shasum'      : None,
}
json2pasta:dict[str,Any] = {v:k for k,v in pasta2json.items() if v is not None}

pastaNameTranslation = {'Rev':'Revision'}

# Special terms in other ELNs: only add the ones that are required for function for PASTA
specialTerms:dict[str,dict[str,str]] = {
    'elabFTW': {
      # 'elabid':'_id',
      # 'title':'-name',
      # 'tags':'-tags',
      # 'lastchange':'-date',
      # 'userid':'-user',
      # 'metadata':'metaUser',
      # 'id':'_id',
      # 'category': '-type',
      # 'dateCreated': '-date'
    },
    'SampleDB':{
      'comment':'userComment',
      'genre': '-type'
    }
}


renameELN = {
  'https://kadi.iam.kit.edu':'Kadi4Mat'
}

METADATA_FILE = 'ro-crate-metadata.json'


def tree(graph:dict[Any,Any]) -> str:
  """
  use metadata to create hierarchical tree structure in ascii

  Args:
    graph (dict): tree-graph to be plotted

  Returns:
    str: output of graph as a nice tree
  """
  def process_part(part:dict[Any,Any], level:int) -> str:
    """
    recursive function call to process this node of the tree-graph

    Args:
      part (dict): dictionary entry of this hasPart=part of a parent node; is a node by-itself
      level (int): hierarchy level

    Returns:
      str: one line in the tree
    """
    prefix = '    '*level + '- '
    # find next node to process
    newNode:list[Any] = [i for i in graph if '@id' in i and i['@id'] == part['@id']]
    if len(newNode) == 1:
      output = f'{prefix} {newNode[0]["@id"]} type:{newNode[0]["@type"]} items: {len(newNode[0])-1}\n'  # -1 because @id is not counted
      subparts = newNode[0].pop('hasPart') if 'hasPart' in newNode[0] else []
      if len(subparts) > 0:  # don't do if no subparts: measurements, ...
        for subpart in subparts:
          output += process_part(subpart, level + 1)
    else:                                                       #not found
      output = f'  items: {len(part) - 1}\n'      # -1 because @id is not counted
    return output

  # main tree-function
  #   find information from master node
  ro_crate_node = [i for i in graph if i["@id"] == METADATA_FILE][0]
  output = '- '+METADATA_FILE+'\n'
  if 'sdPublisher' in ro_crate_node:
    name = ro_crate_node['sdPublisher'].get('name','---')
    output += '    - publisher: ' + name  + '\n'
  if 'version' in ro_crate_node:
    output += '    - version: ' + ro_crate_node['version'] + '\n'
  main_node = [i for i in graph if i["@id"] == "./"][0]
  output += '- ./\n'
  #   iteratively go through list
  for part in main_node['hasPart']:
    output += process_part(part, 1)
  return output


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
  projID, projPWD= '', Path('')
  with ZipFile(elnFileName, 'r', compression=ZIP_DEFLATED) as elnFile:
    files = elnFile.namelist()
    logging.info('All files '+', '.join(files))
    dirName=Path(files[0]).parts[0]
    if f'{dirName}/ro-crate-metadata.json' not in files:
      print('**ERROR: ro-crate does not exist in folder. EXIT')
      return '**ERROR: ro-crate does not exist in folder. EXIT'
    graph = json.loads(elnFile.read(f'{dirName}/ro-crate-metadata.json'))["@graph"]
    #find information from master node
    rocrateNode = [i for i in graph if i["@id"].endswith("ro-crate-metadata.json")][0]
    if 'sdPublisher' in rocrateNode:
      elnName     = rocrateNode['sdPublisher'].get('name', '')
      if elnName == '':
        elnName     = rocrateNode['sdPublisher'].get('@id', '')
    elnVersion = rocrateNode['version'] if 'version' in rocrateNode else ''
    logging.info('Import %s %s', elnName, elnVersion)
    if elnName!='PASTA ELN':
      if elnName in specialTerms:
        json2pasta.update(specialTerms[elnName])
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
        if key in json2pasta:  #use known translation
          output[json2pasta[key]] = value
        else:                  #keep name, only prevent causes for errors
          key = f'imported_{key}' if key.startswith(('-','_')) else key
          output[key] = value
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
      print('\nProcess: '+part['@id'])
      # find next node to process
      docS = [i for i in graph if '@id' in i and i['@id']==part['@id']]
      if len(docS)!=1 or backend.cwd is None:
        print('**ERROR zero or multiple nodes with same id', docS,' or cwd is None in '+part['@id'])
        return -1
      doc, elnID, children, dataType = json2pastaFunction(copy.deepcopy(docS[0]))
      if elnName == 'PASTA ELN' and elnID.startswith('http') and ':/' in elnID:
        fullPath = None
      elif elnName == 'PASTA ELN':
        fullPath = backend.basePath/( '/'.join(elnID.split('/')[1:]) )
      else:
        fullPath = backend.basePath/backend.cwd/elnID.split('/')[-1]
      if fullPath is not None:
        if f'{dirName}/{elnID}' in elnFile.namelist():  #could be directory, nothing to copy then
          target = open(fullPath, "wb")
          source = elnFile.open(f'{dirName}/{elnID}')
          with source, target:  #extract one file to its target directly
            shutil.copyfileobj(source, target)
      # ALL ELNS
      if '-tags' not in doc:
        doc['-tags'] = []
      else:
        doc['-tags'] = [i.strip() for i in doc['-tags'].split(',')]
      # PASTA_ELN
      if elnName == 'PASTA ELN':
        doc['-user'] = '_'
        if fullPath is not None:
          fullPath.mkdir(exist_ok=True)
          with open(fullPath/'.id_pastaELN.json', 'w', encoding='utf-8') as fOut:
            fOut.write(json.dumps(doc))
        elif fullPath is not None:
          if not fullPath.parent.is_dir():
            fullPath.parent.mkdir()
          if f'{dirName}/' + part['@id'][2:] in files:  #if a file is saved
            target = open(fullPath, "wb")
            source = elnFile.open(f'{dirName}/' + part['@id'][2:])
            with source, target:  #extract one file to its target directly
              shutil.copyfileobj(source, target)
            backend.useExtractors(fullPath, doc['shasum'], doc)
          else:
            logging.warning('  could not read file from zip: %s',part['@id'])
        else:
          backend.useExtractors(Path(elnID), doc['shasum'], doc)
        backend.db.saveDoc(doc)
      else:  # OTHER VENDORS
        if dataType.lower()=='dataset':
          docType = 'x'+str(len(elnID.split('/')) - 1)
          nonlocal projID
          nonlocal projPWD
          if docType == 'x1' and projID == '':
            print(f'  Want to created project name:{renameELN.get(elnName, elnName)}')
            projID = backend.addData('x0', {'-name':f'Imported project of {renameELN.get(elnName, elnName)} '})
            backend.changeHierarchy(projID)
            projPWD= Path(backend.cwd)
            backend.hierStack = [projID]
          elif docType == 'x1':
            backend.cwd = Path(projPWD)
            backend.hierStack = [projID]
          # backend.cwd = backend.basePath / Path(elnID).parent
          # if not backend.cwd.exists():
          #   backend.cwd = backend.cwd.parent
        else:
          docType = '-'
        if docType=='x0':
          backend.hierStack = []
        if '_id' in doc:
          doc['externalID'] = doc.pop('_id')
        print(f'Want to add doc:{doc} with type:{docType} and cwd:{backend.cwd}')
        docID = backend.addData(docType, doc)
        if docID[0]=='x':
          backend.hierStack += [docID]
          backend.cwd        = backend.basePath/ backend.db.getDoc(docID)['-branch'][0]['path']

      # children, aka recursive part
      logging.info('subparts:'+', '.join(['  '+i['@id'] for i in children]))
      for child in children:
        if child['@id'].endswith('/metadata.json') or child['@id'].endswith('_metadata.json'):  #skip own metadata
          continue
        addedDocs += processPart(child)

      return addedDocs

    ######################
    #main function
    #iteratively go through list
    addedDocuments = 0
    for part in mainNode['hasPart']:
      if not part['@id'].endswith('ro-crate-metadata.json'):
        addedDocuments += processPart(part)
  #return to home stack and path
  backend.cwd = Path(backend.basePath)
  backend.hierStack = []
  print(f'\n\nGraph in metadata file\n{tree(graph)}')
  return f'Success: imported {str(addedDocuments)} documents from file {elnFileName} from ELN {elnName} {elnVersion}'




##########################################
###               EXPORT               ###
##########################################
def exportELN(backend:Backend, projectIDs:list[str], fileName:str, dTypes:list[str], verbose:bool=False) -> str:
  """
  export eln to file

  Args:
    backend (backend): PASTA backend instance
    projectIDs (list): list of docIds of projects
    fileName (str): fileName which to use for saving
    dTypes (list): list of strings which should be included in the output, alongside folders x0 & x1
    verbose (bool): verbose

  Returns:
    str: report of exportation
  """
  def separate(doc: dict[str,Any], dirNameProject: str) -> tuple[str, dict[str,Any], Optional[str]]:
    """ separate document into
    - main information (for all elns) and
    - supplemental information (specific to PastaELN)

    Args:
      doc (dict): document to separate into main and supplemental information
      dirNameProject (str): name of the project directory
    """
    path =  f"{doc['-branch'][0]['path']}/" if doc['-type'][0][0]=='x' else doc['-branch'][0]['path']
    docMain:dict[str,Any] = {}
    docSupp:dict[str,Any] = {}
    filesNotInData = None
    if path is None:
      path = dirNameProject+'/'+doc['_id']
    elif not path.startswith(dirNameProject) and not path.startswith('http'):
      filesNotInData = path  # files elsewhere, standardOperatingProcedures
    if not path.startswith('http'):
      docMain['@id'] = f'./{dirNameGlobal}/{path}'
    else:
      docMain['@id'] = path
    for key, value in doc.items():
      if key in pasta2json and pasta2json[key] is not None:
        docMain[pasta2json[key]] = value
      else:
        docSupp[key] = value
    # clean individual entries of docSupp: remove personal data
    for k in ['-user', '-client', 'image', '_attachments']:
      if 'image' in docSupp:
        del docSupp[k]
    # clean individual entries of docMain
    if 'keywords' in docMain:
      docMain['keywords'] = ','.join(docMain['keywords'])
    if docMain['genre'][0] == '-' or docMain['genre'][0][0]=='x':
      del docMain['genre']
    else:
      docMain['genre'] = '/'.join(docMain['genre'])
    docMain = {k:v for k,v in docMain.items() if v}
    # move docSupp into docMain
    variableMeasured = []
    for kObject, v in flatten(docSupp).items():
      name = ' \u2192 '.join([i.replace('_','').replace('-','').capitalize() for i in str(kObject).split('.')])
      name = pastaNameTranslation[name] if name in pastaNameTranslation else name
      variableMeasured.append({'value':v, 'propertyID':kObject, 'name':name})
    docMain['variableMeasured'] = variableMeasured
    return path, docMain, filesNotInData

  def appendDocToGraph(graph: list[dict[str,Any]], doc: dict[str,Any]) -> None:
    """
    Append a document / dictionary to a graph

    Args:
      graph (list): graph to be appended to
      doc   (dict): document to append to graph
    """
    idsInGraph = [i['@id'] for i in graph]
    if doc['@id'] not in idsInGraph:
      graph.append(doc)
    return


  def iterateTree(nodeHier:Node, graph:list[dict[str,Any]], dirNameProject:str) -> tuple[Optional[str], list[str]]:
    """
    Recursive function to translate the hierarchical node into a tree-node

    Args:
      nodeHier (Anytree.Node): anytree node
      graph    (list): list of nodes
      dirNameProject (str): name of the project

    Returns:
      str: tree node
    """
    # separate into main and supplemental information
    doc = backend.db.getDoc(nodeHier.id)
    path, docMain, filesNotInBranch = separate(doc, dirNameProject)
    filesNotInProject:list[str] = [] if filesNotInBranch is None else [filesNotInBranch]
    hasPart = []
    if (nodeHier.docType[0] not in dTypes) and nodeHier.docType[0][0]!='x':
      return (None, [])
    for child in nodeHier.children:
      res, filesNotInSubbranch = iterateTree(child, graph, dirNameProject)
      filesNotInProject += filesNotInSubbranch
      if res is not None:
        hasPart.append( res )
    if nodeHier.id[0]=='x':
      parts = []
      if hasPart:
        parts += [{'@id':i} for i in hasPart]
      if parts:
        docMain['hasPart'] = parts
    fullPath = backend.basePath/path
    if path is not None and fullPath.exists() and fullPath.is_file():
      with open(fullPath, 'rb') as fIn:
        fileContent = fIn.read()
        docMain['contentSize'] = str(len(fileContent))
        docMain['sha256']      = hashlib.sha256(fileContent).hexdigest()
      docMain['@type'] = 'File'
    elif path.startswith('http'):
      response = requests.get(path.replace(':/','://'), timeout=10)
      if response.ok:
        docMain['contentSize'] = str(response.headers['content-length'])
        docMain['sha256']      = hashlib.sha256(response.content).hexdigest()
      else:
        print(f'Info: could not get file {path}')
      docMain['@type'] = 'File'
    elif '@type' not in docMain:  #samples will be here
      docMain['@type'] = 'Dataset'
      docMain['@id'] = docMain['@id'] if docMain['@id'].endswith('/') else f"{docMain['@id']}/"
    appendDocToGraph(graph, docMain)
    return docMain['@id'], filesNotInProject


  # define initial information
  fileName = fileName if fileName.endswith('.eln') else f'{fileName}.eln'
  filesNotInProject:list[str] = []
  dirNameGlobal = fileName.split('/')[-1][:-4]
  # == MAIN FUNCTION ==
  logging.info('Create eln file %s',fileName)
  with ZipFile(fileName, 'w', compression=ZIP_DEFLATED) as elnFile:
    graph: list[dict[str,Any]] = []
    dirNameProjects = []
    for projectID in projectIDs:       #for each project
      docProject = backend.db.getDoc(projectID)
      dirNameProject = docProject['-branch'][0]['path']
      dirNameProjects.append(dirNameProject)


      # ------- Create main graph -------------------
      listHier = backend.db.getHierarchy(projectID, allItems=False)
      _, filesNotInProject = iterateTree(listHier, graph, dirNameProject)  # create json object from anytree

      # ------------------ copy data-files --------------------------
      # datafiles are already in the graph-graph: only copy and no addition to graph
      for path, _, files in os.walk(backend.basePath/dirNameProject):
        if '/.git' in path:  #if use datalad
          continue
        relPath = os.path.relpath(path, backend.basePath) #path of the folder
        for iFile in files:                         #iterate through all files in folder
          if iFile.startswith('.git') or iFile=='.id_pastaELN.json':
            continue
          elnFile.write(f'{path}/{iFile}', f'{dirNameGlobal}/{relPath}/{iFile}')
      for path in set(filesNotInProject):  #set ensures that only added once
        elnFile.write(str(backend.basePath/path), f'{dirNameGlobal}/{path}')

    # FOR ALL PROJECTS
    # ------------------- create ro-crate-metadata.json header -----------------------
    index:dict[str,Any] = {}
    index['@context']= 'https://w3id.org/ro/crate/1.1/context'
    # master node ro-crate-metadata.json
    graphMaster:list[dict[str,Any]] = []
    graphMisc:list[dict[str,Any]] = []
    masterNodeInfo = {'@id': 'ro-crate-metadata.json', '@type': 'CreativeWork', 'about': {'@id': './'},
        'conformsTo': {'@id': 'https://w3id.org/ro/crate/1.1'}, 'schemaVersion': 'v1.0', 'version': '1.0',
        'datePublished':datetime.now().isoformat(), 'dateCreated': datetime.now().isoformat(),
        'sdPublisher': {'@type': 'Organization', 'name': 'PASTA ELN',
            'logo': 'https://raw.githubusercontent.com/PASTA-ELN/desktop/main/pasta.png',
            'slogan': 'The favorite ELN for experimental scientists',
            'url': 'https://github.com/PASTA-ELN/', 'description': f'Version {__version__}'}}
    graphMaster.append(masterNodeInfo)
    zipContent = json.dumps(backend.db.getDoc('-dataHierarchy-'))
    dataHierarchyInfo = {'@id':  f'./{dirNameGlobal}/data_hierarchy.json', '@type': 'File',
        'name':  'data structure', 'description': 'data structure / schema of the stored data',
        'contentSize':str(len(zipContent)), 'sha256':hashlib.sha256(zipContent.encode()).hexdigest(),
        'datePublished': datetime.now().isoformat()}
    graphMisc.append(dataHierarchyInfo)
    elnFile.writestr(f'{dirNameGlobal}/data_hierarchy.json', zipContent)
    authors = backend.configuration['authors']
    masterParts = [{'@id': f'./{dirNameGlobal}/{i}/'} for i in dirNameProjects] + [{'@id': f'./{dirNameGlobal}/data_hierarchy.json'}]
    masterNodeRoot = {'@id': './', '@type': 'Dataset', 'hasPart': masterParts,
        'name': 'Exported from PASTA ELN', 'description': 'Exported content from PASTA ELN',
        'license':'CC BY 4.0', 'datePublished':datetime.now().isoformat(),
        'author': [{'firstName': authors[0]['first'], 'surname': authors[0]['last'],
            'title': authors[0]['title'], 'emailAddress': authors[0]['email'],
            'ORCID': authors[0]['orcid'],
            'affiliation': [{'organization': authors[0]['organizations'][0]['organization'],
                'RORID': authors[0]['organizations'][0]['rorid']}]
        }]}
    graphMaster.append(masterNodeRoot)

    #finalize file
    index['@graph'] = graphMaster+graph+graphMisc
    elnFile.writestr(f'{dirNameGlobal}/ro-crate-metadata.json', json.dumps(index))
    # if verbose:
    #   print(json.dumps(index, indent=3))

    #sign file
    if 'signingKeyPair' not in backend.configuration:  #create a key-pair of secret and public key and save it locally
      keyPairRaw = minisign.KeyPair.generate()
      keyPair    = {'id':str(uuid.uuid4()), 'secret':bytes(keyPairRaw.secret_key).decode(), 'public':bytes(keyPairRaw.public_key).decode()}
      backend.configuration['signingKeyPair'] = keyPair
      with open(Path.home()/'.pastaELN.json', 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(backend.configuration,indent=2))
    keyPair = backend.configuration['signingKeyPair']
    secretKey = minisign.SecretKey.from_bytes(keyPair['secret'].encode())
    comment   = {'pubkey_url':f'https://raw.githubusercontent.com/PASTA-ELN/Signatures/main/{keyPair["id"]}.pub',
                 'name': f"{backend.configuration['authors'][0]['title']} {backend.configuration['authors'][0]['first']} {backend.configuration['authors'][0]['last']}",
                 'email': backend.configuration['authors'][0]['email'],
                 'orcid': backend.configuration['authors'][0]['orcid']}
    signature = secretKey.sign(json.dumps(index).encode(), trusted_comment=json.dumps(comment))
    elnFile.writestr(f'{dirNameGlobal}/ro-crate-metadata.json.minisig', bytes(signature).decode())
    elnFile.writestr(f'{dirNameGlobal}/ro-crate.pubkey', keyPair['public'])
  # end writing zip file

  # temporary json output
  if verbose:
    with open(fileName[:-3]+'json','w', encoding='utf-8') as fOut:
      fOut.write( json.dumps(index, indent=2) )
  return f'Success: exported {len(graph)} graph-nodes into file {fileName}'


def testSignature(fileName:str) -> bool:
  """ Test if signature is valid

  Args:
    fileName (str): file name to test against

  Returns:
    bool: success / failure of test
  """
  print(f'Test signature of : {fileName}')
  with ZipFile(fileName, 'r', compression=ZIP_DEFLATED) as elnFile:
    metadataJsonFile = [i for i in elnFile.namelist() if i.endswith(METADATA_FILE)][0]
    with elnFile.open(metadataJsonFile) as fIn:
      metadataData = fIn.read()
    dirName          = metadataJsonFile.split('/')[0]
    signatureFile    = f'{dirName}/{METADATA_FILE}.minisig'
    with elnFile.open(signatureFile) as fIn:
      signature = minisign.Signature.from_bytes(fIn.read())
    publicKeyFile    = f'{dirName}/ro-crate.pubkey'
    with elnFile.open(publicKeyFile) as fIn:
      publicKey = minisign.PublicKey.from_bytes(fIn.read())
    try:
      publicKey.verify(metadataData, signature)
      if 'pubkey_url' in signature.trusted_comment:
        path = json.loads(signature.trusted_comment)['pubkey_url']
        response = requests.get(path, timeout=10)
        if response.ok:
          pubKeyRemote = response.content.strip()
          if pubKeyRemote.decode() == str(bytes(publicKey))[2:-1]:
            print('Success: remote and local key match')
          else:
            print('**ERROR remote and local key differ')
            raise minisign.VerifyError
      print('Signature is acceptable:\n', json.dumps(json.loads(signature.trusted_comment), indent=2))
      return True
    except minisign.VerifyError:
      print('**ERROR VERIFICATION ERROR')
    return False
