#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_utils.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import json
import logging
import os
from base64 import b64decode, b64encode
from unittest.mock import mock_open

import pytest
from cryptography.fernet import Fernet

from pasta_eln.dataverse.database_error import DatabaseError
from pasta_eln.dataverse.upload_status_values import UploadStatusValues
from pasta_eln.dataverse.utils import check_login_credentials, decrypt_data, encrypt_data, get_encrypt_key, \
  log_and_create_error, read_pasta_config_file, set_authors, update_status, write_pasta_config_file

# Constants for test
EXISTING_KEY = b64encode(Fernet.generate_key()).decode('ascii')
NEW_KEY = b64encode(Fernet.generate_key()).decode('ascii')
VALID_KEY = Fernet.generate_key()
HOME_DIR = "/home/user/"
CONFIG_FILE = '.pastaELN.json'
CONFIG_PATH = os.path.join(HOME_DIR, CONFIG_FILE)


class TestDataverseUtils:

  # Parametrized test cases for happy path, edge cases, and error cases
  @pytest.mark.parametrize("status, expected_icon_name, test_id",
                           [(UploadStatusValues.Queued.name, 'ph.queue-bold', 'happy_path_queued'),
                            (UploadStatusValues.Uploading.name, 'mdi6.progress-upload', 'happy_path_uploading'),
                            (UploadStatusValues.Cancelled.name, 'mdi.cancel', 'happy_path_cancelled'),
                            (UploadStatusValues.Finished.name, 'fa.check-circle-o', 'happy_path_finished'),
                            (UploadStatusValues.Error.name, 'msc.error-small', 'happy_path_error'),
                            (UploadStatusValues.Warning.name, 'fa.warning', 'happy_path_warning'), # Add edge cases here
                            # Add error cases here
                            ])
  def test_update_status(self, mocker, status, expected_icon_name, test_id):
    # Arrange
    status_icon_label = mocker.MagicMock()
    status_label = mocker.MagicMock()
    mock_icon = mocker.MagicMock()
    mock_icon.constructor = mocker.patch('pasta_eln.dataverse.utils.icon', return_value=mock_icon)

    # Act
    update_status(status, status_icon_label, status_label)

    # Assert
    status_label.setText.assert_called_once_with(status)
    # Check if the correct icon is set for the given status
    mock_icon.constructor.assert_called_once_with(expected_icon_name)
    status_icon_label.size.assert_called_once()
    status_icon_label.setPixmap.assert_called_once_with(mock_icon.pixmap.return_value)
    mock_icon.pixmap.assert_called_once_with(status_icon_label.size())

  @pytest.mark.parametrize("test_id, config_data",
                           [("SuccessCase-1", {"key": "value", "number": 42}), ("SuccessCase-2", {"empty_dict": {}}),
                            ("SuccessCase-3", {"list_key": [1, 2, 3]}), ], )
  def test_read_pasta_config_file_happy_path(self, mocker, test_id, config_data, tmp_path):
    # Arrange
    mock_logger = mocker.MagicMock(spec=logging.Logger)
    config_file = tmp_path / '.pastaELN.json'
    config_file.write_text(json.dumps(config_data))
    with mocker.patch('pasta_eln.dataverse.utils.Path.home', return_value=tmp_path):
      # Act
      result = read_pasta_config_file(mock_logger)

    # Assert
    assert result == config_data, f"Failed test ID: {test_id}"

  # Parametrized test for error scenarios
  @pytest.mark.parametrize("test_id, exception, message",
                           [("ErrorCase-1", DatabaseError, "Config file not found, Corrupt installation!"), ], )
  def test_read_pasta_config_file_error_path(self, mocker, test_id, exception, message, tmp_path):
    # Arrange
    mock_logger = mocker.MagicMock(spec=logging.Logger)
    with mocker.patch('pasta_eln.dataverse.utils.Path.home', return_value=tmp_path), mocker.patch(
        'pasta_eln.dataverse.utils.exists', return_value=False), pytest.raises(exception) as exc_info:
      # Act
      read_pasta_config_file(mock_logger)

    # Assert
    assert str(exc_info.value) == message, f"Failed test ID: {test_id}"
    mock_logger.error.assert_called_with(message)

  # Parametrized test for happy path scenarios with various realistic test values
  @pytest.mark.parametrize("exception_type, error_message, test_id",
                           [(ValueError, "Invalid value provided", 'happy_path_value_error'),
                            (TypeError, "Type mismatch encountered", 'happy_path_type_error'),
                            (KeyError, "Missing key in dictionary", 'happy_path_key_error'), ],
                           ids=lambda test_id: test_id)
  def test_log_and_create_error_happy_path(self, mocker, exception_type, error_message, test_id):
    # Arrange
    mock_logger = mocker.MagicMock(spec=logging.Logger)

    # Act
    raised_exception = log_and_create_error(mock_logger, exception_type, error_message)

    # Assert
    mock_logger.error.assert_called_once_with(error_message)
    assert isinstance(raised_exception, exception_type)
    assert raised_exception.args[0] == error_message

  # Parametrized test for edge cases
  @pytest.mark.parametrize("exception_type, error_message, test_id", [(Exception, "", 'edge_case_empty_message'), (
      RuntimeError, "  ", 'edge_case_whitespace_message'), (Exception, "A" * 1000, 'edge_case_long_message'), ],
                           ids=lambda test_id: test_id)
  def test_log_and_create_error_edge_cases(self, mocker, exception_type, error_message, test_id):
    # Arrange
    mock_logger = mocker.MagicMock(spec=logging.Logger)

    # Act
    raised_exception = log_and_create_error(mock_logger, exception_type, error_message)

    # Assert
    mock_logger.error.assert_called_once_with(error_message)
    assert isinstance(raised_exception, exception_type)
    assert str(raised_exception) == error_message

  # Parametrized test for error cases
  @pytest.mark.parametrize("exception_type, error_message, test_id",
                           [(None, "Exception type is None", 'error_case_none_exception_type'),
                            ("NotAType", "Exception type is not a type", 'error_case_not_a_type_exception_type'), ],
                           ids=lambda test_id: test_id)
  def test_log_and_create_error_error_cases(self, mocker, exception_type, error_message, test_id):
    # Arrange
    mock_logger = mocker.MagicMock(spec=logging.Logger)

    # Act & Assert
    with pytest.raises(TypeError):
      log_and_create_error(mock_logger, exception_type, error_message)

  # Parametrized test for success path with various realistic test values
  @pytest.mark.parametrize("config_data, metadata, expected_authors_list, test_id", [(
  {'authors': [{'last': 'Doe', 'first': 'John', 'orcid': '0000-0001', 'organizations': [{'organization': 'Org1'}]}]}, {
    'datasetVersion': {'metadataBlocks': {'citation': {'fields': [{'typeName': 'author', 'value': [
      {'authorName': {'value': 'Last, First'}, 'authorIdentifierScheme': {'value': 'ORCID'},
        'authorIdentifier': {'value': ''}, 'authorAffiliation': {'value': ''}}]}]}}}}, [
    {'authorName': {'value': 'Doe, John'}, 'authorIdentifierScheme': {'value': 'ORCID'},
      'authorIdentifier': {'value': '0000-0001'}, 'authorAffiliation': {'value': 'Org1'}}],
  "success-path-single-author"), ({'authors': [{'last': 'Smith', 'first': 'Jane', 'orcid': '0000-0002',
    'organizations': [{'organization': 'Org2'}, {'organization': 'Org3'}]}]}, {'datasetVersion': {'metadataBlocks': {
    'citation': {'fields': [{'typeName': 'author', 'value': [
      {'authorName': {'value': 'Last, First'}, 'authorIdentifierScheme': {'value': 'ORCID'},
        'authorIdentifier': {'value': ''}, 'authorAffiliation': {'value': ''}}]}]}}}}, [
                                    {'authorName': {'value': 'Smith, Jane'},
                                      'authorIdentifierScheme': {'value': 'ORCID'},
                                      'authorIdentifier': {'value': '0000-0002'},
                                      'authorAffiliation': {'value': 'Org2, Org3'}}],
                                  "success-path-single-author-multiple-orgs"), ({'authors': [
    {'last': 'Doe', 'first': 'John', 'orcid': '0000-0001', 'organizations': [{'organization': 'Org1'}]},
    {'last': 'Smith', 'first': 'Jane', 'orcid': '0000-0002', 'organizations': [{'organization': 'Org2'}]},
    {'last': 'Keith', 'first': 'Sean', 'orcid': '0000-0003',
     'organizations': [{'organization': 'Org3'}, {'organization': 'Org4'}]}]}, {'datasetVersion': {'metadataBlocks': {
    'citation': {'fields': [{'typeName': 'author', 'value': [
      {'authorName': {'value': 'Last, First'}, 'authorIdentifierScheme': {'value': 'ORCID'},
       'authorIdentifier': {'value': ''}, 'authorAffiliation': {'value': ''}}]}]}}}}, [
                                                                                  {'authorName': {'value': 'Doe, John'},
                                                                                   'authorIdentifierScheme': {
                                                                                     'value': 'ORCID'},
                                                                                   'authorIdentifier': {
                                                                                     'value': '0000-0001'},
                                                                                   'authorAffiliation': {
                                                                                     'value': 'Org1'}}, {
      'authorName': {'value': 'Smith, Jane'}, 'authorIdentifierScheme': {'value': 'ORCID'},
      'authorIdentifier': {'value': '0000-0002'}, 'authorAffiliation': {'value': 'Org2'}}, {
      'authorName': {'value': 'Keith, Sean'}, 'authorIdentifierScheme': {'value': 'ORCID'},
      'authorIdentifier': {'value': '0000-0003'}, 'authorAffiliation': {'value': 'Org3, Org4'}}],
                                                                                "success-path-multiple-authors"), ])
  def test_set_authors_success_path(self, mocker, config_data, metadata, expected_authors_list, test_id):
    # Arrange
    logger = mocker.MagicMock()
    mock_log_and_create_error = mocker.MagicMock()
    mock_read_pasta_config_file = mocker.patch('pasta_eln.dataverse.utils.read_pasta_config_file')
    mocker.patch('pasta_eln.dataverse.utils.log_and_create_error', return_value=mock_log_and_create_error)
    mock_read_pasta_config_file.return_value = config_data

    # Act
    set_authors(logger, metadata)

    # Assert
    author_field = next(
      f for f in metadata['datasetVersion']['metadataBlocks']['citation']['fields'] if f['typeName'] == 'author')
    authors_list = author_field['value']
    assert authors_list == expected_authors_list
    mock_log_and_create_error.assert_not_called()

  @pytest.mark.parametrize("config_data, metadata, expected_authors_list, test_id", [(
      {'authors': [{'last': '', 'first': '', 'orcid': '', 'organizations': [{'organization': ''}]}]}, {
        'datasetVersion': {'metadataBlocks': {'citation': {'fields': [{'typeName': 'author', 'value': [
          {'authorName': {'value': 'Last, First'}, 'authorIdentifierScheme': {'value': 'ORCID'},
           'authorIdentifier': {'value': ''}, 'authorAffiliation': {'value': ''}}]}]}}}}, [
        {'authorName': {'value': ''}, 'authorIdentifierScheme': {'value': 'ORCID'}, 'authorIdentifier': {'value': ''},
         'authorAffiliation': {'value': ''}}], "edge-case-path-empty-author")])
  def test_set_authors_edge_cases_path(self, mocker, config_data, metadata, expected_authors_list, test_id):
    # Arrange
    logger = mocker.MagicMock()
    mock_log_and_create_error = mocker.MagicMock()
    mock_read_pasta_config_file = mocker.patch('pasta_eln.dataverse.utils.read_pasta_config_file')
    mocker.patch('pasta_eln.dataverse.utils.log_and_create_error', return_value=mock_log_and_create_error)
    mock_read_pasta_config_file.return_value = config_data

    # Act
    set_authors(logger, metadata)

    # Assert
    author_field = next(
      f for f in metadata['datasetVersion']['metadataBlocks']['citation']['fields'] if f['typeName'] == 'author')
    authors_list = author_field['value']
    assert authors_list == expected_authors_list
    mock_log_and_create_error.assert_not_called()

  # Parametrized test for various error cases
  @pytest.mark.parametrize("config_data, metadata, exception, test_id", [  # Test ID: 1
    ({},  # No authors in config
     {'datasetVersion': {
       'metadataBlocks': {'citation': {'fields': [{'typeName': 'author', 'value': [{'authorName': {'value': ''}}]}]}}}},
     DatabaseError("Incorrect config file, authors not found!"), "error-no-authors-in-config"),  # Test ID: 2
    ({'authors': []},  # Empty authors list in config
     {'datasetVersion': {'metadataBlocks': {'citation': {'fields': [{'typeName': 'author', 'value': []}]}}}},
     DatabaseError("Incorrect config file, authors not found!"), "error-empty-authors-list"), ])
  def test_set_authors_error_cases(self, mocker, config_data, metadata, exception, test_id):
    # Arrange
    logger = mocker.MagicMock()
    mocker.patch('pasta_eln.dataverse.utils.read_pasta_config_file', return_value=config_data)
    mock_log_and_create_error = mocker.patch('pasta_eln.dataverse.utils.log_and_create_error', return_value=exception)

    # Act & Assert
    with pytest.raises(type(exception)):
      set_authors(logger, metadata)
    mock_log_and_create_error.assert_called_once()

  # Mocking the DataverseClient to avoid real HTTP requests during testing

  # Parametrized test cases
  @pytest.mark.parametrize(
    "api_token, server_url, server_reachable, server_message, token_valid, expected_result, test_id",
    [  # Success path tests
      ("valid_token", "https://valid.server", True, "Data server is reachable", True,
       (True, "Data server is reachable and token is valid"), "success_path_valid"),  # Edge cases
      ("", "https://valid.server", True, "Data server is reachable", False,
       (False, "Data server is reachable but token is invalid"), "edge_case_empty_token"),  # Error cases
      ("invalid_token", "https://valid.server", True, "Data server is reachable", False,
       (False, "Data server is reachable but token is invalid"), "error_case_invalid_token"), (
        "valid_token", "https://unauthorized.server", False, "Data server is not reachable, Unauthorized", False,
        (False, "Data server is reachable but API token is invalid"), "error_case_unauthorized"), (
        "valid_token", "https://unreachable.server", False, "Data server not reachable", False,
        (False, "Data server is not reachable"), "error_case_unreachable"), ])
  def test_check_login_credentials(self, mocker, api_token, server_url, server_reachable, server_message, token_valid,
                                   expected_result, test_id):
    # Arrange
    mocker.patch('pasta_eln.dataverse.client.DataverseClient.__init__', return_value=None)
    mocker.patch('pasta_eln.dataverse.client.DataverseClient.check_if_dataverse_server_reachable',
                 side_effect=mocker.AsyncMock(return_value=(server_reachable, server_message)))
    mocker.patch('pasta_eln.dataverse.client.DataverseClient.check_if_api_token_is_valid',
                 side_effect=mocker.AsyncMock(return_value=token_valid))
    mock_logger = mocker.MagicMock()

    # Act
    result = check_login_credentials(mock_logger, api_token, server_url)

    # Assert
    assert result == expected_result
    mock_logger.info.assert_called_with("Checking if login info is valid, server_url: %s", server_url)
    if not server_reachable or not token_valid:
      mock_logger.warning.assert_called()
    else:
      mock_logger.info.assert_called()

  @pytest.mark.parametrize("test_id, config, expected_key_exists, expected_key", [  # Success path tests
    ("success-existing-key", {'dataverseEncryptKey': EXISTING_KEY}, True, EXISTING_KEY),
    ("success-new-key", {}, False, NEW_KEY), ])
  def test_get_encrypt_key(self, mocker, test_id, config, expected_key_exists, expected_key):
    # Arrange
    logger = mocker.MagicMock(spec=logging.Logger)
    mock_read_config = mocker.patch('pasta_eln.dataverse.utils.read_pasta_config_file', return_value=config)
    mock_write_config = mocker.patch('pasta_eln.dataverse.utils.write_pasta_config_file')
    mocker.patch('cryptography.fernet.Fernet.generate_key', return_value=b64decode(expected_key))

    # Act
    key_exists, key = get_encrypt_key(logger)

    # Assert
    assert key_exists == expected_key_exists
    assert b64encode(key).decode('ascii') == expected_key
    if not expected_key_exists:
      mock_write_config.assert_called_once()
      logger.warning.assert_called_with("Dataverse encrypt key does not exist, hence generating a new key..")
    else:
      mock_write_config.assert_not_called()
    mock_read_config.assert_called_once_with(logger)
    logger.info.assert_called_with("Getting dataverse encrypt key..")

  # Parametrized test cases for happy path, edge cases, and error cases
  @pytest.mark.parametrize("test_id, config_data, file_exists, expected_call_count, expected_info_log",
                           [  # success path tests with various realistic test values
                             ("success-1", {"key": "value"}, True, 1, ["Writing config file: %s", str(CONFIG_PATH)]),
                             ("success-2", {"empty": {}}, True, 1, ["Writing config file: %s", str(CONFIG_PATH)]),
                             ("success-3", {"list": [1, 2, 3]}, True, 1, ["Writing config file: %s", str(CONFIG_PATH)]),

                             # Edge cases
                             ("edge-1", {}, True, 1, ["Writing config file: %s", str(CONFIG_PATH)]),  # Empty dict

                             # Error cases
                             ("error-1", {"key": "value"}, False, 0, None),  # Config file does not exist
                           ])
  def test_write_pasta_config_file(self, mocker, test_id, config_data, file_exists, expected_call_count,
                                   expected_info_log):
    # Arrange
    logger_mock = mocker.MagicMock(spec=logging.Logger)
    mocker.patch('pasta_eln.dataverse.utils.Path.home', return_value=HOME_DIR)
    mocker.patch('pasta_eln.dataverse.utils.join', return_value=CONFIG_PATH)
    mocker.patch('pasta_eln.dataverse.utils.exists', return_value=file_exists)
    mock_dump = mocker.patch('pasta_eln.dataverse.utils.dump')
    mock_open_call = mocker.patch('pasta_eln.dataverse.utils.open', mock_open())
    mock_error = mocker.patch('pasta_eln.dataverse.utils.log_and_create_error')
    if test_id == "error-1":
      mock_error.side_effect = DatabaseError("Config file not found, Corrupt installation!")

    # Act
    if file_exists:
      write_pasta_config_file(logger_mock, config_data)
    else:
      with pytest.raises(DatabaseError):
        write_pasta_config_file(logger_mock, config_data)

    # Assert
    if file_exists:
      logger_mock.info.assert_called_with(expected_info_log[0], expected_info_log[1])
      assert logger_mock.info.call_count == expected_call_count
      mock_open_call.assert_called_once_with(CONFIG_PATH, 'w', encoding='utf-8')
      mock_dump.assert_called_once_with(config_data, mock_open_call(), ensure_ascii=False, indent=4)
    else:
      mock_error.assert_called_with(logger_mock, DatabaseError, "Config file not found, Corrupt installation!")

  @pytest.mark.parametrize("test_id, encrypt_key, data, expected",
                           [  # success path tests with various realistic test values
                             ("success-ascii", VALID_KEY, "test_data", None),
                             # Expected to be replaced with actual encrypted data
                             ("success-numeric", VALID_KEY, "12345", None),
                             # Expected to be replaced with actual encrypted data
                             ("success-special-chars", VALID_KEY, "!@#$%^&*()", None),
                             # Expected to be replaced with actual encrypted data

                             # Edge cases
                             ("edge-empty-string", VALID_KEY, "", None),
                             # Expected to be replaced with actual encrypted data for empty string

                             # Error cases
                             ("error-none-key", None, "test_data", None), ("error-none-data", VALID_KEY, None, None),
                             ("error-none-both", None, None, None),
                             ("error-invalid-key", b"invalid_key", "test_data", Exception),
                             ("error-invalid-data", VALID_KEY, b"invalid_data", Exception), ])
  def test_encrypt_data(self, mocker, test_id, encrypt_key, data, expected):
    # Arrange
    logger = mocker.MagicMock(spec=logging.Logger)

    # If expected is None, it means we need to generate the expected value for happy path and edge cases
    if expected is None and encrypt_key is not None and data is not None:
      try:
        fernet = Fernet(encrypt_key)
        expected = fernet.encrypt(data.encode('ascii')).decode('ascii')
      except Exception:
        pass

    # Act
    result = encrypt_data(logger, encrypt_key, data)

    # Assert
    if encrypt_key is None or data is None:
      logger.warning.assert_called_once_with("encrypt_key/data cannot be None")
      assert result is None
    elif expected is Exception:
      assert result is None
      logger.warning.assert_called_once()
    else:
      fernet = Fernet(encrypt_key)
      assert fernet.decrypt(result.encode('ascii')).decode('ascii') == fernet.decrypt(expected.encode('ascii')).decode(
        'ascii')

  @pytest.mark.parametrize("test_id, encrypt_key, data, expected",
                           [  # Happy path tests with various realistic test values
                             ("happy-path-valid", VALID_KEY, Fernet(VALID_KEY).encrypt(b"valid_data").decode('ascii'),
                              "valid_data"),
                             ("happy-path-empty-string", VALID_KEY, Fernet(VALID_KEY).encrypt(b"").decode('ascii'), ""),

                             # Error cases
                             ("error-none-key", None, "data", None), ("error-none-data", VALID_KEY, None, None), (
                               "error-invalid-key", b"invalid_key", Fernet(VALID_KEY).encrypt(b"data").decode('ascii'),
                               Exception), ("error-invalid-data", VALID_KEY, "invalid_data", Exception), ])
  def test_decrypt_data(self, mocker, test_id, encrypt_key, data, expected):
    # Arrange
    logger = mocker.MagicMock(spec=logging.Logger)

    # Act
    if isinstance(expected, Exception):
      with expected:
        decrypt_data(logger, encrypt_key, data)
    else:
      result = decrypt_data(logger, encrypt_key, data)

    # Assert
    if expected is None:
      logger.warning.assert_called_with("encrypt_key/data cannot be None")
    elif expected is Exception:
      assert result is None
      logger.warning.assert_called_once()
    else:
      assert result == expected
