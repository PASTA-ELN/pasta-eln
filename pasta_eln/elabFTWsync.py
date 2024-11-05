""" Allow syncing to elabFTW server """
import json, copy, hashlib
from typing import Any
from datetime import datetime
from anytree import PreOrderIter, Node
from PySide6.QtGui import QTextDocument
from .backend import Backend
from .elabFTWapi import ElabFTWApi

# - consider hiding metadata.json (requires hiding the upload (state=2) and ability to read (it is even hidden in the API-read))
#   - hide an upload  api.upLoadUpdate('experiments', 66, 596, {'action':'update', 'state':'2'})
#   - listing all uploads (incl. archived) is not possible in elab currently -> leave visible; change to invisible once in elab

class Pasta2Elab:
  """ Allow syncing to elabFTW server"""

  def __init__(self, backend:Backend, projectGroup:str=''):
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
    self.api = ElabFTWApi(self.backend.configuration['projectGroups'][self.projectGroup]['remote']['url'],
                          self.backend.configuration['projectGroups'][self.projectGroup]['remote']['key'])
    self.docID2elabID:dict[str,tuple[int,bool]] = {}
    self.qtDocument = QTextDocument()   #used for converting html <-> md
    return


  def sync(self) -> None:
    """ Main function """
    if self.api.url:  #only when you are connected to web
      self.syncDocTypes()
      self.createIdDict()
      # sync nodes in parallel
      for projID in self.backend.db.getView('viewDocType/x0')['id'].values:
        proj = self.backend.db.getHierarchy(projID)
        # _ = [self.updateEntry(i) for i in PreOrderIter(proj)]
        self.updateEntry(proj)
    return


  def syncDocTypes(self) -> None:
    """ Syncronize document types between client and server; save datahierarchy to server """
    #try body and metadata: compare, write
    docTypesElab  = {i['title']:i['id'] for i in self.api.read('items_types')}
    docTypesPasta = {i.capitalize() for i in self.backend.db.dataHierarchy('','') if not i.startswith('x')} | \
                    {'Default','Folder','Project','Pasta_Metadata'}
    for docType in docTypesPasta.difference({'Measurement'}|docTypesElab.keys()):  # do not create measurements, use 'experiments'
      self.api.touch('items_types', {"title": docType})
    #verify nothing extraneous
    docTypesElab  = {i['title']:i['id'] for i in self.api.read('items_types')}
    if set(docTypesElab.keys()).difference(docTypesPasta|{'Default','Pasta_Metadata'}):
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


  def updateEntry(self, node:Node) -> bool:
    """ update an entry in elabFTW: all the logic goes here
        - myDesktop: sends content and the date when upload is made; if there is a change in modified time; the change is for real
        - server: gets document; if there is a difference between metadata.json and content: it was changed for real
        - other desktops changes: as before; my desktop **cannot differentiate myChanges vs other desktop changes**
          -> have to save also upload time locally, save in extra column

    Args:
      node (Node): node to process

    Returns:
      bool: success
    """
    # get this content: check if it changed
    docClient   = self.backend.db.getDoc(node.id)
    print('>>>DOC_CLIENT sync&modified', docClient['dateSync'], docClient['dateModified'])
    # pull from server: content and other's client content
    entityType = 'experiments' if self.docID2elabID[node.id][1] else 'items'
    docServer, uploads = self.elab2doc(self.api.read(entityType, self.docID2elabID[node.id][0])[0])
    print('>>>DOC_SERVER', docServer)
    docOther = self.api.download(entityType, self.docID2elabID[node.id][0],
                                 [i for i in uploads if i['real_name']=="do_not_change.json"][0])
    print('>>>DOC_OTHER sync&modified', docOther.get('dateSync','-------'), docOther.get('dateModified','-------'))
    # merge logic -> update client: maximum 2
    # TODO
    print(json.dumps(docClient, indent=2))
    flagUpdateServer = True
    flagUpdateClient = False
    docMerged = copy.deepcopy(docClient)
    docMerged['dateSync'] = datetime.now().isoformat()
    print('>>>MERGE TIME', docMerged['dateSync'])
    # THE REST IS MOSTLY DONE

    # update client
    if flagUpdateClient:
      self.backend.db.updateDoc(docMerged, node.id)
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
    return True

  def elab2doc(self,elab:dict[str,Any]) -> tuple[dict[str,Any], list[Any]]:
    """ Convert an elabFTW dict-html entry into a PASTA doc
    Args:
      elab (dict): elabFTW entry
    Returns:
      dict: PASTA doc

    todo: metadata
    """
    print(json.dumps(elab, indent=2))
    self.qtDocument.setHtml(elab.get('body',''))
    doc = {'name': elab.get('title',''), 'tags':elab.get('tags',''), 'dateCreated':elab.get('created_at',''),
           'dateModified':elab.get('modified_at',''), 'comment':self.qtDocument.toMarkdown()}
    print(json.dumps(doc, indent=2))
    return doc, elab['uploads']

  def doc2elab(self, doc:dict[str,Any]) -> tuple[dict[str,Any], str]:
    """ Convert a PASTA doc into an elabFTW dict-html entry
    Args:
      doc (dict): PASTA doc
    Returns:
      dict: elabFTW entry
    """
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
    metadata  = doc.pop('metaVendor') if 'metaVendor' in doc else {}
    metadata |= doc.pop('metaUser')   if 'metaUser' in doc else {}
    if doc:
      metadata |= {'__':doc}
    elab = {'body':body, 'title':title, 'metadata':json.dumps(metadata), 'tags':tags, 'created_at':created_at, 'modified_at':modified_at}
    return elab, image



# New that works
# print('\nItems types',json.dumps(self.api.read('items_types'), indent=2))
# self.api.delete('items_types/10')

# OLD ---
# print(json.dumps(crud(backend, projectGroup, 'items_types/4'), indent=2))
# #print(crud(backend, projectGroup, 'items_types/4', 'update', {"body":"some json string"}))
# url = 'experiments/1'  #full detail
# print('\nExperiment1',json.dumps(crud(backend, projectGroup, url), indent=2))
# url = 'info'  #version number
# print('\nINFO',json.dumps(crud(backend, projectGroup, url), indent=2))
# url = 'experiments'  #summary
# print('\nExperiments',json.dumps(crud(backend, projectGroup, url), indent=2))
# url = 'items'  #summary
# print('\nItems',json.dumps(crud(backend, projectGroup, url), indent=2))
# url = 'items_types'  #all types incl. default
# crud(backend, projectGroup, url, 'create', {"title": "Go22Go"})
# print(crud(backend, projectGroup, f'{url}/5', 'update', {"color":"#aabbaa"}))
# print(json.dumps(crud(backend, projectGroup, f'{url}/5'), indent=2))
# print('\nItemTypes',json.dumps(crud(backend, projectGroup, url), indent=2))
