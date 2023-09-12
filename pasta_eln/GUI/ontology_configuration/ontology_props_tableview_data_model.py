""" Table view model used for the properties table in the ontology editor """
# Context from Code Snippet pasta_eln/GUI/ontology_configuration/ontology_props_tableview_data_model.py:##  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: ontology_props_tableview_data_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Union, Any

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtWidgets import QWidget

from .ontology_configuration_constants import PROPS_TABLE_LIST_COLUMN_INDEX
from .ontology_tableview_data_model import OntologyTableViewModel


class OntologyPropsTableViewModel(OntologyTableViewModel):
  """
  Data-model for the ontology property table view
  """

  def __init__(self,
               parent: Union[QWidget | None] = None):
    """
    Initialize the data model representing the properties of a type in the ontology document
    Args:
      parent (QWidget): Parent view or the widget
    """
    super().__init__(parent)
    self.logger = logging.getLogger(__name__ + "." + self.__class__.__name__)
    self.data_set = []
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
    self.header_values: list[str] = list(self.data_name_map.values())
    self.columns_count: int = len(self.header_values)

  def setData(self,
              index: Union[QModelIndex, QPersistentModelIndex],
              value: Any, role: int = Qt.ItemDataRole) -> bool:  # type: ignore[assignment]
    """
    Overridden method for setting the data, only handling the PROPS_TABLE_LIST_COLUMN_INDEX, the rest is handled by base class
    Args:
      index (Union[QModelIndex, QPersistentModelIndex]): Table cell index
      value (Any): New value
      role (int): Role for the data

    Returns: Nothing
    """
    if (index.isValid() and
        index.column() == PROPS_TABLE_LIST_COLUMN_INDEX):
      value = [i.strip() for i in value.split(',')] \
        if ',' in value \
        else value
    return super().setData(index, value, role)

  def data(self,
           index: Union[QModelIndex, QPersistentModelIndex],
           role: int = Qt.ItemDataRole) -> Any:  # type: ignore[assignment]
    """
    Overriden method for getting the data, only handles the PROPS_TABLE_LIST_COLUMN_INDEX case
    Args:
      index (Union[QModelIndex, QPersistentModelIndex]): Table cell index
      role (int): Role for the data

    Returns: Data retrieved for the respective index

    """
    if (index.isValid()
        and index.column() == PROPS_TABLE_LIST_COLUMN_INDEX):
      data = super().data(index, role)
      return ",".join(data) \
        if isinstance(data, list) \
        else data
    return super().data(index, role)
