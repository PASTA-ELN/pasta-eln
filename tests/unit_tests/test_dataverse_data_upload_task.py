#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_data_upload_task.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import datetime
from unittest.mock import MagicMock, patch

import pytest

from pasta_eln.dataverse.config_error import ConfigError
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.data_upload_task import DataUploadTask
from pasta_eln.dataverse.upload_model import UploadModel
from pasta_eln.dataverse.upload_status_values import UploadStatusValues


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
  with patch('pasta_eln.dataverse.data_upload_task.ProgressUpdaterThread') as mock:
    yield mock


@pytest.fixture
def mock_upload_model():
  with patch('pasta_eln.dataverse.data_upload_task.UploadModel') as mock:
    yield mock


@pytest.fixture
def setup_task(mocker, mock_db_api, mock_dataverse_client, mock_progress_thread, mock_upload_model):
  # Arrange
  project_name = "Test Project"
  mocker.patch('pasta_eln.dataverse.data_upload_task.logging.getLogger')
  mock_db_api.return_value.create_model_document.return_value = UploadModel(_id="1234567890abcdef1234567890abcdef",
                                                                            _rev="1-1234567890abcdef1234567890abcdef",
                                                                            data_type="Test Data Type",
                                                                            project_name="project_name",
                                                                            project_doc_id="1234567890abcdef1234567890abcdef",
                                                                            status=UploadStatusValues.Queued.name,
                                                                            finished_date_time=datetime.datetime.now().strftime(
                                                                              "%Y-%m-%d %H:%M:%S"),
                                                                            log="",
                                                                            dataverse_url="dataverse_url")
  mock_db_api.return_value.get_config_model.return_value = ConfigModel(_id="1234567890abcdef1234567890abcdef",
                                                                       _rev="1-1234567890abcdef1234567890abcdef",
                                                                       project_upload_items={"Test Item": "Test Value"},
                                                                       parallel_uploads_count=2,
                                                                       dataverse_login_info={
                                                                         "server_url": "dataverse_url",
                                                                         "api_token": "api_token",
                                                                         "dataverse_id": "dataverse_id"},
                                                                       metadata={"key": "value"})
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
  task.cancel = mocker.MagicMock()
  task.start = mocker.MagicMock()
  task.finished = mocker.MagicMock()
  task.id_iterator = mocker.MagicMock()
  return task


