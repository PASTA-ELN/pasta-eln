""" New/Edit dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
from PySide6.QtWidgets import QDialog, QWidget, QFormLayout, QVBoxLayout, QLabel, QTextEdit, QPlainTextEdit, QComboBox, QLineEdit, QDialogButtonBox, QSplitter   # pylint: disable=no-name-in-module
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

        self.textEdit = QPlainTextEdit(value)
        self.textShow = QTextEdit(value)
        self.textShow.setReadOnly(True)
        self.textEdit.textChanged.connect(self.textChanged)
        self.splitter = QSplitter()
        self.splitter.addWidget(self.textEdit)
        self.splitter.addWidget(self.textShow)

        formL.addRow(labelW, self.splitter)
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
      textEdit = QTextEdit(text) #one block
      setattr(self, '_textEdit'+key, QTextEdit(value))
    else:
      text = getattr(self, '_textEdit'+key).toPlainText()
      editor = QTextEdit()
      viewer = QTextEdit()
      viewer.setBaseSize(QSize)
      editor.textChanged.connect(viewer.setMarkdown)
      splitter = QSplitter()
      splitter.addWidget(editor)
      splitter.addWidget(viewer)
      setattr(self, '_textEdit'+key, splitter)

    print("btn clickeeeed", key, text, status)

  def textChanged(self):
    # self.textShow.setMarkdown
    self.textShow.setMarkdown(self.textEdit.toPlainText())