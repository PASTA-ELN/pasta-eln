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
from PySide6.QtWidgets import QCheckBox, QLabel, QMessageBox

from pasta_eln.GUI.dataverse.main_dialog import MainDialog
from pasta_eln.GUI.dataverse.upload_widget_base import Ui_UploadWidgetFrame
from pasta_eln.database.models.config_model import ConfigModel
from pasta_eln.database.models.project_model import ProjectModel
from pasta_eln.database.models.upload_model import UploadModel
from pasta_eln.dataverse.upload_status_values import UploadStatusValues

actual_check_if_dataverse_is_configured = MainDialog.check_if_dataverse_is_configured


@pytest.fixture
def mock_main_dialog(mocker):
  mocker.patch('pasta_eln.GUI.dataverse.main_dialog_base.Ui_MainDialogBase.setupUi')
  mocker.patch('pasta_eln.GUI.dataverse.main_dialog.DatabaseAPI')
  mocker.patch('pasta_eln.GUI.dataverse.main_dialog.UploadConfigDialog')
  mocker.patch('pasta_eln.GUI.dataverse.main_dialog.CompletedUploads')
  mocker.patch('pasta_eln.GUI.dataverse.main_dialog.EditMetadataDialog')
  mocker.patch('pasta_eln.GUI.dataverse.main_dialog.UploadQueueManager')
  mocker.patch('pasta_eln.GUI.dataverse.main_dialog.TaskThreadExtension')
  mocker.patch('pasta_eln.GUI.dataverse.main_dialog.DialogExtension')
  mocker.patch('pasta_eln.GUI.dataverse.main_dialog.ConfigDialog')
  mocker.patch('pasta_eln.GUI.dataverse.main_dialog.logging')
  mocker.patch.object(MainDialog, 'uploadPushButton', create=True)
  mocker.patch.object(MainDialog, 'clearFinishedPushButton', create=True)
  mocker.patch.object(MainDialog, 'selectAllPushButton', create=True)
  mocker.patch.object(MainDialog, 'deselectAllPushButton', create=True)
  mocker.patch.object(MainDialog, 'configureUploadPushButton', create=True)
  mocker.patch.object(MainDialog, 'showCompletedPushButton', create=True)
  mocker.patch.object(MainDialog, 'editFullMetadataPushButton', create=True)
  mocker.patch.object(MainDialog, 'cancelAllPushButton', create=True)
  mocker.patch.object(MainDialog, 'buttonBox', create=True)
  mocker.patch.object(MainDialog, 'config_upload_dialog', create=True)
  mocker.patch(
    'pasta_eln.GUI.dataverse.main_dialog.MainDialog.check_if_dataverse_is_configured',
    return_value=(True, 'Configured'))
  mock_backed = mocker.MagicMock()
  return MainDialog(mock_backed)


