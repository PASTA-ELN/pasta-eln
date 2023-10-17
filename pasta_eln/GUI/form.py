""" New/Edit dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
import logging, re, copy, json
from enum import Enum
from pathlib import Path
from typing import Any, Union
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QSplitter  # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QLabel, QTextEdit, QPushButton, QPlainTextEdit, QComboBox, QLineEdit     # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QSizePolicy, QMessageBox# pylint: disable=no-name-in-module
from PySide6.QtGui import QRegularExpressionValidator # pylint: disable=no-name-in-module
from PySide6.QtCore import QSize, Qt, QTimer          # pylint: disable=no-name-in-module
from ..guiStyle import Image, TextButton, IconButton, Label, showMessage, widgetAndLayout
from ._contextMenu import initContextMenu, executeContextMenu, CommandMenu
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
      imageW, self.imageL = widgetAndLayout('V', mainL)
      Image(self.doc['image'], self.imageL, anyDimension=width)
      if '_id' in self.doc:
        self.docID= doc['_id']  #required for hide to work
        imageW.setContextMenuPolicy(Qt.CustomContextMenu)
        imageW.customContextMenuRequested.connect(lambda pos: initContextMenu(self, pos))

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
    for item in [i for group in ontologyNode for i in ontologyNode[group]]:
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
        TextButton('More', self, [Command.FOCUS_AREA, key], labelL, checkable=True)
        rightSideW, rightSideL = widgetAndLayout('V')
        setattr(self, f'buttonBarW_{key}', QWidget())
        getattr(self, f'buttonBarW_{key}').hide()
        buttonBarL = QHBoxLayout(getattr(self, f'buttonBarW_{key}'))
        for name, tooltip in [['bold','Bold text'],['italic','Italic text'],['list-ul','Bullet list'],\
                                    ['list-ol','Numbered list']]:
          IconButton(f'fa5s.{name}', self, [Command.BUTTON_BAR, name, key], buttonBarL, tooltip)
        for i in range(1,4):
          icon = f'mdi.format-header-{str(i)}'
          IconButton(icon, self, [Command.BUTTON_BAR, f'heading{str(i)}', key], buttonBarL, f'Heading {str(i)}')
        rightSideL.addWidget(getattr(self, f'buttonBarW_{key}'))
        setattr(self, f'textEdit_{key}', QPlainTextEdit(value))
        getattr(self, f'textEdit_{key}').setAccessibleName(key)
        getattr(self, f'textEdit_{key}').setTabStopDistance(20)
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
        ontologyItem = [i for group in ontologyNode for i in ontologyNode[group] if i['name']==key]
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
      allowProjectAndDocTypeChange = all(docID[0] != 'x' for docID in self.doc['_ids'])
    if allowProjectAndDocTypeChange: #if not-new and non-folder
      self.formL.addRow(QLabel('Special properties:'), QLabel('') )
    label = '- unassigned -' if self.flagNewDoc else '- no change -'
    if allowProjectAndDocTypeChange or ('_id' not in self.doc and self.doc['-type'][0][0]!='x'): #if new and non-folder
      self.projectComboBox = QComboBox()
      self.projectComboBox.addItem(label, userData='')
      for line in self.db.getView('viewDocType/x0'):
        # add all projects but the one that is present
        if '-branch' not in self.doc or all(line['id']!=branch['stack'][0] for branch in self.doc['-branch'] \
                                            if len(branch['stack'])>0):
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
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)

    if (Path.home()/'.pastaELN.temp').exists():
      with open(Path.home()/'.pastaELN.temp', 'r', encoding='utf-8') as fTemp:
        content = json.loads(fTemp.read())
        for key in self.doc.keys():
          if key[0] in ['_','-', '#'] or key in ['image','metaVendor','metaUser','shasum'] or \
             key not in content:
            continue
          if key in ['comment','content']:
            getattr(self, f'textEdit_{key}').setPlainText(content[key])
          else:
            getattr(self, f'key_{key}').setText(content[key])
    self.checkThreadTimer = QTimer(self)
    self.checkThreadTimer.setInterval(1*60*1000) #5 min
    self.checkThreadTimer.timeout.connect(self.autosave)
    self.checkThreadTimer.start()


  def autosave(self) -> None:
    """ Autosave comment to file """
    content = {'-name': getattr(self, 'key_-name').text().strip()}
    for key in self.doc.keys():
      if key[0] in ['_','-', '#'] or key in ['image','metaVendor','metaUser','shasum']:
        continue
      if key in ['comment','content']:
        content[key] = getattr(self, f'textEdit_{key}').toPlainText().strip()
      elif isinstance(getattr(self, f'key_{key}'), QComboBox):
        content[key] = getattr(self, f'key_{key}').currentText().strip()
      else:                                            #all text fields
        content[key] = getattr(self, f'key_{key}').text().strip()
    with open(Path.home()/'.pastaELN.temp', 'w', encoding='utf-8') as fTemp:
      fTemp.write(json.dumps(content))
    return


  def closeDialog(self, btn:QPushButton) -> None:
    """
    Action upon save / cancel
    """
    if self.otherChoices.hasFocus():
      return
    if btn.text().endswith('Cancel'):
      ret = QMessageBox.critical(self, 'Warning', 'You will loose all entered data. Do you want to save the '+\
                                 'content for next time?',
                                 QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
      if ret==QMessageBox.StandardButton.No:
        self.checkThreadTimer.stop()
        if (Path.home()/'.pastaELN.temp').exists():
          (Path.home()/'.pastaELN.temp').unlink()
      self.reject()
    elif 'Save' in btn.text():
      # create the data that has to be saved
      self.checkThreadTimer.stop()
      if (Path.home()/'.pastaELN.temp').exists():
        (Path.home()/'.pastaELN.temp').unlink()
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
          if '_ids' not in self.doc or text:  #if group edit, text has to have text
            self.doc[key] = text
            if key == 'content' and '-branch' in self.doc:
              for branch in self.doc['-branch']:
                if branch['path'] is not None:
                  if branch['path'].endswith('.md'):
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
              oldPath = self.comm.backend.basePath/self.doc['-branch'][0]['path']
              newPath = f'{parentPath}/{oldPath.name}'
            self.db.updateBranch( self.doc['_id'], 0, 9999, [self.projectComboBox.currentData()], newPath)
            self.doc['-branch'][0] = {'stack':[self.projectComboBox.currentData()], 'path':newPath or None, 'child':9999, 'show':[True,True]}
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


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks button

    Args:
      command (list): list of commands
    """
    if isinstance(command[0], CommandMenu):
      if executeContextMenu(self, command):
        self.imageL.itemAt(0).widget().setParent(None)   # type: ignore
        width = self.comm.backend.configuration['GUI']['imageSizeDetails'] \
                if hasattr(self.comm.backend, 'configuration') else 300
        Image(self.doc['image'], self.imageL, anyDimension=width)
    elif command[0] is Command.BUTTON_BAR:
      if command[1]=='bold':
        getattr(self, f'textEdit_{command[2]}').insertPlainText('**TEXT**')
      elif command[1]=='italic':
        getattr(self, f'textEdit_{command[2]}').insertPlainText('*TEXT*')
      elif command[1]=='list-ul':
        getattr(self, f'textEdit_{command[2]}').insertPlainText('\n- item 1\n- item 2')
      elif command[1]=='list-ol':
        getattr(self, f'textEdit_{command[2]}').insertPlainText('\n1. item 1\n1. item 2')
      elif command[1].startswith('heading'):
        getattr(self, f'textEdit_{command[2]}').insertPlainText('#' * int(command[1][-1]) +' Heading\n')
    elif command[0] is Command.FOCUS_AREA:
      unknownWidget = []
      if getattr(self, f'buttonBarW_{command[1]}').isHidden(): #current status hidden
        getattr(self, f'textShow_{command[1]}').show()
        getattr(self, f'buttonBarW_{command[1]}').show()
        for i in range(self.formL.count()):
          widget = self.formL.itemAt(i).widget()
          if isinstance(widget, (QLabel, QComboBox, QLineEdit)):
            widget.hide()
          else:
            unknownWidget.append(i)
        if command[1]=='content' and len(unknownWidget)==5:
          self.formL.itemAt(unknownWidget[0]).widget().hide()
          self.formL.itemAt(unknownWidget[1]).widget().hide()
        if command[1]=='comment' and len(unknownWidget)==5:
          self.formL.itemAt(unknownWidget[2]).widget().hide()
          self.formL.itemAt(unknownWidget[3]).widget().hide()
      else:
        getattr(self, f'textShow_{command[1]}').hide()
        getattr(self, f'buttonBarW_{command[1]}').hide()
        for i in range(self.formL.count()):
          widget = self.formL.itemAt(i).widget()
          if isinstance(widget, (QLabel, QComboBox, QLineEdit)):
            widget.show()
          else:
            unknownWidget.append(i)
        if command[1]=='content' and len(unknownWidget)==5:  #show / hide label and right-side of non-content and non-comment
          self.formL.itemAt(unknownWidget[0]).widget().show()
          self.formL.itemAt(unknownWidget[1]).widget().show()
        if command[1]=='comment' and len(unknownWidget)==5:
          self.formL.itemAt(unknownWidget[2]).widget().show()
          self.formL.itemAt(unknownWidget[3]).widget().show()
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


class Command(Enum):
  """ Commands used in this file """
  BUTTON_BAR       = 1
  CHANGE_EXTRACTOR = 2
  SAVE_IMAGE       = 3
  OPEN_FILEBROWSER = 4
  OPEN_EXTERNAL    = 5
  FOCUS_AREA       = 6
