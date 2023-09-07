#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: ontology_attachments_tableview_data_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging

from PySide6.QtWidgets import QWidget

from pasta_eln.ontology_configuration.ontology_tableview_data_model import OntologyTableViewModel


class OntologyAttachmentsTableViewModel(OntologyTableViewModel):
  """
  Abstracted data-model for the ontology editor's attachments table view
  """

  def __init__(self,
               parent: QWidget = None):
    """
    Initialize the data model representing attachments from ontology document in the database
    Args:
      parent (QWidget): Parent view or the widget
    """
    super().__init__(parent)
    self.logger = logging.getLogger(__name__ + "." + self.__class__.__name__)
    self.data_set = []
    self.data_name_map = {
      0: "location",
      1: "link",
      2: "delete",
      3: "re-order"
    }
    self.header_values: list[str] = list(self.data_name_map.values())
    self.columns_count: int = len(self.header_values)
