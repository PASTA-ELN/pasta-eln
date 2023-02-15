""" widget that shows the details of the items """
import json
from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel   # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt, Slot, QByteArray   # pylint: disable=no-name-in-module
from PySide6.QtSvgWidgets import QSvgWidget       # pylint: disable=no-name-in-module
from PySide6.QtGui import QPixmap, QImage         # pylint: disable=no-name-in-module
from .style import TextButton, Image, Label

class Details(QScrollArea):
  """ widget that shows the details of the items """
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    comm.changeDetails.connect(self.changeDetails)
    self.doc  = {}

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
    self.imageL = QVBoxLayout(self.imageW)
    #TODO_P2 include extractor change
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


  @Slot(str)
  def changeDetails(self, docID):
    """
    What happens when details should change

    Args:
      docID (str): document-id
    """
    # show previously hidden buttons
    if docID!='':
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
    if docID=='':  #if given empty docID, return with empty content
      return
    # Create new
    self.doc   = self.comm.backend.db.getDoc(docID)
    Label(self.doc['-name'],'h1', self.headerL)
    self.editBtn = TextButton('Edit',self.callEdit, self.headerL)
    for key in self.doc:
      if key=='image':
        width = self.comm.backend.configuration['GUI']['imageWidthDetails'] \
                if hasattr(self.comm.backend, 'configuration') else 300
        Image(self.doc['image'], self.imageL, width=width)
        self.imageW.show()
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
        self.metaDetailsL.addWidget( QLabel(key+': '+str(self.doc[key])) )
        self.metaDetailsW.show()
    return


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
