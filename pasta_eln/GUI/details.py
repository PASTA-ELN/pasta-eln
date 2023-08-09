""" widget that shows the details of the items """
from pathlib import Path
import platform, subprocess, os, logging
from enum import Enum
from typing import Any
import yaml
from PySide6.QtWidgets import QScrollArea, QLabel, QMenu, QTextEdit  # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt, Slot, QPoint  # pylint: disable=no-name-in-module
from ..guiStyle import TextButton, Image, Label, Action, showMessage, widgetAndLayout
from ..fixedStringsJson import defaultOntologyNode
from ..guiCommunicate import Communicate

class Details(QScrollArea):
  """ widget that shows the details of the items """
  def __init__(self, comm:Communicate):
    super().__init__()
    self.comm = comm
    comm.changeDetails.connect(self.change)
    comm.testExtractor.connect(self.testExtractor)
    self.doc:dict[str,Any]  = {}
    self.docID= ''

    # GUI elements
    self.mainW, self.mainL = widgetAndLayout('V', None)
    self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.setWidgetResizable(True)
    self.setWidget(self.mainW)

    headerW, self.headerL = widgetAndLayout('H', self.mainL, top='s')
    headerW.setContextMenuPolicy(Qt.CustomContextMenu)
    headerW.customContextMenuRequested.connect(self.contextMenu)
    self.specialW, self.specialL = widgetAndLayout('V', self.mainL, top='s')
    self.specialW.setContextMenuPolicy(Qt.CustomContextMenu)
    self.specialW.customContextMenuRequested.connect(self.contextMenu)
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
    self.btnDatabase = TextButton('Database details', self, [Command.SHOW,'Database'], self.mainL, \
                                  'Show / hide database details', checkable= True, style="margin-top: 15px")
    self.metaDatabaseW, self.metaDatabaseL = widgetAndLayout('V', self.mainL)
    self.metaDatabaseW.setMaximumWidth(self.width())
    self.mainL.addStretch(1)


  def contextMenu(self, pos:QPoint) -> None: #TODO_P3 move all context menu of this type to separate function
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
        Action(value,                     self, [Command.CHANGE_EXTRACTOR, key], context)
      context.addSeparator()
      Action('Save image',                self, [Command.SAVE_IMAGE],            context)
    #TODO_P2 not save now: when opening text files, system can crash
    # Action('Open file with another application', self.changeExtractor, context, self, name='_openExternal_')
    Action('Open folder in file browser', self, [Command.OPEN_FILEBROWSER],      context)
    Action('Hide',                        self, [Command.HIDE],                  context)
    context.exec(self.mapToGlobal(pos))
    return


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
      self.headerL.itemAt(i).widget().setParent(None)       # type: ignore
    for i in reversed(range(self.metaDetailsL.count())):
      self.metaDetailsL.itemAt(i).widget().setParent(None)  # type: ignore
    if self.metaVendorL.itemAt(0) is not None:
      self.metaVendorL.itemAt(0).widget().setParent(None)   # type: ignore
    if self.metaUserL.itemAt(0) is not None:
      self.metaUserL.itemAt(0).widget().setParent(None)     # type: ignore
    for i in reversed(range(self.metaDatabaseL.count())):
      self.metaDatabaseL.itemAt(i).widget().setParent(None) # type: ignore
    for i in reversed(range(self.specialL.count())):
      self.specialL.itemAt(i).widget().setParent(None) # type: ignore
    self.specialW.hide()
    self.metaDetailsW.hide()
    self.metaVendorW.hide()
    self.metaUserW.hide()
    self.metaDatabaseW.hide()
    self.btnDetails.setChecked(True)
    self.btnVendor.setChecked(True)
    self.btnUser.setChecked(True)
    self.btnDatabase.setChecked(False)
    if not docID:  #if given '' docID, return
      return
    # Create new
    if docID!='redraw':
      self.docID = docID
    if self.docID=='':
      return
    self.doc   = self.comm.backend.db.getDoc(self.docID)
    if '-name' not in self.doc:  #keep empty details and wait for user to click
      self.comm.changeTable.emit('','')
      return
    if self.doc['-type'][0]=='-':
      ontologyNode = defaultOntologyNode
    else:
      ontologyNode = self.comm.backend.db.ontology[self.doc['-type'][0]]['prop']
    label = self.doc['-name'] if len(self.doc['-name'])<80 else self.doc['-name'][:77]+'...'
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
      elif key=='-tags':
        tags = ['_curated_' if i=='_curated' else f'#{i}' for i in self.doc[key]]
        tags = ['\u2605'*int(i[2]) if i[:2]=='#_' else i for i in tags]
        label = QLabel('Tags: '+' '.join(tags))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.metaDetailsL.addWidget(label)
      elif key[0] in ['_','-'] or key in ['shasum']:
        if key in ['_attachments']:
          continue
        label = QLabel(f'{key}: {str(self.doc[key])}')
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.metaDatabaseL.addWidget(label)
        self.btnDatabase.setChecked(False)
      elif key=='metaVendor':
        self.btnVendor.show()
        label = QLabel()
        label.setWordWrap(True)
        label.setText(yaml.dump(self.doc[key], indent=4))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.metaVendorL.addWidget(label)
        self.metaVendorW.show()
      elif key=='metaUser':
        self.btnUser.show()
        label = QLabel()
        label.setWordWrap(True)
        label.setText(yaml.dump(self.doc[key], indent=4))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.metaUserL.addWidget(label)
        self.metaUserW.show()
      else:
        link = False
        ontologyItem = [i for i in ontologyNode if i['name']==key]
        if '\n' in self.doc[key]:     #if returns in value: format nicely
          _, labelL = widgetAndLayout('H', self.metaDetailsL, top='s', bottom='s')
          labelL.addWidget(QLabel(f'{key}: '), alignment=Qt.AlignTop) # type: ignore
          text = QTextEdit()
          text.setMarkdown(self.doc[key])
          text.setReadOnly(True)
          labelL.addWidget(text)
        else:
          if len(ontologyItem)==1 and 'list' in ontologyItem[0]:
            if not isinstance(ontologyItem[0]['list'], list):                #choice among docType
              table  = self.comm.backend.db.getView('viewDocType/'+ontologyItem[0]['list'])
              choices= [i for i in table if i['id']==self.doc[key]]
              if len(choices)==1:
                value = '\u260D '+choices[0]['value'][0]
                link = True
          elif isinstance(self.doc[key], list):
            value = ', '.join(self.doc[key])
          else:
            value = self.doc[key]
          label = Label(f'{key.capitalize()}: {value}', function=self.clickLink if link else None, docID=self.doc[key])
          label.setTextInteractionFlags(Qt.TextSelectableByMouse)
          self.metaDetailsL.addWidget(label)
        self.metaDetailsW.show()
    return


  def execute(self, command:list[Any]) -> None:
    """
    Hide / show the widget underneath the button

    Args:
      command (list): area to show/hide
    """
    filePath = Path(self.doc['-branch'][0]['path'])
    if command[0] is Command.SHOW:
      if getattr(self, f'btn{command[1]}').isChecked(): #get button in question
        getattr(self, f'meta{command[1]}W').show()
      else:
        getattr(self, f'meta{command[1]}W').hide()
    elif command[0] is Command.OPEN_FILEBROWSER or command[0] is Command.OPEN_EXTERNAL:
      filePath = self.comm.backend.basePath/filePath
      filePath = filePath if command[0] is Command.OPEN_EXTERNAL else filePath.parent
      if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filePath))
      elif platform.system() == 'Windows':    # Windows
        os.startfile(filePath) # type: ignore[attr-defined]
      else:                                   # linux variants
        subprocess.call(('xdg-open', filePath))
    elif command[0] is Command.SAVE_IMAGE:
      image = self.doc['image']
      if image.startswith('data:image/'):
        imageType = image[11:14] if image[14]==';' else image[11:15]
      else:
        imageType = 'svg'
      saveFilePath = self.comm.backend.basePath/filePath.parent/f'{filePath.stem}_PastaExport.{imageType.lower()}'
      path = self.doc['-branch'][0]['path']
      if not path.startswith('http'):
        path = (self.comm.backend.basePath/path).as_posix()
      self.comm.backend.testExtractor(path, recipe='/'.join(self.doc['-type']), saveFig=str(saveFilePath))
    elif command[0] is Command.HIDE:
      self.comm.backend.db.hideShow(self.docID)
      self.comm.changeTable.emit('','')
      self.comm.changeDetails.emit(self.doc['_id'])
    elif command[0] is Command.CHANGE_EXTRACTOR:
      self.doc['-type'] = command[1]
      self.comm.backend.useExtractors(filePath, self.doc['shasum'], self.doc)  #any path is good since the file is the same everywhere; data-changed by reference
      if len(self.doc['-type'])>1 and len(self.doc['image'])>1:
        self.doc = self.comm.backend.db.updateDoc({'image':self.doc['image'], '-type':self.doc['-type']}, self.doc['_id'])
        self.comm.changeTable.emit('','')
        self.comm.changeDetails.emit(self.doc['_id'])
    return


  @Slot()
  def testExtractor(self) -> None:
    """
    User selects to test extractor on this dataset
    """
    logging.debug('details:testExtractor')
    if len(self.doc)>1:
      path = Path(self.doc['-branch'][0]['path'])
      if not path.as_posix().startswith('http'):
        path = self.comm.backend.basePath/path
      report = self.comm.backend.testExtractor(path, outputStyle='html', recipe='/'.join(self.doc['-type']))
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


class Command(Enum):
  """ Commands used in this file """
  SHOW             = 1
  CHANGE_EXTRACTOR = 2
  SAVE_IMAGE       = 3
  OPEN_FILEBROWSER = 4
  OPEN_EXTERNAL    = 5
  HIDE             = 6
