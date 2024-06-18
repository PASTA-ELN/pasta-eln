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
from cloudant.error import CloudantClientException, CloudantDatabaseException

from pasta_eln.dataverse.base_database_api import BaseDatabaseAPI
from pasta_eln.dataverse.database_error import DatabaseError
from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError

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
  mocker.patch('pasta_eln.dataverse.base_database_api.Lock')
  return BaseDatabaseAPI("host", 1234, "user", "pass")


class TestDataverseBaseDatabaseApi:

  # Parametrized test for a success path
  @pytest.mark.parametrize("config_content, expected_username, expected_password",
                           [(create_mock_config(), USER, PASSWORD),
                            # Add more test cases with different realistic values if necessary
                            ], ids=["success_path_default"])
  def test_base_database_api_init_success_path(self, mocker, config_content, expected_username,
                                               expected_password):
    # Arrange
    mock_lock = mocker.patch('pasta_eln.dataverse.base_database_api.Lock')
    with patch('logging.Logger.error') as mock_logger_error:
      # Act
      base_db_api = BaseDatabaseAPI("host", 1234, expected_username, expected_password)

      # Assert
      assert base_db_api.username == expected_username
      assert compare_digest(base_db_api.password, expected_password)
      mock_logger_error.assert_not_called()
      assert base_db_api.update_lock == mock_lock.return_value, "Expected update_lock to be a mock Lock object"

  @pytest.mark.parametrize(
    "hostname, port, username, password",
    [
      ("localhost", 8080, "admin", "admin123"),  # happy path
      ("127.0.0.1", 5432, "user", "pass"),  # happy path
      ("db.example.com", 3306, "root", "root"),  # happy path
      ("", 8080, "admin", "admin123"),  # edge case: empty hostname
      ("localhost", 0, "admin", "admin123"),  # edge case: port 0
      ("localhost", 65535, "admin", "admin123"),  # edge case: max port number
      ("localhost", 8080, "", "admin123"),  # edge case: empty username
      ("localhost", 8080, "admin", ""),  # edge case: empty password
      (None, 8080, "admin", "admin123"),  # error case: None hostname
      ("localhost", None, "admin", "admin123"),  # error case: None port
      ("localhost", 8080, None, "admin123"),  # error case: None username
      ("localhost", 8080, "admin", None),  # error case: None password
    ],
    ids=[
      "success_path_localhost_8080",
      "success_path_127.0.0.1_5432",
      "success_path_db_example_com_3306",
      "edge_case_empty_hostname",
      "edge_case_port_0",
      "edge_case_max_port_number",
      "edge_case_empty_username",
      "edge_case_empty_password",
      "error_case_none_hostname",
      "error_case_none_port",
      "error_case_none_username",
      "error_case_none_password",
    ]
  )
  def test_base_database_api_init(self, mocker, hostname, port, username, password):
    # Arrange
    mock_logger = mocker.patch('pasta_eln.dataverse.base_database_api.logging.getLogger')
    mock_lock = mocker.patch('pasta_eln.dataverse.base_database_api.Lock')

    # Act
    if hostname is None or port is None or username is None or password is None:
      with pytest.raises(IncorrectParameterError):
        BaseDatabaseAPI(hostname, port, username, password)
    else:
      instance = BaseDatabaseAPI(hostname, port, username, password)

      # Assert
      assert instance.host == hostname
      assert instance.port == port
      assert instance.url == f'http://{hostname}:{port}'
      assert instance.username == username
      assert instance.password == password
      assert instance.update_lock == mock_lock.return_value
      mock_lock.assert_called_once()
      mock_logger.assert_called_once_with('pasta_eln.dataverse.base_database_api.BaseDatabaseAPI')
      assert instance.logger == mock_logger.return_value

  # @pytest.mark.parametrize("config, db_name, expected_username, expected_password, test_id", [
  #   ({"projectGroups": {"test_db": {"local": {"user": "test_user", "password": "test_pass"}}}}, "test_db", "test_user",
  #    "test_pass", "success_path"),
  #   ({"projectGroups": {"test_db": {"local": {"user": "user1", "password": "pass1"}}}}, "test_db", "user1", "pass1",
  #    "alternate_credentials"),
  #   # Add more test cases for different realistic values
  # ])
  # def test_set_username_password_success_path(self, mocker, mock_database_api, config, db_name, expected_username,
  #                                             expected_password, test_id):
  #   # Arrange
  #   mock_database_api.dataverse_db_name = db_name
  #
  #   # Act
  #   mock_database_api.set_username_password(config)
  #
  #   # Assert
  #   assert mock_database_api.username == expected_username, f"Test ID: {test_id} - Expected username to be {expected_username}"
  #   assert mock_database_api.password == expected_password, f"Test ID: {test_id} - Expected password to be {expected_password}"

  # @pytest.mark.parametrize("config, db_name, expected_exception, test_id", [
  #   ({}, "test_db", ConfigError, "empty_config"),
  #   ({"projectGroups": {}}, "test_db", ConfigError, "missing_project_groups"),
  #   ({"projectGroups": {"test_db": {}}}, "test_db", ConfigError, "missing_local_info"),
  #   ({"projectGroups": {"test_db": {"local": {}}}}, "test_db", ConfigError, "missing_user_password"),
  #   # Add more test cases for different error scenarios
  # ])
  # def test_set_username_password_error_cases(self, mocker, mock_database_api, config, db_name, expected_exception,
  #                                            test_id):
  #   # Arrange
  #   mock_database_api.dataverse_db_name = db_name
  #
  #   # Act & Assert
  #   with pytest.raises(expected_exception) as exc_info:
  #     mock_database_api.set_username_password(config)
  #   assert exc_info, f"Test ID: {test_id} - Expected exception {expected_exception.__name__} was not raised"
  @pytest.mark.parametrize(
    "db_name, client_create_db_side_effect, expected_warning, expected_db_name",
    [
      ("test_db", None, None, "test_db"),  # happy path
      ("edge_case_db", None, None, "edge_case_db"),  # another happy path
      ("existing_db", CloudantClientException("Database exists"), 'Error creating database: %s',
       "existing_db"),  # database exists
      ("", None, None, ""),  # edge case: empty database name
      ("special_chars_!@#", None, None, "special_chars_!@#"),  # edge case: special characters in name
    ],
    ids=[
      "success_path_test_db",
      "success_path_edge_case_db",
      "error_existing_db",
      "edge_case_empty_db_name",
      "edge_case_special_chars_db_name",
    ]
  )
  def test_create_database(self, mocker, mock_database_api, db_name, client_create_db_side_effect, expected_warning,
                           expected_db_name):
    # Arrange
    mock_database_api.username = "username"
    mock_database_api.password = "password"
    mock_database_api.url = "http://localhost:5984"

    mock_client = mocker.MagicMock()
    mock_couch = mocker.MagicMock()
    mock_couch.__enter__.return_value = mock_client
    if client_create_db_side_effect:
      mock_client.create_database.side_effect = client_create_db_side_effect
    mock_client.create_database.return_value = db_name
    mock_client.__getitem__.return_value = expected_db_name
    mock_couchdb_call = mocker.patch('pasta_eln.dataverse.base_database_api.couchdb', return_value=mock_couch)

    # Act
    db = mock_database_api.create_database(db_name)

    # Assert
    if expected_warning:
      mock_database_api.logger.warning.assert_called_once_with(expected_warning, client_create_db_side_effect)
      mock_client.__getitem__.assert_called_once_with(db_name)
    else:
      mock_database_api.logger.warning.assert_not_called()
    assert db == expected_db_name
    mock_client.create_database.assert_called_once_with(db_name, throw_on_exists=True)
    mock_couchdb_call.assert_called_once_with("username", "password", url="http://localhost:5984", connect=True)
    mock_database_api.logger.info.assert_called_once_with("Creating database with name : %s", db_name)

  @pytest.mark.parametrize("test_id, data, expected_document",
                           [  # Success path tests with various realistic test values
                             ("Success-1", {"name": "Spaghetti", "type": "Pasta"},
                              {"name": "Spaghetti", "type": "Pasta"}),
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
    actual_document = mock_database_api.create_document(data, "test_db")

    # Assert
    mock_database_api.logger.info.assert_called_with(f"Creating document with data: %s in database: %s", data,
                                                     "test_db")
    mock_client.__getitem__.assert_called_with("test_db")
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
    result = mock_database_api.get_document(document_id, "test_db")

    # Assert
    assert result == expected_doc
    mock_db.__getitem__.assert_called_with(document_id)
    mock_database_api.logger.info.assert_called_with('Retrieving document with id: %s from database: %s', document_id,
                                                     "test_db")
    mock_client.__getitem__.assert_called_with("test_db")
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
        document_id, "test_db") is None), f"Expected None, got {mock_database_api.get_document(document_id)}"
      mock_database_api.logger.error("Error retrieving document: %s", exception)
    else:
      with pytest.raises(exception):
        mock_database_api.get_document(document_id, "test_db")
        mock_database_api.logger.error("Document ID cannot be empty!")

  # Parametrized test cases
  @pytest.mark.parametrize("test_id, input_data, expected_data",
                           [  # Success path tests with various realistic test values
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
    mock_database_api.update_document(input_data, "test_db")

    # Assert
    assert mock_dock_dict == expected_data
    mock_database_api.logger.info.assert_called_with('Updating document with data: %s in database: %s', input_data,
                                                     "test_db")
    doc_constructor.assert_called_once_with(mock_db, input_data['_id'])
    couchdb_constructor.assert_called_once_with(mock_database_api.username, mock_database_api.password,
                                                url=mock_database_api.url, connect=True)
    mock_database_api.update_lock.__enter__.assert_called_once()

  @pytest.mark.parametrize("test_id, design_document_name, view_name, map_func, reduce_func, expected_call",
                           [  # Success path tests
                             ("SuccessCase-1", "design_doc_1", "view_1", "function(doc) { emit(doc._id, 1); }", None,
                              True), (
                               "SuccessCase-2", "design_doc_2", "view_2", "function(doc) { emit(doc.name, doc.age); }",
                               "_sum", True),  # Edge cases
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
      mock_database_api.add_view("test_db", design_document_name, view_name, map_func, reduce_func)
      call_success = True
    except Exception:
      call_success = False

    # Assert
    assert call_success == expected_call
    couchdb_constructor.assert_called_once_with(mock_database_api.username, mock_database_api.password,
                                                url=mock_database_api.url, connect=True)
    doc_constructor.assert_called_once_with(mock_db, design_document_name)
    mock_database_api.logger.info.assert_called_with('Adding view: %s to design document: %s, map_func: %s, '
                                                     'reduce_func: %s', view_name, design_document_name, map_func,
                                                     reduce_func)
    if expected_call:
      mock_design_doc.add_view.assert_called_with(view_name, map_func, reduce_func)
    else:
      mock_design_doc.add_view.assert_not_called()

  @pytest.mark.parametrize("design_document_name, view_name, map_func, reduce_func, test_id", [  # Success path tests
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
        mock_database_api.add_view("test_db", design_document_name, view_name, map_func, reduce_func)
    else:
      mock_database_api.add_view("test_db", design_document_name, view_name, map_func, reduce_func)

    # Assert
    mock_database_api.logger.info.assert_called_with(
      "Adding view: %s to design document: %s, map_func: %s, reduce_func: %s in database: %s",
      view_name,
      design_document_name,
      map_func,
      reduce_func,
      "test_db")
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
    [  # Success case tests
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
        mock_database_api.get_view_results("test_db", design_document_name, view_name, map_func, reduce_func)
    else:
      results = mock_database_api.get_view_results("test_db", design_document_name, view_name, map_func, reduce_func)

    # Assert
    mock_database_api.logger.info.assert_called_once_with(
      "Getting view results: %s from design document: %s, map_func: %s, reduce_func: %s in database: %s", view_name,
      design_document_name, map_func, reduce_func, "test_db")
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
    [  # Success path tests
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
      result = mock_database_api.get_view_results_by_id("test_db",
                                                        design_document_name,
                                                        view_name,
                                                        document_id,
                                                        map_func,
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

  @pytest.mark.parametrize("test_id, design_document_name, view_name, expected_result", [  # Success path tests
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
        mock_database_api.get_view("test_db", design_document_name, view_name)
    else:
      result = mock_database_api.get_view("test_db", design_document_name, view_name)

    # Assert
    if not isinstance(expected_result, Exception):
      assert result == expected_result
      mock_database_api.logger.info.assert_called_with("Retrieving view: %s from design document: %s in database: %s",
                                                       view_name,
                                                       design_document_name, "test_db")

  # Parametrized test cases for various scenarios
  @pytest.mark.parametrize(
    "design_document_name, view_name, limit, start_key, start_key_doc_id, expected_result, test_id", [
      ("design1", "view1", 10, None, None, [{"id": "1"}], "happy_path_no_start_keys"),
      ("design1", "view1", 5, 100, "doc100", [{"id": "100"}], "happy_path_with_start_keys"),
      ("design1", "view1", 0, None, None, [], "edge_case_zero_limit"),
      (None, "view1", 10, None, None, DatabaseError, "error_case_no_design_document"),
      ("design1", None, 10, None, None, DatabaseError, "error_case_no_view_name"),
    ])
  def test_get_paginated_view_results(self, mock_database_api, mocker,
                                      design_document_name, view_name, limit, start_key, start_key_doc_id,
                                      expected_result, test_id):
    # Arrange
    mock_client = mocker.MagicMock()
    mock_couch = mocker.MagicMock()
    mock_design_doc = mocker.MagicMock()
    mock_db = mocker.MagicMock()
    mock_couch.__enter__.return_value = mock_client
    mock_design_doc.__enter__.return_value = mock_design_doc
    mock_client.__getitem__.return_value = mock_db
    mock_result = mocker.patch('pasta_eln.dataverse.base_database_api.Result')
    mock_result.return_value = expected_result if not isinstance(expected_result, type) else MagicMock()
    mocker.patch('pasta_eln.dataverse.base_database_api.couchdb', return_value=mock_couch)
    mocker.patch('pasta_eln.dataverse.base_database_api.DesignDocument', return_value=mock_design_doc)

    # Act
    if isinstance(expected_result, type) and issubclass(expected_result, Exception):
      with pytest.raises(expected_result):
        mock_database_api.get_paginated_view_results("test_db", design_document_name, view_name, limit, start_key,
                                                     start_key_doc_id)
    else:
      result = mock_database_api.get_paginated_view_results("test_db", design_document_name, view_name, limit,
                                                            start_key,
                                                            start_key_doc_id)

    # Assert
    if not isinstance(expected_result, type):
      assert result == expected_result
      mock_database_api.logger.info.assert_called_once_with(
        "Retrieving paginated view results, View: %s from design document: %s, limit: %s, start_key_doc_id: %s, start_key: %s in database: %s",
        view_name,
        design_document_name,
        limit,
        start_key_doc_id,
        start_key,
        "test_db")
      mock_result.assert_called_once()
      mock_design_doc.get_view.assert_called_once_with(view_name)

  @pytest.mark.parametrize("test_id, index_name, index_type, fields, expected_exception, expected_log", [
    # Happy path tests
    ("HP-1", "test_index", "json", [{"name": "field1", "type": "asc"}], None, "Creating query index"),
    ("HP-2", "unique_index", "text", [{"name": "field2", "type": "desc"}], None, "Creating query index"),

    # Edge cases
    ("EC-1", "test_index", "json", [], None, "Creating query index"),  # Empty fields list

    # Error cases
    (
        "ER-1", None, "json", [{"name": "field1", "type": "asc"}], DatabaseError,
        "Index name and fields cannot be empty!"),
    ("ER-2", "test_index", "json", None, DatabaseError, "Index name and fields cannot be empty!"),
    ("ER-3", "test_index", "json", [{"name": "field1", "type": "asc"}], None, "Index already exists"),
  ])
  def test_create_query_index(self, mock_database_api, mocker, test_id, index_name, index_type, fields,
                              expected_exception, expected_log):
    # Arrange
    mock_client = mocker.MagicMock()
    mock_couch = mocker.MagicMock()
    mock_db = mocker.MagicMock()
    mock_couch.__enter__.return_value = mock_client
    mock_client.__getitem__.return_value = mock_db
    mocker.patch('pasta_eln.dataverse.base_database_api.couchdb', return_value=mock_couch)
    property_mock = mocker.PropertyMock()
    property_mock.name = index_name
    mock_db.get_query_indexes.return_value = [] if test_id != "ER-3" else [property_mock]

    # Act
    if expected_exception:
      with pytest.raises(expected_exception) as exc_info:
        mock_database_api.create_query_index("test_db", index_name, index_type, fields)
    else:
      mock_database_api.create_query_index("test_db", index_name, index_type, fields)

    # Assert
    mock_database_api.logger.info.assert_called_once_with(
      "Creating query index, name: %s, index_type: %s, fields: %s in database: %s",
      index_name,
      index_type,
      fields,
      "test_db")
    if test_id == "ER-3":
      mock_database_api.logger.warning.assert_called_with("Index already exists: %s", index_name)
    elif not expected_exception:
      mock_db.create_query_index.assert_called_with(index_name=index_name, index_type=index_type, fields=fields)

  @pytest.mark.parametrize("filter_term, filter_fields, bookmark, limit, expected_selector, expected_bookmark, test_id",
                           [
                             # Happy path tests
                             (None, None, None, 10, {"data_type": "dataverse_upload"}, None, "HP-1"),
                             ("test", ["field1", "field2"], None, 10, {"$and": [{"data_type": "dataverse_upload"}, {
                               "$or": [{"field1": {"$regex": "(?i).*test.*"}},
                                       {"field2": {"$regex": "(?i).*test.*"}}]}]}, None, "HP-2"),
                             ("test", ["field1"], "bookmark123", 10, {"$and": [{"data_type": "dataverse_upload"}, {
                               "$or": [{"field1": {"$regex": "(?i).*test.*"}}]}]}, "bookmark123", "HP-3"),

                             # Edge cases
                             ("", ["field1"], None, 10, {"data_type": "dataverse_upload"}, None, "EC-1"),
                             # Empty filter term
                             ("test", [], None, 10, {"data_type": "dataverse_upload"}, None, "EC-2"),
                             # Empty filter fields
                             ("test", None, None, 10, {"data_type": "dataverse_upload"}, None, "EC-3"),
                             # None filter fields

                             # Error cases
                             (None, ["field1"], None, 10, {"data_type": "dataverse_upload"}, None, "ER-1"),
                             # None filter term with non-empty filter fields
                           ])
  def test_get_paginated_upload_model_query_results(self, mock_database_api, mocker, filter_term, filter_fields,
                                                    bookmark, limit, expected_selector, expected_bookmark, test_id):
    # Arrange
    mock_client = mocker.MagicMock()
    mock_couch = mocker.MagicMock()
    mock_query = mocker.MagicMock()
    mock_db = mocker.MagicMock()
    mock_couch.__enter__.return_value = mock_client
    mock_client.__getitem__.return_value = mock_db
    mock_couch_db_ctr = mocker.patch('pasta_eln.dataverse.base_database_api.couchdb', return_value=mock_couch)
    mock_query_ctr = mocker.patch('pasta_eln.dataverse.base_database_api.Query', return_value=mock_query)
    mock_query.return_value = {"docs": [], "bookmark": "new_bookmark"}

    # Act
    result = mock_database_api.get_paginated_upload_model_query_results("test_db",
                                                                        filter_term=filter_term,
                                                                        filter_fields=filter_fields, bookmark=bookmark,
                                                                        limit=limit)

    # Assert
    mock_database_api.logger.info.assert_called_once_with(
      "Getting paginated upload model query results: filter_term: %s, filter_fields: %s, bookmark: %s, limit: %s from database: %s",
      filter_term,
      ",".join(filter_fields) if filter_fields else None,
      bookmark,
      limit,
      "test_db")
    mock_couch_db_ctr.assert_called_with(mock_database_api.username, mock_database_api.password,
                                         url=mock_database_api.url, connect=True)
    mock_client.__getitem__.assert_called_with("test_db")
    mock_query_ctr.assert_called_with(mock_db, selector=expected_selector, sort=[{'finished_date_time': 'desc'}],
                                      limit=limit)
    if expected_bookmark:
      mock_query.assert_called_with(bookmark=expected_bookmark)
    else:
      mock_query.assert_called_with()
    assert result == {"docs": [], "bookmark": "new_bookmark"}, f"Failed test ID: {test_id}"
