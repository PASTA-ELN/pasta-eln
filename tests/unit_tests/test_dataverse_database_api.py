#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_database_api.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_database_api.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from json import JSONDecodeError
from logging import Logger
from os import getcwd
from os.path import dirname, join, realpath
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pasta_eln.dataverse.base_database_api import BaseDatabaseAPI
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.database_api import DatabaseAPI
from pasta_eln.dataverse.database_error import DatabaseError
from pasta_eln.dataverse.project_model import ProjectModel
from pasta_eln.dataverse.upload_model import UploadModel


def mock_config_model(api_token=None, dataverse_login_info_valid=True):
  config_model = ConfigModel()
  if dataverse_login_info_valid:
    config_model.dataverse_login_info = {"api_token": api_token, "dataverse_id": "some_id"} if api_token else {}
  else:
    config_model.dataverse_login_info = None
  return config_model


@pytest.fixture
def mock_database_api(mocker) -> DatabaseAPI:
  mocker.patch('pasta_eln.dataverse.database_api.logging.getLogger')
  mocker.patch('pasta_eln.dataverse.database_api.BaseDatabaseAPI')
  mocker.patch('pasta_eln.dataverse.database_api.get_encrypt_key', return_value=(True, "test_key"))
  mocker.patch('pasta_eln.dataverse.database_api.get_db_credentials', return_value={
    "db_name": "pasta_project_group_db",
    "username": "admin",
    "password": "admin",
    "cred": "cred"
  })
  api = DatabaseAPI()
  mocker.resetall()
  return api


