#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_data_upload_task.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import datetime

import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtGui import QPixmap
from pasta_eln.dataverse.data_upload_task import DataUploadTask
from pasta_eln.dataverse.upload_status_values import UploadStatusValues
from pasta_eln.dataverse.config_error import ConfigError

# Mock dependencies that are not directly related to the functionality being tested
@pytest.fixture
def mock_db_api():
    with patch('pasta_eln.dataverse.data_upload_task.DatabaseAPI') as mock:
        yield mock

@pytest.fixture
def mock_dataverse_client():
    with patch('pasta_eln.dataverse.data_upload_task.DataverseClient') as mock:
        yield mock

@pytest.fixture
def mock_progress_thread():
    with patch('pasta_eln.dataverse.data_upload_task.ProgressThread') as mock:
        yield mock

@pytest.fixture
def mock_upload_model():
    with patch('pasta_eln.dataverse.data_upload_task.UploadModel') as mock:
        yield mock

@pytest.fixture
def setup_task(mocker, mock_db_api, mock_dataverse_client, mock_progress_thread, mock_upload_model):
    # Arrange
    project_name = "Test Project"
    progress_update_callback = MagicMock()
    status_label_set_text_callback = MagicMock()
    status_icon_set_pixmap_callback = MagicMock()
    upload_cancel_clicked_signal_callback = MagicMock()
    task = DataUploadTask(
        project_name,
        progress_update_callback,
        status_label_set_text_callback,
        status_icon_set_pixmap_callback,
        upload_cancel_clicked_signal_callback,
    )
    task.progress_changed = mocker.MagicMock()
    task.status_changed = mocker.MagicMock()
    task.upload_model_created = mocker.MagicMock()
    return task

