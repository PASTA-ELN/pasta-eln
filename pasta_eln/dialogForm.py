""" New/Edit dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
from PySide6.QtWidgets import QDialog, QWidget, QFormLayout, QVBoxLayout, QLabel, QTextEdit, QPlainTextEdit, QComboBox, QLineEdit, QDialogButtonBox, QSplitter, QSizePolicy   # pylint: disable=no-name-in-module
from PySide6.QtCore import QSize
from .style import Image, TextButton

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
    flagNewDoc = True
    if '_id' in doc:
      flagNewDoc = False
    self.setMinimumWidth(600)
    if flagNewDoc:
      self.setWindowTitle('Create new entry')
      doc['-name'] = ''
    else:
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
      if key in ['comment','content']:
        labelW = QWidget()
        labelL = QVBoxLayout(labelW)
        labelL.addWidget(QLabel(key))
        TextButton('Show', self.btnAdvanced, labelL, key, checkable=True)
        setattr(self, 'textEdit_'+key, QPlainTextEdit(value))
        getattr(self, 'textEdit_'+key).setAccessibleName(key)
        getattr(self, 'textEdit_'+key).textChanged.connect(self.textChanged)
        setattr(self, 'textShow_'+key, QTextEdit(value))
        getattr(self, 'textShow_'+key).setReadOnly(True)
        getattr(self, 'textShow_'+key).hide()
        setattr(self, 'splitter_'+key, QSplitter())
        getattr(self, 'splitter_'+key).setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        getattr(self, 'splitter_'+key).addWidget(getattr(self, 'textEdit_'+key))
        getattr(self, 'splitter_'+key).addWidget(getattr(self, 'textShow_'+key))
        formL.addRow(labelW, getattr(self,'splitter_'+key))
      elif isinstance(value, list):
        formL.addRow(QLabel(key),QLineEdit(' '.join(value)))
      elif isinstance(value, str):
        formL.addRow(QLabel(key),QLineEdit(value))
      else:
        print("**ERROR unknown value type",key, value)
    ontologyNode = self.backend.db.ontology[doc['-type'][0]]['prop']
    for item in ontologyNode:
      if item['name'] in doc or item['name'][0] in ['_','-']:
        continue
      formL.addRow(QLabel(item['name']),QLineEdit(''))
    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel) #TODO_P3 next button does not exist
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)



  #TODO_P5 what to do if unidentified datatype '--aoeuaoeu' is edited: create questionare with these
  # ontologyNode = [{"name": "-name","query": "What is the name of task?"},
  #               {"name": "comment","query": "#tags comments remarks :field:value:"},
  #               {"name": "type", "query": "What should be the type","list":["sample","measurement","procedure","instrument"] }]
  # if (docRaw['-type'][0]=='-' && docRaw['type']) { //undefined doctype was redefined
  #   docRaw['-type']=docRaw['type'].split('/');
  #   if (docRaw['type']=='measurement')
  #     docRaw['image']='';
  #   delete docRaw['type'];
  # }

  def save(self, btn):
    """
    Action upon save / cancel
    """
    #TODO_P3 rework the name->name and save the changes
    print('btn clicked',btn.text(),'to work on ',self)


  def btnAdvanced(self, status):
    """
    Action if advanced button is clicked
    """
    key = self.sender().accessibleName()
    if status:
      getattr(self, 'textShow_'+key).hide()
    else:
      getattr(self, 'textShow_'+key).show()
    return

  def textChanged(self):
    key = self.sender().accessibleName()
    getattr(self, 'textShow_'+key).setMarkdown( getattr(self, 'textEdit_'+key).toPlainText())
    return
