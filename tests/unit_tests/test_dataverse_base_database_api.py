#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_base_database_api.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from secrets import compare_digest
from unittest.mock import MagicMock, patch

import pytest
from cloudant.error import CloudantDatabaseException

from pasta_eln.dataverse.base_database_api import BaseDatabaseAPI
from pasta_eln.dataverse.database_error import DatabaseError

# Constants for test cases
CONFIG_FILE_PATH = '/home/user/.pastaELN.json'
DEFAULT_PROJECT_GROUP = 'my_project_group'
USER = 'test_user'
PASSWORD = 'test_password'


def create_mock_config(default_project_group_exists=True, user_and_password_exists=True):
  config = {}
  if default_project_group_exists:
    config['defaultProjectGroup'] = DEFAULT_PROJECT_GROUP
    if user_and_password_exists:
      config['projectGroups'] = {DEFAULT_PROJECT_GROUP: {'local': {'user': USER, 'password': PASSWORD}}}
  return config


@pytest.fixture
def mock_database_api(mocker) -> BaseDatabaseAPI:
  mocker.patch('pasta_eln.dataverse.base_database_api.logging.getLogger')
  with patch('pasta_eln.dataverse.base_database_api.read_pasta_config_file', return_value=create_mock_config()), patch(
    'pasta_eln.dataverse.base_database_api.logging.Logger.error'):
    return BaseDatabaseAPI()


