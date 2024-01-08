""" """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: dataverse_data_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from typing import Any

from PySide6 import QtCore
from PySide6.QtGui import QStandardItem, QStandardItemModel


class DataverseDataModel(QStandardItemModel):
  """DataverseDataModel used for the dataverse data model"""

  def __init__(self):
    super().__init__()
    self.setHeaderData(0, QtCore.Qt.Horizontal, 'Dataverse')

  def add_data(self, data: Any) -> None:
    """

    Returns:

    """
    items = [QStandardItem(str(i)) for i in data]
    for item in items:
      item.setCheckable(True)
      item.setCheckState(QtCore.Qt.Unchecked)
    self.appendColumn(items)
