#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: dataverse_edit_full_metadata.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging
from typing import Any

from PySide6 import QtWidgets

from pasta_eln.GUI.dataverse_ui.dataverse_edit_metadata_dialog import EditMetadataDialog


class EditFullMetadata(EditMetadataDialog):

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Instantiates the create type dialog
    """
    return super(EditFullMetadata, cls).__new__(cls)

  def __init__(self) -> None:
    """
    Initializes the creation type dialog
    """
    super().__init__()
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance.setToolTip("<html>"
                             "<head/>"
                             "<body>"
                             "<p>"
                             "<span style=\" font-style:italic;\">"
                             "Edit the full set of metadata information for the datasets created in dataverse. "
                             "Datasets corresponds to PASTA projects and needs to be mapped to the appropriate PASTA level properties as needed."
                             "</span>"
                             "</p>"
                             "</body>"
                             "</html>")


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = EditFullMetadata()
  ui.instance.show()
  sys.exit(app.exec())
