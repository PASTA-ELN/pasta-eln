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

from PySide6 import QtWidgets
from PySide6.QtWidgets import QDialog, QFrame, QLabel, QMessageBox, QWidget

from pasta_eln.GUI.dataverse.completed_uploads import CompletedUploads
from pasta_eln.GUI.dataverse.config_dialog import ConfigDialog
from pasta_eln.GUI.dataverse.dialog_extension import DialogExtension
from pasta_eln.GUI.dataverse.edit_metadata_dialog import EditMetadataDialog
from pasta_eln.GUI.dataverse.main_dialog_base import Ui_MainDialogBase
from pasta_eln.GUI.dataverse.project_item_frame_base import Ui_ProjectItemFrame
from pasta_eln.GUI.dataverse.upload_config_dialog import UploadConfigDialog
from pasta_eln.GUI.dataverse.upload_widget_base import Ui_UploadWidgetFrame
from pasta_eln.backend import Backend
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.data_upload_task import DataUploadTask
from pasta_eln.dataverse.database_api import DatabaseAPI
from pasta_eln.dataverse.project_model import ProjectModel
from pasta_eln.dataverse.task_thread_extension import TaskThreadExtension
from pasta_eln.dataverse.upload_model import UploadModel
from pasta_eln.dataverse.upload_queue_manager import UploadQueueManager
from pasta_eln.dataverse.upload_status_values import UploadStatusValues
from pasta_eln.dataverse.utils import check_if_dataverse_exists, check_if_minimal_metadata_exists, \
  check_login_credentials, get_formatted_message, update_status


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

  def __init__(self, backend: Backend) -> None:
    """
    Initializes the MainDialog.

    Explanation:
        This method initializes the MainDialog class and sets up the UI.
        It also initializes the database and populates the project widgets.

    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = DialogExtension()
    super().setupUi(self.instance)
    self.backend = backend
    self.db_api = DatabaseAPI()
    self.db_api.initialize_database()
    self.is_dataverse_configured: tuple[bool, str] = self.check_if_dataverse_is_configured()
    self.config_dialog: ConfigDialog | None = None

    if self.is_dataverse_configured[0]:
      self.completed_uploads_dialog = CompletedUploads()
      self.edit_metadata_dialog = EditMetadataDialog()
      self.upload_manager_task = UploadQueueManager()
      self.config_upload_dialog = UploadConfigDialog()
      self.upload_manager_task_thread = TaskThreadExtension(self.upload_manager_task)

      # Connect signals and slots
      self.config_upload_dialog.config_reloaded.connect(self.upload_manager_task.set_concurrent_uploads)
      self.config_upload_dialog.config_reloaded.connect(self.edit_metadata_dialog.reload_config)
      self.uploadPushButton.clicked.connect(self.start_upload)
      self.clearFinishedPushButton.clicked.connect(self.clear_finished)
      self.selectAllPushButton.clicked.connect(lambda: self.select_deselect_all_projects(True))
      self.deselectAllPushButton.clicked.connect(lambda: self.select_deselect_all_projects(False))
      self.configureUploadPushButton.clicked.connect(self.show_configure_upload)
      self.showCompletedPushButton.clicked.connect(self.show_completed_uploads)
      self.editFullMetadataPushButton.clicked.connect(self.show_edit_metadata)
      self.cancelAllPushButton.clicked.connect(self.upload_manager_task.cancel_all_tasks.emit)
      self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.close_ui)
      self.instance.closed.connect(self.close_ui)

      # Load UI
      self.load_ui()

  def load_ui(self) -> None:
    """
    Loads the UI for the main dialog.

    Explanation:
        This method loads the UI for the main dialog by retrieving project models from the database
        and adding corresponding widgets to the projects scroll area.

    Args:
        self: The instance of the class.
    """
    for project in self.db_api.get_models(ProjectModel):
      if isinstance(project, ProjectModel):
        widget = self.get_project_widget(project)
        self.projectsScrollAreaVerticalLayout.addWidget(widget)

  def get_upload_widget(self, project_name: str = "") -> dict[str, QFrame | Ui_UploadWidgetFrame]:
    """
    Creates the upload widget for a project.

    Explanation:
        This method retrieves the upload widget for a specific project.
        It creates a QFrame instance and sets up the UI for the upload widget.

    Args:
        project_name (str): The name of the project.

    Returns:
        dict[str, QFrame | Ui_UploadWidgetFrame]: The upload widget.
    """
    base_frame = QtWidgets.QFrame()
    upload_widget_ui = Ui_UploadWidgetFrame()
    upload_widget_ui.setupUi(base_frame)
    upload_widget_ui.uploadProjectLabel.setText(textwrap.fill(project_name, 45, max_lines=1))
    upload_widget_ui.uploadProjectLabel.setToolTip(project_name)
    update_status(UploadStatusValues.Queued.name,
                  upload_widget_ui.statusLabel.setText,
                  upload_widget_ui.statusIconLabel.setPixmap)
    upload_widget_ui.logConsoleTextEdit.hide()
    upload_widget_ui.showLogPushButton.clicked.connect(lambda: self.show_hide_log(upload_widget_ui.showLogPushButton))
    upload_widget_ui.modelIdLabel.hide()
    return {"base": base_frame, "widget": upload_widget_ui}

  def get_project_widget(self, project: ProjectModel) -> QWidget:
    """
    Creates the project widget.


    Explanation:
        This method retrieves the project widget for a specific project.
        It creates a QWidget instance and sets up the UI for the project widget.

    Args:
        project (ProjectModel): The project model representing the project.

    Returns:
        QWidget: The project widget.

    Raises:
        ValueError: If the project model is not an instance of ProjectModel.
                    If the project model date is not in expected ISO format.
    """
    if not isinstance(project, ProjectModel):
      raise ValueError("Project model must be an instance of ProjectModel!")
    project_widget_frame = QtWidgets.QFrame()
    project_widget_ui = Ui_ProjectItemFrame()
    project_widget_ui.setupUi(project_widget_frame)
    project_widget_ui.projectNameLabel.setText(textwrap.fill(project.name or "", width=80, max_lines=1))
    project_widget_ui.projectNameLabel.setToolTip(project.name)
    project_widget_ui.modifiedDateTimeLabel.setText(
      datetime.datetime.fromisoformat(project.date_modified or "").strftime("%Y-%m-%d %H:%M:%S"))
    project_widget_ui.projectDocIdLabel.hide()
    project_widget_ui.projectDocIdLabel.setText(project.id)
    return project_widget_frame

  def start_upload(self) -> None:
    """
    Starts the upload process.

    Explanation:
        This method starts the upload process for the selected projects.
        It retrieves the selected projects, creates upload widgets, and adds them to the upload queue.
        It also starts the upload manager task to process the upload queue.

    """
    if not self.check_if_minimal_metadata_present():
      self.logger.warning("Minimum metadata not present. Please add all needed metadata and then retry!")
      return
    for widget_pos in range(self.projectsScrollAreaVerticalLayout.count()):
      project_widget = self.projectsScrollAreaVerticalLayout.itemAt(widget_pos).widget()
      if project_widget.findChild(QtWidgets.QCheckBox, name="projectCheckBox").isChecked():
        upload_widget = self.get_upload_widget(
          project_widget.findChild(QtWidgets.QLabel, name="projectNameLabel").toolTip())
        self.uploadQueueVerticalLayout.addWidget(upload_widget["base"])
        widget = upload_widget["widget"]
        if not isinstance(widget, Ui_UploadWidgetFrame):
          continue
        project_id = project_widget.findChild(QtWidgets.QLabel, name="projectDocIdLabel").text()
        task_thread = TaskThreadExtension(
          DataUploadTask(widget.uploadProjectLabel.toolTip(),  # label text may be truncated,
                         #  but the tooltip contains the full project name
                         project_id,
                         widget.uploadProgressBar.setValue,
                         widget.statusLabel.setText,
                         widget.statusIconLabel.setPixmap,
                         widget.uploadCancelPushButton.clicked,
                         self.backend))
        self.upload_manager_task.add_to_queue(task_thread)
        if isinstance(task_thread.task, DataUploadTask):
          task_thread.task.upload_model_created.connect(widget.modelIdLabel.setText)
    self.upload_manager_task_thread.task.start.emit()

  def clear_finished(self) -> None:
    """
    Clears the finished upload widgets.
    Upload activity finishes in the following scenarios:
      Upload status is Finished, Error, Warning, or Canceled

    Explanation:
        This method clears the finished upload widgets from the upload queue.

    """
    for widget_pos in reversed(range(self.uploadQueueVerticalLayout.count())):
      project_widget = self.uploadQueueVerticalLayout.itemAt(widget_pos).widget()
      status_text = project_widget.findChild(QtWidgets.QLabel, name="statusLabel").text()
      if (status_text in [
        UploadStatusValues.Finished.name,
        UploadStatusValues.Error.name,
        UploadStatusValues.Warning.name,
        UploadStatusValues.Cancelled.name
      ]):
        project_widget.setParent(None)

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
    self.completed_uploads_dialog.show()

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

  def check_if_minimal_metadata_present(self) -> bool:
    """
    Checks if minimal metadata is present.

    Returns:
        bool: True if minimal metadata is present, False otherwise.

    Explanation:
        This function checks if minimal metadata is present in the configuration model.
        It returns True if minimal metadata is present, and False otherwise.
        If minimal metadata is missing, it displays a warning message to the user.
    """
    self.logger.info("Checking if minimal metadata is present...")
    config_model = self.db_api.get_config_model()
    metadata_exists = False
    if config_model is None:
      self.logger.error("Failed to load config model!")
      return metadata_exists
    if isinstance(config_model, ConfigModel) and isinstance(config_model.metadata, dict):
      if missing_metadata := check_if_minimal_metadata_exists(self.logger,
                                                              config_model.metadata,
                                                              False):
        message = get_formatted_message(missing_metadata)
        metadata_exists = message == ""
        if not metadata_exists:
          self.show_message(self.instance, "Missing Minimal Metadata", message)
    return metadata_exists

  def check_if_dataverse_is_configured(self) -> tuple[bool, str]:
    """
    Checks if dataverse is configured.

    Explanation:
        This function checks if the dataverse is configured by retrieving configuration details from the database.
        It validates the configuration, including the server URL, API token, and dataverse ID, and returns a success status.

    Returns:
        tuple[bool, str]: A tuple containing a boolean indicating success and a message string.
    """
    self.logger.info("Checking if dataverse is configured..")
    config_model = self.db_api.get_config_model()
    if config_model is None or config_model.dataverse_login_info is None:
      self.logger.error("Failed to load config model!")
      return False, "Failed to load config model!"
    server_url = config_model.dataverse_login_info["server_url"]
    api_token = config_model.dataverse_login_info["api_token"]
    dataverse_id = config_model.dataverse_login_info["dataverse_id"]
    success, _ = check_login_credentials(self.logger, api_token, server_url)
    if not success:
      return False, "Please re-enter the correct API token / server URL via the configuration dialog."
    if success := success and check_if_dataverse_exists(
        self.logger, api_token, server_url, dataverse_id):
      return success, "Dataverse configured successfully!"
    else:
      return False, f"Please re-enter the correct dataverse ID via the configuration dialog, Saved id: {dataverse_id} is incorrect!"

  def show(self) -> None:
    """
    Shows the instance.

    Explanation:
        This method shows the instance by calling its show method if the dataverse is configured.
        If the dataverse is not configured, it displays a message and shows the ConfigDialog.

    Args:
        self: The instance of the class.
    """
    self.logger.info("Show MainDialog UI..")
    if self.is_dataverse_configured[0]:
      self.instance.show()
    else:
      self.config_dialog = ConfigDialog()
      self.config_dialog.show()

  def show_message(self,
                   parent: QDialog,
                   title: str,
                   message: str,
                   icon: QMessageBox.Icon = QMessageBox.Icon.Warning) -> None:
    """
    Shows a message box with the specified title, message, and icon.

    Explanation:
        This function creates a message box with the provided title, message, and icon, and displays it to the user.
        It also adjusts the width of the message box label to fit the content properly.

    Args:
        self: The instance of the class.
        parent (QDialog): The parent dialog for the message box.
        title (str): The title of the message box.
        message (str): The message content to display.
        icon (QMessageBox.Icon, optional): The icon to display in the message box (default is QMessageBox.Warning).
    """

    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setIcon(icon or QMessageBox.Icon.Warning)
    msg_box.setText(message)
    qt_msgbox_label: QLabel | object = msg_box.findChild(QLabel, "qt_msgbox_label")
    if not isinstance(qt_msgbox_label, QLabel):
      self.logger.error("Failed to find message box label!")
      return
    width = qt_msgbox_label.fontMetrics().boundingRect(qt_msgbox_label.text()).width()
    qt_msgbox_label.setFixedWidth(width)
    msg_box.exec()
