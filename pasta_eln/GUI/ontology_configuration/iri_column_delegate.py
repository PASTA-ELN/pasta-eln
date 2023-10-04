""" IriColumnDelegate module used for the table views """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: iri_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging
from typing import Union

from PySide6.QtCore import QModelIndex, QPersistentModelIndex
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QLineEdit, QStyleOptionViewItem, QStyledItemDelegate, QWidget

from pasta_eln.GUI.ontology_configuration.lookup_iri_action import LookupIriAction


class IriColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the line edit with lookup icon for the iri column in ontology editor tables
  """

  def __init__(self) -> None:
    super().__init__()
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

  def createEditor(self,
                   parent: QWidget,
                   option: QStyleOptionViewItem,
                   index: Union[
                     QModelIndex, QPersistentModelIndex]) -> QWidget:
    """
    Creates the line edit with lookup icon for the iri column cell represented by index
    Args:
      parent (QWidget): Parent table view.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index.

    Returns:

    """
    line_edit = QLineEdit(parent)
    lookup_term = None
    if index.isValid():
      # The first column value is taken as the default lookup term
      lookup_term = index.siblingAtColumn(0).data(Qt.UserRole)  # type: ignore[arg-type]
    line_edit.addAction(
      LookupIriAction(cell_index=index,
                      lookup_term=lookup_term),
      QLineEdit.TrailingPosition)
    line_edit.setClearButtonEnabled(True)
    return line_edit
