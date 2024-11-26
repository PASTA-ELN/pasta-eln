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
import textwrap
from typing import Any

from PySide6 import QtCore
from PySide6.QtWidgets import QDialog, QFrame

from pasta_eln.GUI.dataverse.completed_upload_task import Ui_CompletedUploadTaskFrame
from pasta_eln.GUI.dataverse.completed_uploads_base import Ui_CompletedUploadsForm
from pasta_eln.dataverse.database_api import DatabaseAPI
from pasta_eln.dataverse.upload_model import UploadModel
from pasta_eln.dataverse.upload_status_values import UploadStatusValues
from pasta_eln.dataverse.utils import get_formatted_dataverse_url


class CompletedUploads(Ui_CompletedUploadsForm):
  """
  Represents the completed uploads UI.

  Explanation:
      This class handles the completed uploads UI, including loading and clearing the UI,
      and creating the completed upload task widget.
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
    """
    self.next_page: int = 1
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = QDialog()
    super().setupUi(self.instance)
    self.db_api = DatabaseAPI()
    self.instance.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
    self.completedUploadsScrollArea.verticalScrollBar().valueChanged.connect(self.scrolled)
    self.filterTermLineEdit.textChanged.connect(self.load_ui)

  def load_ui(self) -> None:
    """
    Loads the UI for completed uploads.

    Explanation:
        This method loads the UI for completed uploads by clearing the existing UI and adding widgets for each upload.
        It queries the completed uploads from the database and creates the corresponding widgets.

    Args:
        self: Represents the instance of the class.
    """
    self.logger.info("Loading completed uploads..")
    self.clear_ui()
    self.next_page = 1
    result = self.db_api.get_paginated_models(UploadModel,
                                              filter_term=self.filterTermLineEdit.text(),
                                              page_number=self.next_page,
                                              order_by_column="finished_date_time")
    for upload in result:
      if isinstance(upload, UploadModel):
        widget = self.get_completed_upload_task_widget(upload)
        self.completedUploadsVerticalLayout.addWidget(widget)
      else:
        self.logger.error("Incorrect type in queried models!")

  def clear_ui(self) -> None:
    """
    Clears the UI for completed uploads.

    Explanation:
        This method clears the UI for completed uploads by removing all the widgets from the layout.
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
    completed_task_frame = QFrame()
    completed_task_ui = Ui_CompletedUploadTaskFrame()
    completed_task_ui.setupUi(completed_task_frame)
    completed_task_ui.projectNameLabel.setText(textwrap.fill(upload.project_name or "", 45, max_lines=1))
    completed_task_ui.projectNameLabel.setToolTip(
      f"{completed_task_ui.projectNameLabel.toolTip()}\n{upload.project_name}")
    completed_task_ui.statusLabel.setText(upload.status)

    match upload.status:
      case UploadStatusValues.Queued.name | UploadStatusValues.Uploading.name:
        self.set_completed_task_properties(
          completed_task_ui,
          "Waiting..",
          "",
          "Waiting..",
          "Waiting..")
      case UploadStatusValues.Finished.name:
        url_tooltip = f"{completed_task_ui.dataverseUrlLabel.toolTip()}\n{upload.dataverse_url}"

        self.set_completed_task_properties(
          completed_task_ui,
          get_formatted_dataverse_url(upload.dataverse_url or ""),
          url_tooltip,
          upload.created_date_time or "",
          upload.finished_date_time or "")
      case UploadStatusValues.Cancelled.name:
        self.set_completed_task_properties(
          completed_task_ui,
          "NA",
          "",
          "NA",
          "NA")
      case _:  # Error or Warning
        self.set_completed_task_properties(
          completed_task_ui,
          "Error state..",
          "",
          "Error state..",
          "Error state..")
    return completed_task_frame

  def set_completed_task_properties(self,
                                    completed_task_ui: Ui_CompletedUploadTaskFrame,
                                    dataverse_url: str = "",
                                    dataverse_url_tooltip: str = "",
                                    started_date_time: str = "",
                                    finished_date_time: str = "") -> None:
    """
    Sets the properties of the completed task UI.

    Explanation:
        This function updates the properties of the completed task UI based on the provided values.
        It sets the dataverse URL, tooltip, start date time, and finish date time for the task.

    Args:
        completed_task_ui (Ui_CompletedUploadTaskFrame): The UI frame for the completed task.
        dataverse_url (str): The dataverse URL for the task.
        dataverse_url_tooltip (str): The tooltip for the dataverse URL.
        started_date_time (str): The start date and time of the task.
        finished_date_time (str): The finish date and time of the task.
    """

    (completed_task_ui.dataverseUrlLabel
     .setToolTip(dataverse_url_tooltip or completed_task_ui.dataverseUrlLabel.toolTip()))
    (completed_task_ui.dataverseUrlLabel
     .setText(dataverse_url or completed_task_ui.dataverseUrlLabel.text()))
    (completed_task_ui.startedDateTimeLabel
     .setText(started_date_time or completed_task_ui.startedDateTimeLabel.text()))
    (completed_task_ui.finishedDateTimeLabel
     .setText(finished_date_time or completed_task_ui.finishedDateTimeLabel.text()))

  def show(self) -> None:
    """
    Shows the completed uploads dialog.

    Explanation:
        This method displays the completed uploads dialog by loading the UI and showing the dialog instance.

    Args:
        self: Represents the instance of the class.
    """

    self.logger.info("Showing completed uploads..")
    self.load_ui()
    self.instance.show()

  def scrolled(self, scroll_value: int) -> None:
    """Handles the scrolling event for the completed uploads vertical scrollbar.

    This function updates the current page of completed uploads when the scrollbar
    reaches its maximum position and there are more pages available. It retrieves
    additional models from the database and adds them to the layout for display.

    Args:
        scroll_value (int): The current position of the scrollbar.

    Raises:
        DatabaseError: If there is an error retrieving the last page number or
        paginated models from the database.
    """
    vertical_scroll_bar = self.completedUploadsScrollArea.verticalScrollBar()
    last_page = self.db_api.get_last_page_number(UploadModel)
    if scroll_value == vertical_scroll_bar.maximum() and self.next_page < last_page:
      self.next_page += 1
      models = self.db_api.get_paginated_models(UploadModel,
                                                filter_term=self.filterTermLineEdit.text(),
                                                page_number=self.next_page,
                                                order_by_column="finished_date_time")
      for upload in models:
        if isinstance(upload, UploadModel):
          widget = self.get_completed_upload_task_widget(upload)
          self.completedUploadsVerticalLayout.addWidget(widget)
