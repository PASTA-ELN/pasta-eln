""" Backend worker thread for separating GUI and backend operations
CONNECT TO ALL THESE SIGNALS IN COMMUNICATE and UI
"""
import json
import logging
import shutil
import tempfile
import time
from collections import Counter
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional
import pandas as pd
from anytree import Node
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QMessageBox
from ..miscTools import flatten
from ..textTools.stringChanges import createDirName
from .backend import Backend
from .dataverse import DataverseClient
from .elabFTWsync import MERGE_LABELS, Pasta2Elab
from .inputOutput import exportELN, importELN
from .zenodo import ZenodoClient

waitTimeBeforeSendingFirstMessage = 0.1 #ensure all UI elements are up

class Task(Enum):
  """ Tasks that can be used in BackendWorker """
  ADD_DOC        = (1 , '')                                        #keys: hierStack, docType, doc
  EDIT_DOC       = (2 , '')                                        #keys: doc, newProjID
  MOVE_LEAVES    = (3 , '')                                        #keys: docID, stackOld, stackNew, childOld, childNew
  DROP_EXTERNAL  = (4 , 'Including drag&drop files and folders:')  #keys: docID, items
  HIDE_SHOW      = (5 , '')                                        #keys: docID
  SET_GUI        = (6 , '')                                        #keys: docID, gui
  DELETE_DOC     = (7 , '')                                        #keys: docID
  SCAN           = (8 , 'Scanning disk for new data:')             #keys: docID
  SEND_TBL_COLUMN= (9 , '')                                        #keys: docType, newList
  EXTRACTOR_TEST = (10, 'Testing extractor:')                      #keys: fileName, style, recipe, saveFig
  EXTRACTOR_RERUN= (11, 'Rerun extractors:')                       #keys: docIDs, recipe
  SEND_ELAB      = (12, 'Sending data to elabFTW server:')         #keys: projGroup
  GET_ELAB       = (13, 'Getting data from elabFTW server:')       #keys: projGroup
  SMART_ELAB     = (14, 'Syncing with elabFTW server:')            #keys: projGroup
  EXPORT_ELN     = (15, 'Exporting to .eln:')                      #keys: fileName, projID, docTypes
  IMPORT_ELN     = (16, 'Importing an .eln file:')                 #keys: fileName, projID
  SEND_REPOSITORY= (17, 'Sending data to repository:')             #keys: projID, docTypes,repositories,metadata,uploadZenodo
  CHECK_DB       = (18, 'Checking database integrity:')            #keys: style
  OPEN_EXTERNAL  = (19, '')                                        #keys: docID

  def __init__(self, num:int, msgWaitDialog:str='') -> None:
    """ Initialize the task with a number and an optional message for the wait dialog
    Args:
      num (int): Task number
      msgWaitDialog (str): Message to show in the wait dialog
    """
    self.msgWaitDialog = msgWaitDialog


