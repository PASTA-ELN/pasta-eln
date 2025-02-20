""" Allow syncing to elabFTW server """
import copy
import json
from datetime import datetime
from typing import Any, Callable
from anytree import Node, PreOrderIter
from PySide6.QtGui import QTextDocument
from .backend import Backend
from .elabFTWapi import ElabFTWApi
from .handleDictionaries import squashTupleIntoValue
from .miscTools import flatten

# - consider hiding metadata.json (requires hiding the upload (state=2) and ability to read (it is even hidden in the API-read))
#   - hide an upload  api.upLoadUpdate('experiments', 66, 596, {'action':'update', 'state':'2'})
#   - listing all uploads (incl. archived) is not possible in elab currently -> leave visible; change to invisible once in elab

def cliCallback(api:ElabFTWApi , entry:str, idx:int) -> str:
  """ Default callback function for the syncMissingEntries function

  Args:
    api (ElabFTWApi): api to ask about more information
    entry (str): entry type to ask about
    idx (int): entry number on elabFTW server

  Returns:
    str: mode of processing: g,gA,s,sA
  """
  print(f'**ERROR**: default callback function should not be called. API:{api}, entry:{entry}, idx:{idx}')
  return ''


MERGE_LABELS = {
     -1:'-1: ERROR',
      1:'1: client -> server',
      2:'2: other client -> client',
      3:'3: server -> client',
      4:'4: no change',
      5:'5: BOTH CHANGE / Merge'
    }


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
      purge (bool): remove old documents

    Returns:
      bool: success
    '''
    self.backend = backend
    self.projectGroup = projectGroup or self.backend.configuration['defaultProjectGroup']
    if not self.backend.configuration['projectGroups'][self.projectGroup]['remote']['url'] or \
       not self.backend.configuration['projectGroups'][self.projectGroup]['remote']['key']:
      return
    self.api = ElabFTWApi(self.backend.configuration['projectGroups'][self.projectGroup]['remote']['url'],
                          self.backend.configuration['projectGroups'][self.projectGroup]['remote']['key'])
    configRemote = self.backend.configuration['projectGroups'][self.backend.configurationProjectGroup]['remote']
    self.elabProjGroupID = configRemote['config']['id']
    if purge:
      data = self.api.readEntry('items', self.elabProjGroupID)[0]
      _ = [self.api.deleteEntry('experiments', i['entityid']) for i in data['related_experiments_links']]
      _ = [self.api.deleteEntry('items',       i['entityid']) for i in data['related_items_links']]
    self.docID2elabID:dict[str,tuple[int,bool]] = {}  # x-15343154th54325243, (4, bool if experiment)
    self.qtDocument      = QTextDocument()            # used for converting html <-> md
    self.verbose         = True
    return


  def sync(self, mode:str='', callback:Callable[[ElabFTWApi,str,int],str]=cliCallback) -> list[tuple[str,int]]:
    """ Main function

    Args:
      mode (str): sync mode g=get, gA=get-all, s=send, sA=send-all
      callback (func): callback function if non-all mode is given

    Returns:
      list: list of merge cases
    """
    if self.api.url:  #only when you are connected to web
      self.syncDocTypes()  #category agree
      self.createIdDict()
      # sync nodes in parallel
      reports = []
      for projID in self.backend.db.getView('viewDocType/x0')['id'].values:
        projHierarchy, _ = self.backend.db.getHierarchy(projID)
        reports += [self.updateEntry(i, mode, callback) for i in PreOrderIter(projHierarchy)]
      self.syncMissingEntries(mode, callback)
    return reports


  def syncDocTypes(self) -> None:
    """ Synchronize document types between client and server
    - save datahierarchy to server
    """
    #try body and metadata: compare, write
    docTypesElab  = {i['title']:i['id'] for i in self.api.readEntry('items_types')}
    docTypesPasta = {i.capitalize() for i in self.backend.db.dataHierarchy('','') if not i.startswith('x')} | \
                    {'Default','Folder','Project','ProjectGroup'}
    for docType in docTypesPasta.difference({'Measurement'}|docTypesElab.keys()):  # do not create measurements, use 'experiments'
      self.api.touchEntry('items_types', {'title': docType})
    #verify nothing extraneous
    docTypesElab  = {i['title']:i['id'] for i in self.api.readEntry('items_types')}
    if set(docTypesElab.keys()).difference(docTypesPasta|{'Default','ProjectGroup'}) and self.verbose:
      print('**Info: some items exist that should not:', set(docTypesElab.keys()).difference(docTypesPasta|{'Default'}),
            'You can remove manually, but should not interfere since not used.')
    # sync data-hierarchy
    dataHierarchy = []
    for docType in self.backend.db.dataHierarchy('',''):
      dataHierarchy += copy.deepcopy([dict(i) for i in self.backend.db.dataHierarchy(docType,'meta')])
    self.api.updateEntry('items', self.elabProjGroupID, {'metadata':json.dumps(dataHierarchy)})
    return


  def createIdDict(self) -> None:
    """ create mapping of docIDs to elabIDs: if not exist, create elabIds """
    configRemote = self.backend.configuration['projectGroups'][self.backend.configurationProjectGroup]['remote']['config']
    elabTypes = {i['title'].lower():i['id'] for i in self.api.readEntry('items_types')}  |  {'measurement':-1}
    elabTypes |= {'x0':elabTypes.pop('project'), 'x1':elabTypes.pop('folder'), '-':elabTypes.pop('default')}
    def getNewEntry(elabType:str) -> int:
      urlSuffix = 'items'                  if int(elabType)>0 else 'experiments'
      content   = {'category_id':elabType, 'canwrite':configRemote['canWrite'], 'canread':configRemote['canRead']}
      elabID    = self.api.touchEntry(urlSuffix, content)
      self.api.createLink(urlSuffix, elabID, 'items', self.elabProjGroupID)
      return elabID
    self.backend.db.cursor.execute('SELECT id, type, externalId FROM main')
    self.docID2elabID = {i[0]:((i[2],i[1].split('/')[0]=='measurement') if i[2] else (getNewEntry(elabTypes[i[1].split('/')[0]]),i[1].split('/')[0]=='measurement'))
                    for i in self.backend.db.cursor.fetchall()}
    if self.verbose:
      print('List of docIDs and corresponding elabIDs (flag if experiment)')
      print('\n'.join([f'{k} : {v}' for k,v in self.docID2elabID.items()]))
    # save to sqlite
    self.backend.db.cursor.executemany('UPDATE main SET id=?, externalId=? WHERE id=?', [(k,v[0],k) for k, v in self.docID2elabID.items()])
    self.backend.db.connection.commit()
    return


  def updateEntry(self, node:Node, mode:str, callback:Callable[[ElabFTWApi,str,int],str]=cliCallback) -> tuple[str,int]:
    """ update an entry in elabFTW: all the logic goes here
        - myDesktop: sends content and the date when upload is made; if there is a change in modified time; the change is for real
        - server: gets document; if there is a difference between metadata.json and content: it was changed for real
        - other desktops changes: as before; my desktop **cannot differentiate myChanges vs other desktop changes**
          -> have to save also upload time locally, save in extra column

    Args:
      node (Node): node to process
      mode (str): sync mode g=get, gA=get-all, s=send, sA=send-all
      callback (func): callback function if non-all mode is given

    Returns:
      tuple: node.id; merge case
    """
    # get this content: check if it changed
    mergeCase = -1
    docClient   = self.backend.db.getDoc(node.id)
    if 'dateSync' not in docClient or not docClient['dateSync']:
      docClient['dateSync'] = datetime.fromisoformat('2000-01-03').isoformat()+'.0000'
    if self.verbose:
      print(f'\n{node.id}\n>>>DOC_CLIENT sync&modified', docClient['dateSync'], docClient['dateModified'])
    # pull from server: content and other's client content
    entryType = 'experiments' if self.docID2elabID[node.id][1] else 'items'
    docServer, uploads = self.elab2doc(self.api.readEntry(entryType, self.docID2elabID[node.id][0])[0])
    if self.verbose:
      print('>>>DOC_SERVER', docServer)
    if [i for i in uploads if i['real_name']=='do_not_change.json']:
      docOther = self.api.download(entryType, self.docID2elabID[node.id][0],
                                   [i for i in uploads if i['real_name']=='do_not_change.json'][0])
    else:
      docOther = {'name':'Untitled', 'tags':[], 'comment':'', 'dateSync':datetime.fromisoformat('2000-01-02').isoformat()+'.0000',
                  'dateModified':datetime.fromisoformat('2000-01-01').isoformat()+'.0000'}
    if self.verbose:
      print('>>>DOC_OTHER sync&modified', docOther.get('dateSync'), docOther.get('dateModified'))
    docMerged:dict[str,Any] = {}
    flagUpdateClient, flagUpdateServer = False, False
    # merge 1: compare server content and docOther and update later with changes
    flagServerChange = False
    for k,v in docServer.items():
      if isinstance(v, str):
        if v.strip() != docOther[k].strip():
          flagServerChange = True
          if self.verbose:
            print(f'str change k:{k}; v:{v}; vOther:{docOther[k]}|type:{type(v)}')
          docOther[k] = docServer[k]
      elif isinstance(v, dict):
        if v != docOther[k]:
          flagServerChange = True
          if self.verbose:
            print(f'dict change k:{k}; v:{v}; vOther:{docOther[k]}|type:{type(v)}')
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

    # merge 2: compare server client
    pattern = '%Y-%m-%dT%H:%M:%S.%f'
    mergeCase = -1
    #  - Case 1 straight update from client to server: only client updated and server not changed
    if datetime.strptime(docClient['dateModified'], pattern) >  datetime.strptime(docClient['dateSync'], pattern) and \
       datetime.strptime(docOther['dateModified'], pattern)  <= datetime.strptime(docOther['dateSync'], pattern) and  \
       not mode.startswith('g'):
      mergeCase = 1
      if self.verbose:
        print(f'** MERGE CASE {MERGE_LABELS[mergeCase]}')
      flagUpdateServer = True
      flagUpdateClient = False
      docMerged = copy.deepcopy(docClient)
    #  - Case 2 straight update from server to client: only others was updated / server itself was not updated, client not changed
    if datetime.strptime(docClient['dateModified'], pattern) < datetime.strptime(docClient['dateSync'], pattern) and \
         datetime.strptime(docOther['dateModified'], pattern) < datetime.strptime(docOther['dateSync'], pattern) and \
         datetime.strptime(docOther['dateSync'], pattern)     < datetime.strptime(docOther['dateSync'], pattern) and \
         not mode.startswith('s'):
      mergeCase = 2
      if self.verbose:
        print(f'** MERGE CASE {MERGE_LABELS[mergeCase]}')
      flagUpdateServer = False
      flagUpdateClient = True
      docMerged = copy.deepcopy(docOther)
    #  - Case 3 straight update from server to client: only server updated, client not changed
    if datetime.strptime(docClient['dateModified'], pattern) <= datetime.strptime(docClient['dateSync'], pattern) and \
         datetime.strptime(docOther['dateModified'], pattern) > datetime.strptime(docOther['dateSync'], pattern)  and \
         not mode.startswith('s'):
      mergeCase = 3
      if self.verbose:
        print(f'** MERGE CASE {MERGE_LABELS[mergeCase]}')
      flagUpdateServer = True
      flagUpdateClient = True
      docMerged = copy.deepcopy(docOther)
    #  - Case 4 no change: nothing changed
    if datetime.strptime(docClient['dateModified'], pattern) <= datetime.strptime(docClient['dateSync'], pattern) and \
         datetime.strptime(docOther['dateModified'], pattern) <= datetime.strptime(docOther['dateSync'], pattern):
      mergeCase = 4
      if self.verbose:
        print(f'** MERGE CASE {MERGE_LABELS[mergeCase]}')
      # flagUpdateServer = False
      # flagUpdateClient = False
      # docMerged = {}
      return node.id, mergeCase
    #  - Case 5 both are updated: merge: both changed -> GUI
    if datetime.strptime(docClient['dateModified'], pattern) > datetime.strptime(docClient['dateSync'], pattern) and \
       datetime.strptime(docOther['dateModified'], pattern) > datetime.strptime(docOther['dateSync'], pattern):
      mergeCase = 5
      if self.verbose:
        print(f'** MERGE CASE {MERGE_LABELS[mergeCase]}')
      flagUpdateServer = True
      flagUpdateClient = False
      docMerged = copy.deepcopy(docClient)
    if mergeCase<=0:
      print(f'**No clear merge case: should not occur, {mode}')
      return node.id, -1

    docMerged['dateSync'] = datetime.now().isoformat()
    if self.verbose:
      print('>>>MERGE TIME', docMerged['dateSync'])
    # update client
    if flagUpdateClient:
      docUpdate = copy.deepcopy(docMerged)
      docUpdate['branch'] = docUpdate['branch'][0] | {'op':''}
      docUpdate['dateModified'] = docUpdate['dateSync']
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
      self.api.updateEntry(entryType, self.docID2elabID[node.id][0], content)
      # create links
      _ = [self.api.createLink(entryType, self.docID2elabID[node.id][0], 'experiments' if self.docID2elabID[node.id][1] else 'items', self.docID2elabID[i.id][0])
                              for i in node.children]
    # uploads| clean first, then upload: PASTAs document, thumbnail, data-file
    existingUploads = self.api.readEntry(entryType, self.docID2elabID[node.id][0])[0]['uploads']
    uploadsToDelete = {'do_not_change.json', 'metadata.json'}
    if flagUpdateServer:
      uploadsToDelete |= {'thumbnail.svg', 'thumbnail.png', 'thumbnail.jpg'}
    for upload in existingUploads:
      if upload['real_name'] in uploadsToDelete:
        self.api.uploadDelete(entryType, self.docID2elabID[node.id][0], upload['id'])
    self.api.upload(entryType, self.docID2elabID[node.id][0], jsonContent=json.dumps(docMerged))
    if flagUpdateServer:
      if image:
        self.api.upload(entryType, self.docID2elabID[node.id][0], image)
      if docMerged['branch'][0]['path'] is not None and docMerged['type'][0][0]!='x' \
            and not docMerged['branch'][0]['path'].startswith('http') and \
            (self.backend.basePath/docMerged['branch'][0]['path']).name not in {i['real_name'] for i in existingUploads}:
        self.api.upload(entryType, self.docID2elabID[node.id][0], fileName=self.backend.basePath/docMerged['branch'][0]['path'], comment='raw data')
    return node.id, mergeCase


  def syncMissingEntries(self, mode:str='', callback:Callable[[ElabFTWApi,str,int],str]=cliCallback) -> bool:
    """
    Compare information on server and client and delete those on server, that are not on client (because they were deleted there)

    Args:
      mode (str): sync mode g=get, gA=get-all, s=send, sA=send-all
      callback (func): callback function if non-all mode is given

    Returns:
    bool: true=equal; false=differences
    """
    agreement = True
    self.backend.db.cursor.execute('SELECT type, externalId FROM main')
    dataLocal = self.backend.db.cursor.fetchall()
    inPasta = {'experiments': {int(i[1]) for i in dataLocal if i[0].startswith('measurement')},
               'items':       {int(i[1]) for i in dataLocal if not i[0].startswith('measurement')} }
    data = self.api.readEntry('items', self.elabProjGroupID)[0]
    inELAB  = {'experiments': {i['entityid'] for i in data['related_experiments_links']},
               'items':       {i['entityid'] for i in data['related_items_links']} }
    for entryType in ['experiments','items']:
      if diff := inPasta[entryType].difference(inELAB[entryType]):
        agreement = False
        print(f'**ERROR** There is a difference in {entryType} between CLIENT and SERVER. Ids on server: {diff}.')
      if diff := inELAB[entryType].difference(inPasta[entryType]):
        if self.verbose:
          print(f'**INFO** There is a difference in {entryType} between SERVER and CLIENT. Ids on server: {diff}.')
          for idx in diff:
            mode = mode if mode.endswith('A') else callback(self.api, entryType, idx)
            if mode.startswith('s'):
              self.api.deleteEntry(entryType, idx)
            elif mode.startswith('g'):
              _, uploads = self.elab2doc(self.api.readEntry(entryType, idx)[0])
              if listDoNotChange := [i for i in uploads if i['real_name']=='do_not_change.json']:
                docOther = self.api.download(entryType, idx, listDoNotChange[0])
                docOther['dateSync'] = datetime.now().isoformat()
                squashTupleIntoValue(docOther)
                docOther = flatten(docOther, keepPastaStruct=True)                       #type: ignore[assignment]
                try:
                  self.backend.addData('/'.join(docOther['type']), docOther, docOther['branch'][0]['stack'])
                except:
                  docOther.pop('image','')
                  print(f'**ERROR** Tried to add to client elab:{entryType} {idx}: {json.dumps(docOther,indent=2)}')
    return agreement


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
    elab = {'body':body, 'title':title, 'metadata':json.dumps(metadata), 'tags':tags, 'created_at':created_at, 'modified_at':modified_at}
    return elab, image
