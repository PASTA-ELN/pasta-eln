""" widget that shows the table of the items """
import re
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableView, QLabel,  \
                              QHeaderView, QAbstractItemView, QGridLayout, QLineEdit, QComboBox # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt, Slot, QSortFilterProxyModel           # pylint: disable=no-name-in-module
from PySide6.QtGui import QBrush, QStandardItemModel, QStandardItem  # pylint: disable=no-name-in-module
import qtawesome as qta
from .style import TextButton, Label, getColor, LetterButton

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
    self.docType = ''
    self.projID = ''
    self.filterHeader = []

    ### GUI elements
    mainL = QVBoxLayout()
    # header
    self.headerW = QWidget()
    self.headerW.hide()
    headerL = QHBoxLayout(self.headerW)
    self.headline = Label('','h1', headerL)
    TextButton('Group Edit', self.groupEdit, headerL)
    TextButton('Add Filter', self.addFilter, headerL)
    TextButton('Add',self.addItem, headerL)
    mainL.addWidget(self.headerW)
    # filter
    filterW = QWidget()
    self.filterL = QGridLayout(filterW)
    mainL.addWidget(filterW)
    # table
    self.models = []
    self.table = QTableView(self)
    self.table.verticalHeader().hide()
    self.table.clicked.connect(self.cellClicked)
    self.table.setSortingEnabled(True)
    self.table.setAlternatingRowColors(True)
    self.table.setSelectionMode(QAbstractItemView.MultiSelection)
    header = self.table.horizontalHeader()
    header.setSectionsMovable(True)
    header.setSortIndicatorShown(True)
    header.setMaximumSectionSize(200)
    header.resizeSections(QHeaderView.ResizeToContents)
    header.setStretchLastSection(True)
    # ---
    mainL.addWidget(self.table)
    self.setLayout(mainL)


  @Slot(str, str, bool)
  def changeTable(self, docType, projID, redraw):
    """
    What happens when the table changes its raw information

    Args:
      docType (str): document type
      projID (str): id of project
      redraw (bool): redraw. if true, leave other arguments as empty strings
    """
    if docType=='_tags_':
      self.data = self.comm.backend.db.getView('viewIdentify/viewTags')
      header = ['tag','name']
      self.headline.setText('TAGS')
      #TODO_P5 tags should not have add button
    else:
      if not redraw:
        self.docType = docType
        self.projID  = projID
      if self.projID=='':
        self.data = self.comm.backend.db.getView('viewDocType/'+self.docType)
      else:
        self.data = self.comm.backend.db.getView('viewDocType/'+self.docType, preciseKey=self.projID)
      self.headline.setText(self.comm.backend.db.dataLabels[self.docType])
      header = self.comm.backend.db.ontology[self.docType]['prop']
      header = [i['name'][1:] if i['name'][0]=='-' else i['name'] for i in header]  #change -something to something
      header = [i[2:] if i[0:2]=='#_' else i for i in header] #change #_something to somehing
    self.headerW.show()
    nrows, ncols = len(self.data), len(header)
    model = QStandardItemModel(nrows, ncols)
    model.setHorizontalHeaderLabels(header)
    fgColor = getColor(self.comm.backend,'secondaryText')
    for i in range(nrows):
      for j in range(ncols):
        if docType=='_tags_':  #tags list
          if j==0:
            if self.data[i]['key']=='_curated':
              item = QStandardItem('cur\u2605ted')
            elif re.match(r'_\d', self.data[i]['key']):
              item = QStandardItem('\u2605'*int(self.data[i]['key'][1]))
            else:
              item = QStandardItem(self.data[i]['key'])
          else:
            item = QStandardItem(self.data[i]['value'][0])
        else:                 #list for normal doctypes
          # print(i,j, self.data[i]['value'][j], type(self.data[i]['value'][j]))
          if self.data[i]['value'][j] is None or not self.data[i]['value'][j]:  #None, False
            item = QStandardItem(qta.icon('fa5s.times', color=fgColor),'')
          elif isinstance(self.data[i]['value'][j], bool) and self.data[i]['value'][j]: #True
            item = QStandardItem(qta.icon('fa5s.check', color=fgColor),'')
          elif isinstance(self.data[i]['value'][j], list):                      #list
            item =  QStandardItem(', '.join(self.data[i]['value'][j]))
          elif re.match(r'^[a-z]-[a-z0-9]{32}$',self.data[i]['value'][j]):      #Link
            item = QStandardItem(qta.icon('fa5s.link', color=fgColor),'')
          else:
            item = QStandardItem(self.data[i]['value'][j])
        if j==0:
          item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
          item.setCheckState(Qt.CheckState.Unchecked)
        else:
          item.setFlags(Qt.ItemIsEnabled)
        model.setItem(i, j, item)
    self.models.append(model)
    self.table.setModel(self.models[-1])
    self.table.show()
    self.comm.changeDetails.emit('')
    return


  def cellClicked(self, item):
    """
    What happens when user clicks cell in table

    Args:
      item (QStandardItem): cell clicked
    """
    row = item.row()
    # column = item.column()
    if self.data[row]['id'][0]=='x':
      self.comm.changeProject.emit(self.data[row]['id'], '')
    else:
      self.comm.changeDetails.emit(self.data[row]['id'])
    return


  def addItem(self):
    """ What happens when user clicks add-button """
    self.comm.formDoc.emit({'-type':[self.docType]})
    return


  def addFilter(self):
    """ What happens when user clicks add-filter """
    # gui
    rowW = QWidget()
    rowL = QHBoxLayout(rowW)
    text = QLineEdit('')
    rowL.addWidget(text)
    select = QComboBox()
    self.filterHeader = [i['name'] for i in self.comm.backend.db.ontology[self.docType]['prop']]
    self.filterHeader = [i[1:] if i[0]=='-'   else i for i in self.filterHeader]
    self.filterHeader = [i[2:] if i[:2]=='#_' else i for i in self.filterHeader]
    select.addItems(self.filterHeader)
    select.currentIndexChanged.connect(self.filterChoice)
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
    return

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
    if row<len(self.models):
      del self.models[int(row)]
      self.filterL.itemAt(int(row)-1).widget().setParent(None)
    else:
      print('Bug: try to remove from list something that does not exist as accessible name did not change') #TODO_P5
    return

  def groupEdit(self):
    """ What happens after the user has selected multiple rows and wants to edit """
    docIDs = []
    for row in range(self.table.rowCount()):
      if self.table.item(row,0).checkState() == Qt.CheckState.Checked:
        docIDs.append(self.data[row]['id'])
    print("I want to group-edit ", docIDs) #TODO_P3 Continue here
    return
