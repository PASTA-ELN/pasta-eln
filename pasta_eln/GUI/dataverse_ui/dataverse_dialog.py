#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: dataverse_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import datetime
import logging
from typing import Any

from PySide6 import QtWidgets
from PySide6.QtWidgets import QDialog, QWidget

from pasta_eln.GUI.dataverse_ui.dataverse_dialog_base import Ui_DataverseDialogBase
from pasta_eln.GUI.dataverse_ui.dataverse_project_item_frame_base import Ui_ProjectItemFrame
from pasta_eln.GUI.dataverse_ui.dataverse_upload_widget_base import Ui_UploadWidgetFrame


class DataverseDialog(Ui_DataverseDialogBase):

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Instantiates the create type dialog
    """
    return super(DataverseDialog, cls).__new__(cls)

  def __init__(self) -> None:
    """
    Initializes the creation type dialog
    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = QDialog()
    super().setupUi(self.instance)
    for i in range(200):
      widget = self.get_project_widget(f"Example Project {i + 1}")
      self.projectsScrollAreaVerticalLayout.addWidget(widget)
    for i in range(200):
      widget = self.get_upload_widget(f"Example Project {i + 1}")
      self.scrollAreaContentsVerticalLayout.addWidget(widget)

  def get_upload_widget(self, project_name: str = 0) -> QWidget:
    uploadWidgetFrame = QtWidgets.QFrame()
    uploadWidgetUi = Ui_UploadWidgetFrame()
    uploadWidgetUi.setupUi(uploadWidgetFrame)
    uploadWidgetUi.uploadProjectLabel.setText(project_name)
    uploadWidgetUi.logConsoleTextEdit.hide()
    uploadWidgetUi.logConsoleTextEdit.setText(f"<html>Log for {project_name}<br />"
                                              f"Started upload at time: {datetime.datetime.now()}<br />"
                                              f"Generating ELN file: success, filename.................<br />"
                                              f"Uploading.................<br />"
                                              f"Uploading.................<br />"
                                              f"Uploading.................<br />"
                                              f"Uploading.................<br />"
                                              f"Uploading.................<br />"
                                              f"Uploading.................<br />"
                                              f"Upload URL: <a href=\"https://data-beta.fz-juelich.de/dataset.xhtml?persistentId=doi:10.0346/JUELICH-DATA-BETA/BORORQ\">Dataverse Link</a><br />"
                                              f"Finalized upload at time: {datetime.datetime.now()}</html>")
    uploadWidgetUi.showLogPushButton.clicked.connect(lambda:
                                                     uploadWidgetUi.logConsoleTextEdit.show()
                                                     if uploadWidgetUi.logConsoleTextEdit.isHidden()
                                                     else uploadWidgetUi.logConsoleTextEdit.hide())
    return uploadWidgetFrame

  def get_project_widget(self, project_name: str = 0) -> QWidget:
    projectWidgetFrame = QtWidgets.QFrame()
    projectWidgetUi = Ui_ProjectItemFrame()
    projectWidgetUi.setupUi(projectWidgetFrame)
    projectWidgetUi.projectNameLabel.setText(project_name)
    projectWidgetUi.modifiedDateTimeLabel.setText(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return projectWidgetFrame


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = DataverseDialog()
  ui.instance.show()
  sys.exit(app.exec())
