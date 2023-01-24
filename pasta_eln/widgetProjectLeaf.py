""" Widget that shows a leaf in the project tree """
from PySide6.QtWidgets import QWidget, QHBoxLayout, QFormLayout, QLabel, QApplication  # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt, Slot, QSize, QMimeData # pylint: disable=no-name-in-module
from PySide6.QtGui import QDrag         # pylint: disable=no-name-in-module

from .style import Image

class Leaf(QWidget):
  """ Widget that shows a leaf in the project tree """
  def __init__(self, comm, docID):
    super().__init__()
    doc = comm.backend.db.getDoc(docID)
    self.dragStartPosition = None

    # GUI parts
    if ('content' in doc and doc['content']!='') or \
       ('image' in doc and doc['image']!=''    ): #have right side
      mainL = QHBoxLayout(self)
      leftW  = QWidget()
      leftL  = QFormLayout(leftW)
      mainL.addWidget(leftW)
      rightW = QWidget()
      rightW.setMaximumWidth(comm.backend.configuration['GUI']['imageWidthProject'])
      rightW.setMaximumHeight(int(comm.backend.configuration['GUI']['imageWidthProject']/3*2))
      rightL = QHBoxLayout(rightW)
      if 'image' in doc and doc['image']!='': #show image
        Image(doc['image'], rightL)
      else: #show content
        rightL.addWidget(QLabel(doc['content']))
      mainL.addWidget(rightW)
    else:  #no right side: accept drop events
      leftL = QFormLayout(self)
      self.setAcceptDrops(True)

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


  def mousePressEvent(self, event):
    """
    Drag of Drag&Drop 1: re-implementation of mouse press event
    - save start point of drag

    Args:
      event (Event): mouse press event
    """
    if event.button() == Qt.LeftButton:
      self.dragStartPosition = event.pos()
    return
  def mouseMoveEvent(self, event):
    """
    Drag of Drag&Drop 2: re-implementation of mouse move event
    - if moved sufficiently, create dropAction

    Args:
      event (Event): mouse move event
    """
    #Not sure required
    # if event.button()==Qt.LeftButton or event.button()==Qt.RightButton: #move event is NoButton-Event
    #   return
    if (event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance():
      return
    drag = QDrag(self)
    mimeData = QMimeData()
    mimeData.setData('pasta/task', b'data')  #TODO_P2 give data
    drag.setMimeData(mimeData)
    dropAction = drag.exec(Qt.CopyAction | Qt.MoveAction)
    print(dropAction)
    return


  def dragEnterEvent(self, event):  #will not cause an issue with github's pylint
    """
    Drop of Drag&Drop 1: re-implementation of drag enter event
    - which types of data do I except in which leaf

    Args:
      event (Event): mouse move event
    """
    if event.mimeData().hasFormat('libfm/files') or event.mimeData().hasFormat('pasta/task'):
      event.acceptProposedAction()
    return
  def dropEvent(self, event):
    """
    Drag of Drag&Drop 2: re-implementation of successful drop event
    - what to do after user has succeeded

    Args:
      event (Event): mouse move event
    """
    if event.mimeData().hasFormat('libfm/files'):
      print('dropped file',event.mimeData().urls()[0].toLocalFile())
    elif event.mimeData().hasFormat('pasta/task'):
      print('received task for', self)  #TODO_P2
    event.acceptProposedAction()
    return
