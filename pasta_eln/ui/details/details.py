""" This Widget is the right sidebar that shows the details of the currently selected item """
import re
from enum import Enum
from pathlib import Path
from typing import Any
from PySide6.QtCore import QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices, QShowEvent, Qt
from PySide6.QtWidgets import QHBoxLayout, QMenu, QMessageBox, QScrollArea, QSplitter, QTextEdit, QVBoxLayout, QWidget
from pasta_eln.backend_worker.worker import Task
from pasta_eln.fixed_strings_json import SORTED_DB_KEYS
from pasta_eln.misc_tools import clearLayout, makeStringWrappable
from pasta_eln.ui.details.details_hier_item import DetailsHierItem
from pasta_eln.ui.details.resize_image import ResizeImage
from pasta_eln.ui.details.context import DetailContext, DetailOrigin
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import SPACE, Button, ButtonStyle, Label, Widget, action as addAction


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
    self.context = DetailContext()
    self.data: dict[str, Any] = {'content': ''}
    self.contentText: QTextEdit | None = None

    ### HEADER WIDGETS
    self.titleLabel = Label('', 'h1')
    self.titleLabel.setWordWrap(True)
    self.editButton = Button('Edit', self, Command.EDIT, icon='ri.edit-2-fill', style=ButtonStyle.HIGHLIGHTED)
    self.openButton = Button('Open', self,               icon='ri.external-link-line', style=ButtonStyle.PRIMARY)
    self.openMenu = QMenu(self)
    self.openMenu.aboutToShow.connect(self.paintOpenMenu)
    self.openButton.setMenu(self.openMenu)
    self.actionsButton = Button('Actions', self, icon='ri.more-fill', style=ButtonStyle.PRIMARY)
    self.actionsMenu   = QMenu(self)
    self.actionsMenu.aboutToShow.connect(self.paintActionsMenu)
    self.actionsButton.setMenu(self.actionsMenu)

    # Header Layout
    self.headerL = QHBoxLayout()
    self.headerL.addWidget(self.titleLabel, stretch=1)
    self.headerL.addWidget(self.editButton)
    self.headerL.addWidget(self.openButton)
    self.headerL.addWidget(self.actionsButton)
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
    # Vertical Splitter to resize contentPreview
    self.splitter = QSplitter(Qt.Orientation.Vertical, handleWidth=3)
    self.splitter.addWidget(self.contentPreviewW)
    self.splitter.setStretchFactor(0, 1)
    self.splitter.addWidget(self.scrollarea)
    self.splitter.setStretchFactor(1, 1)
    self.splitter.setSizes([200, self.splitter.size().height() - 200])

    # Main Layout
    self.mainL = QVBoxLayout()
    self.mainL.setContentsMargins(SPACE.M, 0, 0, 0)
    self.mainL.addWidget(self.headerW)
    self.mainL.addWidget(self.splitter, stretch=0)
    self.setLayout(self.mainL)

    # Signals
    self.comm.changeDetails.connect(self.onDetailsChanged)
    self.comm.backendThread.worker.beSendDoc.connect(self.onGetData)

    # CODE
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
    title = makeStringWrappable(self.data['name'], nChars=15)
    # Show the filename indicator when every stored path differs from the item name
    paths = [branch['path'] for branch in self.data.get('branch', [])]
    if not paths or any(path is None for path in paths):
      self.titleLabel.setText(title)
      self.titleLabel.setToolTip('')
    else:
      filenames = [Path(path).name for path in paths]
      name = self.data['name'].casefold()
      differs = all(re.sub(r'^\d{3}_', '', filename).casefold() != name for filename in filenames)
      self.titleLabel.setText(f'{title}<sup><span style="font-size: 24pt;">ℹ</span></sup>' if differs else title)
      self.titleLabel.setToolTip('The filename on disk is:\n' + '\n'.join(filenames) if differs else '')

    # BODY
    # clear old items
    self.contentText = None
    clearLayout(self.contentPreviewL)
    clearLayout(self.bodyL)
    self.contentPreviewW.hide()
    # Init the collapsible Items that contain all the details
    detailsItem = DetailsHierItem(self.comm, 'Details', dataHierarchyNode)
    userItem    = DetailsHierItem(self.comm, 'User Metadata', dataHierarchyNode)
    vendorItem  = DetailsHierItem(self.comm, 'Vendor Metadata', dataHierarchyNode, startCollapsed=True)
    elnItem     = DetailsHierItem(self.comm, 'ELN Details', dataHierarchyNode, startCollapsed=True)
    # Populate the Content/Image
    for key in self.data:
      if key == 'name':
        continue
      if key == 'image':
        ResizeImage(self.data['image'], self.contentPreviewL)
        self.contentPreviewW.show()
      elif key == 'content':
        self.contentText = QTextEdit()
        self.contentText.setMarkdown(self.data['content'])
        self.contentText.setReadOnly(True)
        self.contentPreviewL.addWidget(self.contentText)
        self.contentPreviewW.show()
        size = min([int(self.contentText.document().size().height()), self.splitter.size().height() // 2])
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
    if userItem.content:
      self.bodyL.addWidget(userItem)
    if vendorItem.content:
      self.bodyL.addWidget(vendorItem)
    if elnItem.content:
      self.bodyL.addWidget(elnItem)
    self.bodyL.addStretch(0)

  def paintOpenMenu(self) -> None:
    """Build navigation and local-file actions for the selected item."""
    self.openMenu.clear()
    if not self.docID:
      return
    if self.context.origin is DetailOrigin.TABLE:
      addAction('Open in project', self, Command.OPEN_PROJECT, self.openMenu)
    elif self.context.origin is DetailOrigin.PROJECT and self.data['type'][0] in self.comm.docTypesTitles \
        and not self.data['type'][0].startswith('x'):
      addAction('Open in table', self, Command.OPEN_TABLE, self.openMenu)
    sourcePath = self.sourcePath()
    if sourcePath is not None:
      self.openMenu.addSeparator()
      if sourcePath.is_file():
        addAction('Open file with another application', self, Command.OPEN_EXTERNAL, self.openMenu)
      addAction('Open folder in file browser', self, Command.OPEN_FOLDER, self.openMenu)


  def paintActionsMenu(self) -> None:
    """Build item actions that are neither editing nor navigation."""
    self.actionsMenu.clear()
    if not self.docID:
      return
    extractionMenu = self.actionsMenu.addMenu('Extraction')
    branch = self.data.get('branch', [{}])
    path = branch[0].get('path') if branch else None
    documentTypes = self.data.get('type', [])
    extractorChoices: dict[str, str] = {}
    if isinstance(path, str) and path and documentTypes:
      extractors = self.comm.configuration['projectGroups'][self.comm.projectGroup].get('addOns', {}).get('extractors', {})
      extensionExtractors = extractors.get(Path(path).suffix.removeprefix('.').lower(), {})
      extractorChoices = {recipe: label for recipe, label in extensionExtractors.items()
                          if recipe.startswith(documentTypes[0])}
    for recipe, label in extractorChoices.items():
      addAction(label, self, [Command.RERUN_EXTRACTOR, recipe], extractionMenu)
    if self.sourcePath() is not None:
      addAction('Test extraction', self, Command.TEST_EXTRACTION, extractionMenu)
    if bool(extractorChoices) and 'image' in self.data and self.sourcePath() is not None:
      addAction('Save extracted image', self, Command.SAVE_EXTRACTED_IMAGE, extractionMenu)
    if not extractorChoices and self.sourcePath() is None:
      extractionMenu.setEnabled(False)
    self.actionsMenu.addSeparator()
    addAction('Hide item', self,     Command.HIDE_ITEM,    self.actionsMenu)
    addAction('Close details', self, Command.HIDE_DETAILS, self.actionsMenu)
    self.actionsMenu.addSeparator()
    addAction('Remove…', self,       Command.REMOVE,       self.actionsMenu)


  def execute(self, command: Command | list[Any]) -> None:
    """Handle commands emitted by the details controls."""
    commandType = command if isinstance(command, Command) else command[0]
    payload = [] if isinstance(command, Command) else command[1:]
    if commandType is Command.EDIT:
      self.onEditButtonClicked()
    elif commandType is Command.OPEN_PROJECT:
      branch = self.data.get('branch', [{}])
      stack = branch[0].get('stack', []) if branch else []
      if stack:
        self.comm.changeProject.emit(stack[0], self.docID)
    elif commandType is Command.OPEN_TABLE:
      self.comm.changeTable.emit(self.data['type'][0], '')
    elif commandType is Command.RERUN_EXTRACTOR:
      self.comm.uiRequestTask.emit(Task.EXTRACTOR_RERUN, {'docIDs': [self.docID], 'recipe': payload[0]})
    elif commandType is Command.TEST_EXTRACTION:
      sourcePath = self.sourcePath()
      if sourcePath is not None:
        self.comm.uiRequestTask.emit(Task.EXTRACTOR_TEST, {
            'fileName': str(sourcePath), 'style': 'html', 'recipe': '', 'saveFig': ''})
    elif commandType is Command.SAVE_EXTRACTED_IMAGE:
      sourcePath = self.sourcePath()
      if sourcePath is None:
        return
      image = self.data.get('image', '')
      imageType = image[11:14] if isinstance(image, str) and image.startswith('data:image/') and len(image) > 14 and image[14] == ';' \
        else (image[11:15] if isinstance(image, str) and image.startswith('data:image/') else 'svg')
      destination = sourcePath.parent / f'{sourcePath.stem}_PastaExport.{imageType.lower()}'
      self.comm.uiRequestTask.emit(Task.EXTRACTOR_TEST, {
        'fileName': str(sourcePath), 'style': '', 'recipe': '/'.join(self.data['type']), 'saveFig': str(destination),
      })
    elif commandType is Command.OPEN_FOLDER:
      sourcePath = self.sourcePath()
      if sourcePath is not None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(sourcePath if sourcePath.is_dir() else sourcePath.parent)))
    elif commandType is Command.OPEN_EXTERNAL:
      sourcePath = self.sourcePath()
      if sourcePath is not None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(sourcePath)))
    elif commandType is Command.HIDE_ITEM:
      self.comm.uiRequestTask.emit(Task.HIDE_SHOW, {'docID': self.docID})
      self.comm.changeDetails.emit(DetailContext())
    elif commandType is Command.REMOVE:
      message = QMessageBox(self)
      message.setWindowTitle('Remove item')
      message.setText(f'Remove “{self.data["name"]}”?')
      everywhereButton = message.addButton('Remove everywhere', QMessageBox.ButtonRole.DestructiveRole)
      currentButton = None
      if self.context.treeStack:
        currentButton = message.addButton('Remove from current location', QMessageBox.ButtonRole.DestructiveRole)
      message.addButton(QMessageBox.StandardButton.Cancel)
      message.exec()
      if message.clickedButton() in (everywhereButton, currentButton):
        stack = self.context.treeStack if message.clickedButton() is currentButton else ''
        self.comm.uiRequestTask.emit(Task.DELETE_DOC, {'docID': self.docID, 'stack': stack})
        self.comm.changeDetails.emit(DetailContext())
        if stack:
          self.comm.changeProject.emit(stack.split('/')[0], '')
        else:
          self.comm.changeTable.emit(self.data['type'][0], self.comm.projectID)
    elif commandType is Command.HIDE_DETAILS:
      self.comm.changeDetails.emit(DetailContext())                  # all widgets know that details are hidden


  @Slot(object)
  def onDetailsChanged(self, context: DetailContext) -> None:
    """
    What happens when the displayed item changes.
    Args:
      context (DetailContext): Document, origin, and optional tree location to display.
    """
    self.context = context
    if context.docID:
      self.docID = context.docID
      self.comm.uiRequestDoc.emit(self.docID)
    else:
      self.docID = ''
      self.hide()

  def showEvent(self, event: QShowEvent) -> None:
    """Notify the containing splitter when the details panel first becomes visible
    Args:
      event (QShowEvent): event
    """
    super().showEvent(event)
    self.becameVisible.emit()


  @Slot()
  def onEditButtonClicked(self) -> None:
    """
    What happens, when the edit Button in the Top-right is clicked
    """
    self.comm.formDoc.emit(self.data)


  def sourcePath(self) -> Path | None:
    """Return the local source-file path, excluding database-only and remote items."""
    branch = self.data.get('branch', [{}])
    path = branch[0].get('path') if branch else None
    if not isinstance(path, str) or not path or path.startswith('http'):
      return None
    return self.comm.basePath / path


class Command(Enum):
  """Commands handled by :class:`Details`."""
  EDIT                 = 1
  OPEN_PROJECT         = 2
  RERUN_EXTRACTOR      = 3
  TEST_EXTRACTION      = 4
  SAVE_EXTRACTED_IMAGE = 5
  OPEN_FOLDER          = 6
  HIDE_ITEM            = 7
  HIDE_DETAILS         = 8
  OPEN_TABLE           = 9
  OPEN_EXTERNAL        = 10
  REMOVE               = 11
