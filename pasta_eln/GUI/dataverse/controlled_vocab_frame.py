#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: controlled_vocab_frame.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Any

from PySide6 import QtWidgets
from PySide6.QtCore import QSize

from pasta_eln.GUI.dataverse.controlled_vocab_frame_base import Ui_ControlledVocabularyFrame


class ControlledVocabFrame(Ui_ControlledVocabularyFrame):

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    """
    return super(ControlledVocabFrame, cls).__new__(cls)

  def __init__(self, vocabulary_list: list[str]) -> None:
    """
    Initializes the creation type dialog
    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = QtWidgets.QFrame()
    super().setupUi(self.instance)
    self.vocabComboBox.addItems(vocabulary_list)
    self.addPushButton.clicked.connect(self.add_new_vocab_entry)

  def add_new_vocab_entry(self):
    new_vocab_entry_layout = QtWidgets.QHBoxLayout()
    new_vocab_entry_layout.setObjectName("vocabHorizontalLayout")
    combo_box = QtWidgets.QComboBox(parent=self.instance)
    combo_box.setObjectName("vocabComboBox")
    combo_box.setToolTip(self.vocabComboBox.toolTip())
    combo_box.setModel(self.vocabComboBox.model())
    new_vocab_entry_layout.addWidget(combo_box)
    delete_push_button = QtWidgets.QPushButton(parent=self.instance)
    delete_push_button.setText("Delete")
    delete_push_button.setToolTip(self.deletePushButton.toolTip())
    size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(delete_push_button.sizePolicy().hasHeightForWidth())
    delete_push_button.setSizePolicy(size_policy)
    delete_push_button.setMinimumSize(QSize(100, 0))
    delete_push_button.setObjectName("deletePushButton")
    new_vocab_entry_layout.addWidget(delete_push_button)
    self.mainVerticalLayout.addLayout(new_vocab_entry_layout)


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = ControlledVocabFrame(["Test 1", "Test 2", "Test 3"])
  ui.instance.show()
  sys.exit(app.exec())
