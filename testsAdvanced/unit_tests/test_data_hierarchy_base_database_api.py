#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_base_database_api.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from unittest.mock import MagicMock, patch

import pytest
from _pytest.mark import param
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from pasta_eln.GUI.data_hierarchy.base_database_api import BaseDatabaseApi
from pasta_eln.database.error import Error
from pasta_eln.database.incorrect_parameter_error import IncorrectParameterError
from pasta_eln.database.models.data_hierarchy_definition_orm_model import DataHierarchyDefinitionOrmModel
from pasta_eln.database.models.data_hierarchy_model import DataHierarchyModel
from pasta_eln.database.models.data_hierarchy_orm_model import DataHierarchyOrmModel
from pasta_eln.database.models.orm_model_base import OrmModelBase
from pasta_eln.database.orm_model_adapter import OrmModelAdapter


@pytest.fixture
def mock_base_database_api(mocker):
  mocker.patch('pasta_eln.dataverse.base_database_api.logging.getLogger')
  return BaseDatabaseApi('test_path')


class TestDataHierarchyBaseDatabaseApi:

  @pytest.mark.parametrize(
    'pasta_project_group_db_path, expected_db_url',
    [
      # Happy path tests
      ('valid_path.db', 'sqlite:///valid_path.db'),
      ('another_valid_path.db', 'sqlite:///another_valid_path.db'),
      ('/absolute/path/to/db.db', 'sqlite:////absolute/path/to/db.db'),
    ],
    ids=[
      'valid_relative_path',
      'another_valid_relative_path',
      'valid_absolute_path',
    ]
  )
  def test_init_happy_path(self, mocker, pasta_project_group_db_path, expected_db_url):
    # Arrange
    mock_get_logger = mocker.patch('pasta_eln.dataverse.base_database_api.logging.getLogger')

    # Act
    instance = BaseDatabaseApi(pasta_project_group_db_path)

    # Assert
    assert instance.db_url == expected_db_url
    mock_get_logger.assert_called_once_with('sqlalchemy.engine')
    instance.logger.setLevel.assert_called_once_with(logging.INFO)

  @pytest.mark.parametrize(
    'pasta_project_group_db_path, expected_db_url',
    [
      # Edge cases
      ('', 'sqlite:///'),  # Empty string path
      ('   ', 'sqlite:///   '),  # String with spaces
    ],
    ids=[
      'empty_string_path',
      'spaces_in_path',
    ]
  )
  def test_init_edge_cases(self, pasta_project_group_db_path, expected_db_url):

    # Act
    instance = BaseDatabaseApi(pasta_project_group_db_path)

    # Assert
    assert instance.db_url == expected_db_url

  @pytest.mark.parametrize(
    'pasta_project_group_db_path, expected_error_message',
    [
      # Error cases
      (None, 'Database path must be a string: None'),
      (123, 'Database path must be a string: 123'),
      ([], 'Database path must be a string: []'),
      ({}, 'Database path must be a string: {}'),
    ],
    ids=[
      'none_as_path',
      'integer_as_path',
      'list_as_path',
      'dict_as_path',
    ]
  )
  def test_init_error_cases(self, pasta_project_group_db_path, expected_error_message):
    # Act and Assert
    with pytest.raises(IncorrectParameterError) as exc_info:
      BaseDatabaseApi(pasta_project_group_db_path)

    assert str(exc_info.value) == expected_error_message

  @pytest.mark.parametrize(
    'db_url, expected_exception',
    [
      # Happy path test cases
      param('sqlite:///:memory:', None, id='success_path_in_memory'),
      param('postgresql://user:password@localhost/testdb', None, id='success_path_postgresql'),
    ],
    ids=lambda x: x[2]
  )
  def test_create_and_bind_db_tables(self, mocker, mock_base_database_api, db_url, expected_exception):
    # Arrange
    mock_base_database_api.db_url = db_url
    mock_engine = mocker.MagicMock()
    mock_create_engine = mocker.patch('pasta_eln.GUI.data_hierarchy.base_database_api.create_engine',
                                      return_value=mock_engine)
    mock_orm_model_base_metadata = mocker.patch.object(OrmModelBase, 'metadata')

    # Act
    if expected_exception:
      with pytest.raises(expected_exception):
        mock_base_database_api.create_and_bind_db_tables()
    else:
      mock_base_database_api.create_and_bind_db_tables()

    # Assert
    mock_base_database_api.logger.info.assert_called_once_with('Creating and binding table for db : %s', db_url)
    if not expected_exception:
      mock_create_engine.assert_called_once_with(db_url)
      mock_orm_model_base_metadata.tables[DataHierarchyOrmModel.__tablename__].create.assert_any_call(
        bind=mock_engine, checkfirst=True
      )
      mock_orm_model_base_metadata.tables[DataHierarchyDefinitionOrmModel.__tablename__].create.assert_any_call(
        bind=mock_engine, checkfirst=True
      )

  @pytest.mark.parametrize(
    'model_doc_type, db_model, expected_result',
    [
      param(1, MagicMock(spec=DataHierarchyOrmModel), MagicMock(spec=DataHierarchyModel), id='valid_int_id'),
      param('doc_type', MagicMock(spec=DataHierarchyOrmModel), MagicMock(spec=DataHierarchyModel), id='valid_str_id'),
      param(None, None, pytest.raises(Error), id='none_doc_type'),
      param('', None, pytest.raises(Error), id='empty_string_doc_type'),
      param(999, None, None, id='non_existent_int_id'),
      param('non_existent', None, None, id='non_existent_str_id'),
    ],
    ids=lambda x: x[-1]
  )
  def test_get_data_hierarchy_model(self, mock_base_database_api, model_doc_type, db_model, expected_result):
    # Arrange
    with patch('pasta_eln.GUI.data_hierarchy.base_database_api.create_engine') as mock_create_engine, \
        patch('pasta_eln.GUI.data_hierarchy.base_database_api.Session') as mock_session, \
        patch.object(OrmModelAdapter, 'get_data_hierarchy_model') as mock_get_data_hierarchy_model, \
        patch('pasta_eln.GUI.data_hierarchy.base_database_api.log_and_create_error',
              return_value=Error('Mock exception')) as mock_log_and_create_error:

      mock_engine = MagicMock()
      mock_create_engine.return_value = mock_engine
      mock_session_instance = MagicMock(spec=Session)
      mock_session.return_value.__enter__.return_value = mock_session_instance
      mock_session_instance.get.return_value = db_model
      mock_get_data_hierarchy_model.return_value = None if isinstance(expected_result, type(
        pytest.raises(Error))) else expected_result

      # Act
      if isinstance(expected_result, type(pytest.raises(Error))):
        with expected_result:
          result = mock_base_database_api.get_data_hierarchy_model(model_doc_type)
      else:
        result = mock_base_database_api.get_data_hierarchy_model(model_doc_type)

      # Assert
      if not isinstance(expected_result, type(pytest.raises(Error))):
        assert result == expected_result
      else:
        mock_log_and_create_error.assert_called_once_with(mock_base_database_api.logger, Error,
                                                          'Model Doc Type cannot be empty!')

  @pytest.mark.parametrize(
    'orm_models, expected_models',
    [
      # Happy path with multiple models
      param([MagicMock(), MagicMock()], [MagicMock(), MagicMock()], id='multiple_models'),
      # Happy path with a single model
      param([MagicMock()], [MagicMock()], id='single_model'),
      # Edge case with no models
      param([], [], id='no_models'),
    ],
    ids=lambda x: x[2]
  )
  def test_get_data_hierarchy_models_success_path(self, mocker, mock_base_database_api, orm_models,
                                                  expected_models):
    # Arrange
    mock_get_data_hierarchy_model = mocker.patch.object(OrmModelAdapter, 'get_data_hierarchy_model')
    mock_session = mocker.patch('pasta_eln.GUI.data_hierarchy.base_database_api.Session')
    mock_session.return_value.__enter__.return_value.scalars.return_value.all.return_value = orm_models
    mock_get_data_hierarchy_model.side_effect = expected_models
    mock_base_database_api.db_url = 'sqlite:///:memory:'

    # Act
    result = mock_base_database_api.get_data_hierarchy_models()

    # Assert
    assert result == expected_models
    mock_base_database_api.logger.info.assert_called_once_with('Retrieving data_hierarchy_models from database')

  @pytest.mark.parametrize(
    'exception',
    [
      # Error case with SQLAlchemyError
      param(SQLAlchemyError, id='sqlalchemy_error'),
    ],
    ids=lambda x: x[1]
  )
  def test_get_data_hierarchy_models_error_cases(self, mocker, mock_base_database_api, exception):
    # Arrange
    mock_session = mocker.patch('pasta_eln.GUI.data_hierarchy.base_database_api.Session')
    mock_session.return_value.__enter__.side_effect = exception
    api_instance = MagicMock()
    mock_base_database_api.db_url = 'sqlite:///:memory:'

    # Act & Assert
    with pytest.raises(exception):
      mock_base_database_api.get_data_hierarchy_models()
    mock_base_database_api.logger.info.assert_called_once_with('Retrieving data_hierarchy_models from database')

  @pytest.mark.parametrize('data_model, expected_result', [
    param(MagicMock(spec=DataHierarchyModel), MagicMock(spec=DataHierarchyModel), id='success_path'),
    param(None, None, id='edge_case_none_data_model'),
    param(MagicMock(spec=DataHierarchyModel, invalid_attr=True), None, id='error_case_invalid_data_model'),
  ], ids=lambda x: x[2])
  def test_insert_data_hierarchy_model(self, mocker, mock_base_database_api, data_model, expected_result):
    # Arrange
    mock_get_data_hierarchy_model = mocker.patch.object(OrmModelAdapter, 'get_data_hierarchy_model')
    mock_get_orm_data_hierarchy_model = mocker.patch.object(OrmModelAdapter, 'get_orm_data_hierarchy_model')
    mocker.patch('pasta_eln.GUI.data_hierarchy.base_database_api.Session')
    mock_get_data_hierarchy_model.return_value = expected_result

    if data_model is None:
      mock_base_database_api.logger.info = MagicMock(side_effect=TypeError('Data model is None'))

    # Act
    if data_model is not None:
      result = mock_base_database_api.insert_data_hierarchy_model(data_model)
    else:
      with pytest.raises(TypeError):
        result = mock_base_database_api.insert_data_hierarchy_model(data_model)

    # Assert
    if data_model is not None:
      assert result == expected_result
      mock_base_database_api.logger.info.assert_called_once()
      mock_get_data_hierarchy_model.assert_called_once_with(mock_get_orm_data_hierarchy_model.return_value)
      mock_get_orm_data_hierarchy_model.assert_called_once_with(data_model)
    else:
      mock_base_database_api.logger.info.assert_called_once_with(
        'Populating DataHierarchyModel with data: %s in database: %s',
        data_model, mock_base_database_api.db_url)

  @pytest.mark.parametrize('exception', [
    param(SQLAlchemyError, id='error_case_sqlalchemy_exception'),
  ], ids=lambda x: x[1])
  def test_insert_data_hierarchy_model_exceptions(self, mocker, mock_base_database_api, exception):
    # Arrange
    mocker.patch.object(OrmModelAdapter, 'get_data_hierarchy_model')
    mocker.patch.object(OrmModelAdapter, 'get_orm_data_hierarchy_model')
    mock_session = mocker.patch('pasta_eln.GUI.data_hierarchy.base_database_api.Session')
    mock_session.return_value.__enter__.return_value.commit.side_effect = exception
    mock_data_model = MagicMock(spec=DataHierarchyModel)

    # Act
    with pytest.raises(exception):
      mock_base_database_api.insert_data_hierarchy_model(mock_data_model)

    # Assert
    mock_base_database_api.logger.info.assert_called_once_with(
      'Populating DataHierarchyModel with data: %s in database: %s',
      mock_data_model, mock_base_database_api.db_url)

  @pytest.mark.parametrize('data_model, db_exists, expected_exception, test_id', [
    # Happy path test cases
    (DataHierarchyModel(doc_type='doc1'), True, None, 'happy_path_existing_model'),
    (DataHierarchyModel(doc_type='doc2'), True, None, 'happy_path_existing_model_2'),

    # Edge case: doc_type is empty
    (DataHierarchyModel(doc_type=''), False, Error, 'edge_case_empty_doc_type'),

    # Error case: model does not exist in database
    (DataHierarchyModel(doc_type='nonexistent'), False, Error, 'error_case_nonexistent_model'),
  ])
  def test_update_data_hierarchy_model(self, mocker, mock_base_database_api, data_model, db_exists,
                                       expected_exception, test_id):
    # Arrange
    mock_base_database_api.db_url = 'sqlite:///:memory:'
    mock_session = mocker.patch('pasta_eln.GUI.data_hierarchy.base_database_api.Session')
    mock_session.return_value.__enter__.return_value.get.return_value = db_exists
    mock_log_and_create_error = mocker.patch('pasta_eln.GUI.data_hierarchy.base_database_api.log_and_create_error',
                                             side_effect=expected_exception(
                                               'Test exception') if expected_exception else None)

    # Act
    if expected_exception:
      with pytest.raises(expected_exception):
        mock_base_database_api.update_data_hierarchy_model(data_model)
    else:
      mock_base_database_api.update_data_hierarchy_model(data_model)

    # Assert
    if not data_model.doc_type:
      mock_log_and_create_error.assert_called_once_with(mock_base_database_api.logger, Error,
                                                        'Model doc_type cannot be empty!')
    elif not db_exists:
      mock_log_and_create_error.assert_called_once_with(mock_base_database_api.logger, Error,
                                                        'Model does not exist in database!')
    else:
      mock_session.return_value.__enter__.return_value.merge.assert_called_once()
      mock_session.return_value.__enter__.return_value.commit.assert_called_once()

  @pytest.mark.parametrize(
    'model_doc_type, expected_result',
    [
      ('valid_doc_type_1', True),
      ('valid_doc_type_2', True),
    ],
    ids=['valid_doc_type_1', 'valid_doc_type_2']
  )
  def test_check_if_data_hierarchy_model_exists_happy_path(self, mocker, mock_base_database_api, model_doc_type,
                                                           expected_result):
    # Arrange
    mock_session = mocker.patch('pasta_eln.GUI.data_hierarchy.base_database_api.Session')
    mock_session.return_value.__enter__.return_value.get.return_value = mocker.MagicMock(spec=DataHierarchyOrmModel)

    # Act
    result = mock_base_database_api.check_if_data_hierarchy_model_exists(model_doc_type)

    # Assert
    assert result == expected_result
    mock_base_database_api.logger.info.assert_called_once_with('Retrieving data_hierarchy_model with doctype: %s',
                                                               model_doc_type)

  @pytest.mark.parametrize(
    'model_doc_type, expected_result',
    [
      ('', pytest.raises(Error)),
      (None, pytest.raises(Error)),
    ],
    ids=['empty_doc_type', 'none_doc_type']
  )
  def test_check_if_data_hierarchy_model_exists_error_cases(self, mocker, mock_base_database_api, model_doc_type,
                                                            expected_result):
    # Act & Assert
    with expected_result:
      mock_base_database_api.check_if_data_hierarchy_model_exists(model_doc_type)
    mock_base_database_api.logger.info.assert_called_once_with('Retrieving data_hierarchy_model with doctype: %s',
                                                               model_doc_type)
    mock_base_database_api.logger.error.assert_called_once()

  @pytest.mark.parametrize(
    'model_doc_type, mock_return_value, expected_result',
    [
      ('non_existent_doc_type', None, False),
      ('unexpected_type_doc_type', 'unexpected_type', False),
    ],
    ids=['non_existent_doc_type', 'unexpected_type_doc_type']
  )
  def test_check_if_data_hierarchy_model_exists_edge_cases(self, mocker, mock_base_database_api, model_doc_type,
                                                           mock_return_value, expected_result):
    # Arrange
    mock_session = mocker.patch('pasta_eln.GUI.data_hierarchy.base_database_api.Session')
    mock_session.return_value.__enter__.return_value.get.return_value = mock_return_value

    # Act
    result = mock_base_database_api.check_if_data_hierarchy_model_exists(model_doc_type)

    # Assert
    assert result == expected_result
    mock_base_database_api.logger.info.assert_called_once_with('Retrieving data_hierarchy_model with doctype: %s',
                                                               model_doc_type)
