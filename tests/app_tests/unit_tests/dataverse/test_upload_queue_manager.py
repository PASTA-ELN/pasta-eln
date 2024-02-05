#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_upload_queue_manager.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest

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


def get_mock_task_thread(mocker):
  mock = mocker.MagicMock(spec=TaskThreadExtension)
  mock.task = mocker.MagicMock()
  mock.task.id = mocker.MagicMock()
  mock.worker_thread = mocker.MagicMock()
  return mock


class TestUploadQueueManager:

  def test_initialize(self, mock_manager):
    # Assert
    mock_manager.logger.mock_logger_constructor.assert_any_call(
      'pasta_eln.dataverse.generic_task_object.UploadQueueManager')
    mock_manager.set_concurrent_uploads.assert_called_once()
    assert len(mock_manager.upload_queue) == 0
    assert len(mock_manager.running_queue) == 0
    mock_manager.db_api.mock_db_constructor.assert_called_once()

  @pytest.mark.parametrize("test_id, concurrent_uploads, tasks_to_add, expected_upload_queue_length", [
    ("success_01", 2, 1, 1),
    ("success_02", 2, 3, 3),
    ("success_03", 5, 10, 10),
  ])
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
  @pytest.mark.parametrize("test_id, concurrent_uploads, tasks_to_add, tasks_to_remove, expected_upload_queue_length", [
    ("edge_01", 2, 2, 1, 1),
    ("edge_02", 2, 5, 5, 0),
    ("edge_03", 5, 10, 3, 7),
  ])
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
  @pytest.mark.parametrize(
    "test_id, concurrent_uploads, tasks_to_add, expected_upload_queue_length", [
      ("error_01", 2, 2, 2),
      ("error_02", 2, 5, 5),
      ("error_03", 5, 10, 10),
    ])
  def test_remove_from_queue_error_cases(self, mocker, mock_manager, test_id, concurrent_uploads,
                                         tasks_to_add,
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

  @pytest.mark.parametrize(
    "test_id, number_of_concurrent_uploads, upload_queue_size, cancelled, expected_started_count",
    [
      # Success path tests
      ("SuccessCase-1", 2, 3, False, 2),  # Test with queue larger than concurrent uploads
      ("SuccessCase-2", 3, 3, False, 3),  # Test with queue equal to concurrent uploads
      ("SuccessCase-3", 4, 1, False, 1),  # Test with queue smaller than concurrent uploads

      # Edge cases
      ("EdgeCase-1", 1, 0, False, 0),  # Test with empty queue
      ("EdgeCase-2", 0, 3, False, 0),  # Test with zero concurrent uploads

      # Error cases
      ("ErrorCase-1", 2, 3, True, 0),  # Test with task cancelled immediately
    ]
  )
  def test_start_task(self, mocker, mock_manager, test_id, number_of_concurrent_uploads, upload_queue_size, cancelled,
                      expected_started_count):
    # Arrange
    mock_manager.cancelled = cancelled
    mock_manager.number_of_concurrent_uploads = number_of_concurrent_uploads
    mock_manager.running_queue = []
    mock_manager.upload_queue = [get_mock_task_thread(mocker) for _ in range(upload_queue_size)]

    # Act
    with mocker.patch('pasta_eln.dataverse.upload_queue_manager.time.sleep', return_value=None):
      mock_manager.start_task()

    # Assert
    assert len(mock_manager.running_queue) == expected_started_count
    for task_thread in mock_manager.upload_queue:
      if task_thread in mock_manager.running_queue:
        task_thread.task.start.emit.assert_called_once()
      else:
        task_thread.task.start.emit.assert_not_called()
