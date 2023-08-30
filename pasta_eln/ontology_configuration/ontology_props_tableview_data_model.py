#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: ontology_props_tableview_data_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging

from PySide6.QtWidgets import QWidget

from pasta_eln.ontology_configuration.ontology_tableview_data_model import OntologyTableViewModel


class OntologyPropsTableViewModel(OntologyTableViewModel):
  """
  Data-model for the ontology property table view
  """

  def __init__(self,
               parent: QWidget = None):
    """
    Initialize the data model representing the properties of a type in the ontology document
    Args:
      parent (QWidget): Parent view or the widget
    """
    super().__init__(parent)
    self.logger = logging.getLogger(__name__ + "." + self.__class__.__name__)
    self.data_set = None
    self.data_name_map = {
      0: "name",
      1: "query",
      2: "list",
      3: "link",
      4: "required",
      5: "unit",
      6: "delete",
      7: "re-order"
    }
    self.header_values = list(self.data_name_map.values())
    self.columns_count = len(self.header_values)
