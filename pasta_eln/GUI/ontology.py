""" Table Header dialog: change which colums are shown and in which order """
import json
from pathlib import Path
#pylint: disable=no-name-in-module
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QPushButton
#pylint: enable=no-name-in-module
from ..backend import Backend

class Ontology(QDialog):
  """ Table Header dialog: change which colums are shown and in which order """
  def __init__(self, backend:Backend):
    """
    Initialization

    Args:
      backend (Backend): PASTA-ELN backend
    """
    super().__init__()
    self.backend = backend

    # GUI elements
    self.setWindowTitle('Select table headers')
    self.setMinimumWidth(600)
    mainL = QVBoxLayout(self)

    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)


  #++ TODO ontologyCheck: all names must be different
  def closeDialog(self, btn:QPushButton) -> None:
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save'):
      #TODO_P2 finish ontology dialog
      self.accept()  #close
    else:
      print('dialogOntology: did not get a fitting btn ',btn.text())
    return
