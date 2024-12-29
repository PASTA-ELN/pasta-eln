#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_database_api.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from unittest.mock import patch

import pytest
from _pytest.mark import param

from pasta_eln.database.models.config_model import ConfigModel
from pasta_eln.database.models.data_hierarchy_model import DataHierarchyModel
from pasta_eln.dataverse.database_api import DatabaseAPI
from pasta_eln.database.error import Error
from pasta_eln.database.models.project_model import ProjectModel
from pasta_eln.database.models.upload_model import UploadModel


@pytest.fixture
def mock_db_api():
  with patch('pasta_eln.dataverse.database_api.BaseDatabaseApi') as MockBaseDatabaseApi:
    yield MockBaseDatabaseApi.return_value


@pytest.fixture
def mock_config_model():
  return ConfigModel(dataverse_login_info={'api_token': 'encrypted_token'})


@pytest.fixture
def database_api(mocker, mock_db_api):
  mocker.patch('pasta_eln.dataverse.database_api.logging.getLogger')
  mocker.patch('pasta_eln.dataverse.database_api.get_db_info', return_value={'database_path': '/mock/path'})
  mocker.patch('pasta_eln.dataverse.database_api.Path.home', return_value='/mock/path')
  mocker.patch('pasta_eln.dataverse.database_api.get_encrypt_key', return_value=(True, 'key'))
  return DatabaseAPI()


