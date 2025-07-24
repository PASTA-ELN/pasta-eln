""" Backend worker thread for separating GUI and backend operations
CONNECT TO ALL THESE SIGNALS IN COMMUNICATE and UI
"""
import logging
from typing import Any, Optional
import pandas as pd
import time
from anytree import Node
from PySide6.QtCore import QObject, QThread, Signal, Slot
from .backend import Backend

waitTimeBeforeSendingFirstMessage = 0.1 #ensure all UI elements are up

class BackendWorker(QObject):
  """
  Backend worker that runs in a separate thread to handle all backend operations
  """
  # Signals to send data back to GUI
  beSendDocTypes          = Signal(dict)           # Send processed data back
  beSendDataHierarchyNode = Signal(str,list)       # Send data hierarchy nodes
  beSendProjects          = Signal(pd.DataFrame)
  beSendTable             = Signal(pd.DataFrame)   # all tables
  beSendHierarchy         = Signal(Node, dict)
  beSendDoc               = Signal(dict)
  beSendTaskReport        = Signal(str, str, str)       # task, report, and image

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


  @Slot(str, str, bool)
  def returnTable(self, docType:str, projID:str, showAll:bool) -> None:
    """ Return a view from the database """
    if self.backend is not None:
      path = f'viewDocType/{docType}All' if showAll else f'viewDocType/{docType}'
      data = self.backend.db.getView(path, startKey=projID)
      self.beSendTable.emit(data)


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

  @Slot(str, str)
  def returnTaskReport(self, task, subtask, subsubtask) -> None:
    """
    - extractorTest: subtask = fileName, subsubtask = output-style
    """
    time.sleep(3)   #TODO remove
    if Backend is not None:
      if task == 'extractorTest':
        report, image = self.backend.testExtractor(subtask, outputStyle=subsubtask)
        self.beSendTaskReport.emit(task, report, image)
      elif task == 'scan':
        for _ in range(2):                                                         #scan twice: convert, extract
          self.backend.scanProject(None, subtask)
        self.beSendTaskReport.emit(task, 'Scanning finished successfully', '')
      else:
        logging.error('Got task, which I do not understand')

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