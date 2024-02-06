#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_upload_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest

from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError
from pasta_eln.dataverse.upload_model import UploadModel


# Success path tests with various realistic test values
class TestDataverseUploadModel:

  @pytest.mark.parametrize(
    "test_id, identifier, revision, data_type, project_name, project_doc_id, status, finished_date_time, log, dataverse_url",
    [
      ("Success-1", "123", "1.0", "dataset", "ProjectX", "erwerwerwer23424", "completed", "2023-04-01T12:00:00Z",
       "No errors.",
       "http://example.com/dataverse/123"),
      ("Success-2", "456", "2.0", None, "ProjectY", "dsfsfrwer23424", "in_progress", "2023-04-02T12:00:00Z",
       "Processing.",
       "http://example.com/dataverse/456"),
      # Add more test cases as needed
    ])
  def test_instantiation(self,
                         test_id,
                         identifier,
                         revision,
                         data_type,
                         project_name,
                         project_doc_id,
                         status,
                         finished_date_time,
                         log,
                         dataverse_url):
    # Arrange
    expected_data_type = 'dataverse_upload' if data_type is None else data_type

    # Act
    model = UploadModel(identifier, revision, data_type, project_name, project_doc_id, status, finished_date_time, log,
                        dataverse_url)

    # Assert
    assert model.id == identifier
    assert model.rev == revision
    assert model.data_type == expected_data_type
    assert model.project_name == project_name
    assert model.project_doc_id == project_doc_id
    assert model.status == status
    assert model.finished_date_time == finished_date_time
    assert model.log == log
    assert model.dataverse_url == dataverse_url

  # Edge cases
  @pytest.mark.parametrize(
    "test_id, identifier, revision, data_type, project_name, project_doc_id, status, finished_date_time, log, dataverse_url",
    [
      ("EdgeCase-1", "", "", "", "", "", "", "", "", ""),  # Empty strings
      ("EdgeCase-2", None, None, None, None, None, None, None, "", None),  # None values
      # Add more test cases as needed
    ])
  def test_edge_cases(self,
                      test_id,
                      identifier,
                      revision,
                      data_type,
                      project_name,
                      project_doc_id,
                      status,
                      finished_date_time,
                      log,
                      dataverse_url):
    # Arrange
    expected_data_type = 'dataverse_upload' if data_type is None else data_type

    # Act
    model = UploadModel(identifier, revision, data_type, project_name, project_doc_id, status, finished_date_time, log,
                        dataverse_url)

    # Assert
    assert model.id == identifier
    assert model.rev == revision
    assert model.data_type == expected_data_type
    assert model.project_name == project_name
    assert model.project_doc_id == project_doc_id
    assert model.status == status
    assert model.finished_date_time == finished_date_time
    assert model.log == log
    assert model.dataverse_url == dataverse_url

  @pytest.mark.parametrize("test_id, attributes, expected", [
    # Success path tests with various realistic test values
    ("Success-1",
     {
       "id": "value1",
       "rev": "value2",
       "data_type": "value3",
       "project_name": "value4",
       "project_doc_id": "value5",
       "status": "value6",
       "finished_date_time": "value7",
       "log": "value8",
       "dataverse_url": "value9"
     }, [("_id", "value1"),
         ("_rev", "value2"),
         ("data_type", "value3"),
         ("project_name", "value4"),
         ("project_doc_id", "value5"),
         ("status", "value6"),
         ("finished_date_time", "value7"),
         ("log", "value8\n"),
         ("dataverse_url", "value9")]),
    ("Success-2", {}, [('_id', None),
                       ('_rev', None),
                       ('data_type', 'dataverse_upload'),
                       ('project_name', None),
                       ('project_doc_id', None),
                       ('status', None),
                       ('finished_date_time', None),
                       ('log', ''),
                       ('dataverse_url', None)]),  # Testing with an empty object

    # Edge cases
    # Assuming edge cases for this function might involve special attribute types or large numbers of attributes
    ("EdgeCase-1", {"id": None, "rev": True}, [('_id', None),
                                               ('_rev', True),
                                               ('data_type', 'dataverse_upload'),
                                               ('project_name', None),
                                               ('project_doc_id', None),
                                               ('status', None),
                                               ('finished_date_time', None),
                                               ('log', ''),
                                               ('dataverse_url', None)]),
  ])
  def test_iter_method(self, test_id, attributes, expected):
    # Arrange
    instance = UploadModel()
    for attr, value in attributes.items():
      setattr(instance, attr, value)

    # Act
    result = list(instance.__iter__())

    # Assert
    assert result == expected, f"Failed on {test_id}"

  @pytest.mark.parametrize("test_id, attributes, expected", [
    # Success path tests with various realistic test values
    ("Success-1",
     {
       "id": "value1",
       "rev": "value2",
       "data_type": "value3",
       "project_name": "value4",
       "project_doc_id": "value5",
       "status": "value6",
       "finished_date_time": "value7",
       "log": "value8",
       "dataverse_url": "value9"
     }, {'_id': 'value1',
         '_rev': 'value2',
         'data_type': 'value3',
         'project_name': 'value4',
         "project_doc_id": "value5",
         'status': 'value6',
         'finished_date_time': 'value7',
         'log': 'value8\n',
         'dataverse_url': 'value9'
         })
  ])
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
    ("ERR-3", {"status": 123}, IncorrectParameterError, "Expected string type for status but got <class 'int'>"),
    ("ERR-4", {"finished_date_time": 123}, IncorrectParameterError,
     "Expected string type for finished_date_time but got <class 'int'>"),
    ("ERR-5", {"log": 123}, IncorrectParameterError, "Expected string type for log but got <class 'int'>"),
    ("ERR-6", {"dataverse_url": 123}, IncorrectParameterError,
     "Expected string type for dataverse_url but got <class 'int'>"),
    # Add more error cases for other type mismatches
  ])
  def test_upload_model_error_cases(self, test_id, kwargs, expected_exception, expected_message):
    # Arrange
    # Act & Assert
    with pytest.raises(expected_exception) as exc_info:
      UploadModel(**kwargs)
    assert str(exc_info.value) == expected_message
