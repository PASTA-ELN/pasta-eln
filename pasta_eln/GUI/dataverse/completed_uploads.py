""" Represents the completed uploads UI. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: completed_uploads.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from datetime import datetime
from typing import Any

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QDialog, QFrame

from pasta_eln.GUI.dataverse.completed_upload_task import Ui_CompletedUploadTaskFrame
from pasta_eln.GUI.dataverse.completed_uploads_base import Ui_CompletedUploadsForm
from pasta_eln.dataverse.database_api import DatabaseAPI
from pasta_eln.dataverse.upload_model import UploadModel


class CompletedUploads(Ui_CompletedUploadsForm):
  """
  Represents the completed uploads UI.

  Explanation:
      This class handles the completed uploads UI, including loading and clearing the UI,
      and creating the completed upload task widget.

  Args:
      None

  Returns:
      None
  """

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates a new instance of the CompletedUploads class.

    Explanation:
        This method creates a new instance of the CompletedUploads class.

    Args:
        *_: Variable length argument list.
        **__: Arbitrary keyword arguments.

    Returns:
        Any: The new instance of the CompletedUploads class.
    """
    return super(CompletedUploads, cls).__new__(cls)

  def __init__(self) -> None:
    """
    Initializes a new instance of the CompletedUploads class.

    Explanation:
        This method initializes a new instance of the CompletedUploads class.
        It sets up the logger, creates a QDialog instance, and sets the window modality.

    Args:
        None

    Returns:
        None
    """
    self.latest_bookmark: str | None = None
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = QDialog()
    super().setupUi(self.instance)
    self.db_api = DatabaseAPI()
    self.instance.setWindowModality(QtCore.Qt.ApplicationModal)
    self.completedUploadsScrollArea.verticalScrollBar().valueChanged.connect(
      lambda value: self.scrolled(self.completedUploadsScrollArea.verticalScrollBar(), value))
    self.filterTermLineEdit.textChanged.connect(self.load_ui)

  def load_ui(self) -> None:
    """
    Loads the UI for completed uploads.

    Explanation:
        This method loads the UI for completed uploads
        by clearing the existing UI and adding widgets for each upload.
        It retrieves the completed uploads from the database and creates the corresponding widgets.

    Args:
        None

    """
    self.clear_ui()
    result = self.db_api.get_paginated_models(UploadModel, filter_term=self.filterTermLineEdit.text())
    self.latest_bookmark = result["bookmark"]
    for upload in result["models"]:
      if isinstance(upload, UploadModel):
        widget = self.get_completed_upload_task_widget(upload)
        self.completedUploadsVerticalLayout.addWidget(widget)

  def clear_ui(self) -> None:
    """
    Clears the UI for completed uploads.

    Explanation:
        This method clears the UI for completed uploads by removing all the widgets from the layout.

    Args:
        None

    """
    for widget_pos in reversed(range(self.completedUploadsVerticalLayout.count())):
      self.completedUploadsVerticalLayout.itemAt(widget_pos).widget().setParent(None)

  def get_completed_upload_task_widget(self, upload: UploadModel) -> QFrame:
    """
    Retrieves the completed upload task widget.

    Explanation:
        This function retrieves the completed upload task widget for the given upload.
        It creates a QFrame instance and sets up the UI for the completed upload task.

    Args:
        upload (UploadModel): The upload model representing the completed upload.

    Returns:
        QFrame: The completed upload task widget.
    """
    completed_task_frame = QtWidgets.QFrame()
    completed_task_ui = Ui_CompletedUploadTaskFrame()
    completed_task_ui.setupUi(completed_task_frame)
    completed_task_ui.projectNameLabel.setText(upload.project_name)

    completed_task_ui.statusLabel.setText(upload.status)
    match upload.status:
      case "In progress" | "Queued":
        completed_task_ui.dataverseUrlLabel.setText("Waiting..")
        completed_task_ui.finishedDateTimeLabel.setText("Waiting..")
      case "Finished":
        persistent_id = upload.dataverse_url.split("persistentId=", 1)[1]
        url = (f"<html><head/><body><p>Dataverse URL: "
               f"<a href='{upload.dataverse_url}'>"
               f"<span style='font-style:italic; text-decoration: underline; color:#77767b;'>{persistent_id}</span>"
               f"</a></p></body></html>")
        completed_task_ui.dataverseUrlLabel.setText(url)
        completed_task_ui.dataverseUrlLabel.setToolTip(
          completed_task_ui.dataverseUrlLabel.toolTip() + "\n" + upload.dataverse_url)
        completed_task_ui.finishedDateTimeLabel.setText(datetime.fromisoformat(upload.finished_date_time).strftime(
          "%Y-%m-%d %H:%M:%S") if upload.finished_date_time else "")
        completed_task_ui.startedDateTimeLabel.setText(datetime.fromisoformat(upload.created_date_time).strftime(
          "%Y-%m-%d %H:%M:%S") if upload.created_date_time else "")
      case "Failed" | "Cancelled":
        completed_task_ui.dataverseUrlLabel.setText("NA")
        completed_task_ui.startedDateTimeLabel.setText("NA")
        completed_task_ui.finishedDateTimeLabel.setText("NA")
      case _:
        completed_task_ui.dataverseUrlLabel.setText("Error state..")
        completed_task_ui.startedDateTimeLabel.setText("Error state..")
        completed_task_ui.finishedDateTimeLabel.setText("Error state..")
    return completed_task_frame

  def show(self):
    """
    Shows the completed uploads dialog.

    Explanation:
        This method shows the completed uploads dialog.

    """
    self.load_ui()
    self.instance.show()

  def scrolled(self, scrollbar, value):
    if value == scrollbar.maximum() and self.latest_bookmark:
      result = self.db_api.get_paginated_models(UploadModel,
                                                filter_term=self.filterTermLineEdit.text(),
                                                bookmark=self.latest_bookmark)
      if self.latest_bookmark != result["bookmark"]:
        self.latest_bookmark = result["bookmark"]
        for upload in result["models"]:
          if isinstance(upload, UploadModel):
            widget = self.get_completed_upload_task_widget(upload)
            self.completedUploadsVerticalLayout.addWidget(widget)


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = CompletedUploads()
  ui.show()
  sys.exit(app.exec())