class TestDataverseDataUploadTask:

    def test_init_succeeds(self, mocker):
        # Arrange
        mock_get_logger = mocker.patch('pasta_eln.dataverse.data_upload_task.logging.getLogger')
        db_api_mock = mocker.patch('pasta_eln.dataverse.data_upload_task.DatabaseAPI')
        client_mock = mocker.patch('pasta_eln.dataverse.data_upload_task.DataverseClient')
        mocker.patch('pasta_eln.dataverse.data_upload_task.ProgressThread')
        upload_model_mock = mocker.patch('pasta_eln.dataverse.data_upload_task.UploadModel')
        mocker.patch('pasta_eln.dataverse.data_upload_task.super')
        datetime_mock = mocker.patch('pasta_eln.dataverse.data_upload_task.datetime')
        DataUploadTask.progress_changed = mocker.MagicMock()
        DataUploadTask.status_changed = mocker.MagicMock()
        DataUploadTask.upload_model_created = mocker.MagicMock()
        progress_update_callback = MagicMock()
        status_label_set_text_callback = MagicMock()
        status_icon_set_pixmap_callback = MagicMock()
        upload_cancel_clicked_signal_callback = MagicMock()
        project_name = "Test Project"

        # Act
        task = DataUploadTask(
            project_name,
            progress_update_callback,
            status_label_set_text_callback,
            status_icon_set_pixmap_callback,
            upload_cancel_clicked_signal_callback,
        )

        # Assert
        mock_get_logger.assert_called_once_with('pasta_eln.dataverse.data_upload_task.DataUploadTask')
        assert task.project_name == project_name, "Project name should be set"
        assert task.db_api == db_api_mock.return_value, "Database API should be set"
        upload_model_mock.assert_called_once_with(project_name=project_name,
                                                  status=UploadStatusValues.Queued.name,
                                                  log=f"Upload initiated for project {project_name} at {datetime_mock.now.return_value.isoformat.return_value}\n")
        db_api_mock.return_value.create_model_document.assert_called_once_with(upload_model_mock.return_value)
        assert task.upload_model == db_api_mock.return_value.create_model_document.return_value, "Upload model should be set"
        mock_get_logger.return_value.info.assert_called_once_with(f"Upload model created: {task.upload_model}")
        db_api_mock.return_value.get_config_model.assert_called_once()
        assert task.config_model == db_api_mock.return_value.get_config_model.return_value, "Config model should be set"
        task.config_model.dataverse_login_info.get.assert_any_call("server_url", "")
        assert task.dataverse_server_url == task.config_model.dataverse_login_info.get("server_url", ""), "Dataverse server URL should be set"
        task.config_model.dataverse_login_info.get.assert_any_call("api_token", "")
        assert task.dataverse_api_token == task.config_model.dataverse_login_info.get("api_token", ""), "Dataverse API Token should be set"
        task.config_model.dataverse_login_info.get.assert_any_call("dataverse_id", "")
        assert task.dataverse_id == task.config_model.dataverse_login_info.get("dataverse_id", ""), "Dataverse ID should be set"
        assert task.metadata == task.config_model.metadata, "Metadata should be set"
        client_mock.assert_called_once_with(task.dataverse_server_url, task.dataverse_api_token, 60)
        assert task.dataverse_client == client_mock.return_value, "Dataverse client should be set"

    @pytest.mark.parametrize("status,expected_log", [
        ("Uploading", "Upload initiated for project Test Project"),
        ("Cancelled", "Cancelled at"),
        ("Finished", "Successfully uploaded ELN file"),
    ], ids=["happy-path-uploading", "cancel-task", "happy-path-finished"])
    def test_start_task(self, setup_task, status, expected_log):
        task = setup_task
        # Mock methods to simulate behavior
        task.check_if_cancelled = MagicMock(return_value=False)
        task.create_dataset_for_pasta_project = MagicMock(return_value="persistent_id")
        task.check_if_dataset_is_unlocked = MagicMock(return_value=True)
        task.upload_generated_eln_file_to_dataset = MagicMock(return_value="file_pid")
        task.finalize_upload_task = MagicMock()

        # Act
        task.start_task()

        # Assert
        assert expected_log in task.upload_model.log
        task.finalize_upload_task.assert_called()

    @pytest.mark.parametrize("config_model,expected_exception", [
        (None, ConfigError),
    ], ids=["config-error"])
    def test_init_config_error(self, mock_db_api, config_model, expected_exception):
        # Arrange
        mock_db_api.return_value.get_config_model.return_value = config_model
        project_name = "Test Project"
        progress_update_callback = MagicMock()
        status_label_set_text_callback = MagicMock()
        status_icon_set_pixmap_callback = MagicMock()
        upload_cancel_clicked_signal_callback = MagicMock()

        # Act / Assert
        with pytest.raises(expected_exception):
            DataUploadTask(project_name, progress_update_callback, status_label_set_text_callback, status_icon_set_pixmap_callback, upload_cancel_clicked_signal_callback)

    @pytest.mark.parametrize("cancelled,expected_status", [
        (True, UploadStatusValues.Cancelled.name),
        (False, UploadStatusValues.Finished.name),
    ], ids=["cancel-task", "finish-task"])
    def test_finalize_upload_task(self, setup_task, cancelled, expected_status):
        task = setup_task
        task.cancelled = cancelled

        # Act
        task.finalize_upload_task()

        # Assert
        assert task.upload_model.status == expected_status
        task.progress_thread.cancel.emit.assert_called()
        task.finished.emit.assert_called()
        task.status_changed.emit.assert_called_with(expected_status)

    @pytest.mark.parametrize("pid,unlocked,expected_result", [
        ("persistent_id", True, True),
        ("persistent_id", False, False),
    ], ids=["dataset-unlocked", "dataset-locked"])
    def test_check_if_dataset_is_unlocked(self, setup_task, mock_dataverse_client, pid, unlocked, expected_result):
        task = setup_task
        mock_dataverse_client.return_value.get_dataset_locks.return_value = {'locks': []} if unlocked else {'locks': [{'lockType': 'test', 'message': 'locked'}]}

        # Act
        result = task.check_if_dataset_is_unlocked(pid)

        # Assert
        assert result == expected_result
