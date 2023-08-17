#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: required_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Union

from PySide6.QtCore import QModelIndex, QPersistentModelIndex
from PySide6.QtWidgets import QStyledItemDelegate, QCheckBox, QWidget, QStyleOptionViewItem


class RequiredColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the radio buttons for the required column in property table
  """

  def __init__(self):
    """
      Constructor
    """
    super().__init__()

  def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                   index: Union[QModelIndex, QPersistentModelIndex]) -> QWidget:
    checkbox = QCheckBox(parent)
    checkbox.setChecked(False)
    return checkbox
