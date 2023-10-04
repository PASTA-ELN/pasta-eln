""" RetrieveIriAction class which is extended from the QAction class and contains IRI lookup logic"""
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: retrieve_iri_action.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QWidget

from pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog import TerminologyLookupDialog


class RetrieveIriAction(QAction):
  """ RetrieveIriAction class which is extended from the QAction class and contains IRI lookup logic"""

  def __init__(self,
               parent: QWidget = None) -> None:  # type: ignore[assignment]
    """
    Initializes the RetrieveIriAction
    Args:
      parent (QWidget): Parent widget
    """
    super().__init__(
      icon=QIcon.fromTheme("go-next"),
      text="Lookup IRI online",
      parent=parent)
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.terminology_lookup_dialog = TerminologyLookupDialog(self.terminology_lookup_accepted_callback)
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
    self.parent().setText(" ".join(self.terminology_lookup_dialog.selected_iris)) # type: ignore[attr-defined]
