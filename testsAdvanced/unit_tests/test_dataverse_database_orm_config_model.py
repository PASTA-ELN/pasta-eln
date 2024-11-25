#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_database_orm_config_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.database.models.database_orm_config_model import DatabaseOrmConfigModel


class TestDatabaseOrmConfigModel:
  @pytest.mark.parametrize(
    "project_upload_items, parallel_uploads_count, dataverse_login_info, metadata_info, expected_columns",
    [
      # Happy path test cases
      pytest.param(
        {"key": "value"}, 5, {"username": "user"}, {"meta": "data"},
        ["id", "project_upload_items", "parallel_uploads_count", "dataverse_login_info", "metadata_info"],
        id="happy_path_all_fields"
      ),
      pytest.param(
        None, None, None, None,
        ["id", "project_upload_items", "parallel_uploads_count", "dataverse_login_info", "metadata_info"],
        id="happy_path_none_fields"
      ),
      # Edge case test cases
      pytest.param(
        {}, 0, {}, {},
        ["id", "project_upload_items", "parallel_uploads_count", "dataverse_login_info", "metadata_info"],
        id="edge_case_empty_dicts_and_zero"
      ),
      pytest.param(
        {"nested": {"key": "value"}}, 1, {"user": "name"}, {"meta": "info"},
        ["id", "project_upload_items", "parallel_uploads_count", "dataverse_login_info", "metadata_info"],
        id="edge_case_nested_dicts"
      ),
      # Error case test cases
      pytest.param(
        "not_a_dict", 5, {"username": "user"}, {"meta": "data"},
        ["id", "project_upload_items", "parallel_uploads_count", "dataverse_login_info", "metadata_info"],
        id="error_case_invalid_project_upload_items"
      ),
      pytest.param(
        {"key": "value"}, "not_an_int", {"username": "user"}, {"meta": "data"},
        ["id", "project_upload_items", "parallel_uploads_count", "dataverse_login_info", "metadata_info"],
        id="error_case_invalid_parallel_uploads_count"
      ),
    ]
  )
  def test_get_table_columns(self,
                             project_upload_items, parallel_uploads_count, dataverse_login_info, metadata_info,
                             expected_columns
                             ):
    # Arrange
    model_instance = DatabaseOrmConfigModel(
      project_upload_items=project_upload_items,
      parallel_uploads_count=parallel_uploads_count,
      dataverse_login_info=dataverse_login_info,
      metadata_info=metadata_info
    )

    # Act
    result = model_instance.get_table_columns()

    # Assert
    assert result == expected_columns
    assert model_instance.__tablename__ == "config"
