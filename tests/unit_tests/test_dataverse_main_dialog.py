#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_main_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import textwrap
from unittest.mock import MagicMock

import pytest
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QCheckBox, QLabel

from pasta_eln.GUI.dataverse.main_dialog import MainDialog
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.project_model import ProjectModel
from pasta_eln.dataverse.upload_model import UploadModel
from pasta_eln.dataverse.upload_status_values import UploadStatusValues


# Ensure QApplication instance exists for QWidget creation in tests
@pytest.fixture(scope="session", autouse=True)
def app():
  return QApplication([])


@pytest.fixture
def mock_main_dialog(mocker):
  mocker.patch("pasta_eln.GUI.dataverse.main_dialog_base.Ui_MainDialogBase.setupUi")
  mocker.patch("pasta_eln.GUI.dataverse.main_dialog.DatabaseAPI")
  mocker.patch("pasta_eln.GUI.dataverse.main_dialog.UploadConfigDialog")
  mocker.patch("pasta_eln.GUI.dataverse.main_dialog.CompletedUploads")
  mocker.patch("pasta_eln.GUI.dataverse.main_dialog.EditMetadataDialog")
  mocker.patch("pasta_eln.GUI.dataverse.main_dialog.UploadQueueManager")
  mocker.patch("pasta_eln.GUI.dataverse.main_dialog.TaskThreadExtension")
  mocker.patch("pasta_eln.GUI.dataverse.main_dialog.DialogExtension")
  mocker.patch("pasta_eln.GUI.dataverse.main_dialog.ConfigDialog")
  mocker.patch("pasta_eln.GUI.dataverse.main_dialog.logging")
  mocker.patch.object(MainDialog, "uploadPushButton", create=True)
  mocker.patch.object(MainDialog, "clearFinishedPushButton", create=True)
  mocker.patch.object(MainDialog, "selectAllPushButton", create=True)
  mocker.patch.object(MainDialog, "deselectAllPushButton", create=True)
  mocker.patch.object(MainDialog, "configureUploadPushButton", create=True)
  mocker.patch.object(MainDialog, "showCompletedPushButton", create=True)
  mocker.patch.object(MainDialog, "editFullMetadataPushButton", create=True)
  mocker.patch.object(MainDialog, "cancelAllPushButton", create=True)
  mocker.patch.object(MainDialog, "buttonBox", create=True)
  mocker.patch.object(MainDialog, "config_upload_dialog", create=True)
  mocker.patch(
    "pasta_eln.GUI.dataverse.main_dialog.MainDialog.check_if_dataverse_is_configured",
    return_value=(True, "Configured"))
  return MainDialog()


