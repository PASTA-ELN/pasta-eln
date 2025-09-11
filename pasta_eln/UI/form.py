""" New/Edit dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
import copy
import json
import logging
import re
import warnings
from enum import Enum
from pathlib import Path
from typing import Any, Union
import pandas as pd
from PySide6.QtCore import QSize, Qt, QTimer, Slot
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QLayout, QLineEdit, QMessageBox,
                               QScrollArea, QSizePolicy, QSplitter, QTabWidget, QTextEdit, QVBoxLayout, QWidget)
from ..backendWorker.sqlite import MAIN_ORDER
from ..backendWorker.worker import Task
from ..fixedStringsJson import SQLiteTranslationDict, defaultDataHierarchyNode, minimalDocInForm
from ..miscTools import callAddOn
from ..textTools.stringChanges import markdownEqualizer
from ._contextMenu import CommandMenu, executeContextMenu, initContextMenu
from .guiCommunicate import Communicate
from .guiStyle import IconButton, Image, Label, ScrollMessageBox, TextButton, widgetAndLayout, widgetAndLayoutForm
from .messageDialog import showMessage
from .textEditor import TextEditor


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

    # get data into shape
    self.doc:dict[str,Any] = copy.deepcopy(doc)
    self.allDocIDs = self.doc.get('_ids', [self.doc['id']] if 'id' in self.doc else [])
    self.allDocIDsCopy = list(self.allDocIDs)
    self.flagNewDoc = 'id' not in self.doc and '_ids' not in self.doc
    self.groupEdit = '_ids' in self.doc
    self.allowDocTypeChange = self.doc.get('id',' ')[0] != 'x'
    if len(self.allDocIDs)>1:                                                                   #if group edit
      self.allowDocTypeChange = all(docID[0] != 'x' for docID in self.allDocIDs)
    self.allowDocTypeChange = self.allowDocTypeChange and not self.flagNewDoc
    self.allowProjectChange = True

    # GUI elements
    if self.flagNewDoc:
      self.setWindowTitle('Create new entry')
    else:
      self.setWindowTitle('Edit information')
    self.mainL = QVBoxLayout(self)
    self.splitter = QSplitter(Qt.Orientation.Horizontal)                         # will be filled during paint
    self.splitter.setHandleWidth(10)
    self.splitter.setContentsMargins(0,0,0,0)
    self.mainL.addWidget(self.splitter, stretch=2)

    # final button box
    _, buttonLineL = widgetAndLayout('H', self.mainL, 'm')
    self.visibilityText = QLabel('')
    buttonLineL.addWidget(self.visibilityText)
    buttonLineL.addStretch(1)
    self.btnAddKWPairs = IconButton('ri.menu-add-fill', self, [Command.FORM_ADD_KV],   buttonLineL,
                                    'Add key-value pair', style='border-width:1')
    self.btnAddKWPairs.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    self.btnAddKWPairs.setAutoDefault(False)
    self.btnAddKWPairs.setDefault(False)
    if not self.flagNewDoc:                                                                  #existing dataset
      self.showDocBtn = IconButton('fa5s.poll-h',      self, [Command.FORM_SHOW_DOC], buttonLineL, 'Show all information',
                 style='border-width:1')
      self.showDocBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
      self.showDocBtn.setAutoDefault(False)
      self.btnDuplicate = IconButton('fa5s.plus-circle', self, [Command.FORM_SAVE_NEXT], buttonLineL,
                                     'Duplicate data set', style='border-width:1')
      self.btnDuplicate.setFocusPolicy(Qt.FocusPolicy.NoFocus)
      self.btnDuplicate.setAutoDefault(False)
    self.saveBtn = TextButton('Save',             self, [Command.FORM_SAVE],     buttonLineL, 'Save changes')
    self.saveBtn.setShortcut('Ctrl+Return')
    self.saveBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    self.saveBtn.setAutoDefault(False)
    self.cancelBtn = TextButton('Cancel',           self, [Command.FORM_CANCEL],   buttonLineL, 'Discard changes')
    self.cancelBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    self.cancelBtn.setAutoDefault(False)
    if self.flagNewDoc:                                                                           #new dataset
      self.saveNextBtn = TextButton('Save && Next', self, [Command.FORM_SAVE_NEXT], buttonLineL, 'Save this and handle next')
      self.saveNextBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
      self.saveNextBtn.setAutoDefault(False)
    self.setStyleSheet(f"QLineEdit, QComboBox {{ {self.comm.palette.get('secondaryText', 'color')} }}")

    #GUI elements, filled later
    self.tagsBarMainW                         = QWidget()
    self.gradeChoices                         = QComboBox()
    self.tagsBarSubL:QLayout|None             = None
    self.otherChoices                         = QComboBox()
    self.keyValueListW                        = QWidget()
    self.keyValueListL:QFormLayout|None       = None
    self.keyValueLabel                        = QLabel()
    self.projectComboBox                      = QComboBox()
    self.skipKeys  = ['image','metaVendor','metaUser','shasum','._projectID','._ids','.name','.elnIdentifier']
    self.allHidden                            = False
    self.keyLabels: list[QLineEdit]           = []
    self.values:    list[QLineEdit]           = []
    self.imageL:QLayout|None                  = None
    self.dataHierarchyNode:list[dict[str,str]]= [{}]
    self.tabW                                 = QTabWidget()                    # has count=0 if not connected
    self.formsL:list[QLayout]                 = []
    self.allUserElements:list[tuple[str,str]] = []
    self.docTypeComboBox                      = QComboBox()
    self.checkThreadTimer                     = QTimer(self)
    self.tagsAllList: list[str] = []
    self.comboBoxDocTypeList:dict[str, tuple[QComboBox,str]] = {}# dict of docType:.. for links to other items

    # Request data
    if not self.flagNewDoc:
      self.comm.backendThread.worker.beSendDoc.connect(self.onGetData)    # do not wait for data if not needed
    self.comm.backendThread.worker.beSendTable.connect(self.onGetTable)          # tags, docTypes to link, ...
    for docID in self.allDocIDs:
      self.comm.uiRequestDoc.emit(docID)
    self.comm.uiRequestTable.emit('_tags_','', True)
    self.comm.uiRequestTable.emit('x0','', True)

    # setup Autosave, start it and paint form
    if (Path.home()/'.pastaELN.temp').is_file():
      with open(Path.home()/'.pastaELN.temp', encoding='utf-8') as fTemp:
        content = json.loads(fTemp.read())
        if self.doc.get('id', '') in content:
          ret = QMessageBox.information(self, 'Information', 'There is unsaved information from a prematurely '+
                    'closed form. Do you want to restore it?\n If you decline, the unsaved information will be'+
                    ' removed.',
                  QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
                  QMessageBox.StandardButton.Yes)
          if ret==QMessageBox.StandardButton.Yes:
            subContent = content[self.doc.get('id', '')]
            for key in subContent.keys():
              try:
                elementName = f'key_{[idx for idx, (k,_) in enumerate(self.allUserElements) if key==k][0]}'
              except Exception:
                continue
              if key in ('comment', 'content'):
                getattr(self, f'textEdit_{key}').setPlainText(subContent[key])
              elif key in ('tags'):
                self.doc[key] = subContent[key]
                self.updateTagsBar()
              elif isinstance(getattr(self, elementName), QLineEdit):
                getattr(self, elementName).setText(subContent[key])
              # skip QCombobox items since cannot be sure that next from has them and they are easy to recreate
          del content[self.doc.get('id', '')]
      with open(Path.home()/'.pastaELN.temp', 'w', encoding='utf-8') as fTemp:
        fTemp.write(json.dumps(content))
    self.checkThreadTimer.setInterval(1*60*1000)                                                       # 1 min
    self.checkThreadTimer.timeout.connect(self.autosave)
    self.checkThreadTimer.start()
    self.paint()


  @Slot(dict)
  def onGetData(self, doc:dict[str,Any]) -> None:
    """
    Get data from the backend

    Args:
      doc (dict):  document to change / create
    """
    if not doc:
      return
    if doc['id'] in self.allDocIDs:
      self.allDocIDs.remove(doc['id'])
      if 'id' in self.doc and len(self.doc)==1:             # initialize self.doc with a real doc: not just id
        self.doc = doc
      else:
        intersection = set(self.doc).intersection(set(doc))
        #remove keys that should not be group edited and build dict
        intersection = intersection.difference({'branch', 'user', 'client', 'metaVendor', 'shasum', 'id', 'type',
                           'metaUser', 'rev', 'name', 'dateCreated', 'dateModified', 'image', 'links', 'gui', ''})
        docType = list(self.doc['type'])
        self.doc = {i:'' for i in intersection}
        self.doc['tags'] = []
        self.doc['type'] = docType
      self.allowProjectChange = self.allowProjectChange and self.doc['type'][0]!='x0'# none of the items can be a project
    if len(self.allDocIDs)==0:
      self.paint()



  @Slot(pd.DataFrame, str)
  def onGetTable(self, data:pd.DataFrame, docType:str) -> None:
    """
    - Get tags from the backend
    - get list of projects and other docTypes and fill the comboBoxes

    Args:
      data (pd.DataFrame):  DataFrame containing tags
      docType (str): document type
    """
    if docType == '_tags_':
      self.tagsAllList = data['tag'].unique()
      self.updateTagsBar()
    elif docType == 'x0':
      self.projectComboBox.clear()
      self.projectComboBox.addItem('- no change' if self.groupEdit else '- not assigned -', userData='')
      for iDocID, iName in data[['id','name']].values.tolist():           # add all projects incl. the present
        self.projectComboBox.addItem(iName, userData=iDocID)
        stack = self.doc.get('branch',[{}])[0].get('stack', [])
        proj  = stack[0] if stack else ''
        if iDocID in (self.doc.get('_projectID',''), proj):
          self.projectComboBox.setCurrentIndex(self.projectComboBox.count()-1)
    elif docType in self.comboBoxDocTypeList:
      iComboBox, value = self.comboBoxDocTypeList[docType]
      iComboBox.clear()
      iComboBox.addItem('- no link -', userData='')
      for iDocID, iName in data[['id','name']].values.tolist():
        iComboBox.addItem(iName, userData=iDocID)
        if iDocID == value:
          iComboBox.setCurrentIndex(iComboBox.count()-1)
    else:
      logging.warning('Unknown docType in onGetTable: %s', docType)


  def paint(self) -> None:
    """ Paint the form with all the elements """
    if 'type' not in self.doc:
      return
    if '_attachments' in self.doc:
      del self.doc['_attachments']
    for i in reversed(range(self.splitter.count())):                        # remove all widgets from splitter
      widget = self.splitter.widget(i)
      if widget is not None and widget is not self.projectComboBox:
        widget.setParent(None)
    self.comboBoxDocTypeList = {}                                                  # reset comboBoxDocTypeList
    self.allUserElements     = []
    self.doc = copy.deepcopy(minimalDocInForm) | self.doc
    if self.flagNewDoc:
      self.doc['name'] = ''
    if 'branch' in self.doc:
      visibilityIcon = all(all(branch['show']) for branch in self.doc['branch'])
      self.visibilityText = QLabel('' if visibilityIcon else 'HIDDEN     \U0001F441')
      self.btnDuplicate.setHidden(self.doc['branch'][0]['path'] is None)

    # image
    if 'image' in self.doc:
      imageWSA = QScrollArea()
      imageWSA.setWidgetResizable(True)
      imageW, self.imageL = widgetAndLayout('V', self.splitter)
      width= self.comm.configuration['GUI']['imageSizeDetails'] if hasattr(self.comm,'configuration') else 300
      Image(self.doc['image'], self.imageL, anyDimension=width)
      if 'id' in self.doc:
        imageW.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        imageW.customContextMenuRequested.connect(lambda pos: initContextMenu(self, pos))
      imageWSA.setWidget(imageW)
      self.splitter.addWidget(imageWSA)
      self.setMinimumWidth(1100)
      self.setMinimumHeight(600)
    else:
      self.setMinimumWidth(600)

    # create data hierarchy node: data structure
    if self.doc['type'][0] in self.comm.docTypesTitles:
      rawData = self.comm.dataHierarchyNodes[self.doc['type'][0]]
      self.dataHierarchyNode = copy.deepcopy([dict(i) for i in rawData])
    else:
      self.dataHierarchyNode = copy.deepcopy(defaultDataHierarchyNode)
    keysDataHierarchy = [f"{i['class']}.{i['name']}" for i in self.dataHierarchyNode]
    keysDocOrg = [[str(x) for x in (f'{k}.{k1}' for k1 in self.doc[k])] if isinstance(self.doc[k], dict) else [f'.{k}']
               for k in self.doc if k not in MAIN_ORDER+['branch','qrCodes','tags']]
    for keyInDocNotHierarchy in {i for row in keysDocOrg for i in row}.difference(keysDataHierarchy):
      group = keyInDocNotHierarchy.split('.')[0]
      key = keyInDocNotHierarchy.split('.')[1]
      if not key:
        continue
      idx = len([1 for i in self.dataHierarchyNode if i['class']==group])
      self.dataHierarchyNode.append({'docType': self.doc['type'][0], 'class':group, 'idx':str(idx), 'name':key,
                                     'list':'', 'mandatory':'', 'unit':''})
    #TODO: TEMPORARY CHECK: REMOVE 2026
    allKeys = {'docType', 'class', 'idx', 'name', 'unit', 'mandatory', 'list'}
    if any(allKeys.difference(i.keys()) for i in self.dataHierarchyNode):
      #mask = [allKeys.difference(i.keys()) for i in self.dataHierarchyNode]
      raise ValueError('dataHierarchyNode is not complete. Missing keys')
    # END TEMPORARY CHECK
    groups = {i['class'] for i in self.dataHierarchyNode}.difference({'metaVendor','metaUser'})
    # create tabs or not: depending on the number of groups
    if len(groups)>1:
      self.tabW.setParent(self)
      self.tabW.tabBarClicked.connect(self.changeTabs)
      self.splitter.addWidget(self.tabW)

    # create forms by looping
    for group in groups:
      if len(groups)==1:
        _, formL = widgetAndLayoutForm(self.splitter, 's')
      else:
        formW, formL = widgetAndLayoutForm(None, 's', top='m')
        self.tabW.addTab(formW, 'Home' if group=='' else group)
      self.formsL.append(formL)
      for name in [i['name'] for i in self.dataHierarchyNode if i['class']==group]:
        key = f"{group}.{name}"
        defaultValue = self.doc['qrCodes'] if key=='.qrCodes' and 'qrCodes' in self.doc else \
                       self.doc.get(group, {}).get(name, ('','','',''))#tags, name, comment are handled separately
        elementName = f"key_{len(self.allUserElements)}"

        # case list
        if key == '.name' and not self.groupEdit:
          setattr(self, elementName, QLineEdit(self.doc.get('name','')))
          getattr(self, elementName).setValidator(QRegularExpressionValidator('[\\w\\ .-]+'))
          formL.addRow('Name', getattr(self, elementName))
          self.allUserElements.append(('name','LineEdit'))
        elif key == '.tags':
          self.tagsBarMainW, tagsBarMainL = widgetAndLayout('H', spacing='s')
          self.gradeChoices = QComboBox()                                     #part/combobox that shows grades
          self.gradeChoices.setMaximumWidth(95)
          self.gradeChoices.setStyleSheet('padding: 3px;')
          self.gradeChoices.setIconSize(QSize(0,0))
          self.gradeChoices.addItems(['none','\u2605','\u2605'*2,'\u2605'*3,'\u2605'*4,'\u2605'*5])
          gradeTag = [i for i in self.doc['tags'] if i.startswith('_')]
          gradeTagStr = '\u2605'*int(gradeTag[0][1]) if gradeTag else ''
          self.gradeChoices.setCurrentText(gradeTagStr)
          tagsBarMainL.addWidget(self.gradeChoices)
          Label('Tags:', '',  tagsBarMainL, style='margin-left: 20px;')
          tagsBarSubW, self.tagsBarSubL = widgetAndLayout('H', tagsBarMainL, spacing='s', right='m', left='m')#part which shows all the tags
          tagsBarSubW.setMaximumWidth(420)
          self.otherChoices = QComboBox()                             #part/combobox that allow user to select
          self.otherChoices.setToolTip('Choose a tag or type a new one')
          self.otherChoices.setEditable(True)
          self.otherChoices.setMinimumWidth(80)
          self.otherChoices.setValidator(QRegularExpressionValidator('[a-zA-Z]\\w+'))
          self.otherChoices.setIconSize(QSize(0,0))
          self.otherChoices.setInsertPolicy(QComboBox.InsertPolicy.InsertAtBottom)
          self.otherChoices.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
          tagsBarMainL.addWidget(self.otherChoices)
          formL.addRow(QLabel('Rating:'), self.tagsBarMainW)
          self.allUserElements.append(('tags',''))
          self.updateTagsBar()
          self.otherChoices.currentIndexChanged.connect(self.addTag)#connect to slot only after all painting is done
        elif key in ['.comment', '.content']:
          key = key[1:]
          labelW, labelL = widgetAndLayout('V', spacing='s')
          labelL.addWidget(QLabel(key.capitalize()))
          TextButton('More', self, [Command.FOCUS_AREA, key], labelL, checkable=True)
          projectGroup = self.comm.configuration['projectGroups'][self.comm.projectGroup]
          if 'form' in projectGroup.get('addOns',{}) and projectGroup['addOns']['form']:
            TextButton('Auto', self, [Command.AUTO_COMMENT],    labelL, checkable=True)
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
          textStr = self.doc.get(key, '')
          for k,v in SQLiteTranslationDict.items():
            textStr = textStr.replace(v,k)
          setattr(self, f'textEdit_{key}', TextEditor(textStr))
          getattr(self, f'textEdit_{key}').setAccessibleName(key)
          getattr(self, f'textEdit_{key}').textChanged.connect(self.textChanged)
          setattr(self, f'textShow_{key}', QTextEdit())
          getattr(self, f'textShow_{key}').setMarkdown(markdownEqualizer(self.doc.get(key, '')))
          getattr(self, f'textShow_{key}').setReadOnly(True)
          getattr(self, f'textShow_{key}').hide()
          splittedEditor = QSplitter()
          splittedEditor.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
          splittedEditor.addWidget(getattr(self, f'textEdit_{key}'))
          splittedEditor.addWidget(getattr(self, f'textShow_{key}'))
          rightSideL.addWidget(splittedEditor)
          formL.addRow(labelW, rightSideW)
          self.allUserElements.append((key, 'comment'))
        elif key in self.skipKeys:                                                      #skip non desired ones
          continue
        elif isinstance(defaultValue, list):                                 #list of items, qrCodes in sample
          if len(defaultValue)>0 and isinstance(defaultValue[0], str):
            setattr(self, elementName, QLineEdit(' '.join(defaultValue)))
            self.allUserElements.append((key,'LineEdit'))
            formL.addRow(QLabel(key.capitalize()), getattr(self, elementName))
          else:
            logging.info('Cannot display value of key=%s: %s. Write unknown value for docID=%s',
                         key, str(defaultValue), self.doc['id'])
        elif (isinstance(defaultValue, tuple) and len(defaultValue)==4 and isinstance(defaultValue[0], str)) or \
              isinstance(defaultValue, str):                                                  #string or tuple
          dataHierarchyItem = [i for i in self.dataHierarchyNode if i['class']==group and f"{i['class']}.{i['name']}"==key]
          if len(dataHierarchyItem)!=1:
            raise ValueError('more than one dataHierarchyItem')
          label = dataHierarchyItem[0]['name'].capitalize()
          if isinstance(defaultValue, str):
            value = defaultValue
          else:                                                                                         #tuple
            value = defaultValue[0]
            label += '' if defaultValue[1] is None or defaultValue[1]=='' else f' [{defaultValue[1]}]'
            label += '' if defaultValue[3] is None or defaultValue[3]=='' else f'&nbsp;<b><a href="{defaultValue[3]}">&uArr;</a></b>'
          if dataHierarchyItem[0]['list']:                                                    #choice dropdown
            setattr(self, elementName, QComboBox())
            if ',' in dataHierarchyItem[0]['list']:                             #dataHierarchy-defined choices
              getattr(self, elementName).addItems(dataHierarchyItem[0]['list'].split(','))
              getattr(self, elementName).setCurrentText(value)
            else:                                                                        #choice among docType
              listDocType = dataHierarchyItem[0]['list']
              if listDocType not in self.comboBoxDocTypeList:          # if listDocType already exists in dict
                self.comm.uiRequestTable.emit(listDocType, '', True)
                self.comboBoxDocTypeList[listDocType] = (getattr(self, elementName), value)
            self.allUserElements.append((key,'ComboBox'))
          else:                                                                                     #text area
            setattr(self, elementName, QLineEdit(value))
            self.allUserElements.append((key,'LineEdit'))
          formLabelW = QLabel(label)
          formLabelW.setOpenExternalLinks(True)
          formLabelW.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)
          formL.addRow(formLabelW, getattr(self, elementName))
        else:
          print(f"**WARNING dialogForm: unknown value type. key:{key}, type:{type(defaultValue)}")
        if group in self.doc and name in self.doc[group]:
          del self.doc[group][name]
          if not self.doc[group]:
            del self.doc[group]
      if group == '':
        # individual key-value items
        self.keyValueListW, self.keyValueListL = widgetAndLayoutForm(None, 's')
        self.keyValueListW.hide()
        self.keyValueLabel = QLabel('Key - values')
        self.keyValueLabel.hide()
        formL.addRow(self.keyValueLabel, self.keyValueListW)
        # add extra questions at bottom of form
        if self.allowProjectChange or self.allowDocTypeChange:
          formL.addRow(QLabel('Special properties:'), QLabel('') )
        # project change
        if self.allowProjectChange:
          formL.addRow(QLabel('Project'), self.projectComboBox)
        # docType change
        if self.allowDocTypeChange:                                                 #if not-new and non-folder
          self.docTypeComboBox = QComboBox()
          self.docTypeComboBox.addItem('- no change -', userData='')
          for key1, value1 in self.comm.docTypesTitles.items():
            if key1[0]!='x':
              self.docTypeComboBox.addItem(value1['title'], userData=key1)
          self.docTypeComboBox.addItem('_UNIDENTIFIED_', userData='-')
          formL.addRow(QLabel('Data type'), self.docTypeComboBox)
    if [i for i in self.doc if i.startswith('_') and i not in ['_projectID']]:
      logging.error('There should not be "_" in a doc: %s', str(self.doc), exc_info=True)


  def autosave(self) -> None:
    """ Autosave comment to file """
    if self.comm.configuration['GUI']['autosave'] == 'No':
      return
    subContent = {'name':getattr(self, f"key_{self.allUserElements.index(('name','LineEdit'))}").text().strip(),
                  'tags':self.doc['tags']}
    for idx, (key, guiType) in enumerate(self.allUserElements):
      if key in ['tags', 'name']:
        continue
      elementName = f"key_{idx}"
      if key in ['comment','content']:
        subContent[key] = getattr(self, f'textEdit_{key}').toPlainText().strip()
      elif key in self.skipKeys:
        continue
      elif guiType=='ComboBox':
        valueNew = getattr(self, elementName).currentText()
        dataNew  = getattr(self, elementName).currentData()                 #if docID is stored in currentData
        if ((dataNew is not None and re.search(r'^[a-z\-]-[a-z0-9]{32}$',dataNew) is not None)
            or dataNew==''):
          subContent[key] = dataNew
        elif valueNew!='- no link -' or dataNew is None:
          subContent[key] = valueNew
      else:                                                                                 #normal text field
        subContent[key] = getattr(self, elementName).text().strip()
    # skip QCombobox items since cannot be sure that next from has them and they are easy to recreate
    if (Path.home()/'.pastaELN.temp').is_file():
      with open(Path.home()/'.pastaELN.temp', encoding='utf-8') as fTemp:
        content = json.loads(fTemp.read())
    else:
      content = {}
    content[self.doc.get('id', '')] = subContent
    with open(Path.home()/'.pastaELN.temp', 'w', encoding='utf-8') as fTemp:
      fTemp.write(json.dumps(content))
    return


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks button

    Args:
      command (list): list of commands
    """
    if isinstance(command[0], CommandMenu):
      if executeContextMenu(self, command) and self.imageL is not None:
        item = self.imageL.itemAt(0)
        if item is not None: item.widget().setParent(None)
        width=self.comm.configuration['GUI']['imageSizeDetails'] if hasattr(self.comm,'configuration') else 300
        if 'image' in self.doc:
          Image(self.doc['image'], self.imageL, anyDimension=width)
        if 'branch' in self.doc:
          visibilityIcon = all(all(branch['show']) for branch in self.doc['branch'])
          self.visibilityText.setText('' if visibilityIcon else 'HIDDEN     \U0001F441')

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
      idx = 0 if self.tabW.count()==0 else self.tabW.currentIndex()
      if self.allHidden:                                       #hide the special buttons and show general form
        getattr(self, f'textShow_{command[1]}').hide()
        getattr(self, f'buttonBarW_{command[1]}').hide()
        for i in range(self.formsL[idx].count()):
          item = self.formsL[idx].itemAt(i)
          widget = None if item is None else item.widget()
          if isinstance(widget, (QLabel, QComboBox, QLineEdit)):
            widget.show()
          else:
            unknownWidget.append(i)
        self.tagsBarMainW.show()
        if command[1]=='content' and len(unknownWidget)==5:#show / hide label and right-side of non-content and non-comment
          item = self.formsL[idx].itemAt(unknownWidget[0])
          if item is not None: item.widget().show()
          item = self.formsL[idx].itemAt(unknownWidget[1])
          if item is not None: item.widget().show()
        if command[1]=='comment' and len(unknownWidget)==5:
          item = self.formsL[idx].itemAt(unknownWidget[2])
          if item is not None: item.widget().show()
          item = self.formsL[idx].itemAt(unknownWidget[3])
          if item is not None:  item.widget().show()
        if self.keyValueListL is not None and self.keyValueListL.count() == 0:
          self.keyValueLabel.hide()
          self.keyValueListW.hide()
      else:                                   #show buttons to allow for easy markdown edit; hide general form
        getattr(self, f'textShow_{command[1]}').show()
        getattr(self, f'buttonBarW_{command[1]}').show()
        for i in range(self.formsL[idx].count()):
          item = self.formsL[idx].itemAt(i)
          widget = None if item is None else item.widget()
          if isinstance(widget, (QLabel, QComboBox, QLineEdit)):
            widget.hide()
          else:
            unknownWidget.append(i)
        self.tagsBarMainW.hide()
        if command[1]=='content' and len(unknownWidget)==5:
          item = self.formsL[idx].itemAt(unknownWidget[0])
          if item is not None: item.widget().hide()
          item = self.formsL[idx].itemAt(unknownWidget[1])
          if item is not None: item.widget().hide()
        if command[1]=='comment' and len(unknownWidget)==5:
          item = self.formsL[idx].itemAt(unknownWidget[2])
          if item is not None: item.widget().hide()
          item = self.formsL[idx].itemAt(unknownWidget[3])
          if item is not None: item.widget().hide()
      self.allHidden = not self.allHidden

    elif command[0] is Command.AUTO_COMMENT:
      try:
        text  = f'\n{"-"*20}\n'
        text += callAddOn('form_auto', self.comm, self.doc, self)
        text += f'\n{"-"*20}\n'
        self.textEdit_comment.insertPlainText(text)                               # type: ignore[attr-defined]
      except Exception:
        pass

    elif command[0] is Command.FORM_CANCEL:
      if self.comm. configuration['GUI']['autosave'] == 'Yes':
        ret = QMessageBox.critical(self, 'Warning', 'You will lose the entered information. Do you want to '+
          'save everything to a temporary location?',
          QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
          QMessageBox.StandardButton.No)
        if ret==QMessageBox.StandardButton.Cancel:
          return
        if ret==QMessageBox.StandardButton.Yes:
          self.autosave()
      self.checkThreadTimer.stop()
      self.reject()

    elif command[0] in (Command.FORM_SAVE, Command.FORM_SAVE_NEXT, Command.FORM_SAVE_DUPL):
      self.checkThreadTimer.stop()
      if (Path.home()/'.pastaELN.temp').is_file():                               #if there is a temporary file
        with open(Path.home()/'.pastaELN.temp', encoding='utf-8') as fTemp:
          content = json.loads(fTemp.read())
          if self.doc.get('id', '') in content:            #if there is an ID in content -> unique identifier?
            del content[self.doc.get('id', '')]                                                # delete the ID
        with open(Path.home()/'.pastaELN.temp', 'w', encoding='utf-8') as fTemp:  #reopen temporary file again
          fTemp.write(json.dumps(content))

      # loop through all the subitems
      # rating
      rating = self.gradeChoices.currentText()
      self.doc['tags'] = [i for i in self.doc['tags'] if not i.startswith('_')]       # filter out old ratings
      if rating != 'none':
        self.doc['tags'].append(f'_{len(rating)}')
      for idx, (key, guiType) in enumerate(self.allUserElements):
        elementName = f"key_{idx}"
        valueOld = self.doc.get(key, '')
        if '.' in key:
          group, subItem = key.split('.')
        else:
          group, subItem = '', key
        if [i['mandatory'] for i in self.dataHierarchyNode if i['class']==group and i['name']==subItem] == ['T'] and \
          getattr(self, elementName).text().strip()=='':
          print(f'**ERROR group:{group}| key:{key}| subItem:{subItem}: mandatory field is empty')
          showMessage(self, 'Error', f'The created item must have a valid {subItem}')
          return
        if key=='name':
          self.doc['name'] = getattr(self, elementName).text().strip()
        elif key in ('tags'):                                                          #tags are already saved
        #     'image', 'metaVendor', 'metaUser' or not hasattr(self, f'key_{key}') and not hasattr(self, f'textEdit_{key}')):
          continue
        elif key == '.qrCodes':
          self.doc['qrCodes'] = getattr(self, elementName).text().strip().split('/')
        elif key in ('comment','content'):
          text = getattr(self, f'textEdit_{key}').toPlainText().strip()
          if '_ids' not in self.doc or text:                             #if group edit, text has to have text
            self.doc[key] = text
            if key == 'content' and 'branch' in self.doc:
              for branch in self.doc['branch']:
                if branch['path'] is not None and branch['path'].endswith('.md'):
                  with open(self.comm.basePath/branch['path'], 'w', encoding='utf-8') as fOut:
                    fOut.write(self.doc['content'])
                  logging.debug('Wrote new content to %s',branch['path'])
                elif branch['path'] is not None:
                  showMessage(self, 'Information', 'Did update the database but not the file on harddisk, since PASTA-ELN cannot write this format')
        elif isinstance(valueOld, list):                     #items that are comma separated in the text-field
          self.doc[key] = getattr(self, elementName).text().strip().split(' ')
        elif isinstance(valueOld, str):
          if guiType=='ComboBox':
            valueNew = getattr(self, elementName).currentText()
            dataNew  = getattr(self, elementName).currentData()             #if docID is stored in currentData
            if ((dataNew is not None and re.search(r'^[a-z\-]-[a-z0-9]{32}$',dataNew) is not None)
                or dataNew==''):
              self.doc[key] = dataNew
            elif valueNew!='- no link -' or dataNew is None:
              self.doc[key] = valueNew
          else:                                                                             #normal text field
            self.doc[key] = getattr(self, elementName).text().strip()
        # elif valueOld is None and key in self.doc:  #important entry, set to empty string
        #   self.doc[key]=''
        #   print('Is this really needed?')
        else:
          logging.error('Unknown value type %s %s',key, valueOld, exc_info=True)
      # new key-value pairs
      keyValueList = [self.keyValueListL.itemAt(i).widget().text() for i in range(self.keyValueListL.count())]# type: ignore[union-attr]
      keyValueDict = dict(zip(keyValueList[::2],keyValueList[1::2] ))
      keyValueDict = {f'.{k}':v for k,v in keyValueDict.items() if k}
      self.doc = keyValueDict | self.doc
      # ---- if project changed: only branch save; remaining data still needs saving
      newProjID = [self.projectComboBox.currentData()] if self.projectComboBox.currentData() else []
      # ---- if docType changed: save; no further save to db required ----
      if self.docTypeComboBox.currentData() != '' and self.docTypeComboBox.currentData() is not None:
        self.doc['type'] = [self.docTypeComboBox.currentData()]

      docBackup = copy.deepcopy(self.doc)                                           # for duplicate, save&next
      if self.groupEdit:                                                                        # group update
        if 'name' in self.doc:
          del self.doc['name']
        if not self.doc['tags']:
          del self.doc['tags']                                # remove empty tags to not overwrite already set
        self.doc = {k:v for k,v in self.doc.items() if v}                             # filter out empty items
        for docID in self.allDocIDsCopy:
          self.comm.uiRequestTask.emit(Task.EDIT_DOC, {'doc':self.doc|{'id':docID}, 'newProjID':newProjID})
      elif 'id' in self.doc:                                                          # default update on item
        self.comm.uiRequestTask.emit(Task.EDIT_DOC, {'doc':self.doc, 'newProjID':newProjID})
      else:                                                                               # create new dataset
        self.comm.uiRequestTask.emit(Task.ADD_DOC, {'hierStack':newProjID, 'docType':self.doc['type'][0],
                                                    'doc':self.doc})
      self.doc = docBackup
      #!!! NO updates / redraw here since one does not know from where form came
      # e.g. sequential edit cannot have redraw here
      if command[0] in [Command.FORM_SAVE_NEXT, Command.FORM_SAVE_DUPL]:
        for delKey in [i for i in self.doc.keys() if i in ['id'] or i.startswith('meta')]: # delete these keys
          del self.doc[delKey]
        if command[0] is Command.FORM_SAVE_NEXT:
          self.comm.changeTable.emit(self.doc['type'][0], '')
      else:
        self.accept()                                                                                   #close
        self.close()

    elif command[0] is Command.FORM_ADD_KV and self.keyValueListL is not None:
      self.keyValueLabel.show()
      self.keyValueListW.show()
      self.keyLabels.append(QLineEdit(''))
      self.keyLabels[-1].setPlaceholderText('key')
      self.keyLabels[-1].setToolTip('Key (leave empty to delete key-value pair)')
      self.keyLabels[-1].setValidator(QRegularExpressionValidator('[a-zA-Z0-9]\\S+'))
      self.values.append(QLineEdit(''))
      self.values[-1].setPlaceholderText('value')
      self.keyValueListL.addRow(self.keyLabels[-1], self.values[-1])

    elif command[0] is Command.FORM_SHOW_DOC:
      doc = copy.deepcopy(self.doc)
      if 'image' in doc:
        del doc['image']
      messageWindow = ScrollMessageBox('Details', doc, style='QScrollArea{min-width:600 px; min-height:400px}')
      messageWindow.exec()

    else:
      logging.error('Unknown Command %s', command, exc_info=True)
    return


  def textChanged(self) -> None:
    """
    Text changed in editor -> update the display on the right
    """
    key = self.sender().accessibleName()                                                        # type: ignore
    getattr(self, f'textShow_{key}').setMarkdown(markdownEqualizer(getattr(self, f'textEdit_{key}').toPlainText()))
    return

  def delTag(self, _:str, tag:str) -> None:
    """
    Clicked button to delete tag
    """
    self.doc['tags'].remove(tag)
    self.updateTagsBar()
    return

  def addTag(self, tag:Union[str,int]) -> None:
    """
    Clicked to add tag. Since one needs to use indexChanged to allow the user to enter text, that delivers a int. To allow to differentiate
    between both comboboxes, they cannot be the same (both int), hence grades has to be textChanged

    Args:
      tag (str, int): index (otherTags) or text (grades)
    """
    if isinstance(tag, str):                                                                # text from grades
      if tag!='':
        self.doc['tags'] = [i for i in self.doc['tags'] if i[0]!='_']
        self.doc['tags'] += [f'_{len(tag)}']
        self.gradeChoices.setCurrentText('')
    elif tag<1:                                                                   # zero index from other-tags
      return
    else:
      tag = self.otherChoices.currentText()
      if tag not in self.doc['tags']:
        self.doc['tags'] += [tag]
      self.otherChoices.setCurrentText('')
    self.updateTagsBar()
    return

  def updateTagsBar(self) -> None:
    """
    After creation, tag removal, tag addition: update the information on screen
    """
    if self.tagsBarSubL is None:
      return
    #update tags
    for i in reversed(range(self.tagsBarSubL.count())):
      item = self.tagsBarSubL.itemAt(i)
      if item is not None: item.widget().setParent(None)
    for tag in (self.doc['tags'] if 'tags' in self.doc else []):
      if not re.match(r'^_\d$', tag):
        Label(tag, 'h3', self.tagsBarSubL, self.delTag, tag, 'click to remove')
    self.tagsBarSubL.addWidget(QWidget(), stretch=2)                                   #type: ignore[call-arg]
    #update choices in combobox
    tagsSet = {i for i in self.tagsAllList if i[0]!='_'}
    newChoicesList = ['']+list(tagsSet.difference([i for i in self.doc['tags'] if i[0]!='_']))
    self.otherChoices.clear()
    self.otherChoices.addItems(newChoicesList)
    return


  def changeTabs(self, idx:int) -> None:
    """
    Clicked on tabs to change to different one

    Args:
      idx (int): index of tab that was clicked
    """
    if idx == 0:
      self.btnAddKWPairs.show()
    else:
      self.btnAddKWPairs.hide()
    return

  def reject(self) -> None:
    """ Reject the dialog, stop the thread and disconnect signals """
    warnings.filterwarnings('ignore', category=RuntimeWarning)
    if hasattr(self.comm, 'backendThread') and self.comm.backendThread.worker is not None:
      self.comm.backendThread.worker.beSendDoc.disconnect(self.onGetData)
      self.comm.backendThread.worker.beSendTable.disconnect(self.onGetTable)
    self.checkThreadTimer.stop()
    super().reject()


  def accept(self) -> None:
    """ Accept the dialog, stop the thread and disconnect signals """
    warnings.filterwarnings('ignore', category=RuntimeWarning)
    if hasattr(self.comm, 'backendThread') and self.comm.backendThread.worker is not None:
      self.comm.backendThread.worker.beSendDoc.disconnect(self.onGetData)
      self.comm.backendThread.worker.beSendTable.disconnect(self.onGetTable)
    self.checkThreadTimer.stop()
    super().accept()


class Command(Enum):
  """ Commands used in this file """
  BUTTON_BAR       = 1
  CHANGE_EXTRACTOR = 2
  SAVE_IMAGE       = 3
  OPEN_FILEBROWSER = 4
  OPEN_EXTERNAL    = 5
  FOCUS_AREA       = 6
  AUTO_COMMENT     = 7
  FORM_SAVE        = 8
  FORM_CANCEL      = 9
  FORM_ADD_KV      = 10
  FORM_SHOW_DOC    = 11
  FORM_SAVE_NEXT   = 12
  FORM_SAVE_DUPL   = 13
