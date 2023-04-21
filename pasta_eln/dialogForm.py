""" New/Edit dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
import json, logging
from pathlib import Path
from PySide6.QtWidgets import QDialog, QWidget, QFormLayout, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, \
                              QPlainTextEdit, QComboBox, QLineEdit, QDialogButtonBox, QSplitter, QSizePolicy, QPushButton # pylint: disable=no-name-in-module
from PySide6.QtGui import QPixmap, QImage, QRegularExpressionValidator # pylint: disable=no-name-in-module
from .style import Image, TextButton, IconButton
from .fixedStrings import defaultOntologyNode
from .handleDictionaries import fillDocBeforeCreate

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
    self.db   = self.comm.backend.db
    self.doc  = dict(doc)
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
      Image(self.doc['image'], mainL, height=width)
    formW = QWidget()
    mainL.addWidget(formW)
    self.formL = QFormLayout(formW)

    #Add things that are in ontology
    if '-type' in self.doc and '_ids' not in self.doc:  #normal form
      setattr(self, 'key_-name', QLineEdit(self.doc['-name']))
      getattr(self, 'key_-name').setValidator(QRegularExpressionValidator("[\\w\\ .]+"))
      self.formL.addRow('Name', getattr(self, 'key_-name'))
      if self.doc['-type'][0] in self.db.ontology:
        ontologyNode = self.db.ontology[self.doc['-type'][0]]['prop']
      else:
        ontologyNode = defaultOntologyNode
      for item in ontologyNode:
        if item['name'] not in self.doc and  item['name'][0] not in ['_','-']:
          self.doc[item['name']] = ''
    if '-type' not in self.doc and '_ids' in self.doc:  #group edit form
      ontologyNode = defaultOntologyNode
      ontologyNode = [i for i in ontologyNode if i['name']!='-name']
    # Create form
    for key,value in self.doc.items():
      if (key[0] in ['_','-', '#'] and key!='-tags') or key in ['image','metaVendor','metaUser','shasum']:
        continue
      # print("Key:value in form | "+key+':'+str(value))
      if key in ['comment','content']:
        labelW = QWidget()
        labelL = QVBoxLayout(labelW)
        labelL.addWidget(QLabel(key.capitalize()))
        TextButton('Focus', self.btnFocus, labelL, key, checkable=True)
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
        self.formL.addRow(labelW, rightSideW)
      elif key == '-tags':
        print('tagggs', self.comm.dbInfo['tags'])
        #TODO_P2 tags: get selected via a editable QCombobox and get shown as qlabels, that can be deleted
        # RR: can you already implement tags as list of qlabels with a '-' button on the right to delete
        # the qcombox comes later once the database knows what tags are and how to generate the list
      elif isinstance(value, list):       #list of items, qrCodes in sample
        if len(value)>0 and isinstance(value[0], str):
          setattr(self, 'key_'+key, QLineEdit(' '.join(value)))
        else:
          setattr(self, 'key_'+key, QLineEdit('-- strange content --'))
        self.formL.addRow(QLabel(key.capitalize()), getattr(self, 'key_'+key))
      elif isinstance(value, str):        #string
        ontologyItem = [i for i in ontologyNode if i['name']==key]
        if len(ontologyItem)==1 and 'list' in ontologyItem[0]:             #choice dropdown
          setattr(self, 'key_'+key, QComboBox())
          if isinstance(ontologyItem[0]['list'], list):                    #ontology-defined choices
            getattr(self, 'key_'+key).addItems(ontologyItem[0]['list'])
          else:                                                            #choice among docType
            listDocType = ontologyItem[0]['list']
            getattr(self, 'key_'+key).addItem('- no link -', userData='')
            for line in self.db.getView('viewDocType/'+listDocType):
              getattr(self, 'key_'+key).addItem(line['value'][0], userData=line['id'])
              if line['value'][0] == value:
                getattr(self, 'key_'+key).setCurrentText(line['value'][0])
        else:                                         #text area
          setattr(self, 'key_'+key, QLineEdit(value))
        self.formL.addRow(QLabel(key.capitalize()), getattr(self, 'key_'+key))
      else:
        print("**ERROR dialogForm: unknown value type",key, value)
    #add extra questions at bottom of form
    allowProjectAndDocTypeChange = '_id' in self.doc and self.doc['-type'][0][0]!='x'
    if '_ids' in self.doc: #if group edit
      allowProjectAndDocTypeChange = True
      for docID in self.doc['_ids']:
        if docID[0]=='x':
          allowProjectAndDocTypeChange = False
    if allowProjectAndDocTypeChange: #if not-new and non-folder
      self.formL.addRow(QLabel('Special properties:'), QLabel('') )
      self.projectComboBox = QComboBox()
      self.projectComboBox.addItem('- no change -', userData='')
      for line in self.db.getView('viewDocType/x0'):
        self.projectComboBox.addItem(line['value'][0], userData=line['id'])
      self.formL.addRow(QLabel('Project'), self.projectComboBox)
      self.docTypeComboBox = QComboBox()
      self.docTypeComboBox.addItem('- no change -', userData='')
      for key, value in self.db.dataLabels.items():
        if key[0]!='x':
          self.docTypeComboBox.addItem(value, userData=key)
      self.formL.addRow(QLabel('Data type'), self.docTypeComboBox)
    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Save)
    if self.doc['-name']=='': #new dataset
      buttonBox.addButton('Save && Next', QDialogButtonBox.ApplyRole)
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)

  # TODO_P3 add splitter to increase / decrease image
  # TODO_P3 form: add button to add key-values
  # TODO_P3 other items as non-edible things that can be copy-pasted
  def save(self, btn):
    """
    Action upon save / cancel
    """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif 'Save' in btn.text():
      # create the data that has to be saved
      if hasattr(self, 'key_-name'):
        self.doc['-name'] = getattr(self, 'key_-name').text().strip()
      for key, value in self.doc.items():
        if key[0] in ['_','-'] or key in ['image','metaVendor','metaUser'] or \
            (not hasattr(self, 'key_'+key) and not hasattr(self, 'textEdit_'+key)):
          continue
        if key in ['comment','content']:
          self.doc[key] = getattr(self, 'textEdit_'+key).toPlainText().strip()
          if key == 'content':
            for branch in self.doc['-branch']:
              if branch['path'] is not None and branch['path'].endswith('.md'):  #TODO_P5 only write markdown files for now
                with open(self.comm.backend.basePath/branch['path'], 'w', encoding='utf-8') as fOut:
                  fOut.write(self.doc['content'])
                logging.debug('Wrote new content to '+branch['path'])
        elif isinstance(value, list):
          self.doc[key] = getattr(self, 'key_'+key).text().strip().split(' ')
        elif isinstance(value, str):
          if isinstance(getattr(self, 'key_'+key), QComboBox):
            value         = getattr(self, 'key_'+key).currentText()
            if value!='- no link -':
              self.doc[key] = getattr(self, 'key_'+key).currentData()
          else:   #normal text field
            self.doc[key] = getattr(self, 'key_'+key).text().strip()
        else:
          print("**ERROR dialogForm unknown value type",key, value)
      # ---- if project changed: only branch save; remaining data still needs saving
      if hasattr(self, 'projectComboBox') and self.projectComboBox.currentData() != '':
        parentPath = self.db.getDoc(self.projectComboBox.currentData())['-branch'][0]['path']
        if '_ids' in self.doc:  # group update
          for docID in self.doc['_ids']:
            doc = self.db.getDoc(docID)
            if doc['-branch'][0]['stack']!=self.projectComboBox.currentData(): #only if project changed
              if doc['-branch'][0]['path'] is None:
                newPath    = None
              else:
                oldPath    = self.comm.backend.basePath/doc['-branch'][0]['path']
                newPath    = parentPath+'/'+oldPath.name
                oldPath.rename(self.comm.backend.basePath/newPath)
              self.db.updateBranch( doc['_id'], 0, 9999, [self.projectComboBox.currentData()], newPath)
        else:                   # sequential or single update
          if self.doc['-branch'][0]['stack']!=self.projectComboBox.currentData(): #only if project changed
            if self.doc['-branch'][0]['path'] is None:
              newPath    = None
            else:
              oldPath    = self.comm.backend.basePath/self.doc['-branch'][0]['path']
              newPath    = parentPath+'/'+oldPath.name
              oldPath.rename(self.comm.backend.basePath/newPath)
            self.db.updateBranch( self.doc['_id'], 0, 9999, [self.projectComboBox.currentData()], newPath)
      # ---- if docType changed: save; no further save to db required ----
      if hasattr(self, 'docTypeComboBox') and self.docTypeComboBox.currentData() != '':
        self.doc['-type'] = [self.docTypeComboBox.currentData()]
        if '_ids' in self.doc: #group update
          for docID in self.doc.pop('_ids'):
            doc = self.db.getDoc(docID)
            self.db.remove(doc['_id'])
            del doc['_id']
            del doc['_rev']
            doc['-name'] = doc['-branch'][0]['path']
            self.comm.backend.addData(self.docTypeComboBox.currentData(), doc, doc['-branch'][0]['stack'])
        else:                  #single or sequential update
          self.db.remove(self.doc['_id'])
          del self.doc['_id']
          del self.doc['_rev']
          self.comm.backend.addData(self.docTypeComboBox.currentData(), self.doc, self.doc['-branch'][0]['stack'])
      else:
        if '_ids' in self.doc: #group update
          del self.doc['-name']
          ids = self.doc.pop('_ids')
          self.doc = {i:j for i,j in self.doc.items() if j!=''}
          for docID in ids:
            doc = self.db.getDoc(docID)
            doc.update( self.doc )
            self.comm.backend.editData(doc)
        elif '_id' in self.doc:                                   #default update on item
          self.comm.backend.editData(self.doc)
        else:                                                     #create new dataset
          self.comm.backend.addData(self.doc['-type'][0], self.doc)
      #!!! NO updates / redraw here since one does not know from where form came
      # e.g. sequential edit cannot have redraw here
      if btn.text().endswith('Next'):
        for delKey in [i for i in self.doc.keys() if i[0] in ['-','_'] and i not in ['-name','-type']]:
          del self.doc[delKey]
      else:
        self.accept()  #close
    else:
      print('dialogForm: did not get a fitting btn ',btn.text())
    return



  def btnFocus(self, status):
    """
    Action if advanced button is clicked
    """
    key = self.sender().accessibleName()  #comment or content
    unknownWidget = []
    if status:
      getattr(self, 'textShow_'+key).hide()
      getattr(self, 'buttonBarW_'+key).hide()
      for i in range(self.formL.count()):
        widget = self.formL.itemAt(i).widget()
        if isinstance(widget, (QLabel, QComboBox, QLineEdit)):
          widget.show()
        else:
          unknownWidget.append(i)
      if key=='content' and len(unknownWidget)==4:  #show / hide label and right-side of non-content and non-comment
        self.formL.itemAt(unknownWidget[0]).widget().show()
        self.formL.itemAt(unknownWidget[1]).widget().show()
      if key=='comment' and len(unknownWidget)==4:
        self.formL.itemAt(unknownWidget[2]).widget().show()
        self.formL.itemAt(unknownWidget[3]).widget().show()
    else:
      getattr(self, 'textShow_'+key).show()
      getattr(self, 'buttonBarW_'+key).show()
      for i in range(self.formL.count()):
        widget = self.formL.itemAt(i).widget()
        if isinstance(widget, (QLabel, QComboBox, QLineEdit)):
          widget.hide()
        else:
          unknownWidget.append(i)
      if key=='content' and len(unknownWidget)==4:
        self.formL.itemAt(unknownWidget[0]).widget().hide()
        self.formL.itemAt(unknownWidget[1]).widget().hide()
      if key=='comment' and len(unknownWidget)==4:
        self.formL.itemAt(unknownWidget[2]).widget().hide()
        self.formL.itemAt(unknownWidget[3]).widget().hide()
    return


  def btnText(self):
    """
    Add help to text area
    """
    command, key = self.sender().accessibleName().split('_')
    if command=='bold':
      getattr(self, 'textEdit_'+key).insertPlainText('**TEXT**')
    elif command=='italic':
      getattr(self, 'textEdit_'+key).insertPlainText('*TEXT*')
    elif command=='list-ul':
      getattr(self, 'textEdit_'+key).insertPlainText('\n- item 1\n- item 2')
    elif command=='list-ol':
      getattr(self, 'textEdit_'+key).insertPlainText('\n1. item 1\n1. item 2')
    elif command.startswith('heading'):
      getattr(self, 'textEdit_'+key).insertPlainText('#'*int(command[-1])+' Heading\n')
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
