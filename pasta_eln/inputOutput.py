"""Input and output functions towards the .eln file-format"""
import os, json, shutil, logging, hashlib
from typing import Any
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
from pasta_eln import __version__
from .backend import Backend
#TODO_P3 Add read info from ror and orcid
# curl https://api.ror.org/organizations/02nv7yv05
# curl -s -H "Accept: application/json" https://pub.orcid.org/v3.0/0000-0001-7691-2856


#GENERAL TERMS IN ro-crate-metadata.json (None implies not saved)
pasta2json = {
  '_id'    : 'identifier',
  '_rev'   : None,
  '_attachments': None,
  '-name'  : 'name',
  '-tags'  : 'keywords',
  '-date'  : 'dateModified',
  '-user'  : None,
  '-client': None,
  'comment': 'comment',
  'content': 'text',
  'links'  : 'mentions',
}
# Possible extensions
#  'image'  : 'image'
#
# # keys not in this dict and require json name
# 'metaUser', 'status', 'procedure', 'metaVendor', 'chemistry', '-branch', '-type', 'qrCode', 'shasum', 'objective'
requiredKeys = ['_id', '-name', '-tags', '-date', '-user', '-client']

# Special terms in other elns
elabFTW = {
  'elabid':'_id',
  'title':'-name',
  'tags':'-tags',
  'lastchange':'-date',
  'userid':'-user',
  'metadata':'metaUser',
  'id':'_id',
  'category': '-type'
}
# tags: "abc|efg" vs ['abc','efg']
# internal identifier (elabFTW:id) vs global identifier (elabFTW: identifier)



# TODO_P1 if others eln: write new addDoc to add hierStack and branch based on path
# - Don't create folders then
# use internal id for now
# create a dictonary of old id and new id
# tags see if list: else split at |

def importELN(backend:Backend, elnFileName:str) -> str:
  '''
  import .eln file from other ELN or from PASTA

  Args:
    backend (backend): backend
    elnFileName (str): name of file

  Returns:
    str: success message
  '''
  keysNotInDict:set[str] = set()

  def processPart(part:dict[str,str]) -> int:
    """
    recursive function call to process this node

    Args:
      part (dict): dictionary containing this data content

    Returns:
      bool: success of this function
    """
    addedDocs = 0
    if not isinstance(part, dict): #leave these tests in since other .elns might do funky stuff
      print("**ERROR in part",part)
      return False
    logging.info('Process: '+part['@id'])
    print('Process: '+part['@id'])
    # find next node to process
    newNodes = [i for i in graph if '@id' in i and i['@id']==part['@id']]
    if len(newNodes)>1:
      print('**ERROR multiple nodes with same id', newNodes)
      return False
    # if node with more subnodes
    if len(newNodes)==1:
      newNode = newNodes[0]
      subparts = newNode.pop('hasPart') if 'hasPart' in newNode else []
      if len(subparts)>0:
        logging.info('subparts:'+', '.join(['  '+i['@id'] for i in subparts]))
        print('subparts:'+', '.join(['  '+i['@id'] for i in subparts]))
      fullPath = backend.basePath/newNode['@id']
      if newNode['@id'].endswith('.json'):                    #read json content into DB
        with elnFile.open( (Path(dirName)/newNode['@id']).as_posix() ) as fIn:
          jsonContent = fIn.read()
          for dataJson in json.loads(jsonContent):
            #Transcribe content
            dataPasta = {}
            for key, value in dataJson.items():
              if key in json2pasta:
                dataPasta[json2pasta[key]] = value
              else:
                dataPasta[key] = value
                keysNotInDict.add(key)
            dataPasta['-client'] = 'Imported from '+elnName+' '+elnVersion
            addedDocs += 1
            for reqKey in requiredKeys:
              if reqKey not in dataPasta:
                print('**ERROR key not in doc', reqKey)
            backend.db.saveDoc(dataPasta)
      elif newNode['@type']=='Dataset':                     #create folder
        fullPath.mkdir(exist_ok=True)
      else:                                                 #copy file
        # print('copy file', dirName+'/'+part['@id'], fullPath)
        target = open(fullPath, "wb")
        source = elnFile.open( (Path(dirName)/part['@id']).as_posix())
        with source, target:  #extract one file to its target directly
          shutil.copyfileobj(source, target)
      #recursive part
      if len(subparts)>0:  #don't do if no subparts: measurements, ...
        # backend.changeHierarchy(backend.currentID)
        for subpart in subparts:
          addedDocs += processPart(subpart)
        # backend.changeHierarchy(None)
    return addedDocs

  ######################
  #main function
  json2pasta = {v:k for k,v in pasta2json.items() if v is not None}
  elnName = ''
  elnVersion = ''
  with ZipFile(elnFileName, 'r', compression=ZIP_DEFLATED) as elnFile:
    files = elnFile.namelist()
    logging.info('All files '+', '.join(files))
    print('All files '+', '.join(files))
    dirName=Path(files[0]).parts[0]
    if dirName+'/ro-crate-metadata.json' not in files:
      print('**ERROR: ro-crate does not exist in folder. EXIT')
      return '**ERROR: ro-crate does not exist in folder. EXIT'
    graph = json.loads(elnFile.read(dirName+'/ro-crate-metadata.json'))["@graph"]
    #find information from master node
    rocrateNode = [i for i in graph if i["@id"]=="ro-crate-metadata.json"][0]
    if 'sdPublisher' in rocrateNode:
      elnName     = rocrateNode['sdPublisher']['name']
    if 'version' in rocrateNode:
      elnVersion  = rocrateNode['version']
    else:
      elnVersion  = ''
    logging.info('Import '+elnName+' '+elnVersion)
    print('Import '+elnName+' '+elnVersion)
    if elnName=='eLabFTW':
      json2pasta.update(elabFTW)
    mainNode    = [i for i in graph if i["@id"]=="./"][0]
    #iteratively go through list
    addedDocuments = 0
    for part in mainNode['hasPart']:
      if not part['@id'].endswith('ro-crate-metadata.json'):
        addedDocuments += processPart(part)
  return 'Success: imported '+str(addedDocuments)+' documents from file '+elnFileName+\
         ' from ELN '+elnName+' '+elnVersion+'\n'+' '.join(keysNotInDict)


