#!/usr/bin/python3
"""TEST the project view: drag drop randomly items around """
import logging, warnings, random
from pathlib import Path
from PySide6.QtCore import QModelIndex                                  # pylint: disable=no-name-in-module
from pasta_eln.backend import Backend
from pasta_eln.GUI.project import Project
from pasta_eln.guiCommunicate import Communicate
from pasta_eln.GUI.palette import Palette

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
  backend = Backend('research')
  palette = Palette(None, 'light_blue')
  comm = Communicate(backend, palette)
  window = Project(comm)
  qtbot.addWidget(window)
  projID = backend.output('x0').split('|')[-1].strip()
  window.change(projID,'')

  choices = random.choices(range(100), k=16)
  choices = [52,49,38,44,44,91,7,32,55,66,97,34,54,82,84,9]
  print(f'Current choice: [{",".join([str(i) for i in choices])}]')

  # start iteration
  for epoch in range(4):
    print(f'Start drag-drop {epoch}')
    def recursiveRowIteration(index:QModelIndex) -> None:
      item  = window.tree.model().itemFromIndex(index)
      allParentIdx = [index] if item is not None and item.data() is not None and item.data()['docType']==['x1'] else []
      for subRow in range(window.tree.model().rowCount(index)):
        subIndex = window.tree.model().index(subRow,0, index)
        allParentIdx += recursiveRowIteration(subIndex)
      return allParentIdx
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
    print('  ',sourceItem.data(),'->\n  ', targetParent.data())
    validChoices     = range(targetParent.rowCount()+1)
    targetChildRow   = validChoices[choices.pop(0)%len(validChoices)]
    targetParent.setChild(targetChildRow, sourceItem)
    verify(backend)
  return

def verify(backend): # Verify DB
  output = backend.checkDB(outputStyle='text')
  print(output)
  output = '\n'.join(output.split('\n')[8:])
  assert '**ERROR' not in output, 'Error in checkDB'
  return
