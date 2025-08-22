""" widget that shows the table of the items """
import itertools
import logging
import re
from enum import Enum
from pathlib import Path
from typing import Any
import pandas as pd
from PySide6.QtCore import QModelIndex, QSortFilterProxyModel, Qt, Slot
from PySide6.QtGui import QRegularExpressionValidator, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (QApplication, QComboBox, QFileDialog, QHeaderView, QLineEdit, QMenu, QMessageBox,
                               QPushButton, QTableView, QVBoxLayout, QWidget)
from ..backendWorker.worker import Task
from ..miscTools import callAddOn
from .gallery import ImageGallery
from .guiCommunicate import Communicate
from .guiStyle import Action, IconButton, Label, TextButton, space, widgetAndLayout, widgetAndLayoutGrid
from .tableHeader import TableHeader


class FilterItem:
    """Represents a single filter with its model and associated widgets"""

    def __init__(self, filter_id: int, header_options: list[str], parent_widget):
        self.id = filter_id
        self.model = QSortFilterProxyModel()
        self.model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.model.setFilterKeyColumn(0)

        # Create widgets
        self.select = QComboBox()
        self.select.addItems(header_options + ['rating'] if 'tag' in header_options else header_options)
        self.select.setMinimumWidth(max(len(i) for i in header_options) * 14)

        self.text = QLineEdit('')
        self.inverse = IconButton('ph.selection-inverse-fill', parent_widget,
                                  [Command.SET_FILTER, filter_id, 'invert'], None, checkable=True)
        self.delete = IconButton('fa5s.minus-square', parent_widget,
                                 [Command.DELETE_FILTER, filter_id], None)


class FilterManager:
    """Manages the chain of filters applied to a table model"""

    def __init__(self, base_model: QStandardItemModel):
        self.base_model = base_model
        self.filters: dict[int, FilterItem] = {}
        self.next_id = 1
        self._model_chain: list[QStandardItemModel | QSortFilterProxyModel] = [base_model]

    def add_filter(self, header_options: list[str], parent_widget) -> FilterItem:
        """Add a new filter to the chain"""
        filter_id = self.next_id
        self.next_id += 1

        filter_item = FilterItem(filter_id, header_options, parent_widget)
        self.filters[filter_id] = filter_item

        # Link to the current end of the chain
        filter_item.model.setSourceModel(self._model_chain[-1])
        self._model_chain.append(filter_item.model)

        return filter_item

    def remove_filter(self, filter_id: int) -> None:
        """Remove a filter and rebuild the chain"""
        if filter_id not in self.filters:
            return

        # Remove the filter
        del self.filters[filter_id]

        # Rebuild the entire model chain
        self._rebuild_chain()

    def _rebuild_chain(self) -> None:
        """Rebuild the model chain after filter removal"""
        self._model_chain = [self.base_model]

        # Re-link all remaining filters in order of their IDs
        for filter_id in sorted(self.filters.keys()):
            filter_item = self.filters[filter_id]
            filter_item.model.setSourceModel(self._model_chain[-1])
            self._model_chain.append(filter_item.model)

    def get_final_model(self) -> QStandardItemModel | QSortFilterProxyModel:
        """Get the final model in the chain (for table display)"""
        return self._model_chain[-1]

    def get_filter(self, filter_id: int) -> FilterItem | None:
        """Get a specific filter by ID"""
        return self.filters.get(filter_id)

    def clear_all(self) -> None:
        """Remove all filters"""
        self.filters.clear()
        self._model_chain = [self.base_model]

    def set_base_model(self, new_base_model: QStandardItemModel) -> None:
        """Update the base model and rebuild chain"""
        self.base_model = new_base_model
        self._model_chain[0] = new_base_model
        self._rebuild_chain()


