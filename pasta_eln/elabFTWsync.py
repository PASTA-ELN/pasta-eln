""" Allow syncing to elabFTW server """
import json, copy
from typing import Any
from datetime import datetime
from anytree import PreOrderIter, Node
from PySide6.QtGui import QTextDocument
from .backend import Backend
from .elabFTWapi import ElabFTWApi
from .handleDictionaries import squashTupleIntoValue

# - consider hiding metadata.json (requires hiding the upload (state=2) and ability to read (it is even hidden in the API-read))
#   - hide an upload  api.upLoadUpdate('experiments', 66, 596, {'action':'update', 'state':'2'})
#   - listing all uploads (incl. archived) is not possible in elab currently -> leave visible; change to invisible once in elab

class Pasta2Elab:
  """ Allow syncing to elabFTW server"""

  def __init__(self, backend:Backend, projectGroup:str='', purge:bool=False):
    '''
    initiate an elab instance to allow for syncing: save data-hierarchy information
    - cannot save pasta's measurement data hierarchy in any other docTypes; hence, makes no sense to save any data hierarchy
      into any elab-item-types metadata

    Args:
      backend (backend): backend
      projectGroup (str): name of project group

    Returns:
      bool: success
    '''
    self.backend = backend
    if not projectGroup:
      projectGroup = self.backend.configuration['defaultProjectGroup']
    self.projectGroup = projectGroup
    if not self.backend.configuration['projectGroups'][self.projectGroup]['remote']['url'] or \
       not self.backend.configuration['projectGroups'][self.projectGroup]['remote']['key']:
      return
    self.api = ElabFTWApi(self.backend.configuration['projectGroups'][self.projectGroup]['remote']['url'],
                          self.backend.configuration['projectGroups'][self.projectGroup]['remote']['key'])
    if purge:
      self.api.purgeExperimentsItems()
    self.docID2elabID:dict[str,tuple[int,bool]] = {}
    self.qtDocument = QTextDocument()   #used for converting html <-> md
    self.verbose    = True
    return


  def sync(self) -> list[tuple[str,int]]:
    """ Main function

    Returns:
      list: list of merge cases
    """
    if self.api.url:  #only when you are connected to web
      self.syncDocTypes()
      self.createIdDict()
      # sync nodes in parallel
      reports = []
      for projID in self.backend.db.getView('viewDocType/x0')['id'].values:
        proj = self.backend.db.getHierarchy(projID)
        reports += [self.updateEntry(i) for i in PreOrderIter(proj)]
    return reports


  def syncDocTypes(self) -> None:
    """ Synchronize document types between client and server; save datahierarchy to server """
    #try body and metadata: compare, write
    docTypesElab  = {i['title']:i['id'] for i in self.api.read('items_types')}
    docTypesPasta = {i.capitalize() for i in self.backend.db.dataHierarchy('','') if not i.startswith('x')} | \
                    {'Default','Folder','Project','Pasta_Metadata'}
    for docType in docTypesPasta.difference({'Measurement'}|docTypesElab.keys()):  # do not create measurements, use 'experiments'
      self.api.touch('items_types', {"title": docType})
    #verify nothing extraneous
    docTypesElab  = {i['title']:i['id'] for i in self.api.read('items_types')}
    if set(docTypesElab.keys()).difference(docTypesPasta|{'Default','Pasta_Metadata'}) and self.verbose:
      print('**Info: some items exist that should not:', set(docTypesElab.keys()).difference(docTypesPasta|{'Default'}),
            'You can remove manually, but should not interfere since not used.')
    listMetadata = self.api.read('items?q=category%3APasta_Metadata&archived=on')
    dataHierarchy = []
    for docType in self.backend.db.dataHierarchy('',''):
      dataHierarchy += copy.deepcopy([dict(i) for i in self.backend.db.dataHierarchy(docType,'meta')])
    if not listMetadata:
      itemId = self.api.touch('items', {"category_id":int(docTypesElab["Pasta_Metadata"])})
    else:
      itemId = listMetadata[0]["id"]
    self.api.update('items', itemId, {"title":"data hierarchy", "metadata":json.dumps(dataHierarchy), "body":"<p>DO NOT CHANGE ANYTHING</p>","state":2})
    return


  def createIdDict(self) -> None:
    """ create mapping of docIDs to elabIDs: if not exist, create elabIds """
    elabTypes = {i['title'].lower():i['id'] for i in self.api.read('items_types')}|{'measurement':-1}
    elabTypes |= {'x0':elabTypes.pop('project'), 'x1':elabTypes.pop('folder'), '-':elabTypes.pop('default')}
    def getNewEntry(elabType:str) -> int:
      urlSuffix = 'items'                  if int(elabType)>0 else 'experiments'
      content   = {'category_id':elabType}
      return self.api.touch(urlSuffix, content)
    self.backend.db.cursor.execute("SELECT id, type, externalId FROM main")
    self.docID2elabID = {i[0]:((i[2],i[1].split('/')[0]=='measurement') if i[2] else (getNewEntry(elabTypes[i[1].split('/')[0]]),i[1].split('/')[0]=='measurement'))
                    for i in self.backend.db.cursor.fetchall()}
    # save to sqlite
    self.backend.db.cursor.executemany("UPDATE main SET id=?, externalId=? WHERE id=?", [(k,v[0],k) for k, v in self.docID2elabID.items()])
    self.backend.db.connection.commit()
    return


  def updateEntry(self, node:Node) -> tuple[str,int]:
    """ update an entry in elabFTW: all the logic goes here
        - myDesktop: sends content and the date when upload is made; if there is a change in modified time; the change is for real
        - server: gets document; if there is a difference between metadata.json and content: it was changed for real
        - other desktops changes: as before; my desktop **cannot differentiate myChanges vs other desktop changes**
          -> have to save also upload time locally, save in extra column

    Args:
      node (Node): node to process

    Returns:
      tuple: node.id; merge case
    """
    # get this content: check if it changed
    mergeCase = -1
    docClient   = self.backend.db.getDoc(node.id)
    if 'dateSync' not in docClient or not docClient['dateSync']:
      docClient['dateSync'] = datetime.fromisoformat('2000-01-03').isoformat()+'.0000'
    if self.verbose:
      print('\n>>>DOC_CLIENT sync&modified', docClient['dateSync'], docClient['dateModified'])
    # pull from server: content and other's client content
    entityType = 'experiments' if self.docID2elabID[node.id][1] else 'items'
    docServer, uploads = self.elab2doc(self.api.read(entityType, self.docID2elabID[node.id][0])[0])
    if self.verbose:
      print('>>>DOC_SERVER', docServer)
    if [i for i in uploads if i['real_name']=="do_not_change.json"]:
      docOther = self.api.download(entityType, self.docID2elabID[node.id][0],
                                   [i for i in uploads if i['real_name']=="do_not_change.json"][0])
    else:
      docOther = {'name':'Untitled', 'tags':[], 'comment':'', 'dateSync':datetime.fromisoformat('2000-01-02').isoformat()+'.0000',
                  'dateModified':datetime.fromisoformat('2000-01-01').isoformat()+'.0000'}
    if self.verbose:
      print('>>>DOC_OTHER sync&modified', docOther.get('dateSync'), docOther.get('dateModified'))
    docMerged:dict[str,Any] = {}
    flagUpdateClient, flagUpdateServer = False, False
    # merge 1: compare server content and doc and update later with changes
    flagServerChange = False
    for k,v in docServer.items():
      if isinstance(v, (dict, str)):
        if v != docOther[k]:
          flagServerChange = True
          if self.verbose:
            print('str change', k,v, docOther[k])
          docOther[k] = docServer[k]
      elif isinstance(v, list):
        if set(v) != set(docOther[k]):
          flagServerChange = True
          if self.verbose:
            print('list change', k,v, docOther[k])
          docOther[k] = docServer[k]
      elif self.verbose:
        print('other change', k,v, docOther[k], type(v))
    if flagServerChange:
      if self.verbose:
        print('Server content changed from other')
      docOther['dateModified'] = datetime.now().isoformat()
    #  merge 2
    pattern = '%Y-%m-%dT%H:%M:%S.%f'
    # Case 1 straight update from client to server: only client updated and server not changed
    if datetime.strptime(docClient['dateModified'], pattern) > datetime.strptime(docClient['dateSync'], pattern) and \
       datetime.strptime(docOther['dateModified'], pattern)  < datetime.strptime(docOther['dateSync'], pattern):
      mergeCase = 1
      if self.verbose:
        print(f'** MERGE CASE {mergeCase}')
      flagUpdateServer = True
      flagUpdateClient = False
      docMerged = copy.deepcopy(docClient)
    # Case 2 straight update from server to client: only others was updated / server itself was not updated, client not changed
    if datetime.strptime(docClient['dateModified'], pattern) < datetime.strptime(docClient['dateSync'], pattern) and \
         datetime.strptime(docOther['dateModified'], pattern) < datetime.strptime(docOther['dateSync'], pattern) and \
         datetime.strptime(docOther['dateSync'], pattern)     < datetime.strptime(docOther['dateSync'], pattern):
      mergeCase = 2
      if self.verbose:
        print(f'** MERGE CASE {mergeCase}')
      flagUpdateServer = False
      flagUpdateClient = True
      docMerged = copy.deepcopy(docOther)
    # Case 3 straight update from server to client: only server updated, client not changed
    if datetime.strptime(docClient['dateModified'], pattern) < datetime.strptime(docClient['dateSync'], pattern) and \
         datetime.strptime(docOther['dateModified'], pattern) > datetime.strptime(docOther['dateSync'], pattern):
      mergeCase = 3
      if self.verbose:
        print(f'** MERGE CASE {mergeCase}')
      flagUpdateServer = True
      flagUpdateClient = True
      docMerged = copy.deepcopy(docOther)
    # Case 4 no change: nothing changed
    if datetime.strptime(docClient['dateModified'], pattern) < datetime.strptime(docClient['dateSync'], pattern) and \
         datetime.strptime(docOther['dateModified'], pattern) < datetime.strptime(docOther['dateSync'], pattern):
      mergeCase = 4
      if self.verbose:
        print(f'** MERGE CASE {mergeCase}')
      flagUpdateServer = False
      flagUpdateClient = False
      docMerged = {}
    # Case 5 both are updated: merge: both changed -> GUI
    if datetime.strptime(docClient['dateModified'], pattern) > datetime.strptime(docClient['dateSync'], pattern) and \
       datetime.strptime(docOther['dateModified'], pattern) > datetime.strptime(docOther['dateSync'], pattern):
      mergeCase = 5
      if self.verbose:
        print(f'** MERGE CASE {mergeCase}')

    # Case X: else
    # else:
    #   #TODO more complicated
    #   pass
    docMerged['dateSync'] = datetime.now().isoformat()
    if self.verbose:
      print('>>>MERGE TIME', docMerged['dateSync'])
    # THE REST IS MOSTLY DONE

    # update client
    if flagUpdateClient:
      docUpdate = copy.deepcopy(docMerged)
      docUpdate['branch'] = docUpdate['branch'][0] | {'op':''}
      if 'metaVendor' in docUpdate:
        del docUpdate['metaVendor']
      squashTupleIntoValue(docUpdate)
      self.backend.db.updateDoc(docUpdate, node.id)
    else:
      self.backend.db.cursor.execute(f"UPDATE main SET dateSync='{docMerged['dateSync']}' WHERE id = '{node.id}'")
      self.backend.db.connection.commit()
    # send doc (merged version) to server everything
    if flagUpdateServer:
      content, image = self.doc2elab(copy.deepcopy(docMerged))
      self.api.update(entityType, self.docID2elabID[node.id][0], content)
      # create links
      _ = [self.api.createLink(entityType, self.docID2elabID[node.id][0], 'experiments' if self.docID2elabID[node.id][1] else 'items', self.docID2elabID[i.id][0])
                              for i in node.children]
    # uploads| clean first, then upload: PASTAs document, thumbnail, data-file
    existingUploads = self.api.read(entityType, self.docID2elabID[node.id][0])[0]['uploads']
    uploadsToDelete = {'do_not_change.json', 'metadata.json'}
    if flagUpdateServer:
      uploadsToDelete |= {'thumbnail.svg', 'thumbnail.png', 'thumbnail.jpg'}
    for upload in existingUploads:
      if upload["real_name"] in uploadsToDelete:
        self.api.uploadDelete(entityType, self.docID2elabID[node.id][0], upload['id'])
    self.api.upload(entityType, self.docID2elabID[node.id][0], jsonContent=json.dumps(docMerged))
    if flagUpdateServer:
      if image:
        self.api.upload(entityType, self.docID2elabID[node.id][0], image)
      if docMerged['branch'][0]['path'] is not None and docMerged['type'][0][0]!='x' \
            and not docMerged['branch'][0]['path'].startswith('http') and \
            (self.backend.basePath/docMerged['branch'][0]['path']).name not in {i['real_name'] for i in existingUploads}:
        self.api.upload(entityType, self.docID2elabID[node.id][0], fileName=self.backend.basePath/docMerged['branch'][0]['path'], comment='raw data')
    return node.id, mergeCase


  def elab2doc(self,elab:dict[str,Any]) -> tuple[dict[str,Any], list[Any]]:
    """ Convert an elabFTW dict-html entry into a PASTA doc

    Args:
      elab (dict): elabFTW entry

    Returns:
      dict: PASTA doc
    """
    # print(json.dumps(elab, indent=2))
    self.qtDocument.setHtml(elab.get('body',''))
    comment = self.qtDocument.toMarkdown()
    if comment.endswith('\n\n'):
      comment = comment[:-2]  #also handle contents
    # User is not allowed to change dates: ignore these dates from the server
    tags = [] if elab.get('tags','') is None else elab.get('tags','').split('|')
    doc = {'name': elab.get('title',''), 'tags':tags, 'comment':comment}
    metadata = {} if elab.get('metadata') is None else json.loads(elab['metadata'])
    # doc['metaVendor'] = metadata.get('metaVendor',{})  # USERS IS NOT ALLOWED TO CHANGE THESE
    # doc['metaUser']   = metadata.get('metaUser',{})
    doc |= metadata.get('__',{})                         # USERS CAN CHANGE THIS ON ELAB
    return doc, elab.get('uploads',[])


  def doc2elab(self, doc:dict[str,Any]) -> tuple[dict[str,Any], str]:
    """ Convert a PASTA doc into an elabFTW dict-html entry

    Args:
      doc (dict): PASTA doc

    Returns:
      dict: elabFTW entry
    """
    if not doc:
      raise ValueError('Cannot convert / process empty document')
    image     = doc.pop('image') if 'image' in doc else ''
    title     = doc.pop('name')
    bodyMD    = ''
    if 'content' in doc:
      bodyMD += doc.pop('content')+'\n\n__DO NOT CHANGE THIS DELIMITER between content (top) and comment (bottom)__\n\n'
    bodyMD    = doc.pop('comment')
    self.qtDocument.setMarkdown(bodyMD)
    body      = self.qtDocument.toHtml()
    created_at= doc.pop('dateCreated')
    modified_at=doc.pop('dateModified')
    tags       =doc.pop('tags')
    doc        = {k:v for k,v in doc.items() if k not in {'id','user','client','externalId','type','gui','branch','shasum','qrCodes'}}
    metadata = {'metaVendor': doc.pop('metaVendor') if 'metaVendor' in doc else {}}
    metadata['metaUser']    = doc.pop('metaUser')   if 'metaUser' in doc else {}
    if doc:
      doc.pop('dateSync')
      metadata |= {'__':doc}
    #TODO clarify how tags should be encoded
    elab = {'body':body, 'title':title, 'metadata':json.dumps(metadata), 'tags':tags, 'created_at':created_at, 'modified_at':modified_at}
    return elab, image
