""" Backend worker thread for separating GUI and backend operations
CONNECT TO ALL SIGNALS IN COMMUNICATE
"""
import logging
from typing import Any, Optional
import pandas as pd
import sqlite3
from anytree import Node
from pathlib import Path
from PySide6.QtCore import QObject, QThread, Signal, Slot
from .backend import Backend

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
  beSendExtractorReport   = Signal(str, str)       # report, and image

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
  def returnExtractorTest(self, fileName, outputStyle) -> None:
    if Backend is not None:
      report, image = self.backend.testExtractor(fileName, outputStyle=outputStyle)
      self.beSendExtractorReport.emit(report, image)

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