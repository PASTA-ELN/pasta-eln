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
    "test_id, _id, project_upload_items, parallel_uploads_count, dataverse_login_info, metadata", [
      ("Success1", "123", {"item1": "value1"}, 5, {"user": "test", "password": "test"},
       {"title": "Test Dataset"}),
      ("Success2", None, None, None, None, None),
      ("Success3", "456", {}, 0, {}, {}),
    ])
  def test_config_model_init_happy_path(self, test_id, _id, project_upload_items, parallel_uploads_count,
                                        dataverse_login_info, metadata):
    # Arrange - omitted as all input values are provided via test parameters

    # Act
    config_model = ConfigModel(_id, project_upload_items, parallel_uploads_count, dataverse_login_info, metadata)

    # Assert
    assert config_model._id == _id
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
    _id, project_upload_items, dataverse_login_info, metadata = None, None, None, None

    # Act
    config_model = ConfigModel(_id, project_upload_items, parallel_uploads_count, dataverse_login_info, metadata)

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
    _id = None

    # Act & Assert
    with pytest.raises(expected_exception):
      ConfigModel(_id, project_upload_items, parallel_uploads_count, dataverse_login_info, metadata)

  @pytest.mark.parametrize("input_value, expected, test_id", [
    ({"key": "value"}, {"key": "value"}, "dict_with_string"),
    ({1: "number", "str": 2}, {1: "number", "str": 2}, "dict_with_mixed_types"),
    (None, None, "none_value"),
    ({}, {}, "empty_dict")
  ])
  def test_project_upload_items_success_path(self, input_value, expected, test_id):
    # Arrange
    obj = ConfigModel()

    # Act
    obj.project_upload_items = input_value

    # Assert
    assert obj._project_upload_items == expected, "The project_upload_items did not set correctly for valid inputs."

  @pytest.mark.parametrize("input_value, expected_exception, test_id", [
    ("string", IncorrectParameterError, "string_instead_of_dict"),
    (123, IncorrectParameterError, "number_instead_of_dict"),
    ([], IncorrectParameterError, "list_instead_of_dict"),
    (True, IncorrectParameterError, "bool_instead_of_dict")
  ])
  def test_project_upload_items_error_cases(self, input_value, expected_exception, test_id):
    # Arrange
    obj = ConfigModel()

    # Act & Assert
    with pytest.raises(expected_exception) as exc_info:
      obj.project_upload_items = input_value
    assert f"Expected dictionary for upload_items but got {type(input_value)}" in str(
      exc_info.value), "Incorrect error message for invalid inputs."

  @pytest.mark.parametrize("value, expected, test_id", [
    (1, 1, "single_upload"),
    (5, 5, "multiple_uploads"),
    (None, None, "no_parallel_upload"),
    (0, 0, "zero_uploads")  # Assuming 0 is a valid value indicating no parallel uploads
  ])
  def test_parallel_uploads_count_success_path(self, value, expected, test_id):
    # Arrange
    config = ConfigModel()

    # Act
    config.parallel_uploads_count = value

    # Assert
    assert config._parallel_uploads_count == expected, "The parallel_uploads_count should be set correctly for valid inputs"

  # Test cases for various error cases
  @pytest.mark.parametrize("value, test_id", [
    ("string", "string_input"),
    (1.5, "float_input"),
    ([], "list_input"),
    ({}, "dict_input"),
    ((), "tuple_input")
  ])
  def test_parallel_uploads_count_error_cases(self, value, test_id):
    # Arrange
    config = ConfigModel()

    # Act & Assert
    with pytest.raises(IncorrectParameterError) as exc_info:
      config.parallel_uploads_count = value
    assert str(
      exc_info.value) == f"Expected integer for parallel_uploads_count but got {type(value)}", "An IncorrectParameterError should be raised for invalid input types"

  @pytest.mark.parametrize("input_value, expected, test_id", [
    ({"username": "user", "password": "pass"}, {"username": "user", "password": "pass"},
     pytest.param(id="dict_with_credentials")),
    (None, None, pytest.param(id="none_as_value")),
    ({}, {}, pytest.param(id="empty_dict")),
    ({"api_token": "12345"}, {"api_token": "12345"}, pytest.param(id="dict_with_api_token"))
  ])
  def test_dataverse_login_info_success_path(self, input_value, expected, test_id):
    # Arrange
    config_model = ConfigModel()

    # Act
    config_model.dataverse_login_info = input_value

    # Assert
    assert config_model._dataverse_login_info == expected, "The dataverse_login_info should be set correctly for valid inputs."

  @pytest.mark.parametrize("input_value, expected_exception, expected_message, test_id", [
    ("", IncorrectParameterError, "Expected dictionary for dataverse_login_info but got <class 'str'>",
     pytest.param(id="string_instead_of_dict")),
    (123, IncorrectParameterError, "Expected dictionary for dataverse_login_info but got <class 'int'>",
     pytest.param(id="int_instead_of_dict")),
    ([], IncorrectParameterError, "Expected dictionary for dataverse_login_info but got <class 'list'>",
     pytest.param(id="list_instead_of_dict")),
    (True, IncorrectParameterError, "Expected dictionary for dataverse_login_info but got <class 'bool'>",
     pytest.param(id="bool_instead_of_dict"))
  ])
  def test_dataverse_login_info_error_cases(self, input_value, expected_exception, expected_message, test_id):
    # Arrange
    config_model = ConfigModel()

    # Act & Assert
    with pytest.raises(expected_exception) as exc_info:
      config_model.dataverse_login_info = input_value
    assert str(
      exc_info.value) == expected_message, "IncorrectParameterError should be raised with the correct message for invalid inputs."

  @pytest.mark.parametrize("initial_value, expected_exception", [
    ({"api_key": "123", "dataverse_url": "http://example.com"}, None),  # Success path
    ({}, None),  # Edge case: Empty initial value
  ], ids=["happy-path", "edge-case-empty"])
  def test_dataverse_login_info_deletion(self, initial_value, expected_exception):
    # Arrange
    instance = ConfigModel()  # Assuming YourClassName is the class containing the dataverse_login_info property
    if initial_value is not None:
      instance._dataverse_login_info = initial_value  # Directly setting the protected attribute for test setup

    # Act
    if expected_exception:
      with pytest.raises(expected_exception):
        del instance.dataverse_login_info
    else:
      del instance.dataverse_login_info

    # Assert
    if not expected_exception:
      with pytest.raises(AttributeError):
        _ = instance._dataverse_login_info  # Accessing the deleted attribute should raise an AttributeError

  @pytest.mark.parametrize("input_value, expected, test_id", [
    ({"key": "value"}, {"key": "value"}, "simple_dict"),
    ({}, {}, "empty_dict"),
    (None, None, "none_value")
  ])
  def test_metadata_setter_happy_path(self, input_value, expected, test_id):
    # Arrange
    config_model = ConfigModel()

    # Act
    config_model.metadata = input_value

    # Assert
    assert config_model._metadata == expected, "The metadata should be set correctly for valid inputs."

  @pytest.mark.parametrize("input_value, test_id", [
    (["list", "not", "dict"], "list_instead_of_dict"),
    ("string_value", "string_instead_of_dict"),
    (12345, "int_instead_of_dict"),
    (True, "bool_instead_of_dict")
  ])
  def test_metadata_setter_error_cases(self, input_value, test_id):
    # Arrange
    config_model = ConfigModel()

    # Act & Assert
    with pytest.raises(IncorrectParameterError) as exc_info:
      config_model.metadata = input_value
    assert str(exc_info.value) == f"Expected dictionary for metadata but got {type(input_value)}", \
      "An IncorrectParameterError should be raised for invalid input types."

  @pytest.mark.parametrize("metadata, expected_exception", [
    ({"key": "value"}, None),  # Happy path
    ([], None),  # Edge case: Empty list
    ({}, None),  # Edge case: Empty dict
  ], ids=["happy-path-dict", "edge-case-empty-list", "edge-case-empty-dict"])
  def test_metadata_deletion(self, metadata, expected_exception):
    config_model = ConfigModel()

    # Arrange
    if metadata is not None:
      config_model._metadata = metadata  # Directly setting _metadata for testing purpose

    # Act and Assert
    if expected_exception:
      with pytest.raises(expected_exception):
        del config_model.metadata
    else:
      del config_model.metadata
      with pytest.raises(AttributeError):
        _ = config_model._metadata  # Accessing _metadata after deletion should raise AttributeError

  @pytest.mark.parametrize("initial_upload_items", [
    pytest.param([], id="empty_list"),  # Testing with no upload items
    pytest.param(["item1", "item2"], id="multiple_items"),  # Testing with multiple upload items
    pytest.param(["item"], id="single_item"),  # Testing with a single upload item
  ])
  def test_project_upload_items_deleter(self, initial_upload_items):
    # Arrange
    project = ConfigModel()
    project._project_upload_items = initial_upload_items  # Directly setting the protected attribute for testing

    # Act
    del project.project_upload_items

    # Assert
    with pytest.raises(AttributeError):
      _ = project._project_upload_items  # Accessing the deleted attribute should raise an AttributeError

  @pytest.mark.parametrize("initial_value, expected_exception, test_id", [
    (10, None, "happy_path_no_exception"),
    (1, None, "happy_path_min_value")
  ])
  def test_parallel_uploads_count_deletion(self, initial_value, expected_exception, test_id):
    # Arrange
    config = ConfigModel()
    if initial_value is not None:
      config._parallel_uploads_count = initial_value  # Directly setting for test, assuming a setter exists

    # Act
    del_exception = None
    try:
      del config.parallel_uploads_count
    except Exception as e:
      del_exception = type(e)

    # Assert
    if expected_exception:
      assert del_exception == expected_exception, f"Expected {expected_exception} but got {del_exception}"
    else:
      assert not hasattr(config, '_parallel_uploads_count'), "parallel_uploads_count should be deleted"
