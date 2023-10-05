""" LookupIriAction class which is extended from the QAction class and contains IRI lookup logic"""
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: lookup_iri_action.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Union

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QLineEdit, QWidget
from qtawesome import icon

from pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog import TerminologyLookupDialog


class LookupIriAction(QAction):
  """ LookupIriAction class which is extended from the QAction class and contains IRI lookup logic"""

  def __init__(self,
               lookup_term: str | None = None,
               parent_line_edit: QLineEdit | None = None,
               cell_index: Union[QModelIndex, QPersistentModelIndex, None] = None) -> None:
    """
    Initializes the LookupIriAction
    Args:
      lookup_term (object): Search term used for the lookup
      parent_line_edit (QWidget): Parent line edit whose text is to be updated when lookup results are available
      cell_index (Union[QModelIndex, QPersistentModelIndex]): Cell index of the table view whose value is to be updated when lookup results are available
    """
    super().__init__(
      icon=icon('fa.angle-right', color='black', scale_factor=1),
      text="Lookup IRI online",
      parent=parent_line_edit)
    self.parent_line_edit: QLineEdit | None = parent_line_edit
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.terminology_lookup_dialog = TerminologyLookupDialog(lookup_term, self.terminology_lookup_accepted_callback)
    self.cell_index: Union[QModelIndex, QPersistentModelIndex, None] = cell_index
    super().triggered.connect(self.show_terminology_lookup_dialog)

  def show_terminology_lookup_dialog(self) -> None:
    """
    Retrieves the IRI using terminology lookup widget
    Returns: Nothing

    """
    self.logger.info("Lookup dialog shown..")
    self.terminology_lookup_dialog.show()

  def terminology_lookup_accepted_callback(self) -> None:
    """
    Callback for the terminology lookup accepted button
    Returns: Nothing
    """
    self.logger.info("Accepted IRIs: %s", self.terminology_lookup_dialog.selected_iris)
    iris = " ".join(self.terminology_lookup_dialog.selected_iris)
    if self.parent_line_edit:
      self.parent_line_edit.setText(iris)
    if self.cell_index and self.cell_index.isValid():
      self.cell_index.model().setData(self.cell_index, iris, Qt.UserRole)  # type: ignore[arg-type]
