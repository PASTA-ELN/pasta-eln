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
from .miscTools import flatten
from .fixedStringsJson import CONF_FILE_NAME
# .eln file: common between all ELNs
# - can be exported / imported generally; not a 1:1 backup (just zip it)
# - should be able to recreate the exported -> imported data (using the common addDoc)
# - externalID is the only content that cannot be recreated
#   - not sure how important this information is: different groups have different externalIDs
#   - if every it becomes important: just add json (that maps identifier to externalID) as additional file

# GENERAL TERMS IN ro-crate-metadata.json (None: this entry is not saved and will be recreated upon import)
pasta2json:dict[str,Any] = {
  'id'          : 'identifier',
  'branch'      : None,
  'client'      : None,
  'dateModified': 'dateModified',
  'dateCreated' : 'dateCreated',
  'name'        : 'name',
  'tags'        : 'keywords',
  'type'        : 'genre',
  'image'       : None,
  'comment'     : 'description',
  'content'     : 'text',
  'links'       : 'mentions',
  'shasum'      : None,
  'user'        : None,
  'externalId'  : None,
  'gui'         : None
}
json2pasta:dict[str,Any] = {v:k for k,v in pasta2json.items() if v is not None}

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
    logging.info('All files %s',', '.join(files))
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
      if 'tags' not in doc:
        doc['tags'] = []
      else:
        doc['tags'] = [i.strip() for i in doc['tags'].split(',')]
      # PASTA_ELN
      if elnName == 'PASTA ELN':
        doc['user'] = '_'
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
            projID = backend.addData('x0', {'-name':f'Imported project of {renameELN.get(elnName, elnName)} '})['id']
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
        if 'id' in doc:
          doc['externalID'] = doc.pop('id')
        print(f'Want to add doc:{doc} with type:{docType} and cwd:{backend.cwd}')
        docID = backend.addData(docType, doc)['id']
        if docID[0]=='x':
          backend.hierStack += [docID]
          backend.cwd        = backend.basePath/ backend.db.getDoc(docID)['branch'][0]['path']

      # children, aka recursive part
      logging.info('subparts: %s',', '.join(['  '+i['@id'] for i in children]))
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
  # Initialize variables
  fileName = fileName if fileName.endswith('.eln') else f'{fileName}.eln'
  logging.info('Create eln file %s',fileName)
  dirNameGlobal = fileName.split('/')[-1][:-4]
  with ZipFile(fileName, 'w', compression=ZIP_DEFLATED) as elnFile:
    graph: list[dict[str,Any]] = []
    dirNameProjects = []

    def processNode(node:Node) -> str:
      """
      Recursive function to translate the hierarchical node into a tree-node

      Args:
        node (Anytree.Node): anytree node with properties
            name (incl. that of parents), childNum, docType, gui, id

      Returns:
        str: tree node id
      """
      # create node properties
      docDB = backend.db.getDoc(node.id)
      docELN= {"encodingFormat": "text/markdown",}
      docSupp = {}
      for key, value in docDB.items():
        if key in pasta2json:
          if pasta2json[key] is not None:
            docELN[pasta2json[key]] = value
        else:
          docSupp[key] = value
      # clean individual entries of docELN
      if 'keywords' in docELN:
        docELN['keywords'] = ','.join(docELN['keywords'])
      if docELN['genre'][0] == '-':
        del docELN['genre']
      elif docELN['genre'][0][0]=='x':
        docELN['genre'] = 'folder'
      else:
        docELN['genre'] = '/'.join(docELN['genre'])
      docELN = {k:v for k,v in docELN.items() if v}
      # move docSupp into docELN
      variableMeasured = []
      for kObject, v in flatten(docSupp).items():
        name = ' \u2192 '.join([i.replace('_','').replace('-','').capitalize() for i in str(kObject).split('.')])
        varMeasured = {'value':v, 'propertyID':kObject, 'name':name, '@type': 'PropertyValue'}
        if isinstance(v, tuple):
          varMeasured['value'] = v[0]
          if v[1]:
            varMeasured['unitText'] = v[1]
          if v[2]:
            varMeasured['description'] = v[2]
          if v[3]:
            varMeasured['mentions'] = v[3]
        variableMeasured.append(varMeasured)
      docELN['variableMeasured'] = variableMeasured
      # include children, hasPart
      hasPart = []
      if (node.docType[0] not in dTypes) and node.docType[0][0]!='x':
        return ''
      for child in node.children:
        res = processNode(child)
        if res:
          hasPart.append(res)
      if node.docType[0][0]=='x' and hasPart:
        docELN['hasPart'] = [{'@id':i} for i in hasPart]
      # include path and @id
      if docDB['type'][0] == 'x0':
        branch   = docDB['branch'][0]
      else:
        branch   = [i for i in docDB['branch'] if node.parent.id in i['stack']][0]
      path =  f"{branch['path']}/" if docDB['type'][0][0]=='x' else branch['path']
      if path is None:
        path = f"{dirNameProject}/{docDB['id']}"
      if not path.startswith('http'):
        docELN['@id'] = f'./{dirNameGlobal}/{path}'
      else:
        docELN['@id'] = path
      # include content size, etc.
      fullPath = backend.basePath/path
      if path is not None and fullPath.exists() and fullPath.is_file():
        with open(fullPath, 'rb') as fIn:
          fileContent = fIn.read()
          docELN['contentSize'] = str(len(fileContent))
          docELN['sha256']      = hashlib.sha256(fileContent).hexdigest()
        # copy data-files
        elnFile.write(str(fullPath), f'{dirNameGlobal}/{path}')
        docELN['@type'] = 'File'
      elif path is not None and fullPath.exists() and fullPath.is_dir():
        elnFile.mkdir(f'{dirNameGlobal}/{path}')
        docELN['@type'] = 'Dataset'
      elif path.startswith('http'):
        response = requests.get(path.replace(':/','://'), timeout=10)
        if response.ok:
          docELN['contentSize'] = str(response.headers['content-length'])
          docELN['sha256']      = hashlib.sha256(response.content).hexdigest()
        else:
          print(f"Info: could not get file {path.replace(':/','://')}")
        docELN['@type'] = 'File'
      elif '@type' not in docELN:  #samples will be here
        docELN['@type'] = 'Dataset'
        docELN['@id'] = docELN['@id'] if docELN['@id'].endswith('/') else f"{docELN['@id']}/"
        elnFile.mkdir(docELN['@id'][:-1])
      graph.append(docELN)
      return docELN['@id']

    #for each project, append to graph
    for projectID in projectIDs:
      docProject = backend.db.getDoc(projectID)
      dirNameProject = docProject['branch'][0]['path']
      dirNameProjects.append(dirNameProject)
      listHier = backend.db.getHierarchy(projectID, allItems=False)
      processNode(listHier)

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
        'sdPublisher': {'@id': 'PASTA-ELN'}}
    graphMaster.append(masterNodeInfo)
    masterNodeInfo2 = {'@id':'PASTA-ELN','@type': 'Organization', 'name': 'PASTA ELN',
            'logo': 'https://raw.githubusercontent.com/PASTA-ELN/desktop/main/pasta.png',
            'slogan': 'The favorite ELN for experimental scientists',
            'url': 'https://github.com/PASTA-ELN/', 'description': f'Version {__version__}'
    }
    graphMaster.append(masterNodeInfo2)
    masterParts = [{'@id': f'./{dirNameGlobal}/{i}/'} for i in dirNameProjects]
    authorNodes = []
    for author in backend.configuration['authors']:
      # first do affiliations, then use them
      affiliationNodes = []
      for affiliation in author['organizations']:
        affiliationId    = f'affiliation_{affiliation['organization']}'
        if affiliationId not in graphMaster:
          graphMaster.append({'@id':affiliationId, '@type':'organization', 'name':affiliation['organization'], 'RODID':affiliation['rorid']})
          affiliationNodes.append({'@id':affiliationId})
      authorID = f'author_{author['first']}_{author['last']}'
      graphMaster.append({'@id':authorID, '@type':'author', 'firstName': author['first'], 'surname': author['last'],
                          'title': author['title'], 'emailAddress': author['email'], 'identifier': f"https://orcid.org/{author['orcid']}",
                          'affiliation': affiliationNodes})
      authorNodes.append({'@id':authorID})
    masterNodeRoot = {'@id': './', '@type': 'Dataset', 'hasPart': masterParts,
        'name': 'Exported from PASTA ELN', 'description': 'Exported content from PASTA ELN',
        'license':'CC BY 4.0', 'datePublished':datetime.now().isoformat(),
        'author': authorNodes}
    graphMaster.append(masterNodeRoot)

    #finalize file
    index['@graph'] = graphMaster+graph+graphMisc
    elnFile.writestr(f'{dirNameGlobal}/ro-crate-metadata.json', json.dumps(index, indent=2))

    #sign file
    if 'signingKeyPair' not in backend.configuration:  #create a key-pair of secret and public key and save it locally
      keyPairRaw = minisign.KeyPair.generate()
      keyPair    = {'id':str(uuid.uuid4()), 'secret':bytes(keyPairRaw.secret_key).decode(), 'public':bytes(keyPairRaw.public_key).decode()}
      backend.configuration['signingKeyPair'] = keyPair
      with open(Path.home()/CONF_FILE_NAME, 'w', encoding='utf-8') as fConf:
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
    with open(f'{fileName[:-3]}json', 'w', encoding='utf-8') as fOut:
      fOut.write( json.dumps(index, indent=2) )
  return f'Success: exported {len(graph)} graph-nodes into file {fileName}'


def validateSignature(fileName:str) -> bool:
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
