#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_config_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError


class TestDataverseConfigModel:

  # Success path tests with various realistic test values
  @pytest.mark.parametrize(
    "test_id, _id, _rev, project_upload_items, parallel_uploads_count, dataverse_login_info, metadata", [
      ("Success1", "123", "rev1", {"item1": "value1"}, 5, {"user": "test", "password": "test"},
       {"title": "Test Dataset"}),
      ("Success2", None, None, None, None, None, None),
      ("Success3", "456", "rev2", {}, 0, {}, {}),
    ])
  def test_config_model_init_happy_path(self, test_id, _id, _rev, project_upload_items, parallel_uploads_count,
                                        dataverse_login_info, metadata):
    # Arrange - omitted as all input values are provided via test parameters

    # Act
    config_model = ConfigModel(_id, _rev, project_upload_items, parallel_uploads_count, dataverse_login_info, metadata)

    # Assert
    assert config_model._id == _id
    assert config_model._rev == _rev
    assert config_model.project_upload_items == project_upload_items
    assert config_model.parallel_uploads_count == parallel_uploads_count
    assert config_model.dataverse_login_info == dataverse_login_info
    assert config_model.metadata == metadata

  # Various edge cases
  @pytest.mark.parametrize("test_id, parallel_uploads_count", [
    ("EC1", -1),
    ("EC2", 100000),
  ])
  def test_config_model_parallel_uploads_edge_cases(self, test_id, parallel_uploads_count):
    # Arrange
    _id, _rev, project_upload_items, dataverse_login_info, metadata = None, None, None, None, None

    # Act
    config_model = ConfigModel(_id, _rev, project_upload_items, parallel_uploads_count, dataverse_login_info, metadata)

    # Assert
    assert config_model.parallel_uploads_count == parallel_uploads_count

  # Various error cases
  @pytest.mark.parametrize(
    "test_id, project_upload_items, parallel_uploads_count, dataverse_login_info, metadata, expected_exception", [
      ("ERR1", "not_a_dict", None, None, None, IncorrectParameterError),
      ("ERR2", None, "not_an_int", None, None, IncorrectParameterError),
      ("ERR3", None, None, "not_a_dict", None, IncorrectParameterError),
      ("ERR4", None, None, None, "not_a_dict", IncorrectParameterError),
    ])
  def test_config_model_init_error_cases(self, test_id, project_upload_items, parallel_uploads_count,
                                         dataverse_login_info,
                                         metadata, expected_exception):
    # Arrange
    _id, _rev = None, None

    # Act & Assert
    with pytest.raises(expected_exception):
      ConfigModel(_id, _rev, project_upload_items, parallel_uploads_count, dataverse_login_info, metadata)