#Scan button to more button
class Table(QWidget):
  """ widget that shows the table of the items """
  def __init__(self, comm:Communicate):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
    """
    super().__init__()
    self.comm = comm
    self.comm.backendThread.worker.beSendTable.connect(self.onGetData)
    self.comm.changeTable.connect(self.changeTable)
    self.comm.stopSequentialEdit.connect(self.stopSequentialEditFunction)
    self.stopSequentialEdit = False
    self.data         :pd.DataFrame = pd.DataFrame()
    self.base_model   :QStandardItemModel = QStandardItemModel()
    self.filter_manager:FilterManager = FilterManager(self.base_model)
    self.filterHeader:list[str] = []
    self.lastClickedRow = -1
    self.flagGallery = False
    self.docType = 'x0'
    self.showAll= self.comm.configuration['GUI']['showHidden']=='Yes'

    ### GUI elements
    mainL = QVBoxLayout()
    mainL.setSpacing(0)
    mainL.setContentsMargins(space['s'], space['s'], space['s'], space['s'])
    # header
    self.headerW, headerL = widgetAndLayout('H', mainL, 'm')
    self.headerW.hide()
    self.headline = Label('','h1', headerL)
    self.showState= Label('', 'h3', headerL)
    self.subDocTypeL= Label('      subType:', 'h3', headerL)
    self.subDocTypeL.hide()
    self.subDocType=QComboBox(self)
    self.subDocType.setMinimumWidth(200)
    self.subDocType.currentTextChanged.connect(lambda dt: self.changeTable(dt, self.comm.projectID))
    self.subDocType.hide()
    headerL.addWidget(self.subDocType)
    headerL.addStretch(1)
    self.addBtn = TextButton('Add',  self, [Command.ADD_ITEM],   headerL)

    self.selectionBtn = TextButton('Selection', self, [], headerL)
    selectionMenu = QMenu(self)
    Action('Toggle selection',self, [Command.TOGGLE_SELECTION], selectionMenu)
    selectionMenu.addSeparator()
    Action('Group Edit',      self, [Command.GROUP_EDIT],       selectionMenu)
    Action('Sequential edit', self, [Command.SEQUENTIAL_EDIT],  selectionMenu)
    self.toggleHidden  = Action('Invert hidden status of selected', self, [Command.TOGGLE_HIDE],    selectionMenu)
    Action('Rerun extractors',self, [Command.RERUN_EXTRACTORS], selectionMenu)
    Action('Delete',          self, [Command.DELETE],           selectionMenu)
    self.selectionBtn.setMenu(selectionMenu)

    self.visibilityBtn = TextButton('Visibility', self, [], headerL)
    visibilityMenu = QMenu(self)
    Action(                    'Add Filter',                        self, [Command.ADD_FILTER],     visibilityMenu)
    self.showHidden    = Action('Show/hide hidden ___',             self, [Command.SHOW_ALL],       visibilityMenu)
    self.toggleGallery = Action('Toggle gallery view',              self, [Command.TOGGLE_GALLERY], visibilityMenu)
    self.toggleGallery.setVisible(False)
    self.visibilityBtn.setMenu(visibilityMenu)

    self.btnMore = TextButton('More', self, [], headerL)
    self.moreMenu = QMenu(self)
    Action('Export to csv',            self, [Command.EXPORT],   self.moreMenu)
    self.moreMenu.addSeparator()
    projectGroup = self.comm.configuration['projectGroups'][self.comm.projectGroup]
    if projectAddOns := projectGroup.get('addOns',{}).get('table',''):
      for label, description in projectAddOns.items():
        Action(description, self, [Command.ADD_ON, label], self.moreMenu)
      self.moreMenu.addSeparator()
    self.actionChangeColums = Action('Change list columns',  self, [Command.CHANGE_COLUMNS], self.moreMenu)#add this action at end
    self.btnMore.setMenu(self.moreMenu)

    # filter
    _, self.filterL = widgetAndLayoutGrid(mainL, top='s', bottom='s')
    # table
    self.table = QTableView(self)
    self.table.setStyleSheet('QTableView::indicator {width: 16px; height: 16px;}')
    self.table.verticalHeader().hide()
    self.table.clicked.connect(self.cellClicked)
    self.table.doubleClicked.connect(self.cell2Clicked)
    self.table.setSortingEnabled(True)
    self.table.setAlternatingRowColors(True)
    header = self.table.horizontalHeader()
    header.setStyleSheet('QHeaderView::section {padding: 0px 5px; margin: 0px;}')
    header.setSectionsMovable(True)
    header.setSortIndicatorShown(True)
    header.setMaximumSectionSize(self.comm.configuration['GUI']['maxTableColumnWidth'])
    header.setStretchLastSection(True)
    mainL.addWidget(self.table)
    self.gallery = ImageGallery(self.comm)
    self.gallery.setVisible(False)
    mainL.addWidget(self.gallery)
    self.setLayout(mainL)
    self.setStyleSheet(f"QLineEdit, QComboBox {{ {self.comm.palette.get('secondaryText', 'color')} }}")
    self.comm.uiRequestTable.emit(self.docType, self.comm.projectID, self.showAll)


  @Slot(str, str)
  def changeTable(self, docType:str, projID:str) -> None:
    """ What happens when user clicks to change doc-type
    Args:
      docType (str): document type
      projID (str): project id
    """
    if docType:
      self.docType = docType
    if projID:
      self.comm.projectID  = projID
    if self.docType == 'x0':
      self.comm.projectID = ''
    logging.debug('request table for %s, %s %s', self.docType, self.comm.projectID, self.showAll)
    self.comm.uiRequestTable.emit(self.docType, self.comm.projectID, self.showAll)


  @Slot(pd.DataFrame, str)
  def onGetData(self, data:pd.DataFrame, docType:str) -> None:
    """
    Callback function to handle the received data

    Args:
      data (pd.DataFrame): DataFrame containing table
      docType (str): document type
    """
    logging.debug('got table data %s', docType)
    if docType == self.docType:
      self.data = data
      self.paint()


  @Slot()
  def paint(self) -> None:
    """
    What happens when the table changes its raw information
    """
    if self.isHidden():
      return

    # Clear existing filters and GUI elements
    self.filter_manager.clear_all()
    for i in reversed(range(self.filterL.count())):
      item_1 = self.filterL.itemAt(i)
      if item_1 is not None:
        item_1.widget().setParent(None)
    allDocTypes:list[str] = []
    if '/' not in self.docType:
      # get list of all subDocTypes
      allDocTypes = [i for i in self.comm.docTypesTitles if i.startswith(self.docType)]
      if len(allDocTypes)==1:
        self.subDocTypeL.hide()
        self.subDocType.hide()
      elif len(allDocTypes)>1:
        self.subDocTypeL.show()
        self.subDocType.show()
        alreadyInside = {self.subDocType.itemText(i) for i in range(self.subDocType.count())}
        if alreadyInside != set(allDocTypes):
          self.subDocType.clear()
          self.subDocType.addItems(allDocTypes)
    if 'measurement' in self.docType:
      self.toggleGallery.setVisible(True)
    else:
      self.toggleGallery.setVisible(False)
      self.flagGallery = False
    # start tables: use data
    if self.docType=='_tags_':
      self.addBtn.hide()
      self.filterHeader = ['tag','name','type']
      self.headline.setText('TAGS')
      self.actionChangeColums.setVisible(False)
    else:
      self.addBtn.show()
      if self.docType.startswith('x0'):
        self.selectionBtn.hide()
        self.toggleHidden.setVisible(False)
      else:
        self.selectionBtn.show()
        self.toggleHidden.setVisible(True)
      self.showState.setText('(show all rows)' if self.showAll else '(hide hidden rows)')
      docLabel = 'Unidentified'
      if self.docType=='-':
        self.actionChangeColums.setVisible(False)
      else:
        self.actionChangeColums.setVisible(True)
        docLabel = self.comm.docTypesTitles[self.docType]['title']
      if self.comm.projectID:
        self.headline.setText(docLabel)
        self.showHidden.setText(f'Show/hide hidden {docLabel.lower()}')
      else:
        self.headline.setText(f'All {docLabel.lower()}')
        self.showHidden.setText(f'Show/hide all hidden {docLabel.lower()}')
      columnNames = [i.replace('metaUser.','u.') for i in self.data.columns]
      self.filterHeader = list(columnNames)[:-2]
    self.headerW.show()
    nRows, nCols = self.data.shape
    model = QStandardItemModel(nRows, nCols-2)
    model.setHorizontalHeaderLabels(self.filterHeader)
    for i, j in itertools.product(range(nRows), range(nCols-2)):
      value = self.data.iloc[i,j]
      if self.docType=='_tags_':                                                                   # tags list
        if j==0 and re.match(r'_\d', value):                                                            # star
          item = QStandardItem('\u2605'*int(value[1]))
        elif j==0:
          item = QStandardItem(value)
        else:
          item = QStandardItem(value)
      elif value in ('None','','nan'):                                                           # None, False
        item = QStandardItem('-')
      elif value=='True':                                                                               # True
        item = QStandardItem('Y')
      elif isinstance(value, str) and re.match(r'^[a-z\-]-[a-z0-9]{32}$',value):                        # Link
        item = QStandardItem('oo')
      else:
        if self.filterHeader[j]=='tags':
          tags = [i.strip() for i in value.split(',')]
          if elementStar:=list(filter(re.compile(r'^_\d$').match, tags)):
            tags.remove(elementStar[0])
            tags = ['\u2605'*int(elementStar[0][1])]+tags
          text = ' '.join(tags)
        else:
          text = value
        item = QStandardItem(text)
      if (j==0 and self.docType!='_tags_') or (self.docType=='_tags_' and j==1):
        if 'F' in self.data['show'][i]:
          item.setText(f'{item.text()}  \U0001F441')
        item.setAccessibleText(self.data['id'][i])
        if self.docType[0] != 'x':
          item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
          item.setCheckState(Qt.CheckState.Unchecked)
      else:
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
      model.setItem(i, j, item)

    # Update the filter manager with the new base model
    self.base_model = model
    self.filter_manager.set_base_model(model)

    if self.flagGallery:
      self.gallery.updateGrid(model)
      self.gallery.setVisible(True)
      self.table.setVisible(False)
    else:
      self.table.setModel(self.filter_manager.get_final_model())
      self.table.horizontalHeader().resizeSections(QHeaderView.ResizeMode.ResizeToContents)
      self.table.horizontalHeader().setStretchLastSection(True)
      self.table.sortByColumn(0, Qt.SortOrder.AscendingOrder)
      self.table.show()
      self.gallery.setVisible(False)
      self.table.setVisible(True)
    return


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    if command[0] is Command.ADD_ITEM:
      self.comm.formDoc.emit({'type':[self.docType], '_projectID':self.comm.projectID})
      self.comm.changeTable.emit(self.docType, self.comm.projectID)
      if self.docType=='x0':
        self.comm.changeSidebar.emit('redraw')

    elif command[0] is Command.GROUP_EDIT:
      docIDs = []
      final_model = self.filter_manager.get_final_model()
      for row in range(final_model.rowCount()):
        item, docID = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          docIDs.append(docID)
      if docIDs:
        self.comm.formDoc.emit({'type':[self.docType], '_ids':docIDs})
        self.changeTable(self.docType, self.comm.projectID)

    elif command[0] is Command.SEQUENTIAL_EDIT:
      self.stopSequentialEdit = False
      final_model = self.filter_manager.get_final_model()
      for row in range(final_model.rowCount()):
        item, docID = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          self.comm.formDoc.emit({'id':docID})
        if self.stopSequentialEdit:
          break
      self.comm.changeTable.emit(self.docType, self.comm.projectID)

    elif command[0] is Command.DELETE:
      ret = None
      final_model = self.filter_manager.get_final_model()
      for row in range(final_model.rowCount()):
        item, docID = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          if ret is None:
            ret = QMessageBox.critical(self, 'Warning', 'Are you sure you want to delete the data?',
                QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
          if ret==QMessageBox.StandardButton.Yes:
            self.comm.uiRequestTask.emit(Task.DELETE_DOC, {'docID':docID})
      self.comm.changeTable.emit(self.docType, self.comm.projectID)

    elif command[0] is Command.CHANGE_COLUMNS:
      dialog = TableHeader(self.comm, self.docType)
      dialog.exec()
      self.comm.uiRequestTable.emit(self.docType, self.comm.projectID, self.showAll)

    elif command[0] is Command.EXPORT:
      fileName = QFileDialog.getSaveFileName(self,'Export to ..',str(Path.home()),'*.csv')[0]
      if not fileName.endswith('.csv'):
        fileName += '.csv'
      final_model = self.filter_manager.get_final_model()
      with open(fileName,'w', encoding='utf-8') as fOut:
        header = [f'"{i}"' for i in self.filterHeader]
        fOut.write(','.join(header)+'\n')
        for row in range(final_model.rowCount()):
          rowContent = []
          for col in range(final_model.columnCount()):
            value = final_model.index( row, col, QModelIndex()).data(Qt.ItemDataRole.DisplayRole)
            rowContent.append(f'"{value}"')
          fOut.write(','.join(rowContent)+'\n')

    elif command[0] is Command.ADD_ON:
      # check if one is selected, if yes, only export selected; otherwise use All
      final_model = self.filter_manager.get_final_model()
      useAll = True
      for row in range(final_model.rowCount()):
        item, _ = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          useAll = False
          break
      data   = []
      for row in range(final_model.rowCount()):
        item, docID = self.itemFromRow(row)
        if useAll or  item.checkState() == Qt.CheckState.Checked:
          dataRow = [docID]
          for col in range(final_model.columnCount()):
            value = final_model.index(row, col).data(Qt.ItemDataRole.DisplayRole)
            dataRow.append(value)
          data.append(dataRow)
      df = pd.DataFrame(data, columns=['docID']+self.filterHeader)
      callAddOn(command[1], self.comm, df, self)

    elif command[0] is Command.TOGGLE_HIDE:
      changeFlag = False
      final_model = self.filter_manager.get_final_model()
      for row in range(final_model.rowCount()):
        item, docID = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          self.comm.uiRequestTask.emit(Task.HIDE_SHOW, {'docID':docID})
          changeFlag = True
      if changeFlag:
        self.comm.uiRequestTable.emit(self.docType, self.comm.projectID, self.showAll)
      if self.docType=='x0':
        self.comm.changeSidebar.emit('redraw')
      self.paint()

    elif command[0] is Command.TOGGLE_SELECTION:
      final_model = self.filter_manager.get_final_model()
      for row in range(final_model.rowCount()):
        item,_ = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          item.setCheckState(Qt.CheckState.Unchecked)
        else:
          item.setCheckState(Qt.CheckState.Checked)

    elif command[0] is Command.SHOW_ALL:
      self.showAll = not self.showAll
      self.comm.uiRequestTable.emit(self.docType, self.comm.projectID, self.showAll)

    elif command[0] is Command.RERUN_EXTRACTORS:
      docIDs = []
      final_model = self.filter_manager.get_final_model()
      for row in range(final_model.rowCount()):
        item, docID = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          docIDs.append(docID)
      self.comm.uiRequestTask.emit(Task.EXTRACTOR_RERUN, {'docIDs':docIDs,'recipe':''})
      self.comm.uiRequestTable.emit(self.docType, self.comm.projectID, self.showAll)

    elif command[0] is Command.TOGGLE_GALLERY:
      self.flagGallery = not self.flagGallery
      self.paint()

    elif command[0] is Command.ADD_FILTER:
      # Create new filter using FilterManager
      filter_item = self.filter_manager.add_filter(self.filterHeader, self)
      
      # Create GUI row
      _, rowL = widgetAndLayout('H', self.filterL, 'm', 'xl', '0', 'xl')
      rowL.addWidget(filter_item.select)
      rowL.addWidget(filter_item.text)
      rowL.addWidget(filter_item.inverse)
      rowL.addWidget(filter_item.delete)
      
      # Connect signals
      filter_item.select.currentIndexChanged.connect(lambda idx: self.filterChoice(idx, filter_item.id))
      filter_item.text.textChanged.connect(lambda text: self.filterTextChanged(text, filter_item.id))
      
      # Update table model
      self.table.setModel(self.filter_manager.get_final_model())

    elif command[0] is Command.DELETE_FILTER:
      filter_id = command[1]
      
      # Find and remove GUI elements for this filter
      for i in range(self.filterL.count()):
        item = self.filterL.itemAt(i)
        if item and item.widget():
          widget = item.widget()
          layout = widget.layout()
          if layout and layout.count() >= 4:
            # Check if this is the right filter by looking at delete button's command
            delete_btn = layout.itemAt(3).widget()
            if hasattr(delete_btn, 'command') and delete_btn.command[1] == filter_id:
              widget.setParent(None)
              break
      
      # Remove filter from manager
      self.filter_manager.remove_filter(filter_id)
      
      # Update table model
      self.table.setModel(self.filter_manager.get_final_model())

    elif command[0] is Command.SET_FILTER:
      filter_id = command[1]
      if len(command) > 2 and command[2] == 'invert':
        filter_item = self.filter_manager.get_filter(filter_id)
        if filter_item:
          self.filterTextChanged(filter_item.text.text(), filter_id)

    else:
      logging.error('Menu unknown: %s',command, exc_info=True)
    self.setStyleSheet(f"QLineEdit, QComboBox {{ {self.comm.palette.get('secondaryText', 'color')} }}")
    return


  def cellClicked(self, index: QModelIndex) -> None:
    """
    What happens when user clicks cell in table of tags, projects, samples, ..
    -> show details

    Args:
      index (QModelIndex): cell clicked
    """
    row = index.row()
    _, docID = self.itemFromRow(row)

    # Check if shift is held and lastClickedRow is set
    modifiers = QApplication.keyboardModifiers()
    if modifiers == Qt.ShiftModifier and self.lastClickedRow > -1:                # type: ignore[attr-defined]
      start = min(self.lastClickedRow, row)
      end = max(self.lastClickedRow, row)
      target_state = Qt.CheckState.Checked if self.itemFromRow(row)[0].checkState() == Qt.CheckState.Checked \
                      else Qt.CheckState.Unchecked
      for r in range(start, end + 1):
        item, _ = self.itemFromRow(r)
        item.setCheckState(target_state)
    else:                                             # No need to toggle only the clicked row, just record it
      self.lastClickedRow = row
    # Change view
    if docID[0] == 'x':                                                      # only show items for non-folders
      if self.docType == 'x0':
        self.comm.changeProject.emit(docID, '')
        self.comm.changeSidebar.emit(docID)
      else:
        self.comm.changeProject.emit(self.comm.projectID, docID)
        self.comm.changeSidebar.emit(self.comm.projectID)
    else:
      self.comm.changeDetails.emit(docID)
    return


  def cell2Clicked(self, index: QModelIndex) -> None:
    """
    What happens when user double clicks cell in table of projects

    Args:
      index (QModelIndex): cell clicked
    """
    row = index.row()
    _, docID = self.itemFromRow(row)
    if self.docType=='x0':
      self.comm.changeProject.emit(docID, '')
      self.comm.changeSidebar.emit(docID)
    else:
      self.comm.formDoc.emit({'id': docID})
      self.comm.changeTable.emit('','')
      self.comm.changeDetails.emit('redraw')
    return


  @Slot()
  def stopSequentialEditFunction(self) -> None:
    """ Stop the sequential edit of a number of items """
    self.stopSequentialEdit=True
    return


  def itemFromRow(self, row:int) -> tuple[QStandardItem, str]:
    """
    get item from row by iterating through the proxyModels

    Args:
      row (int): row number

    Returns:
      QItem, str: the item and docID
    """
    final_model = self.filter_manager.get_final_model()
    index = final_model.index(row, 0)
    
    # Map through all proxy models back to base model
    current_model = final_model
    while hasattr(current_model, 'mapToSource') and current_model != self.base_model:
      index = current_model.mapToSource(index)
      current_model = current_model.sourceModel()
    
    item = self.base_model.itemFromIndex(index)
    return item, item.accessibleText()


  def filterChoice(self, item:int, filter_id:int) -> None:
    """
    Change the column which is used for filtering

    Args:
       item (int): column number to filter by
       filter_id (int): ID of the filter being modified
    """
    filter_item = self.filter_manager.get_filter(filter_id)
    if not filter_item:
      return
      
    rating = False
    if item == len(self.filterHeader):  # ratings
      item = self.filterHeader.index('tag')
      rating = True
      
    filter_item.model.setFilterKeyColumn(item)
    filter_item.text.setText('')
    if rating:
      filter_item.text.setValidator(QRegularExpressionValidator(r'\*+'))
    else:
      filter_item.text.setValidator(None)
    return


  def filterTextChanged(self, text:str, filter_id:int) -> None:
    """ text in line-edit in the filter is changed: update regex

    Args:
      text (str): filter text
      filter_id (int): ID of the filter being modified
    """
    filter_item = self.filter_manager.get_filter(filter_id)
    if not filter_item:
      return
      
    regexStr = text
    if '*' in regexStr:
      regexStr = regexStr.replace('*','\u2605')
      if filter_item.inverse.isChecked():
        regexStr = f'^((?!{regexStr}).)*$'
      else:
        regexStr = f'^{regexStr}$'
    elif filter_item.inverse.isChecked():
      regexStr = f'^((?!{regexStr}).)*$'
    filter_item.model.setFilterRegularExpression(regexStr)
    return



class Command(Enum):
  """ Commands used in this file """
  ADD_FILTER       = 1
  ADD_ITEM         = 2
  TOGGLE_SELECTION = 3
  GROUP_EDIT       = 4
  SEQUENTIAL_EDIT  = 5
  TOGGLE_HIDE      = 6
  RERUN_EXTRACTORS = 7
  DELETE           = 8
  SHOW_ALL         = 9
  EXPORT           = 10
  CHANGE_COLUMNS   = 11
  DELETE_FILTER    = 12
  SET_FILTER       = 13
  TOGGLE_GALLERY   = 14
  ADD_ON           = 15
