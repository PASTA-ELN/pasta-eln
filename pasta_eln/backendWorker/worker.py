""" Backend worker thread for separating GUI and backend operations
CONNECT TO ALL THESE SIGNALS IN COMMUNICATE and UI
"""
from enum import Enum
import json
import logging
import platform
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional
import pandas as pd
import time
from anytree import Node
from PySide6.QtCore import QObject, QThread, Signal, Slot
from .backend import Backend
from .inputOutput import exportELN, importELN
from .elabFTWsync import Pasta2Elab
from ..UI.messageDialog import showMessage

waitTimeBeforeSendingFirstMessage = 0.1 #ensure all UI elements are up

class Task(Enum):
  """ Tasks that can be used in BackendWorker """
  SCAN           = 1
  EXTRACTOR_TEST = 2
  SEND_ELAB      = 3
  GET_ELAB       = 4
  SMART_ELAB     = 5
  SET_GUI        = 6
  DELETE_DOC     = 7
  EXPORT_ELN     = 8
  IMPORT_ELN     = 9
  CHECK_DB       = 10
  EXTRACTOR_RERUN= 11
  ADD_DOC        = 12
  OPEN_EXTERNAL  = 13
  DROP           = 14
  HIDE_SHOW      = 15


class BackendWorker(QObject):
  """
  Backend worker that runs in a separate thread to handle all backend operations
  """
  # Signals to send data back to GUI
  beSendDocTypes          = Signal(dict)           # Send processed data back
  beSendDataHierarchyNode = Signal(str,list)       # Send data hierarchy nodes
  beSendDataHierarchyAll  = Signal(list)           # Send all entries for this docType
  beSendProjects          = Signal(pd.DataFrame)
  beSendTable             = Signal(pd.DataFrame, str)   # all tables
  beSendHierarchy         = Signal(Node, dict)
  beSendDoc               = Signal(dict)
  beSendTaskReport        = Signal(Task, str, str)       # task, report, and image
  beSendSQL               = Signal(str, pd.DataFrame)

  def __init__(self) -> None:
    """ Initialize the backend worker """
    super().__init__()
    self.backend: Optional[Backend] = None


  @Slot(dict,str)
  def initialize(self, configuration:dict[str,Any], projectGroupName:str) -> None:
    """ Initialize the backend worker with the given configuration """
    self.backend = Backend(configuration, projectGroupName)
    docTypesTitlesIcons = {k:{'title':v} for k,v in self.backend.db.dataHierarchy('','title')}
    for k,v in self.backend.db.dataHierarchy('','icon'):
      docTypesTitlesIcons[k]['icon'] = v
    for k,v in self.backend.db.dataHierarchy('','shortcut'):
      docTypesTitlesIcons[k]['shortcut'] = v
    time.sleep(waitTimeBeforeSendingFirstMessage)
    self.beSendDocTypes.emit(docTypesTitlesIcons)
    self.beSendProjects.emit(self.backend.db.getView('viewDocType/x0'))
    for docType in docTypesTitlesIcons:
      self.beSendDataHierarchyNode.emit(docType, self.backend.db.dataHierarchy(docType, 'meta'))

  @Slot(str)
  def returnDataHierarchyRow(self, docType:str) -> None:
    self.beSendDataHierarchyAll.emit(self.backend.db.dataHierarchy(docType, '*'))


  @Slot(str, str, bool)
  def returnTable(self, docType:str, projID:str, showAll:bool) -> None:
    """ Return a view from the database """
    if docType and self.backend is not None:
      if docType=='_tags_':
        path = 'viewIdentify/viewTags'
      else:
        path = f'viewDocType/{docType}'
      path += 'All' if showAll else ''
      print('returnTable', docType, projID, showAll, path)
      data = self.backend.db.getView(path, startKey=projID)
      self.beSendTable.emit(data, docType)


  @Slot(str)
  def returnHierarchy(self, projID:str, showAll:bool) -> None:
    """ Return a hierarchy"""
    if self.backend is not None:
      hierarchy, error = self.backend.db.getHierarchy(projID, allItems=showAll)
      if error:
        hierarchy = Node('__ERROR_in_getHierarchy__')
      projDoc = self.backend.db.getDoc(projID)
      self.beSendHierarchy.emit(hierarchy, projDoc)

  @Slot(str, str)
  def returnDoc(self, docID:str) -> None:
    if self.backend is not None:
      self.beSendDoc.emit(self.backend.db.getDoc(docID))

  @Slot(Task, dict)
  def returnTaskReport(self, task:Task, data:dict[str,Any]) -> None:
    """
    - extractorTest: subtask = fileName, subsubtask = output-style
    """
    time.sleep(3)   #TODO remove
    if self.backend is not None:
      if task is Task.EXTRACTOR_TEST and set(data.keys())=={'fileName','style','recipe','saveFig'}:
        report, image = self.backend.testExtractor(data['fileName'], style={'main':data['recipe']},
                                                   outputStyle=data['style'], saveFig=data['saveFig'])
        self.beSendTaskReport.emit(task, report, image)
      elif task is Task.CHECK_DB and set(data.keys())=={'style'}:
        report = self.backend.checkDB(outputStyle=data['style'])
        self.beSendTaskReport.emit(task, report, '')
      elif task is Task.SCAN         and set(data.keys())=={'docID'}:
        for _ in range(2):                                                         #scan twice: convert, extract
          self.backend.scanProject(None, data['docID'])
        self.beSendTaskReport.emit(task, 'Scanning finished successfully', '')
      elif task is Task.ADD_DOC      and set(data.keys())=={'hierStack','docType','doc'}:
        parentID  = data['hierStack'][-1]
        self.backend.cwd = Path(self.backend.db.getDoc(parentID)['branch'][0]['path'])
        self.backend.addData(data['docType'], data['doc'], data['hierStack'])
      elif task is Task.DROP         and set(data.keys())=={'docID','files','folders'}:
        commonBase   = os.path.commonpath(data['folders']+[str(i) for i in data['files']])
        doc = self.backend.db.getDoc(data['docID'])
        targetFolder = Path(self.backend.cwd/doc['branch'][0]['path'])
        # create folders and copy files
        for folder in data['folders']:
          (targetFolder/(Path(folder).relative_to(commonBase))).mkdir(parents=True, exist_ok=True)
        for fileStr in data['files']:
          file = Path(fileStr)
          if file.is_file():
            shutil.copy(file, targetFolder/(file.relative_to(commonBase)))
        # scan
        for _ in range(2):                                                         #scan twice: convert, extract
          self.backend.scanProject(None, docID, targetFolder.relative_to(self.backend.basePath))
        self.beSendTaskReport.emit(task, 'Drag-drop operation finished successfully', '')
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
          oldPath.rename(newPath)
        # go through children, remove from DB
        children = self.backend.db.getView('viewHierarchy/viewHierarchy', startKey=data['docID'])
        for docID in {line['id'] for line in children if line['id']!=data['docID']}:
          self.backend.db.remove(docID)
        self.beSendTaskReport.emit(task, 'Deleting finished successfully', '')
      elif task is Task.EXPORT_ELN and set(data.keys())=={'fileName','projID','docTypes'}:
        report = exportELN(self.backend, [data['projID']], data['fileName'], data['docTypes'])
        self.beSendTaskReport.emit(task, report, '')
      elif task is Task.IMPORT_ELN and set(data.keys())=={'fileName','projID'}:
        report, statistics = importELN(self.backend, data['fileName'], data['projID'])
        self.beSendTaskReport.emit(task, f'{report}\n{json.dumps(statistics,indent=2)}', '')
      elif task in (Task.SEND_ELAB, Task.GET_ELAB, Task.SMART_ELAB) and set(data.keys())=={'projGroup'}:
        if 'ERROR' in self.backend.checkDB(minimal=True):
          self.beSendTaskReport.emit(task, 'ERRORs are present in your database. Fix them before uploading', '')
        else:
          sync = Pasta2Elab(self.backend, data['projGroup'])
          if hasattr(sync, 'api') and sync.api.url:                                 #if hostname and api-key given
            if task is Task.SEND_ELAB:
              statistics = sync.sync('sA')
            elif task is Task.GET_ELAB:
              statistics = sync.sync('gA')
            else:
              statistics = sync.sync('')
            self.beSendTaskReport.emit(task, 'Success: Syncronized data with elabFTW server'+str(statistics), '')
          else:                                                                                      #if not given
            self.beSendTaskReport.emit(task, 'ERROR: Please specify a server address and API-key in the Configuration', '')
      elif task is Task.EXTRACTOR_RERUN and set(data.keys())=={'docIDs'}:
        for docID in data['docIDs']:
          doc = self.backend.db.getDoc(docID)
          if doc['branch'][0]['path'] is not None:
            oldDocType = doc['type']
            doc['type'] = ['']
            if doc['branch'][0]['path'].startswith('http'):
              path = Path(doc['branch'][0]['path'])
            else:
              path = self.backend.basePath/doc['branch'][0]['path']
            self.backend.useExtractors(path, doc.get('shasum',''), doc)
            if doc['type'][0] == oldDocType[0]:
              del doc['branch']                                                                    #don't update
              self.backend.db.updateDoc(doc, docID)
            else:
              self.backend.db.remove( docID )
              del doc['id']
              doc['name'] = doc['branch'][0]['path']
              self.backend.addData('/'.join(doc['type']), doc, doc['branch'][0]['stack'])
        self.beSendTaskReport.emit(task, 'Extractors re-ran successfully', '')
      elif task is Task.OPEN_EXTERNAL and set(data.keys())=={'docID'}:
        doc   = self.backend.db.getDoc(data['docID'])
        if doc['branch'][0]['path'] is None:
          showMessage(self, 'Error', 'Cannot open file that is only in the database','Critical')
        else:
          path  = Path(self.backend.basePath)/doc['branch'][0]['path']
          if platform.system() == 'Darwin':                                                              # macOS
            subprocess.call(('open', path))
          elif platform.system() == 'Windows':                                                         # Windows
            os.startfile(path)                                                      # type: ignore[attr-defined]
          else:                                                                                 # linux variants
            subprocess.call(('xdg-open', path))
      elif task is Task.SET_GUI    and set(data.keys())=={'docID','gui'}:
        self.backend.db.setGUI(data['docID'], data['gui'])
      elif task is Task.HIDE_SHOW    and set(data.keys())=={'docID'}:
        self.backend.db.hideShow(data['docID'])
      else:
        logging.error('Got task, which I do not understand %s %s', task, data.keys())


  @Slot(list)
  def executeSQL(self, tasks) -> None:
    for task in tasks:
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
        print("**ERROR unknown task command", task)
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
