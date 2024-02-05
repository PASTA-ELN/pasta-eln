#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_generic_task_object.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from logging import Logger

import pytest

from pasta_eln.dataverse.generic_task_object import GenericTaskObject


class TestGenericTaskObject:
  @pytest.mark.parametrize(
    "test_id, initial_cancelled, initial_started, initial_cleaned, expected_cancelled, expected_started, expected_cleaned",
    [
      # Happy path tests
      ("success_case_1", False, False, False, False, True, False),  # Starting task from initial state
      ("success_case_2", True, False, False, False, True, False),  # Starting task from cancelled state

      # Edge case tests
      ("edge_case_1", False, True, False, False, True, False),  # Starting task when it's already started

    ])
  def test_generic_task_object(self, mocker, test_id, initial_cancelled, initial_started, initial_cleaned,
                               expected_cancelled,
                               expected_started, expected_cleaned):
    # Arrange
    mocker.patch('pasta_eln.dataverse.generic_task_object.next', return_value="test_id")
    mock_logger = mocker.MagicMock(spec=Logger)
    mocker.patch('pasta_eln.dataverse.task_thread_extension.logging.getLogger',
                 return_value=mock_logger)
    task = GenericTaskObject()
    task.cancelled = initial_cancelled
    task.started = initial_started
    task.cleaned = initial_cleaned

    # Act
    task.start.emit()

    # Assert
    assert task.cancelled == expected_cancelled
    assert task.started == expected_started
    assert task.cleaned == expected_cleaned

  @pytest.mark.parametrize("test_id, initial_cancelled, expected_cancelled", [
    # Success path tests
    ("success_case_1", False, True),  # Cancelling task from non-cancelled state

    # Edge case tests
    ("edge_case_1", True, True),  # Cancelling task when it's already cancelled

    # Error case tests
    # No error cases identified for cancel_task as it does not raise exceptions or handle erroneous input
  ])
  def test_cancel_task(self, mocker, test_id, initial_cancelled, expected_cancelled):
    # Arrange
    mocker.patch('pasta_eln.dataverse.generic_task_object.next', return_value="test_id")
    mock_logger = mocker.MagicMock(spec=Logger)
    mocker.patch('pasta_eln.dataverse.task_thread_extension.logging.getLogger',
                 return_value=mock_logger)
    task = GenericTaskObject()
    task.cancelled = initial_cancelled

    # Act
    task.cancel.emit()

    # Assert
    assert task.cancelled == expected_cancelled
    mock_logger.info.assert_called_once_with('Cancelling task, id: %s', 'test_id')

  @pytest.mark.parametrize("initial_cancelled, initial_started, expected_cancelled, expected_started", [
    # Test ID: #1 - Success path test where task is not started or cancelled
    (False, False, False, True),
    # Test ID: #2 - Success path test where task is already started but not cancelled
    (False, True, False, True),
    # Test ID: #3 - Success path test where task is cancelled but not started
    (True, False, False, True),
    # Test ID: #4 - Success path test where task is both started and cancelled
    (True, True, False, True),
  ])
  def test_start_task(self, mocker, initial_cancelled, initial_started, expected_cancelled, expected_started):
    # Arrange
    mocker.patch('pasta_eln.dataverse.generic_task_object.next', return_value="test_id")
    mock_logger = mocker.MagicMock(spec=Logger)
    mocker.patch('pasta_eln.dataverse.task_thread_extension.logging.getLogger',
                 return_value=mock_logger)
    task = GenericTaskObject()
    task.cancelled = initial_cancelled
    task.started = initial_started

    # Act
    task.start_task()

    # Assert
    assert task.cancelled == expected_cancelled, "The task's cancelled state did not match the expected value."
    assert task.started == expected_started, "The task's started state did not match the expected value."
    mock_logger.info.assert_called_once_with('Starting task, id: %s', 'test_id')

  @pytest.mark.parametrize("test_id, initial_cleaned, expected_cleaned", [
    # Success path tests
    ("success_case_1", False, True),  # Cleaning up task from non-cleaned state

    # Edge case tests
    ("edge_case_1", True, True),  # Cleaning up task when it's already cleaned

    # Error case tests
    # No error cases identified for cleanup as it does not raise exceptions or handle erroneous input
  ])
  def test_cleanup(self, mocker, test_id, initial_cleaned, expected_cleaned):
    # Arrange
    mocker.patch('pasta_eln.dataverse.generic_task_object.next', return_value="test_id")
    mock_logger = mocker.MagicMock(spec=Logger)
    mocker.patch('pasta_eln.dataverse.task_thread_extension.logging.getLogger',
                 return_value=mock_logger)
    task = GenericTaskObject()
    task.cleaned = initial_cleaned

    # Act
    task.cleanup()

    # Assert
    assert task.cleaned == expected_cleaned
    mock_logger.info.assert_called_once_with('Cleaning up task, id: %s', 'test_id')
