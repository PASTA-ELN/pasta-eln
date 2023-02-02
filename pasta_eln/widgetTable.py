""" widget that shows the table of the items """
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel   # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot               # pylint: disable=no-name-in-module
from .style import TextButton, Label

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

    # GUI elements
    mainL = QVBoxLayout()
    headerW = QWidget()
    headerL = QHBoxLayout(headerW)
    self.headline = Label('','h1', headerL)
    self.addBtn = TextButton('Add',self.addItem, headerL, hide=True)
    mainL.addWidget(headerW)
    self.table = QTableWidget(self)
    self.table.cellClicked.connect(self.cellClicked)
    self.table.setSortingEnabled(True)
    self.table.setAlternatingRowColors(True)
    mainL.addWidget(self.table)
    self.setLayout(mainL)


  @Slot(str, str)
  def changeTable(self, docType, projID):
    """
    What happens when the table should change should change

    Args:
      docType (str): document type
      projID (str): id of project
    """
    self.docType = docType
    if projID=='':
      self.data = self.comm.backend.db.getView('viewDocType/'+self.docType)
    else:
      self.data = self.comm.backend.db.getView('viewDocType/'+self.docType, preciseKey=projID)
    if len(self.data)==0:
      self.table.hide()
      return
    self.headline.setText(self.comm.backend.db.dataLabels[self.docType])
    self.addBtn.show()
    nrows, ncols = len(self.data), len(self.data[0]['value'])
    self.table.setColumnCount(ncols)
    header = self.comm.backend.db.ontology[self.docType]['prop']
    header = [i['name'][1:] if i['name'][0]=='-' else i['name'] for i in header]
    self.table.setHorizontalHeaderLabels(header)
    self.table.verticalHeader().hide()
    self.table.setRowCount(nrows)
    for i in range(nrows):
      for j in range(ncols):
        item = QTableWidgetItem(str(self.data[i]['value'][j])) #TODO_P2 show icon in table if none, ...
        self.table.setItem(i, j, item)
    self.table.show()
    self.comm.changeDetails.emit('')
    return


  def cellClicked(self, row, column):
    """
    What happens when user clicks cell in table

    Args:
      row (int): row number
      column (int): column number
    """
    # print("Row, column", row, column)
    #change details
    # if column==0:
    self.comm.changeDetails.emit(self.data[row]['id'])
    return


  def addItem(self):
    """ What happens when user clicks add-button """
    self.comm.formDoc.emit({'-type':[self.docType]})
    return
