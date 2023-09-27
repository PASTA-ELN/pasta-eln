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
    super().triggered.connect(self.retrieve_iris)

  def retrieve_iris(self) -> None:
    """
    Retrieves the IRI using terminology lookup widget
    Returns: Nothing

    """
    # Needs to be implemented
    self.logger.info("IRI lookup initiated..")
