import json
from PySide6.QtWidgets import QWidget, QSplitter, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QScrollArea
from PySide6.QtCore import Slot
from PySide6.QtSvgWidgets import QSvgWidget

class Body(QWidget):

  def __init__(self, comm):
    super().__init__()
    self.backend = comm.backend
    comm.chooseDocType.connect(self.changeDoctype)

    # GUI stuff
    self.table = QTableWidget(self)
    self.detailW = QScrollArea(self)
    self.detailL = QVBoxLayout(self.detailW)
    splitter = QSplitter()
    splitter.setHandleWidth(10)
    splitter.addWidget(self.table)
    splitter.addWidget(self.detailW)
    mainLayout = QVBoxLayout()
    mainLayout.addWidget(splitter)
    self.setLayout(mainLayout)

  @Slot(str)
  def changeDoctype(self, docType):
    # table = self.backend.output(docType,True)
    # docID = table.split('\n')[2].split('|')[-1].strip()
    #table
    table = self.backend.db.getView('viewDocType/'+docType)
    nrows, ncols = len(table), len(table[0]['value'])
    self.table.setColumnCount(ncols)
    header = self.backend.db.ontology[docType]
    header = [i['name'][1:] if i['name'][0]=='-' else i['name'] for i in header]
    self.table.setHorizontalHeaderLabels(header)
    self.table.verticalHeader().hide()
    self.table.setRowCount(nrows)
    for i in range(nrows):
      for j in range(ncols):
        item = QTableWidgetItem(str(table[i]['value'][j]))
        self.table.setItem(i, j, item)

    #details
    docID = table[0]['id']  #for now
    doc   = self.backend.db.getDoc(docID)
    imageW = QWidget()
    imageW.setMinimumHeight(400)
    imageL   = QVBoxLayout(imageW)
    metaVendorW   = QWidget()
    metaVendorL   = QVBoxLayout(metaVendorW)
    metaUserW     = QWidget()
    metaUserL     = QVBoxLayout(metaUserW)
    metaDetailsW  = QWidget()
    metaDetailsL  = QVBoxLayout(metaDetailsW)
    metaDatabaseW = QWidget()
    metaDatabaseL = QVBoxLayout(metaDatabaseW)
    self.detailL.addWidget(imageW)
    self.detailL.addWidget(metaDetailsW)
    self.detailL.addWidget(metaVendorW)
    self.detailL.addWidget(metaUserW)
    self.detailL.addWidget(metaDatabaseW)

    metaVendorL.addWidget(QLabel('Metadata vendor:'))
    metaUserL.addWidget(QLabel('Metadata user:'))
    metaDetailsL.addWidget(QLabel('Metadata details:'))
    metaDatabaseL.addWidget(QLabel('Metadata database:'))
    for key in doc:
      if key=='image':
        svgWidget = QSvgWidget()
        svgWidget.renderer().load(bytearray(doc[key], encoding='utf-8'))
        imageL.addWidget(svgWidget)
      elif key.startswith('_') or key.startswith('-'):
        label = QLabel(key+': '+str(doc[key]))
        label.setWordWrap(True)
        metaDatabaseL.addWidget(label)
      elif key=='metaVendor':
        metaVendorL.addWidget(QLabel(str(doc[key])))
      elif key=='metaUser':
        label = QLabel()
        label.setWordWrap(True)
        label.setText(json.dumps(doc[key], indent=2))
        metaUserL.addWidget(label)
      else:
        metaDetailsL.addWidget(QLabel(key+': '+str(doc[key])))
    return