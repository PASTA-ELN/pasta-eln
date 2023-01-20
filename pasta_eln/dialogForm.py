""" New/Edit dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
from PySide6.QtWidgets import QDialog, QWidget, QFormLayout, QVBoxLayout, QLabel, QTextEdit, QComboBox, QLineEdit, QDialogButtonBox   # pylint: disable=no-name-in-module
from .style import Image

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

    # GUI elements
    mainL = QVBoxLayout(self)
    if 'image' in doc:
      Image(doc['image'], mainL)
    formW = QWidget()
    mainL.addWidget(formW)
    formL = QFormLayout(formW)
    formL.addRow(QLabel('name'),QLineEdit(str(doc['-name'])))
    for key,value in doc.items():
      if key[0] in ['_','-'] or key in ['image','metaVendor','metaUser']:
        continue
      formL.addRow(QLabel(key),QLineEdit(str(value)))
    ontologyNode = self.backend.db.ontology[doc['-type'][0]]['prop']
    for item in ontologyNode:
      if item['name'] in doc or item['name'][0] in ['_','-']:
        continue
      formL.addRow(QLabel(item['name']),QLineEdit(''))
    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel) #TODO_P3 next button does not exist
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)

  def save(self, btn):
    """
    Action upon save / cancel
    """
    #TODO_P3 rework the name->name and save the changes
    print('btn clicked',btn.text(),'to work on ',self)
