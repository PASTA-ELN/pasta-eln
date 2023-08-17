#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: delete_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Union

from PySide6.QtCore import QModelIndex, QPersistentModelIndex
from PySide6.QtWidgets import QStyledItemDelegate, QPushButton, QWidget, QStyleOptionViewItem


class DeleteColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the delete icon for the delete column in property table
  """

  def __init__(self):
    """
      Constructor
    """
    super().__init__()

  def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                   index: Union[QModelIndex, QPersistentModelIndex]) -> QWidget:
    button = QPushButton(parent)
    button.setText("Delete")
    return button
