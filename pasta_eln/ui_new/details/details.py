""""""
from typing import Any

import qtawesome
from PySide6.QtCore import QSize, Slot
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QScrollArea, QSplitter, QTextEdit, \
  QVBoxLayout, \
  QWidget

from pasta_eln.fixed_strings_json import SORTED_DB_KEYS
from pasta_eln.misc_tools import clearLayout, makeStringWrappable
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import Label, ResizeImage
from pasta_eln.ui_new.details.details_hier_item import DetailsHierItem


class Details(QWidget):
  """"""

  def __init__(self, comm: Communicate):
    super().__init__()
    self.comm = comm
    self.docID = ""
    self.data = {}

    ### HEADER WIDGETS
    # Title Label
    self.titleLabel = Label("", "h1")
    self.titleLabel.setWordWrap(True)

    # Edit Button
    self.editButton = QPushButton("Edit", default=True)
    iconColor = self.comm.palette.getThemeColor("background", "base")
    self.editButton.setIcon(qtawesome.icon("ri.edit-2-fill", color=iconColor))
    self.editButton.setIconSize(QSize(18, 18))
    self.editButton.clicked.connect(self.onEditButtonClicked)

    # Header Layout
    self.headerLayout = QHBoxLayout()
    self.headerLayout.addWidget(self.titleLabel, stretch=1)
    self.headerLayout.addWidget(self.editButton)
    self.header = QWidget()
    self.header.setLayout(self.headerLayout)

    # Tags TODO

    # Linked Items TODO

    # INFOS like doctype, status and hierarchy

    ### BODY WIDGETS
    # Image/content Preview
    self.contentPreviewLayout = QVBoxLayout()
    self.contentPreviewLayout.setContentsMargins(0, 0, 0, 0)
    self.contentPreviewWidget = QWidget()
    self.contentPreviewWidget.setLayout(self.contentPreviewLayout)

    # Body (Shows all the details of the current item)
    self.bodyLayout = QVBoxLayout()
    self.bodyLayout.setContentsMargins(0, 0, 0, 0)
    self.body = QWidget()
    self.body.setLayout(self.bodyLayout)

    # Detail-Scrollarea (contains body)
    self.scrollarea = QScrollArea(widgetResizable=True)
    self.scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.scrollarea.setContentsMargins(0, 0, 0, 0)
    self.scrollarea.setWidget(self.body)

    # Vertical Splitter to resize contentPreview
    self.splitter = QSplitter(Qt.Orientation.Vertical, handleWidth=3)
    self.splitter.addWidget(self.contentPreviewWidget)
    self.splitter.setStretchFactor(0, 1)
    self.splitter.addWidget(self.scrollarea)
    self.splitter.setStretchFactor(1, 1)
    firstHeight = 200
    self.splitter.setSizes([firstHeight, self.splitter.size().height() - firstHeight])

    # Main Layout
    self.layout = QVBoxLayout()
    self.layout.setContentsMargins(0, 0, 0, 0)
    self.layout.addWidget(self.header)
    self.layout.addWidget(self.splitter, stretch=0)
    self.setLayout(self.layout)

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
    clearLayout(self.contentPreviewLayout)
    clearLayout(self.bodyLayout)
    self.contentPreviewWidget.hide()

    # Init the collapsible Items that contain all the details
    detailsItem = DetailsHierItem(self.comm, "Details", dataHierarchyNode)
    vendorItem = DetailsHierItem(self.comm, "Vendor Metadata", dataHierarchyNode)
    userItem = DetailsHierItem(self.comm, "User Metadata", dataHierarchyNode)
    elnItem = DetailsHierItem(self.comm, "ELN Details", dataHierarchyNode, startCollapsed=True)

    # Populate the Content/Image
    for key in self.data:
      if key == "name":
        continue
      if key == "image":
        image = ResizeImage(self.data['image'], self.contentPreviewLayout)
        self.contentPreviewWidget.show()
      elif key == "content":
        textEdit = QTextEdit()
        textEdit.setMarkdown(self.data['content'])
        textEdit.setReadOnly(True)
        self.contentPreviewLayout.addWidget(textEdit)
        self.contentPreviewWidget.show()
        size = min([int(textEdit.document().size().height()), self.splitter.size().height() // 2])
        self.splitter.setSizes([size, self.splitter.size().height() - size])
      elif key == "metaVendor":
        vendorItem.addContent("metaVendor", self.data["metaVendor"])
      elif key == "metaUser":
        userItem.addContent("metaUser", self.data["metaUser"])
      elif key in SORTED_DB_KEYS:
        elnItem.addContent(key, self.data[key])
      else:
        detailsItem.addContent(key, self.data[key])

    if detailsItem.content:
      self.bodyLayout.addWidget(detailsItem)
    if vendorItem.content:
      self.bodyLayout.addWidget(vendorItem)
    if userItem.content:
      self.bodyLayout.addWidget(userItem)
    if elnItem.content:
      self.bodyLayout.addWidget(elnItem)

    self.bodyLayout.addStretch(0)

  @Slot()
  def onEditButtonClicked(self) -> None:
    """
    What happens, when the edit Button in the Top-right is clicked
    TODO: The Edit Form is not working as Raphael expects it to. (It's buggy when I use it this way...)
    """
    print("Edit Button Clicked, FormDoc still buggy")
    # Open the edit Form
    self.comm.formDoc.emit(self.data)
