#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_utils.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import json
import logging

import pytest

from pasta_eln.dataverse.database_error import DatabaseError
from pasta_eln.dataverse.upload_status_values import UploadStatusValues
from pasta_eln.dataverse.utils import log_and_create_error, read_pasta_config_file, set_authors, update_status


class TestUtils:

  # Parametrized test cases for happy path, edge cases, and error cases
  @pytest.mark.parametrize(
    "status, expected_icon_name, test_id",
    [
      (UploadStatusValues.Queued.name, 'ph.queue-bold', 'happy_path_queued'),
      (UploadStatusValues.Uploading.name, 'mdi6.progress-upload', 'happy_path_uploading'),
      (UploadStatusValues.Cancelled.name, 'mdi.cancel', 'happy_path_cancelled'),
      (UploadStatusValues.Finished.name, 'fa.check-circle-o', 'happy_path_finished'),
      (UploadStatusValues.Error.name, 'msc.error-small', 'happy_path_error'),
      (UploadStatusValues.Warning.name, 'fa.warning', 'happy_path_warning'),
      # Add edge cases here
      # Add error cases here
    ]
  )
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

  @pytest.mark.parametrize(
    "test_id, config_data",
    [
      ("SuccessCase-1", {"key": "value", "number": 42}),
      ("SuccessCase-2", {"empty_dict": {}}),
      ("SuccessCase-3", {"list_key": [1, 2, 3]}),
    ],
  )
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
  @pytest.mark.parametrize(
    "test_id, exception, message",
    [
      ("ErrorCase-1", DatabaseError, "Config file not found, Corrupt installation!"),
    ],
  )
  def test_read_pasta_config_file_error_path(self, mocker, test_id, exception, message, tmp_path):
    # Arrange
    mock_logger = mocker.MagicMock(spec=logging.Logger)
    with mocker.patch('pasta_eln.dataverse.utils.Path.home', return_value=tmp_path), \
        mocker.patch('pasta_eln.dataverse.utils.exists', return_value=False), \
        pytest.raises(exception) as exc_info:
      # Act
      read_pasta_config_file(mock_logger)

    # Assert
    assert str(exc_info.value) == message, f"Failed test ID: {test_id}"
    mock_logger.error.assert_called_with(message)

  # Parametrized test for happy path scenarios with various realistic test values
  @pytest.mark.parametrize("exception_type, error_message, test_id", [
    (ValueError, "Invalid value provided", 'happy_path_value_error'),
    (TypeError, "Type mismatch encountered", 'happy_path_type_error'),
    (KeyError, "Missing key in dictionary", 'happy_path_key_error'),
  ], ids=lambda test_id: test_id)
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
  @pytest.mark.parametrize("exception_type, error_message, test_id", [
    (Exception, "", 'edge_case_empty_message'),
    (RuntimeError, "  ", 'edge_case_whitespace_message'),
    (Exception, "A" * 1000, 'edge_case_long_message'),
  ], ids=lambda test_id: test_id)
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
  @pytest.mark.parametrize("exception_type, error_message, test_id", [
    (None, "Exception type is None", 'error_case_none_exception_type'),
    ("NotAType", "Exception type is not a type", 'error_case_not_a_type_exception_type'),
  ], ids=lambda test_id: test_id)
  def test_log_and_create_error_error_cases(self, mocker, exception_type, error_message, test_id):
    # Arrange
    mock_logger = mocker.MagicMock(spec=logging.Logger)

    # Act & Assert
    with pytest.raises(TypeError):
      log_and_create_error(mock_logger, exception_type, error_message)

  # Parametrized test for success path with various realistic test values
  @pytest.mark.parametrize("config_data, metadata, expected_authors_list, test_id", [
    (
        {'authors': [
          {'last': 'Doe', 'first': 'John', 'orcid': '0000-0001', 'organizations': [{'organization': 'Org1'}]}]},
        {'datasetVersion': {'metadataBlocks': {'citation': {'fields': [{'typeName': 'author', 'value': [
          {'authorName': {'value': 'Last, First'}, 'authorIdentifierScheme': {'value': 'ORCID'},
           'authorIdentifier': {'value': ''}, 'authorAffiliation': {'value': ''}}]}]}}}},
        [{'authorName': {'value': 'Doe, John'}, 'authorIdentifierScheme': {'value': 'ORCID'},
          'authorIdentifier': {'value': '0000-0001'}, 'authorAffiliation': {'value': 'Org1'}}],
        "success-path-single-author"
    ),
    (
        {'authors': [{'last': 'Smith', 'first': 'Jane', 'orcid': '0000-0002',
                      'organizations': [{'organization': 'Org2'}, {'organization': 'Org3'}]}]},
        {'datasetVersion': {'metadataBlocks': {'citation': {'fields': [{'typeName': 'author', 'value': [
          {'authorName': {'value': 'Last, First'}, 'authorIdentifierScheme': {'value': 'ORCID'},
           'authorIdentifier': {'value': ''}, 'authorAffiliation': {'value': ''}}]}]}}}},
        [{'authorName': {'value': 'Smith, Jane'}, 'authorIdentifierScheme': {'value': 'ORCID'},
          'authorIdentifier': {'value': '0000-0002'}, 'authorAffiliation': {'value': 'Org2, Org3'}}],
        "success-path-single-author-multiple-orgs"
    ),
    (
        {'authors': [
          {'last': 'Doe', 'first': 'John', 'orcid': '0000-0001', 'organizations': [{'organization': 'Org1'}]},
          {'last': 'Smith', 'first': 'Jane', 'orcid': '0000-0002', 'organizations': [{'organization': 'Org2'}]},
          {'last': 'Keith', 'first': 'Sean', 'orcid': '0000-0003',
           'organizations': [{'organization': 'Org3'}, {'organization': 'Org4'}]}
        ]},
        {'datasetVersion': {'metadataBlocks': {'citation': {'fields': [{'typeName': 'author', 'value': [
          {'authorName': {'value': 'Last, First'}, 'authorIdentifierScheme': {'value': 'ORCID'},
           'authorIdentifier': {'value': ''}, 'authorAffiliation': {'value': ''}}]}]}}}},
        [
          {'authorName': {'value': 'Doe, John'}, 'authorIdentifierScheme': {'value': 'ORCID'},
           'authorIdentifier': {'value': '0000-0001'}, 'authorAffiliation': {'value': 'Org1'}},
          {'authorName': {'value': 'Smith, Jane'}, 'authorIdentifierScheme': {'value': 'ORCID'},
           'authorIdentifier': {'value': '0000-0002'}, 'authorAffiliation': {'value': 'Org2'}},
          {'authorName': {'value': 'Keith, Sean'}, 'authorIdentifierScheme': {'value': 'ORCID'},
           'authorIdentifier': {'value': '0000-0003'}, 'authorAffiliation': {'value': 'Org3, Org4'}}
        ],
        "success-path-multiple-authors"
    ),
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
    authors_list = author_field['value']
    assert authors_list == expected_authors_list
    mock_log_and_create_error.assert_not_called()

  @pytest.mark.parametrize("config_data, metadata, expected_authors_list, test_id", [
    (
        {'authors': [
          {'last': '', 'first': '', 'orcid': '', 'organizations': [{'organization': ''}]}]},
        {'datasetVersion': {'metadataBlocks': {'citation': {'fields': [{'typeName': 'author', 'value': [
          {'authorName': {'value': 'Last, First'}, 'authorIdentifierScheme': {'value': 'ORCID'},
           'authorIdentifier': {'value': ''}, 'authorAffiliation': {'value': ''}}]}]}}}},
        [{'authorName': {'value': ''}, 'authorIdentifierScheme': {'value': 'ORCID'},
          'authorIdentifier': {'value': ''}, 'authorAffiliation': {'value': ''}}],
        "edge-case-path-empty-author"
    )
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
    authors_list = author_field['value']
    assert authors_list == expected_authors_list
    mock_log_and_create_error.assert_not_called()

  # Parametrized test for various error cases
  @pytest.mark.parametrize("config_data, metadata, exception, test_id", [
    # Test ID: 1
    (
        {},  # No authors in config
        {'datasetVersion': {'metadataBlocks': {
          'citation': {'fields': [{'typeName': 'author', 'value': [{'authorName': {'value': ''}}]}]}}}},
        DatabaseError("Incorrect config file, authors not found!"),
        "error-no-authors-in-config"
    ),
    # Test ID: 2
    (
        {'authors': []},  # Empty authors list in config
        {'datasetVersion': {'metadataBlocks': {'citation': {'fields': [{'typeName': 'author', 'value': []}]}}}},
        DatabaseError("Incorrect config file, authors not found!"),
        "error-empty-authors-list"
    ),
  ])
  def test_set_authors_error_cases(self, mocker, config_data, metadata, exception, test_id):
    # Arrange
    logger = mocker.MagicMock()
    mocker.patch('pasta_eln.dataverse.utils.read_pasta_config_file', return_value=config_data)
    mock_log_and_create_error = mocker.patch('pasta_eln.dataverse.utils.log_and_create_error', return_value=exception)

    # Act & Assert
    with pytest.raises(type(exception)):
      set_authors(logger, metadata)
    mock_log_and_create_error.assert_called_once()
