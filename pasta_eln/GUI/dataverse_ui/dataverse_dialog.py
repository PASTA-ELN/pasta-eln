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
import time
from typing import Any

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QFrame, QWidget

from pasta_eln.GUI.dataverse_ui.dataverse_dialog_base import Ui_DataverseDialogBase
from pasta_eln.GUI.dataverse_ui.dataverse_project_item_frame_base import Ui_ProjectItemFrame
from pasta_eln.GUI.dataverse_ui.dataverse_qt_dialog import DataverseQtDialog
from pasta_eln.GUI.dataverse_ui.dataverse_upload_config_dialog import DataverseUploadConfigDialog
from pasta_eln.GUI.dataverse_ui.dataverse_upload_widget_base import Ui_UploadWidgetFrame
from pasta_eln.dataverse.task_thread_abstraction import TaskThreadAbstraction
from pasta_eln.dataverse.upload_manager import UploadManager
from pasta_eln.dataverse.upload_task import UploadGenericTask


class DataverseDialog(Ui_DataverseDialogBase):

  def __new__(cls, *_: Any, **__: Any) -> Any:
    return super(DataverseDialog, cls).__new__(cls)

  def __init__(self) -> None:
    """
    Initializes the creation type dialog
    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = DataverseQtDialog()
    super().setupUi(self.instance)
    for i in range(300):
      widget = self.get_project_widget(f"Example Project {i + 1}")
      self.projectsScrollAreaVerticalLayout.addWidget(widget)
    self.uploadPushButton.clicked.connect(self.start_upload)
    self.clearFinishedPushButton.clicked.connect(self.clear_finished)
    self.selectAllPushButton.clicked.connect(lambda: self.select_deselect_all_projects(True))
    self.deselectAllPushButton.clicked.connect(lambda: self.select_deselect_all_projects(False))
    self.config_upload_dialog = DataverseUploadConfigDialog()
    self.configureUploadPushButton.clicked.connect(self.show_configure_upload)
    self.upload_manager_task = UploadManager()
    self.upload_manager_task_thread = TaskThreadAbstraction(self.upload_manager_task)
    self.cancelAllPushButton.clicked.connect(lambda: self.upload_manager_task.cancel.emit())
    self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(lambda : self.close_ui())
    self.instance.closed.connect(lambda: self.close_ui())

  def create_update_task(self,
                         widget: Ui_UploadWidgetFrame) -> TaskThreadAbstraction:
    return TaskThreadAbstraction(UploadGenericTask(widget))

  def get_upload_widget(self, project_name: str = 0) -> dict[str, QFrame | Ui_UploadWidgetFrame]:
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
    return {"base": uploadWidgetFrame, "widget": uploadWidgetUi}

  def get_project_widget(self, project_name: str = 0) -> QWidget:
    projectWidgetFrame = QtWidgets.QFrame()
    projectWidgetUi = Ui_ProjectItemFrame()
    projectWidgetUi.setupUi(projectWidgetFrame)
    projectWidgetUi.projectNameLabel.setText(project_name)
    projectWidgetUi.modifiedDateTimeLabel.setText(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return projectWidgetFrame

  def start_upload(self):
    print("Start upload...")
    for widget_pos in range(self.projectsScrollAreaVerticalLayout.count()):
      project_widget = self.projectsScrollAreaVerticalLayout.itemAt(widget_pos).widget()
      if project_widget.findChild(QtWidgets.QCheckBox, name="projectCheckBox").isChecked():
        upload_widget = self.get_upload_widget(
          project_widget.findChild(QtWidgets.QLabel, name="projectNameLabel").text())
        self.uploadQueueVerticalLayout.addWidget(upload_widget["base"])
        task = self.create_update_task(upload_widget["widget"])
        self.upload_manager_task.add_to_queue(task)
    self.upload_manager_task_thread.task.start.emit()

  def clear_finished(self):
    for widget_pos in reversed(range(self.uploadQueueVerticalLayout.count())):
      self.uploadQueueVerticalLayout.itemAt(widget_pos).widget().setParent(None)

  def select_deselect_all_projects(self, checked: bool):
    for widget_pos in range(self.projectsScrollAreaVerticalLayout.count()):
      project_widget = self.projectsScrollAreaVerticalLayout.itemAt(widget_pos).widget()
      project_widget.findChild(QtWidgets.QCheckBox, name="projectCheckBox").setChecked(checked)

  def show_configure_upload(self):
    self.config_upload_dialog.instance.show()

  def release_upload_manager(self):
    self.upload_manager_task_thread.quit()

  def close_ui(self):
    self.upload_manager_task_thread.quit()
    time.sleep(0.5)


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = DataverseDialog()
  ui.instance.show()
  sys.exit(app.exec())
