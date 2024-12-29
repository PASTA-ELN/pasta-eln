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
from os.path import dirname, join, realpath
from typing import Type
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest
from _pytest.mark import param
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import Executable

from pasta_eln.database.models.data_hierarchy_model import DataHierarchyModel
from pasta_eln.dataverse.config_error import ConfigError
from pasta_eln.dataverse.upload_status_values import UploadStatusValues
from pasta_eln.dataverse.utils import adjust_type_name, check_if_compound_field_value_is_missing, \
  check_if_dataverse_exists, check_if_field_value_is_missing, check_if_field_value_not_null, \
  check_if_minimal_metadata_exists, \
  check_login_credentials, \
  clear_value, decrypt_data, \
  encrypt_data, \
  generate_project_join_statement, get_citation_field, get_data_hierarchy_types, get_db_info, get_encrypt_key, \
  get_flattened_metadata, get_formatted_dataverse_url, get_formatted_message, get_formatted_metadata_message, \
  is_date_time_type, \
  log_and_create_error, \
  set_authors, \
  set_field_template_value, set_template_values, update_status, \
  write_pasta_config_file

# Constants for test
EXISTING_KEY = b64encode(Fernet.generate_key()).decode('ascii')
NEW_KEY = b64encode(Fernet.generate_key()).decode('ascii')
VALID_KEY = Fernet.generate_key()
HOME_DIR = '/home/user/'
CONFIG_FILE = '.pastaELN.json'
CONFIG_PATH = os.path.join(HOME_DIR, CONFIG_FILE)


def valid_metadata():
  return {
    'datasetVersion': {
      'metadataBlocks': {
        'citation': {
          'fields': [
            {'typeName': 'title', 'value': 'Sample Title'},
            {'typeName': 'author', 'value': [
              {
                'authorName': {
                  'typeName': 'authorName',
                  'multiple': False,
                  'typeClass': 'primitive',
                  'value': 'Author One'
                },
                'authorAffiliation': {
                  'typeName': 'authorAffiliation',
                  'multiple': False,
                  'typeClass': 'primitive',
                  'value': 'Affiliation One'
                },
                'authorIdentifierScheme': {
                  'typeName': 'authorIdentifierScheme',
                  'multiple': False,
                  'typeClass': 'controlledVocabulary',
                  'value': 'ORCID'
                },
                'authorIdentifier': {
                  'typeName': 'authorIdentifier',
                  'multiple': False,
                  'typeClass': 'primitive',
                  'value': '0000-0000-0000-0001'
                }
              },
              {
                'authorName': {
                  'typeName': 'authorName',
                  'multiple': False,
                  'typeClass': 'primitive',
                  'value': 'Author Two'
                },
                'authorAffiliation': {
                  'typeName': 'authorAffiliation',
                  'multiple': False,
                  'typeClass': 'primitive',
                  'value': 'Affiliation Two'
                },
                'authorIdentifierScheme': {
                  'typeName': 'authorIdentifierScheme',
                  'multiple': False,
                  'typeClass': 'controlledVocabulary',
                  'value': 'ORCID'
                },
                'authorIdentifier': {
                  'typeName': 'authorIdentifier',
                  'multiple': False,
                  'typeClass': 'primitive',
                  'value': '0000-0000-0000-0002'
                }
              }
            ]},
            {'typeName': 'datasetContact', 'value': [
              {
                'datasetContactName': {
                  'typeName': 'datasetContactName',
                  'multiple': False,
                  'typeClass': 'primitive',
                  'value': 'Contact One'
                },
                'datasetContactAffiliation': {
                  'typeName': 'datasetContactAffiliation',
                  'multiple': False,
                  'typeClass': 'primitive',
                  'value': 'Affiliation One'
                },
                'datasetContactEmail': {
                  'typeName': 'datasetContactEmail',
                  'multiple': False,
                  'typeClass': 'primitive',
                  'value': 'contact.one@example.com'
                }
              }
            ]},
            {'typeName': 'dsDescription', 'value': [
              {
                'dsDescriptionValue': {
                  'typeName': 'dsDescriptionValue',
                  'multiple': False,
                  'typeClass': 'primitive',
                  'value': 'Description One'
                },
                'dsDescriptionDate': {
                  'typeName': 'dsDescriptionDate',
                  'multiple': False,
                  'typeClass': 'primitive',
                  'value': '2021-01-01'
                }
              }
            ]},
            {'typeName': 'subject', 'value': 'Subject One'}
          ]
        }
      }
    }
  }


