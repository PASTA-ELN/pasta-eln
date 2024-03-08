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
from typing import Type
from unittest.mock import mock_open

import pytest
from cryptography.fernet import Fernet

from pasta_eln.dataverse.config_error import ConfigError
from pasta_eln.dataverse.upload_status_values import UploadStatusValues
from pasta_eln.dataverse.utils import adjust_type_name, check_login_credentials, clear_value, decrypt_data, \
  delete_layout_and_contents, encrypt_data, \
  get_encrypt_key, \
  is_date_time_type, log_and_create_error, read_pasta_config_file, set_authors, set_template_values, update_status, \
  write_pasta_config_file

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
                            (UploadStatusValues.Warning.name, 'fa.warning', 'happy_path_warning'),
                            # Add edge cases here
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
                           [("ErrorCase-1", ConfigError, "Config file not found, Corrupt installation!"), ], )
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
  @pytest.mark.parametrize("config_data, metadata, expected_authors_list, test_id", [
    ({
       "authors": [
         {
           "last": "Doe",
           "first": "John",
           "orcid": "0000-0001",
           "organizations": [
             {
               "organization": "Org1"
             }
           ]
         }
       ]
     },
     {
       "datasetVersion": {
         "metadataBlocks": {
           "citation": {
             "fields": [
               {
                 "typeName": "author",
                 "valueTemplate": [
                   {
                     "authorName": {
                       "value": "Last, First"
                     },
                     "authorIdentifierScheme": {
                       "value": "ORCID"
                     },
                     "authorIdentifier": {
                       "value": ""
                     },
                     "authorAffiliation": {
                       "value": ""
                     }
                   }
                 ]
               }
             ]
           }
         }
       }
     },
     [
       {
         "authorName": {
           "value": "Doe, John"
         },
         "authorIdentifierScheme": {
           "value": "ORCID"
         },
         "authorIdentifier": {
           "value": "0000-0001"
         },
         "authorAffiliation": {
           "value": "Org1"
         }
       }
     ],
     "success-path-single-author"),
    ({
       "authors": [
         {
           "last": "Smith",
           "first": "Jane",
           "orcid": "0000-0002",
           "organizations": [
             {
               "organization": "Org2"
             },
             {
               "organization": "Org3"
             }
           ]
         }
       ]
     },
     {
       "datasetVersion": {
         "metadataBlocks": {
           "citation": {
             "fields": [
               {
                 "typeName": "author",
                 "valueTemplate": [
                   {
                     "authorName": {
                       "value": "Last, First"
                     },
                     "authorIdentifierScheme": {
                       "value": "ORCID"
                     },
                     "authorIdentifier": {
                       "value": ""
                     },
                     "authorAffiliation": {
                       "value": ""
                     }
                   }
                 ]
               }
             ]
           }
         }
       }
     },
     [
       {
         "authorName": {
           "value": "Smith, Jane"
         },
         "authorIdentifierScheme": {
           "value": "ORCID"
         },
         "authorIdentifier": {
           "value": "0000-0002"
         },
         "authorAffiliation": {
           "value": "Org2, Org3"
         }
       }
     ],
     "success-path-single-author-multiple-orgs"),
    ({
       "authors": [
         {
           "last": "Doe",
           "first": "John",
           "orcid": "0000-0001",
           "organizations": [
             {
               "organization": "Org1"
             }
           ]
         },
         {
           "last": "Smith",
           "first": "Jane",
           "orcid": "0000-0002",
           "organizations": [
             {
               "organization": "Org2"
             }
           ]
         },
         {
           "last": "Keith",
           "first": "Sean",
           "orcid": "0000-0003",
           "organizations": [
             {
               "organization": "Org3"
             },
             {
               "organization": "Org4"
             }
           ]
         }
       ]
     },
     {
       "datasetVersion": {
         "metadataBlocks": {
           "citation": {
             "fields": [
               {
                 "typeName": "author",
                 "valueTemplate": [
                   {
                     "authorName": {
                       "value": "Last, First"
                     },
                     "authorIdentifierScheme": {
                       "value": "ORCID"
                     },
                     "authorIdentifier": {
                       "value": ""
                     },
                     "authorAffiliation": {
                       "value": ""
                     }
                   }
                 ]
               }
             ]
           }
         }
       }
     },
     [
       {
         "authorName": {
           "value": "Doe, John"
         },
         "authorIdentifierScheme": {
           "value": "ORCID"
         },
         "authorIdentifier": {
           "value": "0000-0001"
         },
         "authorAffiliation": {
           "value": "Org1"
         }
       },
       {
         "authorName": {
           "value": "Smith, Jane"
         },
         "authorIdentifierScheme": {
           "value": "ORCID"
         },
         "authorIdentifier": {
           "value": "0000-0002"
         },
         "authorAffiliation": {
           "value": "Org2"
         }
       },
       {
         "authorName": {
           "value": "Keith, Sean"
         },
         "authorIdentifierScheme": {
           "value": "ORCID"
         },
         "authorIdentifier": {
           "value": "0000-0003"
         },
         "authorAffiliation": {
           "value": "Org3, Org4"
         }
       }
     ],
     "success-path-multiple-authors")
  ])
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
    authors_list = author_field['valueTemplate']
    assert authors_list == expected_authors_list
    mock_log_and_create_error.assert_not_called()

  @pytest.mark.parametrize("config_data, metadata, expected_authors_list, test_id", [
    ({
       "authors": [
         {
           "last": "",
           "first": "",
           "orcid": "",
           "organizations": [
             {
               "organization": ""
             }
           ]
         }
       ]
     },
     {
       "datasetVersion": {
         "metadataBlocks": {
           "citation": {
             "fields": [
               {
                 "typeName": "author",
                 "valueTemplate": [
                   {
                     "authorName": {
                       "value": "Last, First"
                     },
                     "authorIdentifierScheme": {
                       "value": "ORCID"
                     },
                     "authorIdentifier": {
                       "value": ""
                     },
                     "authorAffiliation": {
                       "value": ""
                     }
                   }
                 ]
               }
             ]
           }
         }
       }
     },
     [
       {
         "authorName": {
           "value": ""
         },
         "authorIdentifierScheme": {
           "value": "ORCID"
         },
         "authorIdentifier": {
           "value": ""
         },
         "authorAffiliation": {
           "value": ""
         }
       }
     ],
     "edge-case-path-empty-author")
  ])
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
    authors_list = author_field['valueTemplate']
    assert authors_list == expected_authors_list
    mock_log_and_create_error.assert_not_called()

  # Parametrized test for various error cases
  @pytest.mark.parametrize("config_data, metadata, exception, test_id", [
    ({},
     {'datasetVersion': {
       'metadataBlocks': {
         'citation': {'fields': [{'typeName': 'author', 'valueTemplate': [{'authorName': {'value': ''}}]}]}}}},
     ConfigError("Incorrect config file, authors not found!"), "error-no-authors-in-config"),
    (None,
     None,
     ConfigError("Incorrect config file, authors not found!"), "error-no-authors-in-config"),
    ({'authors': []},
     {'datasetVersion': {'metadataBlocks': {'citation': {'fields': [{'typeName': 'author', 'valueTemplate': []}]}}}},
     ConfigError("Incorrect config file, authors not found!"), "error-empty-authors-list"), ])
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
    ("success-new-key", {}, False, NEW_KEY)
  ])
  def test_get_encrypt_key(self, mocker, test_id, config, expected_key_exists, expected_key):
    # Arrange
    logger = mocker.MagicMock(spec=logging.Logger)
    mock_read_config = mocker.patch('pasta_eln.dataverse.utils.read_pasta_config_file', return_value=config)
    mock_write_config = mocker.patch('pasta_eln.dataverse.utils.write_pasta_config_file')
    mocker.patch('cryptography.fernet.Fernet.generate_key', return_value=b64decode(expected_key))

    # Act
    key_exists, key = get_encrypt_key(logger)

    # Assert
    logger.info.assert_called_with("Getting dataverse encrypt key..")
    assert key_exists == expected_key_exists
    assert b64encode(key).decode('ascii') == expected_key
    if not expected_key_exists:
      mock_write_config.assert_called_once()
      logger.warning.assert_called_with("Dataverse encrypt key does not exist, hence generating a new key..")
    else:
      mock_write_config.assert_not_called()
    mock_read_config.assert_called_once_with(logger)

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
      mock_error.side_effect = ConfigError("Config file not found, Corrupt installation!")

    # Act
    if file_exists:
      write_pasta_config_file(logger_mock, config_data)
    else:
      with pytest.raises(ConfigError):
        write_pasta_config_file(logger_mock, config_data)

    # Assert
    if file_exists:
      logger_mock.info.assert_called_with(expected_info_log[0], expected_info_log[1])
      assert logger_mock.info.call_count == expected_call_count
      mock_open_call.assert_called_once_with(CONFIG_PATH, 'w', encoding='utf-8')
      mock_dump.assert_called_once_with(config_data, mock_open_call(), ensure_ascii=False, indent=4)
    else:
      mock_error.assert_called_with(logger_mock, ConfigError, "Config file not found, Corrupt installation!")

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
      logger.error.assert_called_once()
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
                             ("error-none-key", None, "data", None), ("error-none-data", VALID_KEY, None, None),
                             ("error-invalid-key", b"invalid_key", Fernet(VALID_KEY).encrypt(b"data").decode('ascii'),
                              Exception),
                             ("error-invalid-data", VALID_KEY, "invalid_data", Exception),
                             ("error-invalid-data", VALID_KEY, "invalid_data", Exception),
                           ])
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
      logger.error.assert_called_once()
    else:
      assert result == expected

  @pytest.mark.parametrize("test_id, metadata, expected_warning, expected_result", [
    # Happy path with various realistic test values
    ("success_case_1", {
      "datasetVersion": {
        "metadataBlocks": {
          "citation": {
            "fields": [
              {
                "typeClass": "primitive",
                "value": "Some value",
                "multiple": False
              },
              {
                "typeClass": "primitive",
                "value": ["Some value 1", "Some value 2"],
                "multiple": True
              },
              {
                "typeClass": "compound",
                "value": [{"subfield": "Another value"}],
                "multiple": True
              },
              {
                "typeClass": "compound",
                "value": {"subfield": "Another value"},
                "multiple": False
              },
              {
                "typeClass": "controlledVocabulary",
                "value": ["Option1", "Option2"],
                "multiple": True
              },
              {
                "typeName": "journalArticleType",
                "multiple": False,
                "typeClass": "controlledVocabulary",
                "value": "abstract"
              }
            ]
          }
        }
      }
    }, None, {
       "datasetVersion": {
         "metadataBlocks": {
           "citation": {
             "fields": [
               {
                 "typeClass": "primitive",
                 "value": "",
                 "valueTemplate": "Some value",
                 "multiple": False
               },
               {
                 "typeClass": "primitive",
                 "value": [],
                 "valueTemplate": ["Some value 1", "Some value 2"],
                 "multiple": True
               },
               {
                 "typeClass": "compound",
                 "value": [],
                 "valueTemplate": [{"subfield": "Another value"}],
                 "multiple": True
               },
               {
                 "typeClass": "compound",
                 "value": {},
                 "valueTemplate": {"subfield": "Another value"},
                 "multiple": False
               },
               {
                 "typeClass": "controlledVocabulary",
                 "value": [],
                 "valueTemplate": ["Option1", "Option2"],
                 "multiple": True
               },
               {
                 "typeName": "journalArticleType",
                 "multiple": False,
                 "typeClass": "controlledVocabulary",
                 "valueTemplate": "abstract",
                 "value": ""
               }
             ]
           }
         }
       }
     }),
    # Edge case with empty metadata
    ("edge_case_empty_metadata", {}, "Empty metadata, make sure the metadata is loaded correctly...", {}),
    # Error case with invalid metadata structure
    ("error_case_invalid_metadata", {
      "datasetVersion": "Invalid structure"
    }, None, TypeError),
    ("error_case_invalid_metadata_with_unsupported_type", {
      "datasetVersion": {
        "metadataBlocks": {
          "citation": {
            "fields": [
              {
                "typeClass": "unsupported",
                "value": "Some value",
                "multiple": False
              },
              {
                "typeClass": "primitive",
                "value": ["Some value 1", "Some value 2"],
                "multiple": True
              }
            ]
          }
        }
      }
    }, "Unsupported type class: unsupported", {
       "datasetVersion": {
         "metadataBlocks": {
           "citation": {
             "fields": [
               {
                 "typeClass": "unsupported",
                 "value": "Some value",
                 "multiple": False
               },
               {
                 "typeClass": "primitive",
                 "value": [],
                 "valueTemplate": ["Some value 1", "Some value 2"],
                 "multiple": True
               }
             ]
           }
         }
       }
     }),
  ])
  def test_set_template_values(self, mocker, test_id, metadata, expected_warning, expected_result):
    logger = mocker.MagicMock(spec=logging.Logger)

    # Arrange
    # (Omitted if all input values are provided via test parameters)

    # Act
    if isinstance(expected_result, Type) and issubclass(expected_result, Exception):
      with pytest.raises(expected_result):
        set_template_values(logger, metadata)
    else:
      set_template_values(logger, metadata)

    # Assert
    if expected_warning:
      logger.warning.assert_called_with(expected_warning)
      assert metadata == expected_result, f"Test failed for {test_id}"
    if not (isinstance(expected_result, Type) and issubclass(expected_result, Exception)):
      assert metadata == expected_result, f"Test failed for {test_id}"

  # Success path tests with various realistic test values
  @pytest.mark.parametrize("input_string, expected_output", [
    # ID: Test single word starting with uppercase
    ("Camel", "Camel"),
    # ID: Test standard camel case
    ("CamelCaseSplit", "Camel Case Split"),
    # ID: Test consecutive uppercase letters
    ("HTTPRequest", "HTTP Request"),
    # ID: Test single uppercase letter
    ("A", "A"),
    # ID: Test camel case ending with uppercase letter
    ("CamelCaseX", "Camel Case X"),
    # ID: Test camel case with leading uppercase letters
    ("XMLHttpRequest", "XML Http Request"),
    ("alternativeTitle", "Alternative Title"),
  ], ids=[
    "single_word",
    "standard_camel_case",
    "consecutive_uppercase",
    "single_uppercase",
    "ending_with_uppercase",
    "leading_uppercase",
    "starting_lowercase",
  ])
  def test_adjust_type_name_success_path(self, input_string, expected_output):
    # Act
    result = adjust_type_name(input_string)

    # Assert
    assert result == expected_output, f"Expected {expected_output} but got {result}"

  # Edge cases
  @pytest.mark.parametrize("input_string, expected_output", [
    # ID: Test empty string
    ("", ""),
    # ID: Test string with only spaces
    ("   ", ""),
    # ID: Test string with special characters
    ("CamelCase#Split", "Camel Case Split"),
    # ID: Test string with underscores
    ("Camel_Case_Split", "Camel Case Split"),
  ], ids=[
    "empty_string",
    "only_spaces",
    "special_characters",
    "underscores",
  ])
  def test_adjust_type_name_edge_cases(self, input_string, expected_output):
    # Act
    result = adjust_type_name(input_string)

    # Assert
    assert result == expected_output, f"Expected {expected_output} but got {result}"

  # Error cases
  @pytest.mark.parametrize("input_string, expected_exception", [
    # ID: Test input is not a string (integer)
    (123, TypeError),
    # ID: Test input is not a string (list)
    (["CamelCaseSplit"], TypeError),
    # ID: Test input is not a string (None)
    (None, TypeError),
  ], ids=[
    "input_is_integer",
    "input_is_list",
    "input_is_none",
  ])
  def test_adjust_type_name_error_cases(self, input_string, expected_exception):
    # Act / Assert
    with pytest.raises(expected_exception):
      adjust_type_name(input_string)

  # Success path tests with various realistic test values
  @pytest.mark.parametrize("test_input, expected", [
    ({"a": {"value": 1}, "b": {"value": 2}}, {"a": {"value": None}, "b": {"value": None}}),
    ({"single": {"value": "test", "other": "data"}}, {"single": {"value": None, "other": "data"}}),
    ({"empty": {"value": ""}}, {"empty": {"value": None}}),
  ], ids=["SuccessCase-1", "SuccessCase-2", "SuccessCase-3"])
  def test_clear_value_happy_path(self, test_input, expected):
    # Act
    clear_value(test_input)

    # Assert
    assert test_input == expected, f"Expected {expected}, but got {test_input}"

  # Edge cases
  @pytest.mark.parametrize("test_input, expected", [
    # Test ID: EC-1
    ({}, {}),  # Empty dictionary
    # Test ID: EC-2
    ({"none_value": None}, {"none_value": None}),  # Value is already None
    ({"not_a_dict": [{"value": 1}]}, {"not_a_dict": [{"value": 1}]}),  # Value is already None
  ], ids=["EdgeCase-1", "EdgeCase-2", "EdgeCase-3"])
  def test_clear_value_edge_cases(self, test_input, expected):
    # Act
    clear_value(test_input)

    # Assert
    assert test_input == expected, f"Expected {expected}, but got {test_input}"

  # Test for None input
  def test_clear_value_with_none_input(self):
    # Act
    result = clear_value(None)

    # Assert
    assert result is None, "Expected None, but got a different result"

  # Parametrized test for success path with various realistic test values
  @pytest.mark.parametrize("type_name, expected_result", [
    # Test ID: #success_case_1 - type_name contains 'date' in lowercase
    ("date", True),
    # Test ID: #success_case_2 - type_name contains 'Date' in mixed case
    ("DateTime", True),
    # Test ID: #success_case_3 - type_name contains 'time' in lowercase
    ("timestamp", True),
    # Test ID: #success_case_4 - type_name contains 'Time' in mixed case
    ("modificationTime", True),
    # Test ID: #success_case_5 - type_name contains 'date' in the middle
    ("creation_date", True),
    # Test ID: #success_case_6 - type_name contains 'time' at the end
    ("update_time", True),
  ], ids=["success_case_1", "success_case_1", "success_case_2", "success_case_3", "success_case_4", "success_case_5"])
  def test_is_date_time_type_happy_path(self, type_name, expected_result):
    # Act
    result = is_date_time_type(type_name)

    # Assert
    assert result == expected_result, f"Failed for {type_name}"

  # Parametrized test for edge cases
  @pytest.mark.parametrize("type_name, expected_result", [
    # Test ID: #edge_case_1 - type_name is an empty string
    ("", False),
    # Test ID: #edge_case_2 - type_name does not contain 'date' or 'time'
    ("string", False),
    # Test ID: #edge_case_3 - type_name contains 'date' or 'time' as a separate word
    ("my date", True),
    # Test ID: #edge_case_4 - type_name contains 'date' or 'time' with special characters
    ("due-date", True),
    # Test ID: #edge_case_5 - type_name contains 'date' or 'time' with numbers
    ("date1", True),
  ], ids=["edge_case_1", "edge_case_2", "edge_case_3", "edge_case_4", "edge_case_5"])
  def test_is_date_time_type_edge_cases(self, type_name, expected_result):
    # Act
    result = is_date_time_type(type_name)

    # Assert
    assert result == expected_result, f"Failed for {type_name}"

  # Parametrized test for error cases
  @pytest.mark.parametrize("type_name, expected_exception", [
    # Test ID: #error_case_1 - type_name is None (should raise an AttributeError)
    (None, AttributeError),
    # Test ID: #error_case_2 - type_name is not a string (should raise an AttributeError)
    (123, AttributeError),
    # Test ID: #error_case_3 - type_name is a list (should raise an AttributeError)
    (["date"], AttributeError),
  ], ids=["error_case_1", "error_case_2", "error_case_3"])
  def test_is_date_time_type_error_cases(self, type_name, expected_exception):
    # Act and Assert
    with pytest.raises(expected_exception):
      _ = is_date_time_type(type_name)

  @pytest.mark.parametrize(
    "test_id, num_widgets",
    [
      ("success_path_1_widget", 1),  # ID: happy_path_1_widget
      ("success_path_multiple_widgets", 3),  # ID: happy_path_multiple_widgets
      ("success_path_no_widgets", 0),  # ID: happy_path_no_widgets
    ]
  )
  def test_delete_layout_and_contents(self, mocker, test_id, num_widgets):
    # Arrange
    layout = mocker.MagicMock()
    widgets = [mocker.MagicMock() for _ in range(num_widgets)]
    layout.itemAt = lambda pos: widgets[pos]
    layout.count.return_value = len(widgets)

    # Act
    delete_layout_and_contents(layout)

    # Assert
    layout.count.assert_called_once()
    layout.setParent.assert_called_once_with(None)
    for widget in widgets:
      widget.widget.return_value.setParent.assert_called_once_with(None)
