""" Edit properties of a docType """
import string
from typing import Callable, Optional
import qtawesome as qta
from PySide6.QtGui import QRegularExpressionValidator  # pylint: disable=no-name-in-module
from PySide6.QtWidgets import (QLineEdit, QDialog, QLabel, QVBoxLayout, QDialogButtonBox, QComboBox) # pylint: disable=no-name-in-module
from ...guiCommunicate import Communicate
from ...guiStyle import (TextButton, widgetAndLayoutForm, widgetAndLayout)
from ...fixedStringsJson import allIcons


class DocTypeEditor(QDialog):
  """ Edit properties of a docType """
  def __init__(self, comm:Communicate, docType:str, callback:Optional[Callable[[str],None]]=None):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
      doc (dict):  document to change / create
      callback (function): callback to allow sending the new doc-type
    """
    super().__init__()
    self.comm = comm
    self.db   = self.comm.backend.db
    self.docType = docType
    self.callback = callback
    mainL = QVBoxLayout(self)
    _, mainForm = widgetAndLayoutForm(mainL)
    self.setWindowTitle('Edit docType properties')

    initialData = self.comm.backend.db.dataHierarchy(docType,'*') if docType else ['']*6
    self.row1 = QLineEdit(initialData[0])
    self.row1.setToolTip('Name of document type: lower case letters only. Must be unique')
    if docType:
      self.row1.setDisabled(True)
    else:
      data = self.comm.backend.db.dataHierarchy('','')
      regex = ''.join(f'(?!{i})' for i in data)
      self.row1.setValidator(QRegularExpressionValidator(regex+r'(^[a-wyz]\w{3,}$)'))
    mainForm.addRow(QLabel('DocType '), self.row1)

    self.row2 = QLineEdit(initialData[2])
    self.row2.setToolTip('Label that the user reads: it is suggested to start with upper case and end with s as in "Samples"')
    mainForm.addRow(QLabel('Label '), self.row2)

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
    self.comboIcon.setCurrentText(initialData[3])
    row3L.addWidget(self.comboIcon)
    if docType.startswith('x'):
      self.comboIcon.setDisabled(True)
    mainForm.addRow(QLabel('Icon '), row3W)

    self.row4 = QLineEdit(initialData[4])
    self.row4.setToolTip('One letter shortcut used with Ctrl-. Must be unique.')
    if docType.startswith('x'):
      self.row4.setDisabled(True)
    else:
      data = [i[1] for i in self.comm.backend.db.dataHierarchy('','shortcut') if not i[0].startswith('x')]
      dataSet = set(string.ascii_lowercase).difference(data)
      self.row4.setValidator(QRegularExpressionValidator(f'^[{"".join(dataSet)}]$'))
    mainForm.addRow(QLabel('Shortcut '), self.row4)

    #final button box
    mainL.addStretch(1)
    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)


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
      icon     = '' if self.docType.startswith('x') else self.comboIcon.currentText()
      shortcut = '' if self.docType.startswith('x') else self.row4.text()
      if self.docType:
        self.comm.backend.db.cursor.execute(f"UPDATE docTypes SET title='{label}', shortcut='{shortcut}', "\
                                            f"icon='{icon}' WHERE docType = '{self.docType}'")
      else:
        docType = self.row1.text()
        self.comm.backend.db.cursor.execute('INSERT INTO docTypes VALUES (?, ?, ?, ?, ?, ?)',
                                            [docType, '', label, icon, shortcut, ''])
        self.comm.backend.db.cursor.execute('INSERT INTO docTypeSchema VALUES (?, ?, ?, ?, ?, ?, ?)',
                                            [docType, '', '0', 'name', '', '', ''])
        self.comm.backend.db.cursor.execute('INSERT INTO docTypeSchema VALUES (?, ?, ?, ?, ?, ?, ?)',
                                            [docType, '', '1', 'tags', '', '', ''])
        self.comm.backend.db.cursor.execute('INSERT INTO docTypeSchema VALUES (?, ?, ?, ?, ?, ?, ?)',
                                            [docType, '', '2', 'comment', '', '', ''])
        if self.callback is not None:
          self.callback(docType)
      self.comm.backend.db.connection.commit()
      self.accept()
    return
