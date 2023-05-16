""" widget that shows the details of the items """
from pathlib import Path
import platform, subprocess, os, base64, logging
from typing import Any
import yaml
from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMenu, QTextEdit  # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt, Slot, QPoint  # pylint: disable=no-name-in-module
from .style import TextButton, Image, Label, Action, showMessage
from .fixedStrings import defaultOntologyNode
from .communicate import Communicate

class Details(QScrollArea):
  """ widget that shows the details of the items """
  def __init__(self, comm:Communicate):
    super().__init__()
    self.comm = comm
    comm.changeDetails.connect(self.changeDetails)
    comm.testExtractor.connect(self.testExtractor)
    self.doc:dict[str,Any]  = {}
    self.docID= ''

    # GUI elements
    self.mainW = QWidget()
    self.mainL = QVBoxLayout(self.mainW)
    self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.setWidgetResizable(True)
    self.setWidget(self.mainW)

    headerW = QWidget()
    self.headerL = QHBoxLayout(headerW)
    self.mainL.addWidget(headerW)
    self.specialW = QWidget()
    self.specialW.setMaximumWidth(self.width())
    self.specialW.setContextMenuPolicy(Qt.CustomContextMenu)
    self.specialW.customContextMenuRequested.connect(self.contextMenu)
    self.specialL = QVBoxLayout(self.specialW)
    self.mainL.addWidget(self.specialW)
    self.btnDetails = TextButton('Details', self.showArea, self.mainL, 'Details', 'Show / hide details', \
                                  checkable=True, hide=True)
    self.metaDetailsW  = QWidget()
    self.metaDetailsW.setMaximumWidth(self.width())
    self.metaDetailsL = QVBoxLayout(self.metaDetailsW)
    self.mainL.addWidget(self.metaDetailsW)
    self.btnVendor = TextButton('Vendor metadata', self.showArea, self.mainL, 'Vendor', \
      'Show / hide vendor metadata', checkable=True, hide=True, style="margin-top: 15px")
    self.metaVendorW   = QWidget()
    self.metaVendorW.setMaximumWidth(self.width())
    self.metaVendorL = QVBoxLayout(self.metaVendorW)
    self.mainL.addWidget(self.metaVendorW)
    self.btnUser = TextButton('User metadata', self.showArea, self.mainL, 'User', 'Show / hide user metadata',\
      checkable=True, hide=True, style="margin-top: 15px")
    self.metaUserW     = QWidget()
    self.metaUserW.setMaximumWidth(self.width())
    self.metaUserL = QVBoxLayout(self.metaUserW)
    self.mainL.addWidget(self.metaUserW)
    self.btnDatabase = TextButton('Database details', self.showArea, self.mainL, 'Database', \
      'Show / hide database details', checkable= True, hide=True, style="margin-top: 15px")
    self.metaDatabaseW = QWidget()
    self.metaDatabaseW.setMaximumWidth(self.width())
    self.metaDatabaseL = QVBoxLayout(self.metaDatabaseW)
    self.mainL.addWidget(self.metaDatabaseW)
    self.mainL.addStretch(1)


  def contextMenu(self, pos:QPoint) -> None:
    """
    Create a context menu

    Args:
      pos (position): Position to create context menu at
    """
    extractors = self.comm.backend.configuration['extractors']
    extension = Path(self.doc['-branch'][0]['path']).suffix[1:]
    extractors = extractors[extension]
    baseDocType= self.doc['-type'][0]
    choices= {key:value for key,value in extractors.items() \
                if key.startswith(baseDocType)}
    context = QMenu(self)
    for key,value in choices.items():
      Action(value, self.changeExtractor, context, self, name=key)
    context.addSeparator()
    Action('Open folder in file browser', self.changeExtractor, context, self, name='_openInFileBrowser_')
    Action('Save as image',               self.changeExtractor, context, self, name='_saveAsImage_')
    context.exec(self.mapToGlobal(pos))
    return

  def changeExtractor(self) -> None:
    """
    What happens when user changes extractor
    """
    filePath = Path(self.doc['-branch'][0]['path'])
    if self.sender().data()=='_openInFileBrowser_':
      filePath = self.comm.backend.basePath/filePath
      if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filePath.parent))
      elif platform.system() == 'Windows':    # Windows
        os.startfile(filePath.parent) # type: ignore[attr-defined]
      else:                                   # linux variants
        subprocess.call(('xdg-open', filePath.parent))
    elif self.sender().data()=='_saveAsImage_':
      image = self.doc['image']
      if image.startswith('data:image/'):
        imageType = image[11:14] if image[14]==';' else image[11:15]
        image = image[22:] if image[21]==',' else image[23:]
      else:
        imageType = 'svg'
      saveFilePath = filePath.parent/(filePath.stem+'_PastaExport.'+imageType.lower())
      if imageType == 'svg':
        with open(self.comm.backend.basePath/saveFilePath,'w', encoding='utf-8') as fOut:
          fOut.write(image)
      else:
        with open(self.comm.backend.basePath/saveFilePath, "wb") as fOut:
          fOut.write(base64.decodebytes(image.encode('utf-8')))
    else:
      self.doc['-type'] = self.sender().data().split('/')
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
      report = self.comm.backend.testExtractor(path, outputStyle='html')
      showMessage(self, 'Report of extractor test', report, style='QLabel {min-width: 800px}')
    return


  @Slot(str)
  def changeDetails(self, docID:str) -> None:
    """
    What happens when details should change

    Args:
      docID (str): document-id; '' string=draw nothing; 'redraw' implies redraw
    """
    logging.debug('details:changeDetails |'+docID+'|')
    # show previously hidden buttons
    if docID=='':
      self.btnDetails.show()
      self.btnVendor.show()
      self.btnUser.show()
      self.btnDatabase.show()
    else:
      self.btnDetails.show()
      self.btnVendor.show()
      self.btnUser.show()
      self.btnDatabase.show()
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
    if self.specialL.itemAt(0) is not None:
      self.specialL.itemAt(0).widget().setParent(None)      # type: ignore
    self.specialW.hide()
    self.metaDetailsW.hide()
    self.metaVendorW.hide()
    self.metaUserW.hide()
    self.metaDatabaseW.hide()
    if docID=='':  #if given '' docID, return
      return
    # Create new
    if docID!='redraw':
      self.docID = docID
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
    # TextButton('Edit',self.callEdit, self.headerL)
    for key in self.doc:
      if key=='image':
        width = self.comm.backend.configuration['GUI']['imageWidthDetails'] \
                if hasattr(self.comm.backend, 'configuration') else 300
        Image(self.doc['image'], self.specialL, width=width)
        self.specialW.show()
      elif key=='content':
        text = QTextEdit()
        text.setMarkdown(self.doc['content'])
        text.setReadOnly(True)
        self.specialL.addWidget(text)
        self.specialW.show()
        #TODO_P3 design: make full width; scale fonts appropriately
      elif key=='-tags':
        tags = ['_curated_' if i=='_curated' else '#'+i for i in self.doc[key]]
        tags = ['\u2605'*int(i[2]) if i[:2]=='#_' else i for i in tags]
        label = QLabel('Tags: '+' '.join(tags))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.metaDetailsL.addWidget(label)
      elif key[0] in ['_','-'] or key in ['shasum']:
        if key in ['_attachments']:
          continue
        label = QLabel(key+': '+str(self.doc[key]))
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.metaDatabaseL.addWidget(label)
        self.btnDatabase.setChecked(False)
      elif key=='metaVendor':
        label = QLabel()
        label.setWordWrap(True)
        label.setText(yaml.dump(self.doc[key], indent=4))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.metaVendorL.addWidget(label)
        self.metaVendorW.show()
      elif key=='metaUser':
        label = QLabel()
        label.setWordWrap(True)
        label.setText(yaml.dump(self.doc[key], indent=4))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.metaUserL.addWidget(label)
        self.metaUserW.show()
      else:
        link = False
        ontologyItem = [i for i in ontologyNode if i['name']==key]
        if len(ontologyItem)==1 and 'list' in ontologyItem[0]:
          if not isinstance(ontologyItem[0]['list'], list):                #choice among docType
            table  = self.comm.backend.db.getView('viewDocType/'+ontologyItem[0]['list'])
            choices= [i for i in table if i['id']==self.doc[key]]
            if len(choices)==1:
              value = '\u260D '+choices[0]['value'][0]
              link = True
        elif isinstance(self.doc[key], list):
          value = ', '.join(self.doc[key])
        elif '\n' in self.doc[key]:     #if returns in value
          value = '\n    '+self.doc[key].replace('\n','\n    ')
        else:
          value = self.doc[key]
        label = Label(key.capitalize()+': '+value, function=self.clickLink if link else None, docID=self.doc[key])
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.metaDetailsL.addWidget(label)
        self.metaDetailsW.show()
    return


  def showArea(self) -> None:
    """
    Hide / show the widget underneath the button
    """
    name = self.sender().accessibleName()
    if getattr(self, 'btn'+name).isChecked(): #get button in question
      getattr(self, 'meta'+name+'W').show()
    else:
      getattr(self, 'meta'+name+'W').hide()
    return


  def callEdit(self) -> None:
    """
    Call edit dialoge
    """
    if self.doc['-type'][0][0]=='x':
      showMessage(self, 'Information','Cannot change project hierarchy here.')
    else:
      self.comm.formDoc.emit(self.doc)
      self.comm.changeTable.emit('','')
      self.comm.changeDetails.emit('redraw')
    return


  def clickLink(self, label:str, docID:str) -> None:
    """
    Click link in details

    Args:
      label (str): label on link
      docID (str): docID to which to link
    """
    logging.debug('used link on '+label+'|'+docID)
    self.comm.changeDetails.emit(docID)
    return
