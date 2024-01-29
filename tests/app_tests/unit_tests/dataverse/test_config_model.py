#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_config_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.GUI.database_tests.config_model import ConfigModel
from pasta_eln.GUI.database_tests.incorrect_parameter_error import IncorrectParameterError


class TestConfigModel:

  # Happy path tests with various realistic test values
  @pytest.mark.parametrize(
    "test_id, _id, _rev, _upload_items, _parallel_uploads_count, _dataverse_login_info, _metadata",
    [
      ("success_case_full", "id123", "rev123", {"item1": "data1"}, 5, {"user": "test_user"},
       {"title": "Test Metadata"}),
      ("success_case_minimal", None, None, None, None, None, None),
      # Add more test cases as needed
    ], ids=lambda test_id: test_id)
  def test_init_happy_path(self, test_id, _id, _rev, _upload_items, _parallel_uploads_count, _dataverse_login_info,
                           _metadata):
    # Act
    instance = ConfigModel(_id, _rev, _upload_items, _parallel_uploads_count, _dataverse_login_info, _metadata)

    # Assert
    assert instance._id == _id
    assert instance._rev == _rev
    assert instance._upload_items == _upload_items
    assert instance._parallel_uploads_count == _parallel_uploads_count
    assert instance._dataverse_login_info == _dataverse_login_info
    assert instance._metadata == _metadata

  # Edge cases
  @pytest.mark.parametrize(
    "test_id, _id, _rev, _upload_items, _parallel_uploads_count, _dataverse_login_info, _metadata",
    [
      ("edge_case_empty_strings", "", "", {}, 0, {}, {}),
      # Add more edge cases as needed
    ], ids=lambda test_id: test_id)
  def test_init_edge_cases(self, test_id, _id, _rev, _upload_items, _parallel_uploads_count, _dataverse_login_info,
                           _metadata):
    # Act
    instance = ConfigModel(_id, _rev, _upload_items, _parallel_uploads_count, _dataverse_login_info, _metadata)

    # Assert
    assert instance._id == _id
    assert instance._rev == _rev
    assert instance._upload_items == _upload_items
    assert instance._parallel_uploads_count == _parallel_uploads_count
    assert instance._dataverse_login_info == _dataverse_login_info
    assert instance._metadata == _metadata

  # Error cases
  @pytest.mark.parametrize(
    "test_id, _id, _rev, _upload_items, _parallel_uploads_count, _dataverse_login_info, _metadata, expected_exception",
    [
      ("error_case_invalid_metadata", "123", "rev123", {"item1": "data1"}, 5, {"user": "test_user"}, "invalid_metadata",
       IncorrectParameterError),
      ("error_case_invalid_login_info", "123", "rev123", {"item1": "data1"}, 5, 1234, "invalid_metadata",
       IncorrectParameterError),
      # Add more error cases as needed
    ], ids=lambda test_id: test_id)
  def test_init_error_cases(self, test_id, _id, _rev, _upload_items, _parallel_uploads_count, _dataverse_login_info,
                            _metadata,
                            expected_exception):
    # Act & Assert
    with pytest.raises(expected_exception):
      ConfigModel(_id, _rev, _upload_items, _parallel_uploads_count, _dataverse_login_info, _metadata)
