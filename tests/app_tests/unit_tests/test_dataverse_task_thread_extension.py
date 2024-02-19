#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_task_thread_extension.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from logging import Logger
from threading import ThreadError
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QThread

from pasta_eln.dataverse.generic_task_object import GenericTaskObject
from pasta_eln.dataverse.task_thread_extension import TaskThreadExtension


# Mocking GenericTaskObject to isolate TaskThreadExtension behavior
@pytest.fixture
def mock_task():
  task = MagicMock(spec=GenericTaskObject)
  task.cancel = MagicMock()
  task.cleanup = MagicMock()
  task.id = "test_task_id"
  return task


class TestDataverseTaskThreadExtension:

  @pytest.mark.parametrize("test_id, task, exception", [
    # Success path tests with various realistic test values
    ("success", MagicMock(spec=GenericTaskObject), None),

    # Error cases might include initializing with invalid task objects
    # Again, without more context on what constitutes an invalid task, this is speculative
    ("error", MagicMock(spec=GenericTaskObject), ThreadError("Invalid task object")),
  ])
  def test_task_thread_extension_initialization(self, mocker, test_id, task, exception):
    # Arrange & Act
    mock_thread = MagicMock(spec=QThread)
    mock_logger = MagicMock(spec=Logger)
    mocker.patch('pasta_eln.dataverse.task_thread_extension.QtCore.QThread', return_value=mock_thread)
    mock_get_logger = mocker.patch('pasta_eln.dataverse.task_thread_extension.logging.getLogger',
                                   return_value=mock_logger)
    if test_id == "error":
      task.moveToThread.side_effect = exception

      with pytest.raises(ThreadError):
        extension = TaskThreadExtension(task)
    else:
      extension = TaskThreadExtension(task)

    # Assert
    if test_id == "success":
      mock_thread.start.assert_called_once()
      assert extension.task == task
      assert isinstance(extension.worker_thread, QThread)
      # Assuming moveToThread will be called inside the __init__, we should check it
      task.moveToThread.assert_called_once_with(extension.worker_thread)
      mock_get_logger.assert_called_once_with("pasta_eln.dataverse.task_thread_extension.TaskThreadExtension")

  # Parametrized test for the success path
  @pytest.mark.parametrize("test_id", ["success_path_1"])
  def test_task_thread_extension_success_path(self, mocker, mock_task, test_id):
    # Arrange
    mock_thread = MagicMock(spec=QThread)
    mock_logger = MagicMock(spec=Logger)
    mocker.patch('pasta_eln.dataverse.task_thread_extension.QtCore.QThread', return_value=mock_thread)
    mocker.patch('pasta_eln.dataverse.task_thread_extension.logging.getLogger', return_value=mock_logger)
    extension = TaskThreadExtension(mock_task)

    # Act
    extension.quit()

    # Assert
    mock_task.cancel.emit.assert_called_once()
    mock_task.cleanup.assert_called_once()
    assert isinstance(extension.worker_thread, QThread)
    mock_thread.quit.assert_called_once()
    mock_logger.info.assert_called_once_with('Quitting task thread extension, Task id: %s', 'test_task_id')

  # Parametrized test for error cases
  @pytest.mark.parametrize("test_id, exception, expected_behavior", [
    ("error_case_invalid_task", ValueError, "handle_error"),
    ("error_case_thread_error", RuntimeError, "handle_error")
  ])
  def test_task_thread_extension_error_cases(self, mocker, mock_task, test_id, exception, expected_behavior):
    # Arrange
    mock_thread = MagicMock(spec=QThread)
    mocker.patch('pasta_eln.dataverse.task_thread_extension.QtCore.QThread', return_value=mock_thread)
    mock_task.cleanup.side_effect = exception
    extension = TaskThreadExtension(mock_task)

    # Act and Assert
    with pytest.raises(exception):
      extension.quit()
