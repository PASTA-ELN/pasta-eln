""" Widget that shows a leaf in the project tree """
from PySide6.QtWidgets import QWidget, QHBoxLayout, QFormLayout, QLabel, QSizePolicy  # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot, QByteArray, QSize# pylint: disable=no-name-in-module
from PySide6.QtSvgWidgets import QSvgWidget       # pylint: disable=no-name-in-module
from PySide6.QtGui import QPixmap, QImage         # pylint: disable=no-name-in-module

class Leaf(QWidget):
  """ Widget that shows a leaf in the project tree """
  def __init__(self, comm, docID):
    super().__init__()
    doc = comm.backend.db.getDoc(docID)
    if ('content' in doc and doc['content']!='') or \
       ('image' in doc and doc['image']!=''    ): #have right side
      mainL = QHBoxLayout(self)
      leftW  = QWidget()
      leftL  = QFormLayout(leftW)
      mainL.addWidget(leftW)
      rightW = QWidget()
      rightW.setMaximumSize(QSize(300,200))
      rightL = QHBoxLayout(rightW)
      if 'image' in doc and doc['image']!='': #show image
        #similar in widgetDetails
        if doc['image'].startswith('data:image/'): #jpg or png image
          byteArr = QByteArray.fromBase64(bytearray(doc['image'][22:], encoding='utf-8'))
          imageW = QImage()
          imageType = doc['image'][11:15].upper()
          imageW.loadFromData(byteArr, imageType)
          pixmap = QPixmap.fromImage(imageW)
          label = QLabel()
          label.setPixmap(pixmap)
          rightL.addWidget(label)
        elif doc['image'].startswith('<?xml'): #svg image
          imageW = QSvgWidget()
          policy = imageW.sizePolicy()
          policy.setVerticalPolicy(QSizePolicy.Fixed)
          imageW.setSizePolicy(policy)
          imageW.renderer().load(bytearray(doc['image'], encoding='utf-8'))
          rightL.addWidget(imageW)
        else:
          print('WidgetProjectLeaf:What is this image |'+doc['image'][:50]+'|')
      else: #show content
        rightL.addWidget(QLabel(doc['content']))
      mainL.addWidget(rightW)
    else:  #no right side
      leftL = QFormLayout(self)

    #fill left side
    name = doc['-name']
    tags = ', '.join(doc['tags']) if 'tags' in doc else ''
    qrCode = ', '.join(doc['qrCode']) if 'qrCode' in doc else ''
    leftL.addRow(QLabel('NAME: '),QLabel(name))
    leftL.addRow(QLabel('Tags: '),QLabel(tags))
    if len(qrCode)>0:
      leftL.addRow(QLabel('QR-code: '),QLabel(qrCode))
    for key,value in doc.items():
      if key[0] in ['_','-']:
        continue
      if key in ['image','content','tags','qrCode','metaVendor','metaUser','shasum']:
        continue
      leftL.addRow(QLabel(key+':'),QLabel(str(value)))
