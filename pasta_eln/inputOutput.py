"""Input and output functions towards the .eln file-format"""
import json, shutil, logging, hashlib, uuid
from typing import Any
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
import requests
from anytree import Node
from PySide6.QtGui import QTextDocument
from pasta_eln import __version__, minisign
from .backend import Backend
from .miscTools import flatten
from .fixedStringsJson import CONF_FILE_NAME
from .stringChanges import camelCase

# .eln file: common between all ELNs
# - can be exported / imported generally; not a 1:1 backup (just zip it)
# - should be able to recreate the exported -> imported data (using the common addDoc)
# - externalID is the only content that cannot be recreated
#   - not sure how important this information is: different groups have different externalIDs
#   - if every it becomes important: just add json (that maps identifier to externalID) as additional file

# Idea: ELN from other vendor -> import -> export: should be the same
# - not because some information is added (pasta's identifier)
# - some information is changed (what I understand as measurement is not the same as elab's experiment which is more a folder in pasta
# - some information is deleted (data privacy related)

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
  '.links'      : 'mentions',
  'shasum'      : None,
  'user'        : None,
  'externalId'  : None,
  'gui'         : None,
  'dateSync'    : None
}
json2pasta:dict[str,Any] = {v:k for k,v in pasta2json.items() if v is not None}

# # Special terms in other ELNs: only add the ones that are required for function for PASTA
# specialTerms:dict[str,dict[str,str]] = {
#     'elabFTW': {
#       # 'elabid':'_id',
#       # 'title':'-name',
#       # 'tags':'-tags',
#       # 'lastchange':'-date',
#       # 'userid':'-user',
#       # 'metadata':'metaUser',
#       # 'id':'_id',
#       # 'category': '-type',
#       # 'dateCreated': '-date'
#     },
#     'SampleDB':{
#       'comment':'userComment',
#       'genre': '-type'
#     }
# }


METADATA_FILE = 'ro-crate-metadata.json'


# def tree(graph:dict[Any,Any]) -> str:
#   """
#   use metadata to create hierarchical tree structure in ascii

#   Args:
#     graph (dict): tree-graph to be plotted

#   Returns:
#     str: output of graph as a nice tree
#   """
#   def process_part(part:dict[Any,Any], level:int) -> str:
#     """
#     recursive function call to process this node of the tree-graph

#     Args:
#       part (dict): dictionary entry of this hasPart=part of a parent node; is a node by-itself
#       level (int): hierarchy level

#     Returns:
#       str: one line in the tree
#     """
#     prefix = '    '*level + '- '
#     # find next node to process
#     newNode:list[Any] = [i for i in graph if '@id' in i and i['@id'] == part['@id']]
#     if len(newNode) == 1:
#       output = f'{prefix} {newNode[0]["@id"]} type:{newNode[0]["@type"]} items: {len(newNode[0])-1}\n'  # -1 because @id is not counted
#       subparts = newNode[0].pop('hasPart') if 'hasPart' in newNode[0] else []
#       if len(subparts) > 0:  # don't do if no subparts: measurements, ...
#         for subpart in subparts:
#           output += process_part(subpart, level + 1)
#     else:                                                       #not found
#       output = f'  items: {len(part) - 1}\n'      # -1 because @id is not counted
#     return output

#   # main tree-function
#   #   find information from master node
#   ro_crate_node = [i for i in graph if i["@id"] == METADATA_FILE][0]
#   output = f'- {METADATA_FILE}' + '\n'
#   if 'sdPublisher' in ro_crate_node:
#     name = ro_crate_node['sdPublisher'].get('name','---')
#     output += f'    - publisher: {name}' + '\n'
#   if 'version' in ro_crate_node:
#     output += '    - version: ' + ro_crate_node['version'] + '\n'
#   main_node = [i for i in graph if i["@id"] == "./"][0]
#   output += '- ./\n'
#   #   iteratively go through list
#   for part in main_node['hasPart']:
#     output += process_part(part, 1)
#   return output