class TestDataverseDataUploadTask:

  def test_init_succeeds(self, mocker):
    # Arrange
    mock_get_logger = mocker.patch('pasta_eln.dataverse.data_upload_task.logging.getLogger')
    db_api_mock = mocker.patch('pasta_eln.dataverse.data_upload_task.DatabaseAPI')
    client_mock = mocker.patch('pasta_eln.dataverse.data_upload_task.DataverseClient')
    progress_thread_mock = mocker.patch('pasta_eln.dataverse.data_upload_task.ProgressUpdaterThread')
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
      upload_cancel_clicked_signal_callback
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
    assert task.dataverse_server_url == task.config_model.dataverse_login_info.get("server_url",
                                                                                   ""), "Dataverse server URL should be set"
    task.config_model.dataverse_login_info.get.assert_any_call("api_token", "")
    assert task.dataverse_api_token == task.config_model.dataverse_login_info.get("api_token",
                                                                                  ""), "Dataverse API Token should be set"
    task.config_model.dataverse_login_info.get.assert_any_call("dataverse_id", "")
    assert task.dataverse_id == task.config_model.dataverse_login_info.get("dataverse_id",
                                                                           ""), "Dataverse ID should be set"
    assert task.metadata == task.config_model.metadata, "Metadata should be set"
    client_mock.assert_called_once_with(task.dataverse_server_url, task.dataverse_api_token, 60)
    assert task.dataverse_client == client_mock.return_value, "Dataverse client should be set"
    task.progress_changed.connect.assert_called_once_with(progress_update_callback)
    task.status_changed.connect.assert_called_once()
    upload_cancel_clicked_signal_callback.connect.assert_called_once()
    assert task.progress_thread == progress_thread_mock.return_value, "Progress thread should be set"
    assert task.progress_thread.progress_update == task.progress_changed, "Progress thread update signal should be set"

  @pytest.mark.parametrize("test_id, config_model, expected_exception", [
    ("config_error", None, ConfigError),
  ])
  def test_init_config_error(self, mock_db_api, test_id, config_model, expected_exception):
    mock_db_api.return_value.get_config_model.return_value = config_model

    # Act / Assert
    with pytest.raises(expected_exception):
      DataUploadTask("Test Project",
                     MagicMock(),
                     MagicMock(),
                     MagicMock(),
                     MagicMock())

  # Happy path tests with various realistic test values
  @pytest.mark.parametrize("project_name,eln_file_path,persistent_id,file_pid,cancelled", [
    ("Project A", "/home/jmurugan/Artefacts/10/Text File1.txt", "doi:10.5072/FK2/XYZ123", "file_pid_A", False),
    ("Project B", "/home/jmurugan/Artefacts/10/Text File1.txt", "doi:10.5072/FK2/XYZ456", "file_pid_B", True),
  ], ids=["Success-path-A", "Success-path-B"])
  def test_start_task_success_path(self, mocker, setup_task, project_name, eln_file_path, persistent_id, file_pid,
                                   cancelled):
    # Arrange
    mock_super_start_task = mocker.patch('pasta_eln.dataverse.data_upload_task.super')
    mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.check_if_cancelled', return_value=cancelled)
    mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.update_log')
    mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.finalize_upload_task')
    setup_task.project_name = project_name
    setup_task.cancelled = cancelled
    setup_task.check_if_cancelled = MagicMock(side_effect=[False, False, False, False, cancelled])
    setup_task.create_dataset_for_pasta_project = MagicMock(return_value=persistent_id)
    setup_task.check_if_dataset_is_unlocked = MagicMock(return_value=True)
    setup_task.upload_generated_eln_file_to_dataset = MagicMock(return_value=file_pid)

    # Act
    setup_task.start_task()

    # Assert
    mock_super_start_task.assert_called_once()
    mock_super_start_task.return_value.start_task.assert_called_once_with()
    setup_task.status_changed.emit.assert_any_call(UploadStatusValues.Uploading.name)
    setup_task.upload_model_created.emit.assert_called_with("1234567890abcdef1234567890abcdef")
    setup_task.progress_thread.start.assert_called_once()
    setup_task.create_dataset_for_pasta_project.assert_called_once()
    setup_task.check_if_dataset_is_unlocked.assert_called_once_with(persistent_id)
    setup_task.upload_generated_eln_file_to_dataset.assert_called_once_with(persistent_id, eln_file_path)
    final_status = UploadStatusValues.Cancelled.name if cancelled else UploadStatusValues.Finished.name
    setup_task.finalize_upload_task.assert_called_with(final_status)
    setup_task.check_if_cancelled.assert_has_calls([mocker.call(), mocker.call(), mocker.call(), mocker.call()])
    setup_task.update_log.assert_has_calls(
      [mocker.call(f'Step 1: Generating ELN file for project: {project_name}', setup_task.logger.info),
       mocker.call('Successfully generated ELN file: /home/jmurugan/Artefacts/10/Text File1.txt',
                   setup_task.logger.info),
       mocker.call(f'Successfully uploaded ELN file, URL: dataverse_url/dataset.xhtml?persistentId={persistent_id}',
                   setup_task.logger.info)])

  # Various error cases
  @pytest.mark.parametrize("error_step,log_message", [
    ("create_dataset", "Failed to create dataset for project: %s, hence finalizing the upload"),
    ("unlock_dataset", "Failed to unlock dataset for project: %s, hence finalizing the upload"),
    ("upload_eln_file", "Failed to upload eln file to dataset for project: %s, hence finalizing the upload"),
  ], ids=["error-create-dataset", "error-unlock-dataset", "error-upload-eln-file"])
  def test_start_task_error_cases(self, mocker, setup_task, error_step, log_message):
    # Arrange
    mock_super_start_task = mocker.patch('pasta_eln.dataverse.data_upload_task.super')
    mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.check_if_cancelled', return_value=False)
    mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.update_log')
    mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.finalize_upload_task')
    setup_task.project_name = "Project A"
    setup_task.check_if_cancelled = MagicMock(return_value=False)
    if error_step == "create_dataset":
      setup_task.create_dataset_for_pasta_project = MagicMock(return_value=None)
    else:
      setup_task.create_dataset_for_pasta_project = MagicMock(return_value="doi:10.5072/FK2/XYZ123")
      if error_step == "unlock_dataset":
        setup_task.check_if_dataset_is_unlocked = MagicMock(return_value=False)
      else:
        setup_task.check_if_dataset_is_unlocked = MagicMock(return_value=True)
        setup_task.upload_generated_eln_file_to_dataset = MagicMock(return_value=None)

    # Act
    setup_task.start_task()

    # Assert
    mock_super_start_task.assert_called_once()
    mock_super_start_task.return_value.start_task.assert_called_once_with()
    setup_task.logger.warning.assert_called_with(log_message, "Project A")
    setup_task.finalize_upload_task.assert_called_with(UploadStatusValues.Error.name)

  @pytest.mark.parametrize(
    "cancel_status,expected_final_status,create_dataset_return,check_dataset_unlocked_return,upload_file_return", [
      ([False, False, False, False], UploadStatusValues.Finished.name, "persistent_id_mock", True, "file_pid_mock"),
      # Happy path
      ([True, False, False, False], UploadStatusValues.Cancelled.name, "persistent_id_mock", True, "file_pid_mock"),
      # Cancelled after start
      ([False, True, False, False], UploadStatusValues.Cancelled.name, "persistent_id_mock", True, "file_pid_mock"),
      # Cancelled after start
      ([False, False, True, False], UploadStatusValues.Cancelled.name, "persistent_id_mock", True, "file_pid_mock"),
      # Cancelled after start
      ([False, False, False, True], UploadStatusValues.Cancelled.name, "persistent_id_mock", True, "file_pid_mock"),
      # Cancelled after start
      ([False, False, False, False], UploadStatusValues.Error.name, None, True, "file_pid_mock"),
      # Dataset creation fails
      ([False, False, False, False], UploadStatusValues.Error.name, "persistent_id_mock", False, "file_pid_mock"),
      # Dataset unlock fails
      ([False, False, False, False], UploadStatusValues.Error.name, "persistent_id_mock", True, None),
      # File upload fails
    ], ids=["success-path", "cancelled_before_eln_generation", "cancelled_before_dataset_creation",
            "cancelled_before_dataset_unlock", "cancelled_before_eln_upload", "dataset-creation-fails",
            "dataset-unlock-fails", "file-upload-fails"])
  def test_start_task(self, mocker, setup_task, cancel_status, expected_final_status, create_dataset_return,
                      check_dataset_unlocked_return, upload_file_return):
    # Arrange
    mocker.patch('pasta_eln.dataverse.data_upload_task.super')
    setup_task.finalize_upload_task = mocker.MagicMock()
    setup_task.check_if_dataset_is_unlocked = mocker.MagicMock(return_value=check_dataset_unlocked_return)
    setup_task.check_if_cancelled = mocker.MagicMock(side_effect=cancel_status)
    if any(cancel_status):
      setup_task.finalize_upload_task(UploadStatusValues.Cancelled.name)
    setup_task.create_dataset_for_pasta_project = mocker.MagicMock(return_value=create_dataset_return)
    setup_task.upload_generated_eln_file_to_dataset = mocker.MagicMock(return_value=upload_file_return)

    # Act
    setup_task.start_task()

    # Assert
    setup_task.status_changed.emit.assert_called_with(UploadStatusValues.Uploading.name)
    setup_task.upload_model_created.emit.assert_called_with("1234567890abcdef1234567890abcdef")
    setup_task.progress_thread.start.assert_called_once()
    if create_dataset_return is None or not check_dataset_unlocked_return or upload_file_return is None:
      setup_task.finalize_upload_task.assert_called_with(UploadStatusValues.Error.name)
    else:
      setup_task.finalize_upload_task.assert_called_with(expected_final_status)

  @pytest.mark.parametrize("persistent_id, eln_file_path, upload_result, expected", [
    # Success path tests
    ("doi:10.1234/FK2", "/path/to/file1.txt",
     {"file_upload_result": "success",
      "dataset_publish_result": {"protocol": "doi", "authority": "10.1234", "identifier": "FK2"}},
     "doi:10.1234/FK2"),
    ("doi:10.5678/FK3", "/path/to/file2.txt",
     {"file_upload_result": "success",
      "dataset_publish_result": {"protocol": "doi", "authority": "10.5678", "identifier": "FK3"}},
     "doi:10.5678/FK3"),
    # Edge case: Empty file path
    ("doi:10.1234/FK2", "",
     {"file_upload_result": "success",
      "dataset_publish_result": {"protocol": "doi", "authority": "10.1234", "identifier": "FK2"}},
     "doi:10.1234/FK2"),
    # Error cases
    ("doi:10.1234/FK2", "/path/to/file3.txt", {"error": "File not found"}, None),
    ("", "/path/to/file4.txt", {"error": "Invalid persistent ID"}, None),
  ], ids=["success-path-1", "success-path-2", "edge-case-empty-file-path", "error-file-not-found",
          "error-invalid-persistent-id"])
  def test_upload_generated_eln_file_to_dataset(self, mocker, setup_task, persistent_id, eln_file_path, upload_result,
                                                expected):
    # Arrange
    mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.update_log')
    mocker.patch("pasta_eln.dataverse.data_upload_task.asyncio.run", return_value=upload_result)
    setup_task.upload_model.project_name = "Test Project"

    # Act
    result = setup_task.upload_generated_eln_file_to_dataset(persistent_id, eln_file_path)

    # Assert
    assert result == expected
    if expected:
      setup_task.update_log.assert_called_with(f'ELN File uploaded successfully, generated file PID: {expected}',
                                               setup_task.logger.info)
    else:
      setup_task.update_log.assert_called_with(f'ELN File upload failed with errors: {upload_result}',
                                               setup_task.logger.error)

  @pytest.mark.parametrize("status, expected_status", [
    pytest.param(UploadStatusValues.Finished.name, UploadStatusValues.Finished.name, id="success_path_finished"),
    pytest.param(UploadStatusValues.Error.name, UploadStatusValues.Error.name, id="success_path_error"),
    pytest.param(UploadStatusValues.Cancelled.name, UploadStatusValues.Cancelled.name, id="success_path_cancelled"),
    # Edge cases could involve unexpected status values not defined in UploadStatusValues
    pytest.param("NonExistentStatus", "NonExistentStatus", id="edge_case_nonexistent_status"),
  ])
  def test_finalize_upload_task(self, setup_task, status, expected_status):
    # Arrange

    # Act
    setup_task.finalize_upload_task(status)

    # Assert
    setup_task.progress_thread.cancel.emit.assert_called_once()
    setup_task.finished.emit.assert_called_once()
    setup_task.status_changed.emit.assert_called_once_with(expected_status)

  # Parametrized test cases
  @pytest.mark.parametrize("metadata, project_name, dataverse_id, result, expected_pid, log_message, test_id", [
    # Happy path tests
    ({"key": "value"}, "Project A", "dv123", {"identifier": "123", "authority": "10.5072", "protocol": "doi"},
     "doi:10.5072/123", "Dataset creation succeeded with PID: doi:10.5072/123", "success_path_1"),
    ({"key": "value2"}, "Project B", "dv456", {"identifier": "456", "authority": "20.5072", "protocol": "hdl"},
     "hdl:20.5072/456", "Dataset creation succeeded with PID: hdl:20.5072/456", "success_path_2"),
    # Edge cases
    ({}, "Empty Metadata Project", "dv789", {"identifier": "789", "authority": "30.5072", "protocol": "doi"},
     "doi:30.5072/789", "Dataset creation succeeded with PID: doi:30.5072/789", "edge_case_empty_metadata"),
    # Error cases
    ({"key": "value"}, "Error Project", "dv000", "Error: Missing fields", None,
     "Dataset creation failed with errors: Error: Missing fields", "error_case_missing_fields"),
  ])
  def test_create_dataset_for_pasta_project(self, mocker, setup_task, metadata, project_name, dataverse_id, result,
                                            expected_pid, log_message, test_id):
    # Arrange
    mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.update_log')
    mocker.patch('pasta_eln.dataverse.data_upload_task.get_flattened_metadata', return_value=metadata)
    mock_run = mocker.patch('pasta_eln.dataverse.data_upload_task.asyncio.run', return_value=result)
    setup_task.metadata = metadata
    setup_task.upload_model = MagicMock(project_name=project_name)
    setup_task.dataverse_id = dataverse_id
    setup_task.dataverse_client.create_and_publish_dataset.return_value = result

    # Act
    persistent_id = setup_task.create_dataset_for_pasta_project()

    # Assert
    setup_task.dataverse_client.create_and_publish_dataset.assert_called_once_with(dataverse_id,
                                                                                   {"title": project_name, **metadata})
    mock_run.assert_called_once_with(setup_task.dataverse_client.create_and_publish_dataset.return_value)
    if expected_pid:
      setup_task.update_log.assert_called_with(log_message, setup_task.logger.info)
      assert persistent_id == expected_pid
    else:
      setup_task.update_log.assert_called_with(log_message, setup_task.logger.error)
      assert persistent_id is None

  @pytest.mark.parametrize("log, logger_method, expected_log, test_id", [
    # Happy path tests
    ("Log entry 1", lambda x: print(x), "Log entry 1", "happy_path_print"),
    ("Error occurred", lambda x: print(f"ERROR: {x}"), "Error occurred", "happy_path_error_log"),

    # Edge cases
    ("", lambda x: print(x), "", "edge_case_empty_log"),
    ("Log entry 2", None, "Log entry 2", "edge_case_no_logger"),

    # Error cases - considering the function's simplicity, error cases are limited to input types and values
    # which are handled by Python's type hints and runtime. Thus, no explicit error case is defined here.
  ])
  def test_update_log(self, mocker, setup_task, log, logger_method, expected_log, test_id):
    # Arrange
    mock_upload_model = mocker.MagicMock()
    setup_task.upload_model = mock_upload_model

    # Act
    setup_task.update_log(log, logger_method)

    # Assert
    assert mock_upload_model.log == expected_log, f"Test Failed: {test_id}"
    setup_task.db_api.update_model_document.assert_called_once_with(
      mock_upload_model), f"DB update not called: {test_id}"

  @pytest.mark.parametrize("finished,expected_log,expected_status,expected_emission", [
    (False, "Cancelled at 2023-01-01T00:00:00\n", UploadStatusValues.Cancelled.name, UploadStatusValues.Cancelled.name),
    (True, "Cancelled at 2023-01-01T00:00:00\n", UploadStatusValues.Cancelled.name, UploadStatusValues.Cancelled.name),
    # Add more test cases if there are other realistic values or edge cases for the `finished` attribute
  ], ids=["success_path_1", "success_path_2"])
  def test_cancel_task(self, mocker, setup_task, finished, expected_log, expected_status, expected_emission):
    # Arrange
    mock_datetime = mocker.patch('pasta_eln.dataverse.data_upload_task.datetime')
    mock_super = mocker.patch('pasta_eln.dataverse.data_upload_task.super')
    mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T00:00:00"
    setup_task.finished = finished

    # Act
    setup_task.cancel_task()

    # Assert
    if not finished:
      assert (setup_task.upload_model.log == expected_log
              ), "Expected log message not set"
      assert (setup_task.upload_model.status == expected_status
              ), "Expected status not set"
      setup_task.status_changed.emit.assert_called_once_with(expected_emission)
      mock_super.assert_called_once()
      mock_super.return_value.cancel_task.assert_called_once()
    else:
      assert setup_task.upload_model.log == "", "Expected log message not set"
      setup_task.status_changed.emit.assert_not_called()
      mock_super.assert_not_called()
      mock_super.return_value.cancel_task.assert_not_called()

  # Test IDs for clarity and traceability
  # ID Format: Test[HappyPath/EdgeCase/ErrorCase]_[Condition]

  @pytest.mark.parametrize(
    "test_id, get_dataset_locks_return_value, expected_result, expected_log_messages, sleep_call_count", [
      # Happy path tests
      ("TestSuccessPath_Unlocked", {"locks": []}, True, ["Dataset with PID: test_pid is unlocked already!"], 0),
      ("TestSuccessPath_LockedThenUnlocked",
       [{"locks": [{"lockType": "testLock", "message": "Testing"}]}, {"locks": []}, 0],
       True, [
         "Dataset with PID: test_pid is locked. Lock type: testLock, Message: Testing",
         "Dataset with PID: test_pid is unlocked already!"
       ], 1),
      ("TestSuccessPath_LockedMultipleLocksThenUnlocked",
       [{"locks": [{"lockType": "testLock1", "message": "Testing1"}]},
        {"locks": [{"lockType": "testLock2", "message": "Testing2"}]}, {"locks": []}],
       True, [
         "Dataset with PID: test_pid is locked. Lock type: testLock1, Message: Testing1",
         "Dataset with PID: test_pid is locked. Lock type: testLock2, Message: Testing2",
         "Dataset with PID: test_pid is unlocked already!"
       ], 2),
      # Edge case tests
      ("TestEdgeCase_EmptyDict", {}, True, ["Dataset with PID: test_pid is unlocked already!"], 0),
      # Error case tests
      ("TestErrorCase_NonDictResponse", "Error response", False,
       ["Dataset lock check failed. Error response", "Dataset with PID: test_pid is still locked after 10 retries!"],
       10),
    ])
  def test_check_if_dataset_is_unlocked(self, mocker, setup_task, test_id, get_dataset_locks_return_value,
                                        expected_result, expected_log_messages, sleep_call_count):
    # Arrange
    persistent_id = "test_pid"
    mocker.patch('pasta_eln.dataverse.data_upload_task.asyncio.run',
                 side_effect=get_dataset_locks_return_value if isinstance(get_dataset_locks_return_value,
                                                                          list) else None,
                 return_value=None if isinstance(get_dataset_locks_return_value,
                                                 list) else get_dataset_locks_return_value)
    mock_sleep = mocker.patch('pasta_eln.dataverse.data_upload_task.time.sleep')
    mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.update_log')

    # Simulate different responses for consecutive calls
    if isinstance(get_dataset_locks_return_value, list):
      setup_task.dataverse_client.get_dataset_locks.side_effect = get_dataset_locks_return_value
    else:
      setup_task.dataverse_client.get_dataset_locks.return_value = get_dataset_locks_return_value

    # Act
    result = setup_task.check_if_dataset_is_unlocked(persistent_id)

    # Assert
    if sleep_call_count:
      mock_sleep.assert_has_calls([mocker.call(1)] * sleep_call_count)
    else:
      mock_sleep.assert_not_called()

    assert result == expected_result
    for message in expected_log_messages:
      setup_task.update_log.assert_any_call(message,
                                            setup_task.logger.error if "locked after 10 retries!" in message else setup_task.logger.info)

  @pytest.mark.parametrize("cancelled, expected_call, expected_log_message, expected_final_status", [
    (True, True, "User cancelled the upload, hence finalizing the upload!", UploadStatusValues.Cancelled.name),
    (False, False, None, None),
  ], ids=["cancelled-true", "cancelled-false"])
  def test_check_if_cancelled(self, mocker, setup_task, cancelled, expected_call, expected_log_message,
                              expected_final_status):
    # Arrange
    setup_task.cancelled = cancelled
    setup_task.update_log = mocker.MagicMock()
    setup_task.finalize_upload_task = mocker.MagicMock()

    # Act
    result = setup_task.check_if_cancelled()

    # Assert
    assert result == cancelled
    if expected_call:
      setup_task.update_log.assert_called_once_with(expected_log_message, setup_task.logger.info)
      setup_task.finalize_upload_task.assert_called_once_with(expected_final_status)
    else:
      setup_task.update_log.assert_not_called()
      setup_task.finalize_upload_task.assert_not_called()
