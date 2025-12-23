"""example add-on: sort direct children of node
"""
import logging
from PySide6.QtWidgets import QMessageBox
from pasta_eln.backendWorker.worker import Task
from pasta_eln.miscTools import getHierarchy

# The following two variables are mandatory
description  = 'Sort children'  #short description that is shown in the menu
reqParameter = {} #possibility for required parameters: like API-key, etc. {'API': 'text'}


def main(comm, hierStack, widget, parameter={}):
  """ main function: has to exist and is called by the menu
  Args:
    comm (Communicate): communicate-backend
    hierStack (str): node in hierarchy to start the creation
    widget (QWidget): allows to create new gui dialogs
    parameter (dict): ability to pass parameters

  Returns:
      bool: success
  """
  maxNumberSorting = 100
  res = QMessageBox.question(widget, 'Sort direction', 'Sort direct children in ascending order? '
          'If you click no, sort in descending order.',
          buttons=QMessageBox.StandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel),
          defaultButton=QMessageBox.StandardButton.Yes)
  if res == QMessageBox.StandardButton.Cancel:
    return False
  ascendingFlag = res == QMessageBox.StandardButton.Yes
  hierStackI = hierStack.split('/')

  # Issue: previous sorting steps influence later steps. Hence after one sorting step, always get the updated order and look for changes
  # One could use a 'while True' loop but that would risk erroneous endless loops. Better, max. number and then user has to sort again.
  for idx in range(maxNumberSorting):
    hierarchy, _ = getHierarchy(comm, hierStack)
    noChange = True
    for revIdx, node in enumerate(sorted(hierarchy.children, key=lambda n: n.name.lower(), reverse=ascendingFlag)):
      idx = len(hierarchy.children) - 1 - revIdx
      if idx == node.childNum:
        continue
      comm.uiRequestTask.emit(Task.MOVE_LEAVES, {'docID':node.id, 'stackOld':hierStackI,'stackNew':hierStackI,
                                                 'childOld':node.childNum, 'childNew':idx})
      noChange = False
      break
    if noChange:
      break
    if idx == maxNumberSorting-1:
      logging.info('Only sorted %s times according to max. number of sorting', maxNumberSorting)


  return True
