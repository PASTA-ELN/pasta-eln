""" widget that shows the table of the items """
import re, logging
from pathlib import Path
from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QMenu, QFileDialog, QMessageBox, QHeaderView, QLineEdit, QComboBox # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt, Slot, QSortFilterProxyModel, QModelIndex       # pylint: disable=no-name-in-module
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont # pylint: disable=no-name-in-module
from .dialogTableHeader import TableHeader
from .style import TextButton, IconButton, Label, Action, widgetAndLayout, spacesMap
from .fixedStrings import defaultOntologyNode
from .communicate import Communicate

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
    comm.changeTable.connect(self.changeTable)
    comm.stopSequentialEdit.connect(self.stopSequentialEditFunction)
    self.data:list[dict[str,Any]] = []
    self.models:list[QStandardItemModel] = []
    self.docType = ''
    self.projID = ''
    self.filterHeader:list[str] = []
    self.showAll= False

    ### GUI elements
    mainL = QVBoxLayout()
    mainL.setSpacing(0)
    mainL.setContentsMargins(spacesMap['s'], spacesMap['s'], spacesMap['s'], spacesMap['s'])
    # header
    self.headerW, headerL = widgetAndLayout('H', mainL, 'm')
    self.headerW.hide()
    self.headline = Label('','h1', headerL)
    headerL.addStretch(1)
    self.addBtn = TextButton('Add',        self.executeAction, headerL, name='addItem')
    TextButton('Add Filter', self.executeAction, headerL, name='addFilter')

    self.selectionBtn = TextButton('Selection', None, headerL)
    selectionMenu = QMenu(self)
    Action('Toggle selection',self.executeAction, selectionMenu, self, name='toggleSelection')
    selectionMenu.addSeparator()
    Action('Group Edit',      self.executeAction, selectionMenu, self, name='groupEdit')
    Action('Sequential edit', self.executeAction, selectionMenu, self, name='sequentialEdit')
    Action('Toggle hidden',   self.executeAction, selectionMenu, self, name='toggleHide')
    Action('Rerun extractors',self.executeAction, selectionMenu, self, name='rerunExtractors')
    Action('Delete',          self.executeAction, selectionMenu, self, name='delete')
    self.selectionBtn.setMenu(selectionMenu)

    more = TextButton('More',None, headerL)
    self.moreMenu = QMenu(self)
    Action('Show / Hide hidden items', self.executeAction, self.moreMenu, self, name='showAll')
    Action('Export to csv',            self.executeAction, self.moreMenu, self, name='export')
    self.actionChangeColums = Action('Change columns',  self.executeAction, self.moreMenu, self, name='changeColumns')  #add action at end

    more.setMenu(self.moreMenu)
    # filter
    _, self.filterL = widgetAndLayout('Grid', mainL, top='s', bottom='s')
    # table
    self.table = QTableView(self)
    self.table.verticalHeader().hide()
    self.table.clicked.connect(self.cellClicked)
    self.table.doubleClicked.connect(self.cell2Clicked)
    self.table.setSortingEnabled(True)
    self.table.setAlternatingRowColors(True)
    header = self.table.horizontalHeader()
    header.setSectionsMovable(True)
    header.setSortIndicatorShown(True)
    header.setMaximumSectionSize(400) #TODO_P5 addToConfig
    header.resizeSections(QHeaderView.ResizeToContents)
    header.setStretchLastSection(True)
    #TODO_P3 table: shift-select
    # ---
    mainL.addWidget(self.table)
    self.setLayout(mainL)


  @Slot(str, str)
  def changeTable(self, docType:str, projID:str) -> None:
    """
    What happens when the table changes its raw information

    Args:
      docType (str): document type; leave empty for redraw
      projID (str): id of project
    """
    if docType!=self.docType or projID!=self.projID:
      logging.debug('table:changeTable |'+docType+'|'+projID+'|')
    self.models = []
    for i in reversed(range(self.filterL.count())):
      self.filterL.itemAt(i).widget().setParent(None)   # type: ignore
    if docType!='':
      self.docType = docType
      self.projID  = projID
    if self.docType=='_tags_':
      self.addBtn.hide()
      #TODO_P4 projectView: if table-row click, move to view it project
      if self.showAll:
        self.data = self.comm.backend.db.getView('viewIdentify/viewTagsAll')
      else:
        self.data = self.comm.backend.db.getView('viewIdentify/viewTags')
      self.filterHeader = ['tag','name','type']
      self.headline.setText('TAGS')
      self.actionChangeColums.setVisible(False)
    else:
      self.addBtn.show()
      if docType=='x0':
        self.selectionBtn.hide()
      else:
        self.selectionBtn.show()
      path = 'viewDocType/'+self.docType+'All' if self.showAll else 'viewDocType/'+self.docType
      if self.projID=='':
        self.data = self.comm.backend.db.getView(path)
      else:
        self.data = self.comm.backend.db.getView(path, preciseKey=self.projID)
      if self.docType=='-':
        self.headline.setText('Unidentified')
        self.actionChangeColums.setVisible(False)
      else:
        self.actionChangeColums.setVisible(True)
        if self.docType in self.comm.backend.db.dataLabels:
          self.headline.setText(self.comm.backend.db.dataLabels[self.docType])
      if self.docType in self.comm.backend.configuration['tableHeaders']:
        self.filterHeader = self.comm.backend.configuration['tableHeaders'][docType]
      elif self.docType=='-':
        self.filterHeader = [i['name'] for i in defaultOntologyNode]
      else:
        self.filterHeader = [i['name'] for i in self.comm.backend.db.ontology[self.docType]['prop']]
      self.filterHeader = [i[1:] if i[0]=='-'   else i for i in self.filterHeader]  #change -something to something
      self.filterHeader = [i[2:] if i[:2]=='#_' else i for i in self.filterHeader]  #change #_something to somehing
    self.headerW.show()
    nrows, ncols = len(self.data), len(self.filterHeader)
    model = QStandardItemModel(nrows, ncols)
    model.setHorizontalHeaderLabels(self.filterHeader)
    for i in range(nrows):
      for j in range(ncols):
        if self.docType=='_tags_':  #tags list
          if j==0:
            if self.data[i]['key']=='_curated':
              item = QStandardItem('_curated_')
            elif re.match(r'_\d', self.data[i]['key']):
              item = QStandardItem('\u2605'*int(self.data[i]['key'][1]))
            else:
              item = QStandardItem(self.data[i]['key'])
          else:
            item = QStandardItem(self.data[i]['value'][j-1])
        else:                 #list for normal doctypes
          # print(i,j, self.data[i]['value'][j], type(self.data[i]['value'][j]))
          if self.data[i]['value'][j] is None or not self.data[i]['value'][j]:  #None, False
            item = QStandardItem('\u00D7')
            item.setFont(QFont("Helvetica [Cronyx]", 16))
          elif isinstance(self.data[i]['value'][j], bool) and self.data[i]['value'][j]: #True
            item = QStandardItem('\u2713')
            item.setFont(QFont("Helvetica [Cronyx]", 16))
          elif isinstance(self.data[i]['value'][j], list):                      #list, e.g. qrCodes
            item =  QStandardItem(', '.join(self.data[i]['value'][j]))
          elif re.match(r'^[a-z\-]-[a-z0-9]{32}$',self.data[i]['value'][j]):      #Link
            item = QStandardItem('\u260D')
            item.setFont(QFont("Helvetica [Cronyx]", 16))
          else:
            if self.filterHeader[j]=='tags':
              tags = self.data[i]['value'][j].split(' ')
              if '_curated' in tags:
                tags[tags.index('_curated')] = '_curated_'
              for iStar in range(1,6):
                if '_'+str(iStar) in tags:
                  tags[tags.index('_'+str(iStar))] = '\u2605'*iStar
              text = ' '.join(tags)
            else:
              text = self.data[i]['value'][j]
            item = QStandardItem(text)
        if j==0:
          doc = self.comm.backend.db.getDoc(self.data[i]['id'])
          if len([b for b in doc['-branch'] if False in b['show']])>0:
            item.setText( item.text()+'  \U0001F441' )
          item.setAccessibleText(doc['_id'])
          if docType!='x0':
            item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)   # type: ignore[operator]
            item.setCheckState(Qt.CheckState.Unchecked)
            #TODO_P3 design: make the checkboxes larger!
        else:
          item.setFlags(Qt.ItemIsEnabled) # type: ignore[arg-type]
        model.setItem(i, j, item)
    self.models.append(model)
    self.table.setModel(self.models[-1])
    self.table.show()
    return


  def cellClicked(self, item:QStandardItem) -> None:
    """
    What happens when user clicks cell in table of tags, projects, samples, ...
    -> show details

    Args:
      item (QStandardItem): cell clicked
    """
    row = item.row()
    _, docID = self.itemFromRow(row)
    # column = item.column()
    if docID[0]=='x': #only show items for non-folders
      doc = self.comm.backend.db.getDoc(docID)
      if doc['-type'][0]=='x0':
        self.comm.changeProject.emit(docID,'')
        self.comm.changeSidebar.emit(docID)
      else:
        projID = doc['-branch'][0]['stack'][0]
        self.comm.changeProject.emit(projID, docID)
        self.comm.changeSidebar.emit(projID)
    else:
      self.comm.changeDetails.emit(docID)
    return


  def cell2Clicked(self, item:QStandardItem) -> None:
    """
    What happens when user double clicks cell in table of projects

    Args:
      item (QStandardItem): cell clicked
    """
    row = item.row()
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


  def executeAction(self) -> None:
    """ Any action by the buttons and menu at the top of the page """
    if hasattr(self.sender(), 'data'):  #action
      menuName = self.sender().data()
    else:                               #button
      menuName = self.sender().accessibleName()
    if menuName == 'addItem':
      self.comm.formDoc.emit({'-type':[self.docType]})
      self.comm.changeTable.emit(self.docType, self.projID)
      if self.docType=='x0':
        self.comm.changeSidebar.emit('redraw')
    elif menuName == 'addFilter':
      # gui
      _, rowL = widgetAndLayout('H', self.filterL, 'm', 'xl', '0', 'xl')
      text = QLineEdit('')
      rowL.addWidget(text)
      select = QComboBox()
      select.addItems(self.filterHeader)
      select.currentIndexChanged.connect(self.filterChoice)
      # print('create filter row',str(len(self.models)) )
      select.setAccessibleName(str(len(self.models)))
      rowL.addWidget(select)
      IconButton('fa5s.minus-square', self.delFilter, rowL, str(len(self.models)), backend=self.comm.backend)
      # data
      #TODO_P5 can you sort for true false in tables too?
      filterModel = QSortFilterProxyModel()
      text.textChanged.connect(filterModel.setFilterRegularExpression)
      filterModel.setSourceModel(self.models[-1])
      filterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
      filterModel.setFilterKeyColumn(0)
      self.models.append(filterModel)
      self.table.setModel(self.models[-1])
    elif menuName == 'groupEdit':
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
        intersection = intersection.difference({'-branch', '-user', '-client', 'metaVendor', 'shasum', \
          '_id', 'metaUser', '_rev', '-name', '-date', 'image', '_attachments','links'})
        intersectionDict:dict[str,Any] = {i:'' for i in intersection}
        intersectionDict['-tags'] = []
        intersectionDict['-type'] = [self.docType]
        intersectionDict.update({'_ids':docIDs})
        self.comm.formDoc.emit(intersectionDict)
        self.comm.changeDetails.emit('redraw')
        self.comm.changeTable.emit(self.docType, '')
    elif menuName == 'sequentialEdit':
      self.stopSequentialEdit = False
      for row in range(self.models[-1].rowCount()):
        item, docID = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          self.comm.formDoc.emit(self.comm.backend.db.getDoc(docID))
        if self.stopSequentialEdit:
          break
      self.comm.changeTable.emit(self.docType, '')
    elif menuName == 'delete':
      for row in range(self.models[-1].rowCount()):
        item, docID = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          ret = QMessageBox.critical(self, 'Warning', 'Are you sure you want to delete this data: '+item.text()+'?',\
                                    QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
          if ret==QMessageBox.StandardButton.Yes:
            doc = self.comm.backend.db.getDoc(docID)
            for branch in doc['-branch']:
              oldPath = self.comm.backend.basePath/branch['path']
              if oldPath.exists():
                newPath    = oldPath.parent/('trash_'+oldPath.name)
                oldPath.rename(newPath)
            self.comm.backend.db.remove(docID)
      self.comm.changeTable.emit(self.docType, '')
    elif menuName == 'changeColumns':
      dialog = TableHeader(self.comm, self.docType)
      dialog.exec()
    elif menuName == 'export':
      #TODO_P4 export: export via extractor in high resolution: change order: first save, then rescale
      fileName = QFileDialog.getSaveFileName(self,'Export to ..',str(Path.home()),'*.csv')[0]
      with open(fileName,'w', encoding='utf-8') as fOut:
        header = ['"'+i+'"' for i in self.filterHeader]
        fOut.write(','.join(header)+'\n')
        for row in range(self.models[-1].rowCount()):
          rowContent = []
          for col in range(self.models[-1].columnCount()):
            value = self.models[-1].index( row, col, QModelIndex() ).data( Qt.DisplayRole )  # type: ignore[arg-type]
            rowContent.append('"'+value+'"')
          fOut.write(','.join(rowContent)+'\n')
    elif menuName == 'toggleHide':
      for row in range(self.models[-1].rowCount()):
        item, docID = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          self.comm.backend.db.hideShow(docID)
      if self.docType=='x0':
        self.comm.changeSidebar.emit('redraw')
      self.changeTable('','')  # redraw table
    elif menuName == 'toggleSelection':
      for row in range(self.models[-1].rowCount()):
        item,_ = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          item.setCheckState(Qt.CheckState.Unchecked)
        else:
          item.setCheckState(Qt.CheckState.Checked)
    elif menuName == 'showAll':
      self.showAll = not self.showAll
      self.changeTable('','')  # redraw table
    elif menuName == 'rerunExtractors':
      for row in range(self.models[-1].rowCount()):
        item, docID = self.itemFromRow(row)
        if item.checkState() == Qt.CheckState.Checked:
          doc = self.comm.backend.db.getDoc(docID)
          oldDocType = doc['-type']
          if doc['-branch'][0]['path'].startswith('http'):
            path = Path(doc['-branch'][0]['path'])
          else:
            path = self.comm.backend.basePath/doc['-branch'][0]['path']
          self.comm.backend.useExtractors(path, '', doc)
          if doc['-type'][0] == oldDocType[0]:
            del doc['-branch']  #don't update
            self.comm.backend.db.updateDoc(doc, self.data[row]['id'])
          else:  #TODO_P5 this will rerun useExtractor: ok for now
            self.comm.backend.db.remove( self.data[row]['id'] )
            del doc['_id']
            del doc['_rev']
            doc['-name'] = doc['-branch'][0]['path']
            self.comm.backend.addData('/'.join(doc['-type']), doc, doc['-branch'][0]['stack'])
      self.changeTable('','')  # redraw table
      self.comm.changeDetails.emit('redraw')
    else:
      print("**ERROR widgetTable menu unknown:",menuName)
    return


  @Slot()
  def stopSequentialEditFunction(self) -> None:
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
    item = self.models[0].itemFromIndex(index)
    return item, item.accessibleText()


  #TODO_P5 invert filter: not 'Sur' in name => '^((?!Sur).)*$' in name
  def filterChoice(self, item:QStandardItem) -> None:
    """
    Change the column which is used for filtering

    Args:
       item (int): column number to filter by
    """
    row = self.sender().accessibleName()
    self.models[int(row)].setFilterKeyColumn(item)
    return

  def delFilter(self) -> None:
    """ Remove filter from list of filters """
    row = int(self.sender().accessibleName())
    #print('Delete filter row', row)
    for i in range(row, self.filterL.count()):        #e.g. model 1 is in row=0, so start in 1 for renumbering
      minusBtnW = self.filterL.itemAt(i).widget().layout().itemAt(2).widget()
      minusBtnW.setAccessibleName( str(int(minusBtnW.accessibleName())-1) )  #rename: -1 from accessibleName
    del self.models[row]
    self.filterL.itemAt(row-1).widget().setParent(None) # type: ignore # e.g. model 1 is in row=0 for deletion
    for i in range(1, len(self.models)):
      self.models[i].setSourceModel(self.models[i-1])
    self.table.setModel(self.models[-1])
    return
