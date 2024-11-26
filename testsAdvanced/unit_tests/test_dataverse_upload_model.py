#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_upload_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import inspect

import pytest

from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError
from pasta_eln.dataverse.upload_model import UploadModel


# Success path tests with various realistic test values
class TestDataverseUploadModel:
  # Success path tests with various realistic test values
  @pytest.mark.parametrize(
    "test_id, _id, data_type, project_name, project_doc_id, status, created_date_time, finished_date_time, log, dataverse_url",
    [
      ("Success01", "123", "dataset", "Project X", "doc-456", "completed", "2023-01-01T12:00:00",
       "2023-01-01T12:00:00",
       "Upload successful\n", "http://example.com/dataverse"),
      ("Success02", None, None, None, None, None, None, None, "", None),  # Testing defaults
      ("Success03", "124", "image", "Project Y", "doc-789", "in progress", "2023-01-01T12:00:00",
       "2023-01-02T13:00:00", "Uploading\n",
       "http://example.com/dataverse2"),
    ])
  def test_upload_model_success_path(self, test_id, _id, data_type, project_name, project_doc_id, status,
                                     created_date_time, finished_date_time, log, dataverse_url):
    # Arrange

    # Act
    upload_model = UploadModel(_id, data_type, project_name, project_doc_id, status, created_date_time,
                               finished_date_time, log,
                               dataverse_url)

    # Assert
    assert upload_model._id == _id
    assert upload_model.data_type == (data_type if data_type is not None else 'dataverse_upload')
    assert upload_model.project_name == project_name
    assert upload_model.project_doc_id == project_doc_id
    assert upload_model.status == status
    assert upload_model.created_date_time == created_date_time
    assert upload_model.finished_date_time == finished_date_time
    assert upload_model.log == (log + "\n" if log and not log.endswith('\n') else log)
    assert upload_model.dataverse_url == dataverse_url

  # Various edge cases
  @pytest.mark.parametrize("test_id, log, expected_log", [
    ("EC01", "Log entry", "Log entry\n"),  # Test log formatting
    ("EC02", "Log entry\n", "Log entry\n"),  # Test log formatting with newline
  ])
  def test_upload_model_log_edge_cases(self, test_id, log, expected_log):
    # Arrange
    upload_model = UploadModel(log=log)

    # Act
    # No action required, testing initial state

    # Assert
    assert upload_model.log == expected_log

  # Various error cases
  @pytest.mark.parametrize("test_id, param, value", [
    ("ERR01", "data_type", 123),  # Non-string data_type
    ("ERR02", "project_name", 456),  # Non-string project_name
    ("ERR03", "project_doc_id", 789),  # Non-string project_doc_id
    ("ERR04", "status", 101112),  # Non-string status
    ("ERR05", "finished_date_time", 131415),  # Non-string finished_date_time
    ("ERR06", "log", 161718),  # Non-string log
    ("ERR07", "dataverse_url", 192021),  # Non-string dataverse_url
    ("ERR08", "created_date_time", 131415),  # Non-string finished_date_time
  ])
  def test_upload_model_init_error_cases(self, test_id, param, value):
    # Arrange
    kwargs = {
      "_id": None,
      "data_type": None,
      "project_name": None,
      "project_doc_id": None,
      "status": None,
      "finished_date_time": None,
      "log": "",
      "dataverse_url": None,
      param: value,
    }
    # Act / Assert
    with pytest.raises(IncorrectParameterError):
      UploadModel(**kwargs)

  @pytest.mark.parametrize("test_id, attributes, expected", [  # Success path tests with various realistic test values
    ("Success-1",
     {"id": "value1", "data_type": "value3", "project_name": "value4", "project_doc_id": "value5",
      "status": "value6", "finished_date_time": "value7", "created_date_time": "value8", "log": "value9",
      "dataverse_url": "value10"},
     [("id", "value1"), ("data_type", "value3"), ("project_name", "value4"),
      ("project_doc_id", "value5"), ("status", "value6"), ("finished_date_time", "value7"),
      ("created_date_time", "value8"), ("log", "value9\n"),
      ("dataverse_url", "value10")]),
    ("Success-2", {},
     [('id', None), ('data_type', 'dataverse_upload'),
      ('project_name', None), ('project_doc_id', None), ('status', None),
      ('finished_date_time', None), ('created_date_time', None), ('log', ''),
      ('dataverse_url', None)]),
    # Testing with an empty object

    # Edge cases
    # Assuming edge cases for this function might involve special attribute types or large numbers of attributes
    ("EdgeCase-1", {"id": None},
     [('id', None), ('data_type', 'dataverse_upload'), ('project_name', None),
      ('project_doc_id', None), ('status', None), ('finished_date_time', None), ('created_date_time', None),
      ('log', ''),
      ('dataverse_url', None)]), ])
  def test_iter_method(self, test_id, attributes, expected):
    # Arrange
    instance = UploadModel()
    for attr, value in attributes.items():
      setattr(instance, attr, value)

    # Act
    result = list(instance.__iter__())

    # Assert
    assert result == expected, f"Failed on {test_id}"

  @pytest.mark.parametrize("test_id, attributes, expected", [  # Success path tests with various realistic test values
    ("Success-1",
     {"id": "value1", "data_type": "value3", "project_name": "value4", "project_doc_id": "value5",
      "status": "value6", "finished_date_time": "value7", "created_date_time": "value8", "log": "value9",
      "dataverse_url": "value10"},
     {'id': 'value1', 'data_type': 'value3', 'project_name': 'value4', "project_doc_id": "value5",
      'status': 'value6', 'finished_date_time': 'value7', "created_date_time": "value8", 'log': 'value9\n',
      'dataverse_url': 'value10'})])
  def test_dict_method(self, test_id, attributes, expected):
    # Arrange
    instance = UploadModel()
    for attr, value in attributes.items():
      setattr(instance, attr, value)

    # Act
    result = dict(instance)

    # Assert
    assert result == expected, f"Failed on {test_id}"

  # Error cases
  @pytest.mark.parametrize("test_id, kwargs, expected_exception, expected_message", [
    ("ERR-1", {"data_type": 123}, IncorrectParameterError, "Expected string type for data_type but got <class 'int'>"),
    ("ERR-2", {"project_name": 123}, IncorrectParameterError,
     "Expected string type for project_name but got <class 'int'>"),
    ("ERR-3", {"status": 123}, IncorrectParameterError, "Expected string type for status but got <class 'int'>"), (
        "ERR-4", {"finished_date_time": 123}, IncorrectParameterError,
        "Expected string type for finished_date_time but got <class 'int'>"),
    ("ERR-5", {"log": 123}, IncorrectParameterError, "Expected string type for log but got <class 'int'>"), (
        "ERR-6", {"dataverse_url": 123}, IncorrectParameterError,
        "Expected string type for dataverse_url but got <class 'int'>"),
    ("ERR-7", {"created_date_time": 123}, IncorrectParameterError,
     "Expected string type for created_date_time but got <class 'int'>"),
    # Add more error cases for other type mismatches
  ])
  def test_upload_model_error_cases(self, test_id, kwargs, expected_exception, expected_message):
    # Arrange
    # Act & Assert
    with pytest.raises(expected_exception) as exc_info:
      UploadModel(**kwargs)
    assert str(exc_info.value) == expected_message

  def test_attribute_setter_success(self):
    # Arrange
    instance = UploadModel()

    # Act & Assert
    for i in inspect.getmembers(UploadModel):
      if not i[0].startswith('_') and not inspect.ismethod(i[1]):
        setattr(instance, i[0], f"Test {i[0]}")

        assert getattr(instance, i[0]) == f"Test {i[0]}" if i[0] != 'log' else f"Test {i[0]}\n", f"Failed on {i[0]}"

  @pytest.mark.parametrize("test_input, test_id", [
    (123, "integer"),
    (12.34, "float"),
    ([], "empty_list"),
    ({}, "empty_dict"),
    (True, "boolean")
  ])
  def test_setter_error_cases(self, test_input, test_id):
    # Arrange
    instance = UploadModel()

    # Act & Assert
    for i in inspect.getmembers(UploadModel):
      if not i[0].startswith('_') and not inspect.ismethod(i[1]) and i[0] not in ['id', 'rev']:
        with pytest.raises(IncorrectParameterError) as exc_info:
          setattr(instance, i[0], test_input)
        assert str(exc_info.value) == f"Expected string type for {i[0]} but got {type(test_input)}", \
          "An IncorrectParameterError should be raised for non-string inputs."

  @pytest.mark.parametrize("initial_value", [
    ("Test 1"),
    ("")])
  def test_deleter(self, initial_value):
    # Arrange
    instance = UploadModel()

    # Act & Assert
    for i in inspect.getmembers(UploadModel):
      if not i[0].startswith('_') and not inspect.ismethod(i[1]) and i[0] not in ['id', 'rev']:
        setattr(instance, i[0], initial_value)

        # Act and Assert
        delattr(instance, i[0])
        with pytest.raises(AttributeError):  # Asserting that property is indeed deleted
          _ = getattr(instance, i[0])
