""" Edit properties of a docType """
import string
from typing import Callable, Optional
import pandas as pd
import qtawesome as qta
from PySide6.QtCore import Slot
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QLabel, QLineEdit, QVBoxLayout
from ...fixedStringsJson import allIcons
from ..guiCommunicate import Communicate
from ..guiStyle import TextButton, widgetAndLayout, widgetAndLayoutForm
from ..messageDialog import showMessage


class DocTypeEditor(QDialog):
  """ Edit properties of a docType """
  def __init__(self, comm:Communicate, docType:str, callback:Optional[Callable[[str,str],None]]=None):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
      doc (dict):  document to change / create
      callback (function): callback to allow sending the new doc-type
    """
    super().__init__()
    self.comm = comm
    self.comm.backendThread.worker.beSendSQL.connect(self.onGetData)
    self.docType = docType
    self.shortcuts:list[list[str]] = []
    self.callback = callback
    mainL = QVBoxLayout(self)
    _, self.mainForm = widgetAndLayoutForm(mainL)
    self.setWindowTitle('Edit item type properties')
    mainL.addStretch(1)
    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)
    # initialize communication if needed
    self.comm.uiSendSQL.emit([{'type':'get_df',
                               'cmd':'SELECT docType, shortcut from docTypes'}])
    if self.docType in self.comm.docTypesTitles:
      self.comm.uiSendSQL.emit([{'type':'get_df',
                                 'cmd':f'SELECT * from docTypes WHERE docType=="{self.docType}"'}])
      self.initialData = None
    else:
      self.initialData = ['']*6
      self.paint()


  @Slot(str, pd.DataFrame)
  def onGetData(self, cmd:str, data:pd.DataFrame) -> None:
    """ Handle data received from backend worker
    Args:
      cmd (str): command that was sent to backend
      data (pd.DataFrame): DataFrame containing the data
    """
    if cmd == 'SELECT docType, shortcut from docTypes':
      self.shortcuts = [j for i,j in data.values.tolist() if len(j)==1 and i!=self.docType]
    elif cmd.startswith('SELECT * from docTypes WHERE'):
      self.initialData = data.values.tolist()[0]
      self.paint()


  def paint(self) -> None:
    """ Paint the dialog with the initial data """
    if self.initialData is None:
      return
    self.row1 = QLineEdit(self.initialData[0])
    self.row1.setToolTip('Name of item type: lower case letters only. Must be unique')
    if self.docType:
      self.row1.setDisabled(True)
    else:
      self.row1.setValidator(QRegularExpressionValidator(r'(^[a-wyz][\w\/]{3,}$)'))
    self.mainForm.addRow(QLabel('DocType '), self.row1)

    self.row2 = QLineEdit(self.initialData[2])
    self.row2.setToolTip('Label that the user reads: it is suggested to start with upper case and end with s as in "Samples"')
    self.mainForm.addRow(QLabel('Label '), self.row2)

    row3W, row3L = widgetAndLayout('H', None, 's')
    # Label('type:', 'h2', row3L)
    # self.comboType = QComboBox()
    # self.comboType.addItems(set(i.split('.')[0] for i in allIcons))
    # row3L.addWidget(self.comboType)
    # Label('icon:', 'h2', row3L)
    self.comboIcon = QComboBox()
    self.comboIcon.addItem('')
    for icon in allIcons:
      self.comboIcon.addItem(qta.icon(icon, scale_factor=1.5), icon)
    self.comboIcon.setCurrentText(self.initialData[3])
    row3L.addWidget(self.comboIcon)
    if self.docType.startswith('x'):
      self.comboIcon.setDisabled(True)
    self.mainForm.addRow(QLabel('Icon '), row3W)

    self.row4 = QLineEdit(self.initialData[4])
    self.row4.setToolTip('One letter shortcut used with Ctrl-. Must be unique.')
    if self.docType.startswith('x'):
      self.row4.setDisabled(True)
    else:
      dataSet = set(string.ascii_lowercase).difference(self.shortcuts)
      self.row4.setValidator(QRegularExpressionValidator(f'^[{"".join(dataSet)}]$'))
    self.mainForm.addRow(QLabel('Shortcut '), self.row4)


  def closeDialog(self, btn:TextButton) -> None:
    """
    cancel or save entered data

    Args:
      btn (QButton): save or cancel button
    """
    if btn.text().endswith('Cancel'):
      self.reject()
    else:
      label    = self.row2.text()
      if not label or label in [v['title'] for _,v in self.comm.docTypesTitles.items()]:
        showMessage(self, 'Error', 'The label has to be used and cannot be used already by another type.', 'Critical')
        return
      icon     = '' if self.docType.startswith('x') else self.comboIcon.currentText()
      shortcut = '' if self.docType.startswith('x') else self.row4.text()
      if self.docType:                                                               # update existing docType
        cmd = f"UPDATE docTypes SET title='{label}', shortcut='{shortcut}', icon='{icon}' WHERE docType = "\
              f"'{self.docType}'"
        self.comm.uiSendSQL.emit([{'type':'one',  'cmd':cmd}])
        docType = self.docType
      else:                                                  # create new docType, with default schema entries
        docType = self.row1.text()
        if not docType or docType in self.comm.docTypesTitles:
          showMessage(self, 'Error', 'DocType name is not valid or already exists', 'Critical')
          return
        self.comm.uiSendSQL.emit([{'type':'one', 'cmd':'INSERT INTO docTypes VALUES (?, ?, ?, ?, ?, ?)',
                                   'list':[docType, '', label, icon, shortcut, '']},
                                  {'type':'one', 'cmd':'INSERT INTO docTypeSchema VALUES (?, ?, ?, ?, ?, ?, ?)',
                                   'list':[docType, '', '0', 'name', '', '', '']},
                                  {'type':'one', 'cmd':'INSERT INTO docTypeSchema VALUES (?, ?, ?, ?, ?, ?, ?)',
                                   'list':[docType, '', '1', 'tags', '', '', '']},
                                  {'type':'one', 'cmd':'INSERT INTO docTypeSchema VALUES (?, ?, ?, ?, ?, ?, ?)',
                                   'list':[docType, '', '2', 'comment', '', '', '']}])
        if self.callback is not None:
          self.callback(label, docType)
      self.accept()
    return


  def reject(self) -> None:
    """ Reject the dialog, stop the thread and disconnect signals """
    self.comm.backendThread.worker.beSendSQL.disconnect(self.onGetData)
    super().reject()


  def accept(self) -> None:
    """ Accept the dialog, stop the thread and disconnect signals """
    self.comm.backendThread.worker.beSendSQL.disconnect(self.onGetData)
    super().accept()
