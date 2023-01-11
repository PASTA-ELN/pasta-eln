""" widget that shows the details of the items """
import json
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy   # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot, QByteArray   # pylint: disable=no-name-in-module
from PySide6.QtSvgWidgets import QSvgWidget   # pylint: disable=no-name-in-module
from PySide6.QtGui import QPixmap, QImage     # pylint: disable=no-name-in-module

try:
  from .style import TextButton
except:
  from style import TextButton

class Details(QWidget):
  """ widget that shows the details of the items """
  def __init__(self, comm):
    super().__init__()
    self.backend = comm.backend
    comm.changeDetails.connect(self.changeDetails)

    # GUI stuff
    mainL = QVBoxLayout()
    self.imageW = QWidget()
    self.imageW.setMinimumHeight(400)
    self.imageL = QVBoxLayout(self.imageW)
    mainL.addWidget(self.imageW)
    self.btnDetails = TextButton('Details', self.showArea, 'Details', 'Show / hide details', True)
    self.btnDetails.hide()
    mainL.addWidget(self.btnDetails)
    self.metaDetailsW  = QWidget()
    self.metaDetailsL = QVBoxLayout(self.metaDetailsW)
    mainL.addWidget(self.metaDetailsW)
    self.btnVendor = TextButton('Vendor metadata', self.showArea, 'Vendor', 'Show / hide vendor metadata', True)
    self.btnVendor.setStyleSheet("margin-top: 15px")
    self.btnVendor.hide()
    mainL.addWidget(self.btnVendor)
    self.metaVendorW   = QWidget()
    self.metaVendorL = QVBoxLayout(self.metaVendorW)
    mainL.addWidget(self.metaVendorW)
    self.btnUser = TextButton('User metadata', self.showArea, 'User', 'Show / hide user metadata', True)
    self.btnUser.setStyleSheet("margin-top: 15px")
    self.btnUser.hide()
    mainL.addWidget(self.btnUser)
    self.metaUserW     = QWidget()
    self.metaUserL = QVBoxLayout(self.metaUserW)
    mainL.addWidget(self.metaUserW)
    self.btnDatabase = TextButton('Database details', self.showArea, 'Database', 'Show / hide database details', True)
    self.btnDatabase.setStyleSheet("margin-top: 15px")
    self.btnDatabase.hide()
    mainL.addWidget(self.btnDatabase)
    self.metaDatabaseW = QWidget()
    self.metaDatabaseL = QVBoxLayout(self.metaDatabaseW)
    mainL.addWidget(self.metaDatabaseW)
    mainL.addStretch(1)
    self.setLayout(mainL)


  @Slot(str)
  def changeDetails(self, docID):
    """
    What happens when details should change

    Args:
      docID (str): document-id
    """
    # show previously hidden buttons
    self.btnDetails.show()
    self.btnVendor.show()
    self.btnUser.show()
    self.btnDatabase.show()
    # Delete old widgets from layout
    if self.metaDetailsL.itemAt(0) is not None:
      self.metaDetailsL.itemAt(0).widget().setParent(None)
      self.metaVendorL.itemAt(0).widget().setParent(None)
      self.metaUserL.itemAt(0).widget().setParent(None)
      self.metaDatabaseL.itemAt(0).widget().setParent(None)
    if self.imageL.itemAt(0) is not None:
      self.imageL.itemAt(0).widget().setParent(None)
    # Create new
    doc   = self.backend.db.getDoc(docID)
    for key in doc:
      if key=='image':
        if doc['image'].startswith('data:image/png;base64'): #png image
          byteArr = QByteArray.fromBase64(bytearray(doc[key][22:], encoding='utf-8'))
          image = QImage()
          image.loadFromData(byteArr, 'PNG')
          pixmap = QPixmap.fromImage(image)
          label = QLabel()
          label.setPixmap(pixmap)
          self.imageL.addWidget(label)
        elif doc['image'].startswith('<?xml'): #svg image
          image = QSvgWidget()
          policy = image.sizePolicy()
          policy.setVerticalPolicy(QSizePolicy.Fixed)
          image.setSizePolicy(policy)
          image.renderer().load(bytearray(doc[key], encoding='utf-8'))
          self.imageL.addWidget(image)
          self.imageW.show()
      elif key.startswith('_') or key.startswith('-'):
        label = QLabel(key+': '+str(doc[key]))
        label.setWordWrap(True)
        self.metaDatabaseL.addWidget(label)
      elif key=='metaVendor':
        label = QLabel()
        label.setWordWrap(True)
        label.setText(json.dumps(doc[key], indent=2)[2:-2]) #remove initial+trailing defaults
        self.metaVendorL.addWidget(label)
      elif key=='metaUser':
        label = QLabel()
        label.setWordWrap(True)
        label.setText(json.dumps(doc[key], indent=2)[2:-2]) #remove initial+trailing defaults
        self.metaUserL.addWidget(label)
      else:
        self.metaDetailsL.addWidget( QLabel(key+': '+str(doc[key])) )
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
