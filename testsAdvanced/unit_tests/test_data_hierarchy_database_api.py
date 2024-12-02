#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_database_api.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from unittest.mock import MagicMock, patch

import pytest
from _pytest.mark import param

from pasta_eln.GUI.data_hierarchy.data_hierarchy_document_adapter import DataHierarchyDocumentAdapter
from pasta_eln.GUI.data_hierarchy.database_api import DatabaseAPI
from pasta_eln.database.error import Error
from pasta_eln.database.models.data_hierarchy_model import DataHierarchyModel


@pytest.fixture
def mock_database_api(mocker):
  mocker.patch('pasta_eln.GUI.data_hierarchy.database_api.logging.getLogger')
  mocker.patch('pasta_eln.GUI.data_hierarchy.database_api.get_db_info', return_value={"database_path": "/mock/path"})
  mocker.patch('pasta_eln.GUI.data_hierarchy.database_api.BaseDatabaseApi')
  return DatabaseAPI()


class TestDataHierarchyDatabaseApi:

  @pytest.mark.parametrize(
    "db_info, expected_db_path, expected_exception",
    [
      # Happy path test cases
      ({"database_path": "/valid/path"}, "/valid/path/pastaELN.db", None),

      # Edge case: empty database path
      ({"database_path": ""}, "/pastaELN.db", None),

      # Error case: None database path
      ({"database_path": None}, None, Error),
    ],
    ids=[
      "valid_path",
      "empty_path",
      "none_path",
    ]
  )
  def test_database_api_init(self, db_info, expected_db_path, expected_exception):
    # Arrange
    with patch('pasta_eln.GUI.data_hierarchy.database_api.get_db_info', return_value=db_info) as mock_get_db_info:
      with patch('pasta_eln.GUI.data_hierarchy.database_api.BaseDatabaseApi') as mock_base_database_api:
        mock_logger = MagicMock(spec=logging.Logger)
        with patch('pasta_eln.GUI.data_hierarchy.database_api.log_and_create_error',
                   return_value=Error("Mock exception")) as mock_log_and_create_error:

          # Act
          if expected_exception:
            with pytest.raises(expected_exception):
              db_api_instance = DatabaseAPI()
              # Assert
              mock_log_and_create_error.assert_called_once_with(mock_logger, Error, "Database path is None!")
          else:
            db_api_instance = DatabaseAPI()
            # Assert
            mock_base_database_api.assert_called_once_with(expected_db_path)
            mock_get_db_info.assert_called_once_with(db_api_instance.logger)
            mock_log_and_create_error.assert_not_called()
            assert db_api_instance.db_api is mock_base_database_api.return_value
            assert db_api_instance.config_model_id == 1
            assert db_api_instance.pasta_db_name == "pastaELN"

  @pytest.mark.parametrize(
    "data, expected, exception",
    [
      # Happy path tests
      param(DataHierarchyModel(), DataHierarchyModel(), None, id="happy_path_valid_data"),

      # Edge cases
      param(None, None, ValueError, id="edge_case_none_data"),

      # Error cases
      param("invalid_data", None, TypeError, id="error_case_invalid_type"),
    ],
    ids=lambda x: x[-1]
  )
  def test_create_data_hierarchy_model(self, mock_database_api, data, expected, exception):
    # Arrange
    mock_database_api.db_api.insert_data_hierarchy_model = MagicMock(return_value=expected)
    # Act
    if exception:
      with patch('pasta_eln.GUI.data_hierarchy.database_api.log_and_create_error',
                 return_value=exception("Test exception")) as mock_log_and_create_error:
        with pytest.raises(exception):
          mock_database_api.create_data_hierarchy_model(data)
        # Assert
        mock_log_and_create_error.assert_called_once()
    else:
      result = mock_database_api.create_data_hierarchy_model(data)
      # Assert
      assert result == expected

  @pytest.mark.parametrize(
    "data_models, expected_call_count",
    [
      # Happy path with a single model
      pytest.param([MagicMock(spec=DataHierarchyModel)], 1, id="single_model"),
      # Happy path with multiple models
      pytest.param([MagicMock(spec=DataHierarchyModel) for _ in range(5)], 5, id="multiple_models"),
      # Edge case with an empty list
      pytest.param([], 0, id="empty_list"),
    ]
  )
  def test_update_data_hierarchy_models_success_path(self, mock_database_api, data_models, expected_call_count):
    # Arrange
    mock_database_api.update_data_hierarchy_model = MagicMock()

    # Act
    mock_database_api.update_data_hierarchy_models(data_models)

    # Assert
    assert mock_database_api.update_data_hierarchy_model.call_count == expected_call_count
    mock_database_api.logger.info.assert_called_once_with("Updating data hierarchy models...")

    for data_model in data_models:
      mock_database_api.update_data_hierarchy_model.assert_any_call(data_model)

  @pytest.mark.parametrize(
    "data_models, expected_exception",
    [
      # Error case with None as input
      pytest.param(None, TypeError, id="none_input"),
      # Error case with invalid type in list
      pytest.param([None], ValueError, id="invalid_type_in_list"),
    ]
  )
  def test_update_data_hierarchy_models_error_cases(self, mock_database_api, data_models, expected_exception):
    # Act & Assert
    with pytest.raises(expected_exception):
      mock_database_api.update_data_hierarchy_models(data_models)

  @pytest.mark.parametrize("data, expected_exception, expected_message", [
    (None, ValueError, "Data cannot be None!"),  # Error case: None data
    ("not_a_model", TypeError, "Data must be an DataHierarchyModel!"),  # Error case: Incorrect type
  ], ids=["none_data", "incorrect_type"])
  def test_update_data_hierarchy_model_errors(self, mock_database_api, data, expected_exception, expected_message):

    # Act & Assert
    with patch('pasta_eln.dataverse.utils.log_and_create_error') as mock_log_and_create_error:
      mock_log_and_create_error.side_effect = expected_exception(expected_message)
      with pytest.raises(expected_exception) as excinfo:
        mock_database_api.update_data_hierarchy_model(data)
      assert str(excinfo.value) == expected_message

  @pytest.mark.parametrize("data", [
    (DataHierarchyModel()),  # Happy path: Valid DataHierarchyModel
  ], ids=["valid_data"])
  def test_update_data_hierarchy_model_success_path(self, mock_database_api, data):
    # Act
    with patch.object(mock_database_api.db_api, 'update_data_hierarchy_model', return_value=None) as mock_update:
      mock_database_api.update_data_hierarchy_model(data)

    # Assert
    mock_update.assert_called_once_with(data)
    mock_database_api.logger.info.assert_called_once_with('Updating data_hierarchy_model: %s', data)

  @pytest.mark.parametrize(
    "mock_return_value, expected_result",
    [
      # Happy path tests
      param([DataHierarchyModel()], [DataHierarchyModel()], id="single_model"),
      param([DataHierarchyModel(), DataHierarchyModel()], [DataHierarchyModel(), DataHierarchyModel()],
            id="multiple_models"),

      # Edge cases
      param([], [], id="empty_list"),

      # Error cases
      param(None, None, id="none_return_value"),
    ],
    ids=lambda x: x[2]
  )
  def test_get_data_hierarchy_models(self, mock_database_api, mock_return_value, expected_result):
    # Arrange
    mock_database_api.db_api.get_data_hierarchy_models = MagicMock(return_value=expected_result)

    # Act
    result = mock_database_api.get_data_hierarchy_models()

    # Assert
    assert result == expected_result
    mock_database_api.logger.info.assert_called_once_with("Retrieving data_hierarchy_models")
    mock_database_api.db_api.get_data_hierarchy_models.assert_called_once()

  # Happy path tests
  @pytest.mark.parametrize("model_doc_type, expected", [
    ("valid_id_1", DataHierarchyModel()),
    ("valid_id_2", DataHierarchyModel()),
  ], ids=["valid_id_1", "valid_id_2"])
  def test_get_data_hierarchy_model_happy_path(self, mock_database_api, model_doc_type, expected):
    # Arrange
    mock_database_api.db_api.get_data_hierarchy_model = MagicMock(return_value=expected)

    # Act
    result = mock_database_api.get_data_hierarchy_model(model_doc_type)

    # Assert
    assert result == expected
    mock_database_api.logger.info.assert_called_once_with("Retrieving data_hierarchy_model with id: %s", model_doc_type)
    mock_database_api.db_api.get_data_hierarchy_model.assert_called_once_with(model_doc_type)

  # Edge case tests
  @pytest.mark.parametrize("model_doc_type", [
    (""),
    (" " * 1000),
  ], ids=["empty_string", "long_whitespace_string"])
  def test_get_data_hierarchy_model_edge_cases(self, mock_database_api, model_doc_type):
    # Arrange
    mock_database_api.db_api.get_data_hierarchy_model = MagicMock(return_value=MagicMock(spec=DataHierarchyModel))

    # Act
    result = mock_database_api.get_data_hierarchy_model(model_doc_type)

    # Assert
    assert isinstance(result, DataHierarchyModel)
    mock_database_api.logger.info.assert_called_once_with("Retrieving data_hierarchy_model with id: %s", model_doc_type)
    mock_database_api.db_api.get_data_hierarchy_model.assert_called_once_with(model_doc_type)

  # Error case tests
  @pytest.mark.parametrize("model_doc_type", [
    (None),
  ], ids=["none_model_doc_type"])
  def test_get_data_hierarchy_model_error_cases(self, mock_database_api, model_doc_type):
    # Act & Assert
    with pytest.raises(ValueError, match="model_id cannot be None"):
      mock_database_api.get_data_hierarchy_model(model_doc_type)
    mock_database_api.db_api.get_data_hierarchy_model.assert_not_called()
    mock_database_api.logger.error.assert_called_once()  # Assuming log_and_create_error logs an error

  @pytest.mark.parametrize(
    "logger_info_call_count, db_api_call_count, expected_logger_call, expected_db_api_call",
    [
      # Happy path test case
      (1, 1, "Initializing database for data-hierarchy module...", True),
    ],
    ids=[
      "happy_path",
    ]
  )
  def test_initialize_database(self, mock_database_api,
                               logger_info_call_count,
                               db_api_call_count,
                               expected_logger_call,
                               expected_db_api_call):
    # Act
    mock_database_api.initialize_database()

    # Assert
    if expected_logger_call:
      mock_database_api.logger.info.assert_called_once_with(expected_logger_call)
    else:
      assert mock_database_api.logger.info.call_count == logger_info_call_count

    if expected_db_api_call:
      mock_database_api.db_api.create_and_bind_db_tables.assert_called_once()
    else:
      assert mock_database_api.db_api.create_and_bind_db_tables.call_count == db_api_call_count

  # Parametrized test for happy path, edge cases, and error cases
  @pytest.mark.parametrize(
    "mock_models, expected_document, description",
    [
      # Happy path with a single model
      param([{"id": 1, "name": "Model1"}], {"id": 1, "name": "Model1"}, "single model", id="single model"),

      # Happy path with multiple models
      param([{"id": 1, "name": "Model1"}, {"id": 2, "name": "Model2"}],
            {"id": 1, "name": "Model1", "id": 2, "name": "Model2"}, "multiple models", id="multiple models"),

      # Edge case with empty model list
      param([], {}, "empty model list", id="empty model list"),

      # Error case with invalid model data
      param([{"invalid": "data"}], {'invalid': 'data'}, "invalid model data", id="invalid model data"),
    ],
    ids=lambda x: x[2]
  )
  def test_get_data_hierarchy_document(self, mock_database_api, mock_models, expected_document, description):
    # Arrange
    mock_database_api.get_data_hierarchy_models = MagicMock()
    mock_database_api.get_data_hierarchy_models.return_value = mock_models

    # Patch the DataHierarchyDocumentAdapter to return the model as is
    with patch.object(DataHierarchyDocumentAdapter, 'to_data_hierarchy_document', side_effect=lambda x: x):
      # Act
      result = mock_database_api.get_data_hierarchy_document()

      # Assert
      assert result == expected_document
      mock_database_api.logger.info.assert_called_once_with("Retrieving data hierarchy document...")

  @pytest.mark.parametrize(
    "data_hierarchy_document, existing_models, expected_update_calls, expected_create_calls",
    [
      # Happy path: model exists
      pytest.param(
        {"models": [MagicMock(doc_type="type1")]},
        {"type1": True},
        1,
        0,
        id="happy_path_existing_model"
      ),
      # Happy path: model does not exist
      pytest.param(
        {"models": [MagicMock(doc_type="type2")]},
        {"type2": False},
        0,
        1,
        id="happy_path_new_model"
      ),
      # Edge case: empty document
      pytest.param(
        {"models": []},
        {},
        0,
        0,
        id="edge_case_empty_document"
      ),
      # Error case: invalid model type
      pytest.param(
        {"models": [MagicMock(doc_type=None)]},
        {None: False},
        0,
        1,
        id="error_case_invalid_model_type"
      ),
    ]
  )
  def test_save_data_hierarchy_document(self,
                                        mock_database_api, data_hierarchy_document, existing_models,
                                        expected_update_calls, expected_create_calls
                                        ):
    # Patch the DataHierarchyDocumentAdapter to use the mock
    mock_database_api.update_data_hierarchy_model = MagicMock()
    mock_database_api.create_data_hierarchy_model = MagicMock()
    with patch(
        'pasta_eln.GUI.data_hierarchy.database_api.DataHierarchyDocumentAdapter') as mock_data_hierarchy_document_adapter:
      mock_data_hierarchy_document_adapter.to_data_hierarchy_model_list.return_value = data_hierarchy_document.get(
        "models", [])
      # Arrange
      for model_type, exists in existing_models.items():
        mock_database_api.db_api.check_if_data_hierarchy_model_exists.return_value = exists

      # Act
      mock_database_api.save_data_hierarchy_document(data_hierarchy_document)

      # Assert
      assert mock_database_api.update_data_hierarchy_model.call_count == expected_update_calls
      assert mock_database_api.create_data_hierarchy_model.call_count == expected_create_calls