class TestDataverseMainDialog:

  @pytest.mark.parametrize('is_configured', [
    (True, 'Configured'),
    (False, 'Not Configured')
  ])
  def test_init_main_dialog(self, mocker, is_configured):
    # Arrange
    mock_setup_ui = mocker.patch('pasta_eln.GUI.dataverse.main_dialog_base.Ui_MainDialogBase.setupUi')
    mock_database_api = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.DatabaseAPI')
    mock_upload_config_dialog = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.UploadConfigDialog')
    mock_completed_uploads = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.CompletedUploads')
    mock_edit_metadata_dialog = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.EditMetadataDialog')
    mock_upload_queue_manager = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.UploadQueueManager')
    mock_task_thread_extension = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.TaskThreadExtension')
    mock_dialog_extension = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.DialogExtension')
    mocker.patch('pasta_eln.GUI.dataverse.main_dialog.ConfigDialog')
    mocker.patch('pasta_eln.GUI.dataverse.main_dialog.MainDialog.load_ui')
    mock_log = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.logging')
    mocker.patch.object(MainDialog, 'uploadPushButton', create=True)
    mocker.patch.object(MainDialog, 'clearFinishedPushButton', create=True)
    mocker.patch.object(MainDialog, 'selectAllPushButton', create=True)
    mocker.patch.object(MainDialog, 'deselectAllPushButton', create=True)
    mocker.patch.object(MainDialog, 'configureUploadPushButton', create=True)
    mocker.patch.object(MainDialog, 'showCompletedPushButton', create=True)
    mocker.patch.object(MainDialog, 'editFullMetadataPushButton', create=True)
    mocker.patch.object(MainDialog, 'cancelAllPushButton', create=True)
    mocker.patch.object(MainDialog, 'buttonBox', create=True)
    mocker.patch.object(MainDialog, 'config_upload_dialog', create=True)
    mock_check_if_dataverse_is_configured = mocker.patch(
      'pasta_eln.GUI.dataverse.main_dialog.MainDialog.check_if_dataverse_is_configured',
      return_value=is_configured)
    mock_backed = mocker.MagicMock()

    # Act
    dialog = MainDialog(mock_backed)

    # Assert
    mock_log.getLogger.assert_called_once_with('pasta_eln.GUI.dataverse.main_dialog.MainDialog')
    assert dialog.logger == mock_log.getLogger.return_value, 'Logger is not set correctly'
    mock_dialog_extension.assert_called_once()
    assert dialog.instance == mock_dialog_extension.return_value, 'Dialog instance is not set correctly'
    mock_setup_ui.assert_called_once_with(mock_dialog_extension.return_value)
    mock_database_api.assert_called_once()
    assert dialog.db_api == mock_database_api.return_value, 'Database API is not set correctly'
    assert dialog.is_dataverse_configured == is_configured
    dialog.db_api.initialize_database.assert_called_once()
    mock_check_if_dataverse_is_configured.assert_called_once()
    assert dialog.is_dataverse_configured == mock_check_if_dataverse_is_configured.return_value
    if is_configured[0]:
      mock_upload_config_dialog.assert_called_once()
      assert dialog.config_upload_dialog == mock_upload_config_dialog.return_value, 'Config upload dialog is not set correctly'
      mock_completed_uploads.assert_called_once()
      assert dialog.completed_uploads_dialog == mock_completed_uploads.return_value, 'Completed uploads dialog is not set correctly'
      mock_edit_metadata_dialog.assert_called_once()
      assert dialog.edit_metadata_dialog == mock_edit_metadata_dialog.return_value, 'Edit metadata dialog is not set correctly'
      mock_upload_queue_manager.assert_called_once()
      assert dialog.upload_manager_task == mock_upload_queue_manager.return_value, 'Upload queue manager is not set correctly'
      mock_task_thread_extension.assert_called_once_with(mock_upload_queue_manager.return_value)
      assert dialog.upload_manager_task_thread == mock_task_thread_extension.return_value, 'Upload queue manager thread is not set correctly'

      dialog.config_upload_dialog.config_reloaded.connect.assert_any_call(
        dialog.upload_manager_task.set_concurrent_uploads)
      dialog.config_upload_dialog.config_reloaded.connect.assert_any_call(dialog.edit_metadata_dialog.reload_config)
      dialog.uploadPushButton.clicked.connect.assert_called_once_with(dialog.start_upload)
      dialog.clearFinishedPushButton.clicked.connect.assert_called_once_with(dialog.clear_finished)
      dialog.selectAllPushButton.clicked.connect.assert_called_once()
      dialog.deselectAllPushButton.clicked.connect.assert_called_once()
      dialog.configureUploadPushButton.clicked.connect.assert_called_once_with(dialog.show_configure_upload)
      dialog.showCompletedPushButton.clicked.connect.assert_called_once_with(dialog.show_completed_uploads)
      dialog.editFullMetadataPushButton.clicked.connect.assert_called_once_with(dialog.show_edit_metadata)
      dialog.cancelAllPushButton.clicked.connect.assert_called_once_with(
        dialog.upload_manager_task.cancel_all_tasks.emit)
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
      dialog.config_upload_dialog.config_reloaded.connect.assert_not_called()
      dialog.config_upload_dialog.config_reloaded.connect.assert_not_called()
      dialog.uploadPushButton.clicked.connect.assert_not_called()
      dialog.clearFinishedPushButton.clicked.connect.assert_not_called()
      dialog.selectAllPushButton.clicked.connect.assert_not_called()
      dialog.deselectAllPushButton.clicked.connect.assert_not_called()
      dialog.configureUploadPushButton.clicked.connect.assert_not_called()
      dialog.showCompletedPushButton.clicked.connect.assert_not_called()
      dialog.editFullMetadataPushButton.clicked.connect.assert_not_called()
      dialog.cancelAllPushButton.clicked.connect.assert_not_called()
      dialog.buttonBox.button.assert_not_called()
      dialog.buttonBox.button.return_value.clicked.connect.assert_not_called()
      dialog.instance.closed.connect.assert_not_called()
      dialog.load_ui.assert_not_called()

  # Parametrized test for happy path, edge cases, and error cases
  @pytest.mark.parametrize('project_models, expected_call_count', [
    ([ProjectModel()], 1),
    ([ProjectModel(), ProjectModel()], 2),
    ([], 0),
    # Assuming ProjectModel could potentially be subclassed or other models could be retrieved mistakenly
    (['not_a_project_model'], 0),
  ], ids=['success_path_single_project', 'success_path_multiple_projects', 'edge_case_no_projects',
          'error_case_non_project_model'])
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

  @pytest.mark.parametrize('project_name,expected_label_text', [
    pytest.param('Short Project', 'Short Project', id='happy_path_short_name'),
    pytest.param('A very long project name that exceeds the maximum length',
                 'A very long project name that exceeds the maximum length', id='happy_path_long_name'),
    pytest.param('', '', id='edge_case_empty_name'),
  ])
  def test_get_upload_widget(self, mocker, mock_main_dialog, project_name,
                             expected_label_text):
    # Arrange
    mock_frame = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.QtWidgets.QFrame')
    mock_upload_widget_frame = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.Ui_UploadWidgetFrame')
    mock_update_status = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.update_status')
    # Mocking external dependencies and inputs is already handled by decorators

    # Act
    result = mock_main_dialog.get_upload_widget(project_name)

    # Assert
    assert isinstance(result, dict), 'The result should be a dictionary.'
    assert 'base' in result and 'widget' in result, "The result dictionary should have 'base' and 'widget' keys."
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

  @pytest.mark.parametrize(
    'test_id, name, date_created, date_modified, expected_name, expected_date_created, expected_date_modified', [
      # Happy path tests
      ('success-1', 'Test Project', '2023-01-01T00:00:00', '2023-01-01T00:00:00', 'Test Project', '2023-01-01 00:00:00',
       '2023-01-01 00:00:00'),
      ('success-2', 'A' * 100, '2023-12-31T23:59:59', '2023-12-31T23:59:59',
       textwrap.fill('A' * 100, width=80, max_lines=1),
       '2023-12-31 23:59:59', '2023-12-31 23:59:59'),  # Test text wrapping
      # Edge cases
      ('edge-1', '', '2023-01-01T00:00:00', '2023-01-01T00:00:00', '', '2023-01-01 00:00:00', '2023-01-01 00:00:00'),
      # Empty project name
      ('edge-2', 'Test Project', '', '', ValueError, ValueError, ValueError),  # Empty date
      # Error cases
      ('error-1', None, '2023-01-01T00:00:00', '2023-01-01T00:00:00', None, '2023-01-01 00:00:00',
       '2023-01-01 00:00:00'),  # None as project name
      ('error-2', 'Test Project', 'InvalidDate', 'InvalidDate', ValueError, ValueError, ValueError),
      # Invalid date format
    ])
  def test_get_project_widget(self, mocker, mock_main_dialog, test_id, name, date_created, date_modified, expected_name,
                              expected_date_created, expected_date_modified):
    # Arrange
    mock_frame = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.QtWidgets.QFrame')
    mock_project_item_frame = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.Ui_ProjectItemFrame')
    project = ProjectModel()
    project.name = name
    project.date_created = date_created
    project.date_modified = date_modified
    project.id = 'Test'

    if expected_name is ValueError or expected_date_created is ValueError:
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
      mock_project_item_frame.return_value.modifiedDateTimeLabel.setText.assert_called_once_with(expected_date_modified)
      mock_project_item_frame.return_value.projectNameLabel.setToolTip.assert_called_once_with(name)
      mock_project_item_frame.return_value.projectDocIdLabel.hide.assert_called_once()
      mock_project_item_frame.return_value.projectDocIdLabel.setText.assert_called_once_with(project.id)

  @pytest.mark.parametrize('project, expected_exception', [
    # ID: ErrorCase-1 (invalid project type)
    (MagicMock(), ValueError),
    # ID: ErrorCase-2 (invalid date format)
    ({'name': 'Test Project', 'date': 'Invalid Date Format'}, ValueError),
  ])
  def test_get_project_widget_error_cases(self, project, mock_main_dialog, expected_exception):
    # No Arrange section needed as input values are provided via test parameters

    # Act & Assert
    with pytest.raises(expected_exception):
      mock_main_dialog.get_project_widget(project)

  @pytest.mark.parametrize('metadata_present, project_checked, expected_warning, expected_upload', [
    (True, True, None, True),  # Success path: metadata present, project checked
    (True, False, None, False),  # Edge case: metadata present, project not checked
    (False, True, 'Minimum metadata not present. Please add all needed metadata and then retry!', False),
    # Error case: metadata not present
  ], ids=['success-1-metadata-present-project-checked', 'edge-1-metadata-present-project-not-checked',
          'error-1-metadata-not-present'])
  def test_start_upload(self, mocker, mock_main_dialog, metadata_present,
                        project_checked, expected_warning, expected_upload):
    # Arrange
    mock_data_upload_task = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.DataUploadTask')
    mock_task_thread = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.TaskThreadExtension')
    mock_is_instance = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.isinstance', return_value=True)
    mock_main_dialog.get_upload_widget = MagicMock(return_value={'base': MagicMock(), 'widget': MagicMock()})
    mock_main_dialog.check_if_minimal_metadata_present = MagicMock()
    mock_main_dialog.check_if_minimal_metadata_present.return_value = metadata_present
    mock_main_dialog.projectsScrollAreaVerticalLayout = MagicMock()
    mock_main_dialog.projectsScrollAreaVerticalLayout.count.return_value = 1 if project_checked else 0
    mock_project_widget = MagicMock()
    mock_main_dialog.projectsScrollAreaVerticalLayout.itemAt.return_value.widget.return_value = mock_project_widget
    mock_checkbox = mocker.MagicMock()
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
        mock_project_widget.findChild.assert_any_call(QCheckBox, name='projectCheckBox')
        mock_project_widget.findChild.assert_any_call(QLabel, name='projectNameLabel')
        mock_project_widget.findChild.assert_any_call(QLabel, name='projectDocIdLabel')
        mock_project_widget.findChild.return_value.isChecked.assert_called_once()
        mock_project_widget.findChild.return_value.toolTip.assert_called_once()
        mock_main_dialog.get_upload_widget.assert_called_once_with(
          mock_project_widget.findChild.return_value.toolTip.return_value)
        mock_main_dialog.uploadQueueVerticalLayout.addWidget.assert_called_once_with(
          mock_main_dialog.get_upload_widget.return_value['base'])
        mock_data_upload_task.assert_called_once_with(
          mock_main_dialog.get_upload_widget.return_value['widget'].uploadProjectLabel.toolTip(),
          mock_project_widget.findChild.return_value.text(),
          mock_main_dialog.get_upload_widget.return_value['widget'].uploadProgressBar.setValue,
          mock_main_dialog.get_upload_widget.return_value['widget'].statusLabel.setText,
          mock_main_dialog.get_upload_widget.return_value['widget'].statusIconLabel.setPixmap,
          mock_main_dialog.get_upload_widget.return_value['widget'].uploadCancelPushButton.clicked,
          mock_main_dialog.backend
        )
        mock_task_thread.assert_called_once_with(mock_data_upload_task.return_value)
        mock_main_dialog.upload_manager_task.add_to_queue.assert_called_once_with(mock_task_thread.return_value)
        mock_is_instance.assert_any_call(mock_task_thread.return_value.task, mock_data_upload_task)
        mock_is_instance.assert_any_call(mock_main_dialog.get_upload_widget.return_value['widget'],
                                         Ui_UploadWidgetFrame)
        mock_task_thread.return_value.task.upload_model_created.connectassert_called_once_with(
          mock_main_dialog.get_upload_widget.return_value['widget'].modelIdLabel.setText)
        mock_main_dialog.upload_manager_task_thread.task.start.emit.assert_called_once()

  @pytest.mark.parametrize('progress_value,status_text,expected_removal', [
    # ID: SuccessPath-1
    pytest.param(100, UploadStatusValues.Finished.name, True, id='SuccessPath-1-finished-with-100-progress'),
    # ID: SuccessPath-2
    pytest.param(100, UploadStatusValues.Error.name, True, id='SuccessPath-2-error-with-100-progress'),
    # ID: SuccessPath-3
    pytest.param(0, UploadStatusValues.Cancelled.name, True, id='SuccessPath-3-cancelled-with-0-progress'),
    # ID: SuccessPath-4
    pytest.param(100, UploadStatusValues.Cancelled.name, True, id='SuccessPath-4-cancelled-with-100-progress'),
    # ID: EdgeCase-1 (Status not in a specified list)
    pytest.param(100, 'InProgress', False, id='EdgeCase-1'),
    # ID: ErrorCase-1 (Invalid status value)
    pytest.param(100, 'InvalidStatus', False, id='ErrorCase-1'),
  ])
  def test_clear_finished(self, mocker, mock_main_dialog, progress_value, status_text, expected_removal):
    # Arrange
    mock_main_dialog.uploadQueueVerticalLayout = MagicMock()
    widget = MagicMock()
    status_label = mocker.MagicMock()
    status_label.text.return_value = status_text
    widget.findChild.side_effect = lambda x, name: status_label
    mock_main_dialog.uploadQueueVerticalLayout.count.return_value = 1
    mock_main_dialog.uploadQueueVerticalLayout.itemAt.return_value = MagicMock(widget=MagicMock(return_value=widget))

    # Act
    mock_main_dialog.clear_finished()

    # Assert
    mock_main_dialog.uploadQueueVerticalLayout.count.assert_called_once()
    if expected_removal:
      mock_main_dialog.uploadQueueVerticalLayout.itemAt.assert_called_once_with(0)
      mock_main_dialog.uploadQueueVerticalLayout.itemAt.return_value.widget.assert_called_once()
      widget.findChild.assert_any_call(QtWidgets.QLabel, name='statusLabel')
      status_label.text.assert_called_once()
      widget.setParent.assert_called_once_with(None)
    else:
      widget.setParent.assert_not_called()

  @pytest.mark.parametrize('checked, test_id', [
    (True, 'success_path_true'),
    (False, 'success_path_false'),
    (True, 'edge_case_single_project'),
    (False, 'edge_case_no_projects'),  # Assuming the function can handle an empty project list gracefully
    # Error cases are not explicitly defined here because the function does not include error handling.
    # If error handling is added to the function, corresponding tests should be added here.
  ])
  def test_select_deselect_all_projects(self, mocker, mock_main_dialog, checked, test_id, monkeypatch):
    # Arrange
    mock_layout = mocker.MagicMock()
    mock_checkbox = mocker.MagicMock()
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
      mock_widget.findChild.assert_called_once_with(QtWidgets.QCheckBox, name='projectCheckBox')
      mock_checkbox.setChecked.assert_called_once_with(checked)
    else:
      mock_layout.itemAt.assert_not_called()  # Ensuring no attempt to access widgets if none are present

  @pytest.mark.parametrize('test_id', [
    ('success_path'),
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

  @pytest.mark.parametrize('test_id', [
    ('success_path'),
    # Add IDs for edge or error cases if there are any identifiable scenarios
  ])
  def test_show_completed_uploads(self, test_id, mock_main_dialog):
    # Arrange - setup any state or prerequisites for the test
    mock_main_dialog.completed_uploads_dialog = MagicMock()

    # Act
    mock_main_dialog.show_completed_uploads()

    # Assert
    mock_main_dialog.completed_uploads_dialog.show.assert_called_once()

  @pytest.mark.parametrize('test_id', ['success_path', 'show_called_once'])
  def test_show_edit_metadata(self, mock_main_dialog, test_id):
    # Arrange
    mock_main_dialog.edit_metadata_dialog = MagicMock()

    # Act
    mock_main_dialog.show_edit_metadata()

    # Assert
    mock_main_dialog.edit_metadata_dialog.show.assert_called_once()

  @pytest.mark.parametrize('test_id', [
    ('success_path'),
    ('thread_already_quit'),
    ('thread_not_started')
  ])
  def test_release_upload_manager(self, mock_main_dialog, test_id):
    # Arrange
    mock_main_dialog.upload_manager_task_thread = MagicMock()

    if test_id == 'thread_already_quit':
      mock_main_dialog.upload_manager_task_thread.quit.side_effect = RuntimeError('Thread already quit')
    elif test_id == 'thread_not_started':
      mock_main_dialog.upload_manager_task_thread.quit.side_effect = RuntimeError('Thread not started')

    # Act
    try:
      mock_main_dialog.release_upload_manager()
      exception_raised = False
    except RuntimeError:
      exception_raised = True

    # Assert
    if test_id in ['thread_already_quit', 'thread_not_started']:
      assert exception_raised, f"Expected RuntimeError for {test_id}, but none was raised."
    else:
      mock_main_dialog.upload_manager_task_thread.quit.assert_called_once()

  @pytest.mark.parametrize('test_id', [
    ('success_path'),
    ('thread_already_stopped'),
    ('thread_stop_error')
  ])
  def test_close_ui(self, mocker, mock_main_dialog, test_id):
    # Arrange
    mock_sleep = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.time.sleep')
    mock_main_dialog.upload_manager_task_thread = MagicMock()

    if test_id == 'thread_already_stopped':
      mock_main_dialog.upload_manager_task_thread.quit.side_effect = Exception('Thread already stopped')
    elif test_id == 'thread_stop_error':
      mock_main_dialog.upload_manager_task_thread.quit.side_effect = Exception('Error stopping thread')

    # Act
    if test_id in ['success_path', 'thread_already_stopped']:
      try:
        mock_main_dialog.close_ui()
        exception_raised = False
      except Exception:
        exception_raised = True
    elif test_id == 'thread_stop_error':
      with pytest.raises(Exception) as exc_info:
        mock_main_dialog.close_ui()
      assert str(exc_info.value) == 'Error stopping thread', 'Expected an error stopping thread exception'

    # Assert
    mock_main_dialog.upload_manager_task_thread.quit.assert_called_once()
    if test_id == 'success_path':
      assert not exception_raised, 'No exception should be raised on happy path'
      mock_sleep.assert_called_once_with(
        0.5)  # Ensuring that the function is called only if there are projects present in mock_layout.itemAt()
    elif test_id == 'thread_already_stopped':
      assert exception_raised, 'Expected an exception when the thread is already stopped'

  @pytest.mark.parametrize('initial_visibility,expected_visibility,model_id_exists,model_log', [
    # Test ID: Success Path 1 - Initially hidden, valid model ID
    (True, False, True, 'Model log text\n'),
    # Test ID: Success Path 2 - Initially visible, valid model ID
    (False, True, True, 'Different model log text\n'),
    # Test ID: Edge Case 1 - No model ID
    (True, False, False, ''),
    # Test ID: Edge Case 2 - Initially hidden, invalid model ID
    (True, False, True, ''),
  ])
  def test_show_hide_log(self, mocker, mock_main_dialog, initial_visibility, expected_visibility, model_id_exists,
                         model_log):
    # Arrange
    mock_isinstance = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.isinstance', return_value=True)
    mock_button = mocker.MagicMock()
    mock_frame = mocker.MagicMock()
    mock_button.parent.return_value = mock_frame
    mock_text_edit = mocker.MagicMock()
    mock_text_edit.isHidden.return_value = initial_visibility
    mock_text_edit.hide.side_effect = lambda: mocker.patch.object(mock_text_edit, 'isHidden', return_value=True)
    mock_text_edit.show.side_effect = lambda: mocker.patch.object(mock_text_edit, 'isHidden', return_value=False)
    mock_frame.findChild.return_value = mock_text_edit if model_id_exists else None
    mock_label = mocker.MagicMock()
    mock_label.text.return_value = 'valid_model_id' if model_id_exists else ''
    mock_frame.findChild.side_effect = [mock_text_edit, mock_label]
    mock_model = UploadModel()
    mock_model.log = model_log
    mock_main_dialog.db_api = mocker.MagicMock()
    mock_main_dialog.db_api.get_model.return_value = mock_model

    # Act
    mock_main_dialog.show_hide_log(mock_button)

    # Assert
    mock_button.parent.assert_called_once_with()
    mock_frame.findChild.assert_any_call(QtWidgets.QTextEdit, name='logConsoleTextEdit')
    mock_frame.findChild.assert_any_call(QtWidgets.QLabel, name='modelIdLabel')
    mock_isinstance.assert_any_call(mock_text_edit, QtWidgets.QTextEdit)
    mock_isinstance.assert_any_call(mock_label, QtWidgets.QLabel)
    mock_label.text.assert_called_once()

    assert mock_text_edit.isHidden() != initial_visibility
    mock_text_edit.isHidden.assert_called_once()
    if model_id_exists and model_log:
      mock_isinstance.assert_any_call(mock_model, UploadModel)
      mock_main_dialog.db_api.get_model.assert_called_with('valid_model_id', UploadModel)
      mock_text_edit.setText.assert_called_with(model_log)

  @pytest.mark.parametrize('config_model, expected_result, test_id', [
    (ConfigModel(metadata={'key': 'value'}), True, 'happy_path_with_valid_metadata'),
    (ConfigModel(metadata={}), False, 'edge_case_with_empty_metadata'),
    (None, False, 'error_case_with_no_config_model'),
  ])
  def test_check_if_minimal_metadata_present(self, mocker, config_model, mock_main_dialog, expected_result, test_id):
    # Arrange
    mock_main_dialog.db_api.get_config_model = mocker.MagicMock(return_value=config_model)
    mock_main_dialog.show_message = mocker.MagicMock()
    mock_get_formatted_message = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.get_formatted_message',
                                              return_value='' if expected_result else 'Missing1, Missing2')
    mock_check_if_minimal_metadata_exists = mocker.patch(
      'pasta_eln.GUI.dataverse.main_dialog.check_if_minimal_metadata_exists',
      return_value={'title': [],
                    'author': [],
                    'datasetContact': [],
                    'dsDescription': [],
                    'subject': []
                    } if expected_result else {
        'title': ['Missing1'],
        'author': ['Missing2'],
        'datasetContact': [],
        'dsDescription': [],
        'subject': []
      })

    # Act
    result = mock_main_dialog.check_if_minimal_metadata_present()

    # Assert
    mock_main_dialog.logger.info.assert_called_once_with('Checking if minimal metadata is present...')
    assert result == expected_result, f"Test Failed for {test_id}"
    mock_main_dialog.db_api.get_config_model.assert_called_once()
    if not expected_result:
      if config_model is None:
        mock_main_dialog.logger.error.assert_called_once_with('Failed to load config model!')
      else:
        mock_check_if_minimal_metadata_exists.assert_called_once_with(mock_main_dialog.logger, config_model.metadata,
                                                                      False)
        mock_get_formatted_message.assert_called_once_with(mock_check_if_minimal_metadata_exists.return_value)
        mock_main_dialog.show_message.assert_called_once_with(mock_main_dialog.instance, 'Missing Minimal Metadata',
                                                              mock_get_formatted_message.return_value)
    else:
      mock_main_dialog.show_message.assert_not_called()

  @pytest.mark.parametrize(
    'test_id, expected_success, expected_message, dataverse_id, login_success, dataverse_exists, config_exists', [
      # Success path tests
      ('success_path_valid', True, 'Dataverse configured successfully!', None, True, True, True),
      # Edge cases
      ('edge_case_no_dataverse_id', False,
       'Please re-enter the correct dataverse ID via the configuration dialog, Saved id: None is incorrect!', None,
       True, False, True),
      # Error cases
      ('error_case_invalid_login', False,
       'Please re-enter the correct API token / server URL via the configuration dialog.', None, False, True, True),
      ('error_case_no_config_model', False, 'Failed to load config model!', None, True, True, False),
    ])
  def test_check_if_dataverse_is_configured(self, mocker, mock_main_dialog, test_id, expected_success, expected_message,
                                            dataverse_id, login_success, dataverse_exists, config_exists):
    # Arrange
    mock_check_if_dataverse_exists = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.check_if_dataverse_exists')
    mock_check_login_credentials = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.check_login_credentials')
    mock_check_login_credentials.return_value = (login_success, '')
    mock_check_if_dataverse_exists.return_value = dataverse_exists
    config_model = MagicMock() if config_exists else None
    if config_model:
      config_model.dataverse_login_info = {
        'server_url': 'http://example.com',
        'api_token': 'valid_token',
        'dataverse_id': dataverse_id
      }
    mock_main_dialog.db_api.get_config_model.return_value = config_model

    # Act
    success, message = actual_check_if_dataverse_is_configured(mock_main_dialog)

    # Assert
    mock_main_dialog.db_api.get_config_model.assert_called_once()
    assert success == expected_success
    assert message == expected_message
    mock_main_dialog.logger.info.assert_called_once_with('Checking if dataverse is configured..')
    if not config_exists:
      mock_main_dialog.logger.error.assert_called_once_with('Failed to load config model!')
    else:
      mock_check_login_credentials.assert_called_once_with(mock_main_dialog.logger, 'valid_token', 'http://example.com')
    if test_id not in ['error_case_no_config_model', 'error_case_invalid_login']:
      mock_check_if_dataverse_exists.assert_called_once_with(mock_main_dialog.logger, 'valid_token',
                                                             'http://example.com', dataverse_id)

  @pytest.mark.parametrize('is_configured, message, expected_call', [
    pytest.param((True, ''), '', True, id='success-path-configured'),
    pytest.param((False, 'Error message'), 'Dataverse Not Configured', False, id='edge-case-not-configured'),
    # Add more cases as needed
  ])
  def test_show(self, mocker, mock_main_dialog, is_configured, message, expected_call):
    # Arrange
    mock_config_dialog = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.ConfigDialog')
    instance_mock = MagicMock()
    mock_main_dialog.instance = instance_mock
    mock_main_dialog.is_dataverse_configured = is_configured
    mock_main_dialog.show_message = mocker.MagicMock()

    # Act
    mock_main_dialog.show()

    # Assert
    mock_main_dialog.logger.info.assert_called_once_with('Show MainDialog UI..')
    if expected_call:
      instance_mock.show.assert_called_once()
      mock_config_dialog.assert_not_called()
    else:
      instance_mock.show.assert_not_called()
      mock_config_dialog.return_value.show.assert_called_once()

  @pytest.mark.parametrize('title,message,icon,expected_width', [
    pytest.param('Info', 'This is an information message.', QMessageBox.Information, 200, id='info_message'),
    pytest.param('Warning', 'This is a warning message.', QMessageBox.Warning, 150, id='warning_message'),
    pytest.param('Error', 'This is an error message.', QMessageBox.Critical, 100, id='error_message'),
  ])
  def test_show_message_happy_path(self, mocker, mock_main_dialog, title, message, icon, expected_width):
    # Arrange
    parent = MagicMock()
    mock_msg_box = MagicMock()
    mock_label = MagicMock()
    mock_label.fontMetrics.return_value.boundingRect.return_value.width.return_value = expected_width
    mock_isinstance = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.isinstance', return_value=True)
    mock_msgbox_constructor = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.QMessageBox', return_value=mock_msg_box)
    mock_msg_box.findChild.return_value = mock_label
    # Act
    mock_main_dialog.show_message(parent, title, message, icon)
    # Assert
    mock_msgbox_constructor.assert_called_once_with(parent)
    mock_msg_box.setWindowTitle.assert_called_once_with(title)
    mock_msg_box.setIcon.assert_called_once_with(icon)
    mock_msg_box.setText.assert_called_once_with(message)
    mock_label.setFixedWidth.assert_called_once_with(expected_width)
    mock_msg_box.findChild.assert_called_once_with(QLabel, 'qt_msgbox_label')
    mock_isinstance.assert_called_once_with(mock_label, QLabel)
    mock_label.fontMetrics.assert_called_once()
    mock_label.text.assert_called_once()
    mock_label.fontMetrics.return_value.boundingRect.assert_called_once_with(mock_label.text.return_value)
    mock_label.fontMetrics.return_value.boundingRect.return_value.width.assert_called_once()
    mock_msg_box.exec.assert_called_once()

  @pytest.mark.parametrize('title,message,icon', [
    pytest.param('No Icon', 'This message has no icon specified.', None, id='no_icon_specified'),
  ])
  def test_show_message_edge_cases(self, mocker, mock_main_dialog, title, message, icon):
    # Arrange
    parent = MagicMock()
    mock_msg_box = MagicMock()
    mock_label = MagicMock()
    mocker.patch('pasta_eln.GUI.dataverse.main_dialog.isinstance', return_value=True)
    mock_msgbox_constructor = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.QMessageBox', return_value=mock_msg_box)
    mock_msg_box.findChild.return_value = mock_label
    # Act
    mock_main_dialog.show_message(parent, title, message, icon)
    # Assert
    mock_msgbox_constructor.assert_called_once_with(parent)
    mock_msg_box.setIcon.assert_called_once_with(mock_msgbox_constructor.Icon.Warning)  # Default to Warning if None

  @pytest.mark.parametrize('title,message', [
    pytest.param('Error', 'This is an error message with no label found.', id='label_not_found'),
  ])
  def test_show_message_error_cases(self, mocker, mock_main_dialog, title, message):
    # Arrange
    parent = MagicMock()
    mock_msg_box = MagicMock()
    mock_msgbox_constructor = mocker.patch('pasta_eln.GUI.dataverse.main_dialog.QMessageBox', return_value=mock_msg_box)
    mock_msg_box.findChild.return_value = None  # Simulate label not found
    # Act
    mock_main_dialog.show_message(parent, title, message)
    # Assert
    mock_msgbox_constructor.assert_called_once_with(parent)
    mock_msg_box.setWindowTitle.assert_called_once_with(title)
    mock_msg_box.setIcon.assert_called_once_with(QMessageBox.Warning)
    mock_msg_box.setText.assert_called_once_with(message)
    mock_msg_box.findChild.assert_called_once_with(QLabel, 'qt_msgbox_label')
    mock_main_dialog.logger.error.assert_called_once_with('Failed to find message box label!')
