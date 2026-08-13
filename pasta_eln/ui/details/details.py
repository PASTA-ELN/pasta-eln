""" This Widget is the right sidebar that shows the details of the currently selected item """
from enum import Enum
from typing import Any
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QShowEvent, Qt
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QMenu, QScrollArea, QSplitter, QTextEdit,
                               QVBoxLayout, QWidget)
from pasta_eln.fixed_strings_json import SORTED_DB_KEYS
from pasta_eln.misc_tools import clearLayout, makeStringWrappable
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import Label, ResizeImage
from pasta_eln.ui.details.details_hier_item import DetailsHierItem
from pasta_eln.ui.widget import SPACE, Button, ButtonStyle, Widget


class Details(Widget):
  """The right sidebar that shows the details of the currently selected item"""
  becameVisible = Signal()

  def __init__(self, comm: Communicate):
    """Create a details pane on the right-hand side
    Args:
      comm (Communicate): communication pipeline to get colors, etc.
    """
    super().__init__()
    self.comm = comm
    self.docID = ''
    self.data: dict[str, Any] = {'content': ''}

    ### HEADER WIDGETS
    self.titleLabel = Label('', 'h1')
    self.titleLabel.setWordWrap(True)
    self.editButton = Button('Edit', self, Command.EDIT, icon='ri.edit-2-fill', style=ButtonStyle.HIGHLIGHTED)
    self.moreButton = Button('More', self, icon='ri.more-fill', style=ButtonStyle.PRIMARY)
    self.moreMenu   = QMenu(self)
    self.moreMenu.addAction('Copy document ID', self.copyDocumentId)
    self.moreButton.setMenu(self.moreMenu)

    # Header Layout
    self.headerL = QHBoxLayout()
    self.headerL.addWidget(self.titleLabel, stretch=1)
    self.headerL.addWidget(self.editButton)
    self.headerL.addWidget(self.moreButton)
    self.headerW = QWidget()
    self.headerW.setLayout(self.headerL)

    # Tags TODO
    # INFOS like doctype, status and hierarchy

    # Image/content Preview
    self.contentPreviewL = QVBoxLayout()
    self.contentPreviewL.setContentsMargins(0, 0, 0, 0)
    self.contentPreviewW = QWidget()
    self.contentPreviewW.setLayout(self.contentPreviewL)

    # Body (Shows all the details of the current item)
    self.bodyL = QVBoxLayout()
    self.bodyL.setContentsMargins(0, 0, 0, 0)
    self.bodyW = QWidget()
    self.bodyW.setLayout(self.bodyL)

    # Detail-Scrollarea (contains body)
    self.scrollarea = QScrollArea(widgetResizable=True)
    self.scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.scrollarea.setContentsMargins(0, 0, 0, 0)
    self.scrollarea.setWidget(self.bodyW)
    self.textEdit = QTextEdit()
    self.textEdit.setMarkdown(self.data['content'])
    self.textEdit.setReadOnly(True)

    # Vertical Splitter to resize contentPreview
    self.splitter = QSplitter(Qt.Orientation.Vertical, handleWidth=3)
    self.splitter.addWidget(self.contentPreviewW)
    self.splitter.setStretchFactor(0, 1)
    self.splitter.addWidget(self.scrollarea)
    self.splitter.setStretchFactor(1, 1)
    self.splitter.setSizes([200, self.splitter.size().height() - 200])

    # Main Layout
    self.mainLayout = QVBoxLayout()
    self.mainLayout.setContentsMargins(SPACE.M, 0, 0, 0)
    self.mainLayout.addWidget(self.headerW)
    self.mainLayout.addWidget(self.splitter, stretch=0)
    self.setLayout(self.mainLayout)

    # Signals
    self.comm.changeDetails.connect(self.onDetailsChanged)
    self.comm.backendThread.worker.beSendDoc.connect(self.onGetData)

    # CODE
    self.hide()


  @Slot(str)
  def onDetailsChanged(self, docID: str) -> None:
    """
    What happens when the displayed item changes.
    Args:
      docID (str): Document ID of the item to be displayed.
    """
    if docID:
      self.docID = docID
      self.comm.uiRequestDoc.emit(self.docID)
    else:
      self.hide()


  @Slot(dict)
  def onGetData(self, data: dict[str, Any]) -> None:
    """ Function to handle the received data
    Args:
      data (dict): dictionary containing the document data
    """
    if 'id' in data and data['id'] == self.docID:
      self.data = data
      self.paint()


  def paint(self) -> None:
    """
    Fill in the things that change between displaying different items
    """
    self.show()
    dataHierarchyNode = self.comm.dataHierarchyNodes[self.data['type'][0]]

    # HEADER
    self.titleLabel.setText(makeStringWrappable(self.data['name'], nChars=15))

    # BODY
    # clear old items
    clearLayout(self.contentPreviewL)
    clearLayout(self.bodyL)
    self.contentPreviewW.hide()
    # Init the collapsible Items that contain all the details
    detailsItem = DetailsHierItem(self.comm, 'Details', dataHierarchyNode)
    vendorItem  = DetailsHierItem(self.comm, 'Vendor Metadata', dataHierarchyNode)
    userItem    = DetailsHierItem(self.comm, 'User Metadata', dataHierarchyNode)
    elnItem     = DetailsHierItem(self.comm, 'ELN Details', dataHierarchyNode, startCollapsed=True)
    # Populate the Content/Image
    for key in self.data:
      if key == 'name':
        continue
      if key == 'image':
        ResizeImage(self.data['image'], self.contentPreviewL)
        self.contentPreviewW.show()
      elif key == 'content':
        self.contentPreviewL.addWidget(self.textEdit)
        self.contentPreviewW.show()
        size = min([int(self.textEdit.document().size().height()), self.splitter.size().height() // 2])
        self.splitter.setSizes([size, self.splitter.size().height() - size])
      elif key == 'metaVendor':
        vendorItem.addContent('metaVendor', self.data['metaVendor'])
      elif key == 'metaUser':
        userItem.addContent('metaUser', self.data['metaUser'])
      elif key in SORTED_DB_KEYS:
        elnItem.addContent(key, self.data[key])
      else:
        detailsItem.addContent(key, self.data[key])

    if detailsItem.content:
      self.bodyL.addWidget(detailsItem)
    if vendorItem.content:
      self.bodyL.addWidget(vendorItem)
    if userItem.content:
      self.bodyL.addWidget(userItem)
    if elnItem.content:
      self.bodyL.addWidget(elnItem)
    self.bodyL.addStretch(0)


  def execute(self, command: Command) -> None:
    """Handle commands emitted by the details controls."""
    if command is Command.EDIT:
      self.onEditButtonClicked()


  def showEvent(self, event: QShowEvent) -> None:
    """Notify the containing splitter when the details panel first becomes visible
    Args:
      event (QShowEvent): event
    """
    super().showEvent(event)
    self.becameVisible.emit()


  @Slot()
  def copyDocumentId(self) -> None:
    """Copy the selected document identifier from this details panel."""
    QApplication.clipboard().setText(self.docID)


  @Slot()
  def onEditButtonClicked(self) -> None:
    """
    What happens, when the edit Button in the Top-right is clicked
    TODO: The Edit Form is not working as Raphael expects it to. (It's buggy when I use it this way...)
    """
    print('Edit Button Clicked, FormDoc still buggy')
    # Open the edit Form
    self.comm.formDoc.emit(self.data)


class Command(Enum):
  """Commands handled by :class:`Details`."""
  EDIT = 1
