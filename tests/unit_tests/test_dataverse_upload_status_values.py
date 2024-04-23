#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_upload_status_values.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.dataverse.upload_status_values import UploadStatusValues


class TestDataverseUploadStatusValues:
  # Parametrized test for checking all enum values
  @pytest.mark.parametrize("status, expected, test_id", [
    (UploadStatusValues.Queued, 1, "Queued"),
    (UploadStatusValues.Uploading, 2, "Uploading"),
    (UploadStatusValues.Cancelled, 3, "Cancelled"),
    (UploadStatusValues.Finished, 4, "Finished"),
    (UploadStatusValues.Error, 5, "Error"),
    (UploadStatusValues.Warning, 6, "Warning"),
  ])
  def test_upload_status_values(self, status, expected, test_id):
    # Act
    result = status.value

    # Assert
    assert result == expected, f"Expected {expected} but got {result}"

  # Test for checking the enum's iteration and coverage of all defined statuses
  @pytest.mark.parametrize("status, expected_name, test_id", [
    (UploadStatusValues.Queued, "Queued", "Queued_name"),
    (UploadStatusValues.Uploading, "Uploading", "Uploading_name"),
    (UploadStatusValues.Cancelled, "Cancelled", "Cancelled_name"),
    (UploadStatusValues.Finished, "Finished", "Finished_name"),
    (UploadStatusValues.Error, "Error", "Error_name"),
    (UploadStatusValues.Warning, "Warning", "Warning_name"),
  ])
  def test_upload_status_names(self, status, expected_name, test_id):
    # Act
    result = status.name

    # Assert
    assert result == expected_name, f"Expected {expected_name} but got {result}"

  # Test for ensuring the uniqueness of each enum value
  def test_upload_status_uniqueness(self):
    # Arrange
    statuses = [status.value for status in UploadStatusValues]

    # Act
    unique_statuses = set(statuses)

    # Assert
    assert len(statuses) == len(unique_statuses), "Expected all statuses to be unique"

  # Test for ensuring that adding a new status requires updating the tests
  def test_upload_status_completeness(self):
    # Arrange
    expected_number_of_statuses = 6

    # Act
    number_of_statuses = len(UploadStatusValues)

    # Assert
    assert number_of_statuses == expected_number_of_statuses, "Check if a new status has been added or removed"
