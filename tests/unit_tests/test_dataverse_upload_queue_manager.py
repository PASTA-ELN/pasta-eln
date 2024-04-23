#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_upload_queue_manager.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import time
from threading import Thread
from unittest.mock import MagicMock

import pytest

from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.task_thread_extension import TaskThreadExtension
from pasta_eln.dataverse.upload_queue_manager import UploadQueueManager


@pytest.fixture
def mock_manager(mocker):
  mock_logger = mocker.MagicMock()
  mock_database_api = mocker.MagicMock()
  mock_set_concurrent_uploads = mocker.MagicMock()
  mock_logger.mock_logger_constructor = mocker.patch('pasta_eln.dataverse.upload_queue_manager.logging.getLogger',
                                                     return_value=mock_logger)
  mock_database_api.mock_db_constructor = mocker.patch('pasta_eln.dataverse.upload_queue_manager.DatabaseAPI',
                                                       return_value=mock_database_api)
  mocker.patch('pasta_eln.dataverse.upload_queue_manager.UploadQueueManager.set_concurrent_uploads',
               return_value=mock_set_concurrent_uploads)
  return UploadQueueManager()


def get_mock_task_thread(mocker, cancelled=False):
  mock = mocker.MagicMock(spec=TaskThreadExtension)
  mock.task = mocker.MagicMock()
  mock.task.id = mocker.MagicMock()
  mock.task.started = False
  mock.task.cancelled = cancelled

  def set_started():
    mock.task.started = True

  mock.task.start.emit = mocker.MagicMock(side_effect=set_started)
  mock.worker_thread = mocker.MagicMock()
  return mock


