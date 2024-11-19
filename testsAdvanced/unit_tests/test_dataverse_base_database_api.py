#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_base_database_api.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from unittest.mock import MagicMock, patch

import pytest
from _pytest.mark import param
from sqlalchemy.exc import SQLAlchemyError

from pasta_eln.dataverse.base_database_api import BaseDatabaseApi
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.data_hierarchy_model import DataHierarchyModel
from pasta_eln.dataverse.database_error import DatabaseError
from pasta_eln.dataverse.database_names import DatabaseNames
from pasta_eln.dataverse.database_orm_config_model import DatabaseOrmConfigModel
from pasta_eln.dataverse.database_orm_data_hierarchy_model import DatabaseOrmDataHierarchyModel
from pasta_eln.dataverse.database_orm_main_model import DatabaseOrmMainModel
from pasta_eln.dataverse.database_orm_properties_model import DatabaseOrmPropertiesModel
from pasta_eln.dataverse.database_orm_upload_model import DatabaseOrmUploadModel
from pasta_eln.dataverse.database_sqlalchemy_base import DatabaseModelBase
from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError
from pasta_eln.dataverse.project_model import ProjectModel
from pasta_eln.dataverse.upload_model import UploadModel


@pytest.fixture
def base_database_api(mocker):
  mocker.patch("pasta_eln.dataverse.base_database_api.logging.getLogger")
  mocker.patch("pasta_eln.dataverse.base_database_api.DatabaseOrmAdapter")
  return BaseDatabaseApi("dataverse.db", "pasta_project_group.db")


