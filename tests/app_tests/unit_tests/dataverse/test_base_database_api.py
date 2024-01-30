#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_base_database_api.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from pathlib import Path

import pytest
import json
from unittest.mock import patch, mock_open

from cloudant.document import Document

from pasta_eln.dataverse.database_error import DatabaseError
from pasta_eln.dataverse.base_database_api import BaseDatabaseAPI
from secrets import compare_digest

# Constants for test cases
CONFIG_FILE_PATH = '/home/user/.pastaELN.json'
DEFAULT_PROJECT_GROUP = 'my_project_group'
USER = 'test_user'
PASSWORD = 'test_password'


@pytest.fixture
def mock_couchdb_client():
  with patch('pasta_eln.dataverse.base_database_api.couchdb') as mock:
    yield mock


@pytest.fixture
def mock_config_file(mocker):
  with patch('pathlib.Path.exists') as mock_exists:
    mock_open_file = mocker.MagicMock()
    mocker.patch.object(mock_open_file, '__enter__', return_value=mock_open_file)
    mock_os_open = mocker.patch('pasta_eln.dataverse.base_database_api.open',
                                return_value=mock_open_file)
    mock_open_file.read.return_value = '{"defaultProjectGroup": "test", "projectGroups": {"test": {"local": {"user": "testuser", "password": "testpass"}}}}'
    return mock_open_file




@pytest.fixture
def mock_document(mocker):
  return mocker.MagicMock(spec=Document)


def create_mock_config(default_project_group_exists=True, user_and_password_exists=True):
  config = {}
  if default_project_group_exists:
    config['defaultProjectGroup'] = DEFAULT_PROJECT_GROUP
    if user_and_password_exists:
      config['projectGroups'] = {
        DEFAULT_PROJECT_GROUP: {
          'local': {
            'user': USER,
            'password': PASSWORD
          }
        }
      }
  return config

@pytest.fixture
def mock_database_api(mocker) -> BaseDatabaseAPI:
  mocker.patch('pasta_eln.dataverse.base_database_api.logging.getLogger')
  mocker.patch('pasta_eln.dataverse.base_database_api.Path.home', return_value='test_path')
  mocker.patch('pasta_eln.dataverse.base_database_api.join', return_value=CONFIG_FILE_PATH)
  mocker.patch('pasta_eln.dataverse.base_database_api.load', return_value=create_mock_config())
  #mocker.patch('pasta_eln.dataverse.base_database_api.BaseDatabaseAPI.set_username_password')
  with patch('pasta_eln.dataverse.base_database_api.open'), \
      patch('pasta_eln.dataverse.base_database_api.exists', return_value=True), \
      patch('pasta_eln.dataverse.base_database_api.logging.Logger.error'):
    return BaseDatabaseAPI()

class TestBaseDatabaseApi:
  # Parametrized test for success path
  @pytest.mark.parametrize("config_content, expected_db_name, expected_username, expected_password", [
    (create_mock_config(), DEFAULT_PROJECT_GROUP, USER, PASSWORD),
    # Add more test cases with different realistic values if necessary
  ], ids=["success_path_default"])
  def test_base_database_api_init_success_path(self, config_content, expected_db_name, expected_username, expected_password):
    # Arrange
    with patch('builtins.open', mock_open(read_data=config_content)), \
        patch('os.path.exists', return_value=True), \
        patch('logging.Logger.error') as mock_logger_error:
      # Act
      base_db_api = BaseDatabaseAPI()

      # Assert
      assert base_db_api.db_name == expected_db_name
      assert base_db_api.username == expected_username
      assert compare_digest(base_db_api.password, expected_password)
      mock_logger_error.assert_not_called()

  # Parametrized test for various error cases
  @pytest.mark.parametrize("config_content, exists_return_value, expected_error_message", [
    (create_mock_config(), False, "Config file not found, Corrupt installation!"),
    (create_mock_config(default_project_group_exists=False), True,
     "Incorrect config file, defaultProjectGroup not found!"),
    (create_mock_config(user_and_password_exists=False), True, "Incorrect config file, projectGroups not found!"),
    # Add more error cases if necessary
  ], ids=["error_no_config_file", "error_no_default_project_group", "error_no_user_password"])
  def test_base_database_api_init_error_cases(self, mocker, config_content, exists_return_value, expected_error_message):
    # Arrange
    home_mock = mocker.patch('pasta_eln.dataverse.base_database_api.Path.home', return_value='test_path')
    join_mock = mocker.patch('pasta_eln.dataverse.base_database_api.join', return_value=CONFIG_FILE_PATH)
    with patch('pasta_eln.dataverse.base_database_api.open', mock_open(read_data=config_content)), \
        patch('pasta_eln.dataverse.base_database_api.exists', return_value=exists_return_value), \
        patch('pasta_eln.dataverse.base_database_api.logging.Logger.error') as mock_logger_error:
      # Act & Assert
      with pytest.raises(DatabaseError) as exc_info:
        BaseDatabaseAPI()
      assert str(exc_info.value) == expected_error_message
      mock_logger_error.assert_called_once_with(expected_error_message)
      home_mock.assert_called_once()
      join_mock.assert_called_once_with(home_mock.return_value, ".pastaELN.json")


  # Mock the external dependencies
  # Parametrized test cases for create_document
  @pytest.mark.parametrize("test_id, data, expected_result", [
    # Happy path tests
    ("HP-1", {"type": "test"}, Document),
    # Edge cases
    # Error cases
  ])
  def test_create_document(self, test_id, data, expected_result, mock_couchdb_client, mock_config_file):
    # Arrange
    base_db_api = BaseDatabaseAPI()

    # Act
    result = base_db_api.create_document(data)

    # Assert
    assert isinstance(result, expected_result)
    
  def test_with_design_document(self, mocker, mock_database_api):
      created_document = {'type': 'test', '_id': '1733db7725a917262ce3950b440298d6', '_rev': '1-3b717529ff0f515c2c5d8aa52a2c03ab'}
      with patch('pasta_eln.dataverse.base_database_api.couchdb') as mock:
        yield mock
      data = {"type": "test"}
      result = mock_database_api.create_document(data)
      assert result == Document

  def test_with_document_crea(self):
      data = {"type": "test"}
      base_db_api = BaseDatabaseAPI()
      result = base_db_api.create_document(data)
      assert result == Document
      