##########################################
###               EXPORT               ###
##########################################
def exportELN(backend:Backend, docID:str, fileName:str='') -> str:
  """
  export eln to file

  Args:
    backend (backend): PASTA backend instance
    docID (str): docId of project
    fileName (str): fileName which to use for saving; default='' saves in local folder

  Returns:
    str: report of exportation
  """
  docProject = backend.db.getDoc(docID)
  dirNameProject = docProject['-branch'][0]['path']
  fileName = dirNameProject+'.eln' if fileName=='' else fileName
  logging.info('Create eln file '+fileName)
  with ZipFile(fileName, 'w', compression=ZIP_DEFLATED) as elnFile:
    # numAttachments = 0
    graph:list[dict[str,Any]] = []

    # ------- Prepare local pathTree -------------------
    listDocs = backend.db.getView('viewHierarchy/viewPaths', startKey=dirNameProject)
    #create tree of path hierarchy: key=docID; value is a list of children
    pathTree = {}

    def listChildren(parentPath:Path, level:int) -> list[str]:
      """
      List all children

      Args:
        parentPath (Path): path to this document
        level (int): hierarchical level starting from 0

      Returns:
        list: list of children ids
      """
      items = [i for i in listDocs if Path(i['key']).parent==parentPath ]
      #create sub-children
      for item in items:
        children = listChildren(Path(item['key']), level+1)
        pathTree[item['key']] = children
      return [i['key'] for i in items]

    children = listChildren(parentPath=Path(dirNameProject), level=1)  #tree data is filled after this command
    pathTree[dirNameProject] = children

    # ------- Create graph incl. children ----------------
    # incl. information that is in pasta2json into the graph
    for me, children in pathTree.items():
      node = {}
      node['@id']   = me
      myLineInListDocs = [i for i in listDocs if i['key'] == me][0]
      doc = backend.db.getDoc(myLineInListDocs['id'])
      for keyPasta, keyELN in pasta2json.items():
        if keyPasta in doc and keyELN is not None:
          node[keyELN] = doc[keyPasta]
      if myLineInListDocs['id'][0] == 'x':       #folders
        node['@type'] = 'Dataset'
        graph.append({'@id':me+'/metadata.json', '@type':'File'})
        children.append(me+'/metadata.json')
      else:                                      #all others: i.e. measurements
        node['@type'] = 'File'
      if len(children)>0:
        node['hasPart'] = [{'@id':i} for i in children]
      graph.append(node)
      # Attachments are not saved

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
    masterNodeRoot  = {'@id':'./', '@type':['Dataset'], 'hasPart': [{'@id':dirNameProject}, {'@id':dirNameProject+'/ro-crate-metadata.json'}]}
    graphMaster.append(masterNodeRoot)

    # ------------------ copy data-files --------------------------
    # datafiles are already in the graph-graph: only copy and no addition to graph
    for path, _, files in os.walk(backend.basePath/dirNameProject):
      if '/.git' in path:  #if use datalad
        continue
      relPath = os.path.relpath(path, backend.basePath) #path of the folder
      for iFile in files:                            #iterate through all files in folder
        if iFile.startswith('.git') or iFile=='.id_pastaELN.json':
          continue
        # print('copy file', path+'/'+iFile, dirNameProject+'/'+relPath+'/'+iFile )
        elnFile.write(path+'/'+iFile, dirNameProject+'/'+relPath+'/'+iFile)   #zip file

    # ------------------ metadata.json files --------------------------
    # create metadata.json files in zip-file: no addition to graph
    #TODO_P1 get rid of this part

    keysNotInDict = set()
    for path, children in pathTree.items():
      metaDataJsonPaths = [i for i in children if 'metadata.json' in i]
      if len(metaDataJsonPaths)==0:
        continue
      metaDataJsonPath = metaDataJsonPaths[0] #want to write into this name
      #get content
      pastaContent =[]
      folderInListDocs = [i for i in listDocs if i['key'] == path][0]
      stack = folderInListDocs['value'][0]+[folderInListDocs['id']]
      listHierarchy = backend.db.getView('viewHierarchy/viewHierarchy', startKey=' '.join(stack))
      for item in listHierarchy:
        if len(stack)+1 == len(item['key'].split(' ')):
          doc = backend.db.getDoc(item['id'])
          pastaContent.append(doc)
      pastaContent.append( backend.db.getDoc(stack[-1]) )
      #Iterate through content and transcribe
      jsonContent = []
      for dataPasta in pastaContent:
        dataJson = {}
        for key,value in dataPasta.items():
          if key not in pasta2json:                          #keep as is
            keysNotInDict.add(key)
            dataJson[key] = value
          # if key in pasta2json and pasta2json[key] is not None:  #DO NOT TRANSCRIBE
          #   #  dataJson[pasta2json[key]] = value
        jsonContent.append(dataJson)
      elnFile.writestr(dirNameProject+'/'+metaDataJsonPath, json.dumps(jsonContent, indent=2))
    print('Keys not in dictionary', keysNotInDict)


    # ------------------ go through graph and add information ----
    #TODO_P1 get rid of this part

    for node in graph:
      if node['@type']=='File':                    #metadata.json and data file
        node['name'] = node['@id'].split('/')[-1]
        with elnFile.open( dirNameProject+'/'+node['@id'] ) as fIn:
          content = fIn.read()
          node['contentSize'] = str(len(content))
          node['sha256'] = hashlib.sha256(content).hexdigest()
        if node['@id'].endswith('/metadata.json'):    #metadata.json
          node['description'] = 'JSON export'
          node['contentType'] = 'application/json'
        else:                                         #data file
          #one could pull information from the database here
          pass
      else:                                        #dataset = folder
        #one could pull information from the database here
        pass

    #finalize file
    index['@graph'] = graphMaster+graph
    elnFile.writestr(dirNameProject+'/'+'ro-crate-metadata.json', json.dumps(index, indent=2))
    with open(fileName[:-3]+'json','w', encoding='utf-8') as fOut:
      fOut.write( json.dumps(index, indent=2) )
  return 'Success: exported '+str(len(graph))+' documents into file '+fileName
