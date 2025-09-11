"""example add-on: sort direct children of node
"""
from anytree import PreOrderIter
from PIL import Image
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
  res = QMessageBox.question(widget, 'Sort direction', 'Sort direct children in ascending order? '
          'If you click no, sort in descending order.',
          buttons=QMessageBox.StandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel),
          defaultButton=QMessageBox.StandardButton.Yes)
  if res == QMessageBox.StandardButton.Cancel:
    return False
  ascendingFlag = res == QMessageBox.StandardButton.Yes
  hierarchy, _ = getHierarchy(comm, hierStack)
  hierStackI = hierStack.split('/')
  for revIdx, node in enumerate(sorted(hierarchy.children, key=lambda n: n.name.lower(), reverse=ascendingFlag)):
    idx = len(hierarchy.children) - 1 - revIdx
    comm.uiRequestTask.emit(Task.MOVE_LEAVES, {'docID':node.id, 'stackOld':hierStackI,'stackNew':hierStackI,
                                               'childOld':node.childNum, 'childNew':idx})
  return True