class TestDataverseMainDialog(object):

  @pytest.mark.parametrize("is_configured", [
    (True, "Configured"),
    (False, "Not Configured")
  ])
  def test_init_main_dialog(self, mocker, is_configured):
    # Arrange
    mock_setup_ui = mocker.patch("pasta_eln.GUI.dataverse.main_dialog_base.Ui_MainDialogBase.setupUi")
    mock_database_api = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.DatabaseAPI")
    mock_upload_config_dialog = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.UploadConfigDialog")
    mock_completed_uploads = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.CompletedUploads")
    mock_edit_metadata_dialog = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.EditMetadataDialog")
    mock_upload_queue_manager = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.UploadQueueManager")
    mock_task_thread_extension = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.TaskThreadExtension")
    mock_dialog_extension = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.DialogExtension")
    mocker.patch("pasta_eln.GUI.dataverse.main_dialog.ConfigDialog")
    mocker.patch("pasta_eln.GUI.dataverse.main_dialog.MainDialog.load_ui")
    mock_log = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.logging")
    mocker.patch.object(MainDialog, "uploadPushButton", create=True)
    mocker.patch.object(MainDialog, "clearFinishedPushButton", create=True)
    mocker.patch.object(MainDialog, "selectAllPushButton", create=True)
    mocker.patch.object(MainDialog, "deselectAllPushButton", create=True)
    mocker.patch.object(MainDialog, "configureUploadPushButton", create=True)
    mocker.patch.object(MainDialog, "showCompletedPushButton", create=True)
    mocker.patch.object(MainDialog, "editFullMetadataPushButton", create=True)
    mocker.patch.object(MainDialog, "cancelAllPushButton", create=True)
    mocker.patch.object(MainDialog, "buttonBox", create=True)
    mocker.patch.object(MainDialog, "config_upload_dialog", create=True)
    mock_check_if_dataverse_is_configured = mocker.patch(
      "pasta_eln.GUI.dataverse.main_dialog.MainDialog.check_if_dataverse_is_configured",
      return_value=is_configured)

    # Act
    dialog = MainDialog()

    # Assert
    mock_log.getLogger.assert_called_once_with("pasta_eln.GUI.dataverse.main_dialog.MainDialog")
    assert dialog.logger == mock_log.getLogger.return_value, "Logger is not set correctly"
    mock_dialog_extension.assert_called_once()
    assert dialog.instance == mock_dialog_extension.return_value, "Dialog instance is not set correctly"
    mock_setup_ui.assert_called_once_with(mock_dialog_extension.return_value)
    mock_database_api.assert_called_once()
    assert dialog.db_api == mock_database_api.return_value, "Database API is not set correctly"
    assert dialog.is_dataverse_configured == is_configured
    mock_check_if_dataverse_is_configured.assert_called_once()
    assert dialog.is_dataverse_configured == mock_check_if_dataverse_is_configured.return_value
    if is_configured[0]:
      mock_upload_config_dialog.assert_called_once()
      assert dialog.config_upload_dialog == mock_upload_config_dialog.return_value, "Config upload dialog is not set correctly"
      mock_completed_uploads.assert_called_once()
      assert dialog.completed_uploads_dialog == mock_completed_uploads.return_value, "Completed uploads dialog is not set correctly"
      mock_edit_metadata_dialog.assert_called_once()
      assert dialog.edit_metadata_dialog == mock_edit_metadata_dialog.return_value, "Edit metadata dialog is not set correctly"
      mock_upload_queue_manager.assert_called_once()
      assert dialog.upload_manager_task == mock_upload_queue_manager.return_value, "Upload queue manager is not set correctly"
      mock_task_thread_extension.assert_called_once_with(mock_upload_queue_manager.return_value)
      assert dialog.upload_manager_task_thread == mock_task_thread_extension.return_value, "Upload queue manager thread is not set correctly"

      dialog.uploadPushButton.clicked.connect.assert_called_once_with(dialog.start_upload)
      dialog.clearFinishedPushButton.clicked.connect.assert_called_once_with(dialog.clear_finished)
      dialog.selectAllPushButton.clicked.connect.assert_called_once()
      dialog.deselectAllPushButton.clicked.connect.assert_called_once()
      dialog.configureUploadPushButton.clicked.connect.assert_called_once_with(dialog.show_configure_upload)
      dialog.showCompletedPushButton.clicked.connect.assert_called_once_with(dialog.show_completed_uploads)
      dialog.editFullMetadataPushButton.clicked.connect.assert_called_once_with(dialog.show_edit_metadata)
      dialog.config_upload_dialog.config_reloaded.connect.assert_called_once_with(
        dialog.upload_manager_task.set_concurrent_uploads)
      dialog.cancelAllPushButton.clicked.connect.assert_called_once_with(dialog.upload_manager_task.cancel.emit)
      dialog.buttonBox.button.assert_called_once_with(QtWidgets.QDialogButtonBox.Cancel)
      dialog.buttonBox.button.return_value.clicked.connect.assert_called_once_with(dialog.close_ui)
      dialog.instance.closed.connect.assert_called_once_with(dialog.close_ui)
      dialog.load_ui.assert_called_once()
    else:
      # Assertions for the case when dataverse is not configured
      mock_upload_config_dialog.assert_not_called()
      mock_completed_uploads.assert_not_called()
      mock_edit_metadata_dialog.assert_not_called()
      mock_upload_queue_manager.assert_not_called()
      mock_task_thread_extension.assert_not_called()
      dialog.uploadPushButton.clicked.connect.assert_not_called()
      dialog.clearFinishedPushButton.clicked.connect.assert_not_called()
      dialog.selectAllPushButton.clicked.connect.assert_not_called()
      dialog.deselectAllPushButton.clicked.connect.assert_not_called()
      dialog.configureUploadPushButton.clicked.connect.assert_not_called()
      dialog.showCompletedPushButton.clicked.connect.assert_not_called()
      dialog.editFullMetadataPushButton.clicked.connect.assert_not_called()
      dialog.config_upload_dialog.config_reloaded.connect.assert_not_called()
      dialog.cancelAllPushButton.clicked.connect.assert_not_called()
      dialog.buttonBox.button.assert_not_called()
      dialog.buttonBox.button.return_value.clicked.connect.assert_not_called()
      dialog.instance.closed.connect.assert_not_called()
      dialog.load_ui.assert_not_called()

  # Parametrized test for happy path, edge cases, and error cases
  @pytest.mark.parametrize("project_models, expected_call_count", [
    ([ProjectModel()], 1),
    ([ProjectModel(), ProjectModel()], 2),
    ([], 0),
    # Assuming ProjectModel could potentially be subclassed or other models could be retrieved mistakenly
    (["not_a_project_model"], 0),
  ], ids=["success_path_single_project", "success_path_multiple_projects", "edge_case_no_projects",
          "error_case_non_project_model"])
  def test_load_ui(self, mocker, mock_main_dialog, project_models, expected_call_count):
    # Arrange
    mock_main_dialog.db_api.get_models = MagicMock(return_value=project_models)
    mock_main_dialog.get_project_widget = MagicMock()
    mock_main_dialog.projectsScrollAreaVerticalLayout = MagicMock()

    # Act
    mock_main_dialog.load_ui()

    # Assert
    mock_main_dialog.db_api.get_models.assert_called_once_with(ProjectModel)
    assert mock_main_dialog.get_project_widget.call_count == expected_call_count, f"get_project_widget should be called {expected_call_count} times"
    assert mock_main_dialog.projectsScrollAreaVerticalLayout.addWidget.call_count == expected_call_count, f"addWidget should be called {expected_call_count} times"
    mock_main_dialog.projectsScrollAreaVerticalLayout.addWidget.assert_has_calls(
      [mocker.call(mock_main_dialog.get_project_widget.return_value) for _ in range(expected_call_count)])

  @pytest.mark.parametrize("project_name,expected_label_text", [
    pytest.param("Short Project", "Short Project", id="happy_path_short_name"),
    pytest.param("A very long project name that exceeds the maximum length",
                 "A very long project name that exceeds the maximum length", id="happy_path_long_name"),
    pytest.param("", "", id="edge_case_empty_name"),
  ])
  def test_get_upload_widget(self, mocker, mock_main_dialog, project_name,
                             expected_label_text):
    # Arrange
    mock_frame = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.QtWidgets.QFrame")
    mock_upload_widget_frame = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.Ui_UploadWidgetFrame")
    mock_update_status = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.update_status")
    # Mocking external dependencies and inputs is already handled by decorators

    # Act
    result = mock_main_dialog.get_upload_widget(project_name)

    # Assert
    assert isinstance(result, dict), "The result should be a dictionary."
    assert "base" in result and "widget" in result, "The result dictionary should have 'base' and 'widget' keys."
    mock_frame.assert_called_once_with()
    mock_upload_widget_frame.assert_called_once()
    mock_upload_widget_frame.return_value.setupUi.assert_called_once_with(mock_frame.return_value)
    mock_upload_widget_frame.return_value.uploadProjectLabel.setText.assert_called_with(
      textwrap.fill(expected_label_text, 45, max_lines=1))
    mock_upload_widget_frame.return_value.uploadProjectLabel.setToolTip.assert_called_with(project_name)
    mock_upload_widget_frame.return_value.logConsoleTextEdit.hide.assert_called_once()
    mock_upload_widget_frame.return_value.modelIdLabel.hide.assert_called_once()
    mock_update_status.assert_called_once_with(UploadStatusValues.Queued.name,
                                               mock_upload_widget_frame.return_value.statusLabel.setText,
                                               mock_upload_widget_frame.return_value.statusIconLabel.setPixmap)
    mock_upload_widget_frame.return_value.showLogPushButton.clicked.connect.assert_called_once()

  @pytest.mark.parametrize("test_id, name, date, expected_name, expected_date", [
    # Happy path tests
    ("success-1", "Test Project", "2023-01-01T00:00:00", "Test Project", "2023-01-01 00:00:00"),
    ("success-2", "A" * 100, "2023-12-31T23:59:59", textwrap.fill("A" * 100, width=80, max_lines=1),
     "2023-12-31 23:59:59"),  # Test text wrapping
    # Edge cases
    ("edge-1", "", "2023-01-01T00:00:00", "", "2023-01-01 00:00:00"),  # Empty project name
    ("edge-2", "Test Project", "", ValueError, ValueError),  # Empty date
    # Error cases
    ("error-1", None, "2023-01-01T00:00:00", None, "2023-01-01 00:00:00"),  # None as project name
    ("error-2", "Test Project", "InvalidDate", ValueError, ValueError),  # Invalid date format
  ])
  def test_get_project_widget(self, mocker, mock_main_dialog, test_id, name, date, expected_name, expected_date):
    # Arrange
    mock_frame = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.QtWidgets.QFrame")
    mock_project_item_frame = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.Ui_ProjectItemFrame")
    project = ProjectModel()
    project.name = name
    project.date = date

    if expected_name is ValueError or expected_date is ValueError:
      # Assert
      with pytest.raises(expected_name):
        mock_main_dialog.get_project_widget(project)
    else:
      # Act
      widget = mock_main_dialog.get_project_widget(project)

      # Assert
      assert widget == mock_frame.return_value, f"{test_id}: The widget is not an instance of QFrame."
      mock_frame.assert_called_once()
      mock_project_item_frame.assert_called_once()
      mock_project_item_frame.return_value.setupUi.assert_called_once_with(widget)
      mock_project_item_frame.return_value.projectNameLabel.setText.assert_called_once_with(expected_name or '')
      mock_project_item_frame.return_value.modifiedDateTimeLabel.setText.assert_called_once_with(expected_date)
      mock_project_item_frame.return_value.projectNameLabel.setToolTip.assert_called_once_with(name)

  @pytest.mark.parametrize("metadata_present, project_checked, expected_warning, expected_upload", [
    (True, True, None, True),  # Success path: metadata present, project checked
    (True, False, None, False),  # Edge case: metadata present, project not checked
    (False, True, "Minimum metadata not present. Please add all needed metadata and then retry!", False),
    # Error case: metadata not present
  ], ids=["success-1-metadata-present-project-checked", "edge-1-metadata-present-project-not-checked",
          "error-1-metadata-not-present"])
  def test_start_upload(self, mocker, mock_main_dialog, metadata_present,
                        project_checked, expected_warning, expected_upload):
    # Arrange
    mock_data_upload_task = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.DataUploadTask")
    mock_task_thread = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.TaskThreadExtension")
    mock_is_instance = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.isinstance", return_value=True)
    mock_main_dialog.get_upload_widget = MagicMock(return_value={"base": MagicMock(), "widget": MagicMock()})
    mock_main_dialog.check_if_minimal_metadata_present = MagicMock()
    mock_main_dialog.check_if_minimal_metadata_present.return_value = metadata_present
    mock_main_dialog.projectsScrollAreaVerticalLayout = MagicMock()
    mock_main_dialog.projectsScrollAreaVerticalLayout.count.return_value = 1 if project_checked else 0
    mock_project_widget = MagicMock()
    mock_main_dialog.projectsScrollAreaVerticalLayout.itemAt.return_value.widget.return_value = mock_project_widget
    mock_checkbox = mocker.MagicMock(spec=QtWidgets.QCheckBox())
    mock_checkbox.isChecked.return_value = project_checked
    mock_project_widget.findChild.return_value = mock_checkbox if project_checked else None
    mock_main_dialog.uploadQueueVerticalLayout = MagicMock()
    mock_main_dialog.upload_manager_task_thread = MagicMock()
    mock_main_dialog.upload_manager_task = MagicMock()

    # Act
    mock_main_dialog.start_upload()

    # Assert
    mock_main_dialog.check_if_minimal_metadata_present.assert_called_once()
    if expected_warning:
      mock_main_dialog.logger.warning.assert_called_with(expected_warning)
    else:
      mock_main_dialog.logger.warning.assert_not_called()
      assert mock_main_dialog.upload_manager_task.add_to_queue.called == expected_upload
      if expected_upload:
        mock_main_dialog.projectsScrollAreaVerticalLayout.count.assert_called_once()
        mock_main_dialog.projectsScrollAreaVerticalLayout.itemAt.assert_called_once_with(0)
        mock_main_dialog.projectsScrollAreaVerticalLayout.itemAt.return_value.widget.assert_called_once()
        mock_project_widget.findChild.assert_any_call(QCheckBox, name="projectCheckBox")
        mock_project_widget.findChild.assert_any_call(QLabel, name="projectNameLabel")
        mock_project_widget.findChild.return_value.isChecked.assert_called_once()
        mock_project_widget.findChild.return_value.toolTip.assert_called_once()
        mock_main_dialog.get_upload_widget.assert_called_once_with(
          mock_project_widget.findChild.return_value.toolTip.return_value)
        mock_main_dialog.uploadQueueVerticalLayout.addWidget.assert_called_once_with(
          mock_main_dialog.get_upload_widget.return_value["base"])
        mock_data_upload_task.assert_called_once_with(
          mock_main_dialog.get_upload_widget.return_value["widget"].uploadProjectLabel.text(),
          mock_main_dialog.get_upload_widget.return_value["widget"].uploadProgressBar.setValue,
          mock_main_dialog.get_upload_widget.return_value["widget"].statusLabel.setText,
          mock_main_dialog.get_upload_widget.return_value["widget"].statusIconLabel.setPixmap,
          mock_main_dialog.get_upload_widget.return_value["widget"].uploadCancelPushButton.clicked
        )
        mock_task_thread.assert_called_once_with(mock_data_upload_task.return_value)
        mock_main_dialog.upload_manager_task.add_to_queue.assert_called_once_with(mock_task_thread.return_value)
        mock_is_instance.assert_called_once_with(mock_task_thread.return_value.task, mock_data_upload_task)
        mock_task_thread.return_value.task.upload_model_created.connectassert_called_once_with(
          mock_main_dialog.get_upload_widget.return_value["widget"].modelIdLabel.setText)
        mock_main_dialog.upload_manager_task_thread.task.start.emit.assert_called_once()

  @pytest.mark.parametrize("progress_value,status_text,expected_removal", [
    # ID: SuccessPath-1
    pytest.param(100, UploadStatusValues.Finished.name, True, id="SuccessPath-1"),
    # ID: SuccessPath-2
    pytest.param(100, UploadStatusValues.Error.name, True, id="SuccessPath-2"),
    # ID: EdgeCase-1 (Progress not 100)
    pytest.param(99, UploadStatusValues.Finished.name, False, id="EdgeCase-1"),
    # ID: EdgeCase-2 (Status not in specified list)
    pytest.param(100, "InProgress", False, id="EdgeCase-2"),
    # ID: ErrorCase-1 (Invalid status value)
    pytest.param(100, "InvalidStatus", False, id="ErrorCase-1"),
  ])
  def test_clear_finished(self, mocker, mock_main_dialog, progress_value, status_text, expected_removal):
    # Arrange
    mock_main_dialog.uploadQueueVerticalLayout = MagicMock()
    widget = MagicMock()
    progress_bar = mocker.MagicMock(spec=QtWidgets.QProgressBar())
    progress_bar.value.return_value = progress_value
    status_label = mocker.MagicMock(spec=QtWidgets.QLabel())
    status_label.text.return_value = status_text
    widget.findChild.side_effect = lambda x, name: progress_bar if x == QtWidgets.QProgressBar else status_label
    mock_main_dialog.uploadQueueVerticalLayout.count.return_value = 1
    mock_main_dialog.uploadQueueVerticalLayout.itemAt.return_value = MagicMock(widget=MagicMock(return_value=widget))

    # Act
    mock_main_dialog.clear_finished()

    # Assert
    mock_main_dialog.uploadQueueVerticalLayout.count.assert_called_once()
    if expected_removal:
      mock_main_dialog.uploadQueueVerticalLayout.itemAt.assert_called_once_with(0)
      mock_main_dialog.uploadQueueVerticalLayout.itemAt.return_value.widget.assert_called_once()
      widget.findChild.assert_any_call(QtWidgets.QProgressBar, name="uploadProgressBar")
      widget.findChild.assert_any_call(QtWidgets.QLabel, name="statusLabel")
      progress_bar.value.assert_called_once()
      status_label.text.assert_called_once()
      widget.setParent.assert_called_once_with(None)
    else:
      widget.setParent.assert_not_called()

  @pytest.mark.parametrize("checked, test_id", [
    (True, 'success_path_true'),
    (False, 'success_path_false'),
    (True, 'edge_case_single_project'),
    (False, 'edge_case_no_projects'),  # Assuming the function can handle an empty project list gracefully
    # Error cases are not explicitly defined here because the function does not include error handling.
    # If error handling is added to the function, corresponding tests should be added here.
  ])
  def test_select_deselect_all_projects(self, mocker, mock_main_dialog, checked, test_id, monkeypatch):
    # Arrange
    mock_layout = mocker.MagicMock(spec=QtWidgets.QVBoxLayout())
    mock_checkbox = mocker.MagicMock(spec=QtWidgets.QCheckBox())
    mock_widget = MagicMock()
    mock_widget.findChild.return_value = mock_checkbox
    mock_layout.count.return_value = 1 if test_id != 'edge_case_no_projects' else 0
    mock_layout.itemAt.return_value.widget.return_value = mock_widget if test_id != 'edge_case_no_projects' else None

    mock_main_dialog.projectsScrollAreaVerticalLayout = mock_layout

    # Act
    mock_main_dialog.select_deselect_all_projects(checked)

    # Assert
    if test_id != 'edge_case_no_projects':
      mock_layout.count.assert_called_once()  # Ensuring that the function is called only if there are projects present in mock_layout.count
      mock_layout.itemAt.assert_called_once_with(
        0)  # Ensuring that the function is called only if there are projects present in mock_layout.itemAt
      mock_widget.findChild.assert_called_once_with(QtWidgets.QCheckBox, name="projectCheckBox")
      mock_checkbox.setChecked.assert_called_once_with(checked)
    else:
      mock_layout.itemAt.assert_not_called()  # Ensuring no attempt to access widgets if none are present

  @pytest.mark.parametrize("test_id", [
    ("success_path"),
    # Add IDs for edge or error cases if there are any identifiable scenarios
  ])
  def test_show_configure_upload(self, test_id, mock_main_dialog):
    # Arrange - setup any state or prerequisites for the test
    mock_main_dialog.config_upload_dialog = MagicMock()

    # Act
    mock_main_dialog.show_configure_upload()

    # Assert
    mock_main_dialog.config_upload_dialog.load_ui.assert_called_once()
    mock_main_dialog.config_upload_dialog.instance.show.assert_called_once()

  @pytest.mark.parametrize("test_id", [
    ("success_path"),
    # Add IDs for edge or error cases if there are any identifiable scenarios
  ])
  def test_show_completed_uploads(self, test_id, mock_main_dialog):
    # Arrange - setup any state or prerequisites for the test
    mock_main_dialog.completed_uploads_dialog = MagicMock()

    # Act
    mock_main_dialog.show_completed_uploads()

    # Assert
    mock_main_dialog.completed_uploads_dialog.load_ui.assert_called_once()
    mock_main_dialog.completed_uploads_dialog.instance.show.assert_called_once()

  @pytest.mark.parametrize("test_id", ["success_path", "show_called_once"])
  def test_show_edit_metadata(self, mock_main_dialog, test_id):
    # Arrange
    mock_main_dialog.edit_metadata_dialog = MagicMock()

    # Act
    mock_main_dialog.show_edit_metadata()

    # Assert
    mock_main_dialog.edit_metadata_dialog.show.assert_called_once()

  @pytest.mark.parametrize("test_id", [
    ("success_path"),
    ("thread_already_quit"),
    ("thread_not_started")
  ])
  def test_release_upload_manager(self, mock_main_dialog, test_id):
    # Arrange
    mock_main_dialog.upload_manager_task_thread = MagicMock()

    if test_id == "thread_already_quit":
      mock_main_dialog.upload_manager_task_thread.quit.side_effect = RuntimeError("Thread already quit")
    elif test_id == "thread_not_started":
      mock_main_dialog.upload_manager_task_thread.quit.side_effect = RuntimeError("Thread not started")

    # Act
    try:
      mock_main_dialog.release_upload_manager()
      exception_raised = False
    except RuntimeError:
      exception_raised = True

    # Assert
    if test_id in ["thread_already_quit", "thread_not_started"]:
      assert exception_raised, f"Expected RuntimeError for {test_id}, but none was raised."
    else:
      mock_main_dialog.upload_manager_task_thread.quit.assert_called_once()

  @pytest.mark.parametrize("test_id", [
    ("success_path"),
    ("thread_already_stopped"),
    ("thread_stop_error")
  ])
  def test_close_ui(self, mocker, mock_main_dialog, test_id):
    # Arrange
    mock_sleep = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.time.sleep")
    mock_main_dialog.upload_manager_task_thread = MagicMock()

    if test_id == "thread_already_stopped":
      mock_main_dialog.upload_manager_task_thread.quit.side_effect = Exception("Thread already stopped")
    elif test_id == "thread_stop_error":
      mock_main_dialog.upload_manager_task_thread.quit.side_effect = Exception("Error stopping thread")

    # Act
    if test_id in ["success_path", "thread_already_stopped"]:
      try:
        mock_main_dialog.close_ui()
        exception_raised = False
      except Exception:
        exception_raised = True
    elif test_id == "thread_stop_error":
      with pytest.raises(Exception) as exc_info:
        mock_main_dialog.close_ui()
      assert str(exc_info.value) == "Error stopping thread", "Expected an error stopping thread exception"

    # Assert
    mock_main_dialog.upload_manager_task_thread.quit.assert_called_once()
    if test_id == "success_path":
      assert not exception_raised, "No exception should be raised on happy path"
      mock_sleep.assert_called_once_with(
        0.5)  # Ensuring that the function is called only if there are projects present in mock_layout.itemAt()
    elif test_id == "thread_already_stopped":
      assert exception_raised, "Expected an exception when the thread is already stopped"

  @pytest.mark.parametrize("initial_visibility,expected_visibility,model_id_exists,model_log", [
    # Test ID: Success Path 1 - Initially hidden, valid model ID
    (True, False, True, "Model log text\n"),
    # Test ID: Success Path 2 - Initially visible, valid model ID
    (False, True, True, "Different model log text\n"),
    # Test ID: Edge Case 1 - No model ID
    (True, False, False, ""),
    # Test ID: Edge Case 2 - Initially hidden, invalid model ID
    (True, False, True, ""),
  ])
  def test_show_hide_log(self, mocker, mock_main_dialog, initial_visibility, expected_visibility, model_id_exists,
                         model_log):
    # Arrange
    mock_isinstance = mocker.patch("pasta_eln.GUI.dataverse.main_dialog.isinstance", return_value=True)
    mock_button = mocker.MagicMock()
    mock_frame = mocker.MagicMock()
    mock_button.parent.return_value = mock_frame
    mock_text_edit = mocker.MagicMock()
    mock_text_edit.isHidden.return_value = initial_visibility
    mock_text_edit.hide.side_effect = lambda: mocker.patch.object(mock_text_edit, "isHidden", return_value=True)
    mock_text_edit.show.side_effect = lambda: mocker.patch.object(mock_text_edit, "isHidden", return_value=False)
    mock_frame.findChild.return_value = mock_text_edit if model_id_exists else None
    mock_label = mocker.MagicMock()
    mock_label.text.return_value = "valid_model_id" if model_id_exists else ""
    mock_frame.findChild.side_effect = [mock_text_edit, mock_label]
    mock_model = UploadModel()
    mock_model.log = model_log
    mock_main_dialog.db_api = mocker.MagicMock()
    mock_main_dialog.db_api.get_model.return_value = mock_model

    # Act
    mock_main_dialog.show_hide_log(mock_button)

    # Assert
    mock_button.parent.assert_called_once_with()
    mock_frame.findChild.assert_any_call(QtWidgets.QTextEdit, name="logConsoleTextEdit")
    mock_frame.findChild.assert_any_call(QtWidgets.QLabel, name="modelIdLabel")
    mock_isinstance.assert_any_call(mock_text_edit, QtWidgets.QTextEdit)
    mock_isinstance.assert_any_call(mock_label, QtWidgets.QLabel)
    mock_label.text.assert_called_once()

    assert mock_text_edit.isHidden() != initial_visibility
    mock_text_edit.isHidden.assert_called_once()
    if model_id_exists and model_log:
      mock_isinstance.assert_any_call(mock_model, UploadModel)
      mock_main_dialog.db_api.get_model.assert_called_with("valid_model_id", UploadModel)
      mock_text_edit.setText.assert_called_with(model_log)

  @pytest.mark.parametrize("config_model, expected_result, test_id", [
    (ConfigModel(metadata={"key": "value"}), True, "happy_path_with_valid_metadata"),
    (ConfigModel(metadata={}), False, "edge_case_with_empty_metadata"),
    (None, False, "error_case_with_no_config_model"),
  ])
  def test_check_if_minimal_metadata_present(self, mocker, config_model, mock_main_dialog, expected_result, test_id):
    # Arrange
    mock_main_dialog.db_api.get_config_model = mocker.MagicMock(return_value=config_model)
    mock_main_dialog.show_message = mocker.MagicMock()
    mock_get_formatted_message = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.get_formatted_message',
                                              return_value="" if expected_result else "Missing1, Missing2")
    mock_check_if_minimal_metadata_exists = mocker.patch(
      'pasta_eln.GUI.dataverse.main_dialog.check_if_minimal_metadata_exists',
      return_value={'title': [],
                    'author': [],
                    'datasetContact': [],
                    'dsDescription': [],
                    'subject': []
                    } if expected_result else {
        'title': ["Missing1"],
        'author': ["Missing2"],
        'datasetContact': [],
        'dsDescription': [],
        'subject': []
      })

    # Act
    result = mock_main_dialog.check_if_minimal_metadata_present()

    # Assert
    mock_main_dialog.logger.info.assert_called_once_with("Checking if minimal metadata is present...")
    assert result == expected_result, f"Test Failed for {test_id}"
    mock_main_dialog.db_api.get_config_model.assert_called_once()
    if not expected_result:
      if config_model is None:
        mock_main_dialog.logger.error.assert_called_once_with("Failed to load config model!")
      else:
        mock_check_if_minimal_metadata_exists.assert_called_once_with(mock_main_dialog.logger, config_model.metadata,
                                                                      False)
        mock_get_formatted_message.assert_called_once_with(mock_check_if_minimal_metadata_exists.return_value)
        mock_main_dialog.show_message.assert_called_once_with(mock_main_dialog.instance, "Missing Minimal Metadata",
                                                              mock_get_formatted_message.return_value)
    else:
      mock_main_dialog.show_message.assert_not_called()