class TestDataverseBaseDatabaseAPI:
  @pytest.mark.parametrize("dataverse_db_path, pasta_project_group_db_path, expected_exception", [
    ("valid_path.db", "valid_path.db", None),
    (123, "valid_path.db", IncorrectParameterError),
    ("valid_path.db", 123, IncorrectParameterError),
  ], ids=["valid_paths", "invalid_dataverse_path", "invalid_project_group_path"])
  def test_init(self, dataverse_db_path, pasta_project_group_db_path, expected_exception):
    # Act & Assert
    if expected_exception:
      with pytest.raises(expected_exception):
        BaseDatabaseApi(dataverse_db_path, pasta_project_group_db_path)
    else:
      api = BaseDatabaseApi(dataverse_db_path, pasta_project_group_db_path)
      assert api.db_url_map

  @pytest.mark.parametrize("db_url_map, expected_log_message", [
    ({DatabaseNames.DataverseDatabase: "sqlite:///:memory:",
      DatabaseNames.PastaProjectGroupDatabase: "sqlite:///:memory:"},
     ('Creating database at the location : %s', 'sqlite:///:memory:')),
  ], ids=["success_path"])
  def test_create_and_init_database_success_path(self, mocker, base_database_api, db_url_map, expected_log_message):
    # Arrange
    DatabaseModelBase.metadata = mocker.MagicMock()
    DatabaseModelBase.metadata.tables = mocker.MagicMock()
    DatabaseModelBase.metadata.tables = {
      DatabaseOrmConfigModel.__tablename__: mocker.MagicMock(),
      DatabaseOrmUploadModel.__tablename__: mocker.MagicMock(),
      DatabaseOrmDataHierarchyModel.__tablename__: mocker.MagicMock(),
      DatabaseOrmMainModel.__tablename__: mocker.MagicMock(),
      DatabaseOrmPropertiesModel.__tablename__: mocker.MagicMock(),
    }
    mock_create_engine = mocker.patch("pasta_eln.dataverse.base_database_api.create_engine")
    base_database_api.db_url_map = db_url_map

    # Act
    base_database_api.create_and_init_database()

    # Assert
    mock_create_engine.assert_called_with(db_url_map[DatabaseNames.DataverseDatabase])
    mock_create_engine.assert_called_with(db_url_map[DatabaseNames.PastaProjectGroupDatabase])
    DatabaseModelBase.metadata.tables[DatabaseOrmConfigModel.__tablename__].create.assert_called_once_with(
      bind=mock_create_engine.return_value, checkfirst=True)
    DatabaseModelBase.metadata.tables[DatabaseOrmUploadModel.__tablename__].create.assert_called_once_with(
      bind=mock_create_engine.return_value, checkfirst=True)
    DatabaseModelBase.metadata.tables[DatabaseOrmDataHierarchyModel.__tablename__].create.assert_called_once_with(
      bind=mock_create_engine.return_value, checkfirst=True)
    DatabaseModelBase.metadata.tables[DatabaseOrmMainModel.__tablename__].create.assert_called_once_with(
      bind=mock_create_engine.return_value, checkfirst=True)
    DatabaseModelBase.metadata.tables[DatabaseOrmPropertiesModel.__tablename__].create.assert_called_once_with(
      bind=mock_create_engine.return_value, checkfirst=True)
    base_database_api.logger.info.assert_called_with(*expected_log_message)

  @pytest.mark.parametrize("db_url_map", [
    ({"DataverseDatabase": "invalid_url", "PastaProjectGroupDatabase": "sqlite:///:memory:"}),
    ({"DataverseDatabase": "sqlite:///:memory:", "PastaProjectGroupDatabase": "invalid_url"}),
  ], ids=["invalid_dataverse_url", "invalid_pasta_project_group_url"])
  def test_create_and_init_database_error_cases(self, base_database_api, db_url_map):
    # Arrange
    base_database_api.db_url_map = db_url_map

    # Act
    with pytest.raises(KeyError):
      base_database_api.create_and_init_database()

  @pytest.mark.parametrize("data_model, expected_exception", [
    (UploadModel(), None),
    (ConfigModel(), None),
    (None, KeyError),
  ], ids=["valid_upload_model", "valid_config_model", "invalid_none_model"])
  def test_insert_model(self, mocker, base_database_api, data_model, expected_exception):
    # Arrange
    mock_create_engine = mocker.patch("pasta_eln.dataverse.base_database_api.create_engine")
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_session = MagicMock()
    mocker.patch("pasta_eln.dataverse.base_database_api.Session", return_value=mock_session)
    mock_session.__enter__.return_value = mock_session
    if data_model is not None:
      base_database_api.to_orm_converter_map[type(data_model)] = lambda x: x
      base_database_api.to_base_model_converter_map[type(data_model)] = lambda x: x

    # Act & Assert
    if expected_exception:
      with pytest.raises(expected_exception):
        base_database_api.insert_model(data_model)
    else:
      result = base_database_api.insert_model(data_model)
      mock_session.commit.assert_called_once()
      mock_session.add.assert_called_once()
      mock_session.flush.assert_called_once()
      for key, value in data_model.__dict__.items():
        assert getattr(result, key) == value

  @pytest.mark.parametrize("model_id, model_type, expected, test_id", [
    # Happy path tests
    (1, UploadModel, UploadModel(), "success_path_upload"),
    (2, ConfigModel, ConfigModel(), "success_path_config"),
    (3, DataHierarchyModel, DataHierarchyModel(), "success_path_data_hierarchy"),
    ("project_id", ProjectModel, ProjectModel(), "success_path_project"),

    # Edge cases
    (None, UploadModel, DatabaseError, "edge_case_none_id"),
    ("", UploadModel, DatabaseError, "edge_case_empty_string_id"),
    (1, ProjectModel, None, "edge_case_int_id_for_project"),

    # Error cases
    (1, MagicMock, DatabaseError, "error_case_invalid_model_type"),
  ])
  def test_get_model(self, mocker, base_database_api, model_id, model_type, expected, test_id):
    # Arrange
    mock_create_engine = mocker.patch("pasta_eln.dataverse.base_database_api.create_engine")
    base_database_api.get_project_model = MagicMock()
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_session = MagicMock()
    mocker.patch("pasta_eln.dataverse.base_database_api.Session", return_value=mock_session)
    mock_session.__enter__.return_value = mock_session
    mock_session.get.return_value = model_type()
    base_database_api.get_project_model.return_value = expected
    base_database_api.to_base_model_converter_map[DatabaseOrmUploadModel].return_value = expected
    base_database_api.to_base_model_converter_map[DatabaseOrmConfigModel].return_value = expected
    base_database_api.to_base_model_converter_map[DatabaseOrmDataHierarchyModel].return_value = expected

    if isinstance(expected, type) and issubclass(expected, Exception):
      # Act & Assert
      with pytest.raises(expected):
        base_database_api.get_model(model_id, model_type)
    else:
      # Act
      result = base_database_api.get_model(model_id, model_type)

      # Assert
      base_database_api.logger.info.assert_called_with("Retrieving data model with id: %s, type: %s", model_id,
                                                       model_type)
      assert result == expected
      if model_type in [UploadModel, ConfigModel, DataHierarchyModel]:
        mock_session.get.assert_called_once_with(base_database_api.model_mapping[model_type], model_id)

  @pytest.mark.parametrize("model_type, expected_exception", [
    (UploadModel, None),
    (None, DatabaseError),
  ], ids=["valid_model_type", "none_model_type"])
  def test_get_models(self, base_database_api, model_type, expected_exception):
    # Arrange
    with patch("sqlalchemy.create_engine") as mock_create_engine:
      mock_engine = MagicMock()
      mock_create_engine.return_value = mock_engine
      mock_session = MagicMock()
      mock_engine.connect.return_value.__enter__.return_value = mock_session

      # Act & Assert
      if expected_exception:
        with pytest.raises(expected_exception):
          base_database_api.get_models(model_type)
      else:
        result = base_database_api.get_models(model_type)
        assert isinstance(result, list)

  @pytest.mark.parametrize("model_type, db_model, database, expected_count", [
    param(UploadModel, DatabaseOrmUploadModel, DatabaseNames.DataverseDatabase, 0, id="empty_upload_model"),
    param(UploadModel, DatabaseOrmUploadModel, DatabaseNames.DataverseDatabase, 2, id="non_empty_upload_model"),
    param(ConfigModel, DatabaseOrmConfigModel, DatabaseNames.DataverseDatabase, 0, id="empty_config_model"),
    param(ConfigModel, DatabaseOrmConfigModel, DatabaseNames.DataverseDatabase, 10, id="non_empty_config_model"),
    param(DataHierarchyModel, DatabaseOrmDataHierarchyModel, DatabaseNames.PastaProjectGroupDatabase, 0,
          id="empty_data_hierarchy_model"),
  ], ids=lambda x: x[2])
  def test_get_models_success_path(self, mocker, base_database_api, model_type, db_model, database, expected_count):
    # Arrange
    mock_create_engine = mocker.patch("pasta_eln.dataverse.base_database_api.create_engine")
    mock_select = mocker.patch("pasta_eln.dataverse.base_database_api.select")
    base_database_api.get_project_model = MagicMock()
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_session = MagicMock()
    mocker.patch("pasta_eln.dataverse.base_database_api.Session", return_value=mock_session)
    mock_session.__enter__.return_value = mock_session
    mock_session.scalars.return_value.all.return_value = [db_model() for _ in range(expected_count)]

    # Act
    result = base_database_api.get_models(model_type)

    # Assert
    mock_select.assert_called_once_with(base_database_api.model_mapping[model_type])
    mock_create_engine.assert_called_once_with(base_database_api.db_url_map[database])
    assert len(result) == expected_count
    mock_session.scalars.assert_called_once_with(mock_select.return_value)
    mock_session.scalars.return_value.all.assert_called_once()
    assert base_database_api.to_base_model_converter_map[db_model].call_count == expected_count
    base_database_api.logger.info.assert_called_once_with("Retrieving models from database, type: %s", model_type)

  @pytest.mark.parametrize("model_type", [
    param(None, id="none_model_type"),
  ], ids=lambda x: x[1])
  def test_get_models_error_cases(self, base_database_api, model_type):
    # Act & Assert
    with pytest.raises(DatabaseError):
      base_database_api.get_models(model_type)
    base_database_api.logger.info.assert_called_once_with("Retrieving models from database, type: %s", model_type)

  @pytest.mark.parametrize("model_type", [
    param(UploadModel, id="sqlalchemy_error"),
  ], ids=lambda x: x[1])
  def test_get_models_sqlalchemy_error(self, mocker, base_database_api, model_type):
    # Arrange
    mock_create_engine = mocker.patch("pasta_eln.dataverse.base_database_api.create_engine")
    base_database_api.get_project_model = MagicMock()
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_session = MagicMock()
    mocker.patch("pasta_eln.dataverse.base_database_api.Session", return_value=mock_session)
    mock_session.__enter__.return_value = mock_session
    mock_session.scalars.side_effect = SQLAlchemyError

    # Act & Assert
    with pytest.raises(SQLAlchemyError):
      base_database_api.get_models(model_type)
    base_database_api.logger.info.assert_called_once_with("Retrieving models from database, type: %s", model_type)

  @pytest.mark.parametrize(
    "mock_data, expected_count",
    [
      param([(1, "Project A"), (2, "Project B")], 2, id="success_path_two_projects"),
      param([], 0, id="success_path_no_projects"),
    ],
    ids=lambda x: x[2]
  )
  def test_get_project_models_success_path(self, mocker, base_database_api, mock_data, expected_count):
    # Arrange
    mock_create_engine = mocker.patch("pasta_eln.dataverse.base_database_api.create_engine")
    mock_get_project_model = mocker.patch("pasta_eln.dataverse.base_database_api.DatabaseOrmAdapter.get_project_model")
    mock_get_project_model.return_value = MagicMock(spec=ProjectModel)
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_session = MagicMock()
    mocker.patch("pasta_eln.dataverse.base_database_api.Session", return_value=mock_session)
    mock_session.__enter__.return_value = mock_session
    all_items = [mocker.MagicMock() for _ in range(expected_count)]
    for i in range(expected_count):
      all_items[i].tuple.return_value = mock_data[i]
    mock_session.execute.return_value.fetchall.return_value = all_items
    mock_generate_project_join_statement = mocker.patch(
      "pasta_eln.dataverse.base_database_api.generate_project_join_statement")

    # Act
    result = base_database_api.get_project_models()

    # Assert
    mock_create_engine.assert_called_once_with(base_database_api.db_url_map[DatabaseNames.PastaProjectGroupDatabase])
    mock_generate_project_join_statement.assert_called_once_with(None)
    if expected_count != 0:
      mock_session.execute.assert_called_once_with(mock_generate_project_join_statement.return_value)
      mock_session.execute.return_value.fetchall.assert_called_once()
    assert len(result) == expected_count
    assert all(isinstance(proj, ProjectModel) for proj in result)

  @pytest.mark.parametrize(
    "mock_data",
    [
      param([(None, "Project C")], id="edge_case_null_id"),
      param([(1, None)], id="edge_case_null_name"),
    ],
    ids=lambda x: x[1]
  )
  def test_get_project_models_edge_cases(self, mocker, base_database_api, mock_data):
    # Arrange
    mock_create_engine = mocker.patch("pasta_eln.dataverse.base_database_api.create_engine")
    mock_get_project_model = mocker.patch("pasta_eln.dataverse.base_database_api.DatabaseOrmAdapter.get_project_model")
    mock_get_project_model.return_value = MagicMock(spec=ProjectModel)
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_session = MagicMock()
    mocker.patch("pasta_eln.dataverse.base_database_api.Session", return_value=mock_session)
    mock_session.__enter__.return_value = mock_session
    all_items = [mocker.MagicMock() for _ in range(len(mock_data))]
    for i in range(len(mock_data)):
      all_items[i].tuple.return_value = mock_data[i]
    mock_session.execute.return_value.fetchall.return_value = all_items
    mock_generate_project_join_statement = mocker.patch(
      "pasta_eln.dataverse.base_database_api.generate_project_join_statement")

    # Act
    result = base_database_api.get_project_models()

    # Assert
    mock_generate_project_join_statement.assert_called_once_with(None)
    assert len(result) == 1
    assert isinstance(result[0], ProjectModel)

  @pytest.mark.parametrize(
    "exception",
    [
      param(SQLAlchemyError("Database error"), id="error_case_sqlalchemy_error"),
    ],
    ids=lambda x: x[1]
  )
  def test_get_project_models_error_cases(self, mocker, base_database_api, exception):
    # Arrange
    mock_create_engine = mocker.patch("pasta_eln.dataverse.base_database_api.create_engine")
    mock_get_project_model = mocker.patch("pasta_eln.dataverse.base_database_api.DatabaseOrmAdapter.get_project_model")
    mock_get_project_model.return_value = MagicMock(spec=ProjectModel)
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_session = MagicMock()
    mocker.patch("pasta_eln.dataverse.base_database_api.Session", return_value=mock_session)
    mock_session.__enter__.side_effect = exception
    mocker.patch(
      "pasta_eln.dataverse.base_database_api.generate_project_join_statement")

    # Act & Assert
    with pytest.raises(SQLAlchemyError):
      base_database_api.get_project_models()

  @pytest.mark.parametrize("model_id, expected_exception", [
    ("valid_id", None),
    (None, DatabaseError),
  ], ids=["valid_id", "none_id"])
  def test_get_project_model(self, mocker, base_database_api, model_id, expected_exception):
    # Arrange
    mock_create_engine = mocker.patch("pasta_eln.dataverse.base_database_api.create_engine")
    mock_get_project_model = mocker.patch("pasta_eln.dataverse.base_database_api.DatabaseOrmAdapter.get_project_model")
    mock_generate_project_join_statement = mocker.patch(
      "pasta_eln.dataverse.base_database_api.generate_project_join_statement")
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_session = MagicMock()
    mocker.patch("pasta_eln.dataverse.base_database_api.Session", return_value=mock_session)
    mock_session.__enter__.return_value = mock_session

    # Act & Assert
    if expected_exception:
      with pytest.raises(expected_exception):
        base_database_api.get_project_model(model_id)
    else:
      result = base_database_api.get_project_model(model_id)
      base_database_api.logger.info.assert_called_once_with("Retrieving project from database: %s, model id: %s",
                                                            DatabaseNames.PastaProjectGroupDatabase, model_id)
      mock_generate_project_join_statement.assert_called_once_with(model_id)
      mock_session.execute.assert_called_once_with(mock_generate_project_join_statement.return_value)
      mock_session.execute.return_value.fetchone.assert_called_once()
      mock_session.execute.return_value.fetchone.return_value.tuple.assert_called_once()
      mock_get_project_model.assert_any_call(mock_session.execute.return_value.fetchone.return_value.tuple.return_value)

      assert result is not None

  @pytest.mark.parametrize("data_model, expected_exception", [
    param(UploadModel(_id=1), None, id="success_path_upload_model"),
    param(ConfigModel(_id=2), None, id="success_path_config_model"),
    param(UploadModel(_id=None), DatabaseError, id="error_no_id_upload_model"),
    param(ConfigModel(_id=None), DatabaseError, id="error_no_id_config_model"),
    param(UploadModel(_id=999), DatabaseError, id="error_nonexistent_id_upload_model"),
    param(ConfigModel(_id=999), DatabaseError, id="error_nonexistent_id_config_model"),
  ], ids=lambda x: x[2])
  def test_update_model(self, mocker, base_database_api, data_model, expected_exception):
    # Arrange
    mock_create_engine = mocker.patch("pasta_eln.dataverse.base_database_api.create_engine")
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_session = MagicMock()
    mocker.patch("pasta_eln.dataverse.base_database_api.Session", return_value=mock_session)
    mock_session.__enter__.return_value = mock_session
    mock_session.get.return_value = (data_model if data_model.id in [1, 2] else None)
    base_database_api.to_orm_converter_map[type(data_model)] = lambda x: x

    # Act
    if expected_exception:
      with pytest.raises(expected_exception):
        base_database_api.update_model(data_model)
    else:
      base_database_api.update_model(data_model)

    # Assert
    if not expected_exception:
      mock_session.merge.assert_called_once_with(data_model)
      mock_session.commit.assert_called_once()
      base_database_api.logger.info.assert_called_once_with("Updating data model with id: %s, type: %s",
                                                            data_model.id,
                                                            type(data_model))
    else:
      base_database_api.logger.error.assert_called()

  @pytest.mark.parametrize(
    "model_type, filter_term, filter_fields, order_by_column, page_number, limit, expected_count", [
      (UploadModel, None, None, None, 1, 10, 0),  # happy path, no filters
      (ConfigModel, "test", ["metadata"], None, 1, 10, 0),  # happy path, with filter
      (DataHierarchyModel, None, None, "name", 1, 10, 0),  # happy path, with order
    ], ids=["no_filters", "with_filter", "with_order"])
  def test_get_paginated_models_happy_path(self, mocker, base_database_api, model_type, filter_term, filter_fields,
                                           order_by_column,
                                           page_number, limit, expected_count):
    # Arrange
    mock_create_engine = mocker.patch("pasta_eln.dataverse.base_database_api.create_engine")
    mock_select = mocker.patch("pasta_eln.dataverse.base_database_api.select")
    mock_getattr = mocker.patch("pasta_eln.dataverse.base_database_api.getattr")
    mock_or_ = mocker.patch("pasta_eln.dataverse.base_database_api.or_")
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_session = MagicMock()
    mocker.patch("pasta_eln.dataverse.base_database_api.Session", return_value=mock_session)
    mock_session.__enter__.return_value = mock_session
    # Act
    result = base_database_api.get_paginated_models(model_type, filter_term, filter_fields, order_by_column,
                                                    page_number,
                                                    limit)

    # Assert
    mock_select.assert_called_once_with(base_database_api.model_mapping[model_type])
    mock_select.return_value.limit.assert_called_once_with(limit)
    mock_select.return_value.limit.return_value.offset.assert_called_once_with((page_number - 1) * limit)
    mock_create_engine.assert_called_once()
    mock_session.execute.assert_called_once()
    mock_session.execute.return_value.scalars.return_value.all.assert_called_once()
    assert len(result) == expected_count

  @pytest.mark.parametrize("page_number, limit, expected_exception", [
    (0, 10, DatabaseError),  # page_number less than 1
    (1, 0, DatabaseError),  # limit less than 1
  ], ids=["invalid_page_number", "invalid_limit"])
  def test_get_paginated_models_invalid_input(self, base_database_api, page_number, limit, expected_exception):
    # Act & Assert
    with pytest.raises(expected_exception):
      base_database_api.get_paginated_models(UploadModel, None, None, None, page_number, limit)

  @pytest.mark.parametrize(
    "model_type, filter_term, filter_fields, order_by_column, page_number, limit, expected_exception", [
      (UploadModel, None, None, "invalid_column", 1, 10, AttributeError),  # invalid order_by_column
    ], ids=["invalid_order_by_column"])
  def test_get_paginated_models_invalid_order_by(self, base_database_api, model_type, filter_term,
                                                 filter_fields, order_by_column,
                                                 page_number, limit, expected_exception):
    # Act & Assert
    with pytest.raises(expected_exception):
      base_database_api.get_paginated_models(model_type, filter_term, filter_fields, order_by_column, page_number,
                                             limit)

  @pytest.mark.parametrize("model_type, filter_term, filter_fields, order_by_column, page_number, limit", [
    (UploadModel, None, None, None, 1, 10),  # simulate SQLAlchemy error
  ], ids=["sqlalchemy_error"])
  def test_get_paginated_models_sqlalchemy_error(self, mocker, base_database_api, model_type, filter_term,
                                                 filter_fields, order_by_column,
                                                 page_number, limit):
    # Arrange
    mock_create_engine = mocker.patch("pasta_eln.dataverse.base_database_api.create_engine")
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_session = MagicMock()
    mocker.patch("pasta_eln.dataverse.base_database_api.Session", return_value=mock_session)
    mock_session.__enter__.return_value = mock_session
    mock_session.execute.side_effect = SQLAlchemyError
    # Act & Assert
    with pytest.raises(SQLAlchemyError):
      base_database_api.get_paginated_models(model_type, filter_term, filter_fields, order_by_column, page_number,
                                             limit)

  @pytest.mark.parametrize(
    "model_type, expected_count, mock_count",
    [
      param(UploadModel, 5, 5, id="happy_path_upload_model"),
      param(ConfigModel, 0, 0, id="happy_path_config_model_empty"),
      param(DataHierarchyModel, 10, 10, id="happy_path_data_hierarchy_model"),
      param(UploadModel, 0, 0, id="edge_case_no_records"),
      param(ConfigModel, 1, 1, id="edge_case_single_record"),
      param(None, None, None, id="error_case_invalid_model_type"),
    ],
    ids=lambda x: x[-1]
  )
  def test_get_models_count(self, mocker, base_database_api, model_type, expected_count, mock_count):
    # Arrange
    if model_type is not None:
      mock_session = MagicMock()
      mocker.patch("pasta_eln.dataverse.base_database_api.Session", return_value=mock_session)
      mock_session.__enter__.return_value = mock_session
      mock_session.query.return_value.count.return_value = mock_count

      # Act
      result = base_database_api.get_models_count(model_type)

      # Assert
      assert result == expected_count
    else:

      # Act & Assert
      with pytest.raises(KeyError):
        base_database_api.get_models_count(model_type)
