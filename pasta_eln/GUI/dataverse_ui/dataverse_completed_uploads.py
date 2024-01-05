#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: dataverse_completed_uploads.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Any

from PySide6 import QtWidgets
from PySide6.QtWidgets import QDialog

from pasta_eln.GUI.dataverse_ui.dataverse_completed_upload_task import Ui_CompletedUploadTaskFrame
from pasta_eln.GUI.dataverse_ui.dataverse_completed_uploads_base import Ui_DataverseCompletedUploadsForm


class DataverseCompletedUploads(Ui_DataverseCompletedUploadsForm):

    def __new__(cls, *_: Any, **__: Any) -> Any:
        """
        Instantiates the create type dialog
        """
        return super(DataverseCompletedUploads, cls).__new__(cls)
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.instance = QDialog()
        super().setupUi(self.instance)
        for _ in range(1000):
          widget = self.get_completed_upload_task_widget()
          self.completedUploadsVerticalLayout.addWidget(widget)
    def get_completed_upload_task_widget(self):
      completedTaskFrame = QtWidgets.QFrame()
      completedTaskUi = Ui_CompletedUploadTaskFrame()
      completedTaskUi.setupUi(completedTaskFrame)
      return completedTaskFrame


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = DataverseCompletedUploads()
  ui.instance.show()
  sys.exit(app.exec())


