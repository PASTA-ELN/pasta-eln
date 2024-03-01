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

from pasta_eln.GUI.dataverse.primitive_compound_controller_frame_base import Ui_PrimitiveCompoundControlledBaseFrame


class ControlledVocabFrame(Ui_PrimitiveCompoundControlledBaseFrame):
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

  def __init__(self, meta_field: dict[str, Any]) -> None:
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
    self.meta_field = meta_field
    if self.meta_field['multiple']:
      if self.meta_field['value']:
        for value in self.meta_field['value']:
          self.add_new_vocab_entry(self.meta_field["valueTemplate"], value)
      else:
        self.add_new_vocab_entry(self.meta_field["valueTemplate"], None)
    else:
      self.add_new_vocab_entry([self.meta_field["valueTemplate"]],self.meta_field['value'])

    self.addPushButton.clicked.connect(self.add_button_callback)

  def add_button_callback(self):
    if self.meta_field['multiple']:
      self.add_new_vocab_entry(self.meta_field['valueTemplate'], self.meta_field['valueTemplate'][0])
    else:
      self.add_new_vocab_entry([self.meta_field['valueTemplate']], self.meta_field['valueTemplate'])

  def add_new_vocab_entry(self, controlled_vocabulary: list[str] | None = None, value=None) -> None:
    """
    Adds a new vocabulary entry.

    Explanation:
        This method adds a new vocabulary entry to the controlled vocabulary frame.
        It creates a new layout, adds a combo box and a delete button to the layout,
        and adds the layout to the main vertical layout.

    Args:
        controlled_vocabulary ():
        value ():
        None

    """
    new_vocab_entry_layout = QtWidgets.QHBoxLayout()
    new_vocab_entry_layout.setObjectName("vocabHorizontalLayout")
    combo_box = QtWidgets.QComboBox(parent=self.instance)
    combo_box.setObjectName("vocabComboBox")
    combo_box.setToolTip("Select the controlled vocabulary.")
    combo_box.addItems(controlled_vocabulary)
    combo_box.setCurrentText(value)
    new_vocab_entry_layout.addWidget(combo_box)
    delete_push_button = QtWidgets.QPushButton(parent=self.instance)
    delete_push_button.setText("Delete")
    delete_push_button.setToolTip("Delete this particular vocabulary entry.")
    size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(delete_push_button.sizePolicy().hasHeightForWidth())
    delete_push_button.setSizePolicy(size_policy)
    delete_push_button.setMinimumSize(QSize(100, 0))
    delete_push_button.setObjectName("deletePushButton")
    new_vocab_entry_layout.addWidget(delete_push_button)
    delete_push_button.clicked.connect(lambda _: delete(new_vocab_entry_layout))
    self.mainVerticalLayout.addLayout(new_vocab_entry_layout)

  def save_modifications(self):
    if self.meta_field['multiple']:
      self.meta_field['value'].clear()
      for layout_pos in range(self.mainVerticalLayout.count()):
        if vocab_horizontal_layout := self.mainVerticalLayout.itemAt(layout_pos).layout():
          combo_box = vocab_horizontal_layout.itemAt(0).widget()
          self.meta_field['value'].append(combo_box.currentText())
      self.meta_field['value'] = list(set(self.meta_field['value']))
    else:
      layout = self.mainVerticalLayout.findChild(QtWidgets.QHBoxLayout,
                                                  "vocabHorizontalLayout")
      if combo_box := layout.itemAt(0).widget():
        self.meta_field['value'] = combo_box.currentText()


def delete(layout):
  for widget_pos in reversed(range(layout.count())):
    if item := layout.itemAt(widget_pos):
      item.widget().setParent(None)
  layout.setParent(None)


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = ControlledVocabFrame(["Test 1", "Test 2", "Test 3"])
  ui.instance.show()
  sys.exit(app.exec())