class TestDataverseDatabaseAPI:
  # Parametrized test for the happy path
  @pytest.mark.parametrize('db_info, expected_db_api_calls', [
    ({'database_path': '/mock/path'}, [('/mock/path/.pastaELN_dataverse.db', '/mock/path/pastaELN.db')]),
  ], ids=['success_path'])
  def test_database_api_create_instance_success_path(self, mocker, db_info, expected_db_api_calls):
    # Arrange
    mock_get_logger = mocker.patch('pasta_eln.dataverse.database_api.logging.getLogger')
    mock_home = mocker.patch('pasta_eln.dataverse.database_api.Path.home', return_value='/mock/path')
    mock_get_encrypt_key = mocker.patch('pasta_eln.dataverse.database_api.get_encrypt_key', return_value=('', ''))
    with patch('pasta_eln.dataverse.database_api.get_db_info', return_value=db_info) as mock_get_db_info, \
        patch('pasta_eln.dataverse.database_api.BaseDatabaseApi') as MockBaseDatabaseApi:
      # Act
      db_api_instance = DatabaseAPI()

      # Assert
      MockBaseDatabaseApi.assert_called_once_with(*expected_db_api_calls[0])
      mock_home.assert_called_once()
      mock_get_encrypt_key.assert_called_once()
      mock_get_db_info.assert_called_once()
      mock_get_logger.assert_called_once_with('pasta_eln.dataverse.database_api.DatabaseAPI')
      assert db_api_instance.logger is mock_get_logger.return_value
      assert db_api_instance.db_api is MockBaseDatabaseApi.return_value
      assert db_api_instance.dataverse_db_name == '.pastaELN_dataverse'
      assert db_api_instance.pasta_db_name == 'pastaELN'

  # Parametrized test for edge cases
  @pytest.mark.parametrize('db_info, expected_db_api_calls', [
    ({'database_path': ''}, [('/.pastaELN_dataverse.db', '/pastaELN.db')]),
  ], ids=['empty_database_path'])
  def test_database_api_create_instance_edge_cases(self, mocker, db_info, expected_db_api_calls):
    # Arrange
    mocker.patch('pasta_eln.dataverse.database_api.Path.home', return_value='')
    mocker.patch('pasta_eln.dataverse.database_api.get_encrypt_key', return_value=('', ''))
    with patch('pasta_eln.dataverse.database_api.get_db_info', return_value=db_info), \
        patch('pasta_eln.dataverse.database_api.BaseDatabaseApi') as MockBaseDatabaseApi:
      # Act
      db_api_instance = DatabaseAPI()

      # Assert
      MockBaseDatabaseApi.assert_called_once_with(*expected_db_api_calls[0])

  # Parametrized test for error cases
  @pytest.mark.parametrize('db_info, expected_exception', [
    (None, AttributeError),
    ({'database_path': None}, Error),
  ], ids=['none_db_info', 'none_database_path'])
  def test_database_api_create_instance_error_cases(self, mocker, db_info, expected_exception):
    # Arrange
    mock_home = mocker.patch('pasta_eln.dataverse.database_api.Path.home', return_value='/mock/path')
    with patch('pasta_eln.dataverse.database_api.get_db_info', return_value=db_info):
      # Act & Assert
      with pytest.raises(expected_exception):
        db_api_instance = DatabaseAPI()
        mock_home.assert_called_once()

  @pytest.mark.parametrize('data, expected_exception', [
    param(None, ValueError, id='none_data'),
    param('invalid_data', TypeError, id='invalid_data_type'),
    param(UploadModel(), None, id='valid_upload_model'),
    param(ConfigModel(), None, id='valid_config_model'),
  ], ids=lambda x: x[2])
  def test_create_model(self, database_api, data, expected_exception):
    # Act
    if expected_exception:
      with pytest.raises(expected_exception):
        database_api.create_model(data)
    else:
      result = database_api.create_model(data)

      # Assert
      assert result is not None

  @pytest.mark.parametrize('data, expected_exception', [
    param(None, ValueError, id='none_data'),
    param('invalid_data', TypeError, id='invalid_data_type'),
    param(UploadModel(), None, id='valid_upload_model'),
    param(ConfigModel(), None, id='valid_config_model'),
  ], ids=lambda x: x[2])
  def test_update_model(self, database_api, data, expected_exception):
    # Act
    if expected_exception:
      with pytest.raises(expected_exception):
        database_api.update_model(data)
    else:
      database_api.update_model(data)

  @pytest.mark.parametrize('model_type, expected_exception', [
    param(UploadModel, None, id='valid_upload_model'),
    param(ConfigModel, None, id='valid_config_model'),
    param(DataHierarchyModel, None, id='valid_data_hierarchy_model'),
    param(ProjectModel, None, id='valid_project_model'),
    param(str, TypeError, id='invalid_model_type'),
  ], ids=lambda x: x[2])
  def test_get_models(self, database_api, model_type, expected_exception):
    # Arrange
    database_api.db_api.get_models.return_value = [model_type() for _ in range(3)]
    database_api.db_api.get_project_models.return_value = [model_type() for _ in range(3)]
    # Act
    if expected_exception:
      with pytest.raises(expected_exception):
        database_api.get_models(model_type)
    else:
      result = database_api.get_models(model_type)

      # Assert
      database_api.logger.info.assert_called_once_with('Retrieving models of type: %s', model_type)
      assert isinstance(result, list)
      if isinstance(model_type(), ProjectModel):
        database_api.db_api.get_project_models.assert_called_once()
      else:
        database_api.db_api.get_models.assert_called_once_with(model_type)

  @pytest.mark.parametrize(
    'model_type, filter_term, filter_fields, order_by_column, page_number, limit, expected_exception', [
      param(UploadModel, None, None, None, 1, 10, None, id='valid_upload_model'),
      param(ConfigModel, 'term', ['field'], 'column', 2, 5, None, id='valid_config_model_with_filters'),
      param(str, None, None, None, 1, 10, TypeError, id='invalid_model_type'),
    ], ids=lambda x: x[7])
  def test_get_paginated_models(self, database_api, model_type, filter_term, filter_fields, order_by_column,
                                page_number,
                                limit, expected_exception):
    # Arrange
    database_api.db_api.get_paginated_models.return_value = [model_type() for _ in range(3)]

    # Act
    if expected_exception:
      with pytest.raises(expected_exception):
        database_api.get_paginated_models(model_type, filter_term, filter_fields, order_by_column, page_number, limit)
    else:
      result = database_api.get_paginated_models(model_type, filter_term, filter_fields, order_by_column, page_number,
                                                 limit)

      # Assert
      assert isinstance(result, list)
      database_api.logger.info.assert_called_once_with(
        'Retrieving paginated models of type: %s, filter_term: %s, bookmark: %s, limit: %s',
        model_type,
        filter_term,
        page_number,
        limit)
      database_api.db_api.get_paginated_models.assert_called_once_with(model_type, filter_term, filter_fields,
                                                                       order_by_column, page_number, limit)

  @pytest.mark.parametrize('model_type, limit, row_count, expected_value, expected_exception', [
    param(UploadModel, 10, 100, 10, None, id='valid_upload_model'),
    param(ConfigModel, 5, 0, 0, None, id='valid_config_model'),
    param(ConfigModel, 5, 19, 4, None, id='valid_config_model2'),
    param(ConfigModel, 5, 21, 5, None, id='valid_config_model3'),
    param(DataHierarchyModel, 5, 0, 0, None, id='valid_data_hierarchy_model'),
    param(str, 10, 0, 0, TypeError, id='invalid_model_type'),
  ], ids=lambda x: x[3])
  def test_get_last_page_number(self, database_api, model_type, row_count, limit, expected_value, expected_exception):
    # Arrange
    database_api.db_api.get_models_count.return_value = row_count

    # Act
    if expected_exception:
      with pytest.raises(expected_exception):
        database_api.get_last_page_number(model_type, limit)
    else:
      result = database_api.get_last_page_number(model_type, limit)

      # Assert
      assert isinstance(result, int)
      assert expected_value == result
      database_api.db_api.get_models_count.assert_called_once_with(model_type)

  @pytest.mark.parametrize('model_id, model_type, expected_exception', [
    param(1, UploadModel, None, id='valid_upload_model'),
    param('id', ConfigModel, None, id='valid_config_model'),
    param(None, UploadModel, ValueError, id='none_model_id'),
    param(1, str, TypeError, id='invalid_model_type'),
  ], ids=lambda x: x[3])
  def test_get_model(self, database_api, model_id, model_type, expected_exception):
    # Arrange
    database_api.db_api.get_model.return_value = model_type()

    # Act
    if expected_exception:
      with pytest.raises(expected_exception):
        database_api.get_model(model_id, model_type)
    else:
      result = database_api.get_model(model_id, model_type)

      # Assert
      database_api.logger.info.assert_called_once_with('Retrieving model with id: %s, type: %s', model_id, model_type)
      assert result is not None
      assert isinstance(result, model_type)
      database_api.db_api.get_model.assert_called_once_with(model_id, model_type)

  @pytest.mark.parametrize(
    'config_model, encrypt_key, expected_api_token, expected_log_calls',
    [
      # Happy path with encryption key
      param(ConfigModel(_id=123, dataverse_login_info={'api_token': 'encrypted_token'}), 'key', 'decrypted_token', 1,
            id='success_path_with_key'),

      # Happy path without encryption key
      param(ConfigModel(_id=123, dataverse_login_info={'api_token': 'encrypted_token'}), None, None, 2,
            id='success_path_without_key'),

      # Edge case: config_model is None
      param(None, 'key', None, 1, id='config_model_none'),

      # Error case: api_token is None
      param(ConfigModel(_id=123, dataverse_login_info={'api_token': None}), 'key', None, 1, id='api_token_none'),
    ],
    ids=lambda x: x[-1]
  )
  def test_get_config_model(self, mocker, database_api, config_model, encrypt_key, expected_api_token,
                            expected_log_calls):
    # Arrange
    database_api.get_model = mocker.MagicMock()
    database_api.get_model.return_value = config_model
    database_api.encrypt_key = encrypt_key
    with patch('pasta_eln.dataverse.utils.decrypt_data', return_value='decrypted_token') as mock_decrypt:
      # Act
      result = database_api.get_config_model()

      # Assert
      if config_model is None or not isinstance(config_model, ConfigModel):
        database_api.logger.error.assert_called_once_with('Fatal error, Failed to load config model!')
        assert result is None
      elif not isinstance(config_model.dataverse_login_info, dict):
        database_api.logger.error.assert_called_once_with('Fatal Error, Invalid dataverse login info!')
        assert result is None
      else:
        if encrypt_key and config_model.dataverse_login_info.get('api_token'):
          mock_decrypt.assert_called_once_with(database_api.logger, encrypt_key, 'encrypted_token')
          assert result.dataverse_login_info['api_token'] == expected_api_token
        elif not encrypt_key and config_model.dataverse_login_info.get('api_token'):
          database_api.logger.warning.assert_called_once_with(
            'No encryption key found. Hence if any API key exists, it will be removed and the user needs to re-enter it.')
          assert result.dataverse_login_info['api_token'] is None
          assert result.dataverse_login_info['dataverse_id'] is None
          database_api.update_model.assert_called_once_with(config_model)
        assert database_api.logger.info.call_count == expected_log_calls

  @pytest.mark.parametrize(
    'config_model, expected_log, expected_update_call, expected_exception',
    [
      # Happy path with valid data
      pytest.param(
        ConfigModel(_id=123, dataverse_login_info={'api_token': 'token123', 'server_url': 'http://example.com/'}),
        'Saving config model...',
        True,
        None,
        id='happy_path_valid_data'
      ),
      # Edge case: config_model is None
      pytest.param(
        None,
        'Invalid config model!',
        False,
        None,
        id='edge_case_none_config_model'
      ),
      # Edge case: config_model is not an instance of ConfigModel
      pytest.param(
        'not_a_config_model',
        'Invalid config model!',
        False,
        None,
        id='edge_case_invalid_instance'
      ),
      # Error case: No encryption key
      pytest.param(
        ConfigModel(_id=123, dataverse_login_info={'api_token': 'token123', 'server_url': 'http://example.com/'}),
        'Fatal Error, No encryption key found! Make sure to initialize the database!',
        False,
        ValueError,
        id='error_case_no_encryption_key'
      ),
    ],
    ids=lambda x: x[-1]
  )
  def test_save_config_model(self, mocker, database_api, config_model, expected_log, expected_update_call,
                             expected_exception):
    # Arrange
    database_api.update_model = mocker.MagicMock()
    if config_model is not None and isinstance(config_model, ConfigModel):
      database_api.encrypt_key = 'test_key' if expected_update_call else None

    # Act
    if expected_exception:
      with pytest.raises(expected_exception):
        database_api.save_config_model(config_model)
        database_api.logger.error.assert_any_call(expected_log)
    else:
      database_api.save_config_model(config_model)

      # Assert
      if expected_update_call:
        database_api.update_model.assert_called_once_with(config_model)
        database_api.logger.info.assert_any_call(expected_log)
      else:
        database_api.update_model.assert_not_called()
        database_api.logger.error.assert_any_call(expected_log)

  @pytest.mark.parametrize(
    'mock_results, log_warning_called',
    [
      # Happy path with multiple models
      param([DataHierarchyModel(), DataHierarchyModel()], False, id='multiple_models'),
      # Happy path with a single model
      param([DataHierarchyModel()], False, id='single_model'),
      # Edge case with an empty list
      param([], True, id='empty_list'),
      # Error case with None returned
      param(None, True, id='none_returned'),
    ],
    ids=lambda x: x[-1]  # Use test_id for pytest's test case ID
  )
  def test_get_data_hierarchy_models(self, database_api, mock_results, log_warning_called):
    # Arrange
    database_api.db_api.get_models.return_value = mock_results

    # Act
    result = database_api.get_data_hierarchy_models()

    # Assert
    assert result == mock_results
    if log_warning_called:
      database_api.logger.warning.assert_called_once_with('Data hierarchy items not found!')
    else:
      database_api.logger.warning.assert_not_called()
    database_api.logger.info.assert_called_once_with('Retrieving data hierarchy...')

  @pytest.mark.parametrize(
    'config_model_id, model_return_value, expected_initialize_called',
    [
      param('valid_id', None, True, id='happy_path_initialize_config'),
      param('valid_id', ConfigModel(), False, id='happy_path_no_initialize_needed'),
      param('edge_case_empty_id', None, True, id='edge_case_empty_id'),
      param('edge_case_none_id', None, True, id='edge_case_none_id'),
      param('error_case_invalid_model', Exception('DB Error'), False, id='error_case_db_exception'),
    ],
    ids=lambda x: x[-1]
  )
  def test_initialize_database(self, mocker, database_api, config_model_id, model_return_value,
                               expected_initialize_called):
    # Arrange
    database_api.config_model_id = config_model_id
    database_api.db_api.get_model.return_value = model_return_value
    database_api.db_api.create_and_init_database = mocker.MagicMock()
    database_api.initialize_config_document = mocker.MagicMock()

    # Act
    database_api.initialize_database()

    # Assert
    database_api.logger.info.assert_called_once_with('Initializing database for dataverse module...')
    database_api.db_api.create_and_init_database.assert_called_once()
    database_api.db_api.get_model.assert_called_once_with(config_model_id, ConfigModel)
    if expected_initialize_called:
      database_api.initialize_config_document.assert_called_once()
    else:
      database_api.initialize_config_document.assert_not_called()

    # Assert
    # No exception should be raised

  @pytest.mark.parametrize(
    'mock_metadata, expected_project_upload_items',
    [
      # Happy path with valid metadata
      param({'key': 'value'}, {'type1': True, 'type2': True}, id='happy_path_valid_metadata'),
      # Edge case with empty metadata
      param({}, {'type1': True, 'type2': True}, id='edge_case_empty_metadata'),
    ],
    ids=lambda x: x[-1]
  )
  def test_initialize_config_document_happy_path(self, mocker, database_api, mock_metadata,
                                                 expected_project_upload_items):
    # Arrange
    mocker.patch('pasta_eln.dataverse.database_api.realpath', return_value='mock_path')
    mock_get_data_hierarchy_types = mocker.patch('pasta_eln.dataverse.database_api.get_data_hierarchy_types',
                                                 return_value=expected_project_upload_items)
    mocker.patch('pasta_eln.dataverse.database_api.set_template_values')
    mocker.patch('pasta_eln.dataverse.database_api.set_authors')
    mocker.patch('pasta_eln.dataverse.database_api.load', return_value=mock_metadata)
    database_api.get_data_hierarchy_models = mocker.MagicMock()
    database_api.create_model = mocker.MagicMock()
    with patch('pasta_eln.dataverse.database_api.open', new_callable=mocker.MagicMock) as mock_open:
      mock_open.return_value.__enter__.return_value.read.return_value = mock_metadata

      # Act
      database_api.initialize_config_document()

      # Assert
      database_api.logger.info.assert_called_once_with('Initializing and saving the config model...')
      database_api.create_model.assert_called_once()
      created_model = database_api.create_model.call_args[0][0]
      assert created_model.project_upload_items == expected_project_upload_items
      assert created_model.metadata == mock_metadata
      mock_get_data_hierarchy_types.assert_called_once_with(database_api.get_data_hierarchy_models.return_value)
