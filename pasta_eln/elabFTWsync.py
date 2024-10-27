""" Allow syncing to elabFTW server """
import json, copy
from anytree import PreOrderIter, Node
from PySide6.QtGui import QTextDocument
from .backend import Backend
from .elabFTWapi import ElabFTWApi

class Pasta2Elab:
  """ Allow syncing to elabFTW server"""

  def __init__(self, backend:Backend, projectGroup:str):
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
    self.projectGroup = projectGroup
    self.api = ElabFTWApi(self.backend.configuration['projectGroups'][self.projectGroup]['remote']['url'],
                          self.backend.configuration['projectGroups'][self.projectGroup]['remote']['key'])
    #try body and metadata: compare, write
    docTypesElab  = {i['title']:i['id'] for i in self.api.read('items_types')}
    docTypesPasta = {i.capitalize() for i in backend.db.dataHierarchy('','') if not i.startswith('x')} |{'Folder','Project','Pasta_Metadata'}
    for docType in docTypesPasta.difference({'Measurement'}|docTypesElab.keys()):  # do not create measurements, use 'experiments'
      self.api.touch('items_types', {"title": docType})
    #verify nothing extraneous
    docTypesElab  = {i['title']:i['id'] for i in self.api.read('items_types')}
    if set(docTypesElab.keys()).difference(docTypesPasta|{'Default','Pasta_Metadata'}):
      print('**ERROR: some items exist that should not:', set(docTypesElab.keys()).difference(docTypesPasta|{'Default'}))
    listMetadata = self.api.read('items?q=category%3APasta_Metadata')
    dataHierarchy = []
    for docType in backend.db.dataHierarchy('',''):
      dataHierarchy += copy.deepcopy([dict(i) for i in backend.db.dataHierarchy(docType,'meta')])
    if not listMetadata:
      itemId = self.api.touch('items', {"category_id":int(docTypesElab["Pasta_Metadata"])})
    else:
      itemId = listMetadata[0]["id"]
    self.api.update('items', itemId, {"title":"data hierarchy", "metadata":json.dumps(dataHierarchy), "body":"<p>DO NOT CHANGE ANYTHING</p>"})
    return

  def pasta2elab(self) -> bool:
    '''
    import .eln file from other ELN or from PASTA

    Returns:
      bool: success
    '''
    # create mapping of docIDs to elabIDs: if not exist, create elabIds
    elabTypes = {i['title'].lower():i['id'] for i in self.api.read('items_types')}|{'measurement':-1}
    elabTypes |= {'x0':elabTypes.pop('project'), 'x1':elabTypes.pop('folder'), '-':elabTypes.pop('default')}
    def getNewEntry(elabType:str) -> int:
      urlSuffix = 'items'                  if int(elabType)>0 else 'experiments'
      content   = {'category_id':elabType}
      return self.api.touch(urlSuffix, content)
    self.backend.db.cursor.execute("SELECT id, type, externalId FROM main")
    docID2elabID = {i[0]:(i[2] or getNewEntry(elabTypes[i[1].split('/')[0]]))
                    for i in self.backend.db.cursor.fetchall()}
    # save to sqlite
    self.backend.db.cursor.executemany("UPDATE main SET id=?, externalId=? WHERE id=?", [(k,v,k) for k, v in docID2elabID.items()])
    self.backend.db.connection.commit()
    # use map to update
    qtDocument = QTextDocument()   #used
    def updateEntry(node:Node) -> bool:
      """ update an entry in elabFTW

      Args:
        node (Node): node to process

      Returns:
        bool: success
      """
      doc   = self.backend.db.getDoc(node.id)
      image     = doc.pop('image') if 'image' in doc else ''
      title     = doc.pop('name')
      bodyMD    = doc.pop('comment')
      if 'content' in doc:
        bodyMD += '\n\n__DO NOT CHANGE THIS DELIMITER__\n\n'+doc.pop('content')
      qtDocument.setMarkdown(bodyMD)
      body      = qtDocument.toHtml()
      created_at= doc.pop('dateCreated')
      modified_at=doc.pop('dateModified')
      tags       =doc.pop('tags')
      pastaMeta = {'id':doc.pop('id'), 'user':doc.pop('user'), 'client':doc.pop('client'), 'externalId':doc.pop('externalId'),
                   'type':doc.pop('type'), 'gui':doc.pop('gui'), 'branch':doc.pop('branch')}
      if 'qrCodes' in doc:
        pastaMeta['qrCodes'] = doc.pop('qrCodes')
      if 'shasum' in doc:
        pastaMeta['shasum']  = doc.pop('shasum')
      metadata  = doc.pop('metaVendor') if 'metaVendor' in doc else {}
      metadata |= doc.pop('metaUser')   if 'metaUser' in doc else {}
      if doc:
        metadata |= {'__':doc}
      metadata |= {'DO NOT CHANGE':pastaMeta}
      content = {'body':body, 'title':title, 'metadata':json.dumps(metadata), 'tags':tags, 'created_at':created_at, 'modified_at':modified_at}
      entity_type = 'experiments' if pastaMeta['type'][0]=='measurement' else 'items'
      self.api.update(entity_type, docID2elabID[node.id], content)
      # create links
      _ = [self.api.createLink(entity_type, docID2elabID[node.id], 'experiments' if i.docType[0]=='measurement' else 'items', docID2elabID[i.id])
                              for i in node.children]
      if image:
        self.api.upload(entity_type, docID2elabID[node.id], image)
      if pastaMeta['branch'][0]['path'] is not None and \
         pastaMeta['type'][0][0]!='x' and \
         not pastaMeta['branch'][0]['path'].startswith('http'):
        self.api.upload(entity_type, docID2elabID[node.id], fileName=self.backend.basePath/pastaMeta['branch'][0]['path'], comment='raw data')
      return True

    for projID in self.backend.db.getView('viewDocType/x0')['id'].values:
      proj = self.backend.db.getHierarchy(projID)
      _ = [updateEntry(node) for node in PreOrderIter(proj)]
    return True

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
