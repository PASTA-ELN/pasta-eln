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

  @pytest.mark.parametrize("test_id", [
    ("success_path")
  ])
  def test_ProgressThread_init(self, mocker, test_id):
    # Arrange
    ProgressUpdaterThread.cancel = mocker.MagicMock()
    mock_super = mocker.patch("pasta_eln.dataverse.progress_updater_thread.super")

    # Act
    instance = ProgressUpdaterThread()

    # Assert
    mock_super.assert_called_once()
    assert instance.finished == False, "Instance variable 'finished' should be initialized to False"
    instance.cancel.connect.assert_called_with(
      instance.cancel_progress), "cancel.connect should be called with cancel_progress method"

  @pytest.mark.parametrize("finished_at, expected_progress, randint_values, test_id", [
    (None, list(range(1, 98, 4)) + [100], [4], "success_path_no_early_finish"),
    (0, [1], [4], "edge_case_finish_immediately"),
    (50, list(range(1, 54, 4)) + [100], [4], "success_path_finish_midway"),
    (60, list(range(1, 62, 2)) + [100], [2], "success_path_finish_in_between"),
    (99, list(range(1, 97, 5)) + [100], [5], "edge_case_finish_just_before_end"),
  ], ids=["success_path_no_early_finish",
          "edge_case_finish_immediately",
          "success_path_finish_midway",
          "success_path_finish_in_between",
          "edge_case_finish_just_before_end"])
  def test_run(self, mocker, finished_at, expected_progress, randint_values, test_id):
    # Arrange
    mocker.patch("pasta_eln.dataverse.progress_updater_thread.time.sleep")
    mock_randint = mocker.patch("pasta_eln.dataverse.progress_updater_thread.random.randint")
    mock_randint.side_effect = randint_values
    progress_updater = ProgressUpdaterThread()
    progress_updater.progress_update = mocker.MagicMock()
    progress_updater.exit = mocker.MagicMock()
    if finished_at is not None:
      progress_updater.finished = False

      def set_finished(value):
        progress_updater.finished = value >= finished_at

      progress_updater.progress_update.emit.side_effect = set_finished

    # Act
    progress_updater.run()

    # Assert
    progress_call_list = [mocker.call(progress) for progress in expected_progress]
    progress_updater.progress_update.emit.assert_has_calls(progress_call_list)
    progress_updater.exit.assert_called_once()

  @pytest.mark.parametrize("initial_state, expected_state", [
    (False, True),  # ID: 01 - Test transitioning from False to True
    (True, True),  # ID: 02 - Test confirming idempotency, starting from True remains True
  ], ids=["from_false_to_true", "from_true_stays_true"])
  def test_cancel_progress(self, initial_state, expected_state):
    # Arrange
    progress_updater = ProgressUpdaterThread()
    progress_updater.finished = initial_state

    # Act
    progress_updater.cancel_progress()

    # Assert
    assert progress_updater.finished == expected_state, "The finished flag should be set to True"