class TestDataverseDatabaseAPI:

  @pytest.mark.parametrize("test_id", [("success_case_default_values"), ("error_case_design_doc_name_none")])
  def test_database_api_init(self, mocker, test_id):
    # Arrange
    log_mock = mocker.MagicMock(spec=Logger)
    base_db_api_mock = mocker.MagicMock(spec=BaseDatabaseAPI)
    mocker.patch('pasta_eln.dataverse.database_api.get_db_credentials', return_value={
      "db_name": "pasta_project_group_db",
      "username": "admin",
      "password": "admin",
      "cred": "cred"
    })
    mocker.patch('pasta_eln.dataverse.database_api.get_encrypt_key', return_value=(True, "test_key"))
    mocker.patch('pasta_eln.dataverse.utils.exists', return_value=True)
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
      assert db_api.config_doc_id == '-dataverseConfig-'
      assert db_api.data_hierarchy_doc_id == '-dataHierarchy-'
      assert db_api.upload_model_view_name == 'dvUploadView'
      assert db_api.project_model_view_name == 'dvProjectsView'
      assert db_api.upload_models_query_index_name == "uploadModelsQuery"
      assert db_api.upload_models_query_index_fields == ["finished_date_time"]
    else:
      assert db_api is None

  @pytest.mark.parametrize("design_doc_name, expected_id, test_id",
                           [("design_doc_1", "design_doc_1", "success_path_1"), ])
  def test_create_dataverse_design_document_happy_path(self, mocker, design_doc_name, expected_id, test_id,
                                                       mock_database_api):
    # Arrange
    mock_create_document = mocker.MagicMock()
    mock_create_document.return_value = {"_id": expected_id}
    mock_database_api.db_api.create_document = mock_create_document

    # Act
    result = mock_database_api.create_dataverse_design_document("test_db_name")

    # Assert
    assert result["_id"] == expected_id, f"Test {test_id}: The Document ID should be '{expected_id}'."

  @pytest.mark.parametrize("design_doc_name, exception, test_id",
                           [(None, DatabaseError("Document must have an _id"), "error_case_none"),
                            ("", DatabaseError("Document must have an _id"), "error_case_empty"), ])
  def test_create_dataverse_design_document_error_cases(self, mocker, design_doc_name, exception, test_id,
                                                        mock_database_api):
    # Arrange
    mock_create_document = mocker.MagicMock()
    mock_create_document.side_effect = exception
    mock_database_api.db_api.create_document = mock_create_document

    # Act / Assert
    with pytest.raises(DatabaseError) as exc_info:
      mock_database_api.create_dataverse_design_document("test_db_name")
    assert str(
      exc_info.value) == "Document must have an _id", f"Test {test_id}: Expected ValueError with message 'Document must have an _id'."

  @pytest.mark.parametrize("design_doc_name, view_name, map_func, expected_call, exception, test_id",
                           [  # Success path tests with various realistic test values
                             ("design_doc_1", "dvUploadView",
                              "function (doc) { if (doc.data_type === 'dataverse_upload') { emit(doc._id, doc); } }", (
                                  "dataverse",
                                  '_design/viewDataverse', "dvUploadView",
                                  "function (doc) { if (doc.data_type === 'dataverse_upload') { emit(doc._id, doc); } }",
                                  None), None, "SuccessCase-1"),

                             # Error cases could include scenarios where db_api.add_view raises an exception
                             ("design_doc_1", "dvUploadView",
                              "function (doc) { if (doc.data_type === 'dataverse_upload') { emit(doc._id, doc); } }", (
                                  "dataverse",
                                  '_design/viewDataverse', "dvUploadView",
                                  "function (doc) { if (doc.data_type === 'dataverse_upload') { emit(doc._id, doc); } }",
                                  None), DatabaseError("test_error"), "ErrorCase-1"), ])
  def test_create_upload_documents_view(self, mocker, design_doc_name, view_name, map_func, expected_call, exception,
                                        test_id, mock_database_api):
    # Arrange
    mock_add_view = mocker.MagicMock()
    if exception is not None:
      mock_add_view.side_effect = exception
    mock_database_api.db_api.add_view = mock_add_view

    # Act
    if exception is None:
      mock_database_api.create_upload_model_view()
    else:
      with pytest.raises(DatabaseError):
        mock_database_api.create_upload_model_view()

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
       "function (doc) { if (doc['-type'].includes('x0')) {emit(doc._id, {'name': doc['-name'], '_id': doc._id, '_rev': doc._rev, 'objective': doc.objective, 'status': doc.status, 'comment': doc.comment, 'user': doc['-user'], 'date': doc['-date']});}}",
       None),
      ("SuccessCase-2", ('Creating dvProjectsView as part of design document: %s', '_design/viewDataverse'),
       "dvProjectsView",
       "function (doc) { if (doc['-type'].includes('x0')) {emit(doc._id, {'name': doc['-name'], '_id': doc._id, '_rev': doc._rev, 'objective': doc.objective, 'status': doc.status, 'comment': doc.comment, 'user': doc['-user'], 'date': doc['-date']});}}",
       None),

      # Edge cases
      # Assuming empty string is an edge case for design document name
      ("EdgeCase-1", ('Creating dvProjectsView as part of design document: %s', '_design/viewDataverse'),
       "dvProjectsView",
       "function (doc) { if (doc['-type'].includes('x0')) {emit(doc._id, {'name': doc['-name'], '_id': doc._id, '_rev': doc._rev, 'objective': doc.objective, 'status': doc.status, 'comment': doc.comment, 'user': doc['-user'], 'date': doc['-date']});}}",
       None),

      # Error cases
      # Assuming None as an invalid design document name
      ("ErrorCase-1", ('Creating dvProjectsView as part of design document: %s', '_design/viewDataverse'),
       "dvProjectsView",
       "function (doc) { if (doc['-type'].includes('x0')) {emit(doc._id, {'name': doc['-name'], '_id': doc._id, '_rev': doc._rev, 'objective': doc.objective, 'status': doc.status, 'comment': doc.comment, 'user': doc['-user'], 'date': doc['-date']});}}",
       DatabaseError("test_error")),
    ]
  )
  def test_create_projects_view(self, mocker, test_id, expected_info_log, expected_view_name, expected_map_func,
                                exception, mock_database_api):
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
    mock_database_api.db_api.add_view.assert_called_once_with(mock_database_api.default_project_group_db_name,
                                                              mock_database_api.design_doc_name, expected_view_name,
                                                              expected_map_func, None)

  @pytest.mark.parametrize("input_model, expected_output, test_id, exception",
                           [  # Success path tests with various realistic test values
                             (UploadModel(_id="id", _rev='rev1', project_name='data1'),
                              UploadModel(_id='mock_id', _rev='mock_rev', project_name='data1'), 'success_path_upload',
                              None), (UploadModel(_id=None, _rev='rev1', project_name='data1'),
                                      UploadModel(_id='mock_id', _rev='mock_rev', project_name='data1'),
                                      'success_path_upload', None), (
                               ConfigModel(_id="id", _rev='rev2', metadata={'value': 'value'}),
                               ConfigModel(_id='mock_id', _rev='mock_rev', metadata={'value': 'value'}),
                               'success_path_config', None), (ProjectModel(_id="id", _rev='rev3', name='Project'),
                                                              ProjectModel(_id='mock_id', _rev='mock_rev',
                                                                           name='Project'), 'success_path_project',
                                                              None),

                             # Error cases
                             # Assuming error cases would be related to the incorrect types or missing required fields
                             # These tests would normally raise exceptions, but since the function's error handling is not shown, we'll assume it returns None
                             (None, None, 'error_case_none_input', ValueError("Data cannot be None")), (
                               'not_a_model_instance', None, 'error_case_wrong_type',
                               TypeError("Data must be an UploadModel, ConfigModel, or ProjectModel!")), (
                               ProjectModel(_id="id", _rev='rev3', name='Project'),
                               UploadModel(_id='mock_id', _rev='mock_rev', project_name='Project'),
                               'error_case_wrong_type_returned_document',
                               TypeError("Expected UploadModel but got ProjectModel")), ])
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
    mock_database_api.logger.info.assert_called_once_with("Creating model document: %s", input_model)
    if exception is None:
      assert type(result) == type(
        expected_output), f"Result type is {type(result)} but expected {type(expected_output)}"
      assert dict(result) == dict(expected_output), f"Test failed for {test_id}"
      data = dict(input_model)
      del data['_rev']
      if data['_id'] is None:
        del data['_id']
      mock_database_api.db_api.create_document.assert_called_once_with(data, mock_database_api.dataverse_db_name)
    else:
      assert result is None

  @pytest.mark.parametrize("data, exception, test_id", [  # Success path tests with various realistic test values
    (UploadModel(project_name="test/path", status="status"), None, "success_path_upload_model"),
    (ConfigModel(metadata={"key": "value"}, dataverse_login_info={"key": "value"}), None, "success_path_config_model"),
    (ProjectModel(name="name", comment="comment"), None, "success_path_project_model"),

    # Error cases
    (None, ValueError("Data cannot be None"), "error_case_none_data"), (
        "Not a model instance", TypeError("Data must be an UploadModel, ConfigModel, or ProjectModel!"),
        "error_case_wrong_type"),
    (123, TypeError("Data must be an UploadModel, ConfigModel, or ProjectModel!"), "error_case_numeric_data"), ])
  def test_update_model_document(self, data, exception, test_id, mock_database_api):
    # Arrange
    if exception is not None:
      mock_database_api.db_api.update_document.side_effect = exception

    # Act
    if exception is None:
      mock_database_api.update_model_document(data)
    else:
      with pytest.raises(type(exception)):
        mock_database_api.update_model_document(data)

    # Assert
    mock_database_api.logger.info.assert_called_once_with("Updating model document: %s", data)
    if isinstance(data, (UploadModel, ConfigModel, ProjectModel)):
      mock_database_api.db_api.update_document.assert_called_once_with(dict(data), mock_database_api.dataverse_db_name)
      mock_database_api.logger.info.assert_called_once()
    else:
      mock_database_api.db_api.update_document.assert_not_called()
      mock_database_api.logger.error(str(exception))

  @pytest.mark.parametrize("model_type, view_name, expected_results, expected_exception",
                           [  # success path tests with various realistic test values
                             (UploadModel, "dvUploadView", [UploadModel(**res) for res in
                                                            [{'_id': 'upload1', 'project_name': 'data1'},
                                                             {'_id': 'upload2', 'project_name': 'data2'}]], None), (
                               ProjectModel, "dvProjectsView", [ProjectModel(**res) for res in
                                                                [{'_id': 'project1', 'name': 'data1'},
                                                                 {'_id': 'project2', 'name': 'data2'}]], None),
                             # Error case for unsupported model
                             (ConfigModel, None, None, TypeError), ],
                           ids=['success_path_upload_model', 'success_path_project_model',
                                'error_case_unsupported_model'])
  def test_get_models(self, model_type, view_name, expected_results, expected_exception, mock_database_api):
    # Arrange
    if not expected_exception:
      mock_database_api.db_api.get_view_results.return_value = [dict(result) for result in expected_results]

    # Act
    if expected_exception:
      with pytest.raises(expected_exception):
        mock_database_api.get_models(model_type)
    else:
      results = mock_database_api.get_models(model_type)

    # Assert
    mock_database_api.logger.info.assert_called_once_with("Getting models of type: %s", model_type)
    if not expected_exception:
      mock_database_api.db_api.get_view_results.assert_called_with(
        mock_database_api.default_project_group_db_name if model_type is ProjectModel else mock_database_api.dataverse_db_name,
        mock_database_api.design_doc_name, view_name)
      assert type(results) == type(expected_results)
      assert [dict(result) for result in results] == [dict(result) for result in expected_results]
    else:
      mock_database_api.db_api.get_view_results.assert_not_called()
      mock_database_api.logger.error(str(expected_exception))

  @pytest.mark.parametrize("model_id,model_type,expected", [  # Success path tests
    pytest.param("1", UploadModel, UploadModel(_id="1", project_name="Test Model"), id="success_path_upload"),
    pytest.param("2", ConfigModel,
                 ConfigModel(_id="2", metadata={"key": "value"}, dataverse_login_info={"key": "value"}),
                 id="success_path_config"),
    pytest.param("3", ProjectModel, ProjectModel(_id="3", name="Test Model"), id="success_path_project"),

    # Error cases
    pytest.param(None, UploadModel, ValueError("Model ID cannot be None!"), id="error_null_model_id"),
    pytest.param("1", str, TypeError("Model type must be an UploadModel, ConfigModel, or ProjectModel!"),
                 id="error_unsupported_model_type"),
    pytest.param({"1"}, str, TypeError("Model type must be an UploadModel, ConfigModel, or ProjectModel!"),
                 id="error_unsupported_model_type"), ])
  def test_get_model(self, model_id, model_type, expected, mock_database_api):
    # Arrange
    if not isinstance(expected, ValueError | TypeError):
      mock_database_api.db_api.get_document.return_value = dict(expected)

    # Act and Assert
    if isinstance(expected, ValueError | TypeError):
      with pytest.raises(type(expected)):
        mock_database_api.get_model(model_id, model_type)
    else:
      result = mock_database_api.get_model(model_id, model_type)
      # Assert
      assert type(result) == type(expected), f"Expected type {type(expected)}, got type {type(result)}"
      assert dict(result) == dict(expected), f"Expected {expected}, got {result}"
    mock_database_api.logger.info.assert_called_once_with("Getting model with id: %s, type: %s", model_id, model_type)

  @pytest.mark.parametrize("document, expected, test_id", [  # Happy path tests with various realistic test values
    ({"_id": "1", "_rev": "1-abc", "-version": "1.0", "data": "value"}, {"data": "value"}, "happy_path_1"), (
        {"_id": "2", "_rev": "2-def", "-version": "2.0", "more_data": [1, 2, 3]}, {"more_data": [1, 2, 3]},
        "happy_path_2"),

    # Edge case: Empty document except for system fields
    ({"_id": "", "_rev": "", "-version": ""}, {}, "edge_case_empty_doc"),

    # Error case: Document is None
    (None, None, "error_case_none_doc"), ], )
  def test_get_data_hierarchy(self, mocker, document, expected, test_id, mock_database_api):
    # Arrange
    mock_database_api.db_api.get_document.return_value = document

    # Act
    result = mock_database_api.get_data_hierarchy()

    # Assert
    if document is not None:
      mock_database_api.db_api.get_document.assert_called_once_with(mock_database_api.data_hierarchy_doc_id,
                                                                    mock_database_api.default_project_group_db_name)
      assert result == expected, f"Test failed for {test_id}"
    else:
      mock_database_api.logger.warning.assert_called_once_with("Data hierarchy document not found!")
      assert result is None, f"Test failed for {test_id}"
    mock_database_api.logger.info.assert_called_once_with("Getting data hierarchy...")

  @pytest.mark.parametrize(
    "test_id, design_doc_exists, upload_model_view_exists, project_model_view_exists, expected_calls",
    [("success_path", True, True, True, []), ("edge_case_no_design_doc", None, None, None,
                                              ['create_dataverse_design_document', 'create_upload_documents_view',
                                               'create_projects_view', 'initialize_config_document']),
     ("error_case_db_api_failure", None, None, None, ['get_document', 'get_view']), ])
  def test_initialize_database(self, mocker, test_id, design_doc_exists, upload_model_view_exists,
                               project_model_view_exists, expected_calls, mock_database_api):
    # Arrange
    mock_database_api.db_api.get_document.return_value = design_doc_exists
    mock_database_api.db_api.get_view.side_effect = [upload_model_view_exists, project_model_view_exists]
    mock_database_api.create_dataverse_design_document = mocker.MagicMock()
    mock_database_api.create_query_index = mocker.MagicMock()
    mock_database_api.create_upload_model_view = mocker.MagicMock()
    mock_database_api.create_projects_view = mocker.MagicMock()
    mock_database_api.initialize_config_document = mocker.MagicMock()

    # Act
    mock_database_api.initialize_database()

    # Assert
    if design_doc_exists is None:
      mock_database_api.db_api.get_document.assert_called_with(mock_database_api.design_doc_name)
      mock_database_api.db_api.get_view.assert_not_called()
    else:
      mock_database_api.db_api.get_document.assert_called_with(mock_database_api.design_doc_name)
      mock_database_api.create_query_index.assert_called_with(mock_database_api.upload_models_query_index_name,
                                                              "json",
                                                              mock_database_api.upload_models_query_index_fields)
      if not design_doc_exists:
        mock_database_api.create_dataverse_design_document.assert_called_once()
      if not upload_model_view_exists:
        mock_database_api.create_upload_model_view.assert_called_once()
      if not project_model_view_exists:
        mock_database_api.create_projects_view.assert_called_once()
      if not design_doc_exists:
        mock_database_api.initialize_config_document.assert_called_once()

    for call in expected_calls:
      getattr(mock_database_api, call).assert_called_once()

  # Parametrized test cases
  @pytest.mark.parametrize(
    "test_id, design_doc_exists, upload_view_exists, project_view_exists, config_doc_exists, expected_calls",
    [  # Happy path tests with various realistic test values
      ("success_path", None, None, None, None, 3),  # None of the documents/views exist
      ("success_path", {}, None, None, None, 2),  # Only design document exists
      ("success_path", {}, {}, None, None, 1),  # Design document and upload view exist
      ("success_path", {}, {}, {}, None, 1),  # All documents/views exist except config document

      # Edge cases
      ("edge_case", {}, {}, {}, {}, 0),  # All documents/views already exist

      # Error cases
      ("error_case", DatabaseError("DB Error"), None, None, None, 0),  # DB error on getting design document
      # Add more error cases as needed
    ])
  def test_initialize_database(self, mocker, test_id, design_doc_exists, upload_view_exists, project_view_exists,
                               config_doc_exists, expected_calls, mock_database_api):
    # Arrange
    mock_database_api.db_api.get_document.side_effect = [design_doc_exists, design_doc_exists, config_doc_exists]
    mock_database_api.db_api.get_view.side_effect = [upload_view_exists, project_view_exists]
    mock_database_api.create_dataverse_design_document = mocker.MagicMock()
    mock_database_api.create_upload_model_view = mocker.MagicMock()
    mock_database_api.create_projects_view = mocker.MagicMock()
    mock_database_api.initialize_config_document = mocker.MagicMock()

    # Act
    if isinstance(design_doc_exists, DatabaseError):
      with pytest.raises(type(design_doc_exists)):
        mock_database_api.initialize_database()
    else:
      mock_database_api.initialize_database()

    # Assert
    mock_database_api.logger.info.assert_called_with("Initializing database for dataverse module...")
    if not isinstance(design_doc_exists, DatabaseError):
      if design_doc_exists is None:
        mock_database_api.create_dataverse_design_document.assert_any_call(
          mock_database_api.default_project_group_db_name)
        mock_database_api.create_dataverse_design_document.assert_any_call(mock_database_api.dataverse_db_name)
      if upload_view_exists is None:
        mock_database_api.create_upload_model_view.assert_called_once()
      if project_view_exists is None:
        mock_database_api.create_projects_view.assert_called_once()
      if config_doc_exists is None:
        mock_database_api.initialize_config_document.assert_called_once()
      mock_database_api.db_api.create_query_index.assert_called_with(mock_database_api.dataverse_db_name,
                                                                     mock_database_api.upload_models_query_index_name,
                                                                     "json",
                                                                     mock_database_api.upload_models_query_index_fields)
    else:
      mock_database_api.db_api.get_document.assert_called_with(mock_database_api.design_doc_name,
                                                               mock_database_api.default_project_group_db_name)

  @pytest.mark.parametrize(
    "data_hierarchy, data_hierarchy_types,config_file_content, expected_metadata, exception",
    [
      pytest.param(["type1", "type2"], ["Type1", "Type2", "Undefined"], '{"key": "value"}', {"key": "value"}, None,
                   id="success_path"),
      pytest.param([], ["Undefined"], '{}', {}, None, id="empty_hierarchy"),
      pytest.param(["type1"], ["Type1", "Undefined"], '{"key": "value"}', {"key": "value"}, None,
                   id="single_hierarchy_type"),
      pytest.param(["type1"], ["Type1", "Undefined"], '', None, JSONDecodeError, id="invalid_json"),
      pytest.param(["type1"], ["Type1", "Undefined"], '{"key": "value"}', {"key": "value"}, FileNotFoundError,
                   id="missing_file"),
    ],
    ids=lambda x: x[-1]
  )
  def test_initialize_config_document(self, mocker, mock_database_api, data_hierarchy, data_hierarchy_types,
                                      config_file_content, expected_metadata,
                                      exception):
    # Arrange
    mock_get_data_hierarchy_types = mocker.patch('pasta_eln.dataverse.database_api.get_data_hierarchy_types',
                                                 return_value=data_hierarchy_types)
    mock_set_template_values = mocker.patch('pasta_eln.dataverse.database_api.set_template_values')
    mock_set_authors = mocker.patch('pasta_eln.dataverse.database_api.set_authors')
    mock_database_api.create_model_document = mocker.MagicMock()
    mock_database_api.get_data_hierarchy = mocker.MagicMock()
    mock_database_api.get_data_hierarchy.return_value = data_hierarchy
    mock_open = mocker.patch("pasta_eln.dataverse.database_api.open", mock_open=True)
    mock_open.return_value.__enter__.return_value.read.return_value = config_file_content

    if exception is FileNotFoundError:
      mock_open.side_effect = exception
    if exception is JSONDecodeError:
      mocker.patch('pasta_eln.dataverse.database_api.load', side_effect=JSONDecodeError("", "", 0))

    # Act
    if exception:
      with pytest.raises(exception):
        mock_database_api.initialize_config_document()
    else:
      mock_database_api.initialize_config_document()

    # Assert
    if not exception:
      mock_get_data_hierarchy_types.assert_called_once_with(mock_database_api.get_data_hierarchy.return_value)
      mock_database_api.get_data_hierarchy.assert_called_once()
      mock_database_api.create_model_document.assert_called_once()
      created_model = mock_database_api.create_model_document.call_args[0][0]
      assert isinstance(created_model, ConfigModel)
      assert created_model._id == '-dataverseConfig-'
      assert created_model.parallel_uploads_count == 3
      assert created_model.metadata == expected_metadata
      assert created_model.project_upload_items == {data_type: True for data_type in data_hierarchy_types}
      mock_set_template_values.assert_called_once_with(mock_database_api.logger, expected_metadata or {})
      mock_set_authors.assert_called_once_with(mock_database_api.logger, expected_metadata or {})

  @pytest.mark.parametrize("test_id", [("success_path_default_values")])
  def test_initialize_config_document_success_path(self, mocker, test_id, mock_database_api):
    # Arrange
    mock_database_api.create_model_document = mocker.MagicMock()
    mock_database_api.get_data_hierarchy = mocker.MagicMock()
    mocker.patch('pasta_eln.dataverse.database_api.get_data_hierarchy_types')
    current_path = realpath(join(getcwd(), dirname(__file__)))
    with open(join(current_path, "../../pasta_eln/dataverse", "dataset-create-new-all-default-fields.json"),
              encoding="utf-8") as config_file:
      file_data = config_file.read()

    # Act
    with patch('pasta_eln.dataverse.database_api.realpath') as mock_realpath, patch(
        'pasta_eln.dataverse.database_api.getcwd') as mock_getcwd, patch(
      'pasta_eln.dataverse.database_api.dirname') as mock_dirname, patch(
      'pasta_eln.dataverse.database_api.open') as mock_file, patch(
      'pasta_eln.dataverse.database_api.set_authors') as mock_set_authors:
      mock_file.side_effect = (mock_open(read_data=file_data).return_value, mock_open(
        read_data="{\"authors\": [{\"first\": \"\",\"last\": \"\",\"title\": \"\",\"email\": \"\",\"orcid\": \"\",\"organizations\": [{\"organization\": \"\",\"rorid\": \"\"}]}]}").return_value,)
      mock_realpath.return_value = '/fakepath'
      mock_getcwd.return_value = '/home/jmurugan'
      mock_dirname.return_value = '/pasta_eln/src/pasta_eln/dataverse'

      mock_database_api.initialize_config_document()
      mock_set_authors.assert_called_once()

    # Assert
    mock_database_api.logger.info.assert_called_with("Initializing config document...")
    mock_database_api.create_model_document.assert_called_once()
    called_with_model = mock_database_api.create_model_document.call_args[0][0]
    assert isinstance(called_with_model, ConfigModel)
    assert called_with_model._id == mock_database_api.config_doc_id
    assert called_with_model.parallel_uploads_count == 3
    assert called_with_model.dataverse_login_info == {"server_url": "", "api_token": "", "dataverse_id": ""}
    assert called_with_model.project_upload_items == {}
    assert called_with_model.metadata is not None

  # Various error cases
  # Assuming error cases might involve exceptions thrown during file reading or JSON parsing
  @pytest.mark.parametrize("side_effect, test_id", [(FileNotFoundError(), "error_case_file_not_found"), (
      JSONDecodeError("Expecting value", "", 0), "error_case_invalid_json"), ])
  def test_initialize_config_document_error_cases(self, mocker, side_effect, test_id, mock_database_api):
    # Arrange
    mock_database_api.create_model_document = mocker.MagicMock()
    mocker.patch('pasta_eln.dataverse.database_api.get_data_hierarchy_types', return_value=['data_type1', 'data_type2'])
    mock_database_api.get_data_hierarchy = mocker.MagicMock()

    # Act & Assert
    with patch('pasta_eln.dataverse.database_api.realpath') as mock_realpath, patch(
        'pasta_eln.dataverse.database_api.getcwd') as mock_getcwd, patch(
      'pasta_eln.dataverse.database_api.dirname') as mock_dirname, patch('pasta_eln.dataverse.database_api.open',
                                                                         mock_open()) as mock_file:
      mock_file.side_effect = side_effect
      mock_realpath.return_value = '/fakepath'
      mock_getcwd.return_value = '/home/jmurugan'
      mock_dirname.return_value = '/pasta_eln/src/pasta_eln/dataverse'
      with pytest.raises(type(side_effect)):
        mock_database_api.initialize_config_document()

  # Parametrized test covering happy paths, edge cases, and error cases
  @pytest.mark.parametrize(
    "encrypt_key,api_token,dataverse_login_info_valid,expected_api_token,expected_warning,expected_error", [
      # ID: Happy Path with encryption
      (True, "encrypted_token", True, "decrypted_token", None, None),
      # ID: Happy Path without encryption
      (False, "plain_token", True, None,
       "No encryption key found. Hence if any API key exists, it will be removed and the user needs to re-enter it.",
       None),
      # ID: Error case with invalid dataverse_login_info
      (True, None, False, None, None, "Fatal Error, Invalid dataverse login info!"),
      # ID: Error case with no config model found
      (True, None, True, None, None, "Fatal error, Failed to load config model!"),
    ])
  def test_get_config_model(self, mocker, mock_database_api, encrypt_key, api_token, dataverse_login_info_valid,
                            expected_api_token,
                            expected_warning,
                            expected_error):
    # Arrange
    mock_database_api.encrypt_key = "fake_key" if encrypt_key else None
    mock_database_api.config_doc_id = "config_doc_id"
    mock_config = None if expected_error == "Fatal error, Failed to load config model!" else mock_config_model(
      api_token, dataverse_login_info_valid)
    mocker.patch.object(mock_database_api, 'get_model', return_value=mock_config)
    mocker.patch('pasta_eln.dataverse.database_api.decrypt_data', return_value="decrypted_token" if api_token else None)

    # Act
    result = mock_database_api.get_config_model()

    # Assert
    mock_database_api.logger.info.assert_any_call("Getting config model...")
    if expected_error:
      mock_database_api.logger.error.assert_called_with(expected_error)
      assert result is None
    elif expected_warning:
      mock_database_api.logger.warning.assert_any_call(expected_warning)
      assert result.dataverse_login_info["api_token"] is None
      assert result.dataverse_login_info["dataverse_id"] is None
    else:
      assert result.dataverse_login_info["api_token"] == expected_api_token

  # Parametrized test cases for happy path, edge cases, and error cases
  @pytest.mark.parametrize("api_token, server_url, expected_api_token, expected_server_url, test_id", [
    ("token123", "http://example.com/", "encrypted_token123", "http://example.com", "success_path"),
    ("", "http://example.com/", "", "http://example.com", "empty_api_token"),
    ("token123", "", "encrypted_token123", "", "empty_server_url"),
    ("token123", "http://example.com//", "encrypted_token123", "http://example.com", "server_url_with_trailing_slash"),
    ("token123", "http://example.com\\", "encrypted_token123", "http://example.com", "server_url_with_backslash"),
  ], ids=["happy_path", "empty_api_token", "empty_server_url", "server_url_with_trailing_slash",
          "server_url_with_backslash"])
  def test_save_config_model_success_path_and_edge_cases(self, mocker, mock_database_api, api_token, server_url,
                                                         expected_api_token, expected_server_url, test_id):
    # Arrange
    mock_config = mocker.MagicMock(spec=ConfigModel)
    mock_database_api.update_model_document = mocker.MagicMock()
    mock_config.dataverse_login_info = {"api_token": api_token, "server_url": server_url}
    mock_encrypt = mocker.patch('pasta_eln.dataverse.database_api.encrypt_data', return_value=expected_api_token)
    # Act
    mock_database_api.save_config_model(mock_config)

    # Assert
    mock_database_api.logger.info.assert_any_call("Saving config model...")
    if api_token:
      mock_encrypt.assert_called_once_with(mock_database_api.logger, mock_database_api.encrypt_key, api_token)
    assert mock_config.dataverse_login_info["api_token"] == expected_api_token
    assert mock_config.dataverse_login_info["server_url"] == expected_server_url
    mock_database_api.update_model_document.assert_called_once_with(mock_config)

  @pytest.mark.parametrize("config_model, test_id", [
    (None, "none_config_model"),
    ("not_a_config_model", "invalid_type_config_model"),
    (MagicMock(spec=ConfigModel, dataverse_login_info="not_a_dict"), "invalid_dataverse_login_info_type"),
  ], ids=["none_config_model", "invalid_type_config_model", "invalid_dataverse_login_info_type"])
  def test_save_config_model_error_cases(self, mocker, mock_database_api, config_model, test_id):
    # Arrange
    mock_database_api.update_model_document = mocker.MagicMock()
    original_update_model_document_call_count = mock_database_api.update_model_document.call_count

    # Act
    mock_database_api.save_config_model(config_model)

    # Assert
    mock_database_api.logger.info.assert_any_call("Saving config model...")
    mock_database_api.logger.error.assert_called_once()
    assert mock_database_api.update_model_document.call_count == original_update_model_document_call_count

  @pytest.mark.parametrize("encrypt_key, test_id", [
    (None, "no_encrypt_key"),
  ], ids=["no_encrypt_key"])
  def test_save_config_model_fatal_error_cases(self, mock_database_api, encrypt_key, test_id):
    # Arrange
    mock_database_api.encrypt_key = encrypt_key
    mock_config = MagicMock(spec=ConfigModel)
    mock_config.dataverse_login_info = {"api_token": "token123", "server_url": "http://example.com/"}

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
      mock_database_api.save_config_model(mock_config)
    mock_database_api.logger.info.assert_any_call("Saving config model...")
    assert "Fatal Error, No encryption key found!" in str(exc_info.value)

  @pytest.mark.parametrize("model_type, filter_term, bookmark, limit, expected_output, test_id", [
    # Happy path tests
    (UploadModel, None, None, 10, {"bookmark": "next_page_token", "models": [
      UploadModel(project_name="Project1", dataverse_url="http://example.com", finished_date_time="2023-01-01",
                  status="completed")]}, "HP-1"),
    (UploadModel, "filter", "page1", 5, {"bookmark": "next_page_token", "models": [
      UploadModel(project_name="Project1", dataverse_url="http://example.com", finished_date_time="2023-01-01",
                  status="completed")]}, "HP-2"),

    # Error cases
    (ConfigModel, None, None, 10, TypeError, "EC-1"),
    (ProjectModel, None, None, 10, TypeError, "EC-2"),
  ])
  def test_get_paginated_models(self, mock_database_api, mocker, model_type, filter_term, bookmark, limit,
                                expected_output, test_id):
    # Arrange
    mock_database_api.db_api.get_paginated_upload_model_query_results = mocker.MagicMock(
      return_value={
        "bookmark": "next_page_token",
        "docs": [
          {"project_name": "Project1", "dataverse_url": "http://example.com", "finished_date_time": "2023-01-01",
           "status": "completed"}
        ]
      }
    )

    # Act
    if isinstance(expected_output, type) and issubclass(expected_output, Exception):
      with pytest.raises(expected_output):
        mock_database_api.get_paginated_models(model_type, filter_term, bookmark, limit)
    else:
      result = mock_database_api.get_paginated_models(model_type, filter_term, bookmark, limit)

    # Assert
    mock_database_api.logger.info("Getting paginated models of type: %s, filter_term: %s, bookmark: %s, limit: %s",
                                  model_type,
                                  filter_term,
                                  bookmark,
                                  limit)
    if not isinstance(expected_output, type):
      mock_database_api.db_api.get_paginated_upload_model_query_results.assert_called_once_with(
        mock_database_api.dataverse_db_name,
        filter_term,
        ["project_name",
         "dataverse_url",
         "finished_date_time",
         "status"],
        bookmark,
        limit)
      assert result['bookmark'] == expected_output[
        'bookmark'], f"Test ID: {test_id}, Expected: {expected_output['bookmark']}, Actual: {result['bookmark']}"
      assert len(result['models']) == len(expected_output[
                                            'models']), f"Test ID: {test_id}, Expected: {len(expected_output['models'])}, Actual: {len(result['models'])}"
      assert result['models'][0].__dict__ == expected_output['models'][
        0].__dict__, f"Test ID: {test_id}, Expected: {expected_output['models'][0].__dict__}, Actual: {result['models'][0].__dict__}"
