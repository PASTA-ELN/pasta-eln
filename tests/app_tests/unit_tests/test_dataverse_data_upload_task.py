#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_data_upload_task.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import datetime
from threading import Thread
from time import sleep
from unittest.mock import MagicMock, patch

import pytest

from pasta_eln.GUI.dataverse.upload_widget_base import Ui_UploadWidgetFrame
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.data_upload_task import DataUploadTask
from pasta_eln.dataverse.upload_model import UploadModel
from pasta_eln.dataverse.upload_status_values import UploadStatusValues

# Mock the QtCore module to avoid errors related to Qt dependencies
pytest.mockQtCore = MagicMock()
pytest.mockQtCore.Signal = MagicMock(return_value=MagicMock())


# Mock the Ui_UploadWidgetFrame to avoid GUI interactions
@pytest.fixture
def mock_widget():
  widget = MagicMock(spec=Ui_UploadWidgetFrame)
  widget.uploadProgressBar = MagicMock()
  widget.statusIconLabel = MagicMock()
  widget.statusLabel = MagicMock()
  widget.uploadProjectLabel = MagicMock()
  widget.uploadProjectLabel.text.return_value = "TestProject"
  widget.uploadCancelPushButton = MagicMock()
  return widget


@pytest.fixture
def mock_data_upload_task(mocker, mock_widget, mock_upload_model):
  mocker.patch('pasta_eln.dataverse.data_upload_task.DatabaseAPI')
  mocker.patch('pasta_eln.dataverse.data_upload_task.UploadModel')
  mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.progressChanged')
  mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.statusChanged')
  mocker.patch('pasta_eln.dataverse.data_upload_task.DataUploadTask.uploadModelCreated')
  mock_data_upload_task = DataUploadTask(mock_widget)
  mock_data_upload_task.db_api.create_model_document.return_value = mock_upload_model
  return mock_data_upload_task


# Mock the UploadModel to avoid actual database interactions
@pytest.fixture
def mock_upload_model():
  with patch('pasta_eln.dataverse.data_upload_task.UploadModel') as mock:
    mock.id = "test_id"
    return mock


# Mock time.sleep to speed up the tests
@pytest.fixture(autouse=True)
def mock_sleep():
  with patch('time.sleep', return_value=None):
    yield


class TestDataverseDataUploadTask:

  # Happy path tests with various realistic test values
  @pytest.mark.parametrize("test_id, project_name", [
    ("Success_01", "TestProject1"),
    ("Success_02", "TestProject2"),
    ("Success_03", "TestProject3"),
  ])
  def test_data_upload_task_happy_path(self, mocker, mock_widget, test_id, project_name):
    # Arrange
    mock_widget.uploadProjectLabel.text.return_value = project_name
    mock_db_api = mocker.MagicMock()
    mock_db_api.create_model_document.return_value = UploadModel(project_name=project_name)
    mock_db_api.get_model.return_value = ConfigModel()
    mocker.patch('pasta_eln.dataverse.data_upload_task.DatabaseAPI', return_value=mock_db_api)

    # Act
    task = DataUploadTask(mock_widget)

    # Assert
    assert task.project_name == project_name
    assert isinstance(task.upload_model, UploadModel)
    assert task.upload_model.project_name == project_name
    assert isinstance(task.config_model, ConfigModel)
    mock_widget.uploadCancelPushButton.clicked.connect.assert_called_once()

  # Error cases
  @pytest.mark.parametrize("test_id, exception, expected_exception", [
    ("error_01", Exception("DB Connection Error"), Exception),
    ("error_02", ValueError("Invalid Project Name"), ValueError),
  ])
  def test_data_upload_task_error_cases(self, mocker, mock_widget, test_id, exception, expected_exception):
    # Arrange
    mock_db_api = mocker.MagicMock()
    mock_db_api.create_model_document.side_effect = exception
    mocker.patch('pasta_eln.dataverse.data_upload_task.DatabaseAPI', return_value=mock_db_api)

    # Act & Assert
    with pytest.raises(expected_exception):
      DataUploadTask(mock_widget)

  @pytest.mark.parametrize("progress_values, expected_status", [
    (range(101), UploadStatusValues.Finished.name),  # ID: success-path-complete
    (range(50), UploadStatusValues.Cancelled.name),  # ID: success-path-cancelled-midway
  ])
  def test_start_task_happy_path(self, mock_data_upload_task, progress_values, expected_status):
    # Arrange
    def cancel_task():
      sleep(2)
      mock_data_upload_task.cancelled = expected_status == UploadStatusValues.Cancelled.name

    # Act
    mock_data_upload_task.start_task()
    start_task = Thread(target=mock_data_upload_task.start_task)
    cancel_task = Thread(target=cancel_task)
    start_task.start()
    sleep(1)
    cancel_task.start()
    start_task.join()

    # Assert
    assert mock_data_upload_task.upload_model.status == expected_status
    mock_data_upload_task.db_api.update_model_document.assert_called()
    mock_data_upload_task.progressChanged.emit.assert_called()
    if expected_status == UploadStatusValues.Finished.name:
      assert mock_data_upload_task.upload_model.dataverse_url == f"https://dataverse.harvard.edu/dataverse/{mock_data_upload_task.upload_model.project_name}"

  # Parametrized test for error cases
  @pytest.mark.parametrize("exception, expected_status", [
    (Exception, UploadStatusValues.Error.name),  # ID: error-case-exception
  ])
  def test_start_task_error_cases(self, mock_data_upload_task, exception, expected_status):
    # Arrange
    mock_data_upload_task.db_api.update_model_document.side_effect = exception

    # Act & Assert
    with pytest.raises(exception):
      mock_data_upload_task.start_task()

  @pytest.mark.parametrize(
    "test_id, current_time, expected_log, expected_status",
    [
      ("happy_path_1", datetime.datetime(2023, 4, 1, 12, 0), "Cancelled at 2023-04-01T12:00:00", "Cancelled"),
      ("happy_path_2", datetime.datetime(2023, 4, 2, 13, 30), "Cancelled at 2023-04-02T13:30:00", "Cancelled"),
      # Add more test cases for different times and scenarios
    ],
  )
  def test_cancel_task(self, test_id, mock_data_upload_task, current_time, expected_log, expected_status, mocker):
    # Arrange
    mocker.patch('datetime.datetime')
    datetime.datetime.now.return_value = current_time
    mock_data_upload_task.upload_model = MagicMock()
    mock_data_upload_task.statusChanged = MagicMock()
    super_mock = MagicMock()
    mocker.patch('pasta_eln.dataverse.data_upload_task.super', return_value=super_mock)

    # Act
    mock_data_upload_task.cancel_task()

    # Assert
    super_mock.cancel_task.assert_called_once()
    assert mock_data_upload_task.upload_model.log == expected_log
    assert mock_data_upload_task.upload_model.status == expected_status
    mock_data_upload_task.statusChanged.emit.assert_called_once_with(expected_status)