class TestDataverseBaseDatabaseApi:
  # Parametrized test for a success path
  @pytest.mark.parametrize("config_content, expected_db_name, expected_username, expected_password",
                           [(create_mock_config(), DEFAULT_PROJECT_GROUP, USER, PASSWORD),
                             # Add more test cases with different realistic values if necessary
                           ], ids=["success_path_default"])
  def test_base_database_api_init_success_path(self, config_content, expected_db_name, expected_username,
                                               expected_password):
    # Arrange
    with patch('pasta_eln.dataverse.base_database_api.read_pasta_config_file',
               return_value=config_content) as read_config_mock, patch('logging.Logger.error') as mock_logger_error:
      # Act
      base_db_api = BaseDatabaseAPI()

      # Assert
      assert base_db_api.db_name == expected_db_name
      assert base_db_api.username == expected_username
      assert compare_digest(base_db_api.password, expected_password)
      read_config_mock.assert_called_once()
      mock_logger_error.assert_not_called()

  # Parametrized test for various error cases
  @pytest.mark.parametrize("config_content, exists_return_value, expected_error_message",
                           [(create_mock_config(), False, "Config file not found, Corrupt installation!"), (
                           create_mock_config(default_project_group_exists=False), True,
                           "Incorrect config file, defaultProjectGroup not found!"), (
                           create_mock_config(user_and_password_exists=False), True,
                           "Incorrect config file, projectGroups not found!"), # Add more error cases if necessary
                           ], ids=["error_no_config_file", "error_no_default_project_group", "error_no_user_password"])
  def test_base_database_api_init_error_cases(self, config_content, exists_return_value, expected_error_message):
    # Arrange
    with patch('pasta_eln.dataverse.base_database_api.read_pasta_config_file', return_value=config_content,
               side_effect=None if exists_return_value else DatabaseError(
                 "Config file not found, Corrupt installation!")) as read_config_mock, patch(
      'pasta_eln.dataverse.base_database_api.logging.Logger.error') as mock_logger_error:
      # Act & Assert
      with pytest.raises(DatabaseError) as exc_info:
        BaseDatabaseAPI()
      assert str(exc_info.value) == expected_error_message
      read_config_mock.assert_called_once()
      if exists_return_value:
        mock_logger_error.assert_called_once_with(expected_error_message)

  @pytest.mark.parametrize("test_id, data, expected_document", [# Success path tests with various realistic test values
    ("Success-1", {"name": "Spaghetti", "type": "Pasta"}, {"name": "Spaghetti", "type": "Pasta"}),
    ("Success-2", {"name": "Fusilli", "quantity": 100}, {"name": "Fusilli", "quantity": 100}),

    # Edge cases
    ("EdgeCase-1", {}, {}),  # Empty document data

    # Error cases
    ("ErrorCase-1", {"name": "Macaroni"}, None), ])
  def test_create_document(self, mocker, test_id, data, expected_document, mock_database_api):
    # Arrange
    mock_client = mocker.MagicMock()
    mock_couch = mocker.MagicMock()
    mock_db = mocker.MagicMock()
    mock_couch.__enter__.return_value = mock_client
    mock_client.__getitem__.return_value = mock_db
    mock_db.create_document.return_value = expected_document
    exception = CloudantDatabaseException(409, "docid")
    if expected_document is None:
      mock_db.create_document.side_effect = exception
    mock_couchdb_call = mocker.patch('pasta_eln.dataverse.base_database_api.couchdb', return_value=mock_couch)

    # Act
    actual_document = mock_database_api.create_document(data)

    # Assert
    mock_database_api.logger.info.assert_called_with(f"Creating document with data: %s", data)
    mock_client.__getitem__.assert_called_with(mock_database_api.db_name)
    mock_db.create_document.assert_called_with(data, throw_on_exists=True)
    mock_couch.__enter__.assert_called_once()
    mock_couchdb_call.assert_called_once_with(mock_database_api.username, mock_database_api.password,
                                              url=mock_database_api.url, connect=True)
    assert actual_document == expected_document
    if expected_document is None:
      mock_database_api.logger.error.assert_called_once_with('Error creating document: %s', exception)
    else:
      mock_database_api.logger.error.assert_not_called()

  # Happy path tests with various realistic test values
  @pytest.mark.parametrize("document_id, expected_doc",
                           [pytest.param("12345", {'_id': '12345', 'data': 'value'}, id="valid_id_with_data"),
                             pytest.param("67890", {'_id': '67890', 'data': 'value'},
                                          id="valid_id_with_different_data"), ], ids=str)
  def test_get_document_success_path(self, mocker, document_id, expected_doc, mock_database_api):
    # Arrange
    mock_client = mocker.MagicMock()
    mock_couch = mocker.MagicMock()
    mock_db = mocker.MagicMock()
    mock_couch.__enter__.return_value = mock_client
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = expected_doc
    mock_couchdb_call = mocker.patch('pasta_eln.dataverse.base_database_api.couchdb', return_value=mock_couch)

    # Act
    result = mock_database_api.get_document(document_id)

    # Assert
    assert result == expected_doc
    mock_db.__getitem__.assert_called_with(document_id)
    mock_database_api.logger.info.assert_called_with('Retrieving document with id: %s', document_id)
    mock_client.__getitem__.assert_called_with(mock_database_api.db_name)
    mock_couch.__enter__.assert_called_once()
    mock_couchdb_call.assert_called_once_with(mock_database_api.username, mock_database_api.password,
                                              url=mock_database_api.url, connect=True)

  # Edge cases
  # (No edge cases identified for this function as it has a straightforward behavior)

  # Error cases
  @pytest.mark.parametrize("document_id, exception",
                           [pytest.param("nonexistent_id", KeyError, id="nonexistent_document"),
                             pytest.param(None, DatabaseError, id="none_as_document_id"), ], ids=str)
  def test_get_document_error_cases(self, mocker, document_id, exception, mock_database_api):
    # Arrange
    mock_client = mocker.MagicMock()
    mock_couch = mocker.MagicMock()
    mock_db = mocker.MagicMock()
    mock_couch.__enter__.return_value = mock_client
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.side_effect = exception
    mocker.patch('pasta_eln.dataverse.base_database_api.couchdb', return_value=mock_couch)
    if document_id is None:
      mock_database_api.log_and_raise_error = mocker.MagicMock(
        side_effect=DatabaseError("Document ID cannot be empty!"))

    # Act & Assert
    if document_id is not None:
      assert (mock_database_api.get_document(
        document_id) is None), f"Expected None, got {mock_database_api.get_document(document_id)}"
      mock_database_api.logger.error("Error retrieving document: %s", exception)
    else:
      with pytest.raises(exception):
        mock_database_api.get_document(document_id)
        mock_database_api.logger.error("Document ID cannot be empty!")

  # Parametrized test cases
  @pytest.mark.parametrize("test_id, input_data, expected_data",
                           [# Success path tests with various realistic test values
                             ("SuccessCase_01", {'_id': '123', 'name': 'Spaghetti', 'type': 'Pasta'},
                              {'name': 'Spaghetti', 'type': 'Pasta'}), (
                               "SuccessCase_02", {'_id': '456', 'color': 'Yellow', 'texture': 'Smooth'},
                               {'color': 'Yellow', 'texture': 'Smooth'}),

                             # Edge cases
                             ("EdgeCase_01", {'_id': '789', '_rev': '1-abc', 'name': ''}, {'name': ''}),
                             # Empty string value
                             ("EdgeCase_02", {'_id': '101', '_rev': '2-def'}, {}),  # No fields other than _id and _rev
                           ])
  def test_update_document(self, mocker, test_id, input_data, expected_data, mock_database_api):
    # Arrange
    mock_client = mocker.MagicMock()
    mock_couch = mocker.MagicMock()
    mock_doc = mocker.MagicMock()
    mock_db = mocker.MagicMock()
    mock_couch.__enter__.return_value = mock_client
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.side_effect = expected_data
    couchdb_constructor = mocker.patch('pasta_eln.dataverse.base_database_api.couchdb', return_value=mock_couch)
    mock_doc.__enter__.return_value = mock_doc
    mock_dock_dict = {}
    mock_doc.__setitem__.side_effect = mock_dock_dict.__setitem__
    doc_constructor = mocker.patch('pasta_eln.dataverse.base_database_api.Document', return_value=mock_doc)
    # Act
    mock_database_api.update_document(input_data)

    # Assert
    assert mock_dock_dict == expected_data
    mock_database_api.logger.info.assert_called_with('Updating document with data: %s', input_data)
    doc_constructor.assert_called_once_with(mock_db, input_data['_id'])
    couchdb_constructor.assert_called_once_with(mock_database_api.username, mock_database_api.password,
                                                url=mock_database_api.url, connect=True)

  @pytest.mark.parametrize("test_id, design_document_name, view_name, map_func, reduce_func, expected_call",
                           [# Success path tests
                             ("SuccessCase-1", "design_doc_1", "view_1", "function(doc) { emit(doc._id, 1); }", None,
                              True), (
                           "SuccessCase-2", "design_doc_2", "view_2", "function(doc) { emit(doc.name, doc.age); }",
                           "_sum", True), # Edge cases
                             ("EdgeCase-1", "", "view", "function(doc) { emit(doc._id, 1); }", None, True),
                             # Empty design document name
                             ("EdgeCase-2", "design_doc", "", "function(doc) { emit(doc._id, 1); }", None, True),
                             # Empty view name
                             # Error cases
                             ("ErrorCase-1", None, "view", "function(doc) { emit(doc._id, 1); }", None, False),
                             # None as design document name
                             ("ErrorCase-2", "design_doc", None, "function(doc) { emit(doc._id, 1); }", None, False),
                             # None as view name
                           ])
  def test_add_view(self, mocker, test_id, design_document_name, view_name, map_func, reduce_func, expected_call,
                    mock_database_api):
    # Arrange
    mock_client = mocker.MagicMock()
    mock_couch = mocker.MagicMock()
    mock_design_doc = mocker.MagicMock()
    mock_db = mocker.MagicMock()
    mock_add_view = mocker.MagicMock()
    mock_couch.__enter__.return_value = mock_client
    mock_design_doc.__enter__.return_value = mock_design_doc
    mock_design_doc.add_view = mock_add_view
    mock_client.__getitem__.return_value = mock_db
    couchdb_constructor = mocker.patch('pasta_eln.dataverse.base_database_api.couchdb', return_value=mock_couch)
    doc_constructor = mocker.patch('pasta_eln.dataverse.base_database_api.DesignDocument', return_value=mock_design_doc)

    # Act
    try:
      mock_database_api.add_view(design_document_name, view_name, map_func, reduce_func)
      call_success = True
    except Exception:
      call_success = False

    # Assert
    assert call_success == expected_call
    if expected_call:
      mock_design_doc.add_view.assert_called_with(view_name, map_func, reduce_func)
    else:
      mock_design_doc.add_view.assert_not_called()

  @pytest.mark.parametrize("design_document_name, view_name, map_func, reduce_func, test_id", [# Success path tests
    ("design_doc_1", "view_1", "function(doc) { emit(doc._id, 1); }", "_count", "success_case_1"),
    ("design_doc_2", "view_2", "function(doc) { emit(doc.name, doc.age); }", None, "success_case_2"),

    # Edge cases
    ("design_doc_3", "view_3", "function(doc) { emit(doc._id, 1); }", "", "edge_case_empty_reduce"),

    # Error cases
    (None, "view_4", "function(doc) { emit(doc._id, 1); }", None, "error_case_no_design_doc"),
    ("design_doc_5", None, "function(doc) { emit(doc._id, 1); }", None, "error_case_no_view_name"),
    ("design_doc_6", "view_6", None, None, "error_case_no_map_func"), ])
  def test_add_view(self, mocker, design_document_name, view_name, map_func, reduce_func, test_id, mock_database_api):
    # Arrange
    mock_client = mocker.MagicMock()
    mock_couch = mocker.MagicMock()
    mock_design_doc = mocker.MagicMock()
    mock_db = mocker.MagicMock()
    mock_add_view = mocker.MagicMock()
    mock_couch.__enter__.return_value = mock_client
    mock_design_doc.__enter__.return_value = mock_design_doc
    mock_design_doc.add_view = mock_add_view
    mock_client.__getitem__.return_value = mock_db
    couchdb_constructor = mocker.patch('pasta_eln.dataverse.base_database_api.couchdb', return_value=mock_couch)
    doc_constructor = mocker.patch('pasta_eln.dataverse.base_database_api.DesignDocument', return_value=mock_design_doc)

    # Act
    if test_id.startswith("error_case"):
      with pytest.raises(DatabaseError):
        mock_database_api.add_view(design_document_name, view_name, map_func, reduce_func)
    else:
      mock_database_api.add_view(design_document_name, view_name, map_func, reduce_func)

    # Assert
    mock_database_api.logger.info.assert_called_with(
      'Adding view: %s to design document: %s, map_func: %s, reduce_func: %s', view_name, design_document_name,
      map_func, reduce_func)
    if test_id.startswith("success_case"):
      mock_database_api.logger.info.assert_called()
      mock_add_view.assert_called_with(view_name, map_func, reduce_func)
      couchdb_constructor.assert_called_once_with(mock_database_api.username, mock_database_api.password,
                                                  url=mock_database_api.url, connect=True)
      doc_constructor.assert_called_once_with(mock_db, design_document_name)
    elif test_id.startswith("edge_case"):
      mock_database_api.logger.info.assert_called()
      mock_add_view.assert_called_with(view_name, map_func, reduce_func)
      couchdb_constructor.assert_called_once_with(mock_database_api.username, mock_database_api.password,
                                                  url=mock_database_api.url, connect=True)
      doc_constructor.assert_called_once_with(mock_db, design_document_name)
    elif test_id.startswith("error_case"):
      mock_add_view.assert_not_called()
      mock_database_api.logger.error.assert_called_with(
        "Design document name, view name, and map function cannot be empty!")

  @pytest.mark.parametrize(
    "design_document_name, view_name, map_func, reduce_func, view_result, expected_results, test_id",
    [# Success case tests
      ("design_doc_1", "view_1", None, None, [{"value": {'key': 'value'}}], [{'key': 'value'}],
       "success_case_no_map_reduce"), ("design_doc_2", "view_2", "function(doc) { emit(doc._id, 1); }", "_count",
                                       [{"value": {'key': 'value'}}, {"value": {'key': 'value'}}],
                                       [{'key': 'value'}, {'key': 'value'}], "success_case_with_map_reduce"),

      # Edge cases
      # Assuming empty map_func and reduce_func are valid and treated as None
      ("design_doc_3", "view_3", "", "", [{"value": {'key': 'value'}}], [{'key': 'value'}],
       "edge_case_empty_map_reduce"),

      # Error cases
      # None values for design_document_name and view_name should raise an error
      (None, "view_4", None, None, None, DatabaseError, "error_case_no_design_doc"),
      ("design_doc_5", None, None, None, None, DatabaseError, "error_case_no_view_name"), ])
  def test_get_view_results(self, mocker, design_document_name, view_name, map_func, reduce_func, view_result,
                            expected_results, test_id, mock_database_api):
    # Arrange
    mock_client = mocker.MagicMock()
    mock_couch = mocker.MagicMock()
    mock_design_doc = mocker.MagicMock()
    mock_db = mocker.MagicMock()
    mock_view = mocker.MagicMock()
    mock_view.result = view_result
    mock_add_view = mocker.MagicMock()
    mock_couch.__enter__.return_value = mock_client
    mock_design_doc.__enter__.return_value = mock_design_doc
    mock_design_doc.add_view = mock_add_view
    mock_client.__getitem__.return_value = mock_db
    couchdb_constructor = mocker.patch('pasta_eln.dataverse.base_database_api.couchdb', return_value=mock_couch)
    doc_constructor = mocker.patch('pasta_eln.dataverse.base_database_api.DesignDocument', return_value=mock_design_doc)
    view_constructor = mocker.patch('pasta_eln.dataverse.base_database_api.View', return_value=mock_view)

    # Act
    if isinstance(expected_results, type) and issubclass(expected_results, Exception):
      with pytest.raises(expected_results):
        mock_database_api.get_view_results(design_document_name, view_name, map_func, reduce_func)
    else:
      results = mock_database_api.get_view_results(design_document_name, view_name, map_func, reduce_func)

    # Assert
    mock_database_api.logger.info.assert_called_once_with(
      "Getting view results: %s from design document: %s, map_func: %s, reduce_func: %s", view_name,
      design_document_name, map_func, reduce_func)
    if not isinstance(expected_results, type):
      assert results == expected_results

      couchdb_constructor.assert_called_once_with(mock_database_api.username, mock_database_api.password,
                                                  url=mock_database_api.url, connect=True)
      doc_constructor.assert_called_once_with(mock_db, design_document_name)
      view_constructor.assert_called_once_with(mock_design_doc, view_name, map_func, reduce_func)
    else:
      couchdb_constructor.assert_not_called()
      doc_constructor.assert_not_called()
      view_constructor.assert_not_called()
      mock_database_api.logger.error.assert_called_with("Design document name and view name cannot be empty!")

  @pytest.mark.parametrize(
    "design_document_name, view_name, document_id, map_func, reduce_func, view_result, expected_result, test_id",
    [# Success path tests
      ("design_doc_1", "view_1", "doc_1", None, None, {"doc_1": [{"value": {'key': 'value'}}]}, {'key': 'value'},
       "success_path_1"), (
    "design_doc_2", "view_2", "doc_2", "map_func_2", "reduce_func_2", {"doc_2": [{"value": {'key': 'value'}}]},
    {'key': 'value'}, "success_path_2"),

      # Error cases
      (None, "view_1", "doc_1", None, None, None, None, "error_missing_design_document"),
      ("design_doc_1", None, "doc_1", None, None, None, None, "error_missing_view_name"),
      ("design_doc_1", "view_1", None, None, None, None, None, "error_missing_document_id"), ])
  def test_get_view_results_by_id(self, mocker, design_document_name, view_name, document_id, map_func, reduce_func,
                                  view_result, expected_result, test_id, mock_database_api):
    # Arrange
    mock_client = mocker.MagicMock()
    mock_couch = mocker.MagicMock()
    mock_design_doc = mocker.MagicMock()
    mock_db = mocker.MagicMock()
    mock_view = mocker.MagicMock()
    mock_view.result = view_result
    mock_add_view = mocker.MagicMock()
    mock_couch.__enter__.return_value = mock_client
    mock_design_doc.__enter__.return_value = mock_design_doc
    mock_design_doc.add_view = mock_add_view
    mock_client.__getitem__.return_value = mock_db
    couchdb_constructor = mocker.patch('pasta_eln.dataverse.base_database_api.couchdb', return_value=mock_couch)
    doc_constructor = mocker.patch('pasta_eln.dataverse.base_database_api.DesignDocument', return_value=mock_design_doc)
    view_constructor = mocker.patch('pasta_eln.dataverse.base_database_api.View', return_value=mock_view)

    # Act
    if expected_result is not None:
      result = mock_database_api.get_view_results_by_id(design_document_name, view_name, document_id, map_func,
                                                        reduce_func)
      # Assert
      assert result == expected_result
      mock_database_api.logger.info.assert_called()
      couchdb_constructor.assert_called_once_with(mock_database_api.username, mock_database_api.password,
                                                  url=mock_database_api.url, connect=True)
      doc_constructor.assert_called_once_with(mock_db, design_document_name)
      view_constructor.assert_called_once_with(mock_design_doc, view_name, map_func, reduce_func)
    else:
      with pytest.raises(DatabaseError):
        mock_database_api.get_view_results_by_id(design_document_name, view_name, document_id, map_func, reduce_func)
        # Assert
        mock_database_api.logger.info.assert_called()
        mock_database_api.logger.error.assert_called_with(
          "Design document name, view name and document id cannot be empty!")

  @pytest.mark.parametrize("test_id, design_document_name, view_name, expected_result", [# Success path tests
    ("SuccessCase-1", "design_doc_1", "view_1", MagicMock()), ("SuccessCase-2", "design_doc_2", "view_2", MagicMock()),
    # Edge cases
    ("EdgeCase-1", "", "view", None),  # Empty design document name
    ("EdgeCase-2", "design_doc", "", None),  # Empty view name
    # Error cases
    ("ErrorCase-1", None, "view", DatabaseError("Design document name and view name cannot be empty")),
    # None design document name
    ("ErrorCase-2", "design_doc", None, DatabaseError("Design document name and view name cannot be empty")),
    # None view name
  ])
  def test_get_view(self, mocker, test_id, design_document_name, view_name, expected_result, mock_database_api):
    # Arrange
    mock_client = mocker.MagicMock()
    mock_couch = mocker.MagicMock()
    mock_design_doc = mocker.MagicMock()
    mock_db = mocker.MagicMock()
    mock_design_doc.get_view.return_value = expected_result
    mock_add_view = mocker.MagicMock()
    mock_couch.__enter__.return_value = mock_client
    mock_design_doc.__enter__.return_value = mock_design_doc
    mock_design_doc.add_view = mock_add_view
    mock_client.__getitem__.return_value = mock_db
    mocker.patch('pasta_eln.dataverse.base_database_api.couchdb', return_value=mock_couch)
    mocker.patch('pasta_eln.dataverse.base_database_api.DesignDocument', return_value=mock_design_doc)

    # Act
    if isinstance(expected_result, Exception):
      with pytest.raises(type(expected_result)):
        mock_database_api.get_view(design_document_name, view_name)
    else:
      result = mock_database_api.get_view(design_document_name, view_name)

    # Assert
    if not isinstance(expected_result, Exception):
      assert result == expected_result
      mock_database_api.logger.info.assert_called_with("Retrieving view: %s from design document: %s", view_name,
                                                       design_document_name)
