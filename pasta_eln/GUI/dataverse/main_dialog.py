""" Represents the main dialog for dataverse integration. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: main_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import datetime
import logging
import textwrap
import time
from typing import Any

import qtawesome as qta
from PySide6 import QtWidgets
from PySide6.QtWidgets import QFrame, QWidget

from pasta_eln.GUI.dataverse.completed_uploads import CompletedUploads
from pasta_eln.GUI.dataverse.dialog_extension import DialogExtension
from pasta_eln.GUI.dataverse.edit_metadata_dialog import EditMetadataDialog
from pasta_eln.GUI.dataverse.main_dialog_base import Ui_MainDialogBase
from pasta_eln.GUI.dataverse.project_item_frame_base import Ui_ProjectItemFrame
from pasta_eln.GUI.dataverse.upload_config_dialog import UploadConfigDialog
from pasta_eln.GUI.dataverse.upload_widget_base import Ui_UploadWidgetFrame
from pasta_eln.dataverse.data_upload_task import DataUploadTask
from pasta_eln.dataverse.database_api import DatabaseAPI
from pasta_eln.dataverse.project_model import ProjectModel
from pasta_eln.dataverse.task_thread_extension import TaskThreadExtension
from pasta_eln.dataverse.upload_model import UploadModel
from pasta_eln.dataverse.upload_queue_manager import UploadQueueManager


class MainDialog(Ui_MainDialogBase):
  """
  Represents the main dialog.

  Explanation:
      This class represents the main dialog of the application.
      It provides methods to handle UI events and manage the upload process.

  """

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates a new instance of the MainDialog class.

    Explanation:
        This method creates a new instance of the MainDialog class.

    Args:
        *_: Variable length argument list.
        **__: Arbitrary keyword arguments.

    Returns:
        Any: The new instance of the MainDialog class.
    """
    return super(MainDialog, cls).__new__(cls)

  def __init__(self) -> None:
    """
    Initializes the MainDialog.

    Explanation:
        This method initializes the MainDialog class and sets up the UI.
        It also initializes the database and populates the project widgets.

    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = DialogExtension()
    super().setupUi(self.instance)
    self.db_api = DatabaseAPI()
    for project in self.db_api.get_models(ProjectModel):
      if isinstance(project, ProjectModel):
        widget = self.get_project_widget(project)
        self.projectsScrollAreaVerticalLayout.addWidget(widget)
    self.uploadPushButton.clicked.connect(self.start_upload)
    self.clearFinishedPushButton.clicked.connect(self.clear_finished)
    self.selectAllPushButton.clicked.connect(lambda: self.select_deselect_all_projects(True))
    self.deselectAllPushButton.clicked.connect(lambda: self.select_deselect_all_projects(False))
    self.config_upload_dialog = UploadConfigDialog()
    self.completed_uploads_dialog = CompletedUploads()
    self.edit_metadata_dialog = EditMetadataDialog()
    self.configureUploadPushButton.clicked.connect(self.show_configure_upload)
    self.showCompletedPushButton.clicked.connect(self.show_completed_uploads)
    self.editFullMetadataPushButton.clicked.connect(self.show_edit_metadata)
    self.upload_manager_task = UploadQueueManager()
    self.config_upload_dialog.config_reloaded.connect(self.upload_manager_task.set_concurrent_uploads)
    self.upload_manager_task_thread = TaskThreadExtension(self.upload_manager_task)
    self.cancelAllPushButton.clicked.connect(self.upload_manager_task.cancel.emit)
    self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.close_ui)
    self.instance.closed.connect(self.close_ui)

  def get_upload_widget(self, project_name: str = "") -> dict[str, QFrame | Ui_UploadWidgetFrame]:
    """
    Retrieves the upload widget for a project.

    Explanation:
        This method retrieves the upload widget for a specific project.
        It creates a QFrame instance and sets up the UI for the upload widget.

    Args:
        project_name (str): The name of the project.

    Returns:
        dict[str, QFrame | Ui_UploadWidgetFrame]: The upload widget.
    """
    upload_widget_frame = QtWidgets.QFrame()
    upload_widget_ui = Ui_UploadWidgetFrame()
    upload_widget_ui.setupUi(upload_widget_frame)
    upload_widget_ui.uploadProjectLabel.setText(textwrap.fill(project_name, 45, max_lines=1))
    upload_widget_ui.uploadProjectLabel.setToolTip(project_name)
    upload_widget_ui.statusIconLabel.setPixmap(
      qta.icon('ph.queue-light').pixmap(upload_widget_ui.statusIconLabel.size()))
    upload_widget_ui.logConsoleTextEdit.hide()
    upload_widget_ui.showLogPushButton.clicked.connect(lambda: self.show_hide_log(upload_widget_ui.showLogPushButton))
    upload_widget_ui.modelIdLabel.hide()
    return {"base": upload_widget_frame, "widget": upload_widget_ui}

  def get_project_widget(self, project: ProjectModel) -> QWidget:
    """
    Retrieves the project widget.

    Explanation:
        This method retrieves the project widget for a specific project.
        It creates a QWidget instance and sets up the UI for the project widget.

    Args:
        project (ProjectModel): The project model representing the project.

    Returns:
        QWidget: The project widget.
    """
    project_widget_frame = QtWidgets.QFrame()
    project_widget_ui = Ui_ProjectItemFrame()
    project_widget_ui.setupUi(project_widget_frame)
    project_widget_ui.projectNameLabel.setText(textwrap.fill(project.name or "", width=80, max_lines=1))
    project_widget_ui.projectNameLabel.setToolTip(project.name)
    project_widget_ui.modifiedDateTimeLabel.setText(
      datetime.datetime.fromisoformat(project.date or "").strftime("%Y-%m-%d %H:%M:%S"))
    return project_widget_frame

  def start_upload(self) -> None:
    """
    Starts the upload process.

    Explanation:
        This method starts the upload process for the selected projects.
        It retrieves the selected projects, creates upload widgets, and adds them to the upload queue.
        It also starts the upload manager task to process the upload queue.

    """
    for widget_pos in range(self.projectsScrollAreaVerticalLayout.count()):
      project_widget = self.projectsScrollAreaVerticalLayout.itemAt(widget_pos).widget()
      if project_widget.findChild(QtWidgets.QCheckBox, name="projectCheckBox").isChecked():
        upload_widget = self.get_upload_widget(
          project_widget.findChild(QtWidgets.QLabel, name="projectNameLabel").toolTip())
        self.uploadQueueVerticalLayout.addWidget(upload_widget["base"])
        task_thread = TaskThreadExtension(DataUploadTask(upload_widget["widget"]))
        self.upload_manager_task.add_to_queue(task_thread)
        if isinstance(task_thread.task, DataUploadTask):
          task_thread.task.uploadModelCreated.connect(upload_widget["widget"].modelIdLabel.setText)
    self.upload_manager_task_thread.task.start.emit()

  def clear_finished(self) -> None:
    """
    Clears the finished upload widgets.

    Explanation:
        This method clears the finished upload widgets from the upload queue.

    """
    for widget_pos in reversed(range(self.uploadQueueVerticalLayout.count())):
      self.uploadQueueVerticalLayout.itemAt(widget_pos).widget().setParent(None)

  def select_deselect_all_projects(self, checked: bool) -> None:
    """
    Selects or deselects all projects.

    Explanation:
        This method selects or deselects all projects based on the provided checked value.
        It iterates over the project widgets and sets the checked state of the projectCheckBox.

    Args:
        checked (bool): The checked state to set for the projectCheckBox.

    """
    for widget_pos in range(self.projectsScrollAreaVerticalLayout.count()):
      project_widget = self.projectsScrollAreaVerticalLayout.itemAt(widget_pos).widget()
      project_widget.findChild(QtWidgets.QCheckBox, name="projectCheckBox").setChecked(checked)

  def show_configure_upload(self) -> None:
    """
    Shows the configure upload dialog.

    Explanation:
        This method shows the configure upload dialog.

    """
    self.config_upload_dialog.load_ui()
    self.config_upload_dialog.instance.show()

  def show_completed_uploads(self) -> None:
    """
    Shows the completed uploads dialog.

    Explanation:
        This method shows the completed uploads dialog.

    """
    self.completed_uploads_dialog.load_ui()
    self.completed_uploads_dialog.instance.show()

  def show_edit_metadata(self) -> None:
    """
    Shows the edit metadata dialog.

    Explanation:
        This method shows the edit metadata dialog.

    """
    self.edit_metadata_dialog.show()

  def release_upload_manager(self) -> None:
    """
    Releases the upload manager.

    Explanation:
        This method releases the upload manager by quitting the upload manager task thread.

    """
    self.upload_manager_task_thread.quit()

  def close_ui(self) -> None:
    """
    Closes the UI.

    Explanation:
        This method closes the UI by quitting the upload manager task thread and adding a delay of 0.5 seconds.

    """
    self.upload_manager_task_thread.quit()
    time.sleep(0.5)

  def show_hide_log(self, button: QtWidgets.QPushButton) -> None:
    """
    Shows or hides the log console.

    Explanation:
        This method shows or hides the log console based on the current state.
        It retrieves the log console text edit widget and toggles its visibility.
        It also retrieves the model ID label and updates the log console text based on the model ID.

    Args:
        button (QtWidgets.QPushButton): The button triggering the action.

    """
    frame = button.parent()
    log_console_text_edit = frame.findChild(QtWidgets.QTextEdit, name="logConsoleTextEdit")
    if isinstance(log_console_text_edit, QtWidgets.QTextEdit):
      if log_console_text_edit.isHidden():
        log_console_text_edit.show()
      else:
        log_console_text_edit.hide()
      id_label = frame.findChild(QtWidgets.QLabel, name="modelIdLabel")
      if upload_model_id := id_label.text() if isinstance(id_label, QtWidgets.QLabel) else "":
        model = self.db_api.get_model(upload_model_id, UploadModel)
        log_console_text_edit.setText(model.log if isinstance(model, UploadModel) else "")


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = MainDialog()
  ui.instance.show()
  sys.exit(app.exec())
