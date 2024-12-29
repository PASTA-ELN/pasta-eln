#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_progress_updater_thread.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest

from pasta_eln.dataverse.progress_updater_thread import ProgressUpdaterThread


class TestDataverseProgressUpdaterThread:

  @pytest.mark.parametrize('test_id', [
    ('success_path')
  ])
  def test_ProgressThread_init(self, mocker, test_id):
    # Arrange
    ProgressUpdaterThread.cancel = mocker.MagicMock()
    ProgressUpdaterThread.finalize = mocker.MagicMock()
    mock_super = mocker.patch('pasta_eln.dataverse.progress_updater_thread.super')

    # Act
    instance = ProgressUpdaterThread()

    # Assert
    mock_super.assert_called_once()
    assert instance.cancelled == False, "Instance variable 'cancelled' should be initialized to False"
    assert instance.finalized == False, "Instance variable 'finalized' should be initialized to False"
    instance.finalize.connect.assert_called_with(
      instance.finalize_progress), 'finalize.connect should be called with finalize_progress method'
    instance.cancel.connect.assert_called_with(
      instance.cancel_progress), 'cancel.connect should be called with cancel_progress method'

  @pytest.mark.parametrize('cancelled_at, expected_progress, randint_values, test_id', [
    (None, list(range(1, 98, 4)) + [100], [4], 'success_path_no_early_finish'),
    (0, [1], [4], 'edge_case_finish_immediately'),
    (50, list(range(1, 54, 4)), [4], 'success_path_finish_midway'),
    (60, list(range(1, 62, 2)), [2], 'success_path_finish_in_between'),
    (95, list(range(1, 95, 3)), [3], 'edge_case_finish_just_before_end'),
  ], ids=['success_path_no_early_finish',
          'edge_case_finish_immediately',
          'success_path_finish_midway',
          'success_path_finish_in_between',
          'edge_case_finish_just_before_end'])
  def test_run(self, mocker, cancelled_at, expected_progress, randint_values, test_id):
    # Arrange
    mocker.patch('pasta_eln.dataverse.progress_updater_thread.time.sleep')
    mock_randint = mocker.patch('pasta_eln.dataverse.progress_updater_thread.random.randint')
    mock_randint.side_effect = randint_values
    progress_updater = ProgressUpdaterThread()
    progress_updater.progress_update = mocker.MagicMock()
    progress_updater.end = mocker.MagicMock()
    if cancelled_at is not None:
      progress_updater.cancelled = False

      def set_cancelled(value):
        progress_updater.cancelled = value >= cancelled_at

      progress_updater.progress_update.emit.side_effect = set_cancelled

    # Act
    progress_updater.run()

    # Assert
    progress_call_list = [mocker.call(progress) for progress in expected_progress]
    progress_updater.progress_update.emit.assert_has_calls(progress_call_list)
    progress_updater.end.emit.assert_called_once()

  @pytest.mark.parametrize('initial_state, expected_state', [
    (False, True),  # ID: 01 - Test transitioning from False to True
    (True, True),  # ID: 02 - Test confirming idempotency, starting from True remains True
  ], ids=['from_false_to_true', 'from_true_stays_true'])
  def test_cancel_progress(self, initial_state, expected_state):
    # Arrange
    progress_updater = ProgressUpdaterThread()
    progress_updater.cancelled = initial_state

    # Act
    progress_updater.cancel_progress()

    # Assert
    assert progress_updater.cancelled == expected_state, 'The cancelled flag should be set to True'

  @pytest.mark.parametrize('initial_finalized_state, expected_finalized_state', [
    (False, True),  # Test ID: 01 - Success path, attribute changes from False to True
    (True, True),  # Test ID: 02 - Edge case, attribute already True, should remain True
  ])
  def test_finalize_progress(self, initial_finalized_state, expected_finalized_state):
    # Arrange
    progress_updater = ProgressUpdaterThread()
    progress_updater.finalized = initial_finalized_state

    # Act
    progress_updater.finalize_progress()

    # Assert
    assert progress_updater.finalized == expected_finalized_state, 'finalize_progress should set finalized to True'
