""" Allow syncing to elabFTW server """
import copy
import json
import logging
import re
import traceback
from collections import Counter
from datetime import datetime
from typing import Any, Callable
from anytree import Node, PreOrderIter
from .backend import Backend
from .elabFTWapi import ElabFTWApi
from .textTools.handleDictionaries import squashTupleIntoValue
from .miscTools import flatten
from .textTools.html2markdown import html2markdown
from .textTools.markdown2html import markdown2html

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
    configuration = self.backend.configuration
    self.projectGroup = projectGroup or configuration['defaultProjectGroup']
    if not configuration['projectGroups'][self.projectGroup]['remote']['url'] or \
       not configuration['projectGroups'][self.projectGroup]['remote']['key'] or \
       'config' not in configuration['projectGroups'][self.projectGroup]['remote'] or \
       'id' not in configuration['projectGroups'][self.projectGroup]['remote']['config']:
      return
    self.api = ElabFTWApi(configuration['projectGroups'][self.projectGroup]['remote']['url'],
                          configuration['projectGroups'][self.projectGroup]['remote']['key'])
    configRemote = configuration['projectGroups'][self.projectGroup]['remote']
    self.elabProjGroupID = configRemote['config']['id']
    if purge:
      data = self.api.readEntry('items', self.elabProjGroupID)[0]
      _ = [self.api.deleteEntry('experiments', i['entityid']) for i in data['related_experiments_links']]
      _ = [self.api.deleteEntry('items',       i['entityid']) for i in data['related_items_links']]
    self.docID2elabID:dict[str,tuple[int,bool]] = {}  # x-15343154th54325243, (4, bool if experiment)
    self.readWriteAccess:dict[str,str] = {}
    self.verbose         = False
    return


  def sync(self, mode:str='', callback:Callable[[ElabFTWApi,str,int],str]=cliCallback,
           progressCallback:Callable[...,None]|None=None) -> list[tuple[str,int]]:
    """ Main function

    Args:
      mode (str): sync mode g=get, gA=get-all, s=send, sA=send-all
      callback (func): callback function if non-all mode is given
      progressCallback (func): callback function to implement progress-bar

    Returns:
      list: list of merge cases
    """
    def updateEntryLocal(i:Node, mode:str, callback:Callable[[ElabFTWApi,str,int],str]=cliCallback,
                         idx:int=-1, count:int=-1) -> tuple[str,int]:
      """Intermediate function used in list comprehension"""
      res = self.updateEntry(i, mode, callback)
      if progressCallback is not None:
        progressCallback('count', str(int(idx/count*100)))
      return res

    if hasattr(self,'api') and self.api.url:  #only when you are connected to web
      report = []
      if progressCallback is not None:
        progressCallback('text', '### Start syncing with elabFTW server\n#### Set up sync\nStart...')
      self.syncDocTypes()  # sync categories ~1sec
      self.createIdDict()  # TODO: get progressCallback as argument
      if progressCallback is not None:
        progressCallback('append', 'Done\n#### Sync each document\nStart...')
      for projID in self.backend.db.getView('viewDocType/x0')['id'].values:
        projHierarchy, _ = self.backend.db.getHierarchy(projID)
        count = len(list(PreOrderIter(projHierarchy)))
        report += [updateEntryLocal(i, mode, callback, idx, count) for idx, i in enumerate(PreOrderIter(projHierarchy))]
      if progressCallback is not None:
        progressCallback('append', 'Done\n#### Sync missing entries\nStart...')
      report += self.syncMissingEntries(mode, callback, progressCallback)
    else:
      print('**ERROR Not connected to elab server!')
      return []
    if progressCallback is not None:
      reportSum = Counter([i[1] for i in report])
      reportText = '\n  - '.join(['']+[f'{v:>4}:{MERGE_LABELS[k][2:]}' for k,v in reportSum.items()])
      progressCallback('count', '100')
      progressCallback('append', f'Done\n#### Summary\nSend all data to server: success\n{reportText}')
    return report


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
    configRemote = self.backend.configuration['projectGroups'][self.projectGroup]['remote']['config']
    # set default read/write access rules
    self.readWriteAccess =  {'canwrite':configRemote['canWrite'], 'canread':configRemote['canRead']}
    elabTypes = {i['title'].lower():i['id'] for i in self.api.readEntry('items_types')}  |  {'measurement':-1}
    elabTypes |= {'x0':elabTypes.pop('project'), 'x1':elabTypes.pop('folder'), '-':elabTypes.pop('default')}
    def getNewEntry(elabType:str) -> int:
      urlSuffix = 'items'                  if int(elabType)>0 else 'experiments'
      content   = {'category_id':elabType} | self.readWriteAccess
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
    docClient   = self.backend.db.getDoc(node.id)
    elabID = self.docID2elabID[node.id][0]
    if 'dateSync' not in docClient or not docClient['dateSync']:
      docClient['dateSync'] = datetime.fromisoformat('2000-01-03').isoformat()+'.0000'
    if self.verbose:
      print(f'\n{node.id}\n>>>DOC_CLIENT sync&modified', docClient['dateSync'], docClient['dateModified'])
    # pull from server: content and other's client content
    entryType = 'experiments' if self.docID2elabID[node.id][1] else 'items'
    docServer, uploads = self.elab2doc(self.api.readEntry(entryType, elabID)[0])
    if self.verbose:
      print('>>>DOC_SERVER', docServer)
    if listDoNotChange :=[i for i in uploads if i['real_name']=='do_not_change.json']:
      docOther = self.api.download(entryType, elabID, listDoNotChange[0])
    else:
      docOther = {'name':'Untitled', 'tags':[], 'comment':'', 'dateSync':datetime.fromisoformat('2000-01-02').isoformat()+'.0000',
                  'dateModified':datetime.fromisoformat('2000-01-01').isoformat()+'.0000'}
      # return(node.id, -1)
    if self.verbose:
      print('>>>DOC_OTHER sync&modified', docOther.get('dateSync'), docOther.get('dateModified'))
    docMerged:dict[str,Any] = {}
    flagUpdateClient, flagUpdateServer = False, False

    # merge 1: compare server content and docOther and update later with changes
    flagServerChange = False
    for k,v in docServer.items():
      if isinstance(v, str):
        if v != html2markdown(markdown2html(docOther[k])):
          flagServerChange = True
          if self.verbose:
            print(f'str change k:{k}; v:\n|{v}|\nvOther:\n|{docOther[k]}|\n|{html2markdown(markdown2html(docOther[k]))}|\ntype:{type(v)}')
          docOther[k] = docServer[k]
      elif isinstance(v, dict):
        if v != docOther[k]:
          flagServerChange = True
          if self.verbose:
            print(f'dict change k:{k}; v:{v}; vOther:{docOther[k]}|type:{type(v)}')
          docOther[k] = docServer[k]
      elif isinstance(v, list):
        if set(v) != {i for i in docOther[k] if not re.match(r'^_\d$', i)}:
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
    if (datetime.strptime(docClient['dateModified'], pattern) >  datetime.strptime(docClient['dateSync'], pattern) and \
        datetime.strptime(docOther['dateModified'], pattern)  <= datetime.strptime(docOther['dateSync'], pattern) and  \
        not mode.startswith('g'))     or     mode=='sA':
      mergeCase = 1
      if self.verbose:
        print(f'** MERGE CASE {MERGE_LABELS[mergeCase]}')
      flagUpdateServer = True
      flagUpdateClient = False
      docMerged = copy.deepcopy(docClient)
    #  - Case 2 straight update from server to client: only others was updated / server itself was not updated, client not changed
    if (datetime.strptime(docClient['dateModified'], pattern) <= datetime.strptime(docClient['dateSync'], pattern) and \
        datetime.strptime(docOther['dateModified'], pattern)  >  datetime.strptime(docOther['dateSync'], pattern) and \
        not mode.startswith('s'))     or     mode=='gA':
      mergeCase = 2
      if self.verbose:
        print(f'** MERGE CASE {MERGE_LABELS[mergeCase]}')
      flagUpdateServer = False
      flagUpdateClient = True
      docMerged = copy.deepcopy(docOther)
    #  - Case 3 straight update from server to client: only server updated, client not changed
    if datetime.strptime(docClient['dateModified'], pattern) <= datetime.strptime(docClient['dateSync'], pattern) and \
       datetime.strptime(docOther['dateModified'], pattern)  >  datetime.strptime(docOther['dateSync'], pattern) and \
       flagServerChange and not mode.startswith('s'):
      mergeCase = 3
      if self.verbose:
        print(f'** MERGE CASE {MERGE_LABELS[mergeCase]}')
      flagUpdateServer = True
      flagUpdateClient = True
      docMerged = copy.deepcopy(docOther)
    #  - Case 4 no change: nothing changed
    if datetime.strptime(docClient['dateModified'], pattern) <= datetime.strptime(docClient['dateSync'], pattern) and \
       datetime.strptime(docOther['dateModified'], pattern)  <= datetime.strptime(docOther['dateSync'], pattern) and \
          not mode.endswith('A'):
      mergeCase = 4
      if self.verbose:
        print(f'** MERGE CASE {MERGE_LABELS[mergeCase]}')
      # flagUpdateServer = False
      # flagUpdateClient = False
      # docMerged = {}
      return node.id, mergeCase
    #  - Case 5 both are updated: merge: both changed -> GUI
    if datetime.strptime(docClient['dateModified'], pattern) > datetime.strptime(docClient['dateSync'], pattern) and \
       datetime.strptime(docOther['dateModified'], pattern)  > datetime.strptime(docOther['dateSync'], pattern):
      mergeCase = 5
      if self.verbose:
        print(f'** MERGE CASE {MERGE_LABELS[mergeCase]}')
      flagUpdateServer = True
      flagUpdateClient = False
      docMerged = copy.deepcopy(docClient)
    if mergeCase<=0:
      print(f'**ERROR** No merge case set! {mode}')
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
    # send doc (merged version) to server
    if flagUpdateServer:
      content, image = self.doc2elab(copy.deepcopy(docMerged))
      success = self.api.updateEntry(entryType, elabID, content|self.readWriteAccess)
      if not success:
        logging.error('Could not sync data %s, %s  %s',entryType, elabID, json.dumps(content|self.readWriteAccess, indent=2))
        return node.id, -1
      # create links
      _ = [self.api.createLink(entryType, elabID,
                               'experiments' if self.docID2elabID[i.id][1] else 'items', self.docID2elabID[i.id][0])
                               for i in node.children]
    # uploads| clean first, then upload: PASTAs document, thumbnail, data-file
    existingUploads = self.api.readEntry(entryType, elabID)[0]['uploads']
    uploadsToDelete = {'do_not_change.json', 'metadata.json'}
    if flagUpdateServer:
      uploadsToDelete |= {'thumbnail.svg', 'thumbnail.png', 'thumbnail.jpg'}
    for upload in existingUploads:
      if upload['real_name'] in uploadsToDelete:
        self.api.uploadDelete(entryType, elabID, upload['id'])
    self.api.upload(entryType, elabID, jsonContent=json.dumps(docMerged))
    if flagUpdateServer:
      if image:
        self.api.upload(entryType, elabID, image)
      if docMerged['branch'][0]['path'] is not None and docMerged['type'][0][0]!='x' \
            and not docMerged['branch'][0]['path'].startswith('http') and \
            (self.backend.basePath/docMerged['branch'][0]['path']).name not in {i['real_name'] for i in existingUploads}:
        self.api.upload(entryType, elabID, fileName=self.backend.basePath/docMerged['branch'][0]['path'], comment='raw data')
    return node.id, mergeCase


  def syncMissingEntries(self, mode:str='', callback:Callable[[ElabFTWApi,str,int],str]=cliCallback,
                         progressCallback:Callable[...,None]|None=None) -> list[tuple[str,int]]:
    """
    Compare information on server and client and delete those on server, that are not on client (because they were deleted there)

    Args:
      mode (str): sync mode g=get, gA=get-all, s=send, sA=send-all
      callback (func): callback function if non-all mode is given
      progressCallback (func): callback function to allow to monitor the progress

    Returns:
      list: changes
    """
    report = []
    self.backend.db.cursor.execute('SELECT type, externalId FROM main')
    dataLocal = self.backend.db.cursor.fetchall()
    inPasta = {'experiments': {int(i[1]) for i in dataLocal if i[0].startswith('measurement')},
               'items':       {int(i[1]) for i in dataLocal if not i[0].startswith('measurement')} }
    data = self.api.readEntry('items', self.elabProjGroupID)[0]
    inELAB  = {'experiments': {i['entityid'] for i in data['related_experiments_links']},
               'items':       {i['entityid'] for i in data['related_items_links']} }
    for count0, entryType in enumerate(['experiments','items']):
      if diff := inPasta[entryType].difference(inELAB[entryType]):
        print(f'**ERROR** There is a difference in {entryType} between CLIENT and SERVER. Ids on server: {diff}.')
      if diff := inELAB[entryType].difference(inPasta[entryType]):
        if self.verbose:
          print(f'**INFO** There is a difference in {entryType} between SERVER and CLIENT. Ids on server: {diff}.')
        for count1, idx in enumerate(diff):
          if progressCallback is not None:
            progressCallback('count', str(round(count0*50+count1*50/len(diff))))
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
                branch = copy.deepcopy(docOther['branch'][0])
                # create folder
                if branch['path'] is not None:
                  if docOther['type'][0][0]=='x':
                    (self.backend.basePath/branch['path']).mkdir(parents=True, exist_ok=True)
                    with open(self.backend.basePath/branch['path']/'.id_pastaELN.json', 'w', encoding='utf-8') as fOut:
                      json.dump({'id':docOther['id']}, fOut)
                  else:
                    (self.backend.basePath/branch['path']).parent.mkdir(parents=True, exist_ok=True)
                docOther['branch'] = branch | {'op':'c'} #TODO: one remains only
                if 'tags' not in docOther:
                  docOther['tags'] = []
                self.backend.db.saveDoc(docOther)
                # save datafile if exists
                if listFile := [i for i in uploads if i['real_name']!='do_not_change.json' and \
                                not i['real_name'].startswith('thumbnail.')]:
                  data = self.api.download(listFile[0]['type'], idx, listFile[0])
                  with open(self.backend.basePath/branch['path'], 'wb') as fOut:
                    fOut.write(data['data'])
                report.append((docOther['id'], 2))
              except Exception:
                docOther.pop('image','')
                for k in list(docOther.keys()):
                  if k.startswith('metaVendor.'):
                    docOther.pop(k,'')
                print(f'**ERROR** Tried to add to client elab:{entryType} {idx}: {json.dumps(docOther,indent=2)}')
                print(traceback.format_exc())
                report.append((docOther['id'], -1))
    return report


  def elab2doc(self,elab:dict[str,Any]) -> tuple[dict[str,Any], list[Any]]:
    """ Convert an elabFTW dict-html entry into a PASTA doc

    Args:
      elab (dict): elabFTW entry

    Returns:
      dict: PASTA doc
    """
    # print(json.dumps(elab, indent=2))
    comment = html2markdown(elab.get('body','')).strip()
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
    body      = markdown2html(bodyMD)
    # created_at= doc.pop('dateCreated')
    # modified_at=doc.pop('dateModified')
    tags       =doc.pop('tags')
    ratings    = [i[1] for i in tags if i.startswith('_')]
    tags       = [i for i in tags if not re.match(r'^_\d$', i)]
    doc        = {k:v for k,v in doc.items() if k not in {'id','user','client','externalId','type','gui','branch','shasum','qrCodes'}}
    metadata = {'metaVendor': doc.pop('metaVendor') if 'metaVendor' in doc else {}}
    metadata['metaUser']    = doc.pop('metaUser')   if 'metaUser' in doc else {}
    if doc:
      doc.pop('dateSync')
      metadata |= {'__':doc}
    elab = {'body':body, 'title':title, 'metadata':json.dumps(metadata), 'tags':tags,
            # 'created_at':created_at, 'modified_at':modified_at,
            'rating': ratings[0] if ratings else '0'}
    return elab, image