class BackendWorker(QObject):
  """
  Backend worker that runs in a separate thread to handle all backend operations
  """
  # Signals to send data back to GUI
  beSendDocTypes          = Signal(dict)           # Send processed data back
  beSendDataHierarchyNode = Signal(str,list)       # Send data hierarchy nodes
  beSendDataHierarchyAll  = Signal(list)           # Send all entries for this docType
  beSendTable             = Signal(pd.DataFrame, str)   # all tables
  beSendHierarchy         = Signal(Node, dict)
  beSendDoc               = Signal(dict)
  beSendTaskReport        = Signal(Task, str, str, str)       # task, report, image, path
  beSendSQL               = Signal(str, pd.DataFrame)

  def __init__(self) -> None:
    """ Initialize the backend worker """
    super().__init__()
    self.backend: Optional[Backend] = None


  @Slot(dict,str)
  def initialize(self, configuration:dict[str,Any], projectGroupName:str) -> None:
    """ Initialize the backend worker with the given configuration
    Args:
      configuration (dict): Configuration dictionary with database and other settings
      projectGroupName (str): Name of the project group to initialize
    """
    self.backend = Backend(configuration, projectGroupName)
    docTypesTitlesIcons = {k:{'title':v} for k,v in self.backend.db.dataHierarchy('','title')}
    for k,v in self.backend.db.dataHierarchy('','icon'):
      docTypesTitlesIcons[k]['icon'] = v
    for k,v in self.backend.db.dataHierarchy('','shortcut'):
      docTypesTitlesIcons[k]['shortcut'] = v
    time.sleep(waitTimeBeforeSendingFirstMessage)
    self.beSendDocTypes.emit(docTypesTitlesIcons)
    for docType in docTypesTitlesIcons:
      self.beSendDataHierarchyNode.emit(docType, self.backend.db.dataHierarchy(docType, 'meta'))

  @Slot(str)
  def returnDataHierarchyRow(self, docType:str) -> None:
    """ Return a data hierarchy row for the given docType
    Args:
      docType (str): Document type to return data hierarchy for
    """
    if self.backend is not None:
      self.beSendDataHierarchyAll.emit(self.backend.db.dataHierarchy(docType, '*'))


  @Slot(str, str, bool)
  def returnTable(self, docType:str, projID:str, showAll:bool) -> None:
    """ Return a view from the database
    Args:
      docType (str): Document type to return
      projID (str): Project ID to get the view for
      showAll (bool): Whether to return all items or only the non-hidden ones"""
    if docType and self.backend is not None:
      if docType=='_tags_':
        path = 'viewIdentify/viewTags'
      else:
        path = f'viewDocType/{docType}'
      path += 'All' if showAll else ''
      logging.debug('returnTable %s %s %s %s', docType, projID, showAll, path)
      data = self.backend.db.getView(path, startKey=projID)
      self.beSendTable.emit(data, docType)


  @Slot(str, bool)
  def returnHierarchy(self, projID:str, showAll:bool) -> None:
    """ Return a hierarchy
    Args:
      projID (str): Project ID to get the hierarchy for
      showAll (bool): Whether to return all items or only the non-hidden ones
    """
    if self.backend is not None and projID:#TODO: during test_13 for some reason the projID is empty, not sure why
      hierarchy, error = self.backend.db.getHierarchy(projID, allItems=showAll)
      if error:
        hierarchy = Node('__ERROR_in_getHierarchy__')
      projDoc = self.backend.db.getDoc(projID)
      logging.debug('returnHierarchy %s %s %s', hierarchy, projID, showAll)
      self.beSendHierarchy.emit(hierarchy, projDoc)


  @Slot(str, str)
  def returnDoc(self, docID:str) -> None:
    """ Return a document from the database
    Args:
      docID (str): ID of the document to return
      """
    if self.backend is not None:
      self.beSendDoc.emit(self.backend.db.getDoc(docID))


  @Slot(Task, dict)
  def returnTaskReport(self, task:Task, data:dict[str,Any]) -> None:
    """ Handle a rather complicated task request from the GUI and possibly return a report
    Args:
      task (Task): Task to perform
      data (dict): Data required for the task
    """
    if self.backend is None:
      return
    if task is Task.EXTRACTOR_TEST and set(data.keys())=={'fileName','style','recipe','saveFig'}:
      report, image = self.backend.testExtractor(data['fileName'], style={'main':data['recipe']},
                                                 outputStyle=data['style'], saveFig=data['saveFig'])
      self.beSendTaskReport.emit(task, report, image, '')

    elif task is Task.CHECK_DB and set(data.keys())=={'style'}:
      report = self.backend.checkDB(outputStyle=data['style'])
      self.beSendTaskReport.emit(task, report, '', '')

    elif task is Task.SCAN         and set(data.keys())=={'docID'}:
      for _ in range(2):                                                         #scan twice: convert, extract
        self.backend.scanProject(None, data['docID'])
      self.beSendTaskReport.emit(task, 'Scanning finished successfully', '', '')

    elif task is Task.ADD_DOC      and set(data.keys())=={'hierStack','docType','doc'}:
      if data['hierStack']:
        parentID  = data['hierStack'][-1]
        self.backend.cwd = Path(self.backend.db.getDoc(parentID)['branch'][0]['path'])
      else:                                                                                          # project
        self.backend.cwd = Path(self.backend.basePath)
      if '_projectID' in data['doc']:
        del data['doc']['_projectID']
      self.backend.addData(data['docType'], data['doc'], data['hierStack'])
      self.beSendDoc.emit(data['doc'])                                          # send updated doc back to GUI
      if data['docType']=='x0':
        self.beSendTable.emit(self.backend.db.getView('viewDocType/x0'), 'x0')


    elif task is Task.EDIT_DOC      and set(data.keys())=={'doc','newProjID'}:
      # update the path, if the project changed
      if data['newProjID'] and 'branch' in data['doc'] and len(data['doc']['branch'][0]['stack'])>0 and \
         data['doc']['branch'][0]['stack'][0]!=data['newProjID'][0]:                  #only if project changed
        if data['doc']['branch'][0]['path'] is None:
          newPath    = ''
        else:
          oldPath = self.backend.basePath/data['doc']['branch'][0]['path']
          parentPath = self.backend.db.getDoc(data['newProjID'][0])['branch'][0]['path']
          newPath = f'{parentPath}/{oldPath.name}'
        data['doc']['branch'][0] = {'stack':[] if data['newProjID'][0]=='NONE' else [data['newProjID'][0]],
                                    'path':newPath or None, 'child':9999, 'show':[True,True]}
      # update the doc in the database
      doc = self.backend.db.getDoc(data['doc']['id'])
      if '_projectID' in data['doc']:
        del data['doc']['_projectID']
      doc.update(data['doc'])
      doc = flatten(doc, True)                                                      # type: ignore[assignment]
      self.backend.editData(doc)
      self.beSendDoc.emit(self.backend.db.getDoc(data['doc']['id']))            # send updated doc back to GUI

    elif task is Task.MOVE_LEAVES and set(data.keys())=={'docID','stackOld','stackNew','childOld','childNew'}:
      verbose = False                                                                 # Convenient for testing
      doc      = self.backend.db.getDoc(data['docID'])
      branchOldList= [i for i in doc['branch'] if i['stack']==data['stackOld']]
      if len(branchOldList)!=1:
        logging.error('Cannot move leaves: %s has no branch with stack %s', doc['id'], data['stackOld'], exc_info=True)
        return
      branchOld = branchOldList[0]
      if branchOld['path'] is not None and not branchOld['path'].startswith('http'):
        parentDir = Path(self.backend.db.getDoc(data['stackNew'][-1])['branch'][0]['path'])
        if doc['type'][0][0]=='x':
          dirNameNew= createDirName(doc, data['childNew'], parentDir)# create path name: do not create directory on disk yet
        else:
          dirNameNew= Path(branchOld['path']).name                                              # use old name
        pathNew = f'{parentDir}/{dirNameNew}'
      else:
        pathNew = branchOld['path']
      siblingsNew = self.backend.db.getView('viewHierarchy/viewHierarchy', startKey='/'.join(data['stackNew']))#sorted by docID
      siblingsNew = [i for i in siblingsNew if len(i['key'].split('/'))==len(data['stackNew'])+1]
      childNums   = [f"{i['value'][0]:05d}{i['id']}{idx}" for idx,i in enumerate(siblingsNew)]
      siblingsNew = [x for _, x in sorted(zip(childNums, siblingsNew))]  #sorted by childNum 1st and docID 2nd
      # --- CHANGE ----
      # change new siblings
      if verbose:
        print('\n=============================================\nStep 1: before new siblings')
        print('\n'.join([f'{i["value"][0]} {i["id"]} {i["value"][2]}' for i in siblingsNew]))
      for idx, line in reversed(list(enumerate(siblingsNew))):
        shift = 1 if idx>=data['childNew'] else 0#shift those before the insertion point by 0 and those after by 1
        if line['id']==data['docID'] or line['value'][0]==idx+shift:#ignore this id & those that are correct already
          continue
        if verbose:
          print(f'  {line["id"]}: move: {idx} {shift}')
        self.backend.db.updateBranch(docID=line['id'], branch=line['value'][4], child=idx+shift)
      if verbose:
        siblingsNew = self.backend.db.getView('viewHierarchy/viewHierarchy', startKey='/'.join(data['stackNew']))#sorted by docID
        siblingsNew = [i for i in siblingsNew if len(i['key'].split('/'))==len(data['stackNew'])+1]
        childNums   = [f"{i['value'][0]:05d}{i['id']}{idx}" for idx,i in enumerate(siblingsNew)]
        siblingsNew = [x for _, x in sorted(zip(childNums, siblingsNew))]#sorted by childNum 1st and docID 2nd
        print('Step 2: after new siblings')
        print('\n'.join([f'{i["value"][0]} {i["id"]} {i["value"][2]}' for i in siblingsNew]))
      # change item in question
      if verbose:
        print(f'  manual move {data["childOld"]} -> {data["childNew"]}: {data["docID"]}')
      self.backend.db.updateBranch(docID=data['docID'], branch=-99, stack=data['stackNew'], path=pathNew,
                                   child=data['childNew'], stackOld=data['stackOld']+[data['docID']])
      # change old siblings
      siblingsOld = self.backend.db.getView('viewHierarchy/viewHierarchy', startKey='/'.join(data['stackOld']))#sorted by docID
      siblingsOld = [i for i in siblingsOld if len(i['key'].split('/'))==len(data['stackOld'])+1]
      childNums   = [f"{i['value'][0]:05d}{i['id']}{idx}" for idx,i in enumerate(siblingsOld)]
      siblingsOld = [x for _, x in sorted(zip(childNums, siblingsOld))]#sorted by childNum 1st and docID 2nd
      if verbose:
        print('Step 3: before old siblings')
        print('\n'.join([f'{i["value"][0]} {i["id"]} {i["value"][2]}' for i in siblingsOld]))
      for idx, line in enumerate(siblingsOld):
        if line['value'][0]==idx:                  #ignore id in question and those that are correct already
          continue
        if verbose:
          print(f'  {line["id"]}: move: {idx}')
        self.backend.db.updateBranch(  docID=line['id'], branch=line['value'][4], child=idx)
      if verbose:
        siblingsOld = self.backend.db.getView('viewHierarchy/viewHierarchy', startKey='/'.join(data['stackOld']))#sorted by docID
        siblingsOld = [i for i in siblingsOld if len(i['key'].split('/'))==len(data['stackOld'])+1]
        childNums   = [f"{i['value'][0]:05d}{i['id']}{idx}" for idx,i in enumerate(siblingsOld)]
        siblingsOld = [x for _, x in sorted(zip(childNums, siblingsOld))]#sorted by childNum 1st and docID 2nd
        print('Step 4: end of function')
        print('\n'.join([f'{i["value"][0]} {i["id"]} {i["value"][2]}' for i in siblingsOld]))

    elif task is Task.DROP_EXTERNAL and set(data.keys())=={'docID','items'}:
      doc = self.backend.db.getDoc(data['docID'])
      targetFolder = Path(self.backend.basePath/doc['branch'][0]['path'])
      for item in data['items']:
        itemPath = Path(item)
        if itemPath.is_dir():
          shutil.copytree(itemPath, targetFolder/itemPath.name)
        else:
          shutil.copy(itemPath, targetFolder/itemPath.name)
      # scan
      for _ in range(2):                                                       #scan twice: convert, extract
        self.backend.scanProject(None, data['docID'], targetFolder.relative_to(self.backend.basePath))
      self.beSendTaskReport.emit(task, 'Drag-drop operation finished successfully', '', '')

    elif task is Task.DELETE_DOC   and  set(data.keys())=={'docID'}:
      # delete doc: possibly a folder or a project or a measurement
      # delete database and rename folder
      doc = self.backend.db.remove(data['docID'])
      if 'branch' in doc and len(doc['branch'])>0 and 'path' in doc['branch'][0]:
        oldPath = self.backend.basePath/doc['branch'][0]['path']
        newPath = oldPath.parent/f'trash_{oldPath.name}'
        nextIteration = 1
        while newPath.is_dir():
          newPath = oldPath.parent/f'trash_{oldPath.name}_{nextIteration}'
          nextIteration += 1
        if oldPath != newPath:
          oldPath.rename(newPath)
      # go through children, remove from DB
      children = self.backend.db.getView('viewHierarchy/viewHierarchy', startKey='/'.join(doc['branch'][0]['stack']+[data['docID']]))
      for docID in {line['id'] for line in children if line['id']!=data['docID']}:
        self.backend.db.remove(docID)
      # finish it
      if doc['type'][0]=='x0':
        self.beSendTable.emit(self.backend.db.getView('viewDocType/x0'), 'x0')

    elif task is Task.EXPORT_ELN and set(data.keys())=={'fileName','projID','docTypes'}:
      report = exportELN(self.backend, [data['projID']], data['fileName'], data['docTypes'])
      self.beSendTaskReport.emit(task, report, '', '')

    elif task is Task.IMPORT_ELN and set(data.keys())=={'fileName','projID'}:
      report, statistics = importELN(self.backend, data['fileName'], data['projID'])
      self.beSendTaskReport.emit(task, f'{report}\n{json.dumps(statistics,indent=2)}', '', '')

    elif task in (Task.SEND_ELAB, Task.GET_ELAB, Task.SMART_ELAB) and set(data.keys())=={'projGroup'}:
      if 'ERROR' in self.backend.checkDB(minimal=True):
        self.beSendTaskReport.emit(task, 'ERRORs are present in your database. Fix them before uploading', '', '')
      else:
        try:
          sync = Pasta2Elab(self.backend, data['projGroup'])
          if hasattr(sync, 'api') and sync.api.url:                             #if hostname and api-key given
            if task is Task.SEND_ELAB:
              stats = sync.sync('sA')
            elif task is Task.GET_ELAB:
              stats = sync.sync('gA')
            else:
              stats = sync.sync('')
            logging.debug('elabFTW sync stats: %s', stats)
            statsCount = Counter([i[1] for i in stats])
            msg = ', '.join([f'{MERGE_LABELS[k]}: {v}' for k,v in statsCount.items()])
            self.beSendTaskReport.emit(task, f'Success: Synchronized with server. Items per action: {msg}', '', '')
          else:                                                                                  #if not given
            self.beSendTaskReport.emit(task, 'ERROR: Please specify a server address and API-key in the Configuration', '', '')
        except ConnectionError as e:
          logging.error('Connection-Error connecting to elabFTW server')
          self.beSendTaskReport.emit(task, f'ERROR: Connection error to elabFTW server\n{e}', '', '')

    elif task is Task.SEND_TBL_COLUMN and set(data.keys())=={'docType','newList'}:
      self.backend.db.dataHierarchyChangeView(data['docType'], data['newList'])

    elif task is Task.SEND_REPOSITORY and set(data.keys())=={'projID','docTypes','repositories','metadata','uploadZenodo'}:
      tempELN = str(Path(tempfile.gettempdir())/'export.eln')
      res0 = exportELN(self.backend, [data['projID']], tempELN, data['docTypes'])
      print('Export eln',res0)
      repositories = data['repositories']
      if data['uploadZenodo']:                                                                       #Zenodo
        clientZ = ZenodoClient(repositories['zenodo']['url'], repositories['zenodo']['key'])
        metadataZ = clientZ.prepareMetadata(data['metadata'])
        res = clientZ.uploadRepository(metadataZ, tempELN)
      else:                                                                                       #Dataverse
        clientD = DataverseClient(repositories['dataverse']['url'], repositories['dataverse']['key'],
                                repositories['dataverse']['dataverse'])
        metadataD = clientD.prepareMetadata(data['metadata'])
        res = clientD.uploadRepository(metadataD, tempELN)
      msg = 'Successful upload to repository\n'
      # update project with upload details
      if res[0]:
        docProject = self.backend.db.getDoc(data['projID'])
        docProject['.repository_upload'] = f'{datetime.now().strftime("%Y-%m-%d")} {res[1]}'
        docProject['branch'] = docProject['branch'][0] | {'op':'u'}
        self.backend.db.updateDoc(docProject, data['projID'])
        msg += 'Saved information to project'
      else:
        msg += 'Error while writing project information to database'
      self.beSendTaskReport.emit(task, msg, '', '')

    elif task is Task.EXTRACTOR_RERUN and set(data.keys())=={'docIDs','recipe'}:
      for docID in data['docIDs']:
        doc = self.backend.db.getDoc(docID)
        if data['recipe']:
          doc['type'] = data['recipe'].split('/')
        #any path is good since the file is the same everywhere; data-changed by reference
        if doc['branch'][0]['path'] is not None:
          oldDocType = doc['type']
          doc['type'] = ['']
          if doc['branch'][0]['path'].startswith('http'):
            path = Path(doc['branch'][0]['path'])
          else:
            path = self.backend.basePath/doc['branch'][0]['path']
          self.backend.useExtractors(path, doc.get('shasum',''), doc)
          if doc['type'][0] == oldDocType[0]:
            del doc['branch']                                                                  #don't update
            self.backend.db.updateDoc(doc, docID)
          else:
            self.backend.db.remove( docID )
            del doc['id']
            doc['name'] = doc['branch'][0]['path']
            self.backend.addData('/'.join(doc['type']), doc, doc['branch'][0]['stack'])
      self.beSendTaskReport.emit(task, 'Extractors re-ran successfully', '', '')

    elif task is Task.OPEN_EXTERNAL and set(data.keys())=={'docID'}:
      doc   = self.backend.db.getDoc(data['docID'])
      if doc['branch'][0]['path'] is None:
        QMessageBox.critical(None, 'ERROR', 'Cannot open file that is only in the database')
      else:
        path  = Path(self.backend.basePath)/doc['branch'][0]['path']
        self.beSendTaskReport.emit(task, '', '', str(path))

    elif task is Task.SET_GUI    and set(data.keys())=={'docID','gui'}:
      self.backend.db.setGUI(data['docID'], data['gui'])

    elif task is Task.HIDE_SHOW    and set(data.keys())=={'docID'}:
      self.backend.db.hideShow(data['docID'])

    else:
      logging.error('Got task, which I do not understand %s %s', task, data.keys(), exc_info=True)


  @Slot(list)
  def executeSQL(self, tasks:list[dict[str,Any]]) -> None:
    """ Execute SQL commands in the backend database: fast change
    Args:
      tasks (list): List of tasks to execute, each task is a dict with keys:
                    - type: 'one', 'many', 'df', or 'get_df'
                    - cmd: SQL command to execute
                    - list: List of parameters for the command (optional)
    """
    if self.backend is None:
      return
    for task in tasks:
      logging.debug('Executing SQL task %s', task)
      if task['type']=='one':
        self.backend.db.cursor.execute(task['cmd'], task.get('list',()))
      elif task['type']=='many':
        self.backend.db.cursor.executemany(task['cmd'], task['list'])
      elif task['type']=='df':
        task['df'].to_sql(task['table'], self.backend.db.connection, if_exists='append', index=False, dtype='str')
      elif task['type']=='get_df':
        df = pd.read_sql_query(task['cmd'], self.backend.db.connection).fillna('')
        self.beSendSQL.emit(task['cmd'], df)
      else:
        print('**ERROR unknown task command', task)
    self.backend.db.connection.commit()


  def exit(self) -> None:
    """ Exit the worker thread """
    if self.backend is not None:
      self.deleteLater()


class BackendThread(QThread):
  """
  Thread that manages the backend worker
  """
  def __init__(self, parent:QObject|None=None) -> None:
    """Initialize the backend thread with a parent QObject
    Args:
      parent (QObject): Parent QObject for the thread
    """
    super().__init__(parent)
    self.worker = BackendWorker()
    self.worker.moveToThread(self)
    self.finished.connect(self.worker.exit)

  def run(self) -> None:
    """
    Run the thread event loop
    """
    self.exec()
