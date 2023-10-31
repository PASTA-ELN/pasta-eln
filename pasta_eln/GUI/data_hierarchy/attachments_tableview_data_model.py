""" AttachmentsTableViewModel used for the ontology editor's attachments table view """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: attachments_tableview_data_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging
from typing import Union

from PySide6.QtWidgets import QWidget

from .tableview_data_model import TableViewModel


class AttachmentsTableViewModel(TableViewModel):
  """
  Abstracted data-model for the ontology editor's attachments table view
  """

  def __init__(self,
               parent: Union[QWidget | None] = None):
    """
    Initialize the data model representing attachments from ontology document in the database
    Args:
      parent (QWidget): Parent view or the widget
    """
    super().__init__(parent)
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.data_set = []
    self.data_name_map = {
      0: "description",
      1: "type",
      2: "delete",
      3: "re-order"
    }
    self.column_widths: dict[int, int] = {
      0: 300,  # Location column width
      1: 600,  # Link column width
      2: 120,  # Delete column width
      3: 120,  # Re-order column width
    }
    self.header_values: list[str] = list(self.data_name_map.values())
    self.columns_count: int = len(self.header_values)
