""" New/Edit dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
#pylint: disable=no-name-in-module
from PySide6.QtWidgets import QDialog, QWidget, QFormLayout, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, \
                              QPlainTextEdit, QComboBox, QLineEdit, QDialogButtonBox, QSplitter, QSizePolicy
#pylint: enable=no-name-in-module
from .style import Image, TextButton, IconButton

class Form(QDialog):
  """ New/Edit dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
  def __init__(self, comm, doc):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
      doc (dict):  document to change / create
    """
    super().__init__()
    self.comm = comm
    self.doc = dict(doc)
    if '_attachments' in self.doc:
      del self.doc['_attachments']
    flagNewDoc = True
    if '_id' in self.doc:
      flagNewDoc = False
    if flagNewDoc:
      self.setWindowTitle('Create new entry')
      self.doc['-name'] = ''
    else:
      self.setWindowTitle('Edit content')
    self.setMinimumWidth(600)

    # GUI elements
    mainL = QVBoxLayout(self)
    if 'image' in self.doc:
      width = self.comm.backend.configuration['GUI']['imageWidthDetails'] \
                if hasattr(self.comm.backend, 'configuration') else 300
      Image(self.doc['image'], mainL, width=width)
    formW = QWidget()
    mainL.addWidget(formW)
    formL = QFormLayout(formW)

    #Add things that are in ontology
    if '-type' in self.doc:
      setattr(self, 'key_-name', QLineEdit(self.doc['-name']))
      formL.addRow('Name', getattr(self, 'key_-name'))
      ontologyNode = self.comm.backend.db.ontology[self.doc['-type'][0]]['prop']
      for item in ontologyNode:
        if item['name'] not in self.doc and  item['name'][0] not in ['_','-']:
          self.doc[item['name']] = ''
    for key,value in self.doc.items():
      if key[0] in ['_','-'] or key in ['image','metaVendor','metaUser','shasum']:
        continue
      if key in ['comment','content']:
        labelW = QWidget()
        labelL = QVBoxLayout(labelW)
        labelL.addWidget(QLabel(key.capitalize()))
        TextButton('Show', self.btnAdvanced, labelL, key, checkable=True)
        rightSideW = QWidget()
        rightSideL = QVBoxLayout(rightSideW)
        setattr(self, 'buttonBarW_'+key, QWidget())
        getattr(self, 'buttonBarW_'+key).hide()
        buttonBarL = QHBoxLayout(getattr(self, 'buttonBarW_'+key))
        for name, tooltip in [['bold','Bold text'],['italic','Italic text'],['list-ul','Bullet list'],\
                              ['list-ol','Numbered list']]:
          IconButton('fa5s.'+name, self.btnText, buttonBarL, name+'_'+key, tooltip)
        for i in range(1,4):
          IconButton('mdi.format-header-'+str(i), self.btnText, buttonBarL, 'heading'+str(i)+'_'+key, \
                     'Heading '+str(i))
        rightSideL.addWidget(getattr(self, 'buttonBarW_'+key))
        setattr(self, 'textEdit_'+key, QPlainTextEdit(value))
        getattr(self, 'textEdit_'+key).setAccessibleName(key)
        getattr(self, 'textEdit_'+key).textChanged.connect(self.textChanged)
        setattr(self, 'textShow_'+key, QTextEdit(value))
        getattr(self, 'textShow_'+key).setReadOnly(True)
        getattr(self, 'textShow_'+key).hide()
        splitter= QSplitter()
        splitter.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        splitter.addWidget(getattr(self, 'textEdit_'+key))
        splitter.addWidget(getattr(self, 'textShow_'+key))
        rightSideL.addWidget(splitter)
        formL.addRow(labelW, rightSideW)
      elif key == '-tags':  #remove - to make work
        # TODO_P3: tags get selected via a editable QCombobox and get shown as qlabels, that can be deleted
        # RR: can you already implement tags as list of qlabels with a '-' button on the right to delete
        # the qcombox comes later once the database knows what tags are and how to generate the list
        print('')
      elif isinstance(value, list):       #list of items
        if isinstance(value[0], str):
          setattr(self, 'key_'+key, QLineEdit(' '.join(value)))
          formL.addRow(QLabel(key.capitalize()), getattr(self, 'key_'+key))
      elif isinstance(value, str):        #string
        ontologyItem = [i for i in ontologyNode if i['name']==key]
        if len(ontologyItem)==1 and 'list' in ontologyItem[0]:  #choice dropdown
          setattr(self, 'key_'+key, QComboBox())
          if ',' in ontologyItem[0]['list']:                    #defined choices
            getattr(self, 'key_'+key).addItems([i.strip() for i in ontologyItem[0]['list'].split(',')])
          else:                                                 #docType
            listDocType = ontologyItem[0]['list']
            getattr(self, 'key_'+key).addItem('- no link -', userData='')
            for line in self.comm.backend.db.getView('viewDocType/'+listDocType):
              getattr(self, 'key_'+key).addItem(line['value'][0], userData=line['id'])
              if line['id'] == value: #TODO_P5 what if names are identical
                getattr(self, 'key_'+key).setCurrentText(line['value'][0])
        else:                                         #text area
          setattr(self, 'key_'+key, QLineEdit(value))
        formL.addRow(QLabel(key.capitalize()), getattr(self, 'key_'+key))
      else:
        print("**ERROR unknown value type",key, value)
    self.projectComboBox = QComboBox()
    self.projectComboBox.addItem('- no change -', userData='')
    for line in self.comm.backend.db.getView('viewDocType/x0'):
      self.projectComboBox.addItem(line['value'][0], userData=line['id'])
    formL.addRow(QLabel('Project'), self.projectComboBox)
    self.docTypeComboBox = QComboBox()
    self.docTypeComboBox.addItem('- no change -', userData='')
    for key, value in self.comm.backend.db.dataLabels.items():
      if key[0]!='x':
        self.docTypeComboBox.addItem(value, userData=key)
    formL.addRow(QLabel('Data type'), self.docTypeComboBox)
    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel) #TODO_P5 next button does not exist; a list has to exist
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)

  # TODO_P5 add button to add key-values
  def save(self, btn):
    """
    Action upon save / cancel
    """
    if btn.text()=='Cancel':
      self.reject()
    elif btn.text()=='Save':
      if hasattr(self, 'key_-name'):
        self.doc['-name'] = getattr(self, 'key_-name').text().strip()
      for key, value in self.doc.items():
        if key[0] in ['_','-'] or key in ['image','metaVendor','metaUser'] or \
            (not hasattr(self, 'key_'+key) and not hasattr(self, 'textEdit_'+key)):
          continue
        if key in ['comment','content']:
          self.doc[key] = getattr(self, 'textEdit_'+key).toPlainText().strip()
        elif isinstance(value, list):
          self.doc[key] = getattr(self, 'key_'+key).text().strip().split(' ')
        elif isinstance(value, str):
          if isinstance(getattr(self, 'key_'+key), QComboBox):
            self.doc[key] = getattr(self, 'key_'+key).currentData()
          else:   #normal text field
            self.doc[key] = getattr(self, 'key_'+key).text().strip()
        else:
          print("**ERROR dialogeForm unknown value type",key, value)
      if '-branch' in self.doc:
        del self.doc['-branch']
      if self.projectComboBox.currentData() != '':
        parentPath = self.comm.backend.db.getDoc(self.projectComboBox.currentData())['-branch'][0]['path']
        self.doc['-branch'] = {'op':'u', 'stack':[self.projectComboBox.currentData()], 'childNum':9999, \
                               'path':parentPath}
      if self.docTypeComboBox.currentData() != '':
        self.doc['-type'] = [self.projectComboBox.currentData()]
        print("**WARNING: I ALSO SHOULD CHANGE DOCID") #TODO_P5
        #remove old, create new
      else:
        if '_ids' in self.doc:
          del self.doc['-name']
          ids = self.doc.pop('_ids')
          self.doc = {i:j for i,j in self.doc.items() if j!=''}
          for docID in ids:
            self.comm.backend.db.updateDoc(self.doc, docID)
        else: #default update
          self.comm.backend.db.updateDoc(self.doc, self.doc['_id'])
      #TODO_P5 execute redraw of table and details using self.comm
      self.accept()  #close
    return


  def btnAdvanced(self, status):
    """
    Action if advanced button is clicked
    TODO_P5 Think if all other form-elements should become hidden: show/hide form and hide/show text-boxes
    """
    key = self.sender().accessibleName()
    if status:
      getattr(self, 'textShow_'+key).hide()
      getattr(self, 'buttonBarW_'+key).hide()
    else:
      getattr(self, 'textShow_'+key).show()
      getattr(self, 'buttonBarW_'+key).show()
    return


  def btnText(self):
    """
    Add help to text area
    """
    command, key = self.sender().accessibleName().split('_')
    if command=='bold':
      getattr(self, 'textEdit_'+key).appendPlainText('**TEXT**')
    elif command=='italic':
      getattr(self, 'textEdit_'+key).appendPlainText('*TEXT*')
    elif command=='list-ul':
      getattr(self, 'textEdit_'+key).appendPlainText('\n- item 1\n- item 2')
    elif command=='list-ol':
      getattr(self, 'textEdit_'+key).appendPlainText('\n1. item 1\n1. item 2')
    elif command.startswith('heading'):
      getattr(self, 'textEdit_'+key).appendPlainText('\n\n'+'#'*int(command[-1])+' Heading')
    else:
      print('**ERROR dialogForm: unknowCommand',command)
    return


  def textChanged(self):
    """
    Text changed in editor -> update the display on the right
    """
    key = self.sender().accessibleName()
    getattr(self, 'textShow_'+key).setMarkdown( getattr(self, 'textEdit_'+key).toPlainText())
    return
