""" widget that shows the details of the items """
import logging
from enum import Enum
from pathlib import Path
from typing import Any
from PySide6.QtWidgets import QScrollArea, QLabel, QTextEdit  # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt, Slot                           # pylint: disable=no-name-in-module
from ..guiStyle import TextButton, Image, Label, showMessage, widgetAndLayout, getColor
from ._contextMenu import initContextMenu, executeContextMenu, CommandMenu
from ..fixedStringsJson import defaultDataHierarchyNode
from ..guiCommunicate import Communicate
from ..handleDictionaries import dict2ul
from ..miscTools import markdownStyler

CSS_STYLE = """
<style> ul {list-style-type: none; padding-left: 0; margin: 0;} a:link {text-decoration: none;}
a:visited {text-decoration: none;} a:hover {text-decoration: none;} a:active {text-decoration: none;} </style>
"""
PASTA_DETAILS = ['shasum','type','branch','gui','dateCreated','dateModified','id','user','client','externalId']

class Details(QScrollArea):
  """ widget that shows the details of the items """
  def __init__(self, comm:Communicate):
    super().__init__()
    self.comm = comm
    comm.changeDetails.connect(self.change)
    comm.testExtractor.connect(self.testExtractor)
    self.doc:dict[str,Any]  = {}
    self.docID= ''
    self.rescaleTexts:list[QTextEdit] = []

    # GUI elements
    self.mainW, self.mainL = widgetAndLayout('V', None)
    self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.setWidgetResizable(True)
    self.setWidget(self.mainW)

    headerW, self.headerL = widgetAndLayout('H', self.mainL, top='s')
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
                                'Show / hide vendor metadata', checkable=True, style="margin-top: 15px")
    self.metaVendorW, self.metaVendorL = widgetAndLayout('V', self.mainL)
    self.metaVendorW.setMaximumWidth(self.width())
    self.btnUser = TextButton('User metadata', self, [Command.SHOW, 'User'], self.mainL, \
                              'Show / hide user metadata', checkable=True, style="margin-top: 15px")
    self.metaUserW, self.metaUserL     = widgetAndLayout('V', self.mainL)
    self.metaUserW.setMaximumWidth(self.width())
    self.btnDatabase = TextButton('ELN details', self, [Command.SHOW,'Database'], self.mainL, \
                                  'Show / hide database details', checkable= True, style="margin-top: 15px")
    self.metaDatabaseW, self.metaDatabaseL = widgetAndLayout('V', self.mainL)
    self.metaDatabaseW.setMaximumWidth(self.width())
    self.mainL.addStretch(1)


  @Slot(str)
  def change(self, docID:str) -> None:
    """
    What happens when details should change

    Args:
      docID (str): document-id; '' string=draw nothing; 'redraw' implies redraw
    """
    logging.debug('details:changeDetails |%s|',docID)
    # Delete old widgets from layout
    for i in reversed(range(self.headerL.count())):
      self.headerL.itemAt(i).widget().setParent(None)
    for i in reversed(range(self.metaDetailsL.count())):
      self.metaDetailsL.itemAt(i).widget().setParent(None)
    if self.metaVendorL.itemAt(0) is not None:
      self.metaVendorL.itemAt(0).widget().setParent(None)
    if self.metaUserL.itemAt(0) is not None:
      self.metaUserL.itemAt(0).widget().setParent(None)
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
    self.rescaleTexts = []
    if not docID:  #if given '' docID, return
      return
    # Create new
    if docID!='redraw':
      self.docID = docID
    if self.docID=='':
      return
    self.doc   = self.comm.backend.db.getDoc(self.docID)
    if 'name' not in self.doc:  #keep empty details and wait for user to click
      self.comm.changeTable.emit('','')
      return
    if self.doc['type'][0] not in self.comm.backend.db.dataHierarchy('', ''):
      dataHierarchyNode = defaultDataHierarchyNode
    else:
      dataHierarchyNode = self.comm.backend.db.dataHierarchy(self.doc['type'][0], 'meta')
    label = self.doc['name'] if len(self.doc['name'])<80 else self.doc['name'][:77]+'...'
    Label(label,'h1', self.headerL)
    if 'metaVendor' not in self.doc:
      self.btnVendor.hide()
    if 'metUser' not in self.doc:
      self.btnUser.hide()
    for key in self.doc:
      size = self.comm.backend.configuration['GUI']['imageSizeDetails'] \
                        if hasattr(self.comm.backend, 'configuration') else 300
      if key=='image':
        Image(self.doc['image'], self.specialL, anyDimension=size)
        self.specialW.show()
      elif key=='content':
        text = QTextEdit()
        text.setMarkdown(self.doc['content'])
        text.setFixedHeight(int(size/3*2))
        text.setReadOnly(True)
        self.specialL.addWidget(text)
        self.specialW.show()
      elif key=='tags':
        tags = ['_curated_' if i=='_curated' else f'#{i}' for i in self.doc[key]]
        tags = ['\u2605'*int(i[2]) if i[:2]=='#_' else i for i in tags]
        label = QLabel('Tags: '+' '.join(tags))
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.metaDetailsL.addWidget(label)
      elif key in PASTA_DETAILS:
        label = QLabel(f'{key}: {str(self.doc[key])}')
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.metaDatabaseL.addWidget(label)
        self.btnDatabase.setChecked(False)
      elif key=='metaVendor':
        self.btnVendor.show()
        label = QLabel()
        label.setWordWrap(True)
        label.setText(CSS_STYLE+dict2ul(self.doc[key]))
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        label.setOpenExternalLinks(True)
        self.metaVendorL.addWidget(label)
        self.metaVendorW.show()
      elif key=='metaUser':
        self.btnUser.show()
        label = QLabel()
        label.setWordWrap(True)
        label.setText(CSS_STYLE+dict2ul(self.doc[key]))
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        label.setOpenExternalLinks(True)
        self.metaUserL.addWidget(label)
        self.metaUserW.show()
      else:
        #TODO create one function to render "'':lalala" into correct shape and use that function here and in project...
        link = False
        if (isinstance(self.doc[key],str) and '\n' in self.doc[key]) or key=='comment':
          labelW, labelL = widgetAndLayout('H', self.metaDetailsL, top='s', bottom='s')
          labelL.addWidget(QLabel(f'{key}: '), alignment=Qt.AlignmentFlag.AlignTop)
          text = QTextEdit()
          text.setMarkdown(markdownStyler(self.doc[key]))
          bgColor = getColor(self.comm.backend, 'secondaryDark')
          fgColor = getColor(self.comm.backend, 'primaryText')
          text.setStyleSheet(f"QTextEdit {{ border: none; padding: 0px; background-color: {bgColor}; "\
                                f"color: {fgColor} }}")
          text.document().setTextWidth(labelW.width())
          self.rescaleTexts.append(text)
          height:int = text.document().size().toTuple()[1]    # type:ignore[index]
          text.setFixedHeight(height)
          text.setReadOnly(True)
          labelL.addWidget(text, stretch=1)
        else:
          dataHierarchyItems = [dict(i) for i in dataHierarchyNode if i['name']==key]
          if len(dataHierarchyItems)==1 and 'list' in dataHierarchyItems[0] and dataHierarchyItems[0]['list'] and \
              not isinstance(dataHierarchyItems[0]['list'], list):                #choice among docType
            table  = self.comm.backend.db.getView('viewDocType/'+dataHierarchyItems[0]['list'])
            names= list(table[table.id==self.doc[key][0]]['name'])
            if len(names)==1:
              value = '\u260D '+names[0]
              link = True
          elif isinstance(self.doc[key], list):
            value = ', '.join(self.doc[key])
          elif isinstance(self.doc[key], tuple) and len(self.doc[key])==4:
            value = self.doc[key][0]
          elif isinstance(self.doc[key], dict):
            value = dict2ul({k:v[0] for k,v in self.doc[key].items()})
          else:
            value = self.doc[key]
          label = Label(f'{key.capitalize()}: {value}', function=self.clickLink if link else None, docID=self.doc[key])
          label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
          self.metaDetailsL.addWidget(label)
        self.metaDetailsW.show()
    return


  def execute(self, command:list[Any]) -> None:
    """
    Hide / show the widget underneath the button

    Args:
      command (list): area to show/hide
    """
    if command[0] is Command.SHOW:
      if getattr(self, f'btn{command[1]}').isChecked(): #get button in question
        getattr(self, f'meta{command[1]}W').show()
      else:
        getattr(self, f'meta{command[1]}W').hide()
    elif isinstance(command[0], CommandMenu):
      if executeContextMenu(self, command):
        self.comm.changeTable.emit('','')
        self.comm.changeDetails.emit(self.doc['_id'])
    else:
      print("**ERROR details command unknown:",command)
    return


  @Slot()
  def testExtractor(self) -> None:
    """
    User selects to test extractor on this dataset
    """
    logging.debug('details:testExtractor')
    if len(self.doc)>1:
      path = Path(self.doc['branch'][0]['path'])
      if not path.as_posix().startswith('http'):
        path = self.comm.backend.basePath/path
      report = self.comm.backend.testExtractor(path, outputStyle='html', recipe='/'.join(self.doc['type']))
      showMessage(self, 'Report of extractor test', report, style='QLabel {min-width: 800px}')
    return


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


  def resizeWidth(self, width:int) -> None:
    """ called if details is resized by splitter at the parent widget
    - resize all text-documents
    """
    if not self.rescaleTexts:
      return
    self.metaDetailsW.setFixedWidth(width)
    for text in self.rescaleTexts:
      text.document().setTextWidth(width)
      height:int = text.document().size().toTuple()[1] # type:ignore[index]
      text.setFixedHeight(height)
    return


class Command(Enum):
  """ Commands used in this file """
  SHOW             = 1
