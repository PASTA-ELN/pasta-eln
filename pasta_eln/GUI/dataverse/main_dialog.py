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

  def __new__(cls, *_: Any, **__: Any) -> Any:
    return super(MainDialog, cls).__new__(cls)

  def __init__(self) -> None:
    """
    Initializes the creation type dialog
    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = DialogExtension()
    super().setupUi(self.instance)
    self.db_api = DatabaseAPI()
    self.db_api.initialize_database()
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
    self.cancelAllPushButton.clicked.connect(lambda: self.upload_manager_task.cancel.emit())
    self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.close_ui)
    self.instance.closed.connect(self.close_ui)

  def get_upload_widget(self, project_name: str = "") -> dict[str, QFrame | Ui_UploadWidgetFrame]:
    uploadWidgetFrame = QtWidgets.QFrame()
    uploadWidgetUi = Ui_UploadWidgetFrame()
    uploadWidgetUi.setupUi(uploadWidgetFrame)
    uploadWidgetUi.uploadProjectLabel.setText(textwrap.fill(project_name, 45
                                                            , max_lines=1))
    uploadWidgetUi.uploadProjectLabel.setToolTip(project_name)
    uploadWidgetUi.statusIconLabel.setPixmap(qta.icon('ph.queue-light').pixmap(uploadWidgetUi.statusIconLabel.size()))
    uploadWidgetUi.logConsoleTextEdit.hide()
    uploadWidgetUi.showLogPushButton.clicked.connect(lambda: self.show_hide_log(uploadWidgetUi.showLogPushButton))
    uploadWidgetUi.modelIdLabel.hide()
    return {"base": uploadWidgetFrame, "widget": uploadWidgetUi}

  def get_project_widget(self, project: ProjectModel) -> QWidget:
    projectWidgetFrame = QtWidgets.QFrame()
    projectWidgetUi = Ui_ProjectItemFrame()
    projectWidgetUi.setupUi(projectWidgetFrame)
    projectWidgetUi.projectNameLabel.setText(textwrap.fill(project.name or "", width=80, max_lines=1))
    projectWidgetUi.projectNameLabel.setToolTip(project.name)
    projectWidgetUi.modifiedDateTimeLabel.setText(
      datetime.datetime.fromisoformat(project.date or "").strftime("%Y-%m-%d %H:%M:%S"))
    return projectWidgetFrame

  def start_upload(self) -> None:
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
    for widget_pos in reversed(range(self.uploadQueueVerticalLayout.count())):
      self.uploadQueueVerticalLayout.itemAt(widget_pos).widget().setParent(None)

  def select_deselect_all_projects(self, checked: bool) -> None:
    for widget_pos in range(self.projectsScrollAreaVerticalLayout.count()):
      project_widget = self.projectsScrollAreaVerticalLayout.itemAt(widget_pos).widget()
      project_widget.findChild(QtWidgets.QCheckBox, name="projectCheckBox").setChecked(checked)

  def show_configure_upload(self) -> None:
    self.config_upload_dialog.load_ui()
    self.config_upload_dialog.instance.show()

  def show_completed_uploads(self) -> None:
    self.completed_uploads_dialog.load_ui()
    self.completed_uploads_dialog.instance.show()

  def show_edit_metadata(self) -> None:
    self.edit_metadata_dialog.load_ui()
    self.edit_metadata_dialog.instance.show()

  def release_upload_manager(self) -> None:
    self.upload_manager_task_thread.quit()

  def close_ui(self) -> None:
    self.upload_manager_task_thread.quit()
    time.sleep(0.5)

  def show_hide_log(self, button: QtWidgets.QPushButton) -> None:
    frame = button.parent()
    log_console_text_edit = frame.findChild(QtWidgets.QTextEdit, name="logConsoleTextEdit")
    log_console_text_edit.show() if log_console_text_edit.isHidden() else log_console_text_edit.hide()
    if (upload_model_id :=
    frame.findChild(QtWidgets.QLabel, name="modelIdLabel").text()):
      model = self.db_api.get_model(upload_model_id, UploadModel)
      log_console_text_edit.setText(model.log if isinstance(model, UploadModel) else "")


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = MainDialog()
  ui.instance.show()
  sys.exit(app.exec())
