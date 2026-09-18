"""Project GUI add-on for selecting Nextcloud files as PASTA pointers."""
import json
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QLabel, QListWidget, QListWidgetItem,
                               QVBoxLayout)

from pasta_eln.configuration_file import loadConfiguration
from testsComplicated.nextcloud_common import NextcloudBrowser, writeNclinks

description = 'Import files from Nextcloud'
reqParameter:dict[str,str] = {}


class NextcloudDialog(QDialog):
  """Dialog for browsing one Nextcloud account and selecting files."""

  def __init__(self, comm:Any, projectID:str, projectPath:Path, parent:Any=None) -> None:
    """Create the Nextcloud file browser.
    Args:
      comm (Any): PASTA GUI communication object.
      projectID (str): Project receiving the pointers.
      projectPath (Path): Project directory.
      parent (Any): Optional Qt parent.
    """
    super().__init__(parent)
    self.comm = comm
    self.projectID = projectID
    self.projectPath = projectPath
    self.credentials = loadConfiguration(comm.basePath/'.nextcloud_credentials.json')
    self.accounts = self.credentials['addOnParameter']['nextcloud']
    self.browser:NextcloudBrowser|None = None
    self.instanceBox = QComboBox(self)
    self.fileList = QListWidget(self)
    self.fileList.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
    self.fileList.itemDoubleClicked.connect(self.onItemDoubleClicked)
    self.status = QLabel(self)
    self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
    self.buttons.accepted.connect(self.importSelected)
    self.buttons.rejected.connect(self.reject)
    layout = QVBoxLayout(self)
    layout.addWidget(QLabel('Nextcloud instance:', self))
    layout.addWidget(self.instanceBox)
    layout.addWidget(self.fileList)
    layout.addWidget(self.status)
    layout.addWidget(self.buttons)
    self.setWindowTitle('Import files from Nextcloud')
    self.instanceBox.addItems(sorted(self.accounts))
    self.instanceBox.currentTextChanged.connect(self.onInstanceChanged)
    self.onInstanceChanged(self.instanceBox.currentText())


  def onInstanceChanged(self, instance:str) -> None:
    """Connect to the selected instance and show its root folder.
    Args:
      instance (str): Instance alias.
    """
    account = json.loads(self.accounts[instance])
    self.browser = NextcloudBrowser(account)
    self.refresh()


  def refresh(self) -> None:
    """Refresh entries in the browser's current folder."""
    if self.browser is None:
      return
    self.fileList.clear()
    for entry in self.browser.listFolder():
      item = QListWidgetItem(('📁 ' if entry['isFolder'] else '')+entry['name'])
      item.setData(Qt.ItemDataRole.UserRole, entry)
      self.fileList.addItem(item)
    self.status.setText(self.browser.currentPath)


  def onItemDoubleClicked(self, item:QListWidgetItem) -> None:
    """Enter a double-clicked folder.
    Args:
      item (QListWidgetItem): Activated list item.
    """
    entry = item.data(Qt.ItemDataRole.UserRole)
    if entry['isFolder'] and self.browser is not None:
      self.browser.openFolder(entry['name'])
      self.refresh()


  def importSelected(self) -> None:
    """Write pointers for selected files and refresh the project tree."""
    if self.browser is None:
      return
    names = [item.data(Qt.ItemDataRole.UserRole)['name'] for item in self.fileList.selectedItems()
             if not item.data(Qt.ItemDataRole.UserRole)['isFolder']]
    if not names:
      self.status.setText('Select at least one file.')
      return
    selected = self.browser.selectFiles(names)
    writeNclinks(self.projectPath, self.instanceBox.currentText(), selected)
    self.comm.uiRequestHierarchy.emit(self.projectID, True)
    self.accept()


def main(comm:Any, hierStack:str, widget:Any, parameter:dict[str,Any]) -> bool:
  """Open the Nextcloud browser for a project.
  Args:
    comm (Any): PASTA GUI communication object.
    hierStack (str): Project document ID.
    widget (Any): Parent widget.
    parameter (dict[str, Any]): Add-on parameters.
  Returns:
    bool: True when the dialog completed successfully.
  """
  backend = comm.backendThread.worker.backend
  projectPath = comm.basePath/backend.db.getDoc(hierStack)['branch'][0]['path']
  return NextcloudDialog(comm, hierStack, projectPath, widget).exec() == QDialog.DialogCode.Accepted
