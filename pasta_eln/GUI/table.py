""" widget that shows the table of the items """
import itertools
import logging
import re
from enum import Enum
from pathlib import Path
from typing import Any
import pandas as pd
from PySide6.QtCore import QModelIndex, QSortFilterProxyModel, Qt, Slot  # pylint: disable=no-name-in-module
from PySide6.QtGui import (QRegularExpressionValidator, QStandardItem,  # pylint: disable=no-name-in-module
                           QStandardItemModel)
from PySide6.QtWidgets import (QApplication, QComboBox, QFileDialog, QHeaderView,  # pylint: disable=no-name-in-module
                               QLineEdit, QMenu, QMessageBox, QPushButton, QTableView, QVBoxLayout, QWidget)
from ..guiCommunicate import Communicate
from ..guiStyle import Action, IconButton, Label, TextButton, space, widgetAndLayout, widgetAndLayoutGrid
from ..miscTools import callAddOn, dfConvertColumns
from .gallery import ImageGallery
from .tableHeader import TableHeader


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
    comm.changeTable.connect(self.change)
    comm.stopSequentialEdit.connect(self.stopSequentialEditFunction)
    self.stopSequentialEdit = False
    self.data         :pd.DataFrame = pd.DataFrame()
    self.models       :list[QSortFilterProxyModel] = []
    self.filterSelect :list[QComboBox]             = []
    self.filterText   :list[QLineEdit]             = []
    self.filterInverse:list[QPushButton]           = []
    self.filterDelete :list[QPushButton]           = []
    self.docType = ''
    self.projID = ''
    self.filterHeader:list[str] = []
    self.showAll= True
    self.lastClickedRow = -1
    self.flagGallery = False

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
    self.subDocType.setStyleSheet(self.comm.palette.get('secondaryText','color'))
    self.subDocType.currentTextChanged.connect(lambda dt: self.change(dt, self.projID))
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
    Action('Rerun extractors',self, [Command.RERUN_EXTRACTORS], selectionMenu)
    Action('Delete',          self, [Command.DELETE],           selectionMenu)
    self.selectionBtn.setMenu(selectionMenu)

    self.visibilityBtn = TextButton('Visibility', self, [], headerL)
    visibilityMenu = QMenu(self)
    Action(                    'Add Filter',                        self, [Command.ADD_FILTER],     visibilityMenu)
    self.showHidden    = Action('Show/hide hidden ___',             self, [Command.SHOW_ALL],       visibilityMenu)
    self.toggleHidden  = Action('Invert hidden status of selected', self, [Command.TOGGLE_HIDE],    visibilityMenu)
    self.toggleGallery = Action('Toggle gallery view',              self, [Command.TOGGLE_GALLERY], visibilityMenu)
    self.toggleGallery.setVisible(False)
    self.visibilityBtn.setMenu(visibilityMenu)

    more = TextButton('More', self, [], headerL)
    self.moreMenu = QMenu(self)
    Action('Export to csv',            self, [Command.EXPORT],   self.moreMenu)
    self.moreMenu.addSeparator()
    projectGroup = self.comm.backend.configuration['projectGroups'][self.comm.backend.configurationProjectGroup]
    if projectAddOns := projectGroup.get('addOns',{}).get('table',''):
      for label, description in projectAddOns.items():
        Action(description, self, [Command.ADD_ON, label], self.moreMenu)
      self.moreMenu.addSeparator()
    self.actionChangeColums = Action('Change columns',  self, [Command.CHANGE_COLUMNS], self.moreMenu)  #add this action at end
    more.setMenu(self.moreMenu)

    # filter
    _, self.filterL = widgetAndLayoutGrid(mainL, top='s', bottom='s')
    # table
    self.table = QTableView(self)
    self.table.setStyleSheet('QTableView::indicator {width: 24px; height: 24px;}')
    self.table.verticalHeader().hide()
    self.table.clicked.connect(self.cellClicked)
    self.table.doubleClicked.connect(self.cell2Clicked)
    self.table.setSortingEnabled(True)
    self.table.setAlternatingRowColors(True)
    header = self.table.horizontalHeader()
    header.setStyleSheet("QHeaderView::section {padding: 0px 5px; margin: 0px;}")
    header.setSectionsMovable(True)
    header.setSortIndicatorShown(True)
    header.setMaximumSectionSize(self.comm.backend.configuration['GUI']['maxTableColumnWidth'])
    header.setStretchLastSection(True)
    mainL.addWidget(self.table)
    self.gallery = ImageGallery(self.comm)
    self.gallery.setVisible(False)
    mainL.addWidget(self.gallery)
    self.setLayout(mainL)


  @Slot(str, str)                                       # type: ignore[arg-type]
  def change(self, docType:str, projID:str) -> None:
    """
    What happens when the table changes its raw information

    Args:
      docType (str): document type; leave empty for redraw
      projID (str): id of project
    """
    if docType!=self.docType or projID!=self.projID:
      logging.debug('table:changeTable |%s|%s|',docType, projID)
    self.models = []
    self.filterSelect = []
    self.filterText   = []
    self.filterInverse= []
    self.filterDelete = []
    #if not docType:  #only remove old filters, when docType changes
    #   make sure internal updates are accounted for: i.e. comment
    for i in reversed(range(self.filterL.count())):
      item_1 = self.filterL.itemAt(i)
      if item_1 is not None:
        item_1.widget().setParent(None)
    allDocTypes:list[str] = []
    if (docType!=self.docType or projID!=self.projID) and '/' not in docType:
      # get list of all subDocTypes
      allDocTypes = self.comm.backend.db.dataHierarchy('', '')
      allDocTypes = [i for i in allDocTypes if i.startswith(docType)]
      if len(allDocTypes)==1:
        self.subDocTypeL.hide()
        self.subDocType.hide()
      elif len(allDocTypes)>1 and docType:
        self.subDocTypeL.show()
        self.subDocType.show()
        alreadyInside = {self.subDocType.itemText(i) for i in range(self.subDocType.count())}
        if alreadyInside != set(allDocTypes):
          self.subDocType.clear()
          self.subDocType.addItems(allDocTypes)
    if docType!='':
      self.docType = docType
      self.projID  = projID
    if 'measurement' in self.docType:
      self.toggleGallery.setVisible(True)
    else:
      self.toggleGallery.setVisible(False)
      self.flagGallery = False
    # start tables: collect data
    if self.docType=='_tags_':
      self.addBtn.hide()
      if self.showAll:
        self.data = self.comm.backend.db.getView('viewIdentify/viewTagsAll')
      else:
        self.data = self.comm.backend.db.getView('viewIdentify/viewTags')
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
      path = (f'viewDocType/{self.docType}All' if self.showAll else f'viewDocType/{self.docType}')
      if self.projID=='':
        self.data = self.comm.backend.db.getView(path)
      else:
        self.data = self.comm.backend.db.getView(path, startKey=self.projID)
      self.showState.setText('(show all rows)' if self.showAll else '(hide hidden rows)')
      docLabel = 'Unidentified'
      if self.docType=='-':
        self.actionChangeColums.setVisible(False)
      else:
        self.actionChangeColums.setVisible(True)
        docLabel = self.comm.backend.db.dataHierarchy(self.docType,'title')[0]
      if self.projID:
        self.headline.setText(docLabel)
        self.showHidden.setText(f'Show/hide hidden {docLabel.lower()}')
      else:
        self.comm.changeSidebar.emit('')  #close the project in sidebar
        self.headline.setText(f'All {docLabel.lower()}')
        self.showHidden.setText(f'Show/hide all hidden {docLabel.lower()}')
      self.filterHeader = list(self.data.columns)[:-1]
    self.headerW.show()
    nRows, nCols = self.data.shape
    model = QStandardItemModel(nRows, nCols-1)
    model.setHorizontalHeaderLabels(self.filterHeader)
    for i, j in itertools.product(range(nRows), range(nCols-1)):
      value = self.data.iloc[i,j]
      if self.docType=='_tags_':  #tags list
        if j==0:
          if value=='_curated':          # curated
            item = QStandardItem('_curated_')
          elif re.match(r'_\d', value):  # star
            item = QStandardItem('\u2605'*int(value[1]))
          else:
            item = QStandardItem(value)
        else:
          item = QStandardItem(value)
      elif value in ('None','','nan'):  #None, False
        item = QStandardItem('-') # if you want to add nice glyphs, see also below \u00D7')
        # item.setFont(QFont("Helvetica [Cronyx]", 16))
      elif value=='True': #True
        item = QStandardItem('Y') # \u2713')
        # item.setFont(QFont("Helvetica [Cronyx]", 16))
      elif isinstance(value, str) and re.match(r'^[a-z\-]-[a-z0-9]{32}$',value):      #Link
        item = QStandardItem('oo') # \u260D')
        # item.setFont(QFont("Helvetica [Cronyx]", 16))
      else:
        if self.filterHeader[j]=='tags':
          tags = [i.strip() for i in value.split(',')]
          if '_curated' in tags:
            tags[tags.index('_curated')] = '_curated_'
          elementStar = list(filter(re.compile(r'^_\d$').match, tags))
          if elementStar:
            tags.remove(elementStar[0])
            tags = ['\u2605'*int(elementStar[0][1])]+tags
          text = ' '.join(tags)
        else:
          text = value
        item = QStandardItem(text)
      if j == 0:
        doc = self.comm.backend.db.getDoc(self.data['id'][i])
        if [b for b in doc['branch'] if False in b['show']]:
          item.setText(f'{item.text()}  \U0001F441')
        item.setAccessibleText(doc['id'])
        if self.docType != 'x0':
          item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
          item.setCheckState(Qt.CheckState.Unchecked)
      else:
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
      model.setItem(i, j, item)
    self.models.append(model)                                                                                # type: ignore[arg-type]
    if self.flagGallery:
      self.gallery.updateGrid(model)
      self.gallery.setVisible(True)
      self.table.setVisible(False)
    else:
      self.table.setModel(self.models[-1])
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
      self.comm.formDoc.emit({'type':[self.docType], '_projectID':self.projID})
      self.comm.changeTable.emit(self.docType, self.projID)
      if self.docType=='x0':
        self.comm.changeSidebar.emit('redraw')
    elif command[0] is Command.GROUP_EDIT:
      intersection = None
      docIDs = []
      for row in range(self.models[-1].rowCount()):
        item, docID = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          docIDs.append(docID)
          thisKeys = set(self.comm.backend.db.getDoc(docID))
          if intersection is None:
            intersection = thisKeys
          else:
            intersection = intersection.intersection(thisKeys)
      #remove keys that should not be group edited and build dict
      if intersection is not None:
        intersection = intersection.difference({'branch', 'user', 'client', 'metaVendor', 'shasum', \
            'id', 'metaUser', 'rev', 'name', 'dateCreated', 'dateModified', 'image', 'links', 'gui'})
        intersectionDict:dict[str,Any] = {i:'' for i in intersection}  | \
                                         {k:v  for k,v in self.comm.backend.db.getDoc(docID).items()
                                          if isinstance(v,dict) and k not in ('metaUser','metaVendor')}
        intersectionDict['tags'] = []
        intersectionDict['type'] = [self.docType]
        intersectionDict['_ids'] = docIDs
        self.comm.formDoc.emit(intersectionDict)
        self.comm.changeDetails.emit('redraw')
        self.comm.changeTable.emit(self.docType, self.projID)
    elif command[0] is Command.SEQUENTIAL_EDIT:
      self.stopSequentialEdit = False
      for row in range(self.models[-1].rowCount()):
        item, docID = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          self.comm.formDoc.emit(self.comm.backend.db.getDoc(docID))
        if self.stopSequentialEdit:
          break
      self.comm.changeTable.emit(self.docType, self.projID)
    elif command[0] is Command.DELETE:
      ret = None
      for row in range(self.models[-1].rowCount()):
        item, docID = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          if ret is None:
            ret = QMessageBox.critical(self, 'Warning', 'Are you sure you want to delete the data?',
                QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
          if ret==QMessageBox.StandardButton.Yes:
            doc = self.comm.backend.db.getDoc(docID)
            for branch in doc['branch']:
              if branch['path'] is not None:
                oldPath = self.comm.backend.basePath/branch['path']
                if oldPath.exists():
                  newPath = oldPath.parent / f'trash_{oldPath.name}'
                  oldPath.rename(newPath)
            self.comm.backend.db.remove(docID)
      self.comm.changeTable.emit(self.docType, self.projID)
    elif command[0] is Command.CHANGE_COLUMNS:
      dialog = TableHeader(self.comm, self.docType)
      dialog.exec()
    elif command[0] is Command.EXPORT:
      fileName = QFileDialog.getSaveFileName(self,'Export to ..',str(Path.home()),'*.csv')[0]
      if not fileName.endswith('.csv'):
        fileName += '.csv'
      with open(fileName,'w', encoding='utf-8') as fOut:
        header = [f'"{i}"' for i in self.filterHeader]
        fOut.write(','.join(header)+'\n')
        for row in range(self.models[-1].rowCount()):
          rowContent = []
          for col in range(self.models[-1].columnCount()):
            value = self.models[-1].index( row, col, QModelIndex()).data(Qt.ItemDataRole.DisplayRole)
            rowContent.append(f'"{value}"')
          fOut.write(','.join(rowContent)+'\n')
    elif command[0] is Command.ADD_ON:
      data   = []
      for row in range(self.models[-1].rowCount()):
        _, docID = self.itemFromRow(row)
        path = self.comm.backend.db.getDoc(docID)['branch'][0]['path']
        dataRow = [docID, self.comm.backend.basePath/path]
        for col in range(self.models[-1].columnCount()):
          value = self.models[-1].index(row, col).data(Qt.ItemDataRole.DisplayRole)
          dataRow.append(value)
        data.append(dataRow)
      df = pd.DataFrame(data, columns=['docID','path']+self.filterHeader)
      callAddOn(command[1], self.comm.backend, df, self)
    elif command[0] is Command.TOGGLE_HIDE:
      for row in range(self.models[-1].rowCount()):
        item, docID = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          self.comm.backend.db.hideShow(docID)
      if self.docType=='x0':
        self.comm.changeSidebar.emit('redraw')
      self.change('','')  # redraw table
    elif command[0] is Command.TOGGLE_SELECTION:
      for row in range(self.models[-1].rowCount()):
        item,_ = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          item.setCheckState(Qt.CheckState.Unchecked)
        else:
          item.setCheckState(Qt.CheckState.Checked)
    elif command[0] is Command.SHOW_ALL:
      self.showAll = not self.showAll
      self.change('','')  # redraw table
    elif command[0] is Command.RERUN_EXTRACTORS:
      redraw = False
      for row in range(self.models[-1].rowCount()):
        item, docID = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          doc = self.comm.backend.db.getDoc(docID)
          if doc['branch'][0]['path'] is None:
            continue
          redraw = True
          oldDocType = doc['type']
          doc['type'] = ['']
          if doc['branch'][0]['path'].startswith('http'):
            path = Path(doc['branch'][0]['path'])
          else:
            path = self.comm.backend.basePath/doc['branch'][0]['path']
          self.comm.backend.useExtractors(path, doc.get('shasum',''), doc)
          if doc['type'][0] == oldDocType[0]:
            del doc['branch']  #don't update
            self.comm.backend.db.updateDoc(doc, docID)
          else:
            self.comm.backend.db.remove( docID )
            del doc['id']
            doc['name'] = doc['branch'][0]['path']
            self.comm.backend.addData('/'.join(doc['type']), doc, doc['branch'][0]['stack'])
      if redraw:
        self.change('','')  # redraw table
        self.comm.changeDetails.emit('redraw')
    elif command[0] is Command.TOGGLE_GALLERY:
      self.flagGallery = not self.flagGallery
      self.change('','')    # redraw table/gallery
    elif command[0] is Command.ADD_FILTER:
      # gui
      _, rowL = widgetAndLayout('H', self.filterL, 'm', 'xl', '0', 'xl')
      self.filterSelect.append(QComboBox())
      self.filterSelect[-1].setStyleSheet(self.comm.palette.get('secondaryText', 'color'))
      self.filterSelect[-1].addItems(self.filterHeader+['rating'] if 'tag' in self.filterHeader else
                                     self.filterHeader)
      self.filterSelect[-1].currentIndexChanged.connect(self.filterChoice)
      self.filterSelect[-1].setMinimumWidth(max(len(i) for i in self.filterHeader)*14)
      rowL.addWidget(self.filterSelect[-1])
      self.filterText.append(QLineEdit(''))
      self.filterText[-1].setStyleSheet(self.comm.palette.get('secondaryText', 'color'))
      self.filterText[-1].setValidator(QRegularExpressionValidator(r'[a-zA-Z0-9_\.]+'))
      rowL.addWidget(self.filterText[-1])
      btnInverse = IconButton('ph.selection-inverse-fill', self, [Command.SET_FILTER,    len(self.models), 'invert'], rowL, checkable=True)
      self.filterInverse.append(btnInverse)
      btnDelete  = IconButton('fa5s.minus-square',         self, [Command.DELETE_FILTER, len(self.models)],           rowL)
      self.filterDelete.append(btnDelete)

      # data
      filterModel = QSortFilterProxyModel()
      self.filterText[-1].textChanged.connect(self.filterTextChanged)
      filterModel.setSourceModel(self.models[-1])
      filterModel.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
      filterModel.setFilterKeyColumn(0)
      self.models.append(filterModel)
      self.table.setModel(self.models[-1])
    elif command[0] is Command.DELETE_FILTER: # Remove filter from list of filters
      row = command[1]
      # change the information in the minus-button command
      for i in range(row, self.filterL.count()):        #e.g. model 1 is in row=0, so start in 1 for renumbering
        item_1 = self.filterL.itemAt(i)
        if item_1 is not None:
          layout_2 = item_1.widget().layout()
          if layout_2 is not None:
            item_2   = layout_2.itemAt(2)
            if item_2 is not None:
              item_2.widget().command[1] -= 1   # type: ignore[attr-defined]
      # remove row in GUI
      item_1 = self.filterL.itemAt(row-1)
      if item_1 is not None:
        item_1.widget().setParent(None) # e.g. model 1 is in row=0 for deletion
      # delete one row in models and adopt the sources
      del self.models[row]
      for i in range(1, len(self.models)):
        self.models[i].setSourceModel(self.models[i-1])
      self.table.setModel(self.models[-1])
    elif command[0] is Command.SET_FILTER:
      self.filterTextChanged('', command[1])
    else:
      print('**ERROR table menu unknown:',command)
    return


  def filterTextChanged(self, _:Any, row:int=-1) -> None:
    """ text in line-edit in the filter is changed: update regex

    Args:
      row (int): row number
    """
    if row<0:
      for idx,lineEdit in enumerate(self.filterText):
        if lineEdit==self.sender():
          row = idx
    else:
      row -= 1
    regexStr = self.filterText[row].text()
    if '*' in regexStr:
      regexStr = regexStr.replace('*','\u2605')
      if self.filterInverse[row].isChecked():
        regexStr = f'^((?!{regexStr}).)*$'
      else:
        regexStr = f'^{regexStr}$'
    elif self.filterInverse[row].isChecked():
      regexStr = f'^((?!{regexStr}).)*$'
    self.models[row+1].setFilterRegularExpression(regexStr)
    return


  def cellClicked(self, index: QModelIndex) -> None:
    """
    What happens when user clicks cell in table of tags, projects, samples, ...
    -> show details

    Args:
      index (QModelIndex): cell clicked
    """
    row = index.row()
    _, docID = self.itemFromRow(row)

    # Check if shift is held and lastClickedRow is set
    modifiers = QApplication.keyboardModifiers()
    if modifiers == Qt.ShiftModifier and self.lastClickedRow > -1:   # type: ignore[attr-defined]
      start = min(self.lastClickedRow, row)
      end = max(self.lastClickedRow, row)
      target_state = Qt.CheckState.Checked if self.itemFromRow(row)[0].checkState() == Qt.CheckState.Checked \
                      else Qt.CheckState.Unchecked
      for r in range(start, end + 1):
        item, _ = self.itemFromRow(r)
        item.setCheckState(target_state)
    else: # No need to toggle only the clicked row, just record it
      self.lastClickedRow = row

    if docID[0] == 'x':  # only show items for non-folders
      doc = self.comm.backend.db.getDoc(docID)
      if doc['type'][0] == 'x0':
        self.comm.changeProject.emit(docID, '')
        self.comm.changeSidebar.emit(docID)
      else:
        projID = doc['branch'][0]['stack'][0]
        self.comm.changeProject.emit(projID, docID)
        self.comm.changeSidebar.emit(projID)
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
      doc = self.comm.backend.db.getDoc(docID)
      self.comm.formDoc.emit(doc)
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
    index = self.models[-1].index(row,0)
    for idxModel in range(len(self.models)-1,0,-1):
      index = self.models[idxModel].mapToSource(index)
    item = self.models[0].itemFromIndex(index)                                                               # type: ignore[attr-defined]
    return item, item.accessibleText()


  def filterChoice(self, item:int) -> None:
    """
    Change the column which is used for filtering

    Args:
       item (int): column number to filter by
    """
    rating = False
    if item == self.models[-1].columnCount():  # ratings
      item = self.filterHeader.index('tag')
      rating = True
    for idx,combobox in enumerate(self.filterSelect):
      if combobox==self.sender():
        self.models[idx+1].setFilterKeyColumn(item)
        self.filterText[idx].setText('')
        if rating:
          self.filterText[idx].setValidator(QRegularExpressionValidator(r'\*+'))
        else:
          self.filterText[idx].setValidator(QRegularExpressionValidator(r'[a-zA-Z0-9_]+'))
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
