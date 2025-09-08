"""Input and output functions towards the .eln file-format"""
import copy
import hashlib
import json
import logging
import shutil
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
import requests
from anytree import Node
from pasta_eln import __version__, minisign
from ..fixedStringsJson import CONF_FILE_NAME
from ..miscTools import flatten
from ..textTools.html2markdown import html2markdown
from ..textTools.stringChanges import camelCase
from .backend import Backend

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

METADATA_FILE = 'ro-crate-metadata.json'


##########################################
###               IMPORT               ###
##########################################

def importELN(backend:Backend, elnFileName:str, projID:str) -> tuple[str,dict[str,Any]]:
  '''
  import .eln file from other ELN or from PASTA

  Args:
    backend (backend): backend
    elnFileName (str): name of file
    projID (str): project to import data into

  Returns:
    str: success message, statistics
  '''
  elnName = ''
  statistics:dict[str,Any] = {}
  with ZipFile(elnFileName, 'r', compression=ZIP_DEFLATED) as elnFile:
    files = elnFile.namelist()
    dirName=Path(files[0]).parts[0]
    statistics['num. files'] = len([i for i in files if Path(i).parent!=Path(dirName)])
    if f'{dirName}/ro-crate-metadata.json' not in files:
      logging.error('ro-crate does not exist in folder. EXIT', exc_info=True)
      return 'ERROR: ro-crate does not exist in folder. EXIT',{}
    graph = json.loads(elnFile.read(f'{dirName}/ro-crate-metadata.json'))['@graph']
    listAllTypes = [i['@type'] for i in graph if isinstance(i['@type'],str)]
    statistics['types'] = {i:listAllTypes.count(i) for i in listAllTypes}

    #find information from master node
    rocrateNode = [i for i in graph if i['@id'].endswith('ro-crate-metadata.json')][0]
    if 'sdPublisher' in rocrateNode:
      publisherNode = rocrateNode['sdPublisher']
      if 'name' not in publisherNode:
        publisherNode = [i for i in graph if i['@id']==rocrateNode['sdPublisher']['@id']][0]
      elnName = publisherNode['name']
    logging.info('Import %s', elnName)
    if not projID:
      return 'FAILURE: YOU CANNOT IMPORT AS PROJECT IF NON PASTA-ELN FILE',{}
    backend.changeHierarchy(projID)
    childrenStack = [0]
    mainNode    = [i for i in graph if i['@id']=='./'][0]
    # clean subchildren from mainNode: see https://github.com/TheELNConsortium/TheELNFileFormat/issues/98
    parentNodes = {i['@id'] for i in mainNode['hasPart']}
    for nodeAny in graph:
      if nodeAny['@id']=='./':
        continue
      children = {i['@id'] for i in nodeAny.get('hasPart',[])}
      parentNodes = parentNodes.difference(children)
    mainNode['hasPart'] = [{'@id':i} for i in parentNodes]

    ################
    # subfunctions #
    ################
    def json2pastaFunction(inputData:dict[str,Any]) -> tuple[dict[str,Any], str, list[Any], str]:
      """
      convert json data to pastaStyle
        - clean all the @id, @type

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
        if key in json2pasta:                                                           #use known translation
          doc[json2pasta[key]] = value
        elif key == 'encodingFormat':
          encodingFormat = inputData[key]
        elif value:                                                 #keep name, only prevent causes for errors
          doc[f'.{key}'] = value
      # change into Pasta's native format
      if isinstance(doc.get('comment',''), (dict,list)):
        if isinstance(doc['comment'], dict):
          doc['comment'] = [doc['comment']]
        doc['comment'] = '\n\n'.join([i['text'] for i in doc['comment']])
      if '.comment' in doc:
        doc['comment'] = doc.get('comment','') + \
                         '\n\n'.join(['']+[f'{i["dateCreated"]}:\n{i["text"]}' for i in doc.pop('.comment')])
      if encodingFormat=='text/html':
        if 'comment' in doc:
          doc['comment'] = html2markdown(doc['comment'])
        if 'content' in doc:
          doc['content'] = html2markdown(doc['content'])
      if 'tags' in doc:
        doc['tags'] = [i.strip() for i in doc['tags'].split(',')]
      else:
        doc['tags'] = []
      if 'id' in doc:
        doc['.oldIdentifier'] = doc.pop('id')
      doc['.elnIdentifier'] = elnID
      if (children and ('type' not in doc or doc['type']!='x1')):
        doc['type'] = 'x1'
      if 'type' not in doc:
        doc['type'] = ''
      if doc['type']=='folder':
        doc['type'] = 'x1'
      # change .variable measured into pastaSystem
      variableMeasured = doc.pop('.variableMeasured',[])
      if variableMeasured is not None:
        for data in variableMeasured:
          propertyID = data['propertyID'] if '.' in data['propertyID'] and ' ' not in data['propertyID'] else f"imported.{camelCase(data['propertyID'])}"
          # print('propertyID', propertyID, elnName)
          doc[propertyID] = (data['value'], data.get('unitText',''), data.get('description',''), data.get('mentions',''))
      # final cleaning
      for key, value in doc.items():
        if isinstance(value, list) and len(value)>0 and isinstance(value[0], dict):
          newValue = []
          for item in copy.deepcopy(value):
            del item['@id']
            del item['@type']
            newValue.append(item)
          if len(newValue)==1:
            newValue = newValue[0]
          doc[key] = newValue
        elif isinstance(value, dict):
          for keyI in list(value.keys()):
            if keyI.startswith('@'):
              newKey = keyI[1:]
              newKey = 'imported_'+newKey if newKey in ['id','type','branch'] else newKey
              value[newKey] = value.pop(keyI)
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
      if not isinstance(part, dict):              #leave these tests in since other .elns might do funky stuff
        logging.error('in part %s', part, exc_info=True)
        return 0
      # print('\nProcess: '+part['@id'])
      # find next node to process
      docS = [i for i in graph if '@id' in i and i['@id']==part['@id']]
      if len(docS)!=1 or backend.cwd is None:
        logging.error('zero or multiple nodes with same id %s or cwd is None in %s', docS, part['@id'], exc_info=True)
        return -1
      # pull all subentries (variableMeasured, comments, ...) into this dict: do not pull hasPart-entries in
      keys = [k for k,v in docS[0].items() if k!='hasPart' and (isinstance(v,dict) or (isinstance(v,list) and len(v)>0 and isinstance(v[0], dict)))]
      for key in keys:
        value = docS[0].get(key, [])
        if isinstance(value, list):
          items = [i['@id'] for i in value]
        else:
          items = [value['@id']]
        # print(f'Replace {key} -entries using ids: {items}')
        try:
          docS[0][key] = [ [j for j in graph if j['@id']==i][0] for i in items]
        except Exception:
          # Causes for exception
          # - @id is a link to external IRI (http...). Hence it is not in the file
          # - the graph is not fully flattend: @id is in a leaf of a node but not a separate note
          docS[0][key] = value
          logging.warning('Could not replace %s-entries using ids: %s', key, items)
      # convert to Pasta's style
      doc, elnID, children, dataType = json2pastaFunction(docS[0])
      if elnName == 'PASTA ELN' and elnID.startswith('http') and ':/' in elnID:
        fullPath = None
      else:
        fullPath = backend.basePath/backend.cwd/elnID.split('/')[-1]
      if fullPath is not None and f'{dirName}/{elnID}' in elnFile.namelist():        #Copy file onto hard disk
        target = open(fullPath, 'wb')
        source = elnFile.open(f'{dirName}/{elnID}')
        with source, target:                                          #extract one file to its target directly
          shutil.copyfileobj(source, target)
      # FOR ALL ELNs
      if elnName == 'PASTA ELN':
        docType = doc['type']
      else:
        if dataType.lower()=='dataset':
          docType = 'x0' if not projID and len(elnID.split('/'))==0 else 'x1'
        else:
          docType = ''
      if docType=='x0':
        backend.hierStack = []
      childrenStack[-1] += 1
      doc['childNum'] = childrenStack[-1]
      qrCodes = [v[0] for k,v in doc.items() if 'qrCodes.' in k]
      doc = {k:v for k,v in doc.items() if 'qrCodes.' not in k}
      doc['qrCodes'] = qrCodes
      # print(f'Want to add doc:{doc} with type:{docType} and cwd:{backend.cwd}')
      try:
        docID = backend.addData(docType, doc)['id']
      except Exception:
        logging.error('Cannot process %s', json.dumps(doc,indent=2), exc_info=True)
        docID = None
      if docID[0]=='x':
        backend.changeHierarchy(docID)
        childrenStack.append(0)
        with open(backend.basePath/backend.cwd/'.id_pastaELN.json','w', encoding='utf-8') as f:#local path, update in any case
          f.write(json.dumps(backend.db.getDoc(docID)))
        # children, aka recursive part
        for child in children:
          if child['@id'].endswith('/metadata.json') or child['@id'].endswith('_metadata.json'):#skip own metadata
            continue
          try:
            addedDocs += processPart(child)
          except Exception:
            logging.error('Cannot process child %s', json.dumps(child,indent=2), exc_info=True)
        backend.changeHierarchy(None)
        childrenStack.pop()
      return addedDocs

    ######################
    #main function
    #iteratively go through list
    addedDocuments = 0
    for part in mainNode['hasPart']:
      try:
        addedDocuments += processPart(part)
      except Exception:
        logging.error('Cannot process main part %s', json.dumps(part,indent=2), exc_info=True)
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

    def mkDirectory(path:str) -> None:
      """ create directory in zip file

      Args:
        path (str): path to create
      """
      if sys.version_info >= (3, 10):
        elnFile.mkdir(path)
      else:
        dirInfo = ZipInfo(path if path.endswith('/') else f'{path}/')
        dirInfo.date_time = time.localtime(time.time())[:6]
        dirInfo.external_attr = 0o40775 << 16                                                     # drwxrwxr-x
        elnFile.writestr(dirInfo, '')

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
      docELN:dict[str,Any] = {'encodingFormat': 'text/markdown'}
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
      if path.startswith('http'):
        docELN['@id'] = path
        docELN['url'] = path
      else:
        docELN['@id'] = f'./{path}'
      # include content size, etc
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
        mkDirectory(docELN['@id'][:-1])
        docELN['@type'] = 'Dataset'
      elif path.startswith('http'):
        response = requests.get(path, timeout=10)
        if response.ok:
          docELN['contentSize'] = str(response.headers['content-length'])
          docELN['sha256']      = hashlib.sha256(response.content).hexdigest()
        else:
          print(f"Info: could not get file {path}")
        docELN['@type'] = 'File'
      elif '@type' not in docELN:                                                        #samples will be here
        docELN['@type'] = 'Dataset'
        docELN['@id'] = docELN['@id'] if docELN['@id'].endswith('/') else f"{docELN['@id']}/"
        mkDirectory(docELN['@id'][:-1])
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

    # for each project, append to graph
    masterParts = []
    for projectID in projectIDs:
      docProject = backend.db.getDoc(projectID)
      dirNameProject = docProject['branch'][0]['path']
      listHier, _ = backend.db.getHierarchy(projectID, allItems=False)#error not handled since should not occur during export
      processNode(listHier)
      masterParts.append(f'./{dirNameProject}/')

    # all items have to appear in hasPart of ./ -> masterParts are changed
    # https://github.com/TheELNConsortium/TheELNFileFormat/issues/98
    somethingChanged = True                                                                #starting condition
    nodesProcessed = set()
    while somethingChanged:
      somethingChanged = False
      for node in copy.deepcopy(masterParts):
        if node in nodesProcessed:
          continue
        nodesProcessed.add(node)
        possNodes = [i for i in graph if i['@id']==node]
        if len(possNodes)==1:
          idx = masterParts.index(node)
          variables:list[str] = []
          # variables = [i['@id'] for i in possNodes[0].get('variableMeasured',[])] #variables go not into ./
          children            = [i['@id'] for i in possNodes[0].get('hasPart',[])]
          masterParts = masterParts[:idx+1] + variables + children + masterParts[idx+1:]
          if variables or children:
            somethingChanged = True

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
    masterNodeRoot:dict[str,Any] = {'@id': './', '@type': 'Dataset', 'hasPart': [{'@id':i} for i in masterParts],
        'name': 'Exported from PASTA ELN', 'description': 'Exported content from PASTA ELN',
        'license':'https://creativecommons.org/licenses/by-nc-sa/4.0/', 'datePublished':datetime.now().isoformat()}
    if authorNodes:
      masterNodeRoot = masterNodeRoot | {'creator': authorNodes}
    graphMaster.append(masterNodeRoot)

    #finalize file
    index['@graph'] = graphMaster+graph+graphMisc
    elnFile.writestr(f'{dirNameGlobal}/ro-crate-metadata.json', json.dumps(index, indent=2))

    #sign file
    if 'signingKeyPair' not in backend.configuration or not backend.configuration['signingKeyPair']:
      #create a key-pair of secret and public key and save it locally
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
            logging.info('Success: remote and local key match')
          else:
            logging.error('remote and local key differ', exc_info=True)
            raise minisign.VerifyError
      print('Signature is acceptable:\n', json.dumps(json.loads(signature.trusted_comment), indent=2))
      return True
    except minisign.VerifyError:
      logging.error('VERIFICATION', exc_info=True)
    return False
