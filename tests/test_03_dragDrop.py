#!/usr/bin/python3
"""TEST the project view: drag drop randomly items around """
import logging, warnings, random
from pathlib import Path
from anytree import PreOrderIter
from PySide6.QtCore import QModelIndex, QEventLoop                         # pylint: disable=no-name-in-module
from pasta_eln.UI.project import Project
from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.backendWorker.worker import Task


def test_simple(qtbot):
  """
  main function
  """
  # initialization: create database, destroy on filesystem and database and then create new one
  warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
  warnings.filterwarnings('ignore', message='invalid escape sequence')
  warnings.filterwarnings('ignore', category=ResourceWarning, module='PIL')
  warnings.filterwarnings('ignore', category=ImportWarning)
  logPath = Path.home()/'pastaELN.log'
  logging.basicConfig(filename=logPath, level=logging.INFO, format='%(asctime)s|%(levelname)s:%(message)s',
                      datefmt='%m-%d %H:%M:%S')   #This logging is always info, since for installation only
  for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib.font_manager']:
    logging.getLogger(package).setLevel(logging.WARNING)
  logging.info('Start 03 test')

  # start app and load project
  comm = Communicate('research')
  window = Project(comm)
  qtbot.addWidget(window)
  while comm.backendThread.worker.backend is None:
    qtbot.wait(100)
  projID = comm.backendThread.worker.backend.output('x0').split('|')[-2].strip()  #for testing purposes
  window.change(projID,'')

  choices = random.choices(range(100), k=16)
  # choices =
  print(f'Current choice: [{",".join([str(i) for i in choices])}]')
  # start iteration
  for epoch in range(4):
    print(f'{"*"*40}\nStart drag-drop {epoch}\n{"*"*40}')
    def recursiveRowIteration(index:QModelIndex) -> list[QModelIndex]:
      item  = window.tree.model().itemFromIndex(index)
      allParentIdx = [index] if item is not None and item.data() is not None and item.data()['docType']==['x1'] else []
      for subRow in range(window.tree.model().rowCount(index)):
        subIndex = window.tree.model().index(subRow,0, index)
        allParentIdx += recursiveRowIteration(subIndex)
      return allParentIdx
    qtbot.wait(1000)
    allParentIdx = recursiveRowIteration( window.tree.model().index(-1,0))
    validChoices     = [i for i in allParentIdx if window.tree.model().rowCount(i)>0 ]
    sourceParentIdx  = validChoices[choices.pop(0)%len(validChoices)]
    sourceParentItem = window.tree.model().itemFromIndex(sourceParentIdx)
    validChoices     = range(window.tree.model().rowCount(sourceParentIdx))
    sourceChildRow   = validChoices[choices.pop(0)%len(validChoices)]
    sourceItem       = sourceParentItem.takeChild(sourceChildRow)
    if sourceItem.data() is None:
      continue
    validChoices     = [window.tree.model().itemFromIndex(i) for i in allParentIdx
                        if window.tree.model().itemFromIndex(i).data() is not None and
                          window.tree.model().itemFromIndex(i).data()['hierStack'].split('/')[-1] != sourceItem.data()['hierStack'].split('/')[-1] ]
    targetParent     = validChoices[choices.pop(0)%len(validChoices)]
    validChoices     = range(targetParent.rowCount()+1)
    targetChildRow   = validChoices[choices.pop(0)%len(validChoices)]
    print('  ',sourceItem.data(),'->\n  ', targetParent.data(),'   child', targetChildRow)
    targetParent.setChild(targetChildRow, sourceItem)
    verify(comm, projID, epoch)

  # close everything
  print(f'{"*"*40}\nEND TEST 03\n{"*"*40}')
  comm.shutdownBackendThread()
  return


def verify(comm, projID, epoch): # Output hierarchy and verify DB
  # to communicate with backend
  loop = QEventLoop()
  def hierarchyCallback(hierarchy):
    print(f'{"*"*40}\nHierarchy after drag-drop {epoch}\n{"*"*40}')
    print(''.join('  '*node.depth + node.name + ' | ' + '/'.join(node.docType) + (f' | {node.id}') +'\n'
                   for node in PreOrderIter(hierarchy)))
    loop.quit()
  def checkDBCallback(_, output):
    print(f'{"*"*40}\nCheckDB after drag-drop {epoch}\n{"*"*40}')
    print(output)
    output = '\n'.join(output.split('\n')[8:])
    assert '**ERROR' not in output, 'Error in checkDB'
    loop.quit()
  comm.backendThread.worker.beSendHierarchy.connect(hierarchyCallback)
  comm.backendThread.worker.beSendTaskReport.connect(checkDBCallback)
  comm.uiRequestHierarchy.emit(projID, True)
  loop.exec()
  comm.uiRequestTask.emit(Task.CHECK_DB, {'style':'text'})
  loop.exec()
  comm.backendThread.worker.beSendHierarchy.disconnect(hierarchyCallback)
  comm.backendThread.worker.beSendTaskReport.disconnect(checkDBCallback)
  return
