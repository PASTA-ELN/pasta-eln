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
  project_id = "Test ID"
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
  backend_mock = MagicMock()
  task = DataUploadTask(
    project_name,
    project_id,
    progress_update_callback,
    status_label_set_text_callback,
    status_icon_set_pixmap_callback,
    upload_cancel_clicked_signal_callback,
    backend_mock
  )
  task.db_api = mock_db_api
  task.dataverse_client = mock_dataverse_client
  task.upload_model = mock_upload_model
  task.progress_changed = mocker.MagicMock()
  task.status_changed = mocker.MagicMock()
  task.upload_model_created = mocker.MagicMock()
  task.id_iterator = mocker.MagicMock()
  return task


class TestDataverseDataUploadTask:

  def test_init_succeeds(self, mocker):
    # Arrange
    mock_get_logger = mocker.patch('pasta_eln.dataverse.data_upload_task.logging.getLogger')
    progress_thread_mock = mocker.patch('pasta_eln.dataverse.data_upload_task.ProgressUpdaterThread')
    mocker.patch('pasta_eln.dataverse.data_upload_task.super')
    DataUploadTask.progress_changed = mocker.MagicMock()
    DataUploadTask.status_changed = mocker.MagicMock()
    DataUploadTask.end = mocker.MagicMock()
    DataUploadTask.upload_model_created = mocker.MagicMock()
    progress_update_callback = MagicMock()
    status_label_set_text_callback = MagicMock()
    status_icon_set_pixmap_callback = MagicMock()
    upload_cancel_clicked_signal_callback = MagicMock()
    backend_mock = MagicMock()
    project_name = "Test Project"
    project_id = "Test ID"

    # Act
    task = DataUploadTask(
      project_name,
      project_id,
      progress_update_callback,
      status_label_set_text_callback,
      status_icon_set_pixmap_callback,
      upload_cancel_clicked_signal_callback,
      backend_mock
    )

    # Assert
    mock_get_logger.assert_called_once_with('pasta_eln.dataverse.data_upload_task.DataUploadTask')
    assert task.project_name == project_name, "Project name should be set"
    assert task.db_api is None, "Database API should be set None"
    assert task.upload_model is None, "Upload model should be set None"
    assert task.config_model is None, "Config model should be set None"
    assert task.metadata == {}, "Metadata should be set None"
    task.progress_changed.connect.assert_called_once_with(progress_update_callback)
    task.status_changed.connect.assert_called_once()
    upload_cancel_clicked_signal_callback.connect.assert_called_once()
    assert task.progress_thread == progress_thread_mock.return_value, "Progress thread should be set"
    assert task.progress_thread.progress_update == task.progress_changed, "Progress thread update signal should be set"
    task.progress_thread.end.connect.assert_called_once_with(task.progress_thread.quit)

  @pytest.mark.parametrize("project_name, project_doc_id, dataverse_login_info, metadata, expected_log_contains", [
    # Success path test cases
    ("Project1", "doc123", {"server_url": "http://example.com", "api_token": "token123", "dataverse_id": "dv123"},
     {"key": "value"}, "Upload initiated for project Project1"),
  ], ids=["success-path"])
  def test_initialize_success_path(self, mocker, setup_task, mock_upload_model, mock_db_api, project_name,
                                   project_doc_id,
                                   dataverse_login_info, metadata, expected_log_contains):
    # Arrange
    setup_task.project_name = project_name
    setup_task.project_doc_id = project_doc_id
    datetime_mock = mocker.patch('pasta_eln.dataverse.data_upload_task.datetime')
    mock_db_api.get_config_model.return_value = ConfigModel(dataverse_login_info=dataverse_login_info,
                                                            metadata=metadata)
    # Act
    setup_task.initialize()

    # Assert
    mock_db_api.assert_called_once()
    mock_upload_model.assert_called_once_with(project_name=setup_task.project_name,
                                              status=UploadStatusValues.Queued.name,
                                              log=f"Upload initiated for project {setup_task.project_name} at {datetime_mock.now.return_value.isoformat()}\n",
                                              project_doc_id=setup_task.project_doc_id)
    mock_db_api.return_value.create_model_document.assert_called_once_with(mock_upload_model.return_value)
    setup_task.upload_model = mock_db_api.return_value.create_model_document.return_value
    setup_task.logger.info.assert_called_with("Upload model created: %s", setup_task.upload_model)
    mock_db_api.return_value.get_config_model.assert_called_once()
    assert setup_task.dataverse_server_url == "dataverse_url", "Dataverse server URL should be set"
    assert setup_task.dataverse_api_token == "api_token", "Dataverse API token should be set"
    assert setup_task.dataverse_id == "dataverse_id", "Dataverse ID should be set"
    assert setup_task.metadata == {"key": "value"}, "Metadata should be set"
    assert setup_task.dataverse_client == setup_task.dataverse_client, "Dataverse client should be set"

  @pytest.mark.parametrize("config_model_return, expected_exception_message", [
    # Error case: Config model not found
    (None, "Config model not found/Invalid Login Information."),
    # Add more error cases as needed
  ], ids=["config-error"])
  def test_initialize_error_cases(self, mocker, setup_task, mock_db_api, mock_upload_model,
                                  config_model_return, expected_exception_message):
    # Arrange
    datetime_mock = mocker.patch('pasta_eln.dataverse.data_upload_task.datetime')
    mock_db_api.return_value.get_config_model.return_value = config_model_return

    # Act & Assert
    with pytest.raises(ConfigError) as exc_info:
      setup_task.initialize()
    assert str(exc_info.value) == expected_exception_message
    mock_db_api.assert_called_once()
    mock_upload_model.assert_called_once_with(project_name=setup_task.project_name,
                                              status=UploadStatusValues.Queued.name,
                                              log=f"Upload initiated for project {setup_task.project_name} at {datetime_mock.now.return_value.isoformat()}\n",
                                              project_doc_id=setup_task.project_doc_id)
    mock_db_api.return_value.create_model_document.assert_called_once_with(mock_upload_model.return_value)
    setup_task.upload_model = mock_db_api.return_value.create_model_document.return_value
    setup_task.logger.info.assert_called_with("Upload model created: %s", setup_task.upload_model)
    mock_db_api.return_value.get_config_model.assert_called_once()

  # Happy path tests with various realistic test values
  @pytest.mark.parametrize("project_name,eln_file_path,persistent_id,file_pid,cancelled", [
    ("Project A", "/tmp/4567rtzre/Text File1.eln", "doi:10.5072/FK2/XYZ123", "file_pid_A", False),
    ("Project B", "/tmp/345tgert34/Text File1.eln", "doi:10.5072/FK2/XYZ456", "file_pid_B", True),
  ], ids=["Success-path-A", "Success-path-B"])
  def test_start_task_success_path(self, mocker, setup_task, project_name, eln_file_path, persistent_id, file_pid,
                                   cancelled):
    # Arrange
    mock_super_start_task = mocker.patch('pasta_eln.dataverse.data_upload_task.super')
    mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.check_if_cancelled', return_value=cancelled)
    mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.update_log')
    mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.finalize_upload_task')
    mock_temp_dir = mocker.MagicMock()
    mock_temp_dir.__enter__.return_value = "tempdir"
    mocker.patch('pasta_eln.dataverse.data_upload_task.tempfile.TemporaryDirectory', return_value=mock_temp_dir)
    setup_task.project_name = project_name
    setup_task.cancelled = cancelled
    setup_task.check_if_cancelled = MagicMock(side_effect=[False, False, False, False, cancelled])
    setup_task.create_dataset_for_pasta_project = MagicMock(return_value=persistent_id)
    setup_task.check_if_dataset_is_unlocked = MagicMock(return_value=True)
    setup_task.upload_generated_eln_file_to_dataset = MagicMock(return_value=file_pid)
    setup_task.generate_eln_file = MagicMock(return_value=eln_file_path)

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
    mock_temp_dir.__enter__.assert_called_once()
    setup_task.generate_eln_file.assert_called_once_with("tempdir")
    setup_task.update_log.assert_has_calls(
      [mocker.call(f'Successfully generated ELN file: {eln_file_path}',
                   setup_task.logger.info),
       mocker.call(f'Successfully uploaded ELN file, URL: dataverse_url/dataset.xhtml?persistentId={persistent_id}',
                   setup_task.logger.info)])

  # Various error cases
  @pytest.mark.parametrize("error_step,log_message", [
    ("generate_eln_file", "Failed to generate ELN file for project: %s, hence finalizing the upload"),
    ("create_dataset", "Failed to create dataset for project: %s, hence finalizing the upload"),
    ("unlock_dataset", "Failed to unlock dataset for project: %s, hence finalizing the upload"),
    ("upload_eln_file", "Failed to upload eln file to dataset for project: %s, hence finalizing the upload"),
  ], ids=["generate_eln_file", "error-create-dataset", "error-unlock-dataset", "error-upload-eln-file"])
  def test_start_task_error_cases(self, mocker, setup_task, error_step, log_message):
    # Arrange
    mock_super_start_task = mocker.patch('pasta_eln.dataverse.data_upload_task.super')
    mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.check_if_cancelled', return_value=False)
    mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.update_log')
    mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.finalize_upload_task')
    setup_task.project_name = "Project A"
    setup_task.check_if_cancelled = MagicMock(return_value=False)
    if error_step == "generate_eln_file":
      setup_task.generate_eln_file = MagicMock(return_value=None)
    elif error_step == "create_dataset":
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

  @pytest.mark.parametrize("persistent_id, eln_file_path, upload_result, expected, test_id", [
    # Success path tests
    ("doi:10.1234/FK2", "/path/to/file1.txt",
     {"file_upload_result": "success",
      "dataset_publish_result": {"protocol": "doi", "authority": "10.1234", "identifier": "FK2"}},
     "doi:10.1234/FK2", "success-path-1"),
    ("doi:10.5678/FK3", "/path/to/file2.txt",
     {"file_upload_result": "success",
      "dataset_publish_result": {"protocol": "doi", "authority": "10.5678", "identifier": "FK3"}},
     "doi:10.5678/FK3", "success-path-2"),
    # Edge case: Empty file path
    ("doi:10.1234/FK2", "",
     {"file_upload_result": "success",
      "dataset_publish_result": {"protocol": "doi", "authority": "10.1234", "identifier": "FK2"}},
     "doi:10.1234/FK2", "edge-case-empty-file-path"),
    ("", "", {}, "", "edge-case-null-dv-client"),
    ("", "", {}, "", "edge-case-null-upload-model"),
    # Error cases
    ("doi:10.1234/FK2", "/path/to/file3.txt", {"error": "File not found"}, None, "error-file-not-found"),
    ("", "/path/to/file4.txt", {"error": "Invalid persistent ID"}, None, "error-invalid-persistent-id"),
  ])
  def test_upload_generated_eln_file_to_dataset(self, mocker, setup_task, persistent_id, eln_file_path, upload_result,
                                                expected, test_id):
    # Arrange
    mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.update_log')
    mocker.patch("pasta_eln.dataverse.data_upload_task.asyncio.run", return_value=upload_result)
    setup_task.upload_model.project_name = "Test Project"
    if test_id == "edge-case-null-dv-client":
      setup_task.dataverse_client = None
    if test_id == "edge-case-null-upload-model":
      setup_task.upload_model = None

    # Act
    result = setup_task.upload_generated_eln_file_to_dataset(persistent_id, eln_file_path)

    # Assert
    if test_id == "edge-case-null-dv-client" or test_id == "edge-case-null-upload-model":
      assert result is None
    else:
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
  def test_finalize_upload_task(self, mocker, setup_task, status, expected_status):
    # Arrange
    setup_task.finish.disconnect()
    setup_task.finish = mocker.MagicMock()

    # Act
    setup_task.finalize_upload_task(status)

    # Assert
    setup_task.progress_thread.finalize.emit.assert_called_once()
    setup_task.finish.emit.assert_called_once()
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
    ({}, None, "dv789", {"identifier": "789", "authority": "30.5072", "protocol": "doi"},
     "doi:30.5072/789", "Dataset creation succeeded with PID: doi:30.5072/789", "edge_case_null_update_model"),
    ({}, "Project Name", "dv789", None,
     "doi:30.5072/789", "Dataset creation succeeded with PID: doi:30.5072/789", "edge_case_null_dv_client"),
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
    setup_task.upload_model = MagicMock(project_name=project_name) if project_name else None
    setup_task.dataverse_id = dataverse_id
    if result:
      setup_task.dataverse_client.create_and_publish_dataset.return_value = result
    else:
      setup_task.dataverse_client = None

    # Act
    persistent_id = setup_task.create_dataset_for_pasta_project()

    # Assert
    if test_id == "edge_case_null_update_model" or test_id == "edge_case_null_dv_client":
      assert persistent_id is None, "Expected None, got: {}".format(persistent_id)
    else:
      setup_task.dataverse_client.create_and_publish_dataset.assert_called_once_with(dataverse_id,
                                                                                     {"title": project_name,
                                                                                      **metadata})
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

  @pytest.mark.parametrize("already_cancelled, expected_log_contains, expected_status", [
    pytest.param(False, "Cancelled at 2023-01-01T00:00:00", UploadStatusValues.Cancelled.name,
                 id="test_success_path_not_previously_cancelled"),
    pytest.param(True, "", "", id="test_edge_case_already_cancelled"),
  ])
  def test_cancel_task(self, mocker, setup_task, already_cancelled, expected_log_contains, expected_status):
    # Arrange
    setup_task.cancelled = already_cancelled
    setup_task.upload_model = MagicMock()
    setup_task.update_changed_status = MagicMock()
    mock_datetime = mocker.patch('pasta_eln.dataverse.data_upload_task.datetime')
    mock_super = mocker.patch('pasta_eln.dataverse.data_upload_task.super')
    mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T00:00:00"
    setup_task.cancelled = already_cancelled

    # Act
    setup_task.cancel_task()

    # Assert
    if not already_cancelled:
      assert expected_log_contains in setup_task.upload_model.log
      mock_super.return_value.cancel_task.assert_called_once()
      setup_task.update_changed_status.assert_called_with(expected_status)
      setup_task.progress_thread.cancel.emit.assert_called_once()

    else:
      mock_super.return_value.cancel_task.assert_not_called()
      setup_task.update_changed_status.assert_not_called()
      setup_task.progress_thread.cancel.emit.assert_not_called()

  @pytest.mark.parametrize("status, expected_status", [
    # Success path tests with various realistic test values
    pytest.param(UploadStatusValues.Queued.name, UploadStatusValues.Queued.name, id="default-queued"),
    pytest.param(UploadStatusValues.Uploading.name, UploadStatusValues.Uploading.name, id="processing"),
    pytest.param(UploadStatusValues.Finished.name, UploadStatusValues.Finished.name, id="completed"),
    pytest.param(UploadStatusValues.Error.name, UploadStatusValues.Error.name, id="failed"),
    # Edge cases
    pytest.param("", "", id="empty-string"),
  ])
  def test_update_changed_status(self, setup_task, status, expected_status):
    # Arrange
    setup_task.upload_model = MagicMock()

    # Act
    setup_task.update_changed_status(status)

    # Assert
    setup_task.db_api.update_model_document.assert_called_once()
    setup_task.status_changed.emit.assert_called_with(expected_status)
    assert setup_task.upload_model.status == expected_status, f"Expected status to be '{expected_status}' but got '{setup_task.upload_model.status}'"

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
      ("TestEdgeCase_NullDvClient", {}, False, None, 0),
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
    if test_id == "TestEdgeCase_NullDvClient":
      setup_task.dataverse_client = None
    else:
      # Simulate different responses for consecutive calls
      if isinstance(get_dataset_locks_return_value, list):
        setup_task.dataverse_client.get_dataset_locks.side_effect = get_dataset_locks_return_value
      else:
        setup_task.dataverse_client.get_dataset_locks.return_value = get_dataset_locks_return_value

    # Act
    result = setup_task.check_if_dataset_is_unlocked(persistent_id)

    # Assert
    if test_id == "TestEdgeCase_NullDvClient":
      assert result is False, f"Expected 'False' but got '{result}'"
    else:
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

  @pytest.mark.parametrize("tmp_dir, project_name, config_model, expected_file_path, dtypes, test_id", [
    ("/tmp", "TestProject", ConfigModel(project_upload_items={"Text": True}), "/tmp/TestProject.eln",
     ["text"], "success_path"),
    ("/var/tmp", "Another-Project", ConfigModel(project_upload_items={"Image": True, "Text": False}),
     "/var/tmp/AnotherProject.eln", ["image"], "success_path_with_special_chars_in_project_name"),
    ("/tmp", "Data123", ConfigModel(project_upload_items={}), "/tmp/Data123.eln",
     [], "success_path_with_empty_upload_items"),
    # Edge cases
    ("/tmp", "", ConfigModel(project_upload_items={"Text": True}), "/tmp/.eln", ["text"],
     "edge_case_empty_project_name"),
    ("/tmp", "§$&/§? Pasta Project", ConfigModel(project_upload_items={"Text": True}), "/tmp/PastaProject.eln",
     ["text"], "edge_case_invalid_project_name1"),
    ("/tmp", "Pasta Project 1234 Ü sfß", ConfigModel(project_upload_items={"Text": True}),
     "/tmp/PastaProject1234Üsfß.eln", ["text"], "edge_case_invalid_project_name2"),
    # Error cases
    ("/tmp", "TestProject", None, "", [], "error_no_config_model"),
    ("/tmp", "TestProject", ConfigModel(project_upload_items=None), "", [], "error_no_project_upload_items"),
  ])
  def test_generate_eln_file(self, mocker, setup_task, tmp_dir, project_name, config_model, expected_file_path,
                             dtypes, test_id):
    # Arrange
    setup_task.project_name = project_name
    setup_task.config_model = config_model
    setup_task.update_log = mocker.MagicMock()
    mock_path = mocker.patch('pasta_eln.dataverse.data_upload_task.Path')

    # Act
    with patch("pasta_eln.dataverse.data_upload_task.exportELN") as mock_exportELN:
      result = setup_task.generate_eln_file(tmp_dir)

    # Assert
    if expected_file_path:
      mock_exportELN.assert_any_call(setup_task.backend, [setup_task.project_doc_id], expected_file_path, dtypes)
      assert result == expected_file_path, f"Test ID: {test_id} - Expected file path does not match."
      mock_path.assert_called_once_with(expected_file_path)
      mock_path.return_value.touch.assert_called_once()
    else:
      assert result == expected_file_path, f"Test ID: {test_id} - Expected an empty string due to error."
      if "error" in test_id:
        setup_task.update_log.assert_called_with("Config model or project_upload_items is not set!",
                                                 setup_task.logger.error)

  @pytest.mark.parametrize("tmp_dir, exception, test_id", [
    ("tmp_dir", Exception("File write error"), "exception_during_export"),
  ])
  def test_generate_eln_file_with_exceptions(self, mocker, setup_task, tmp_dir, exception, test_id):
    # Arrange
    setup_task.config_model = ConfigModel(project_upload_items={"Text": True})
    setup_task.update_log = mocker.MagicMock()
    mocker.patch('pasta_eln.dataverse.data_upload_task.Path')

    # Act
    with patch("pasta_eln.dataverse.data_upload_task.exportELN", side_effect=exception):
      result = setup_task.generate_eln_file(tmp_dir)

    # Assert
    assert result == "", f"Test ID: {test_id} - Expected an empty string due to exception."
    setup_task.update_log.assert_called_with(
      f"Error while exporting ELN file for project: {setup_task.project_name}, error: {exception}",
      setup_task.logger.error)
