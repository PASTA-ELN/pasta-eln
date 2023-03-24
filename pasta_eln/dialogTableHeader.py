""" Table Header dialog: change which colums are shown and in which order """
import json
from pathlib import Path
#pylint: disable=no-name-in-module
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, \
                              QLineEdit, QDialogButtonBox
#pylint: enable=no-name-in-module
from .style import IconButton

#TODO_P4 after save: information should be integrated into ontology; and then the views have to be rebuild

class TableHeader(QDialog):
  """ Table Header dialog: change which colums are shown and in which order """
  def __init__(self, comm, docType):
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
    self.allSet = {'\u2605'+i[1:]+'\u2605' if i[0] in ['-','_'] else i for i in self.allSet}  #change -something to something
    self.allSet = {'cur\u2605ted'          if i=='#_curated'    else i for i in self.allSet}  #change #_something to somehing
    self.selectedList = ['\u2605'+i[1:]+'\u2605' if i[0] in ['-','_'] else i for i in self.selectedList]  #change -something to something
    self.selectedList = ['cur\u2605ted'          if i=='#_curated'    else i for i in self.selectedList]  #change #_something to somehing

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
    self.choicesW.addItems(self.allSet.difference(self.selectedList))
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


  def moveKey(self):
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
    self.choicesW.addItems(self.allSet.difference(self.selectedList))
    self.selectW.clear()
    self.selectW.addItems(self.selectedList)
    if oldIndex>-1 and newIndex>-1:
      self.selectW.setCurrentRow(newIndex)
    return


  def save(self, btn):
    """ save selectedList to configuration and exit """
    if btn.text()=='Cancel':
      self.reject()
    elif btn.text()=='Save':
      # self.selectedList = ['#_curated' if i=='cur\u2605ted' else i  for i in self.selectedList]  #change #_something to somehing
      # self.selectedList = ['-'+i[1:-1] if i[0]=='\u2605' and i[-1]=='\u2605'else i  for i in self.selectedList] #change -something to something
      # self.comm.backend.configuration['tableHeaders'][self.docType] = self.selectedList
      # with open(Path.home()/'.pastaELN.json', 'w', encoding='utf-8') as fConf:
      #   fConf.write(json.dumps(self.comm.backend.configuration,indent=2))
      # self.comm.changeTable('','')
      # self.comm.changeDetails('redraw')
      #TODO_P4 requires view to change to
      print('DOES NOT WORK YES')
      self.accept()  #close
    return
