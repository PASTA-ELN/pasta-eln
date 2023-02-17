""" widget that shows the table of the items """
import re
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel   # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot               # pylint: disable=no-name-in-module
import qtawesome as qta
from .style import TextButton, Label, getColor

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
    self.headline.setText(self.comm.backend.db.dataLabels[self.docType])
    self.addBtn.show()
    header = self.comm.backend.db.ontology[self.docType]['prop']
    header = [i['name'][1:] if i['name'][0]=='-' else i['name'] for i in header]
    nrows, ncols = len(self.data), len(header)
    self.table.setColumnCount(ncols)
    self.table.setHorizontalHeaderLabels(header)
    self.table.verticalHeader().hide()
    self.table.setRowCount(nrows)
    fgColor = getColor(self.comm.backend,'secondaryText')
    for i in range(nrows):
      for j in range(ncols):
        # print(i,j, self.data[i]['value'][j], type(self.data[i]['value'][j]))
        if self.data[i]['value'][j] is None or not self.data[i]['value'][j]:  #None, False
          item = QTableWidgetItem(qta.icon('fa5s.times', color=fgColor),'')
        elif isinstance(self.data[i]['value'][j], bool) and self.data[i]['value'][j]: #True
          item = QTableWidgetItem(qta.icon('fa5s.check', color=fgColor),'')
        elif isinstance(self.data[i]['value'][j], list):                      #list
          item =  QTableWidgetItem(', '.join(self.data[i]['value'][j]))
        elif re.match(r'^[a-z]-[a-z0-9]{32}$',self.data[i]['value'][j]):      #Link
          item = QTableWidgetItem(qta.icon('fa5s.link', color=fgColor),'')
        else:
          item = QTableWidgetItem(self.data[i]['value'][j])
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
