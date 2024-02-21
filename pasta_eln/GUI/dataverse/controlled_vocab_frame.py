""" Represents the controlled vocabulary frame. """
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
  """
  Represents the controlled vocabulary frame.

  Explanation:
      This class handles the controlled vocabulary frame, including the initialization of the frame
      and the addition of new vocabulary entries.

  Args:
      vocabulary_list (list[str]): The list of vocabulary entries.

  Returns:
      None
  """

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates a new instance of the ControlledVocabFrame class.

    Explanation:
        This method creates a new instance of the ControlledVocabFrame class.

    Args:
        *_: Variable length argument list.
        **__: Arbitrary keyword arguments.

    Returns:
        Any: The new instance of the ControlledVocabFrame class.
    """
    return super(ControlledVocabFrame, cls).__new__(cls)

  def __init__(self, vocabulary_list: list[str]) -> None:
    """
    Initializes a new instance of the ControlledVocabFrame class.

    Explanation:
        This method initializes a new instance of the ControlledVocabFrame class.
        It sets up the logger, creates a QFrame instance, and sets up the UI for the controlled vocabulary frame.

    Args:
        vocabulary_list (list[str]): The list of vocabulary entries.

    Returns:
        None
    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = QtWidgets.QFrame()
    super().setupUi(self.instance)
    self.vocabComboBox.addItems(vocabulary_list)
    self.addPushButton.clicked.connect(self.add_new_vocab_entry)

  def add_new_vocab_entry(self) -> None:
    """
    Adds a new vocabulary entry.

    Explanation:
        This method adds a new vocabulary entry to the controlled vocabulary frame.
        It creates a new layout, adds a combo box and a delete button to the layout,
        and adds the layout to the main vertical layout.

    Args:
        None

    """
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