class TestDataverseUploadQueueManager:

  def test_initialize(self, mock_manager):
    # Assert
    mock_manager.logger.mock_logger_constructor.assert_any_call(
      'pasta_eln.dataverse.generic_task_object.UploadQueueManager')
    mock_manager.set_concurrent_uploads.assert_called_once()
    assert len(mock_manager.upload_queue) == 0
    assert len(mock_manager.running_queue) == 0
    mock_manager.db_api.mock_db_constructor.assert_called_once()

  @pytest.mark.parametrize("test_id, concurrent_uploads, tasks_to_add, expected_upload_queue_length",
                           [("success_01", 2, 1, 1), ("success_02", 2, 3, 3), ("success_03", 5, 10, 10), ])
  def test_add_to_queue_success_path(self, mocker, mock_manager, test_id, concurrent_uploads, tasks_to_add,
                                     expected_upload_queue_length):
    # Arrange
    task_threads = [get_mock_task_thread(mocker) for _ in range(tasks_to_add)]

    # Act
    for task_thread in task_threads:
      mock_manager.add_to_queue(task_thread)

    # Assert
    assert mock_manager.upload_queue == task_threads
    for task_thread in task_threads:
      task_thread.task.finished.connect.assert_called_once()

  # Edge cases tests
  @pytest.mark.parametrize("test_id, concurrent_uploads, tasks_to_add, tasks_to_remove, expected_upload_queue_length",
                           [("edge_01", 2, 2, 1, 1), ("edge_02", 2, 5, 5, 0), ("edge_03", 5, 10, 3, 7), ])
  def test_remove_from_queue_edge_cases(self, mocker, mock_manager, test_id, concurrent_uploads, tasks_to_add,
                                        tasks_to_remove, expected_upload_queue_length):
    # Arrange
    task_threads = [get_mock_task_thread(mocker) for _ in range(tasks_to_add)]
    for task_thread in task_threads:
      mock_manager.add_to_queue(task_thread)

    # Act
    for task_thread in task_threads[:tasks_to_remove]:
      mock_manager.remove_from_queue(task_thread)

    # Assert
    assert len(mock_manager.upload_queue) == expected_upload_queue_length
    for task_thread in task_threads[:tasks_to_remove]:
      task_thread.worker_thread.quit.assert_called_once()

  # Error cases tests
  @pytest.mark.parametrize("test_id, concurrent_uploads, tasks_to_add, expected_upload_queue_length",
                           [("error_01", 2, 2, 2), ("error_02", 2, 5, 5), ("error_03", 5, 10, 10), ])
  def test_remove_from_queue_error_cases(self, mocker, mock_manager, test_id, concurrent_uploads, tasks_to_add,
                                         expected_upload_queue_length):
    # Arrange
    task_threads = [get_mock_task_thread(mocker) for _ in range(tasks_to_add)]
    thread_task_to_remove = get_mock_task_thread(mocker)
    for task_thread in task_threads:
      mock_manager.add_to_queue(task_thread)

    # Act
    mock_manager.remove_from_queue(thread_task_to_remove)

    # Assert
    assert len(mock_manager.upload_queue) == expected_upload_queue_length
    thread_task_to_remove.worker_thread.quit.assert_called_once()

  @pytest.mark.parametrize("test_id, in_upload_queue, in_running_queue, expected_quit_call", [
    ("happy_path_both_queues", True, True, 1),
    ("happy_path_upload_only", True, False, 1),
    ("happy_path_running_only", False, True, 1),
    ("edge_case_neither_queue", False, False, 1),
  ])
  def test_remove_from_queue(self, mock_manager, test_id, in_upload_queue, in_running_queue, expected_quit_call):
    # Arrange
    mock_manager.upload_queue = []
    mock_manager.running_queue = []
    upload_task_thread = MagicMock()
    upload_task_thread.worker_thread.quit = MagicMock()

    if in_upload_queue:
      mock_manager.upload_queue.append(upload_task_thread)
    if in_running_queue:
      mock_manager.running_queue.append(upload_task_thread)

    # Act
    mock_manager.remove_from_queue(upload_task_thread)

    # Assert
    if in_upload_queue:
      assert upload_task_thread not in mock_manager.upload_queue
    if in_running_queue:
      assert upload_task_thread not in mock_manager.running_queue
    assert upload_task_thread.worker_thread.quit.call_count == expected_quit_call

  @pytest.mark.parametrize(
    "test_id, number_of_concurrent_uploads, upload_queue_size, cancelled, expected_started_count",
    [  # Success path tests
      ("SuccessCase-1", 2, 3, False, 2),  # Test with queue larger than concurrent uploads
      ("SuccessCase-2", 3, 3, False, 3),  # Test with queue equal to concurrent uploads
      ("SuccessCase-3", 4, 1, False, 1),  # Test with queue smaller than concurrent uploads

      # Edge cases
      ("EdgeCase-1", 1, 0, False, 0),  # Test with empty queue
      ("EdgeCase-2", 0, 3, False, 0),  # Test with zero concurrent uploads

      # Error cases
      ("ErrorCase-1", 2, 3, True, 0),  # Test with task cancelled immediately
    ])
  def test_start_task(self, mocker, mock_manager, test_id, number_of_concurrent_uploads, upload_queue_size, cancelled,
                      expected_started_count):
    # Arrange
    mock_manager.cancelled = cancelled
    mock_manager.number_of_concurrent_uploads = number_of_concurrent_uploads
    mock_manager.running_queue = []
    mock_manager.upload_queue = [get_mock_task_thread(mocker, test_id == "ErrorCase-1") for _ in
                                 range(upload_queue_size)]

    # Act
    with mocker.patch('pasta_eln.dataverse.upload_queue_manager.sleep', return_value=None):
      start_task = Thread(target=mock_manager.start_task, args=())

      def cancel_queue_manager():
        time.sleep(2)
        mock_manager.cancelled = True

      cancel_task = Thread(target=lambda: cancel_queue_manager(), args=())
      start_task.start()
      time.sleep(1)
      cancel_task.start()
      start_task.join()

    # Assert
    assert len(mock_manager.running_queue) == expected_started_count
    for task_thread in mock_manager.upload_queue:
      if task_thread in mock_manager.running_queue:
        task_thread.task.start.emit.assert_called_once()
      else:
        task_thread.task.start.emit.assert_not_called()

  @pytest.mark.parametrize("test_id", [("success_path_1")])
  def test_cleanup_success_path(self, mocker, mock_manager, test_id):
    # Arrange
    mock_manager.empty_upload_queue = mocker.MagicMock()
    mock_base_cleanup = mocker.MagicMock()
    mocker.patch('pasta_eln.dataverse.generic_task_object.GenericTaskObject.cleanup', side_effect=mock_base_cleanup)

    # Act
    mock_manager.cleanup()

    # Assert
    mock_manager.logger.info.assert_called_with("Cleaning up upload manager..")
    mock_manager.empty_upload_queue.assert_called_once()
    mock_base_cleanup.assert_called_once()

  @pytest.mark.parametrize("test_id, exception, expected_call_count",
                           [("error_case_exception_in_super_cleanup", Exception, 0), ])
  def test_cleanup_error_cases(self, mocker, mock_manager, test_id, exception, expected_call_count):
    # Arrange
    mock_manager.empty_upload_queue = mocker.MagicMock()
    mocker.patch('pasta_eln.dataverse.generic_task_object.GenericTaskObject.cleanup', side_effect=exception)

    # Act & Assert
    with pytest.raises(Exception):
      mock_manager.cleanup()
    mock_manager.logger.info.assert_called_with("Cleaning up upload manager..")
    assert mock_manager.empty_upload_queue.call_count == expected_call_count

  @pytest.mark.parametrize("test_id, upload_tasks_count",
                           [("happy_path_single_task", 1), ("happy_path_multiple_tasks", 3),
                            ("happy_path_no_tasks", 0), ], ids=str)
  def test_empty_upload_queue_happy_path(self, mocker, mock_manager, test_id, upload_tasks_count):
    # Arrange
    mock_manager.upload_queue = [get_mock_task_thread(mocker) for _ in range(upload_tasks_count)]

    # Act
    mock_manager.empty_upload_queue()

    # Assert
    assert len(mock_manager.upload_queue) == 0, "Upload queue should be empty after emptying"
    for task in mock_manager.upload_queue:
      task.quit.assert_called_once()
    mock_manager.logger.info.assert_called_once_with("Emptying upload queue..")

  # Edge cases
  # No edge cases are identified for this function as it handles the queue regardless of its state

  # Error cases
  # Assuming that quit() method could raise an exception
  @pytest.mark.parametrize("test_id, upload_tasks_count, exception, call_count",
                           [("error_quit_exception_single_task", 1, Exception("Task quit failed"), 1),
                            ("error_quit_exception_multiple_tasks", 3, Exception("Task quit failed"), 3), ], ids=str)
  def test_empty_upload_queue_error_cases(self, mocker, mock_manager, test_id, upload_tasks_count, exception,
                                          call_count):
    # Arrange
    mock_manager.upload_queue = [get_mock_task_thread(mocker) for _ in range(upload_tasks_count)]
    for task in mock_manager.upload_queue:
      task.quit.side_effect = exception

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
      mock_manager.empty_upload_queue()
    assert str(exc_info.value) == "Task quit failed", "Exception message should match the expected one"
    mock_manager.logger.info.assert_called_with("Emptying upload queue..")

  @pytest.mark.parametrize("test_id", [
    ("success_path"),
    ("super_method_failure"),
    ("cancel_all_failure")
  ])
  def test_cancel_task(self, mocker, mock_manager, test_id):
    # Arrange
    mock_manager.cancel_all_queued_tasks_and_empty_queue = MagicMock()
    mocker.patch('pasta_eln.dataverse.upload_queue_manager.super')

    if test_id == "super_method_failure":
      with mocker.patch.object(UploadQueueManager, "cancel_task", side_effect=Exception("Super method failure")):
        # Act
        with pytest.raises(Exception) as exc_info:
          mock_manager.cancel_task()
        # Assert
        assert "Super method failure" in str(exc_info.value), "Exception message should be 'Super method failure'"
    elif test_id == "cancel_all_failure":
      mock_manager.cancel_all_queued_tasks_and_empty_queue.side_effect = Exception("Cancel all failure")
      # Act
      with pytest.raises(Exception) as exc_info:
        mock_manager.cancel_task()
      # Assert
      mock_manager.logger.info.assert_called_once_with("Cancelling upload manager..")
      assert "Cancel all failure" in str(exc_info.value), "Exception message should be 'Cancel all failure'"
    else:
      # Act
      mock_manager.cancel_task()
      # Assert
      mock_manager.logger.info.assert_called_once_with("Cancelling upload manager..")
      assert mock_manager.cancel_all_queued_tasks_and_empty_queue.called, "Expected cancel_all_queued_tasks_and_empty_queue to be called"

  @pytest.mark.parametrize("test_id, parallel_uploads_count, expected",
                           [  # Success path tests with various realistic test values
                             ("SuccessCase-1", 1, 1), ("SuccessCase-2", 5, 5), ("SuccessCase-3", 10, 10),

                             # Edge cases
                             ("EdgeCase-1", 0, 0),  # Minimum value for parallel uploads
                             ("EdgeCase-2", 100, 100),  # High value for parallel uploads
                           ])
  def test_set_concurrent_uploads(self, mocker, test_id, parallel_uploads_count, expected):
    # Arrange
    mock_db_api = mocker.MagicMock()
    mock_logger = mocker.MagicMock()
    mock_config_model = ConfigModel()
    mock_config_model.parallel_uploads_count = parallel_uploads_count
    mock_db_api.get_config_model.return_value = mock_config_model
    mocker.patch('pasta_eln.dataverse.upload_queue_manager.DatabaseAPI', return_value=mock_db_api)
    upload_queue_manager = UploadQueueManager()
    upload_queue_manager.db_api = mock_db_api
    upload_queue_manager.logger = mock_logger
    mock_db_api.get_config_model.reset_mock()

    # Act
    upload_queue_manager.set_concurrent_uploads()

    # Assert
    mock_db_api.get_config_model.assert_called_once()
    mock_logger.info.assert_called_once_with("Resetting number of concurrent uploads..")
    assert upload_queue_manager.number_of_concurrent_uploads == expected, f"Test ID {test_id}: Expected number_of_concurrent_uploads to be {expected}, got {upload_queue_manager.number_of_concurrent_uploads}"

  @pytest.mark.parametrize("test_id, upload_queue_size", [
    ("success_path_single_task", 1),  # Testing with a single task in the queue
    ("success_path_multiple_tasks", 5),  # Testing with multiple tasks in the queue
    ("edge_case_empty_queue", 0),  # Testing with an empty queue
  ], ids=str)
  def test_cancel_all_queued_tasks_and_empty_queue(self, mocker, mock_manager, test_id, upload_queue_size):
    # Arrange
    mock_manager.upload_queue = [mocker.MagicMock() for _ in range(upload_queue_size)]
    mock_manager.empty_upload_queue = mocker.MagicMock()
    mock_manager.logger = mocker.MagicMock()

    # Act
    mock_manager.cancel_all_queued_tasks_and_empty_queue()

    # Assert
    # Verify that each task's cancel method was called once for each task in the queue
    for task in mock_manager.upload_queue:
      task.task.cancel.emit.assert_called_once()
    # Verify that the empty_upload_queue method was called once
    mock_manager.empty_upload_queue.assert_called_once()
    # Verify that a log message was emitted
    mock_manager.logger.info.assert_called_once_with("Cancelling upload queue and the empty the upload queue..")

  @pytest.mark.parametrize("test_id, exception, expected_log_message", [
    ("error_case_exception_during_cancel", RuntimeError("Task cancel failed"), "Task cancel failed"),
  ], ids=str)
  def test_cancel_all_queued_tasks_and_empty_queue_with_errors(self, mocker, mock_manager, test_id, exception,
                                                               expected_log_message):
    # Arrange
    task_mock = mocker.MagicMock()
    task_mock.task.cancel.emit.side_effect = exception  # Simulate an exception when cancel is called
    mock_manager.upload_queue = [task_mock]
    mock_manager.empty_upload_queue = mocker.MagicMock()
    mock_manager.logger = mocker.MagicMock()

    # Act
    with pytest.raises(RuntimeError) as exc_info:
      mock_manager.cancel_all_queued_tasks_and_empty_queue()

    # Assert
    assert str(exc_info.value) == expected_log_message
    mock_manager.empty_upload_queue.assert_not_called()
    # Verify that a log message was emitted before the exception
    mock_manager.logger.info.assert_called_once_with("Cancelling upload queue and the empty the upload queue..")
