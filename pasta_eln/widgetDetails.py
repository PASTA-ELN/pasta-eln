""" widget that shows the details of the items """
import json
from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel, QSizePolicy   # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt, Slot, QByteArray   # pylint: disable=no-name-in-module
from PySide6.QtSvgWidgets import QSvgWidget       # pylint: disable=no-name-in-module
from PySide6.QtGui import QPixmap, QImage         # pylint: disable=no-name-in-module
from .style import TextButton

class Details(QScrollArea):
  """ widget that shows the details of the items """
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    comm.changeDetails.connect(self.changeDetails)

    # GUI stuff
    self.mainW = QWidget()
    self.mainL = QVBoxLayout(self.mainW)
    self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.setWidgetResizable(True)
    self.setWidget(self.mainW)

    self.editBtn = TextButton('Edit',self.callEdit)
    self.editBtn.hide()
    self.mainL.addWidget(self.editBtn)
    self.imageW = QWidget()
    self.imageW.setMinimumHeight(400)
    self.imageL = QVBoxLayout(self.imageW)
    self.mainL.addWidget(self.imageW)
    self.btnDetails = TextButton('Details', self.showArea, 'Details', 'Show / hide details', True)
    self.btnDetails.hide()
    self.mainL.addWidget(self.btnDetails)
    self.metaDetailsW  = QWidget()
    self.metaDetailsL = QVBoxLayout(self.metaDetailsW)
    self.mainL.addWidget(self.metaDetailsW)
    self.btnVendor = TextButton('Vendor metadata', self.showArea, 'Vendor', 'Show / hide vendor metadata', True)
    self.btnVendor.setStyleSheet("margin-top: 15px")
    self.btnVendor.hide()
    self.mainL.addWidget(self.btnVendor)
    self.metaVendorW   = QWidget()
    self.metaVendorL = QVBoxLayout(self.metaVendorW)
    self.mainL.addWidget(self.metaVendorW)
    self.btnUser = TextButton('User metadata', self.showArea, 'User', 'Show / hide user metadata', True)
    self.btnUser.setStyleSheet("margin-top: 15px")
    self.btnUser.hide()
    self.mainL.addWidget(self.btnUser)
    self.metaUserW     = QWidget()
    self.metaUserL = QVBoxLayout(self.metaUserW)
    self.mainL.addWidget(self.metaUserW)
    self.btnDatabase = TextButton('Database details', self.showArea, 'Database', 'Show / hide database details', True)
    self.btnDatabase.setStyleSheet("margin-top: 15px")
    self.btnDatabase.hide()
    self.mainL.addWidget(self.btnDatabase)
    self.metaDatabaseW = QWidget()
    self.metaDatabaseL = QVBoxLayout(self.metaDatabaseW)
    self.mainL.addWidget(self.metaDatabaseW)
    self.mainL.addStretch(1)

  #Textbutton initially unchecked: database details

  @Slot(str)
  def changeDetails(self, docID):
    """
    What happens when details should change

    Args:
      docID (str): document-id
    """
    # show previously hidden buttons
    if docID!='':
      self.editBtn.show()
    self.btnDetails.show()
    self.btnVendor.show()
    self.btnUser.show()
    self.btnDatabase.show()
    # Delete old widgets from layout
    if self.metaDetailsL.itemAt(0) is not None:
      self.metaDetailsL.itemAt(0).widget().setParent(None)
    if self.metaVendorL.itemAt(0) is not None:
      self.metaVendorL.itemAt(0).widget().setParent(None)
    if self.metaUserL.itemAt(0) is not None:
      self.metaUserL.itemAt(0).widget().setParent(None)
    if self.metaDatabaseL.itemAt(0) is not None:
      self.metaDatabaseL.itemAt(0).widget().setParent(None)
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
    for key in self.doc:
      if key=='image':
        #similar in widgetProjectLeaf
        if self.doc['image'].startswith('data:image/'): #jpg or png image
          byteArr = QByteArray.fromBase64(bytearray(self.doc[key][22:], encoding='utf-8'))
          image = QImage()
          imageType = self.doc[key][11:15].upper()
          print(imageType)  #TODO not sure it is good for png and jpg: JPG;
          image.loadFromData(byteArr, imageType)
          pixmap = QPixmap.fromImage(image)
          label = QLabel()
          label.setPixmap(pixmap)
          self.imageL.addWidget(label)
        elif self.doc['image'].startswith('<?xml'): #svg image
          image = QSvgWidget()
          policy = image.sizePolicy()
          policy.setVerticalPolicy(QSizePolicy.Fixed)
          image.setSizePolicy(policy)
          image.renderer().load(bytearray(self.doc[key], encoding='utf-8'))
          self.imageL.addWidget(image)
          self.imageW.show()
        else:
          print('widgetDetails:image?',self.doc['image'][:50])
        self.imageW.show()
      elif key.startswith('_') or key.startswith('-'):
        label = QLabel(key+': '+str(self.doc[key]))
        label.setWordWrap(True)
        self.metaDatabaseL.addWidget(label)
        self.metaDatabaseW.show()
      elif key=='metaVendor':
        label = QLabel()
        label.setWordWrap(True)
        label.setText(json.dumps(self.doc[key], indent=2)[2:-2]) #remove initial+trailing defaults
        self.metaVendorL.addWidget(label)
        self.metaVendorW.show()
      elif key=='metaUser':
        label = QLabel()
        label.setWordWrap(True)
        label.setText(json.dumps(self.doc[key], indent=2)[2:-2]) #remove initial+trailing defaults
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
