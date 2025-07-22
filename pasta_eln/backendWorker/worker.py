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
  beSendDocTypes = Signal(dict)           # Send processed data back
  beSendProjects = Signal(pd.DataFrame)
  beSendTable    = Signal(pd.DataFrame)   # all tables
  beSendHierarchy= Signal(Node, dict)

  def __init__(self):
    super().__init__()
    self.backend: Optional[Backend] = None


  @Slot(dict,str)
  def initialize(self, configuration:dict, projectGroupName:str) -> None:
    """ Initialize the backend worker with the given configuration """
    self.backend = Backend(configuration, projectGroupName)
    docTypesTitlesIcons = {k:{'title':v} for k,v in self.backend.db.dataHierarchy('','title')}
    for k,v in self.backend.db.dataHierarchy('','icon'):
      docTypesTitlesIcons[k]['icon'] = v
    for k,v in self.backend.db.dataHierarchy('','shortcut'):
      docTypesTitlesIcons[k]['shortcut'] = v
    self.beSendDocTypes.emit(docTypesTitlesIcons)
    self.beSendProjects.emit(self.backend.db.getView('viewDocType/x0'))

  @Slot(str, str, bool)
  def returnTable(self, docType:str, projID:str, showAll:bool) -> None:
    """ Return a view from the database """
    path = f'viewDocType/{docType}All' if showAll else f'viewDocType/{docType}'
    data = self.backend.db.getView(path, startKey=projID)
    self.beSendTable.emit(data)

  @Slot(str)
  def returnHierarchy(self, projID:str, showAll:bool) -> None:
    """ Return a hierarchy"""
    hierarchy, error = self.backend.db.getHierarchy(projID, allItems=showAll)
    if error:
      hierarchy = Node('__ERROR_in_getHierarchy__')
    projDoc = self.backend.db.getDoc(projID)
    self.beSendHierarchy.emit(hierarchy, projDoc)

  def exit(self) -> None:
    """ Exit the worker thread """
    self.deleteLater()


class BackendThread(QThread):
  """
  Thread that manages the backend worker
  """
  def __init__(self, parent=None):
    """ Initialize the backend thread with a parent QObject
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