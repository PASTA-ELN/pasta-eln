#!/usr/bin/python3
"""Test the Nextcloud project add-on browser widget."""
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from testsComplicated import project_nextcloud
from testsComplicated.nextcloud_common import readNclink


class SignalSpy:
  """Record signal emissions made by the add-on."""

  def __init__(self) -> None:
    self.calls:list[tuple[Any, ...]] = []


  def emit(self, *args:Any) -> None:
    """Record one signal emission.
    Args:
      args (Any): Emitted signal arguments.
    """
    self.calls.append(args)


class FakeBrowser:
  """Small in-memory browser used to test the Qt workflow."""

  def __init__(self, account:dict[str,str]) -> None:
    self.currentPath = '/'
    self.entries = [
      {'name':'folder', 'isFolder':True},
      {'name':'root.txt', 'isFolder':False, 'fileId':'1', 'nextcloudETag':'"1"',
       'nextcloudContentType':'text/plain', 'nextcloudSize':1},
    ]


  def listFolder(self) -> list[dict[str,Any]]:
    """Return entries in the current fake folder."""
    return self.entries


  def openFolder(self, name:str) -> None:
    """Enter the fake folder.
    Args:
      name (str): Folder name.
    """
    self.currentPath = f'/{name}/'
    self.entries = [
      {'name':'a.txt', 'isFolder':False, 'fileId':'2', 'nextcloudETag':'"2"',
       'nextcloudContentType':'text/plain', 'nextcloudSize':2},
      {'name':'b.txt', 'isFolder':False, 'fileId':'3', 'nextcloudETag':'"3"',
       'nextcloudContentType':'text/plain', 'nextcloudSize':3},
    ]


  def selectFiles(self, names:list[str]) -> list[dict[str,Any]]:
    """Select named files in the current fake folder.
    Args:
      names (list[str]): File names.
    Returns:
      list[dict[str, Any]]: Selected files.
    """
    return [entry for entry in self.entries if entry['name'] in names]


def test_nextcloud_dialog_browses_and_writes_multiple_files(qtbot, monkeypatch, tmp_path:Path) -> None:
  """Navigate into a folder, select two files, and write both pointers."""
  monkeypatch.setattr(project_nextcloud, 'NextcloudBrowser', FakeBrowser)
  monkeypatch.setattr(project_nextcloud, 'loadConfiguration',
                      lambda path: {'addOnParameter': {'nextcloud': {'test': '{}'}}})
  projectPath = tmp_path/'project'
  projectPath.mkdir()
  backend = SimpleNamespace(db=SimpleNamespace(getDoc=lambda projectID: {'branch':[{'path':'project'}]}))
  comm = SimpleNamespace(basePath=tmp_path, backendThread=SimpleNamespace(worker=SimpleNamespace(backend=backend)),
                         uiRequestHierarchy=SignalSpy())
  dialog = project_nextcloud.NextcloudDialog(comm, 'x0-test', projectPath)
  qtbot.addWidget(dialog)

  folderItem = dialog.fileList.item(0)
  dialog.onItemDoubleClicked(folderItem)
  dialog.fileList.item(0).setSelected(True)
  dialog.fileList.item(1).setSelected(True)
  dialog.importSelected()

  assert readNclink(projectPath/'a.txt.nclink')['fileId'] == '2'
  assert readNclink(projectPath/'b.txt.nclink')['fileId'] == '3'
  assert comm.uiRequestHierarchy.calls == [('x0-test', True)]
