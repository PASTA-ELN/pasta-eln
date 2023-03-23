""" widget that shows the details of the items """
import json
from pathlib import Path
from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMenu  # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt, Slot, QByteArray   # pylint: disable=no-name-in-module
from PySide6.QtSvgWidgets import QSvgWidget       # pylint: disable=no-name-in-module
from PySide6.QtGui import QPixmap, QImage, QAction# pylint: disable=no-name-in-module
from .style import TextButton, Image, Label

class Details(QScrollArea):
  """ widget that shows the details of the items """
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    comm.changeDetails.connect(self.changeDetails)
    self.doc  = {}
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
    self.imageW = QWidget()
    self.imageW.setContextMenuPolicy(Qt.CustomContextMenu)
    self.imageW.customContextMenuRequested.connect(self.contextMenu)
    self.imageL = QVBoxLayout(self.imageW)
    self.mainL.addWidget(self.imageW)
    self.btnDetails = TextButton('Details', self.showArea, self.mainL, 'Details', 'Show / hide details', \
                                  checkable=True, hide=True)
    self.metaDetailsW  = QWidget()
    self.metaDetailsL = QVBoxLayout(self.metaDetailsW)
    self.mainL.addWidget(self.metaDetailsW)
    self.btnVendor = TextButton('Vendor metadata', self.showArea, self.mainL, 'Vendor', \
      'Show / hide vendor metadata', checkable=True, hide=True, style="margin-top: 15px")
    self.metaVendorW   = QWidget()
    self.metaVendorL = QVBoxLayout(self.metaVendorW)
    self.mainL.addWidget(self.metaVendorW)
    self.btnUser = TextButton('User metadata', self.showArea, self.mainL, 'User', 'Show / hide user metadata',\
      checkable=True, hide=True, style="margin-top: 15px")
    self.metaUserW     = QWidget()
    self.metaUserL = QVBoxLayout(self.metaUserW)
    self.mainL.addWidget(self.metaUserW)
    self.btnDatabase = TextButton('Database details', self.showArea, self.mainL, 'Database', \
      'Show / hide database details', checkable= True, hide=True, style="margin-top: 15px")
    self.metaDatabaseW = QWidget()
    self.metaDatabaseL = QVBoxLayout(self.metaDatabaseW)
    self.mainL.addWidget(self.metaDatabaseW)
    self.mainL.addStretch(1)

  def contextMenu(self, pos):
    """
    Create a context menu

    Args:
      pos (position): Position to create context menu at
    """
    context = QMenu(self)
    mask   = '/'.join(self.doc['-type'][:3])
    choices= {key:value for key,value in self.comm.backend.configuration['extractors'].items() \
                if key.startswith(mask)}
    for key,value in choices.items():
      thisAction = QAction(value, self)
      thisAction.setData(key)
      thisAction.triggered.connect(self.changeExtractor)
      context.addAction(thisAction)
    context.exec(self.mapToGlobal(pos))
    return


  def changeExtractor(self):
    """
    What happens when user changes extractor
    """
    self.doc['-type'] = self.sender().data().split('/')
    self.comm.backend.useExtractors(Path(self.doc['-branch'][0]['path']), self.doc['shasum'], self.doc, \
      extractorRedo=True)  #any path is good since the file is the same everywhere; data-changed by reference
    if len(self.doc['-type'])>1 and len(self.doc['image'])>1:
      self.doc = self.comm.backend.db.updateDoc({'image':self.doc['image'], '-type':self.doc['-type']}, self.doc['_id'])
      self.comm.changeTable.emit('','',True)
      self.comm.changeDetails.emit(self.doc['_id'])
    return


  @Slot(str)
  def changeDetails(self, docID):
    """
    What happens when details should change

    Args:
      docID (str): document-id; 'empty' string=draw nothing; 'redraw' implies redraw
    """
    # show previously hidden buttons
    if docID=='empty':
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
      self.headerL.itemAt(i).widget().setParent(None)
    for i in reversed(range(self.metaDetailsL.count())):
      self.metaDetailsL.itemAt(i).widget().setParent(None)
    if self.metaVendorL.itemAt(0) is not None:
      self.metaVendorL.itemAt(0).widget().setParent(None)
    if self.metaUserL.itemAt(0) is not None:
      self.metaUserL.itemAt(0).widget().setParent(None)
    for i in reversed(range(self.metaDatabaseL.count())):
      self.metaDatabaseL.itemAt(i).widget().setParent(None)
    if self.imageL.itemAt(0) is not None:
      self.imageL.itemAt(0).widget().setParent(None)
    self.imageW.hide()
    self.metaDetailsW.hide()
    self.metaVendorW.hide()
    self.metaUserW.hide()
    self.metaDatabaseW.hide()
    if docID=='empty':  #if given empty docID, return with empty content
      return
    # Create new
    if docID!='redraw':
      self.docID = docID
    self.doc   = self.comm.backend.db.getDoc(self.docID)
    Label(self.doc['-name'],'h1', self.headerL)
    TextButton('Edit',self.callEdit, self.headerL)
    for key in self.doc:
      if key=='image':
        width = self.comm.backend.configuration['GUI']['imageWidthDetails'] \
                if hasattr(self.comm.backend, 'configuration') else 300
        Image(self.doc['image'], self.imageL, width=width)
        self.imageW.show()
      elif key=='-tags':
        tags = ['cur\u2605ted' if i=='_curated' else '#'+i for i in self.doc[key]]
        tags = ['\u2605'*int(i[2]) if i[:2]=='#_' else i for i in tags]
        self.metaDetailsL.addWidget( QLabel('Tags: '+' '.join(tags)))
      elif key.startswith('_') or key.startswith('-'):
        label = QLabel(key+': '+str(self.doc[key]))
        label.setWordWrap(True)
        self.metaDatabaseL.addWidget(label)
        self.btnDatabase.setChecked(False)
      elif key=='metaVendor':
        label = QLabel()
        label.setWordWrap(True)
        label.setText(json.dumps(self.doc[key], indent=2)[2:-2].replace('"','')) #remove initial+trailing defaults
        self.metaVendorL.addWidget(label)
        self.metaVendorW.show()
      elif key=='metaUser':
        label = QLabel()
        label.setWordWrap(True)
        label.setText(json.dumps(self.doc[key], indent=2)[2:-2].replace('"','')) #remove initial+trailing defaults
        self.metaUserL.addWidget(label)
        self.metaUserW.show()
      else:
        self.metaDetailsL.addWidget( QLabel(key.capitalize()+': '+str(self.doc[key])) )
        self.metaDetailsW.show()
    return

  #TODO_P1: render content better

  def showArea(self):
    """
    Hide / show the widget underneath the button
    """
    name = self.sender().accessibleName()
    if getattr(self, 'btn'+name).isChecked(): #get button in question
      getattr(self, 'meta'+name+'W').show()
    else:
      getattr(self, 'meta'+name+'W').hide()
    return

  def callEdit(self):
    """
    Call edit dialoge
    """
    self.comm.formDoc.emit(self.doc)
