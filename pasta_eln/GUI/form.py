""" New/Edit dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
import logging, re, copy, subprocess, platform, os
from typing import Any, Union
from pathlib import Path
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QSplitter, QSizePolicy, QMenu # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QLabel, QTextEdit, QPushButton, QPlainTextEdit, QComboBox, QLineEdit # pylint: disable=no-name-in-module
from PySide6.QtGui import QRegularExpressionValidator # pylint: disable=no-name-in-module
from PySide6.QtCore import QSize, Qt, QPoint                  # pylint: disable=no-name-in-module
from ..guiStyle import Image, TextButton, IconButton, Label, Action, showMessage, widgetAndLayout
from ..fixedStringsJson import defaultOntologyNode
from ..handleDictionaries import fillDocBeforeCreate
from ..miscTools import createDirName
from ..guiCommunicate import Communicate

class Form(QDialog):
  """ New/Edit dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
  def __init__(self, comm:Communicate, doc:dict[str,Any]):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
      doc (dict):  document to change / create
    """
    super().__init__()
    self.comm = comm
    self.db   = self.comm.backend.db
    self.doc  = copy.deepcopy(doc)
    if '_attachments' in self.doc:
      del self.doc['_attachments']
    self.flagNewDoc = True
    if '_id' in self.doc or '_ids' in self.doc:
      self.flagNewDoc = False
    if self.flagNewDoc:
      self.setWindowTitle('Create new entry')
      self.doc['-name'] = ''
    else:
      self.setWindowTitle('Edit content')
    self.setMinimumWidth(600)

    # GUI elements
    mainL = QVBoxLayout(self)
    if 'image' in self.doc:
      width = self.comm.backend.configuration['GUI']['imageSizeDetails'] \
                  if hasattr(self.comm.backend, 'configuration') else 300
      imageW, imageL = widgetAndLayout('V', mainL)
      Image(self.doc['image'], imageL, anyDimension=width)
      imageW.setContextMenuPolicy(Qt.CustomContextMenu)
      imageW.customContextMenuRequested.connect(self.contextMenu)

    _, self.formL = widgetAndLayout('Form', mainL, 's')
    #Add things that are in ontology
    if '_ids' not in self.doc:  #normal form
      setattr(self, 'key_-name', QLineEdit(self.doc['-name']))
      getattr(self, 'key_-name').setValidator(QRegularExpressionValidator("[\\w\\ .-]+"))
      self.formL.addRow('Name', getattr(self, 'key_-name'))
    if self.doc['-type'][0] in self.db.ontology:
      ontologyNode = self.db.ontology[self.doc['-type'][0]]['prop']
    else:
      ontologyNode = defaultOntologyNode
    for item in ontologyNode:
      if item['name'] not in self.doc and  item['name'][0] not in ['_','-']:
        self.doc[item['name']] = ''
    # Create form
    if '-tags' not in self.doc:
      self.doc['-tags'] = []
    for key,value in self.doc.items():
      if (key[0] in ['_','-', '#'] and key!='-tags') or key in ['image','metaVendor','metaUser','shasum']:
        continue
      # print("Key:value in form | "+key+':'+str(value))
      if key in ['comment','content']:
        labelW, labelL = widgetAndLayout('V')
        labelL.addWidget(QLabel(key.capitalize()))
        TextButton('More', self.btnFocus, labelL, key, checkable=True)  # type: ignore # btnFocus req. bool, cannot get it to work
        rightSideW, rightSideL = widgetAndLayout('V')
        setattr(self, f'buttonBarW_{key}', QWidget())
        getattr(self, f'buttonBarW_{key}').hide()
        buttonBarL = QHBoxLayout(getattr(self, f'buttonBarW_{key}'))
        for name, tooltip in [['bold','Bold text'],['italic','Italic text'],['list-ul','Bullet list'],\
                                ['list-ol','Numbered list']]:
          IconButton(f'fa5s.{name}', self.btnText, buttonBarL, f'{name}_{key}', tooltip)
        for i in range(1,4):
          IconButton(
              f'mdi.format-header-{str(i)}',
              self.btnText,
              buttonBarL,
              f'heading{str(i)}_{key}',
              f'Heading {str(i)}',
          )
        rightSideL.addWidget(getattr(self, f'buttonBarW_{key}'))
        setattr(self, f'textEdit_{key}', QPlainTextEdit(value))
        getattr(self, f'textEdit_{key}').setAccessibleName(key)
        getattr(self, f'textEdit_{key}').textChanged.connect(self.textChanged)
        setattr(self, f'textShow_{key}', QTextEdit(value))
        getattr(self, f'textShow_{key}').setReadOnly(True)
        getattr(self, f'textShow_{key}').hide()
        splitter= QSplitter()
        splitter.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        splitter.addWidget(getattr(self, f'textEdit_{key}'))
        splitter.addWidget(getattr(self, f'textShow_{key}'))
        rightSideL.addWidget(splitter)
        self.formL.addRow(labelW, rightSideW)
      elif key == '-tags':
        tagsBarMainW, tagsBarMainL = widgetAndLayout('H', spacing='s')
        _, self.tagsBarSubL = widgetAndLayout('H', tagsBarMainL, spacing='s', right='m') #part which shows all the tags
        self.otherChoices = QComboBox()   #part/combobox that allow user to select
        self.otherChoices.setEditable(True)
        self.otherChoices.setMaximumWidth(100)
        self.otherChoices.setValidator(QRegularExpressionValidator("[a-z]\\w+"))
        self.otherChoices.setIconSize(QSize(0,0))
        self.otherChoices.setInsertPolicy(QComboBox.InsertAtBottom)
        tagsBarMainL.addWidget(self.otherChoices)
        self.gradeChoices = QComboBox()   #part/combobox that shows grades
        self.gradeChoices.setMaximumWidth(80)
        self.gradeChoices.setIconSize(QSize(0,0))
        self.gradeChoices.addItems(['','\u2605','\u2605'*2,'\u2605'*3,'\u2605'*4,'\u2605'*5])
        self.gradeChoices.currentTextChanged.connect(self.addTag)
        tagsBarMainL.addWidget(self.gradeChoices)
        self.formL.addRow(QLabel('Tags:'), tagsBarMainW)
        self.updateTagsBar()
        self.otherChoices.currentIndexChanged.connect(self.addTag) #connect to slot only after all painting is done
      elif isinstance(value, list):   #list of items, qrCodes in sample
        if len(value)>0 and isinstance(value[0], str):
          setattr(self, f'key_{key}', QLineEdit(' '.join(value)))
        else:
          setattr(self, f'key_{key}', QLineEdit('-- strange content --'))
        self.formL.addRow(QLabel(key.capitalize()), getattr(self, f'key_{key}'))
      elif isinstance(value, str):    #string
        ontologyItem = [i for i in ontologyNode if i['name']==key]
        if len(ontologyItem)==1 and 'list' in ontologyItem[0]:       #choice dropdown
          setattr(self, f'key_{key}', QComboBox())
          if isinstance(ontologyItem[0]['list'], list):            #ontology-defined choices
            getattr(self, f'key_{key}').addItems(ontologyItem[0]['list'])
          else:                                                    #choice among docType
            listDocType = ontologyItem[0]['list']
            getattr(self, f'key_{key}').addItem('- no link -', userData='')
            for line in self.db.getView(f'viewDocType/{listDocType}'):
              getattr(self, f'key_{key}').addItem(line['value'][0], userData=line['id'])
              if line['value'][0] == value:
                getattr(self, f'key_{key}').setCurrentText(line['value'][0])
        else:                                   #text area
          setattr(self, f'key_{key}', QLineEdit(value))
        self.formL.addRow(QLabel(key.capitalize()), getattr(self, f'key_{key}'))
      else:
        print("**ERROR dialogForm: unknown value type",key, value)
    #add extra questions at bottom of form
    allowProjectAndDocTypeChange = '_id' in self.doc and self.doc['-type'][0][0]!='x'
    if '_ids' in self.doc: #if group edit
      allowProjectAndDocTypeChange = not any(docID[0]=='x' for docID in self.doc['_ids'])
    if allowProjectAndDocTypeChange: #if not-new and non-folder
      self.formL.addRow(QLabel('Special properties:'), QLabel('') )
    label = '- unassigned -' if self.flagNewDoc else '- no change -'
    if allowProjectAndDocTypeChange or ('_id' not in self.doc and self.doc['-type'][0][0]!='x'): #if new and non-folder
      self.projectComboBox = QComboBox()
      self.projectComboBox.addItem(label, userData='')
      for line in self.db.getView('viewDocType/x0'):
        if not '-branch' in self.doc or not any(line['id']==branch['stack'][0] for branch in self.doc['-branch']):
          self.projectComboBox.addItem(line['value'][0], userData=line['id'])
      self.formL.addRow(QLabel('Project'), self.projectComboBox)
    if allowProjectAndDocTypeChange: #if not-new and non-folder
      self.docTypeComboBox = QComboBox()
      self.docTypeComboBox.addItem(label, userData='')
      for key, value in self.db.dataLabels.items():
        if key[0]!='x':
          self.docTypeComboBox.addItem(value, userData=key)
      self.docTypeComboBox.addItem('_UNIDENTIFIED_', userData='-')
      self.formL.addRow(QLabel('Data type'), self.docTypeComboBox)
    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Save)
    if self.flagNewDoc: #new dataset
      buttonBox.addButton('Save && Next', QDialogButtonBox.ApplyRole)
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)

  # TODO_P2 make markdown format correctly immediately
  # TODO_P2 move folder to different folder: use unidentified for notes
  # TODO_P4 add splitter to increase / decrease image
  # TODO_P3 form: add button to add key-values
  # TODO_P3 form: other items as non-edible things that can be copy-pasted
  def save(self, btn:QPushButton) -> None:
    # sourcery skip: merge-else-if-into-elif
    """
    Action upon save / cancel
    """
    if self.otherChoices.hasFocus():
      return
    if btn.text().endswith('Cancel'):
      self.reject()
    elif 'Save' in btn.text():
      # create the data that has to be saved
      if hasattr(self, 'key_-name'):
        self.doc['-name'] = getattr(self, 'key_-name').text().strip()
        if self.doc['-name'] == '':
          showMessage(self, 'Error', 'A created item has to have a valid name')
          return
        if self.doc['-type'][0]=='x0':  #prevent project-directory names that are identical
          others = self.comm.backend.db.getView('viewDocType/x0All')
          if '_id' in self.doc:
            others = [i for i in others if i['id']!=self.doc['_id']] # create list of names but filter own name
          others = [i['value'][0] for i in others]
          othersList = [createDirName(str(i),'x0', 0) for i in others] #create names
          while createDirName(self.doc['-name'],'x0', 0) in othersList:
            if re.search(r"_\d+$", self.doc['-name']) is None:
              self.doc['-name'] += '_1'
            else:
              self.doc['-name'] = '_'.join(self.doc['-name'].split('_')[:-1])+'_'+str(int(self.doc['-name'].split('_')[-1])+1)
      # loop through all the subitems
      for key, valueOld in self.doc.items():
        if (key[0] in ['_', '-'] or key in ['image', 'metaVendor', 'metaUser']
            or not hasattr(self, f'key_{key}') and not hasattr(self, f'textEdit_{key}')):
          continue
        if key in ['comment','content']:
          text = getattr(self, f'textEdit_{key}').toPlainText().strip()
          if not ('_ids' in self.doc and not text):  #if group edit, text has to have text
            self.doc[key] = text
            if key == 'content' and '-branch' in self.doc:
              for branch in self.doc['-branch']:
                if branch['path'] is not None:
                  if branch['path'].endswith('.md'):  #TODO_P5 only write markdown files for now
                    with open(self.comm.backend.basePath/branch['path'], 'w', encoding='utf-8') as fOut:
                      fOut.write(self.doc['content'])
                    logging.debug('Wrote new content to '+branch['path'])
                  else:
                    showMessage(self, 'Information', 'Did update the database but not the file on harddisk, since PASTA-ELN cannot write this format')
        elif isinstance(valueOld, list):  #items that are comma separated in the text-field
          self.doc[key] = getattr(self, f'key_{key}').text().strip().split(' ')
        elif isinstance(valueOld, str):
          if isinstance(getattr(self, f'key_{key}'), QComboBox):
            valueNew = getattr(self, f'key_{key}').currentText()
            if (valueNew != '- no link -'
                and getattr(self, f'key_{key}').currentData() is not None
                and re.search(
                    r"^[a-z\-]-[a-z0-9]{32}$",
                    getattr(self, f'key_{key}').currentData(),
                ) is not None):
              #if docID is stored in currentData
              self.doc[key] = getattr(self, f'key_{key}').currentData()
            elif valueNew!='- no link -' :
              self.doc[key] = valueNew
          else:                          #normal text field
            self.doc[key] = getattr(self, f'key_{key}').text().strip()
        elif valueOld is None and key in self.doc:  #important entry, set to empty string
          self.doc[key]=''
        else:
          print("**ERROR dialogForm unknown value type",key, valueOld)
      # ---- if project changed: only branch save; remaining data still needs saving
      newProjID = []
      if hasattr(self, 'projectComboBox') and self.projectComboBox.currentData() != '':
        parentPath = self.db.getDoc(self.projectComboBox.currentData())['-branch'][0]['path']
        if '_ids' in self.doc:  # group update
          for docID in self.doc['_ids']:
            doc = self.db.getDoc(docID)
            if doc['-branch'][0]['stack']!=self.projectComboBox.currentData(): #only if project changed
              if doc['-branch'][0]['path'] is None:
                newPath    = ''
              else:
                oldPath    = self.comm.backend.basePath/doc['-branch'][0]['path']
                newPath = f'{parentPath}/{oldPath.name}'
                oldPath.rename(self.comm.backend.basePath/newPath)
              self.db.updateBranch( doc['_id'], 0, 9999, [self.projectComboBox.currentData()], newPath)
        elif '-branch' in self.doc:             # sequential or single update
          if self.doc['-branch'][0]['stack']!=self.projectComboBox.currentData(): #only if project changed
            if self.doc['-branch'][0]['path'] is None:
              newPath    = ''
            else:
              oldPath    = self.comm.backend.basePath/self.doc['-branch'][0]['path']
              newPath = f'{parentPath}/{oldPath.name}'
            self.db.updateBranch( self.doc['_id'], 0, 9999, [self.projectComboBox.currentData()], newPath)
        else:
          newProjID = [self.projectComboBox.currentData()]
      # ---- if docType changed: save; no further save to db required ----
      if hasattr(self, 'docTypeComboBox') and self.docTypeComboBox.currentData() != '':
        self.doc['-type'] = [self.docTypeComboBox.currentData()]
        if '_ids' in self.doc: #group update
          for docID in self.doc.pop('_ids'):
            doc = self.db.getDoc(docID)
            doc.update( self.doc )
            self.db.remove(doc['_id'])
            del doc['_id']
            del doc['_rev']
            doc = fillDocBeforeCreate(doc, self.docTypeComboBox.currentData())
            self.db.saveDoc(doc)
        else:                  #single or sequential update
          self.db.remove(self.doc['_id'])
          del self.doc['_id']
          del self.doc['_rev']
          self.doc = fillDocBeforeCreate(self.doc, self.docTypeComboBox.currentData())
          self.db.saveDoc(self.doc)
      # ---- all other changes ----
      else:
        if '_ids' in self.doc: #group update
          if '-name' in self.doc:
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
          self.comm.backend.addData(self.doc['-type'][0], copy.deepcopy(self.doc), newProjID)
      #!!! NO updates / redraw here since one does not know from where form came
      # e.g. sequential edit cannot have redraw here
      if btn.text().endswith('Next'):
        for delKey in [i for i in self.doc.keys() if i[0] in ['-','_'] and i not in ['-name','-type','-tags']]:
          del self.doc[delKey]
        self.comm.changeTable.emit('', '')
      else:
        self.accept()  #close
        self.close()
    else:
      print('dialogForm: did not get a fitting btn ',btn.text())
    return


  def contextMenu(self, pos:QPoint) -> None:
    # sourcery skip: extract-method
    """
    Create a context menu

    Args:
      pos (position): Position to create context menu at
    """
    context = QMenu(self)
    # for extractors
    extractors = self.comm.backend.configuration['extractors']
    extension = Path(self.doc['-branch'][0]['path']).suffix[1:]
    if extension.lower() in extractors:
      extractors = extractors[extension.lower()]
      baseDocType= self.doc['-type'][0]
      choices= {key:value for key,value in extractors.items() \
                  if key.startswith(baseDocType)}
      for key,value in choices.items():
        Action(value, self.changeExtractor, context, self, name=key)
      context.addSeparator()
      Action('Save image',                       self.changeExtractor, context, self, name='_saveAsImage_')
    #TODO_P2 not save now: when opening text files, system can crash
    # Action('Open file with another application', self.changeExtractor, context, self, name='_openExternal_')
    Action('Open folder in file browser',        self.changeExtractor, context, self, name='_openInFileBrowser_')
    context.exec(self.mapToGlobal(pos))
    return


  def changeExtractor(self) -> None:
    """
    What happens when user changes extractor
    """
    menuName = self.sender().data()
    filePath = Path(self.doc['-branch'][0]['path'])
    if menuName in ['_openInFileBrowser_','_openExternal_']:
      filePath = self.comm.backend.basePath/filePath
      filePath = filePath if menuName=='_openExternal_' else filePath.parent
      if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filePath))
      elif platform.system() == 'Windows':    # Windows
        os.startfile(filePath) # type: ignore[attr-defined]
      else:                                   # linux variants
        subprocess.call(('xdg-open', filePath))
    elif menuName =='_saveAsImage_':
      image = self.doc['image']
      if image.startswith('data:image/'):
        imageType = image[11:14] if image[14]==';' else image[11:15]
      else:
        imageType = 'svg'
      saveFilePath = self.comm.backend.basePath/filePath.parent/f'{filePath.stem}_PastaExport.{imageType.lower()}'
      path = Path(self.doc['-branch'][0]['path'])
      if not path.as_posix().startswith('http'):
        path = self.comm.backend.basePath/path
      self.comm.backend.testExtractor(path, recipe='/'.join(self.doc['-type']), saveFig=str(saveFilePath))
    else:
      self.doc['-type'] = menuName.split('/')
      self.comm.backend.useExtractors(filePath, self.doc['shasum'], self.doc)  #any path is good since the file is the same everywhere; data-changed by reference
      if len(self.doc['-type'])>1 and len(self.doc['image'])>1:
        self.doc = self.comm.backend.db.updateDoc({'image':self.doc['image'], '-type':self.doc['-type']}, self.doc['_id'])
        self.comm.changeTable.emit('','')
        self.comm.changeDetails.emit(self.doc['_id'])
    return


  def btnFocus(self, status:bool) -> None:
    """
    Action if advanced button is clicked
    """
    key = self.sender().accessibleName()  #comment or content
    unknownWidget = []
    if status:
      getattr(self, f'textShow_{key}').hide()
      getattr(self, f'buttonBarW_{key}').hide()
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
      getattr(self, f'textShow_{key}').show()
      getattr(self, f'buttonBarW_{key}').show()
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


  def btnText(self) -> None:
    """
    Add help to text area
    """
    command, key = self.sender().accessibleName().split('_')
    if command=='bold':
      getattr(self, f'textEdit_{key}').insertPlainText('**TEXT**')
    elif command=='italic':
      getattr(self, f'textEdit_{key}').insertPlainText('*TEXT*')
    elif command=='list-ul':
      getattr(self, f'textEdit_{key}').insertPlainText('\n- item 1\n- item 2')
    elif command=='list-ol':
      getattr(self, f'textEdit_{key}').insertPlainText('\n1. item 1\n1. item 2')
    elif command.startswith('heading'):
      getattr(self, f'textEdit_{key}').insertPlainText('#' * int(command[-1]) +
                                                       ' Heading\n')
    else:
      print('**ERROR dialogForm: unknowCommand',command)
    return

  def textChanged(self) -> None:
    """
    Text changed in editor -> update the display on the right
    """
    key = self.sender().accessibleName()
    getattr(self, f'textShow_{key}').setMarkdown(
        getattr(self, f'textEdit_{key}').toPlainText())
    return

  def delTag(self, _:str, tag:str) -> None:
    """
    Clicked button to delete tag
    """
    self.doc['-tags'].remove(tag)
    self.updateTagsBar()
    return

  def addTag(self, tag:Union[str,int]) -> None:
    """
    Clicked to add tag. Since one needs to use indexChanged to allow the user to enter text, that delivers a int. To allow to differentiate
    between both comboboxes, they cannot be the same (both int), hence grades has to be textChanged

    Args:
      tag (str, int): index (otherTags) or text (grades)
    """
    if isinstance(tag, str):#text from grades
      if tag!='':
        self.doc['-tags'] = [i for i in self.doc['-tags'] if i[0]!='_']
        self.doc['-tags'] += [f'_{len(tag)}']
        self.gradeChoices.setCurrentText('')
    elif tag<1:               #zero index from other-tags
      return
    else:
      tag = self.otherChoices.currentText()
      if tag not in self.doc['-tags']:
        self.doc['-tags'] += [tag]
      self.otherChoices.setCurrentText('')
    self.updateTagsBar()
    return


  def updateTagsBar(self) -> None:
    """
    After creation, tag removal, tag addition: update the information on screen
    """
    #update tags
    for i in reversed(range(self.tagsBarSubL.count())):
      self.tagsBarSubL.itemAt(i).widget().setParent(None)  # type: ignore
    for tag in self.doc['-tags']:
      if tag in ['_curated']:
        continue
      if tag[0]=='_':
        Label('\u2605'*int(tag[1]), 'h3', self.tagsBarSubL, self.delTag, tag, 'click to remove')
      else:
        Label(tag, 'h3', self.tagsBarSubL, self.delTag, tag, 'click to remove')
    self.tagsBarSubL.addWidget(QWidget(), stretch=2)  # type: ignore
    #update choices in combobox
    tagsAllList = self.comm.backend.db.getView('viewIdentify/viewTagsAll')
    tagsSet = {i['key'] for i in tagsAllList if i['key'][0]!='_'}
    newChoicesList = ['']+list(tagsSet.difference([i for i in self.doc['-tags'] if i[0]!='_']))
    self.otherChoices.clear()
    self.otherChoices.addItems(newChoicesList)
    return