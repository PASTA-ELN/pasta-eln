""" Table Header dialog: change which colums are shown and in which order """
from pathlib import Path
#pylint: disable=no-name-in-module
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, \
                              QLineEdit, QDialogButtonBox
#pylint: enable=no-name-in-module
from .style import IconButton, showMessage
from .communicate import Communicate

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
    if docType in self.comm.backend.configuration['tableHeaders']:
      self.selectedList = self.comm.backend.configuration['tableHeaders'][docType]
      self.allSet = set(i['name'] for i in self.comm.backend.db.ontology[docType]['prop'])
    else:   #default if not defined
      self.selectedList = [i['name'] for i in self.comm.backend.db.ontology[docType]['prop']]
      self.allSet = set()
    self.allSet = self.allSet.union({i['name'] for i in self.comm.backend.db.ontology[docType]['prop']})
    self.allSet = self.allSet.union({'date','#_curated', '-type', '-name', 'comment', '-tags', 'image'})
    #clean it
    self.allSet = {'_'+i[1:]+'_' if i[0] in ['-','_'] else i for i in self.allSet}  #change -something to something
    self.allSet = {'_curated_'   if i=='#_curated'    else i for i in self.allSet}  #change #_something to somehing
    self.selectedList = ['_'+i[1:]+'_' if i[0] in ['-','_'] else i for i in self.selectedList]  #change -something to something
    self.selectedList = ['_curated_'   if i=='#_curated'    else i for i in self.selectedList]  #change #_something to somehing

    # GUI elements
    self.setWindowTitle('Select table headers')
    self.setMinimumWidth(600)
    mainL = QVBoxLayout(self)
    bodyW = QWidget()
    bodyL = QHBoxLayout(bodyW)
    mainL.addWidget(bodyW)
    leftW = QWidget()
    leftL = QVBoxLayout(leftW)
    self.choicesW = QListWidget()
    self.choicesW.addItems(list(self.allSet.difference(self.selectedList)))
    leftL.addWidget(self.choicesW)
    self.inputLine = QLineEdit()
    leftL.addWidget(self.inputLine)
    bodyL.addWidget(leftW)
    centerW = QWidget()
    centerL = QVBoxLayout(centerW)
    IconButton('fa5s.angle-right', self.moveKey, centerL, 'add', 'add right')
    IconButton('fa5s.angle-left', self.moveKey, centerL, 'del', 'remove right')
    IconButton('fa5s.angle-up', self.moveKey, centerL, 'up', 'move up')
    IconButton('fa5s.angle-down', self.moveKey, centerL, 'down', 'move down')
    IconButton('fa5s.angle-double-right', self.moveKey, centerL, 'text', 'use text')
    bodyL.addWidget(centerW)
    self.selectW = QListWidget()
    self.selectW.addItems(self.selectedList)
    bodyL.addWidget(self.selectW)
    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)


  def moveKey(self) -> None:
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
      # self.selectedList = ['#_curated' if i=='_curated_' else i  for i in self.selectedList]  #change #_something to somehing
      # self.selectedList = ['-'+i[1:-1] if i[0]=='\u2605' and i[-1]=='\u2605' else i  for i in self.selectedList] #change -something to something
      # self.comm.backend.configuration['tableHeaders'][self.docType] = self.selectedList
      # with open(Path.home()/'.pastaELN.json', 'w', encoding='utf-8') as fConf:
      #   fConf.write(json.dumps(self.comm.backend.configuration,indent=2))
      # self.comm.changeTable('','')
      # self.comm.changeDetails('redraw')
      #TODO_P3 tableHeaderChange: requires view to change to views, not ontology
      showMessage(self, 'To be implemented','The changing of the table headers has to be fully implemented, yet.')
      self.comm.backend.db.initViews(self.comm.backend.configuration)
      self.accept()  #close
    else:
      print('dialogTableHeader: did not get a fitting btn ',btn.text())
    return
