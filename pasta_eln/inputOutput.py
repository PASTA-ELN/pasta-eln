"""Input and output functions towards the .eln file-format"""
import os, json, shutil, logging, hashlib, copy
from typing import Any, Optional
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
import requests
from anytree import Node
from pasta_eln import __version__
from .backend import Backend
from .miscTools import createDirName, generic_hash

# to discuss
# - where to store additional metadata, not in ro-crate-metadata, separate files for each entry?
# "ro-crate-metadata.json", "sdPublisher": "@id": or name
# how to store different versions?
# how should the folder structure be? kadi4mat, sampleDB:

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
  'image'       : None,
  'comment'     : 'description',
  'content'     : 'text',
  'links'       : 'mentions',
  'shasum'      : None,
}
json2pasta = {v:k for k,v in pasta2json.items() if v is not None}


# Special terms in other ELNs: only add the ones that are required for function for PASTA
specialTerms = {
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

renameELN_names = {
  'https://kadi.iam.kit.edu':'Kadi4Mat'
}

def tree(graph:dict[str,Any]) -> str:
  """
  use metadata to create hierarchical tree struction in ascii

  Args:
    metadata: graph
  """
  METADATA_FILE = 'ro-crate-metadata.json'

  def process_part(part, level):
    """
    recursive function call to process this node
    """
    prefix = '    '*level + '- '
    # find next node to process
    newNode = [i for i in graph if '@id' in i and i['@id'] == part['@id']]
    if len(newNode) == 1:
      output = f'{prefix} {newNode[0]["@id"]} type:{newNode[0]["@type"]} items: {len(newNode[0])-1}\n'  # -1 because @id is not counted
      subparts = newNode[0].pop('hasPart') if 'hasPart' in newNode[0] else []
      if len(subparts) > 0:  # don't do if no subparts: measurements, ...
        for subpart in subparts:
          output += process_part(subpart, level + 1)
    else:                                                       #not found
      output += ('  items: ' + str(len(part) - 1) + '\n')  # -1 because @id is not counted
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
  projID, projPWD= '', ''
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
      json2pasta.update(specialTerms.get(elnName, {}))
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
      logging.info('\nProcess: '+part['@id'])
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
        fullPath = backend.basePath/elnID
      else:
        fullPath = backend.basePath/backend.cwd/elnID.split('/')[-1]
      datasetIsFolder = False
      if dataType.lower()=='dataset':
        #print('  Dataset',elnID,dataType)
        if elnName == 'PASTA ELN':
          supplementalInfo = Path(dirName)/elnID/'metadata.json'
        elif elnName == 'eLabFTW':
          supplementalInfo = Path(dirName)/elnID/'export-elabftw.json'
        else:
          print('**Info: no additional information in', elnName)
          supplementalInfo = Path('')
        if supplementalInfo.as_posix() in elnFile.namelist():
          datasetIsFolder = True
          with elnFile.open(supplementalInfo.as_posix()) as fIn:
            jsonContent = json.loads( fIn.read() )
            if isinstance(jsonContent, list):
              jsonContent = jsonContent[0]
            if elnName == 'PASTA ELN':
              doc.update( jsonContent['__main__'] )
            else:
              doc[f'from {elnName}'] = jsonContent
      if not datasetIsFolder:
        #print('  ELSE ',elnID,dataType)
        if elnName == 'PASTA ELN':
          if elnID.endswith('data_hierarchy.json'):
            return 0
          parentIDList = [i['@id'] for i in graph if 'hasPart' in i and {'@id':'./'+elnID} in i['hasPart']]
          if not parentIDList: #if no parent found, aka for remote data
            parentIDList = [i['@id'] for i in graph if 'hasPart' in i and {'@id':elnID} in i['hasPart']]
          if len(parentIDList)==1:
            metadataPath = Path(dirName)/parentIDList[0]/'metadata.json'
            with elnFile.open(metadataPath.as_posix()) as fIn:
              metadataContent = json.loads( fIn.read() )
              doc.update( metadataContent[doc['_id']] )
        elif elnName == 'eLabFTW' and elnID.endswith('export-elabftw.json'):
          return 0
        elif fullPath is not None:
          if f'{dirName}/{elnID}' in elnFile.namelist():  #could be directory, nothing to copy then
            target = open(fullPath, "wb")
            source = elnFile.open(f'{dirName}/{elnID}')
            with source, target:  #extract one file to its target directly
              shutil.copyfileobj(source, target)
      # save
      # ALL ELNS
      if '-tags' not in doc:
        doc['-tags'] = []
      else:
        doc['-tags'] = [i.strip() for i in doc['-tags'].split(',')]
      # PASTA_ELN
      if elnName == 'PASTA ELN':
        doc['-user'] = '_'
        if datasetIsFolder and fullPath is not None:
          fullPath.mkdir(exist_ok=True)
          with open(fullPath/'.id_pastaELN.json', 'w', encoding='utf-8') as fOut:
            fOut.write(json.dumps(doc))
        elif fullPath is not None:
          if not fullPath.parent.exists():
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
            print(f'  Want to created project name:{renameELN_names[elnName]}')
            projID = backend.addData('x0', {'-name':f'Imported project of {renameELN_names[elnName]} '})
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
  print(f'\n\nGraph in metadatafile\n{tree(graph)}')

  return f'Success: imported {str(addedDocuments)} documents from file {elnFileName} from ELN {elnName} {elnVersion}'




##########################################
###               EXPORT               ###
##########################################
def exportELN(backend:Backend, projectID:str, fileName:str='', dTypes:list[str]=[]) -> str:
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

  def separate(doc: dict[str,Any]) -> tuple[str, dict[str,Any], dict[str,Any]]:
    """ separate document into
    - main information (for all elns) and
    - supplemental information (specific to PastaELN)
    """
    path =  f"{doc['-branch'][0]['path']}/" if doc['-type'][0][0]=='x' else doc['-branch'][0]['path']
    pathUsed = True
    if path is None:
      pathUsed = False
      path = './'+dirNameProject+'/'+doc['_id']
    if not path.startswith(dirNameProject) and not path.startswith('http') and pathUsed:
      filesNotInProject.append(path)
    if not path.startswith('http') and pathUsed:
      path = f'./{path}'
    docMain= {'@id': path}
    docSupp = {}
    for key, value in doc.items():
      if key in pasta2json and pasta2json[key] is not None:
        docMain[pasta2json[key]] = value
      else:
        docSupp[key] = value
    # clean individual entries of docSupp: remove personal data
    del docSupp['-user']
    if 'image' in docSupp:
      del docSupp['image']
    if '_attachments' in docSupp:
      del docSupp['_attachments']
    docSupp['_id'] = docMain['identifier'] #ensure id is present in main and supplementary information
    # clean individual entries of docMain
    if 'keywords' in docMain:
      docMain['keywords'] = ','.join(docMain['keywords'])
    docMain = {k:v for k,v in docMain.items() if v}
    nonlocal keysInSupplemental
    keysInSupplemental = keysInSupplemental.union(docSupp)
    return path, docMain, docSupp


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
    if (nodeHier.docType[0] not in dTypes) and nodeHier.docType[0][0]!='x' and len(dTypes)>0:
      return None
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
      viewFull = backend.db.getView('viewHierarchy/viewHierarchyAll', startKey=' '.join(hierStack))
      viewIDs = [i['id'] for i in viewFull if len(i['key'].split())==len(hierStack)+1 and i['value'][1][0][0]!='x']
      for childID in viewIDs:
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
      elnFile.writestr(f'{dirNameProject}/{pathMetadata[2:]}', zipContent)
      docMain['@type'] = 'Dataset'
      appendDocToGraph(graph, roCrateMetadata)

    fullPath = backend.basePath/path
    if path is not None and fullPath.exists() and fullPath.is_file():
      with open(fullPath, 'rb') as fIn:
        fileContent = fIn.read()
        docMain['contentSize'] = str(len(fileContent))
        docMain['sha256']      = hashlib.sha256(fileContent).hexdigest()
      docMain['@type'] = 'File'
    elif path.startswith('http'):
      response = requests.get(path.replace(':/','://'))
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
        '@id': 'ro-crate-metadata.json',
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
    zipContent = json.dumps(backend.db.getDoc('-dataHierarchy-'))
    dataHierarchyInfo = {
        '@id':  f'./{dirNameProject}/data_hierarchy.json',
        '@type': 'File',
        'name':  'data structure',
        'description': 'data structure / schema of the stored data',
        'contentSize':str(len(zipContent)),
        'sha256':hashlib.sha256(zipContent.encode()).hexdigest(),
        'datePublished': datetime.now().isoformat()
    }
    graphMisc.append(dataHierarchyInfo)
    graph[-1]['hasPart'] += [{'@id': f'./{dirNameProject}/data_hierarchy.json'}]
    elnFile.writestr(f'{dirNameProject}/{dirNameProject}/data_hierarchy.json', zipContent)

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
    print(json.dumps(index, indent=3))
  # end writing zip file
  # temporary json output
  # with open(fileName[:-3]+'json','w', encoding='utf-8') as fOut:
  #   fOut.write( json.dumps(index, indent=2) )
  keysInSupplemental = {i for i in keysInSupplemental if i not in pasta2json}
  logging.info('Keys in supplemental information'+', '.join(keysInSupplemental))
  return f'Success: exported {len(graph)} graph-nodes into file {fileName}'
