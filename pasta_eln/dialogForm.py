""" New/Edit dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
from PySide6.QtWidgets import QDialog, QFormLayout, QLabel, QTextEdit, QComboBox, QPushButton, QLineEdit   # pylint: disable=no-name-in-module

class Form(QDialog):
  """ New/Edit dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
  def __init__(self, backend, doc):
    """
    Initialization

    Args:
      backend (Pasta): backend, not communication
      doc (dict): if edit: document to change
    """
    super().__init__()
    self.backend = backend
    self.setWindowTitle('Edit content')

    # GUI Stuff
    mainL = QFormLayout(self)
    for key,value in doc.items():
      if key[0] in ['_','-'] or key in ['image','metaVendor','metaUser']:
        continue
      mainL.addRow(QLabel(key),QLineEdit(str(value)))
    ontologyNode = self.backend.db.ontology[doc['-type'][0]]
    for item in ontologyNode:
      if item['name'] in doc or item['name'][0] in ['_','-']:
        continue
      mainL.addRow(QLabel(item['name']),QLineEdit(''))
