""" widget that shows the details of the items """
import logging
import re
from enum import Enum
from pathlib import Path
from typing import Any
import pandas as pd
from PySide6.QtCore import Qt, Slot                                        # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QLabel, QLayout, QScrollArea, QTextEdit      # pylint: disable=no-name-in-module
from ..backendWorker.worker import Task
from ..fixedStringsJson import SORTED_DB_KEYS, cssStyleHtmlEditors, defaultDataHierarchyNode
from ..textTools.handleDictionaries import dict2ul
from ..textTools.stringChanges import markdownEqualizer
from ._contextMenu import CommandMenu, executeContextMenu, initContextMenu
from .guiCommunicate import Communicate
from .guiStyle import IconButton, Image, Label, TextButton, widgetAndLayout
from .messageDialog import showMessage


class Details(QScrollArea):
  """ widget that shows the details of the items """
  def __init__(self, comm:Communicate):
    super().__init__()
    self.comm = comm
    self.comm.changeDetails.connect(self.change)
    self.comm.backendThread.worker.beSendDoc.connect(self.onGetData)
    self.comm.backendThread.worker.beSendTable.connect(self.onGetTable)
    self.comm.testExtractor.connect(self.testExtractor)
    self.doc:dict[str,Any]  = {}
    self.docID= ''
    self.idsTypesNames = pd.DataFrame(columns=['id','type','name'])
    self.textEditors:list[QTextEdit] = []

    # GUI elements
    self.mainW, self.mainL = widgetAndLayout('V', None)
    self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.setWidgetResizable(True)
    self.setWidget(self.mainW)

    headerW, self.headerL = widgetAndLayout('H', self.mainL, spacing='m', top='s', right='s')
    headerW.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    headerW.customContextMenuRequested.connect(lambda pos: initContextMenu(self, pos))
    self.specialW, self.specialL = widgetAndLayout('V', self.mainL, top='s')
    self.specialW.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    self.specialW.customContextMenuRequested.connect(lambda pos: initContextMenu(self, pos))
    self.btnDetails = TextButton('Details', self, [Command.SHOW, 'Details'], self.mainL, \
                                 'Show / hide details', checkable=True, style='margin-top: 3px')
    self.metaDetailsW, self.metaDetailsL  = widgetAndLayout('V', self.mainL)
    self.metaDetailsW.setMaximumWidth(self.width())
    self.btnVendor = TextButton('Vendor metadata', self, [Command.SHOW, 'Vendor'], self.mainL, \
                                'Show / hide vendor metadata', checkable=True, style='margin-top: 15px')
    self.metaVendorW, self.metaVendorL = widgetAndLayout('V', self.mainL)
    self.metaVendorW.setMaximumWidth(self.width())
    self.btnUser = TextButton('User metadata', self, [Command.SHOW, 'User'], self.mainL, \
                              'Show / hide user metadata', checkable=True, style='margin-top: 15px')
    self.metaUserW, self.metaUserL     = widgetAndLayout('V', self.mainL)
    self.metaUserW.setMaximumWidth(self.width())
    self.btnDatabase = TextButton('ELN details', self, [Command.SHOW,'Database'], self.mainL, \
                                  'Show / hide database details', checkable= True, style='margin-top: 15px')
    self.metaDatabaseW, self.metaDatabaseL = widgetAndLayout('V', self.mainL)
    self.metaDatabaseW.setMaximumWidth(self.width())
    self.mainL.addStretch(1)


  @Slot(str)
  def change(self, docID:str) -> None:
    """ What happens when user clicks to change to a different document
    Args:
      docID (str): document-id
    """
    self.docID = docID
    self.comm.uiRequestDoc.emit(self.docID)


  @Slot(dict)
  def onGetData(self, doc:dict[str,Any]) -> None:
    """ Function to handle the received data
    Args:
      doc (dict): dictionary containing the document data
    """
    if 'id' in doc and doc['id'] == self.docID:
      self.doc = doc
      self.paint()


  @Slot(pd.DataFrame, str)
  def onGetTable(self, data:pd.DataFrame, docType:str) -> None:
    """
    Callback function to handle the received data

    Args:
      data (pd.DataFrame): DataFrame containing table
      docType (str): document type
    """
    data = data[['id','name']]
    data['type']= docType
    self.idsTypesNames = pd.concat([self.idsTypesNames, data], ignore_index=True)


  @Slot()
  def paint(self) -> None:
    """ What happens when details should change """
    if self.isHidden():
      return
    # Delete old widgets from layout
    for i in reversed(range(self.headerL.count())):
      aWidget = self.headerL.itemAt(i).widget()
      if aWidget is not None:
        aWidget.setParent(None)
    for i in reversed(range(self.metaDetailsL.count())):
      self.metaDetailsL.itemAt(i).widget().setParent(None)
    for i in reversed(range(self.metaVendorL.count())):
      self.metaVendorL.itemAt(i).widget().setParent(None)
    for i in reversed(range(self.metaUserL.count())):
      self.metaUserL.itemAt(i).widget().setParent(None)
    for i in reversed(range(self.metaDatabaseL.count())):
      self.metaDatabaseL.itemAt(i).widget().setParent(None)
    for i in reversed(range(self.specialL.count())):
      self.specialL.itemAt(i).widget().setParent(None)
    self.specialW.hide()
    self.metaDetailsW.hide()
    self.metaVendorW.hide()
    self.metaUserW.hide()
    self.metaDatabaseW.hide()
    self.btnDetails.setChecked(True)
    self.btnVendor.setChecked(True)
    self.btnUser.setChecked(True)
    self.btnDatabase.setChecked(False)
    self.textEditors = []
    # Create new
    if not self.docID or not self.doc:
      return
    # Not sure if required #TODO
    # if 'name' not in self.doc:                                  #keep empty details and wait for user to click
    #   self.comm.changeTable.emit('','')
    #   return
    if self.doc['type'][0] not in self.comm.docTypesTitles:
      dataHierarchyNode = defaultDataHierarchyNode
    else:
      dataHierarchyNode = self.comm.dataHierarchyNodes[self.doc['type'][0]]
    label = self.doc['name'] if len(self.doc['name'])<80 else self.doc['name'][:77]+'...'
    Label(label,'h1', self.headerL)
    self.headerL.addStretch(1)
    IconButton('mdi.file-tree-outline', self, [Command.TO_PROJECT], self.headerL, tooltip='Change to project')
    IconButton('fa5s.times-circle',     self, [Command.CLOSE],      self.headerL, tooltip='Close')
    if 'metaVendor' not in self.doc:
      self.btnVendor.hide()
    if 'metUser' not in self.doc:
      self.btnUser.hide()
    size = self.comm.configuration['GUI']['imageSizeDetails'] if hasattr(self.comm, 'configuration') else 300
    for key in self.doc:
      if key=='image':
        Image(self.doc['image'], self.specialL, anyDimension=size)
        self.specialW.show()
      elif key=='content':
        text = QTextEdit()                                                   # pylint: disable=qt-local-widget
        text.setMarkdown(self.doc['content'])
        text.setFixedHeight(int(size/3*2))
        text.setReadOnly(True)
        self.specialL.addWidget(text)
        self.specialW.show()
      elif key in ['name']:                                                                              #skip
        continue
      elif key in SORTED_DB_KEYS:
        self.addDocDetails(self.metaDatabaseL, key, self.doc[key], dataHierarchyNode)
        self.btnDatabase.setChecked(False)
      elif key=='metaVendor':
        self.btnVendor.show()
        self.addDocDetails(self.metaVendorL,   '',  self.doc[key], dataHierarchyNode)
        self.metaVendorW.show()
      elif key=='metaUser':
        self.btnUser.show()
        self.addDocDetails(self.metaUserL,     '',  self.doc[key], dataHierarchyNode)
        self.metaUserW.show()
      else:
        self.addDocDetails(self.metaDetailsL,  key, self.doc[key], dataHierarchyNode)
        self.metaDetailsW.show()
    return


  def execute(self, command:list[Any]) -> None:
    """
    Hide / show the widget underneath the button

    Args:
      command (list): area to show/hide
    """
    if command[0] is Command.SHOW:
      if getattr(self, f'btn{command[1]}').isChecked():                                #get button in question
        getattr(self, f'meta{command[1]}W').show()
      else:
        getattr(self, f'meta{command[1]}W').hide()
    elif command[0] is Command.CLOSE:
      self.hide()
    elif command[0] is Command.TO_PROJECT:
      self.comm.changeProject.emit(self.doc['branch'][0]['stack'][0], self.doc['id'])
    elif isinstance(command[0], CommandMenu):
      if executeContextMenu(self, command):
        self.comm.changeTable.emit('','')
        self.comm.changeDetails.emit(self.doc['id'])
    else:
      logging.error('Details command unknown: %s',command)
    return


  @Slot()
  def testExtractor(self) -> None:
    """
    User selects to test extractor on this dataset
    """
    logging.debug('details:testExtractor')
    if len(self.doc)>1:
      pathStr = self.doc['branch'][0]['path']
      if pathStr is None:
        showMessage(self, 'Warning', 'Selected item has no path.')
      else:
        path = Path(pathStr)
        if not path.as_posix().startswith('http'):
          path = self.comm.basePath/path
        self.comm.uiRequestTask.emit(Task.EXTRACTOR_TEST, {'fileName':str(path), 'style':'html', 'recipe':'', 'saveFig':''})
    else:
      showMessage(self, 'Warning', 'No item was selected via table-view, i.e. no details are shown.')
    return


  def resizeWidth(self, width:int) -> None:
    """ called if details is resized by splitter at the parent widget
    - resize all text-documents
    """
    if not self.textEditors:
      return
    self.metaDetailsW.setFixedWidth(width)
    for text in self.textEditors:
      text.document().setTextWidth(width-80)
      height:int = text.document().size().toTuple()[1]                                    # type:ignore[index]
      text.setFixedHeight(height)
    return



  def addDocDetails(self, layout:QLayout, key:str, value:Any, dataHierarchyNode:list[dict[str,Any]]) -> str:
    """ add document details to a widget's layout: take care of all the formatting

    Args:
      layout (QLayout): layout to which to add
      key    (str): key/label to add
      value  (Any): information
      dataHierarchyNode (list): information on data-structure

    Returns:
      str: /n separated lines of text
    """
    if not key and isinstance(value,dict):
      return '\n'.join([self.addDocDetails(layout, k, v, dataHierarchyNode) for k, v in value.items()])
    link = False
    if not value:
      return ''
    labelStr = ''
    if key=='tags':
      rating = ['\u2605'*int(i[1]) for i in value if re.match(r'^_\d$', i)]
      tags = ['_curated_' if i=='_curated' else i for i in value]
      tags = [i for i in tags if not re.match(r'^_\d$', i)]
      labelStr = f'Rating: {rating[0]}' if rating else ''
      labelStr = f'{labelStr}   Tags: '+' '.join(tags)
      if layout is not None:
        label = QLabel(labelStr)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label)
    elif (isinstance(value,str) and '\n' in value) or key=='comment':        # long values with /s or comments
      labelW, labelL = widgetAndLayout('H', layout, top='s', bottom='s')
      labelL.addWidget(QLabel(f'{key}: '), alignment=Qt.AlignmentFlag.AlignTop)
      text = QTextEdit()                                                     # pylint: disable=qt-local-widget
      text.setMarkdown(markdownEqualizer(value))
      bgColor = self.comm.palette.get('secondaryDark', 'background-color')
      fgColor = self.comm.palette.get('secondaryText', 'color')
      text.setStyleSheet(f"QTextEdit {{ border: none; padding: 0px; {bgColor} {fgColor}}}")
      text.document().setTextWidth(labelW.width())
      if hasattr(self, 'rescaleTexts'):
        self.textEditors.append(text)
      height:int = text.document().size().toTuple()[1]                                    # type:ignore[index]
      text.setFixedHeight(height)
      text.setReadOnly(True)
      labelL.addWidget(text, stretch=1)
    else:
      dataHierarchyItems = [dict(i) for i in dataHierarchyNode if i['name']==key]
      docID = ''
      if len(dataHierarchyItems)==1 and 'list' in dataHierarchyItems[0] and dataHierarchyItems[0]['list'] and \
          ',' not in dataHierarchyItems[0]['list'] and ' ' not  in dataHierarchyItems[0]['list']:#choice among docType
        if dataHierarchyItems[0]['list'] not in self.idsTypesNames['type'].values:
          self.comm.uiRequestTable.emit(dataHierarchyItems[0]['list'], '', True)
        else:
          names= list(self.idsTypesNames[self.idsTypesNames.id==value[0]]['name'])
          if len(names)==1:                                            # default find one item that we link to
            docID = value[0]
            value = '\u260D '+names[0]
            link = True
          elif not names:        # likely empty link because the value was not yet defined: just print to show
            value = value[0] if isinstance(value,tuple) else value
          else:
            raise ValueError(f'list target exists multiple times. Key: {key}')
      elif isinstance(value, list):
        value = ', '.join([str(i) for i in value])
      labelStr = f'<b>{key.capitalize()}</b>: {value}'
      if isinstance(value, tuple) and len(value)==4:
        key = key if value[2] is None or value[2]=='' else value[2]
        valueString = f'{value[0]} {value[1]}'
        valueString = valueString if value[3] is None or value[3]=='' else \
                      f'{valueString}&nbsp;<b><a href="{value[3]}">&uArr;</a></b>'
        labelStr = f'{key.capitalize()}: {valueString}<br>'
      if isinstance(value, dict):
        value = {k:(v[0] if isinstance(v, (list,tuple)) else v) for k,v in value.items()}
        labelStr = f'{cssStyleHtmlEditors}{key.capitalize()}: {dict2ul(value)}'
      if layout is not None:
        label = Label(labelStr, function=lambda x,y: self.clickLink(x,y) if link else None, docID=docID)
        label.setOpenExternalLinks(True)
        label.setWordWrap(True)
        layout.addWidget(label)
    return labelStr


  def clickLink(self, label:str, docID:str) -> None:
    """
    Click link in details

    Args:
      label (str): label on link
      docID (str): docID to which to link
    """
    logging.debug('used link on %s|%s',label,docID)
    self.comm.changeDetails.emit(docID)
    return


class Command(Enum):
  """ Commands used in this file """
  SHOW             = 1
  CLOSE            = 2
  TO_PROJECT       = 3
