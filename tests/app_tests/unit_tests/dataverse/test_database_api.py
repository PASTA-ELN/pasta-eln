#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_database_api.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from logging import Logger

import pytest

from pasta_eln.dataverse.base_database_api import BaseDatabaseAPI
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.database_api import DatabaseAPI
from pasta_eln.dataverse.database_error import DatabaseError
from pasta_eln.dataverse.project_model import ProjectModel
from pasta_eln.dataverse.upload_model import UploadModel


@pytest.fixture
def mock_database_api(mocker) -> DatabaseAPI:
  mocker.patch('pasta_eln.dataverse.database_api.logging.getLogger')
  mocker.patch('pasta_eln.dataverse.database_api.BaseDatabaseAPI')
  return DatabaseAPI()


class TestDatabaseAPI:

  @pytest.mark.parametrize("test_id", [
    ("success_case_default_values"),
    ("error_case_design_doc_name_none")
  ])
  def test_database_api_init(self, mocker, test_id):
    # Arrange
    log_mock = mocker.MagicMock(spec=Logger)
    base_db_api_mock = mocker.MagicMock(spec=BaseDatabaseAPI)
    logger_mock = mocker.patch('pasta_eln.dataverse.database_api.logging.getLogger', return_value=log_mock)
    if test_id == "success_case_default_values":
      base_db_api_constructor_mock = mocker.patch('pasta_eln.dataverse.database_api.BaseDatabaseAPI',
                                                  return_value=base_db_api_mock)
    else:
      base_db_api_constructor_mock = mocker.patch('pasta_eln.dataverse.database_api.BaseDatabaseAPI',
                                                  side_effect=DatabaseError("test_error"))

    # Act
    db_api = None
    if test_id == "success_case_default_values":
      db_api = DatabaseAPI()
    else:
      with pytest.raises(DatabaseError):
        db_api = DatabaseAPI()

    # Assert
    base_db_api_constructor_mock.assert_called_once()
    logger_mock.assert_called_once_with("pasta_eln.dataverse.database_api.DatabaseAPI")
    if test_id == "success_case_default_values":
      assert db_api.db_api == base_db_api_mock
      assert db_api.design_doc_name == '_design/viewDataverse'
    else:
      assert db_api is None

  @pytest.mark.parametrize(
    "design_doc_name, expected_id, test_id",
    [
      ("design_doc_1", "design_doc_1", "success_path_1"),
    ]
  )
  def test_create_dataverse_design_document_happy_path(self, mocker, design_doc_name, expected_id, test_id,
                                                       mock_database_api):
    # Arrange
    mock_create_document = mocker.MagicMock()
    mock_create_document.return_value = {"_id": expected_id}
    mock_database_api.db_api.create_document = mock_create_document

    # Act
    result = mock_database_api.create_dataverse_design_document()

    # Assert
    assert result["_id"] == expected_id, f"Test {test_id}: The Document ID should be '{expected_id}'."

  @pytest.mark.parametrize(
    "design_doc_name, exception, test_id",
    [
      (None, DatabaseError("Document must have an _id"), "error_case_none"),
      ("", DatabaseError("Document must have an _id"), "error_case_empty"),
    ]
  )
  def test_create_dataverse_design_document_error_cases(self, mocker, design_doc_name, exception, test_id,
                                                        mock_database_api):
    # Arrange
    mock_create_document = mocker.MagicMock()
    mock_create_document.side_effect = exception
    mock_database_api.db_api.create_document = mock_create_document

    # Act / Assert
    with pytest.raises(DatabaseError) as exc_info:
      mock_database_api.create_dataverse_design_document()
    assert str(
      exc_info.value) == "Document must have an _id", f"Test {test_id}: Expected ValueError with message 'Document must have an _id'."

  @pytest.mark.parametrize("design_doc_name, view_name, map_func, expected_call, exception, test_id", [
    # Success path tests with various realistic test values
    ("design_doc_1", "dvUploadView",
     "function (doc) { if (doc.data_type === 'dataverse_upload') { emit(doc._id, doc); } }",
     ('_design/viewDataverse', "dvUploadView",
      "function (doc) { if (doc.data_type === 'dataverse_upload') { emit(doc._id, doc); } }", None), None,
     "SuccessCase-1"),

    # Error cases could include scenarios where db_api.add_view raises an exception
    ("design_doc_1", "dvUploadView",
     "function (doc) { if (doc.data_type === 'dataverse_upload') { emit(doc._id, doc); } }",
     ('_design/viewDataverse', "dvUploadView",
      "function (doc) { if (doc.data_type === 'dataverse_upload') { emit(doc._id, doc); } }", None),
     DatabaseError("test_error"), "ErrorCase-1"),
  ])
  def test_create_upload_documents_view(self, mocker, design_doc_name, view_name, map_func, expected_call, exception,
                                        test_id,
                                        mock_database_api):
    # Arrange
    mock_add_view = mocker.MagicMock()
    if exception is not None:
      mock_add_view.side_effect = exception
    mock_database_api.db_api.add_view = mock_add_view

    # Act
    if exception is None:
      mock_database_api.create_upload_documents_view()
    else:
      with pytest.raises(DatabaseError):
        mock_database_api.create_upload_documents_view()

    # Assert
    mock_database_api.db_api.add_view.assert_called_once_with(*expected_call)
    mock_database_api.logger.info.assert_called_with("Creating dvUploadView as part of design document: %s",
                                                     mock_database_api.design_doc_name)

  @pytest.mark.parametrize(
    "test_id, expected_info_log, expected_view_name, expected_map_func, exception",
    [
      # Happy path tests with various realistic test values
      ("SuccessCase-1", ('Creating dvProjectsView as part of design document: %s', '_design/viewDataverse'),
       "dvProjectsView",
       "function (doc) { if (doc['-type']=='x0') {emit(doc._id, {'name': doc['-name'], '_id': doc._id, '_rev': doc._rev, 'objective': doc.objective, 'status': doc.status, 'comment': doc.comment, 'user': doc['-user'], 'date': doc['-date']});}}",
       None),
      ("SuccessCase-2", ('Creating dvProjectsView as part of design document: %s', '_design/viewDataverse'),
       "dvProjectsView",
       "function (doc) { if (doc['-type']=='x0') {emit(doc._id, {'name': doc['-name'], '_id': doc._id, '_rev': doc._rev, 'objective': doc.objective, 'status': doc.status, 'comment': doc.comment, 'user': doc['-user'], 'date': doc['-date']});}}",
       None),

      # Edge cases
      # Assuming empty string is an edge case for design document name
      ("EdgeCase-1", ('Creating dvProjectsView as part of design document: %s', '_design/viewDataverse'),
       "dvProjectsView",
       "function (doc) { if (doc['-type']=='x0') {emit(doc._id, {'name': doc['-name'], '_id': doc._id, '_rev': doc._rev, 'objective': doc.objective, 'status': doc.status, 'comment': doc.comment, 'user': doc['-user'], 'date': doc['-date']});}}",
       None),

      # Error cases
      # Assuming None as an invalid design document name
      ("ErrorCase-1", ('Creating dvProjectsView as part of design document: %s', '_design/viewDataverse'),
       "dvProjectsView",
       "function (doc) { if (doc['-type']=='x0') {emit(doc._id, {'name': doc['-name'], '_id': doc._id, '_rev': doc._rev, 'objective': doc.objective, 'status': doc.status, 'comment': doc.comment, 'user': doc['-user'], 'date': doc['-date']});}}",
       DatabaseError("test_error")),
    ]
  )
  def test_create_projects_view(self, mocker, test_id, expected_info_log, expected_view_name, expected_map_func,
                                exception,
                                mock_database_api):
    # Arrange
    mock_add_view = mocker.MagicMock()
    if exception is not None:
      mock_add_view.side_effect = exception
    mock_database_api.db_api.add_view = mock_add_view

    # Act
    if exception is None:
      mock_database_api.create_projects_view()
    else:
      with pytest.raises(DatabaseError):
        mock_database_api.create_projects_view()

    # Assert
    # Check if logger.info was called with the expected message
    mock_database_api.logger.info.assert_called_once_with(*expected_info_log)
    # Check if db_api.add_view was called with the expected parameters
    mock_database_api.db_api.add_view.assert_called_once_with(mock_database_api.design_doc_name, expected_view_name,
                                                              expected_map_func,
                                                              None)

  @pytest.mark.parametrize("input_model, expected_output, test_id, exception", [
    # Success path tests with various realistic test values
    (UploadModel(_id="id", _rev='rev1', project_name='data1'),
     UploadModel(_id='mock_id', _rev='mock_rev', project_name='data1'), 'success_path_upload', None),
    (UploadModel(_id="", _rev='rev1', project_name='data1'),
     UploadModel(_id='mock_id', _rev='mock_rev', project_name='data1'), 'success_path_upload', None),
    (ConfigModel(_id="id", _rev='rev2', metadata={'value': 'value'}),
     ConfigModel(_id='mock_id', _rev='mock_rev', metadata={'value': 'value'}), 'success_path_config', None),
    (ProjectModel(_id="id", _rev='rev3', name='Project'), ProjectModel(_id='mock_id', _rev='mock_rev', name='Project'),
     'success_path_project', None),

    # Error cases
    # Assuming error cases would be related to the incorrect types or missing required fields
    # These tests would normally raise exceptions, but since the function's error handling is not shown, we'll assume it returns None
    (None, None, 'error_case_none_input', ValueError("Data cannot be None")),
    ('not_a_model_instance', None, 'error_case_wrong_type', ValueError("Data cannot be None")),
    # Add more error cases as needed
  ])
  def test_create_model_document(self, input_model, expected_output, test_id, exception, mocker, mock_database_api):
    # Arrange
    mock_create_document = mocker.MagicMock()
    if exception is not None:
      mock_create_document.side_effect = exception
    else:
      mock_create_document.return_value = dict(expected_output)
    mock_database_api.db_api.create_document = mock_create_document

    # Act
    result = None
    if exception is None:
      result = mock_database_api.create_model_document(input_model)
    else:
      with pytest.raises(type(exception)):
        result = mock_database_api.create_model_document(input_model)

    # Assert
    if exception is None:
      assert type(result) == type(
        expected_output), f"Result type is {type(result)} but expected {type(expected_output)}"
      assert dict(result) == dict(expected_output), f"Test failed for {test_id}"
      data = dict(input_model)
      del data['_rev']
      mock_database_api.db_api.create_document.assert_called_once_with(data)
    else:
      assert result is None