class TestDataverseUtils:

  # Assuming qtawesome.icon function is patched to return a simple mock object
  # that can produce a QPixmap when its pixmap method is called.
  @pytest.mark.parametrize('status, expected_icon_name, test_id', [
    (UploadStatusValues.Queued.name, 'fa.circle-o-notch', 'queued_status'),
    (UploadStatusValues.Uploading.name, 'fa.cloud-upload', 'uploading_status'),
    (UploadStatusValues.Cancelled.name, 'fa.minus-circle', 'cancelled_status'),
    (UploadStatusValues.Finished.name, 'fa.check-circle-o', 'finished_status'),
    (UploadStatusValues.Error.name, 'fa.times-circle-o', 'error_status'),
    (UploadStatusValues.Warning.name, 'fa.warning', 'warning_status'),
    ('UnknownStatus', 'fa.times-circle-o', 'default_case'),
  ])
  def test_update_status(self, mocker, status, expected_icon_name, test_id):
    # Arrange
    mock_icon = mocker.patch('pasta_eln.dataverse.utils.icon', return_value=mocker.MagicMock(pixmap=mocker.MagicMock()))
    mocker.patch('pasta_eln.dataverse.utils.QSize')
    status_label_set_text_callback = mocker.MagicMock()
    status_icon_set_pixmap_callback = mocker.MagicMock()

    # Act
    update_status(status, status_label_set_text_callback, status_icon_set_pixmap_callback)

    # Assert
    status_label_set_text_callback.assert_called_once_with(status)
    mock_icon.assert_called_once_with(expected_icon_name)
    status_icon_set_pixmap_callback.assert_called_once_with(mock_icon.return_value.pixmap.return_value)

  # Parametrized test for error scenarios

  # Parametrized test for happy path scenarios with various realistic test values
  @pytest.mark.parametrize('exception_type, error_message, test_id',
                           [(ValueError, 'Invalid value provided', 'happy_path_value_error'),
                            (TypeError, 'Type mismatch encountered', 'happy_path_type_error'),
                            (KeyError, 'Missing key in dictionary', 'happy_path_key_error'), ],
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
  @pytest.mark.parametrize('exception_type, error_message, test_id', [(Exception, '', 'edge_case_empty_message'), (
      RuntimeError, '  ', 'edge_case_whitespace_message'), (Exception, 'A' * 1000, 'edge_case_long_message'), ],
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
  @pytest.mark.parametrize('exception_type, error_message, test_id',
                           [(None, 'Exception type is None', 'error_case_none_exception_type'),
                            ('NotAType', 'Exception type is not a type', 'error_case_not_a_type_exception_type'), ],
                           ids=lambda test_id: test_id)
  def test_log_and_create_error_error_cases(self, mocker, exception_type, error_message, test_id):
    # Arrange
    mock_logger = mocker.MagicMock(spec=logging.Logger)

    # Act & Assert
    with pytest.raises(TypeError):
      log_and_create_error(mock_logger, exception_type, error_message)

  # Parametrized test for success path with various realistic test values
  @pytest.mark.parametrize('config_data, metadata, expected_authors_list, test_id', [
    ({
       'authors': [
         {
           'last': 'Doe',
           'first': 'John',
           'orcid': '0000-0001',
           'organizations': [
             {
               'organization': 'Org1'
             }
           ]
         }
       ]
     },
     {
       'datasetVersion': {
         'metadataBlocks': {
           'citation': {
             'fields': [
               {
                 'typeName': 'author',
                 'value': [],
                 'valueTemplate': [
                   {
                     'authorName': {
                       'value': 'Last, First'
                     },
                     'authorIdentifierScheme': {
                       'value': 'ORCID'
                     },
                     'authorIdentifier': {
                       'value': ''
                     },
                     'authorAffiliation': {
                       'value': ''
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
         'authorName': {
           'value': 'Doe, John'
         },
         'authorIdentifierScheme': {
           'value': 'ORCID'
         },
         'authorIdentifier': {
           'value': '0000-0001'
         },
         'authorAffiliation': {
           'value': 'Org1'
         }
       }
     ],
     'success-path-single-author'),
    ({
       'authors': [
         {
           'last': 'Smith',
           'first': 'Jane',
           'orcid': '0000-0002',
           'organizations': [
             {
               'organization': 'Org2'
             },
             {
               'organization': 'Org3'
             }
           ]
         }
       ]
     },
     {
       'datasetVersion': {
         'metadataBlocks': {
           'citation': {
             'fields': [
               {
                 'typeName': 'author',
                 'value': [],
                 'valueTemplate': [
                   {
                     'authorName': {
                       'value': 'Last, First'
                     },
                     'authorIdentifierScheme': {
                       'value': 'ORCID'
                     },
                     'authorIdentifier': {
                       'value': ''
                     },
                     'authorAffiliation': {
                       'value': ''
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
         'authorName': {
           'value': 'Smith, Jane'
         },
         'authorIdentifierScheme': {
           'value': 'ORCID'
         },
         'authorIdentifier': {
           'value': '0000-0002'
         },
         'authorAffiliation': {
           'value': 'Org2, Org3'
         }
       }
     ],
     'success-path-single-author-multiple-orgs'),
    ({
       'authors': [
         {
           'last': 'Doe',
           'first': 'John',
           'orcid': '0000-0001',
           'organizations': [
             {
               'organization': 'Org1'
             }
           ]
         },
         {
           'last': 'Smith',
           'first': 'Jane',
           'orcid': '0000-0002',
           'organizations': [
             {
               'organization': 'Org2'
             }
           ]
         },
         {
           'last': 'Keith',
           'first': 'Sean',
           'orcid': '0000-0003',
           'organizations': [
             {
               'organization': 'Org3'
             },
             {
               'organization': 'Org4'
             }
           ]
         }
       ]
     },
     {
       'datasetVersion': {
         'metadataBlocks': {
           'citation': {
             'fields': [
               {
                 'typeName': 'author',
                 'value': [],
                 'valueTemplate': [
                   {
                     'authorName': {
                       'value': 'Last, First'
                     },
                     'authorIdentifierScheme': {
                       'value': 'ORCID'
                     },
                     'authorIdentifier': {
                       'value': ''
                     },
                     'authorAffiliation': {
                       'value': ''
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
         'authorName': {
           'value': 'Doe, John'
         },
         'authorIdentifierScheme': {
           'value': 'ORCID'
         },
         'authorIdentifier': {
           'value': '0000-0001'
         },
         'authorAffiliation': {
           'value': 'Org1'
         }
       },
       {
         'authorName': {
           'value': 'Smith, Jane'
         },
         'authorIdentifierScheme': {
           'value': 'ORCID'
         },
         'authorIdentifier': {
           'value': '0000-0002'
         },
         'authorAffiliation': {
           'value': 'Org2'
         }
       },
       {
         'authorName': {
           'value': 'Keith, Sean'
         },
         'authorIdentifierScheme': {
           'value': 'ORCID'
         },
         'authorIdentifier': {
           'value': '0000-0003'
         },
         'authorAffiliation': {
           'value': 'Org3, Org4'
         }
       }
     ],
     'success-path-multiple-authors')
  ])
  def test_set_authors_success_path(self, mocker, config_data, metadata, expected_authors_list, test_id):
    # Arrange
    logger = mocker.MagicMock()
    mock_log_and_create_error = mocker.MagicMock()
    mock_get_instance = mocker.patch('pasta_eln.dataverse.utils.PastaConfigReaderFactory.get_instance')
    mocker.patch('pasta_eln.dataverse.utils.log_and_create_error', return_value=mock_log_and_create_error)
    mock_get_instance.return_value.config = config_data

    # Act
    set_authors(logger, metadata)

    # Assert
    author_field = next(
      f for f in metadata['datasetVersion']['metadataBlocks']['citation']['fields'] if f['typeName'] == 'author')
    authors_list = author_field['value']
    assert authors_list == expected_authors_list
    mock_log_and_create_error.assert_not_called()

  @pytest.mark.parametrize('config_data, metadata, expected_authors_list, test_id', [
    ({
       'authors': [
         {
           'last': '',
           'first': '',
           'orcid': '',
           'organizations': [
             {
               'organization': ''
             }
           ]
         }
       ]
     },
     {
       'datasetVersion': {
         'metadataBlocks': {
           'citation': {
             'fields': [
               {
                 'typeName': 'author',
                 'value': [],
                 'valueTemplate': [
                   {
                     'authorName': {
                       'value': 'Last, First'
                     },
                     'authorIdentifierScheme': {
                       'value': 'ORCID'
                     },
                     'authorIdentifier': {
                       'value': ''
                     },
                     'authorAffiliation': {
                       'value': ''
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
         'authorName': {
           'value': ''
         },
         'authorIdentifierScheme': {
           'value': 'ORCID'
         },
         'authorIdentifier': {
           'value': ''
         },
         'authorAffiliation': {
           'value': ''
         }
       }
     ],
     'edge-case-path-empty-author')
  ])
  def test_set_authors_edge_cases_path(self, mocker, config_data, metadata, expected_authors_list, test_id):
    # Arrange
    logger = mocker.MagicMock()
    mock_log_and_create_error = mocker.MagicMock()
    mock_get_instance = mocker.patch('pasta_eln.dataverse.utils.PastaConfigReaderFactory.get_instance')
    mocker.patch('pasta_eln.dataverse.utils.log_and_create_error', return_value=mock_log_and_create_error)
    mock_get_instance.return_value.config = config_data

    # Act
    set_authors(logger, metadata)

    # Assert
    author_field = next(
      f for f in metadata['datasetVersion']['metadataBlocks']['citation']['fields'] if f['typeName'] == 'author')
    authors_list = author_field['value']
    assert authors_list == expected_authors_list
    mock_log_and_create_error.assert_not_called()

  # Parametrized test for various error cases
  @pytest.mark.parametrize('config_data, metadata, exception, test_id', [
    ({},
     {'datasetVersion': {
       'metadataBlocks': {
         'citation': {'fields': [{'typeName': 'author', 'valueTemplate': [{'authorName': {'value': ''}}]}]}}}},
     ConfigError('Incorrect config file, authors not found!'), 'error-no-authors-in-config'),
    (None,
     None,
     ConfigError('Incorrect config file, authors not found!'), 'error-no-authors-in-config'),
    ({'authors': []},
     {'datasetVersion': {'metadataBlocks': {'citation': {'fields': [{'typeName': 'author', 'valueTemplate': []}]}}}},
     ConfigError('Incorrect config file, authors not found!'), 'error-empty-authors-list'), ])
  def test_set_authors_error_cases(self, mocker, config_data, metadata, exception, test_id):
    # Arrange
    logger = mocker.MagicMock()
    mock_get_instance = mocker.patch('pasta_eln.dataverse.utils.PastaConfigReaderFactory.get_instance')
    mock_get_instance.return_value.config = config_data
    mock_log_and_create_error = mocker.patch('pasta_eln.dataverse.utils.log_and_create_error', return_value=exception)

    # Act & Assert
    with pytest.raises(type(exception)):
      set_authors(logger, metadata)
    mock_log_and_create_error.assert_called_once()

  # Mocking the DataverseClient to avoid real HTTP requests during testing

  # Parametrized test cases
  @pytest.mark.parametrize(
    'api_token, server_url, server_reachable, server_message, token_valid, expected_result, test_id',
    [  # Success path tests
      ('valid_token', 'https://valid.server', True, 'Data server is reachable', True,
       (True, 'Data server is reachable and token is valid'), 'success_path_valid'),  # Edge cases
      ('', 'https://valid.server', True, 'Data server is reachable', False,
       (False, 'Data server is reachable but token is invalid'), 'edge_case_empty_token'),  # Error cases
      ('invalid_token', 'https://valid.server', True, 'Data server is reachable', False,
       (False, 'Data server is reachable but token is invalid'), 'error_case_invalid_token'), (
        'valid_token', 'https://unauthorized.server', False, 'Data server is not reachable, Unauthorized', False,
        (False, 'Data server is reachable but API token is invalid'), 'error_case_unauthorized'), (
        'valid_token', 'https://unreachable.server', False, 'Data server not reachable', False,
        (False, 'Data server is not reachable'), 'error_case_unreachable'), ])
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
    mock_logger.info.assert_called_with('Checking if login info is valid, server_url: %s', server_url)
    if not server_reachable or not token_valid:
      mock_logger.warning.assert_called()
    else:
      mock_logger.info.assert_called()

  @pytest.mark.parametrize('test_id, config, expected_key_exists, expected_key', [  # Success path tests
    ('success-existing-key', {'dataverseEncryptKey': EXISTING_KEY}, True, EXISTING_KEY),
    ('success-new-key', {}, False, NEW_KEY)
  ])
  def test_get_encrypt_key(self, mocker, test_id, config, expected_key_exists, expected_key):
    # Arrange
    logger = mocker.MagicMock(spec=logging.Logger)
    mock_get_instance = mocker.patch('pasta_eln.dataverse.utils.PastaConfigReaderFactory.get_instance')
    mock_get_instance.return_value.config = config
    mock_write_config = mocker.patch('pasta_eln.dataverse.utils.write_pasta_config_file')
    mocker.patch('cryptography.fernet.Fernet.generate_key', return_value=b64decode(expected_key))

    # Act
    key_exists, key = get_encrypt_key(logger)

    # Assert
    logger.info.assert_called_with('Getting dataverse encrypt key..')
    assert key_exists == expected_key_exists
    assert b64encode(key).decode('ascii') == expected_key
    if not expected_key_exists:
      mock_write_config.assert_called_once()
      logger.warning.assert_called_with('Dataverse encrypt key does not exist, hence generating a new key..')
    else:
      mock_write_config.assert_not_called()
    mock_get_instance.assert_called_once()

  @pytest.mark.parametrize('test_id, config_data, file_exists, expected_call_count, expected_info_log',
                           [  # success path tests with various realistic test values
                             ('success-1', {'key': 'value'}, True, 1, ['Writing config file: %s', str(CONFIG_PATH)]),
                             ('success-2', {'empty': {}}, True, 1, ['Writing config file: %s', str(CONFIG_PATH)]),
                             ('success-3', {'list': [1, 2, 3]}, True, 1, ['Writing config file: %s', str(CONFIG_PATH)]),

                             # Edge cases
                             ('edge-1', {}, True, 1, ['Writing config file: %s', str(CONFIG_PATH)]),  # Empty dict

                             # Error cases
                             ('error-1', {'key': 'value'}, False, 0, None),  # Config file does not exist
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
    if test_id == 'error-1':
      mock_error.side_effect = ConfigError('Config file not found, Corrupt installation!')

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
      mock_error.assert_called_with(logger_mock, ConfigError, 'Config file not found, Corrupt installation!')

  @pytest.mark.parametrize('test_id, encrypt_key, data, expected',
                           [  # success path tests with various realistic test values
                             ('success-ascii', VALID_KEY, 'test_data', None),
                             # Expected to be replaced with actual encrypted data
                             ('success-numeric', VALID_KEY, '12345', None),
                             # Expected to be replaced with actual encrypted data
                             ('success-special-chars', VALID_KEY, '!@#$%^&*()', None),
                             # Expected to be replaced with actual encrypted data

                             # Edge cases
                             ('edge-empty-string', VALID_KEY, '', None),
                             # Expected to be replaced with actual encrypted data for empty string

                             # Error cases
                             ('error-none-key', None, 'test_data', None), ('error-none-data', VALID_KEY, None, None),
                             ('error-none-both', None, None, None),
                             ('error-invalid-key', b'invalid_key', 'test_data', Exception),
                             ('error-invalid-data', VALID_KEY, b'invalid_data', Exception), ])
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
      logger.warning.assert_called_once_with('encrypt_key/data cannot be None')
      assert result is None
    elif expected is Exception:
      assert result is None
      logger.error.assert_called_once()
    else:
      fernet = Fernet(encrypt_key)
      assert fernet.decrypt(result.encode('ascii')).decode('ascii') == fernet.decrypt(expected.encode('ascii')).decode(
        'ascii')

  @pytest.mark.parametrize('encrypt_key, data, expected', [
    # Happy path tests
    pytest.param(VALID_KEY, 'test_data', 'encrypted', id='success_path_valid_data'),
    pytest.param(VALID_KEY, '123456', 'encrypted', id='success_path_numeric_data'),
    pytest.param(VALID_KEY, '!@#$%^&*()', 'encrypted', id='success_path_special_char_data'),

    # Edge cases
    pytest.param(VALID_KEY, '',
                 'gAAAAABmJlW4UG-J2AIlziPekpaZENRwA7QKFEU2GU5RMZx5vk5Vp1JCd8fqnBBwv5EgPMCR31nIXeKu1PHuuOqU5DTKplW6Lw==',
                 id='edge_case_empty_string'),
    pytest.param(VALID_KEY, ' ' * 5, 'encrypted', id='edge_case_spaces'),

    # Error cases
    pytest.param(None, 'test_data', None, id='error_case_no_key'),
    pytest.param(VALID_KEY, None, None, id='error_case_no_data'),
    pytest.param(b'invalid_key', 'test_data', None, id='error_case_invalid_key'),
  ])
  def test_encrypt_data_2(self, mocker, encrypt_key, data, expected):
    logger = mocker.MagicMock()

    # Act
    result = encrypt_data(logger, encrypt_key, data)

    # Assert
    if expected is None:
      assert result is None, f"Expected None, got {result}"
    else:
      assert result is not None and result != data, 'Expected encrypted data, got original or None'

    if encrypt_key is None or data is None:
      logger.warning.assert_called_with('encrypt_key/data cannot be None')
    elif encrypt_key == b'invalid_key':
      logger.error.assert_called_once_with('Value error: %s', mocker.ANY)
    else:
      assert not logger.error.called, 'Expected no error logs'

  def test_encrypt_data_throws_error(self, mocker):
    # Arrange
    error = InvalidToken('InvalidToken Error')
    mock_fernet = mocker.patch('pasta_eln.dataverse.utils.Fernet')
    mock_fernet.return_value.encrypt.side_effect = error
    logger = mocker.MagicMock(spec=logging.Logger)

    # Act
    result = encrypt_data(logger, VALID_KEY, 'data')

    # Assert
    assert result is None, f"Expected None, got {result}"
    logger.error.assert_called_once_with('Invalid token: %s', error)
    mock_fernet.assert_called_once_with(VALID_KEY)
    mock_fernet.return_value.encrypt.assert_called_once_with(b'data')

  @pytest.mark.parametrize('test_id, encrypt_key, data, expected',
                           [  # Happy path tests with various realistic test values
                             ('happy-path-valid', VALID_KEY, Fernet(VALID_KEY).encrypt(b'valid_data').decode('ascii'),
                              'valid_data'),
                             ('happy-path-empty-string', VALID_KEY, Fernet(VALID_KEY).encrypt(b'').decode('ascii'), ''),

                             # Error cases
                             ('error-none-key', None, 'data', None), ('error-none-data', VALID_KEY, None, None),
                             ('error-invalid-key', b'invalid_key', Fernet(VALID_KEY).encrypt(b'data').decode('ascii'),
                              Exception),
                             ('error-invalid-data', VALID_KEY, 'invalid_data', Exception),
                             ('error-invalid-data', VALID_KEY, 'invalid_data', Exception),
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
      logger.warning.assert_called_with('encrypt_key/data cannot be None')
    elif expected is Exception:
      assert result is None
      logger.error.assert_called_once()
    else:
      assert result == expected

  def test_decrypt_data_throws_error(self, mocker):
    # Arrange
    error = AttributeError('Wrong Attribute Error')
    mock_fernet = mocker.patch('pasta_eln.dataverse.utils.Fernet')
    mock_fernet.return_value.decrypt.side_effect = error
    logger = mocker.MagicMock(spec=logging.Logger)

    # Act
    result = decrypt_data(logger, VALID_KEY, 'data')

    # Assert
    assert result is None, f"Expected None, got {result}"
    logger.error.assert_called_once_with('AttributeError: %s', error)
    mock_fernet.assert_called_once_with(VALID_KEY)
    mock_fernet.return_value.decrypt.assert_called_once_with(b'data')

  @pytest.mark.parametrize('test_id, metadata, expected_warning, expected_result', [
    # Happy path with various realistic test values
    ('success_case_1', {
      'datasetVersion': {
        'metadataBlocks': {
          'citation': {
            'fields': [
              {
                'typeClass': 'primitive',
                'value': 'Some value',
                'multiple': False
              },
              {
                'typeClass': 'primitive',
                'value': ['Some value 1', 'Some value 2'],
                'multiple': True
              },
              {
                'typeClass': 'compound',
                'value': [{'subfield': 'Another value'}],
                'multiple': True
              },
              {
                'typeClass': 'compound',
                'value': {'subfield': 'Another value'},
                'multiple': False
              },
              {
                'typeClass': 'controlledVocabulary',
                'value': ['Option1', 'Option2'],
                'multiple': True
              },
              {
                'typeName': 'journalArticleType',
                'multiple': False,
                'typeClass': 'controlledVocabulary',
                'value': 'abstract'
              }
            ]
          }
        }
      }
    }, None, {
       'datasetVersion': {
         'metadataBlocks': {
           'citation': {
             'fields': [
               {
                 'typeClass': 'primitive',
                 'value': '',
                 'valueTemplate': 'Some value',
                 'multiple': False
               },
               {
                 'typeClass': 'primitive',
                 'value': [],
                 'valueTemplate': ['Some value 1', 'Some value 2'],
                 'multiple': True
               },
               {
                 'typeClass': 'compound',
                 'value': [],
                 'valueTemplate': [{'subfield': 'Another value'}],
                 'multiple': True
               },
               {
                 'typeClass': 'compound',
                 'value': {},
                 'valueTemplate': {'subfield': 'Another value'},
                 'multiple': False
               },
               {
                 'typeClass': 'controlledVocabulary',
                 'value': [],
                 'valueTemplate': ['No Value', 'Option1', 'Option2'],
                 'multiple': True
               },
               {
                 'typeName': 'journalArticleType',
                 'multiple': False,
                 'typeClass': 'controlledVocabulary',
                 'valueTemplate': 'abstract',
                 'value': ''
               }
             ]
           }
         }
       }
     }),
    # Edge case with empty metadata
    ('edge_case_empty_metadata', {}, 'Empty metadata, make sure the metadata is loaded correctly...', {}),
    # Error case with invalid metadata structure
    ('error_case_invalid_metadata', {
      'datasetVersion': 'Invalid structure'
    }, None, TypeError),
    ('error_case_invalid_metadata_with_unsupported_type', {
      'datasetVersion': {
        'metadataBlocks': {
          'citation': {
            'fields': [
              {
                'typeClass': 'unsupported',
                'value': 'Some value',
                'multiple': False
              },
              {
                'typeClass': 'primitive',
                'value': ['Some value 1', 'Some value 2'],
                'multiple': True
              }
            ]
          }
        }
      }
    }, 'Unsupported type class: unsupported', {
       'datasetVersion': {
         'metadataBlocks': {
           'citation': {
             'fields': [
               {
                 'typeClass': 'unsupported',
                 'value': 'Some value',
                 'multiple': False
               },
               {
                 'typeClass': 'primitive',
                 'value': [],
                 'valueTemplate': ['Some value 1', 'Some value 2'],
                 'multiple': True
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

  @pytest.mark.parametrize(
    'field, expected',
    [
      # Happy path tests
      pytest.param(
        {'typeClass': 'primitive', 'multiple': False, 'value': 'Example'},
        {'typeClass': 'primitive', 'multiple': False, 'value': '', 'valueTemplate': 'Example'},
        id='single_primitive'
      ),
      pytest.param(
        {'typeClass': 'primitive', 'multiple': True, 'value': ['Example1', 'Example2']},
        {'typeClass': 'primitive', 'multiple': True, 'value': [], 'valueTemplate': ['Example1', 'Example2']},
        id='multiple_primitive'
      ),
      pytest.param(
        {'typeClass': 'complex', 'multiple': False, 'value': {'key': 'value'}},
        {'typeClass': 'complex', 'multiple': False, 'value': '', 'valueTemplate': {'key': 'value'}},
        id='single_complex'
      ),
      pytest.param(
        {'typeClass': 'complex', 'multiple': True, 'value': [{'key1': 'value1'}, {'key2': 'value2'}]},
        {'typeClass': 'complex', 'multiple': True, 'value': [],
         'valueTemplate': [{'key1': 'value1'}, {'key2': 'value2'}]},
        id='multiple_complex'
      ),
      # Edge cases
      pytest.param(
        {'typeClass': 'primitive', 'multiple': False, 'value': ''},
        {'typeClass': 'primitive', 'multiple': False, 'value': '', 'valueTemplate': ''},
        id='single_empty_string'
      ),
      pytest.param(
        {'typeClass': 'primitive', 'multiple': True, 'value': []},
        {'typeClass': 'primitive', 'multiple': True, 'value': [], 'valueTemplate': []},
        id='multiple_empty_list'
      ),
      pytest.param(
        {'typeClass': 'complex', 'multiple': False, 'value': {}},
        {'typeClass': 'complex', 'multiple': False, 'value': '', 'valueTemplate': {}},
        id='single_empty_dict'
      ),
      pytest.param(
        {'typeClass': 'complex', 'multiple': True, 'value': [{}]},
        {'typeClass': 'complex', 'multiple': True, 'value': [], 'valueTemplate': [{}]},
        id='multiple_empty_dict_list'
      ),
      # Error cases
      pytest.param(
        {'typeClass': 'primitive', 'multiple': False},
        {'typeClass': 'primitive', 'multiple': False, 'valueTemplate': None},
        id='missing_value_key',
        marks=pytest.mark.xfail(raises=KeyError)
      ),
      pytest.param(
        {'typeClass': 'primitive', 'multiple': True, 'value': None},
        {'typeClass': 'primitive', 'multiple': True, 'value': [], 'valueTemplate': []},
        id='value_none',
        marks=pytest.mark.xfail(raises=AttributeError)
      ),
    ]
  )
  def test_set_field_template_value(self, field, expected):
    # Act
    set_field_template_value(field)

    # Assert
    assert field == expected

  @pytest.mark.parametrize(
    'field, missing_information, missing_field_name, check, expected',
    [
      (
          {'value': 'some data'},
          {'field_name': []},
          'field_name',
          True,
          {'field_name': []}
      ),
      (
          {'value': 123},
          {'numeric_field': []},
          'numeric_field',
          True,
          {'numeric_field': []}
      ),
      (
          {'value': [1, 2, 3]},
          {'list_field': []},
          'list_field',
          True,
          {'list_field': []}
      ),
    ], ids=['SuccessCase-1', 'SuccessCase-2', 'SuccessCase-3']
  )
  def test_check_if_field_value_not_null_success_path(self, field, missing_information, missing_field_name, check,
                                                      expected):
    # Act
    check_if_field_value_not_null(field, missing_information, missing_field_name, check)

    # Assert
    assert missing_information == expected

  # Edge cases
  @pytest.mark.parametrize(
    'field, missing_information, missing_field_name, check, expected',
    [
      # Test ID: EC-1
      (
          {'value': ''},
          {'empty_string': []},
          'empty_string',
          True,
          {'empty_string': ['Add at-least a single entry for Empty_string!']}
      ),
      # Test ID: EC-2
      (
          {'value': None},
          {'none_field': []},
          'none_field',
          True,
          {'none_field': ['Add at-least a single entry for None_field!']}
      ),
      # Test ID: EC-3
      (
          {'value': 'data'},
          {'no_check': []},
          'no_check',
          False,
          {'no_check': []}
      ),
    ], ids=['EdgeCase-1', 'EdgeCase-2', 'EdgeCase-3']
  )
  def test_check_if_field_value_not_null_edge_cases(self, field, missing_information, missing_field_name, check,
                                                    expected):
    # Act
    check_if_field_value_not_null(field, missing_information, missing_field_name, check)

    # Assert
    assert missing_information == expected

  # Error cases
  @pytest.mark.parametrize(
    'field, missing_information, missing_field_name, check, expected_exception',
    [
      (
          {'no_value': 'data'},
          {},
          'nonexistent_field',
          True,
          KeyError
      ),
      (
          {'value': None},
          {'field_name': 'not a list'},
          'field_name',
          True,
          AttributeError
      ),
    ], ids=['ErrorCase-1', 'ErrorCase-2']
  )
  def test_check_if_field_value_not_null_error_cases(self, field, missing_information, missing_field_name, check,
                                                     expected_exception):
    # Act & Assert
    with pytest.raises(expected_exception):
      check_if_field_value_not_null(field, missing_information, missing_field_name, check)

  @pytest.mark.parametrize(
    'field, field_key, field_name, missing_field_name, missing_information, expected',
    [
      (
          {'sample': {'value': 'data'}},  # field
          'sample',  # field_key
          'sample',  # field_name
          'Sample',  # missing_field_name
          {'sample': []},  # missing_information
          {'sample': []},  # expected
      ),
      (
          {'experiment': {'value': 'result'}},  # field
          'experiment',  # field_key
          'experiment',  # field_name
          'Experiment',  # missing_field_name
          {'experiment': []},  # missing_information
          {'experiment': []},  # expected
      ),
    ],
    ids=['SuccessCase-1', 'SuccessCase-2']
  )
  def test_check_if_field_value_is_missing_success_path(self, field, field_key, field_name, missing_field_name,
                                                        missing_information, expected):
    # Act
    check_if_field_value_is_missing(field, field_key, field_name, missing_field_name, missing_information)

    # Assert
    assert missing_information == expected

  # Parametrized test for edge cases
  @pytest.mark.parametrize(
    'field, field_key, field_name, missing_field_name, missing_information, expected',
    [
      # Test ID: EC-1
      (
          {'sample': {'value': ''}},  # field with empty string value
          'sample',  # field_key
          'sample',  # field_name
          'Sample',  # missing_field_name
          {'sample': []},  # missing_information
          {'sample': ['Sample field is missing for one of the samples!']},  # expected
      ),
      # Test ID: EC-2
      (
          {'experiment': {'value': None}},  # field with None value
          'experiment',  # field_key
          'experiment',  # field_name
          'Experiment',  # missing_field_name
          {'experiment': []},  # missing_information
          {'experiment': ['Experiment field is missing for one of the experiments!']},  # expected
      ),
    ],
    ids=['EdgeCase-1', 'EdgeCase-2']
  )
  def test_check_if_field_value_is_missing_edge_cases(self, field, field_key, field_name, missing_field_name,
                                                      missing_information, expected):
    # Act
    check_if_field_value_is_missing(field, field_key, field_name, missing_field_name, missing_information)

    # Assert
    assert missing_information == expected

  # Parametrized test for error cases
  @pytest.mark.parametrize(
    'field, field_key, field_name, missing_field_name, missing_information, expected',
    [
      # Test ID: ER-1
      (
          {},  # field without the key
          'sample',  # field_key
          'sample',  # field_name
          'Sample',  # missing_field_name
          {'sample': []},  # missing_information,
          {'sample': ['Sample field is missing for one of the samples!']}
      ),
      # Test ID: ER-2
      (
          {'sample': {}},  # field without 'value' key
          'sample',  # field_key
          'sample',  # field_name
          'Sample',  # missing_field_name
          {'sample': []},  # missing_information
          {'sample': ['Sample field is missing for one of the samples!']}
      )  # ),
    ],
    ids=['ErrorCase-1', 'ErrorCase-2']
  )
  def test_check_if_field_value_is_missing_error_cases(self, field, field_key, field_name, missing_field_name,
                                                       missing_information, expected):
    # Act & Assert
    check_if_field_value_is_missing(field, field_key, field_name, missing_field_name, missing_information)

    assert missing_information == expected, 'Expected missing information dictionary not equal to actual!'

  # Parametrized test cases
  @pytest.mark.parametrize(
    'test_id, field, field_key, missing_information, sub_fields, expected, expected_mock_call_1, expected_mock_call_2',
    [
      # Success path tests with various realistic test values
      ('success_case', {'value': [{'subfield1': 'data1', 'subfield2': 'data2'}]}, 'field_key', {},
       [('subfield1', 'missing_subfield1'), ('subfield2', 'missing_subfield2')], None,
       ({'value': [{'subfield1': 'data1', 'subfield2': 'data2'}]}, {}, 'field_key'),
       ({'subfield1': 'data1', 'subfield2': 'data2'},
        'field_key',
        'subfield2',
        'missing_subfield2',
        {})),

      # Edge case where 'value' is an empty list
      (
          'edge_empty_field_value', {'value': []}, 'field_key', {}, [('subfield1', 'missing_subfield1')], None, None,
          None),

      # Error case where a sub_field is missing in the field_value
      ('error_missing_sub_field', {'value': [{'subfield1': 'data1'}]}, 'field_key', {},
       [('subfield1', 'missing_subfield1'), ('subfield2', 'missing_subfield2')], KeyError,
       ({'value': [{'subfield1': 'data1'}]}, {}, 'field_key'), None),
    ])
  def test_check_if_compound_field_value_is_missing(self, mocker, test_id, field, field_key, missing_information,
                                                    sub_fields,
                                                    expected,
                                                    expected_mock_call_1,
                                                    expected_mock_call_2):
    # Arrange
    check_if_field_value_not_null_mock = mocker.patch('pasta_eln.dataverse.utils.check_if_field_value_not_null')
    check_if_field_value_is_missing_mock = mocker.patch('pasta_eln.dataverse.utils.check_if_field_value_is_missing')
    if expected:
      check_if_field_value_is_missing_mock.side_effect = expected

    # Act
    if expected is None:
      check_if_compound_field_value_is_missing(field, field_key, missing_information, sub_fields)
    else:
      with pytest.raises(expected):
        check_if_compound_field_value_is_missing(field, field_key, missing_information, sub_fields)

    # Assert
    if expected_mock_call_1:
      check_if_field_value_not_null_mock.assert_called_once_with(*expected_mock_call_1)
    if expected_mock_call_2:
      check_if_field_value_is_missing_mock.assert_called_with(*expected_mock_call_2)

  @pytest.mark.parametrize('metadata, check_title, expected_warnings, expected_result', [
    # ID: Success-Path-Complete-Metadata
    (valid_metadata(), True, [], {
      'title': [],
      'author': [],
      'datasetContact': [],
      'dsDescription': [],
      'subject': []
    }),
    # ID: Success-Path-Ignore-Title
    (valid_metadata(), False, [], {
      'title': [],
      'author': [],
      'datasetContact': [],
      'dsDescription': [],
      'subject': []
    }),
    # ID: Success-Path-Minimal-Metadata1
    ({'datasetVersion': {'metadataBlocks': {'citation': {'fields': [
      {'typeName': 'title', 'value': 'Sample Title'},
      {'typeName': 'author', 'value': [{'authorName': {
        'typeName': 'authorName',
        'multiple': False,
        'typeClass': 'primitive',
        'value': 'Author One'
      }}]},
      {'typeName': 'datasetContact', 'value': [{'datasetContactName': {
        'typeName': 'datasetContactName',
        'multiple': False,
        'typeClass': 'primitive',
        'value': 'Contact One'
      }}]},
      {'typeName': 'dsDescription', 'value': [{'dsDescriptionValue': {
        'typeName': 'dsDescriptionValue',
        'multiple': False,
        'typeClass': 'primitive',
        'value': 'Description One'
      }}]},
      {'typeName': 'subject', 'value': 'Subject One'}
    ]}}}}, True, [], {'author': ['Author Affiliation field is missing for one of the authors!',
                                 'Author Identifier Scheme field is missing for one of the authors!',
                                 'Author Identifier field is missing for one of the authors!'],
                      'datasetContact': ['Dataset Contact Affiliation field is missing for one of '
                                         'the datasetContacts!',
                                         'Dataset Contact Email field is missing for one of the '
                                         'datasetContacts!'],
                      'dsDescription': ['Dataset Description Date field is missing for one of the '
                                        'dsDescriptions!'],
                      'subject': [],
                      'title': []}),
    # ID: Success-Path-Minimal-Metadata2
    ({'datasetVersion': {'metadataBlocks': {'citation': {'fields': [
      {'typeName': 'title', 'value': 'Sample Title'},
      {'typeName': 'author', 'value': [{'authorName': {
        'typeName': 'authorName',
        'multiple': False,
        'typeClass': 'primitive',
        'value': 'Author One'
      }},
        {'authorIdentifierScheme': {
          'typeName': 'authorIdentifierScheme',
          'multiple': False,
          'typeClass': 'primitive',
          'value': 'ORCID'
        }}
      ]},
      {'typeName': 'datasetContact', 'value': [{'datasetContactName': {
        'typeName': 'datasetContactName',
        'multiple': False,
        'typeClass': 'primitive',
        'value': 'Contact One'
      }}]},
      {'typeName': 'dsDescription', 'value': [{'dsDescriptionValue': {
        'typeName': 'dsDescriptionValue',
        'multiple': False,
        'typeClass': 'primitive',
        'value': 'Description One'
      }}]},
      {'typeName': 'subject', 'value': 'Subject One'}
    ]}}}}, True, [], {'author': ['Author Affiliation field is missing for one of the authors!',
                                 'Author Identifier Scheme field is missing for one of the authors!',
                                 'Author Identifier field is missing for one of the authors!',
                                 'Author Name field is missing for one of the authors!'],
                      'datasetContact': ['Dataset Contact Affiliation field is missing for one of '
                                         'the datasetContacts!',
                                         'Dataset Contact Email field is missing for one of the '
                                         'datasetContacts!'],
                      'dsDescription': ['Dataset Description Date field is missing for one of the '
                                        'dsDescriptions!'],
                      'subject': [],
                      'title': []}),
  ], ids=['Success-Path-Complete-Metadata', 'Success-Path-Ignore-Title', 'Success-Path-Minimal-Metadata1',
          'Success-Path-Minimal-Metadata2'])
  def test_check_if_minimal_metadata_exists_success_path(self,
                                                         mocker,
                                                         metadata,
                                                         check_title,
                                                         expected_warnings,
                                                         expected_result):
    # Arrange
    mock_logger = mocker.MagicMock(spec=logging.Logger)

    # Act
    missing_information = check_if_minimal_metadata_exists(mock_logger, metadata, check_title)

    # Assert
    mock_logger.warning.assert_not_called()
    assert missing_information == expected_result, f"Unexpected missing information: {missing_information}"

  # Parametrized test for edge cases
  @pytest.mark.parametrize('metadata, check_title, expected_warnings', [
    # ID: Edge-Case-Empty-Metadata
    ({}, True, ['Empty metadata, make sure the metadata is loaded correctly...']),
    # ID: Edge-Case-Title-Missing
    (valid_metadata(), True, ['Missing title information']),
    # ID: Edge-Case-Subject-Missing
    (valid_metadata(), True, ['Missing subject information']),
  ], ids=['Edge-Case-Empty-Metadata', 'Edge-Case-Title-Missing', 'Edge-Case-Subject-Missing'])
  def test_check_if_minimal_metadata_exists_edge_cases(self, mocker, metadata, check_title, expected_warnings):
    # Arrange
    mock_logger = mocker.MagicMock(spec=logging.Logger)
    if 'title' in expected_warnings:
      metadata['datasetVersion']['metadataBlocks']['citation']['fields'][0]['value'] = None
    if 'subject' in expected_warnings:
      metadata['datasetVersion']['metadataBlocks']['citation']['fields'][4]['value'] = None

    # Act
    missing = check_if_minimal_metadata_exists(mock_logger, metadata, check_title)

    # Assert
    if 'Empty metadata' in expected_warnings[0]:
      mock_logger.warning.assert_any_call(expected_warnings[0])

  # Parametrized test for error cases
  @pytest.mark.parametrize('metadata, check_title, expected_warnings', [
    # ID: Error-Case-Invalid-Metadata-Structure
    ({'datasetVersion': {}}, True, ["'metadataBlocks'"]),
  ], ids=['Error-Case-Invalid-Metadata-Structure'])
  def test_check_if_minimal_metadata_exists_error_cases(self, mocker, metadata, check_title, expected_warnings):
    # Arrange
    mock_logger = mocker.MagicMock(spec=logging.Logger)
    if 'metadataBlocks' in expected_warnings:
      del metadata['datasetVersion']['metadataBlocks']
    if "'value'" in expected_warnings:
      del metadata['datasetVersion']['metadataBlocks']['citation']['fields'][0]['value']

    # Act
    with pytest.raises(KeyError) as exc_info:
      check_if_minimal_metadata_exists(mock_logger, metadata, check_title)

    # Assert
    assert str(exc_info.value) in expected_warnings

  def test_check_if_minimal_metadata_exists_for_default_metadata_should_return_empty_missing_info(self, mocker):
    # Arrange
    logger = mocker.MagicMock(spec=logging.Logger)
    current_path = realpath(join(os.getcwd(), dirname(__file__)))
    with open(join(current_path, '..//..//pasta_eln//dataverse', 'dataset-create-new-all-default-fields.json'),
              encoding='utf-8') as config_file:
      file_data = config_file.read()
      metadata = json.loads(file_data)

    # Act
    missing_info = check_if_minimal_metadata_exists(logger, metadata)

    assert missing_info == {'author': [],
                            'datasetContact': [],
                            'dsDescription': [],
                            'subject': [],
                            'title': []}, 'missing_info is not as expected'

  @pytest.mark.parametrize('metadata, name, expected', [
    ({'datasetVersion': {'metadataBlocks': {'citation': {'fields': [{'typeName': 'title', 'value': 'Sample Title'}]}}}},
     'title', {'typeName': 'title', 'value': 'Sample Title'}),
    ({'datasetVersion': {'metadataBlocks': {'citation': {
      'fields': [{'typeName': 'author', 'value': 'Author Name'}, {'typeName': 'title', 'value': 'Sample Title'}]}}}},
     'author', {'typeName': 'author', 'value': 'Author Name'}),
  ],
                           ids=['valid_field', 'valid_field_with_multiple'])
  def test_get_citation_field_success_path(self, metadata, name, expected):
    # Act
    result = get_citation_field(metadata, name)

    # Assert
    assert result == expected, 'The returned value is not as expected'

  @pytest.mark.parametrize('metadata, name, expected_exception', [
    # Test ID: ER-1
    ({'datasetVersion': {'metadataBlocks': {'citation': {'fields': [{'typeName': 'author', 'value': 'Author Name'}]}}}},
     'title', StopIteration),
    # Test ID: ER-2
    ({'datasetVersion': {'metadataBlocks': {}}}, 'title', KeyError),
    # Test ID: ER-3
    ({'datasetVersion': {}}, 'title', KeyError),
    # Test ID: ER-4
    ({}, 'title', KeyError),
  ], ids=['field_not_found', 'metadata_missing_citation', 'metadata_missing_blocks',
          'metadata_missing_version'])
  def test_get_citation_field_error_cases(self, metadata, name, expected_exception):
    # Act & Assert
    with pytest.raises(expected_exception):
      _ = get_citation_field(metadata, name)

  # Success path tests with various realistic test values
  @pytest.mark.parametrize('input_string, expected_output', [
    # ID: Test single word starting with uppercase
    ('Camel', 'Camel'),
    # ID: Test standard camel case
    ('CamelCaseSplit', 'Camel Case Split'),
    # ID: Test consecutive uppercase letters
    ('HTTPRequest', 'HTTP Request'),
    # ID: Test single uppercase letter
    ('A', 'A'),
    # ID: Test camel case ending with uppercase letter
    ('CamelCaseX', 'Camel Case X'),
    # ID: Test camel case with leading uppercase letters
    ('XMLHttpRequest', 'XML Http Request'),
    ('alternativeTitle', 'Alternative Title'),
  ], ids=[
    'single_word',
    'standard_camel_case',
    'consecutive_uppercase',
    'single_uppercase',
    'ending_with_uppercase',
    'leading_uppercase',
    'starting_lowercase',
  ])
  def test_adjust_type_name_success_path(self, input_string, expected_output):
    # Act
    result = adjust_type_name(input_string)

    # Assert
    assert result == expected_output, f"Expected {expected_output} but got {result}"

  # Edge cases
  @pytest.mark.parametrize('input_string, expected_output', [
    # ID: Test empty string
    ('', ''),
    # ID: Test string with only spaces
    ('   ', ''),
    # ID: Test string with special characters
    ('CamelCase#Split', 'Camel Case Split'),
    # ID: Test string with underscores
    ('Camel_Case_Split', 'Camel Case Split'),
  ], ids=[
    'empty_string',
    'only_spaces',
    'special_characters',
    'underscores',
  ])
  def test_adjust_type_name_edge_cases(self, input_string, expected_output):
    # Act
    result = adjust_type_name(input_string)

    # Assert
    assert result == expected_output, f"Expected {expected_output} but got {result}"

  # Error cases
  @pytest.mark.parametrize('input_string, expected_exception', [
    # ID: Test input is not a string (integer)
    (123, TypeError),
    # ID: Test input is not a string (list)
    (['CamelCaseSplit'], TypeError),
    # ID: Test input is not a string (None)
    (None, TypeError),
  ], ids=[
    'input_is_integer',
    'input_is_list',
    'input_is_none',
  ])
  def test_adjust_type_name_error_cases(self, input_string, expected_exception):
    # Act / Assert
    with pytest.raises(expected_exception):
      adjust_type_name(input_string)

  # Success path tests with various realistic test values
  @pytest.mark.parametrize('test_input, expected', [
    ({'a': {'value': 1}, 'b': {'value': 2}}, {'a': {'value': None}, 'b': {'value': None}}),
    ({'single': {'value': 'test', 'other': 'data'}}, {'single': {'value': None, 'other': 'data'}}),
    ({'empty': {'value': ''}}, {'empty': {'value': None}}),
  ], ids=['SuccessCase-1', 'SuccessCase-2', 'SuccessCase-3'])
  def test_clear_value_happy_path(self, test_input, expected):
    # Act
    clear_value(test_input)

    # Assert
    assert test_input == expected, f"Expected {expected}, but got {test_input}"

  # Edge cases
  @pytest.mark.parametrize('test_input, expected', [
    # Test ID: EC-1
    ({}, {}),  # Empty dictionary
    # Test ID: EC-2
    ({'none_value': None}, {'none_value': None}),  # Value is already None
    ({'not_a_dict': [{'value': 1}]}, {'not_a_dict': [{'value': 1}]}),  # Value is already None
  ], ids=['EdgeCase-1', 'EdgeCase-2', 'EdgeCase-3'])
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
    assert result is None, 'Expected None, but got a different result'

  # Parametrized test for success path with various realistic test values
  @pytest.mark.parametrize('type_name, expected_result', [
    # Test ID: #success_case_1 - type_name contains 'date' in lowercase
    ('date', True),
    # Test ID: #success_case_2 - type_name contains 'Date' in mixed case
    ('DateTime', True),
    # Test ID: #success_case_3 - type_name contains 'time' in lowercase
    ('timestamp', True),
    # Test ID: #success_case_4 - type_name contains 'Time' in mixed case
    ('modificationTime', True),
    # Test ID: #success_case_5 - type_name contains 'date' in the middle
    ('creation_date', True),
    # Test ID: #success_case_6 - type_name contains 'time' at the end
    ('update_time', True),
  ], ids=['success_case_1', 'success_case_1', 'success_case_2', 'success_case_3', 'success_case_4', 'success_case_5'])
  def test_is_date_time_type_happy_path(self, type_name, expected_result):
    # Act
    result = is_date_time_type(type_name)

    # Assert
    assert result == expected_result, f"Failed for {type_name}"

  # Parametrized test for edge cases
  @pytest.mark.parametrize('type_name, expected_result', [
    # Test ID: #edge_case_1 - type_name is an empty string
    ('', False),
    # Test ID: #edge_case_2 - type_name does not contain 'date' or 'time'
    ('string', False),
    # Test ID: #edge_case_3 - type_name contains 'date' or 'time' as a separate word
    ('my date', True),
    # Test ID: #edge_case_4 - type_name contains 'date' or 'time' with special characters
    ('due-date', True),
    # Test ID: #edge_case_5 - type_name contains 'date' or 'time' with numbers
    ('date1', True),
  ], ids=['edge_case_1', 'edge_case_2', 'edge_case_3', 'edge_case_4', 'edge_case_5'])
  def test_is_date_time_type_edge_cases(self, type_name, expected_result):
    # Act
    result = is_date_time_type(type_name)

    # Assert
    assert result == expected_result, f"Failed for {type_name}"

  # Parametrized test for error cases
  @pytest.mark.parametrize('type_name, expected_exception', [
    # Test ID: #error_case_1 - type_name is None (should raise an AttributeError)
    (None, AttributeError),
    # Test ID: #error_case_2 - type_name is not a string (should raise an AttributeError)
    (123, AttributeError),
    # Test ID: #error_case_3 - type_name is a list (should raise an AttributeError)
    (['date'], AttributeError),
  ], ids=['error_case_1', 'error_case_2', 'error_case_3'])
  def test_is_date_time_type_error_cases(self, type_name, expected_exception):
    # Act and Assert
    with pytest.raises(expected_exception):
      _ = is_date_time_type(type_name)

  # Parametrized test cases for happy path, edge cases, and error cases
  @pytest.mark.parametrize('missing_metadata, expected_output, test_id', [
    # Success path tests with various realistic test values
    (
        {'author': ['Name', 'Email'], 'datasetContact': ['Phone']},
        "<html><p><i>Goto 'Edit Metadata' dialog, select 'Minimal' metadata list, enter the below given missing information and retry the upload!"
        '</i></p><br></br><b><i>Author:</i></b><ul><i '
        'style="color:Crimson"><li>Name</li></i><i '
        'style="color:Crimson"><li>Email</li></i></ul><br></br><b><i>Dataset '
        'Contact:</i></b><ul><i style="color:Crimson"><li>Phone</li></i></ul></html>',
        'success_path_multiple_fields1'
    ),
    (
        {'author': ['Name']},
        "<html><p><i>Goto 'Edit Metadata' dialog, select 'Minimal' metadata list, enter the below given missing information and retry the upload!"
        '</i></p><br></br><b><i>Author:</i></b><ul><i '
        'style="color:Crimson"><li>Name</li></i></ul></html>',
        'success_path_single_field'
    ),
    (
        {
          'author': ['Author1 Missing!', 'Author2 Missing!'],
          'datasetContact': ['Dataset Contact 1 Missing!', 'Dataset Contact 2 Missing!'],
          'dsDescription': ['Dataset Description 1 Missing!', 'Dataset Description 2 Missing!'],
          'subject': ['Subject 1 Missing!', 'Subject 2 Missing!']
        },
        "<html><p><i>Goto 'Edit Metadata' dialog, select 'Minimal' metadata list, enter the below given missing information and retry the upload!"
        '</i></p><br></br><b><i>Author:</i></b><ul><i '
        'style="color:Crimson"><li>Author1 Missing!</li></i><i '
        'style="color:Crimson"><li>Author2 '
        'Missing!</li></i></ul><br></br><b><i>Dataset Contact:</i></b><ul><i '
        'style="color:Crimson"><li>Dataset Contact 1 Missing!</li></i><i '
        'style="color:Crimson"><li>Dataset Contact 2 '
        'Missing!</li></i></ul><br></br><b><i>Dataset Description:</i></b><ul><i '
        'style="color:Crimson"><li>Dataset Description 1 Missing!</li></i><i '
        'style="color:Crimson"><li>Dataset Description 2 '
        'Missing!</li></i></ul><br></br><b><i>Subject:</i></b><ul><i '
        'style="color:Crimson"><li>Subject 1 Missing!</li></i><i '
        'style="color:Crimson"><li>Subject 2 Missing!</li></i></ul></html>',
        'success_path_multiple_fields2'
    ),
    (
        {
          'author': [],
          'datasetContact': [],
          'dsDescription': [],
          'subject': []
        },
        '',
        'success_path_empty_fields'
    ),

    # Edge cases
    (
        {},
        '',
        'edge_case_empty_input'
    ),
    (
        {'author': [], 'datasetContact': []},
        '',
        'edge_case_empty_lists'
    ),

    # Error cases
    (
        {'unknownField': ['Unknown']},
        KeyError("dict object has no attribute 'unknownField'"),
        'error_case_unknown_field'
    ),
  ])
  def test_get_formatted_message(self, missing_metadata, expected_output, test_id):
    # Arrange
    result = None
    # Act
    if isinstance(expected_output, Exception):
      with pytest.raises(type(expected_output)):
        result = get_formatted_message(missing_metadata)
    else:
      result = get_formatted_message(missing_metadata)
    # Assert
    if isinstance(expected_output, Exception):
      assert result is None, f"Test failed for {test_id}"
    else:
      assert result == expected_output, f"Test failed for {test_id}"

  # Test cases for happy path scenarios
  @pytest.mark.parametrize('metadata,expected_output', [
    # Test ID: SuccessCase-1
    (
        {
          'datasetVersion': {
            'license': 'CC0',
            'metadataBlocks': {
              'citation': {
                'fields': [
                  {'typeName': 'title', 'value': 'Test Dataset'},
                  {'typeName': 'author', 'value': ['Author 1', 'Author 2']},
                ]
              }
            }
          }
        },
        {'license': 'CC0', 'title': 'Test Dataset', 'author': ['Author 1', 'Author 2']}
    ),
    # Test ID: SuccessCase-2
    (
        {
          'datasetVersion': {
            'license': None,
            'metadataBlocks': {
              'citation': {
                'fields': [
                  {'typeName': 'title', 'value': 'No License Dataset'},
                ]
              }
            }
          }
        },
        {'title': 'No License Dataset'}
    ),
  ], ids=['SuccessCase-1', 'SuccessCase-2'])
  def test_get_flattened_metadata_happy_path(self, metadata, expected_output):
    # Act
    result = get_flattened_metadata(metadata)

    # Assert
    assert result == expected_output, 'The flattened metadata does not match the expected output.'

  # Test cases for edge cases
  @pytest.mark.parametrize('metadata,expected_output', [
    # Test ID: EdgeCase-1
    (
        {'datasetVersion': {'license': 'CC0', 'metadataBlocks': {}}},
        {'license': 'CC0'}
    ),
    # Test ID: EdgeCase-2
    (
        {
          'datasetVersion': {
            'license': 'CC0',
            'metadataBlocks': {
              'citation': {
                'fields': []
              }
            }
          }
        },
        {'license': 'CC0'}
    ),
  ], ids=['EdgeCase-1', 'EdgeCase-2'])
  def test_get_flattened_metadata_edge_cases(self, metadata, expected_output):
    # Act
    result = get_flattened_metadata(metadata)

    # Assert
    assert result == expected_output, 'The flattened metadata does not match the expected output for edge cases.'

  # Test cases for error scenarios
  @pytest.mark.parametrize('metadata,error_type', [
    # Test ID: ErrorCase-1
    ({}, KeyError),
    # Test ID: ErrorCase-2
    ({'datasetVersion': {}}, KeyError),
    # Test ID: ErrorCase-3
    (
        {
          'datasetVersion': {
            'license': 'CC0',
            'metadataBlocks': {
              'citation': {
                'fields': [
                  {'typeName': 'title'},  # Missing 'value' key
                ]
              }
            }
          }
        },
        KeyError
    ),
  ], ids=['ErrorCase-1', 'ErrorCase-2', 'ErrorCase-3'])
  def test_get_flattened_metadata_error_cases(self, metadata, error_type):
    # Act & Assert
    with pytest.raises(error_type):
      get_flattened_metadata(metadata)

  @pytest.mark.parametrize('api_token, server_url, dataverse_id, info_return, expected_result, test_id', [
    # Success path tests
    ('valid_token', 'https://valid.server.com', 'valid_id', {'id': '123', 'alias': 'valid_id'}, True,
     'success_path_valid'),
    ('valid_token', 'https://valid.server.com', 'another_valid_id', {'id': '456', 'alias': 'another_valid_id'}, True,
     'success_path_another_valid'),

    # Edge cases
    ('', 'https://valid.server.com', 'valid_id', {'id': '123', 'alias': 'valid_id'}, True, 'edge_case_empty_token'),
    ('valid_token', '', 'valid_id', {'id': '123', 'alias': 'valid_id'}, True, 'edge_case_empty_server_url'),
    ('valid_token', 'https://valid.server.com', '', {'id': '123', 'alias': ''}, True, 'edge_case_empty_dataverse_id'),

    # Error cases
    ('invalid_token', 'https://valid.server.com', 'valid_id', 'Unauthorized access', False, 'error_case_unauthorized'),
    ('valid_token', 'https://invalid.server.com', 'valid_id', 'Server not found', False, 'error_case_server_not_found'),
    ('valid_token', 'https://valid.server.com', 'nonexistent_id', None, False, 'error_case_nonexistent_id'),
  ])
  def test_check_if_dataverse_exists(self, mocker, api_token, server_url, dataverse_id,
                                     info_return, expected_result, test_id):
    # Arrange
    mock_logger = mocker.MagicMock()
    client_mock = mocker.patch('pasta_eln.dataverse.utils.DataverseClient')
    client_mock.return_value.get_dataverse_info = AsyncMock(return_value=info_return)

    # Act
    result = check_if_dataverse_exists(mock_logger, api_token, server_url, dataverse_id)

    # Assert
    assert result == expected_result, f"Test ID: {test_id}"
    if isinstance(info_return, dict):
      mock_logger.info.assert_called_with('Checking if login info is valid, server_url: %s', server_url)
    else:
      mock_logger.warning.assert_called()

  @pytest.mark.parametrize('metadata, expected_output, test_id', [
    # Happy path tests
    ({'datasetVersion': {'license': {'name': 'CC0', 'uri': 'https://creativecommons.org/publicdomain/zero/1.0/'},
                         'metadataBlocks': {
                           'citation': {
                             'displayName': 'Citation Metadata',
                             'fields': [
                               {'typeName': 'title', 'value': 'Test Title', 'multiple': False, 'typeClass': 'primitive'}
                             ]
                           }
                         }}},
     "<html><b style=\"color:Black\">License Metadata:</b><ul><li style=\"color:Gray\">Name: <i>CC0</i></li><li style=\"color:Gray\">URI: <i>https://creativecommons.org/publicdomain/zero/1.0/</i></li></ul><b style=\"color:Black\">Citation Metadata:</b><ul><b style=\"color:#737373\"><li>Title:</li></b><ul><i style=\"color:Gray\"><li>Test Title</li></i></ul></ul></html>",
     'success_path_basic_metadata'),

    # Edge case: Empty metadata
    ({'datasetVersion': {'license': None, 'metadataBlocks': {}}},
     '<html></html>',
     'edge_case_empty_metadata'),

    # Complex nested metadata
    ({'datasetVersion': {'license': {'name': 'CC BY', 'uri': 'https://creativecommons.org/licenses/by/4.0/'},
                         'metadataBlocks': {
                           'citation': {
                             'displayName': 'Citation Metadata',
                             'fields': [
                               {'typeName': 'author',
                                'value': [{'authorName': {'typeName': 'authorName', 'value': 'John Doe'}},
                                          {'authorName': {'typeName': 'authorName', 'value': 'Jane Doe'}}],
                                'multiple': True, 'typeClass': 'compound'}
                             ]
                           }
                         }}},
     "<html><b style=\"color:Black\">License Metadata:</b><ul><li style=\"color:Gray\">Name: <i>CC BY</i></li><li style=\"color:Gray\">URI: <i>https://creativecommons.org/licenses/by/4.0/</i></li></ul><b style=\"color:Black\">Citation Metadata:</b><ul><b style=\"color:#737373\"><li>Author:</li></b><ul><li style=\"color:Gray\">Item 1:</li><ul><li style=\"color:Gray\">Author Name: <i>John Doe</li></i></ul><li style=\"color:Gray\">Item 2:</li><ul><li style=\"color:Gray\">Author Name: <i>Jane Doe</li></i></ul></ul></ul></html>",
     'complex_nested_metadata')
  ], ids=['success_path_basic_metadata', 'edge_case_empty_metadata', 'complex_nested_metadata'])
  def test_get_formatted_metadata_message_version_1(self, test_id, metadata, expected_output):
    # Act
    result = get_formatted_metadata_message(metadata)

    # Assert
    assert result == expected_output

  @pytest.mark.parametrize(
    'metadata, expected_output',
    [
      # Success path test case
      param(
        {
          'datasetVersion': {
            'license': {'name': 'CC0', 'uri': 'https://creativecommons.org/publicdomain/zero/1.0/'},
            'metadataBlocks': {
              'citation': {
                'displayName': 'Citation Metadata',
                'fields': [
                  {'typeName': 'title', 'value': 'Test Title', 'multiple': False, 'typeClass': 'primitive'}
                ]
              }
            }
          }
        },
        '<html><b style="color:Black">License Metadata:</b><ul>'
        '<li style="color:Gray">Name: <i>CC0</i></li>'
        '<li style="color:Gray">URI: <i>https://creativecommons.org/publicdomain/zero/1.0/</i></li>'
        '</ul><b style="color:Black">Citation Metadata:</b><ul>'
        '<b style="color:#737373"><li>Title:</li></b><ul>'
        '<i style="color:Gray"><li>Test Title</li></i></ul></ul></html>',
        id='success_path_single_field'
      ),
      # Success path test case
      param(
        {
          'datasetVersion': {
            'license': {'name': 'CC0', 'uri': 'https://creativecommons.org/publicdomain/zero/1.0/'},
            'metadataBlocks': {
              'citation': {
                'displayName': 'Citation Metadata',
                'fields': [
                  {'typeName': 'coverage.Spectral.Wavelength', 'value': [
                    {
                      'coverage.Spectral.MinimumWavelength': {
                        'typeName': 'coverage.Spectral.MinimumWavelength',
                        'multiple': False,
                        'typeClass': 'primitive',
                        'value': '4001'
                      },
                      'coverage.Spectral.MaximumWavelength': {
                        'typeName': 'coverage.Spectral.MaximumWavelength',
                        'multiple': False,
                        'typeClass': 'primitive',
                        'value': '4002'
                      }
                    },
                    {
                      'coverage.Spectral.MinimumWavelength': {
                        'typeName': 'coverage.Spectral.MinimumWavelength',
                        'multiple': False,
                        'typeClass': 'primitive',
                        'value': '4003'
                      },
                      'coverage.Spectral.MaximumWavelength': {
                        'typeName': 'coverage.Spectral.MaximumWavelength',
                        'multiple': False,
                        'typeClass': 'primitive',
                        'value': '4004'
                      }
                    }
                  ], 'multiple': True, 'typeClass': 'compound'}
                ]
              }
            }
          }
        },
        '<html><b style="color:Black">License Metadata:</b><ul><li '
        'style="color:Gray">Name: <i>CC0</i></li><li style="color:Gray">URI: '
        '<i>https://creativecommons.org/publicdomain/zero/1.0/</i></li></ul><b '
        'style="color:Black">Citation Metadata:</b><ul><b '
        'style="color:#737373"><li>Coverage Spectral Wavelength:</li></b><ul><li '
        'style="color:Gray">Item 1:</li><ul><li style="color:Gray">Coverage Spectral '
        'Minimum Wavelength: <i>4001</li></i><li style="color:Gray">Coverage Spectral '
        'Maximum Wavelength: <i>4002</li></i></ul><li style="color:Gray">Item '
        '2:</li><ul><li style="color:Gray">Coverage Spectral Minimum Wavelength: '
        '<i>4003</li></i><li style="color:Gray">Coverage Spectral Maximum Wavelength: '
        '<i>4004</li></i></ul></ul></ul></html>',
        id='success_path_multiple_compound_field'
      ),
      # Success path test case
      param(
        {
          'datasetVersion': {
            'license': {'name': 'CC0', 'uri': 'https://creativecommons.org/publicdomain/zero/1.0/'},
            'metadataBlocks': {
              'citation': {
                'displayName': 'Citation Metadata',
                'fields': [
                  {
                    'typeName': 'targetSampleSize',
                    'multiple': False,
                    'typeClass': 'compound',
                    'value': {
                      'targetSampleActualSize': {
                        'typeName': 'targetSampleActualSize',
                        'multiple': False,
                        'typeClass': 'primitive',
                        'value': '100'
                      },
                      'targetSampleSizeFormula': {
                        'typeName': 'targetSampleSizeFormula',
                        'multiple': False,
                        'typeClass': 'primitive',
                        'value': 'TargetSampleSizeFormula'
                      }
                    }
                  }
                ]
              }
            }
          }
        },
        '<html><b style="color:Black">License Metadata:</b><ul><li '
        'style="color:Gray">Name: <i>CC0</i></li><li style="color:Gray">URI: '
        '<i>https://creativecommons.org/publicdomain/zero/1.0/</i></li></ul><b '
        'style="color:Black">Citation Metadata:</b><ul><b '
        'style="color:#737373"><li>Target Sample Size:</li></b><ul><li '
        'style="color:Gray">Target Sample Actual Size: <i>100</li></i><li '
        'style="color:Gray">Target Sample Size Formula: '
        '<i>TargetSampleSizeFormula</li></i></ul></ul></html>',
        id='success_path_single_compound_field'
      ),
      # Edge case: Empty metadata
      param(
        {
          'datasetVersion': {
            'license': None,
            'metadataBlocks': {}
          }
        },
        '<html></html>',
        id='empty_metadata'
      ),
      # Edge case: No license
      param(
        {
          'datasetVersion': {
            'license': None,
            'metadataBlocks': {
              'citation': {
                'displayName': 'Citation Metadata',
                'fields': [
                  {'typeName': 'title', 'value': 'Test Title', 'multiple': False, 'typeClass': 'primitive'}
                ]
              }
            }
          }
        },
        '<html><b style="color:Black">Citation Metadata:</b><ul>'
        '<b style="color:#737373"><li>Title:</li></b><ul>'
        '<i style="color:Gray"><li>Test Title</li></i></ul></ul></html>',
        id='no_license'
      ),
      # Edge case: No fields in metadata block
      param(
        {
          'datasetVersion': {
            'license': {'name': 'CC0', 'uri': 'https://creativecommons.org/publicdomain/zero/1.0/'},
            'metadataBlocks': {
              'citation': {
                'displayName': 'Citation Metadata',
                'fields': []
              }
            }
          }
        },
        '<html><b style="color:Black">License Metadata:</b><ul>'
        '<li style="color:Gray">Name: <i>CC0</i></li>'
        '<li style="color:Gray">URI: <i>https://creativecommons.org/publicdomain/zero/1.0/</i></li>'
        '</ul><b style="color:Black">Citation Metadata:</b><ul>'
        '<li style="color:#737373">No Value</li></ul></ul></html>',
        id='no_fields_in_metadata_block'
      ),
      # Error case: Missing datasetVersion key
      param(
        {},
        KeyError,
        id='missing_datasetVersion_key'
      ),
      # Error case: Missing metadataBlocks key
      param(
        {
          'datasetVersion': {
            'license': {'name': 'CC0', 'uri': 'https://creativecommons.org/publicdomain/zero/1.0/'}
          }
        },
        KeyError,
        id='missing_metadataBlocks_key'
      ),
    ]
  )
  def test_get_formatted_metadata_message_version_2(self, metadata, expected_output):
    # Act
    if isinstance(expected_output, type) and issubclass(expected_output, Exception):
      with pytest.raises(expected_output):
        get_formatted_metadata_message(metadata)
    else:
      result = get_formatted_metadata_message(metadata)

      # Assert
      assert result == expected_output

  # Test data for error cases
  @pytest.mark.parametrize('metadata,expected_exception, test_id', [
    ({}, KeyError, 'error_case_empty_metadata'),
    ({'datasetVersion': {}}, KeyError, 'error_case_missing_license_and_metadata_blocks'),
  ])
  def test_get_formatted_metadata_message_error_cases(self, metadata, expected_exception, test_id):
    # Arrange - done via test parameters

    # Act & Assert
    with pytest.raises(expected_exception):
      get_formatted_metadata_message(metadata)

  @pytest.mark.parametrize(
    'dataverse_url, expected_output',
    [
      # Happy path tests
      pytest.param('http://example.com?persistentId=12345',
                   "<html><head/><body><p>Dataverse URL: <a href='http://example.com?persistentId=12345'><span style='font-style:italic; text-decoration: underline; color:#77767b;'>12345</span></a></p></body></html>",
                   id='success_path_1'),
      pytest.param('https://dataverse.org?persistentId=abcde',
                   "<html><head/><body><p>Dataverse URL: <a href='https://dataverse.org?persistentId=abcde'><span style='font-style:italic; text-decoration: underline; color:#77767b;'>abcde</span></a></p></body></html>",
                   id='success_path_2'),

      # Edge cases
      pytest.param('http://example.com?persistentId=',
                   "<html><head/><body><p>Dataverse URL: <a href='http://example.com?persistentId='><span style='font-style:italic; text-decoration: underline; color:#77767b;'></span></a></p></body></html>",
                   id='edge_case_empty_persistent_id'),
      pytest.param('http://example.com?persistentId=12345&otherParam=value',
                   "<html><head/><body><p>Dataverse URL: <a href='http://example.com?persistentId=12345&otherParam=value'><span style='font-style:italic; text-decoration: underline; color:#77767b;'>12345&otherParam=value</span></a></p></body></html>",
                   id='edge_case_additional_params'),

      # Error cases
      pytest.param('', '', id='error_case_empty_url'),
      pytest.param(None, '', id='error_case_none_url'),
      pytest.param('http://example.com', '', id='error_case_no_persistent_id'),
    ]
  )
  def test_get_formatted_dataverse_url(self, dataverse_url, expected_output):
    # Act
    result = get_formatted_dataverse_url(dataverse_url)

    # Assert
    assert result == expected_output

  @pytest.mark.parametrize(
    'data_hierarchy, expected',
    [
      # Happy path tests
      param([DataHierarchyModel(doc_type='report'), DataHierarchyModel(doc_type='summary')],
            ['Report', 'Summary', 'Unidentified'], id='happy_path_different_types'),
      param([DataHierarchyModel(doc_type='report'), DataHierarchyModel(doc_type='report')], ['Report', 'Unidentified'],
            id='happy_path_duplicate_types'),

      # Edge cases
      param(None, [], id='edge_case_none_input'),
      param([], ['Unidentified'], id='edge_case_empty_list'),
      param(
        [DataHierarchyModel(doc_type='x0'), DataHierarchyModel(doc_type='x1')], ['Unidentified'],
        id='edge_case_excluded_types'),
      param([DataHierarchyModel(doc_type='')], ['Unidentified'], id='edge_case_empty_docType'),
      param([DataHierarchyModel(doc_type=None)], ['Unidentified'], id='edge_case_none_docType'),

      # Error cases
      param([DataHierarchyModel(doc_type='report'), None], ['Report', 'Unidentified'], id='error_case_none_in_list'),
      param([None, DataHierarchyModel(doc_type='report')], ['Report', 'Unidentified'],
            id='error_case_none_first_in_list'),
    ],
    ids=lambda x: x[2]
  )
  def test_get_data_hierarchy_types(self, data_hierarchy, expected, request):
    # Act
    result = get_data_hierarchy_types(data_hierarchy)

    # Assert
    assert result == expected, f"Failed on test case: {request.node.callspec.id}"

  @pytest.mark.parametrize(
    'config, expected, exception',
    [
      # Happy path test cases
      param(
        {
          'defaultProjectGroup': 'group1',
          'projectGroups': {
            'group1': {
              'local': {
                'path': '/path/to/db',
                'database': 'test_db'
              }
            }
          }
        },
        {'database_path': '/path/to/db', 'database_name': 'test_db'},
        None,
        id='happy_path_valid_config'
      ),
      # Edge case: Empty defaultProjectGroup
      param(
        {
          'defaultProjectGroup': '',
          'projectGroups': {
            'group1': {
              'local': {
                'path': '/path/to/db',
                'database': 'test_db'
              }
            }
          }
        },
        None,
        ConfigError,
        id='edge_case_empty_defaultProjectGroup'
      ),
      # Edge case: Empty projectGroups
      param(
        {
          'defaultProjectGroup': 'group1',
          'projectGroups': {}
        },
        None,
        ConfigError,
        id='edge_case_empty_projectGroups'
      ),
      # Error case: Missing defaultProjectGroup
      param(
        {
          'projectGroups': {
            'group1': {
              'local': {
                'path': '/path/to/db',
                'database': 'test_db'
              }
            }
          }
        },
        None,
        ConfigError,
        id='error_case_missing_defaultProjectGroup'
      ),
      # Error case: Missing projectGroups
      param(
        {
          'defaultProjectGroup': 'group1'
        },
        None,
        ConfigError,
        id='error_case_missing_projectGroups'
      ),
      # Error case: defaultProjectGroup not in projectGroups
      param(
        {
          'defaultProjectGroup': 'group2',
          'projectGroups': {
            'group1': {
              'local': {
                'path': '/path/to/db',
                'database': 'test_db'
              }
            }
          }
        },
        None,
        ConfigError,
        id='error_case_defaultProjectGroup_not_in_projectGroups'
      ),
      # Error case: Missing local info
      param(
        {
          'defaultProjectGroup': 'group1',
          'projectGroups': {
            'group1': {}
          }
        },
        None,
        ConfigError,
        id='error_case_missing_local_info'
      ),
      # Error case: Missing database path
      param(
        {
          'defaultProjectGroup': 'group1',
          'projectGroups': {
            'group1': {
              'local': {
                'database': 'test_db'
              }
            }
          }
        },
        None,
        ConfigError,
        id='error_case_missing_database_path'
      ),
      # Error case: Missing database name
      param(
        {
          'defaultProjectGroup': 'group1',
          'projectGroups': {
            'group1': {
              'local': {
                'path': '/path/to/db'
              }
            }
          }
        },
        None,
        ConfigError,
        id='error_case_missing_database_name'
      ),
    ],
    ids=lambda x: x[-1]
  )
  def test_get_db_info(self, config, expected, exception):
    # Arrange
    logger = MagicMock(spec=logging.Logger)
    with patch(
        'pasta_eln.dataverse.pasta_config_reader_factory.PastaConfigReaderFactory.get_instance') as mock_get_instance:
      mock_get_instance.return_value.config = config

      # Act
      if exception:
        with pytest.raises(exception):
          get_db_info(logger)
      else:
        result = get_db_info(logger)

        # Assert
        assert result == expected

  @pytest.mark.parametrize(
    'model_id, expected_type, expected_id',
    [
      # Happy path with a specific model_id
      param('123', 'x0', '123', id='happy_path_with_id'),
      # Happy path with None model_id
      param(None, 'x0', None, id='happy_path_without_id'),
      # Edge case with empty string model_id
      param('', 'x0', '', id='edge_case_empty_string_id'),
      # Edge case with special characters in model_id
      param('!@#$', 'x0', '!@#$', id='edge_case_special_chars_id'),
      # Edge case with very long model_id
      param('a' * 256, 'x0', 'a' * 256, id='edge_case_long_id'),
    ],
    ids=lambda x: x[-1]
  )
  def test_generate_project_join_statement(self, model_id, expected_type, expected_id):
    # Act
    join_statement = generate_project_join_statement(model_id)

    # Assert
    assert isinstance(join_statement, Executable)
    assert join_statement.whereclause is not None
    if model_id is not None:
      assert str(join_statement.whereclause) == 'main.type = :type_1 AND main.id = :id_1' or 'main.type = :type_1'
    else:
      assert str(join_statement.whereclause) == 'main.type = :type_1'

    # Check if the join conditions are correct
    assert any(
      str(condition) == 'main.type = :type_1 AND main.id = :id_1'
      or 'main.type = :type_1 AND main.id = :id_2'
      or 'main.type = :type_1'
      for condition in join_statement._where_criteria
    )
