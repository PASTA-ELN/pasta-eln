""" widget that shows the table of the items """
import re, json, logging
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableView, QLabel, QMenu, QFileDialog, \
                              QHeaderView, QAbstractItemView, QGridLayout, QLineEdit, QComboBox # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt, Slot, QSortFilterProxyModel, QModelIndex       # pylint: disable=no-name-in-module
from PySide6.QtGui import QBrush, QStandardItemModel, QStandardItem, QAction, QFont # pylint: disable=no-name-in-module
import qtawesome as qta
from .dialogTableHeader import TableHeader
from .style import TextButton, Label, getColor, LetterButton, Action, showMessage
from .fixedStrings import defaultOntologyNode

#Scan button to more button
class Table(QWidget):
  """ widget that shows the table of the items """
  def __init__(self, comm):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
    """
    super().__init__()
    self.comm = comm
    comm.changeTable.connect(self.changeTable)
    self.data = []
    self.models = []
    self.docType = ''
    self.projID = ''
    self.filterHeader = []
    self.showAll= False

    ### GUI elements
    mainL = QVBoxLayout()
    # header
    self.headerW = QWidget()
    self.headerW.hide()
    headerL = QHBoxLayout(self.headerW)
    self.headline = Label('','h1', headerL)
    headerL.addStretch(1)
    self.addBtn = TextButton('Add',        self.executeAction, headerL, name='addItem')
    TextButton('Add Filter', self.executeAction, headerL, name='addFilter')

    selection = TextButton('Selection',None, headerL)
    selectionMenu = QMenu(self)
    Action('Toggle selection',self.executeAction, selectionMenu, self, name='toggleSelection')
    selectionMenu.addSeparator()
    Action('Group Edit',      self.executeAction, selectionMenu, self, name='groupEdit')
    Action('Sequential edit', self.executeAction, selectionMenu, self, name='sequentialEdit')
    Action('Toggle hidden',   self.executeAction, selectionMenu, self, name='toggleHide')
    #TODO_P3 extractors: rerun happens on scan now
    #Action('Rerun extractors',self.executeAction, selectionMenu, self, name='rerunExtractors')
    selection.setMenu(selectionMenu)

    more = TextButton('More',None, headerL)
    self.moreMenu = QMenu(self)
    Action('Show / Hide hidden items', self.executeAction, self.moreMenu, self, name='showAll')
    Action('Export',                   self.executeAction, self.moreMenu, self, name='export')
    more.setMenu(self.moreMenu)
    mainL.addWidget(self.headerW)
    # filter
    filterW = QWidget()
    self.filterL = QGridLayout(filterW)
    mainL.addWidget(filterW)
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
    # ---
    mainL.addWidget(self.table)
    self.setLayout(mainL)


  @Slot(str, str)
  def changeTable(self, docType, projID):
    """
    What happens when the table changes its raw information

    Args:
      docType (str): document type; leave empty for redraw
      projID (str): id of project
    """
    self.models = []
    for i in reversed(range(self.filterL.count())):
      self.filterL.itemAt(i).widget().setParent(None)
    if docType!='':
      self.docType = docType
      self.projID  = projID
    if self.docType=='_tags_':
      self.addBtn.hide()
      if self.showAll:
        self.data = self.comm.backend.db.getView('viewIdentify/viewTagsAll')
      else:
        self.data = self.comm.backend.db.getView('viewIdentify/viewTags')
      self.filterHeader = ['tag','name']
      self.headline.setText('TAGS')
      if self.moreMenu.actions()[-1].text()!='Export':
        self.moreMenu.removeAction(self.moreMenu.actions()[-1])  #remove last action
    else:
      self.addBtn.show()
      path = 'viewDocType/'+self.docType+'All' if self.showAll else 'viewDocType/'+self.docType
      if self.projID=='':
        self.data = self.comm.backend.db.getView(path)
      else:
        self.data = self.comm.backend.db.getView(path, preciseKey=self.projID)
      if self.docType=='-':
        self.headline.setText('Unidentified')
        if self.moreMenu.actions()[-1].text()!='Export':
          self.moreMenu.removeAction(self.moreMenu.actions()[-1])  #remove last action
      else:
        if self.moreMenu.actions()[-1].text()=='Export':
          Action('Change headers',  self.executeAction, self.moreMenu, self, name='changeTableHeader')  #add action at end
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
            item = QStandardItem(self.data[i]['value'][0])
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
          elif re.match(r'^[a-z]-[a-z0-9]{32}$',self.data[i]['value'][j]):      #Link
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
          item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
          item.setCheckState(Qt.CheckState.Unchecked)
        else:
          item.setFlags(Qt.ItemIsEnabled)
        model.setItem(i, j, item)
    self.models.append(model)
    self.table.setModel(self.models[-1])
    self.table.show()
    self.comm.changeDetails.emit('empty')
    return


  def cellClicked(self, item):
    """
    What happens when user clicks cell in table of tags, projects, samples, ...
    -> show details

    Args:
      item (QStandardItem): cell clicked
    """
    row = item.row()
    docID = self.models[-1].item(row,0).accessibleText()
    # column = item.column()
    if docID!='x0': #only show items for non-folders
      self.comm.changeDetails.emit(docID)
    return


  def cell2Clicked(self, item):
    """
    What happens when user double clicks cell in table of projects

    Args:
      item (QStandardItem): cell clicked
    """
    row = item.row()
    docID = self.models[-1].item(row,0).accessibleText()
    if self.docType=='x0':
      self.comm.changeProject.emit(docID, '')
    else:
      doc = self.comm.backend.db.getDoc(docID)
      self.comm.formDoc.emit(doc)
      self.comm.changeTable.emit('','')
      self.comm.changeDetails.emit('redraw')
    return


  def executeAction(self):
    """ Any action by the buttons and menu at the top of the page """
    if hasattr(self.sender(), 'data'):  #action
      menuName = self.sender().data()
    else:                               #button
      menuName = self.sender().accessibleName()
    if menuName == 'addItem':
      self.comm.formDoc.emit({'-type':[self.docType]})
      self.comm.changeTable.emit(self.docType, '')
      if self.docType=='x0':
        self.comm.changeSidebar.emit()
    elif menuName == 'addFilter':
      # gui
      rowW = QWidget()
      rowL = QHBoxLayout(rowW)
      text = QLineEdit('')
      rowL.addWidget(text)
      select = QComboBox()
      select.addItems(self.filterHeader)
      select.currentIndexChanged.connect(self.filterChoice)
      # print('create filter row',str(len(self.models)) )
      select.setAccessibleName(str(len(self.models)))
      rowL.addWidget(select)
      LetterButton('-', self.delFilter, rowL, str(len(self.models)))
      self.filterL.addWidget(rowW)
      # data
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
        if hasattr(self.models[-1], 'item'):
          if self.models[-1].item(row,0).checkState() == Qt.CheckState.Checked:
            docIDs.append( self.data[row]['id'] )
            thisKeys = set(self.comm.backend.db.getDoc(self.data[row]['id']))
            if intersection is None:
              intersection = thisKeys
            else:
              intersection = intersection.intersection(thisKeys)
        else:
          logging.error('widgetTable model has no item '+str(self.models[-1])+' '+str(row)+' '+str(thisKeys))
          showMessage(self, 'Send information to Steffen','widgetTable model has no item '+\
                            str(self.models[-1])+' '+str(row)+' '+str(thisKeys))
          #TODO_P4 debugging: when does this occur
      #remove keys that should not be group edited and build dict
      intersection = intersection.difference({'-type', '-branch', '-user', '-client', 'metaVendor', 'shasum', \
        '_id', 'metaUser', '_rev', '-name', '-date', 'image', '_attachments','links'})
      intersection = {i:'' for i in intersection}
      intersection.update({'_ids':docIDs})
      self.comm.formDoc.emit(intersection)
      self.comm.changeDetails.emit('redraw')
    elif menuName == 'sequentialEdit':
      for row in range(self.models[-1].rowCount()):
        if self.models[-1].item(row,0).checkState() == Qt.CheckState.Checked:
          self.comm.formDoc.emit(self.comm.backend.db.getDoc( self.data[row]['id'] ))
      self.comm.changeTable.emit(self.docType, '')
    elif menuName == 'changeTableHeader':
      if self.docType in ['-','_tags_'] :
        logging.error('widgetTable: cannot show changeTableHeader for '+self.docType)
      else:
        dialog = TableHeader(self.comm, self.docType)
        dialog.exec()
    elif menuName == 'export':
      fileName = QFileDialog.getSaveFileName(self,'Export to ..',str(Path.home()),'*.csv')[0]
      with open(fileName,'w', encoding='utf-8') as fOut:
        header = ['"'+i+'"' for i in self.filterHeader]
        fOut.write(','.join(header)+'\n')
        for row in range(self.models[-1].rowCount()):
          rowContent = []
          for col in range(self.models[-1].columnCount()):
            value = self.models[-1].index( row, col, QModelIndex() ).data( Qt.DisplayRole )
            rowContent.append('"'+value+'"')
          fOut.write(','.join(rowContent)+'\n')
    elif menuName == 'toggleHide':
      for row in range(self.models[-1].rowCount()):
        if self.models[-1].item(row,0).checkState() == Qt.CheckState.Checked:
          self.comm.backend.db.hideShow( self.data[row]['id'] )
      if self.docType=='x0':
        self.comm.changeSidebar.emit()
      self.changeTable('','')  # redraw table
    elif menuName == 'toggleSelection':
      for row in range(self.models[-1].rowCount()):
        if self.models[-1].item(row,0).checkState() == Qt.CheckState.Checked:
          self.models[-1].item(row,0).setCheckState(Qt.CheckState.Unchecked)
        else:
          self.models[-1].item(row,0).setCheckState(Qt.CheckState.Checked)
    elif menuName == 'showAll':
      self.showAll = not self.showAll
      self.changeTable('','')  # redraw table
    elif menuName == 'rerunExtractors':
      for row in range(self.models[-1].rowCount()):
        if self.models[-1].item(row,0).checkState() == Qt.CheckState.Checked:
          doc = self.comm.backend.db.getDoc( self.data[row]['id'] )
          if doc['-branch'][0]['path'].startswith('http'):
            path = Path(doc['-branch'][0]['path'])
          else:
            path = self.comm.backend.basePath/doc['-branch'][0]['path']
          self.useExtractors(path, '', doc)
          del doc['-branch']  #don't update
          self.db.updateDoc(doc, self.data[row]['id'])
      self.changeTable('','')  # redraw table
      self.comm.changeDetails.emit('redraw') # redraw details
    else:
      print("**ERROR widgetTable menu unknown:",menuName)
    return

  #TODO_P3 invert filter: not 'Sur' in name => '^((?!Sur).)*$' in name
  def filterChoice(self, item):
    """
    Change the column which is used for filtering

    Args:
       item (int): column number to filter by
    """
    row = self.sender().accessibleName()
    self.models[int(row)].setFilterKeyColumn(item)
    return
  def delFilter(self):
    """ Remove filter from list of filters """
    row = int(self.sender().accessibleName())
    #print('Delete filter row', row)
    for i in range(row, self.filterL.count()):        #e.g. model 1 is in row=0, so start in 1 for renumbering
      minusBtnW = self.filterL.itemAt(i).widget().layout().itemAt(2).widget()
      minusBtnW.setAccessibleName( str(int(minusBtnW.accessibleName())-1) )  #rename: -1 from accessibleName
    del self.models[row]
    self.filterL.itemAt(row-1).widget().setParent(None) #e.g. model 1 is in row=0 for deletion
    for i in range(1, len(self.models)):
      self.models[i].setSourceModel(self.models[i-1])
    self.table.setModel(self.models[-1])
    return