def importELN(backend:Backend, elnFileName:str, projID:str) -> tuple[str,dict[str,Any]]:
  '''
  import .eln file from other ELN or from PASTA

  Args:
    backend (backend): backend
    elnFileName (str): name of file
    projID (str): project to import data into. If '', create a new project (only available for PastaELN)

  Returns:
    str: success message, statistics
  '''
  elnName = ''
  qtDocument = QTextDocument()   #used for html -> markdown conversion
  statistics:dict[str,Any] = {}
  with ZipFile(elnFileName, 'r', compression=ZIP_DEFLATED) as elnFile:
    files = elnFile.namelist()
    dirName=Path(files[0]).parts[0]
    statistics['num. files'] = len([i for i in files if Path(i).parent!=Path(dirName)])
    if f'{dirName}/ro-crate-metadata.json' not in files:
      print('**ERROR: ro-crate does not exist in folder. EXIT')
      return '**ERROR: ro-crate does not exist in folder. EXIT',{}
    graph = json.loads(elnFile.read(f'{dirName}/ro-crate-metadata.json'))["@graph"]
    listAllTypes = [i['@type'] for i in graph if isinstance(i['@type'],str)]
    statistics['types'] = {i:listAllTypes.count(i) for i in listAllTypes}

    #find information from master node
    rocrateNode = [i for i in graph if i["@id"].endswith("ro-crate-metadata.json")][0]
    if 'sdPublisher' in rocrateNode:
      publisherNode = rocrateNode['sdPublisher']
      if 'name' not in publisherNode:
        publisherNode = [i for i in graph if i["@id"]==rocrateNode['sdPublisher']['@id']][0]
      elnName = publisherNode['name']
    logging.info('Import %s', elnName)
    if not projID and elnName!='PASTA ELN':
      return "FAILURE: YOU CANNOT IMPORT AS PROJECT IF NON PASTA-ELN FILE",{}
    if projID:
      backend.changeHierarchy(projID)
    # if elnName!='PASTA ELN' and elnName in specialTerms:
    #   json2pasta.update(specialTerms[elnName])
    # logging.info('ELN and translator: %s %s', elnName, str(json2pasta))
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
      doc = {}
      elnID = inputData['@id'][2:] if inputData['@id'][:2]=='./' else inputData['@id']
      children = inputData.pop('hasPart') if 'hasPart' in inputData else []
      dataType = inputData['@type']
      encodingFormat = ''
      for key, value in inputData.items():
        if key in ['@id','@type','hasPart','author','contentSize', 'sha256']:
          continue
        if key in json2pasta:  #use known translation
          doc[json2pasta[key]] = value
        elif key == 'encodingFormat':
          encodingFormat = inputData[key]
        else:                  #keep name, only prevent causes for errors
          doc[f'.{key}'] = value
      # change into Pasta's native format
      if encodingFormat=='text/html':
        if 'comment' in doc:
          qtDocument.setHtml(doc['comment'])
          doc['comment'] = qtDocument.toMarkdown()
        if 'content' in doc:
          qtDocument.setHtml(doc['content'])
          doc['content'] = qtDocument.toMarkdown()
      if 'tags' in doc:
        doc['tags'] = [i.strip() for i in doc['tags'].split(',')]
      else:
        doc['tags'] = []
      if elnName!='PASTA ELN' and 'id' in doc:
        doc['.oldIdentifier'] = doc.pop('id')
      doc['.elnIdentifier'] = elnID
      if (children and ('type' not in doc or doc['type'][0]!='x1')):
        doc['type'] = ['x1']
      if 'type' not in doc:
        doc['type'] = ''
      if doc['type']=='folder':
        doc['type'] = ['x1']
      # change .variable measured into pastaSystem
      variableMeasured = doc.pop('.variableMeasured',[])
      if variableMeasured is not None:
        for data in variableMeasured:

          propertyID = data['propertyID'] if '.' in data['propertyID'] and ' ' not in data['propertyID'] else f"imported.{camelCase(data['propertyID'])}"
          # print('propertyID', propertyID, elnName)
          doc[propertyID] = (data['value'], data.get('unitText',''), data.get('description',''), data.get('mentions',''))
      # print(f'Node becomes: {json.dumps(doc, indent=2)}')
      return doc, elnID, children, dataType


    def processPart(part:dict[str,str]) -> int:
      """
      recursive function call to process this node

      Args:
        part (dict): dictionary containing this data content

      Returns:
        int: number of documents added
      """
      addedDocs = 1
      if not isinstance(part, dict): #leave these tests in since other .elns might do funky stuff
        print("**ERROR in part",part)
        return 0
      # print('\nProcess: '+part['@id'])
      # find next node to process
      docS = [i for i in graph if '@id' in i and i['@id']==part['@id']]
      if len(docS)!=1 or backend.cwd is None:
        print('**ERROR zero or multiple nodes with same id', docS,' or cwd is None in '+part['@id'])
        return -1
      doc, elnID, children, dataType = json2pastaFunction(docS[0])
      # TESTED UNTIL HERE
      if elnName == 'PASTA ELN' and elnID.startswith('http') and ':/' in elnID:
        fullPath = None
      else:
        fullPath = backend.basePath/backend.cwd/elnID.split('/')[-1]
      if fullPath is not None and f'{dirName}/{elnID}' in elnFile.namelist():  #Copy file onto hard disk
        target = open(fullPath, "wb")
        source = elnFile.open(f'{dirName}/{elnID}')
        with source, target:  #extract one file to its target directly
          shutil.copyfileobj(source, target)
      # FOR ALL ELNs
      if elnName == "PASTA ELN":
        docType = '/'.join(doc['type'])
      else:
        if dataType.lower()=='dataset':
          docType = 'x0' if not projID and len(elnID.split('/'))==0 else 'x1'
        else:
          docType = ''
      if docType=='x0':
        backend.hierStack = []
      # print(f'Want to add doc:{doc} with type:{docType} and cwd:{backend.cwd}')
      docID = backend.addData(docType, doc)['id']
      if docID[0]=='x':
        backend.changeHierarchy(docID)
        with open(backend.basePath/backend.cwd/'.id_pastaELN.json','w', encoding='utf-8') as f:  #local path, update in any case
          f.write(json.dumps(backend.db.getDoc(docID)))
        # children, aka recursive part
        for child in children:
          if child['@id'].endswith('/metadata.json') or child['@id'].endswith('_metadata.json'):  #skip own metadata
            continue
          addedDocs += processPart(child)
        backend.changeHierarchy(None)
      return addedDocs

    ######################
    #main function
    #iteratively go through list
    addedDocuments = 0
    for part in mainNode['hasPart']:
      addedDocuments += processPart(part)
  #return to home stack and path
  backend.cwd = Path(backend.basePath)
  backend.hierStack = []
  return f'Success: imported {str(addedDocuments)} documents from file {elnFileName} from ELN {elnName}', statistics




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
      docELN:dict[str,Any] = {"encodingFormat": "text/markdown"}
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
      docELN['@id'] = path if path.startswith('http') else f'./{path}'
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
        # elnFile.mkdir(docELN['@id'][:-1]) #NOT REQUIRED for standard and does not work in python 3.10
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
        # elnFile.mkdir(docELN['@id'][:-1]) #NOT REQUIRED for standard and does not work in python 3.10
      # move docSupp into separate nodes
      variableMeasuredIDs = []
      for kObject, v in flatten(docSupp).items():
        name = ' \u2192 '.join([i.replace('_','').replace('-','').capitalize() for i in str(kObject).split('.')])
        varMeasured = {'value':v, 'propertyID':kObject, 'name':name, '@type': 'PropertyValue','@id':f'{docELN["@id"]}_{kObject}'}
        if isinstance(v, tuple):
          varMeasured['value'] = v[0]
          if v[1]:
            varMeasured['unitText'] = v[1]
        if isinstance(v, tuple):
          varMeasured['value'] = v[0]
          if v[1]:
            varMeasured['unitText'] = v[1]
          if v[2]:
            varMeasured['description'] = v[2]
          if v[3]:
            varMeasured['identifier'] = v[3]
        graph.append(varMeasured)
        variableMeasuredIDs.append({'@id':f'{docELN["@id"]}_{kObject}'})
      if variableMeasuredIDs:
        docELN['variableMeasured'] = variableMeasuredIDs
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
        'conformsTo': {'@id': 'https://w3id.org/ro/crate/1.1'}, 'version': '1.0',
        'additionalType': 'https://purl.archive.org/purl/elnconsortium/eln-spec/1.1',
        'datePublished':datetime.now().isoformat(), 'dateCreated': datetime.now().isoformat(),
        'sdPublisher': {'@id': 'PASTA-ELN'}}
    graphMaster.append(masterNodeInfo)
    masterNodeInfo2 = {'@id':'PASTA-ELN','@type': 'Organization', 'name': 'PASTA ELN',
            'logo': 'https://raw.githubusercontent.com/PASTA-ELN/desktop/main/pasta.png',
            'slogan': 'The favorite ELN for experimental scientists',
            'url': 'https://github.com/PASTA-ELN/', 'description': f'Version {__version__}'
    }
    graphMaster.append(masterNodeInfo2)
    masterParts = [{'@id': f'./{i}/'} for i in dirNameProjects]
    authorNodes = []
    for author in backend.configuration['authors']:
      affiliationNodes = []
      for affiliation in author['organizations']:
        affiliationId    = f"affiliation_{affiliation['organization']}"
        if affiliationId not in graphMaster:
          graphMaster.append({'@id':affiliationId, '@type':'organization', 'name':affiliation['organization'], 'RODID':affiliation['rorid']})
          affiliationNodes.append({'@id':affiliationId})
      authorID = f"author_{author['first']}_{author['last']}"
      graphMaster.append({'@id':authorID, '@type':'Person', 'givenName': author['first'], 'familyName': author['last'],
                          'honorificPrefix': author['title'], 'email': author['email'], 'identifier': f"https://orcid.org/{author['orcid']}",
                          'worksFor': affiliationNodes})
      authorNodes.append({'@id':authorID})
    masterNodeRoot:dict[str,Any] = {'@id': './', '@type': 'Dataset', 'hasPart': masterParts,
        'name': 'Exported from PASTA ELN', 'description': 'Exported content from PASTA ELN',
        'license':'CC BY 4.0', 'datePublished':datetime.now().isoformat()}
    if authorNodes:
      masterNodeRoot = masterNodeRoot | {'creator': authorNodes}
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
        json.dump(backend.configuration, fConf, ensure_ascii=False, indent=2)
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
