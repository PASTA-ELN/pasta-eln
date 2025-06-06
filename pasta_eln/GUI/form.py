""" New/Edit dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
import copy
import json
import logging
import re
from enum import Enum
from pathlib import Path
from typing import Any, Union
from PySide6.QtCore import QSize, Qt, QTimer  # pylint: disable=no-name-in-module
from PySide6.QtGui import QRegularExpressionValidator  # pylint: disable=no-name-in-module
from PySide6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QLabel, QLineEdit,  # pylint: disable=no-name-in-module
                               QMessageBox, QScrollArea, QSizePolicy, QSplitter, QTabWidget, QTextEdit, QVBoxLayout,
                               QWidget)
from ..fixedStringsJson import SQLiteTranslationDict, defaultDataHierarchyNode, minimalDocInForm
from ..guiCommunicate import Communicate
from ..guiStyle import (IconButton, Image, Label, ScrollMessageBox, TextButton, showMessage, widgetAndLayout,
                        widgetAndLayoutForm)
from ..miscTools import flatten, callAddOn
from ..sqlite import MAIN_ORDER
from ..textTools.stringChanges import createDirName, markdownEqualizer
from ._contextMenu import CommandMenu, executeContextMenu, initContextMenu
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
    self.db   = self.comm.backend.db
    self.doc  = copy.deepcopy(doc)
    if '_attachments' in self.doc:
      del self.doc['_attachments']
    self.flagNewDoc = True
    if 'id' in self.doc or '_ids' in self.doc:
      self.flagNewDoc = False
    if self.flagNewDoc:
      self.setWindowTitle('Create new entry')
      self.doc['name'] = ''
    else:
      self.setWindowTitle('Edit information')
    self.skipKeys = ['image','metaVendor','metaUser','shasum','._projectID','._ids','.name','.elnIdentifier']
    self.allHidden = False
    self.doc = minimalDocInForm | self.doc

    # GUI elements
    mainL = QVBoxLayout(self)
    splitter = QSplitter(Qt.Orientation.Horizontal)
    splitter.setHandleWidth(10)
    splitter.setContentsMargins(0,0,0,0)
    mainL.addWidget(splitter, stretch=2)

    # image
    if 'image' in self.doc:
      imageWSA = QScrollArea()
      imageWSA.setWidgetResizable(True)
      imageW, self.imageL = widgetAndLayout('V', splitter)
      width = self.comm.backend.configuration['GUI']['imageSizeDetails'] \
                if hasattr(self.comm.backend, 'configuration') else 300
      Image(self.doc['image'], self.imageL, anyDimension=width)
      if 'id' in self.doc:
        self.docID= doc['id']  #required for hide to work
        imageW.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        imageW.customContextMenuRequested.connect(lambda pos: initContextMenu(self, pos))
      imageWSA.setWidget(imageW)
      splitter.addWidget(imageWSA)
      self.setMinimumWidth(1000)
    else:
      self.setMinimumWidth(600)

    # create data hierarchy node: data structure
    if self.doc['type']==['x2']:
      self.doc['type'] = ['x1']
    if self.doc['type'][0] in self.db.dataHierarchy('', ''):
      rawData = self.db.dataHierarchy(self.doc['type'][0], 'meta')
      self.dataHierarchyNode = copy.deepcopy([dict(i) for i in rawData])
    else:
      self.dataHierarchyNode = copy.deepcopy(defaultDataHierarchyNode)
    keysDataHierarchy = [f"{i['class']}.{i['name']}" for i in self.dataHierarchyNode]
    keysDocOrg = [[str(x) for x in (f'{k}.{k1}' for k1 in self.doc[k])] if isinstance(self.doc[k], dict) else [f'.{k}']
               for k in self.doc if k not in MAIN_ORDER+['branch','qrCodes','tags']]
    for keyInDocNotHierarchy in {i for row in keysDocOrg for i in row}.difference(keysDataHierarchy):
      group = keyInDocNotHierarchy.split('.')[0]
      key = keyInDocNotHierarchy.split('.')[1]
      idx = len([1 for i in self.dataHierarchyNode if i['class']==group])
      self.dataHierarchyNode.append({'docType': self.doc['type'][0], 'class':group, 'idx':idx, 'name':key, 'list':''})
    groups = {i['class'] for i in self.dataHierarchyNode}.difference({'metaVendor','metaUser'})
    # create tabs or not: depending on the number of groups
    self.tabW = QTabWidget() #has count=0 if not connected
    if len(groups)>1:
      self.tabW.setParent(self)
      self.tabW.tabBarClicked.connect(self.changeTabs)
      splitter.addWidget(self.tabW)

    # create forms by looping
    self.formsL = []
    self.allUserElements:list[tuple[str,str]] = []
    for group in groups:
      if len(groups)==1:
        _, formL = widgetAndLayoutForm(splitter, 's')
      else:
        formW, formL = widgetAndLayoutForm(None, 's', top='m')
        self.tabW.addTab(formW, 'Home' if group=='' else group)
      self.formsL.append(formL)
      for name in [i['name'] for i in self.dataHierarchyNode if i['class']==group]:
        key = f"{group}.{name}"
        defaultValue = self.doc['qrCodes'] if key=='.qrCodes' and 'qrCodes' in self.doc else \
                       self.doc.get(group, {}).get(name, ('','','','')) #tags, name, comment are handled separately
        elementName = f"key_{len(self.allUserElements)}"

        # case list
        if key == '.name' and '_ids' not in self.doc:
          setattr(self, elementName, QLineEdit(self.doc['name']))
          getattr(self, elementName).setStyleSheet(self.comm.palette.get('secondaryText','color'))
          getattr(self, elementName).setValidator(QRegularExpressionValidator('[\\w\\ .-]+'))
          formL.addRow('Name', getattr(self, elementName))
          self.allUserElements.append(('name','LineEdit'))
        elif key == '.tags':
          self.tagsBarMainW, tagsBarMainL = widgetAndLayout('H', spacing='s')
          self.gradeChoices = QComboBox()   #part/combobox that shows grades
          self.gradeChoices.setMaximumWidth(80)
          self.gradeChoices.setIconSize(QSize(0,0))
          self.gradeChoices.addItems(['','\u2605','\u2605'*2,'\u2605'*3,'\u2605'*4,'\u2605'*5])
          gradeTag = [i for i in self.doc['tags'] if i.startswith('_')]
          gradeTagStr = '\u2605'*int(gradeTag[0][1]) if gradeTag else ''
          self.gradeChoices.setCurrentText(gradeTagStr)
          tagsBarMainL.addWidget(self.gradeChoices)
          Label('Tags:', '',  tagsBarMainL, style='margin-left: 20px;')
          _, self.tagsBarSubL = widgetAndLayout('H', tagsBarMainL, spacing='s', right='m', left='m') #part which shows all the tags
          self.otherChoices = QComboBox()   #part/combobox that allow user to select
          self.otherChoices.setToolTip('Choose a tag or type a new one')
          self.otherChoices.setEditable(True)
          self.otherChoices.setMaximumWidth(100)
          self.otherChoices.setValidator(QRegularExpressionValidator('[a-zA-Z]\\w+'))
          self.otherChoices.setIconSize(QSize(0,0))
          self.otherChoices.setInsertPolicy(QComboBox.InsertPolicy.InsertAtBottom)
          tagsBarMainL.addWidget(self.otherChoices)
          formL.addRow(QLabel('Rating:'), self.tagsBarMainW)
          self.allUserElements.append(('tags',''))
          self.updateTagsBar()
          self.otherChoices.currentIndexChanged.connect(self.addTag) #connect to slot only after all painting is done
        elif key in ['.comment', '.content']:
          key = key[1:]
          labelW, labelL = widgetAndLayout('V', spacing='s')
          labelL.addWidget(QLabel(key.capitalize()))
          TextButton('More', self, [Command.FOCUS_AREA, key], labelL, checkable=True)
          projectGroup = self.comm.backend.configuration['projectGroups'][self.comm.backend.configurationProjectGroup]
          if 'form' in projectGroup.get('addOns',{}):
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
          splitter= QSplitter()
          splitter.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
          splitter.addWidget(getattr(self, f'textEdit_{key}'))
          splitter.addWidget(getattr(self, f'textShow_{key}'))
          rightSideL.addWidget(splitter)
          formL.addRow(labelW, rightSideW)
          self.allUserElements.append((key, 'comment'))
        elif key in self.skipKeys:  #skip non desired ones
          continue
        elif isinstance(defaultValue, list):   #list of items, qrCodes in sample
          if len(defaultValue)>0 and isinstance(defaultValue[0], str):
            setattr(self, elementName, QLineEdit(' '.join(defaultValue)))
            self.allUserElements.append((key,'LineEdit'))
            formL.addRow(QLabel(key.capitalize()), getattr(self, elementName))
          else:
            logging.info('Cannot display value of key=%s: %s. Write unknown value for docID=%s',
                         key, str(defaultValue), self.doc['id'])
        elif (isinstance(defaultValue, tuple) and len(defaultValue)==4 and isinstance(defaultValue[0], str)) or \
              isinstance(defaultValue, str):    #string or tuple
          dataHierarchyItem = [i for i in self.dataHierarchyNode if i['class']==group and f"{i['class']}.{i['name']}"==key]
          if len(dataHierarchyItem)!=1:
            raise ValueError('more than one dataHierarchyItem')
          label = dataHierarchyItem[0]['name'].capitalize()
          if isinstance(defaultValue, str):
            value = defaultValue
          else:  #tuple
            value = defaultValue[0]
            label += '' if defaultValue[1] is None or defaultValue[1]=='' else f' [{defaultValue[1]}]'
            label += '' if defaultValue[3] is None or defaultValue[3]=='' else f'&nbsp;<b><a href="{defaultValue[3]}">&uArr;</a></b>'
          if dataHierarchyItem[0]['list']: #choice dropdown
            setattr(self, elementName, QComboBox())
            if ',' in dataHierarchyItem[0]['list']:                  #dataHierarchy-defined choices
              getattr(self, elementName).addItems(dataHierarchyItem[0]['list'].split(','))
              getattr(self, elementName).setCurrentText(value)
            else:                                                    #choice among docType
              listDocType = dataHierarchyItem[0]['list']
              getattr(self, elementName).addItem('- no link -', userData='')
              for _, line in self.db.getView(f'viewDocType/{listDocType}').iterrows():
                getattr(self, elementName).addItem(line['name'], userData=line['id'])
                if line['id'] == value:
                  getattr(self, elementName).setCurrentIndex(getattr(self, elementName).count()-1)
            self.allUserElements.append((key,'ComboBox'))
          else:                                   #text area
            setattr(self, elementName, QLineEdit(value))
            self.allUserElements.append((key,'LineEdit'))
          getattr(self, elementName).setStyleSheet(self.comm.palette.get('secondaryText','color'))
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
        allowDocTypeChange = 'id' in self.doc and self.doc['type'][0][0]!='x'
        if '_ids' in self.doc: #if group edit
          allowDocTypeChange = all(docID[0] != 'x' for docID in self.doc['_ids'])
        allowProjectChange = self.doc['type'][0]!='x0'
        if allowProjectChange or allowDocTypeChange:
          formL.addRow(QLabel('Special properties:'), QLabel('') )
          label = '- unassigned -' if self.flagNewDoc else '- no change -'
        # project change
        if allowProjectChange:
          self.projectComboBox = QComboBox()
          self.projectComboBox.setStyleSheet(self.comm.palette.get('secondaryText','color'))
          self.projectComboBox.addItem(label, userData='')
          for _, line in self.db.getView('viewDocType/x0').iterrows():
            # add all projects but the one that is present
            if 'branch' not in self.doc or \
                all( len(branch['stack']) <= 0 or line['id'] != branch['stack'][0] for branch in self.doc['branch']):
              self.projectComboBox.addItem(line['name'], userData=line['id'])
              if self.doc.get('_projectID','') == line['id']:
                self.projectComboBox.setCurrentIndex(self.projectComboBox.count()-1)
          formL.addRow(QLabel('Project'), self.projectComboBox)
        if '_projectID' in self.doc:
          del self.doc['_projectID']
        # docType change
        if allowDocTypeChange: #if not-new and non-folder
          self.docTypeComboBox = QComboBox()
          self.docTypeComboBox.setStyleSheet(self.comm.palette.get('secondaryText','color'))
          self.docTypeComboBox.addItem(label, userData='')
          for key, value in self.db.dataHierarchy('', 'title'):
            if key[0]!='x':
              self.docTypeComboBox.addItem(value, userData=key)
          self.docTypeComboBox.addItem('_UNIDENTIFIED_', userData='-')
          formL.addRow(QLabel('Data type'), self.docTypeComboBox)
    if [i for i in self.doc if i.startswith('_')]:
      logging.error('There should not be "_" in a doc: %s', str(self.doc))
    # final button box
    _, buttonLineL = widgetAndLayout('H', mainL, 'm')
    if 'branch' in self.doc:
      visibilityIcon = all(all(branch['show']) for branch in self.doc['branch'])
      self.visibilityText = QLabel('' if visibilityIcon else 'HIDDEN     \U0001F441')
      buttonLineL.addWidget(self.visibilityText)
    buttonLineL.addStretch(1)
    self.btnAddKWPairs = IconButton('ri.menu-add-fill', self, [Command.FORM_ADD_KV],   buttonLineL,
                                    'Add key-value pair', style='border-width:1')
    if not self.flagNewDoc: #existing dataset
      IconButton('fa5s.poll-h',      self, [Command.FORM_SHOW_DOC], buttonLineL, 'Show all information',
                 style='border-width:1')
      IconButton('fa5s.plus-circle', self, [Command.FORM_SAVE_NEXT], buttonLineL, 'Duplicate data set',
                 style='border-width:1')
    saveBtn = TextButton('Save',             self, [Command.FORM_SAVE],     buttonLineL, 'Save changes')
    saveBtn.setShortcut('Ctrl+Return')
    TextButton('Cancel',           self, [Command.FORM_CANCEL],   buttonLineL, 'Discard changes')
    if self.flagNewDoc: #new dataset
      TextButton('Save && Next', self, [Command.FORM_SAVE_NEXT], buttonLineL, 'Save this and handle next')
    # end of creating form autosave
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
    self.checkThreadTimer = QTimer(self)
    self.checkThreadTimer.setInterval(1*60*1000) #1 min
    self.checkThreadTimer.timeout.connect(self.autosave)
    self.checkThreadTimer.start()


  def autosave(self) -> None:
    """ Autosave comment to file """
    if self.comm.backend.configuration['GUI']['autosave'] == 'No':
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
        dataNew  = getattr(self, elementName).currentData()  #if docID is stored in currentData
        if ((dataNew is not None and re.search(r'^[a-z\-]-[a-z0-9]{32}$',dataNew) is not None)
            or dataNew==''):
          subContent[key] = dataNew
        elif valueNew!='- no link -' or dataNew is None:
          subContent[key] = valueNew
      else:                          #normal text field
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
      if executeContextMenu(self, command):
        self.imageL.itemAt(0).widget().setParent(None)
        width = self.comm.backend.configuration['GUI']['imageSizeDetails'] \
                if hasattr(self.comm.backend, 'configuration') else 300
        if 'image' in self.doc:
          Image(self.doc['image'], self.imageL, anyDimension=width)
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
      if self.allHidden:  #hide the special buttons and show general form
        getattr(self, f'textShow_{command[1]}').hide()
        getattr(self, f'buttonBarW_{command[1]}').hide()
        for i in range(self.formsL[idx].count()):
          widget = self.formsL[idx].itemAt(i).widget()
          if isinstance(widget, (QLabel, QComboBox, QLineEdit)):
            widget.show()
          else:
            unknownWidget.append(i)
        self.tagsBarMainW.show()
        if command[1]=='content' and len(unknownWidget)==5:  #show / hide label and right-side of non-content and non-comment
          self.formsL[idx].itemAt(unknownWidget[0]).widget().show()
          self.formsL[idx].itemAt(unknownWidget[1]).widget().show()
        if command[1]=='comment' and len(unknownWidget)==5:
          self.formsL[idx].itemAt(unknownWidget[2]).widget().show()
          self.formsL[idx].itemAt(unknownWidget[3]).widget().show()
        if self.keyValueListL.count() == 0:
          self.keyValueLabel.hide()
          self.keyValueListW.hide()
      else:  #show buttons to allow for easy markdown edit; hide general form
        getattr(self, f'textShow_{command[1]}').show()
        getattr(self, f'buttonBarW_{command[1]}').show()
        for i in range(self.formsL[idx].count()):
          widget = self.formsL[idx].itemAt(i).widget()
          if isinstance(widget, (QLabel, QComboBox, QLineEdit)):
            widget.hide()
          else:
            unknownWidget.append(i)
        self.tagsBarMainW.hide()
        if command[1]=='content' and len(unknownWidget)==5:
          self.formsL[idx].itemAt(unknownWidget[0]).widget().hide()
          self.formsL[idx].itemAt(unknownWidget[1]).widget().hide()
        if command[1]=='comment' and len(unknownWidget)==5:
          self.formsL[idx].itemAt(unknownWidget[2]).widget().hide()
          self.formsL[idx].itemAt(unknownWidget[3]).widget().hide()
      self.allHidden = not self.allHidden
    elif command[0] is Command.AUTO_COMMENT:
      try:
        text  = f'\n{"-"*20}\n'
        text += callAddOn('form_auto', self.comm.backend, self.doc, self)
        text += f'\n{"-"*20}\n'
        self.textEdit_comment.insertPlainText(text)                               # type: ignore[attr-defined]
      except Exception:
        pass
    elif command[0] is Command.FORM_CANCEL:
      if self.comm.backend.configuration['GUI']['autosave'] == 'Yes':
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
      if (Path.home()/'.pastaELN.temp').is_file(): #if there is a temporary file
        with open(Path.home()/'.pastaELN.temp', encoding='utf-8') as fTemp: #open it
          content = json.loads(fTemp.read()) #and read its contents
          if self.doc.get('id', '') in content: #if there is an ID in content -> unique identifier?
            del content[self.doc.get('id', '')]# delete the ID
        with open(Path.home()/'.pastaELN.temp', 'w', encoding='utf-8') as fTemp: #then open the temporary file again
          fTemp.write(json.dumps(content)) #and write all content into the file

      # loop through all the subitems
      if self.gradeChoices.currentText():
        self.doc['tags'] = [i for i in self.doc['tags'] if not i.startswith('_')]
        self.doc['tags'].append(f'_{len(self.gradeChoices.currentText())}')
      for idx, (key, guiType) in enumerate(self.allUserElements):
        elementName = f"key_{idx}"
        valueOld = self.doc.get(key, '')
        if '.' in key:
          group, subItem = key.split('.')
        else:
          group, subItem = '', key
        if [i['mandatory'] for i in self.dataHierarchyNode if i['class']==group and i['name']==subItem] == ['T'] and \
          getattr(self, elementName).text().strip()=='':
          print(group,key,subItem)
          showMessage(self, 'Error', f'The created item must have a valid {subItem}')
          return
        if key=='name':
          self.doc['name'] = getattr(self, elementName).text().strip()
          if self.doc['type'][0]=='x0':  #prevent project-directory names that are identical
            others = self.comm.backend.db.getView('viewDocType/x0All')
            if 'id' in self.doc:
              others = others[others['id']!=self.doc['id']] # filter data frame by own id
            othersList = [createDirName(str(i),'x0', 0) for i in others['name']] #create names
            while createDirName(self.doc['name'],'x0', 0) in othersList:
              if re.search(r'_\d+$', self.doc['name']) is None:
                self.doc['name'] += '_1'
              else:
                self.doc['name'] = '_'.join(self.doc['name'].split('_')[:-1])+'_'+str(int(self.doc['name'].split('_')[-1])+1)
        elif key in ('tags'):  #tags are already saved
        #     'image', 'metaVendor', 'metaUser' or not hasattr(self, f'key_{key}') and not hasattr(self, f'textEdit_{key}')):
          continue
        elif key == '.qrCodes':
          self.doc['qrCodes'] = getattr(self, elementName).text().strip().split('/')
        elif key in ('comment','content'):
          text = getattr(self, f'textEdit_{key}').toPlainText().strip()
          if '_ids' not in self.doc or text:  #if group edit, text has to have text
            self.doc[key] = text
            if key == 'content' and 'branch' in self.doc:
              for branch in self.doc['branch']:
                if branch['path'] is not None and branch['path'].endswith('.md'):
                  with open(self.comm.backend.basePath/branch['path'], 'w', encoding='utf-8') as fOut:
                    fOut.write(self.doc['content'])
                  logging.debug('Wrote new content to %s',branch['path'])
                elif branch['path'] is not None:
                  showMessage(self, 'Information', 'Did update the database but not the file on harddisk, since PASTA-ELN cannot write this format')
        elif isinstance(valueOld, list):  #items that are comma separated in the text-field
          self.doc[key] = getattr(self, elementName).text().strip().split(' ')
        elif isinstance(valueOld, str):
          if guiType=='ComboBox':
            valueNew = getattr(self, elementName).currentText()
            dataNew  = getattr(self, elementName).currentData()  #if docID is stored in currentData
            if ((dataNew is not None and re.search(r'^[a-z\-]-[a-z0-9]{32}$',dataNew) is not None)
                or dataNew==''):
              self.doc[key] = dataNew
            elif valueNew!='- no link -' or dataNew is None:
              self.doc[key] = valueNew
          else:                          #normal text field
            self.doc[key] = getattr(self, elementName).text().strip()
        elif valueOld is None and key in self.doc:  #important entry, set to empty string
          self.doc[key]=''
          print('Is this really needed?')
        else:
          print('**ERROR dialogForm unknown value type',key, valueOld)
      # new key-value pairs
      keyValueList = [self.keyValueListL.itemAt(i).widget().text() for i in range(self.keyValueListL.count())]# type: ignore[attr-defined]
      keyValueDict = dict(zip(keyValueList[::2],keyValueList[1::2] ))
      keyValueDict = {k:v for k,v in keyValueDict.items() if k}
      self.doc = keyValueDict | self.doc
      # ---- if project changed: only branch save; remaining data still needs saving
      newProjID = self.doc['branch'][0]['stack'] if 'branch' in self.doc else []
      if hasattr(self, 'projectComboBox') and self.projectComboBox.currentData() != '':
        parentPath = self.db.getDoc(self.projectComboBox.currentData())['branch'][0]['path']
        if '_ids' in self.doc:  # group update
          for docID in self.doc['_ids']:
            doc = self.db.getDoc(docID)
            if doc['branch'][0]['stack']!=self.projectComboBox.currentData(): #only if project changed
              if doc['branch'][0]['path'] is None:
                newPath    = ''
              else:
                oldPath    = self.comm.backend.basePath/doc['branch'][0]['path']
                newPath = f'{parentPath}/{oldPath.name}'
                oldPath.rename(self.comm.backend.basePath/newPath)
              self.db.updateBranch( doc['id'], 0, 9999, [self.projectComboBox.currentData()], newPath)
        elif 'branch' in self.doc:             # sequential or single update
          if self.doc['branch'][0]['stack']!=self.projectComboBox.currentData(): #only if project changed
            if self.doc['branch'][0]['path'] is None:
              newPath    = ''
            else:
              oldPath = self.comm.backend.basePath/self.doc['branch'][0]['path']
              newPath = f'{parentPath}/{oldPath.name}'
            self.db.updateBranch( self.doc['id'], 0, 9999, [self.projectComboBox.currentData()], newPath)
            self.doc['branch'][0] = {'stack':[self.projectComboBox.currentData()], 'path':newPath or None, 'child':9999, 'show':[True,True]}
        else:
          newProjID = [self.projectComboBox.currentData()]
      # ---- if docType changed: save; no further save to db required ----
      if hasattr(self, 'docTypeComboBox') and self.docTypeComboBox.currentData() != '':
        self.doc['type'] = [self.docTypeComboBox.currentData()]
      self.doc = flatten(self.doc, True)                  # type: ignore[assignment]
      docBackup = copy.deepcopy(self.doc)                # for duplicate, save&next
      if '_ids' in self.doc:                              # group update
        if 'name' in self.doc:
          del self.doc['name']
        self.doc = {k:v for k,v in self.doc.items() if v} # filter out empty items
        for docID in self.doc.pop('_ids'):
          doc = self.db.getDoc(docID)
          doc.update( self.doc )
          self.comm.backend.editData(doc)
      elif 'id' in self.doc:                             # default update on item
        self.comm.backend.editData(self.doc)
      else:                                               # create new dataset
        self.comm.backend.addData(self.doc['type'][0], copy.deepcopy(self.doc), newProjID)
      self.doc = docBackup
      #!!! NO updates / redraw here since one does not know from where form came
      # e.g. sequential edit cannot have redraw here
      if command[0] in [Command.FORM_SAVE_NEXT, Command.FORM_SAVE_DUPL]:
        for delKey in [i for i in self.doc.keys() if i in ['id'] or i.startswith('meta')]: #delete these keys
          del self.doc[delKey]
        if command[0] is Command.FORM_SAVE_NEXT:
          self.comm.changeTable.emit('', '')
        #TODO implement a correct refresh of table and project view: send signal and only refresh the view that is open
      else:
        self.accept()  #close
        self.close()
    elif command[0] is Command.FORM_ADD_KV:
      self.keyValueLabel.show()
      self.keyValueListW.show()
      keyLabel = QLineEdit('')
      keyLabel.setPlaceholderText('key')
      keyLabel.setToolTip('Key (leave empty to delete key-value pair)')
      keyLabel.setValidator(QRegularExpressionValidator('[a-zA-Z0-9]\\S+'))
      value = QLineEdit('')
      value.setPlaceholderText('value')
      self.keyValueListL.addRow(keyLabel, value)
    elif command[0] is Command.FORM_SHOW_DOC:
      doc = self.comm.backend.db.getDoc(self.doc['id'])
      if 'image' in doc:
        del doc['image']
      messageWindow = ScrollMessageBox('Details', doc, style='QScrollArea{min-width:600 px; min-height:400px}')
      ret = messageWindow.exec()
    else:
      print('**ERROR dialogForm: unknown Command ', command)
    return


  def textChanged(self) -> None:
    """
    Text changed in editor -> update the display on the right
    """
    key = self.sender().accessibleName()                                                                     # type: ignore
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
    if isinstance(tag, str):#text from grades
      if tag!='':
        self.doc['tags'] = [i for i in self.doc['tags'] if i[0]!='_']
        self.doc['tags'] += [f'_{len(tag)}']
        self.gradeChoices.setCurrentText('')
    elif tag<1:               #zero index from other-tags
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
    #update tags
    for i in reversed(range(self.tagsBarSubL.count())):
      self.tagsBarSubL.itemAt(i).widget().setParent(None)
    for tag in (self.doc['tags'] if 'tags' in self.doc else []):
      if not re.match(r'^_\d$', tag):
        Label(tag, 'h3', self.tagsBarSubL, self.delTag, tag, 'click to remove')
    self.tagsBarSubL.addWidget(QWidget(), stretch=2)
    #update choices in combobox
    tagsAllList = self.comm.backend.db.getView('viewIdentify/viewTagsAll')['tag'].unique()
    tagsSet = {i for i in tagsAllList if i[0]!='_'}
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
