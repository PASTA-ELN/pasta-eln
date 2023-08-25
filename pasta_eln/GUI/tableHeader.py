""" Table Header dialog: change which colums are shown and in which order """
from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QLineEdit, QDialogButtonBox  # pylint: disable=no-name-in-module
from ..guiStyle import IconButton, widgetAndLayout, showMessage
from ..miscTools import restart
from ..guiCommunicate import Communicate
from ..fixedStringsJson import tableHeaderHelp

class TableHeader(QDialog):
  """ Table Header dialog: change which colums are shown and in which order """
  def __init__(self, comm:Communicate, docType:str):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
      docType (string):  document type
    """
    super().__init__()
    self.comm = comm
    self.docType = docType
    self.selectedList = self.comm.backend.db.getColumnNames()[docType].split(',')
    self.allSet = {i['name'] for i in self.comm.backend.db.ontology[docType]['prop']}
    self.allSet = self.allSet.union({'date','#_curated', 'type', 'name', 'comment', 'tags', 'image'})
    #clean it
    self.allSet       = {i[1:] if i[0] in ['-','_'] else i for i in self.allSet}  #change -something to something
    self.selectedList = [i[1:] if i[0] in ['-','_'] else i for i in self.selectedList]  #change -something to something

    # GUI elements
    self.setWindowTitle('Select table headers')
    self.setMinimumWidth(600)
    mainL = QVBoxLayout(self)
    _, bodyL = widgetAndLayout('H', mainL)
    _, leftL = widgetAndLayout('V', bodyL, spacing='m')
    self.choicesW = QListWidget()
    self.choicesW.addItems(list(self.allSet.difference(self.selectedList)))
    leftL.addWidget(self.choicesW)
    self.inputLine = QLineEdit()
    leftL.addWidget(self.inputLine)
    _, centerL = widgetAndLayout('V', bodyL)
    IconButton('fa5s.angle-right',        self.executeAction, centerL, 'add',  'add right')
    IconButton('fa5s.angle-left',         self.executeAction, centerL, 'del',  'remove right')
    IconButton('fa5s.angle-up',           self.executeAction, centerL, 'up',   'move up')
    IconButton('fa5s.angle-down',         self.executeAction, centerL, 'down', 'move down')
    IconButton('fa5s.angle-double-right', self.executeAction, centerL, 'text', 'use text')
    self.selectW = QListWidget()
    self.selectW.addItems(self.selectedList)
    bodyL.addWidget(self.selectW)
    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel | QDialogButtonBox.Help)
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)


  def executeAction(self) -> None:
    """ Event if user clicks button in the center """
    btn = self.sender().accessibleName()
    selectedLeft   = [i.text() for i in self.choicesW.selectedItems()]
    selectedRight  = [i.text() for i in self.selectW.selectedItems()]
    oldIndex, newIndex = -1, -1
    if btn == 'add':
      self.selectedList += selectedLeft
    elif btn == 'del':
      self.selectedList = [i for i in self.selectedList if i not in selectedRight ]
    elif btn == 'up' and len(selectedRight)==1:
      oldIndex = self.selectedList.index(selectedRight[0])
      if oldIndex>0:
        newIndex = oldIndex-1
    elif btn == 'down' and len(selectedRight)==1:
      oldIndex = self.selectedList.index(selectedRight[0])
      if oldIndex<len(self.selectedList)-1:
        newIndex = oldIndex+1
    elif btn == 'text' and self.inputLine.text()!='':
      self.selectedList += [self.inputLine.text()]
      self.allSet.add(self.inputLine.text())
    #change content
    if oldIndex>-1 and newIndex>-1:
      self.selectedList.insert(newIndex, self.selectedList.pop(oldIndex))
    self.choicesW.clear()
    self.choicesW.addItems(list(self.allSet.difference(self.selectedList)))
    self.selectW.clear()
    self.selectW.addItems(self.selectedList)
    if oldIndex>-1 and newIndex>-1:
      self.selectW.setCurrentRow(newIndex)
    return


  def save(self, btn:IconButton) -> None:
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save'):
      specialFields = ['name', 'type', 'tags', 'user', 'date']
      self.selectedList = [
          f'-{i}' if i in specialFields else i for i in self.selectedList
      ]
      self.comm.backend.db.initDocTypeViews(self.comm.backend.configuration['tableColumnsMax'],
                                            docTypeChange=self.docType, columnsChange=self.selectedList)
      restart()
        # self.comm.changeTable.emit('','')
        # self.accept()  #close
    elif btn.text().endswith('Help'):
      showMessage(self, 'Help on individual entry', tableHeaderHelp)
    else:
      print('dialogTableHeader: did not get a fitting btn ',btn.text())
    return
