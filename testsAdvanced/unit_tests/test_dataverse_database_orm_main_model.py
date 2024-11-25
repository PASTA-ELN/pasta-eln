#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_database_orm_main_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.database.models.database_orm_main_model import DatabaseOrmMainModel


class TestDatabaseOrmMainModel:
  @pytest.mark.parametrize(
    "expected_columns, test_id",
    [
      (["id", "name", "user", "type", "dateCreated", "dateModified", "comment"], "default columns"),
    ],
    ids=["default columns"]
  )
  def test_get_table_columns(self, expected_columns, test_id):
    # Act
    result = DatabaseOrmMainModel.get_table_columns()

    # Assert
    assert result == expected_columns

  @pytest.mark.parametrize(
    "id, name, user, type, dateCreated, dateModified, comment, expected",
    [
      ("1", "Project A", "User1", "Type1", "2023-01-01", "2023-01-02", "Initial comment", "valid data"),
      ("2", None, None, None, None, None, None, "minimal data"),
      ("3", "", "", "", "", "", "", "empty strings"),
    ],
    ids=["valid data", "minimal data", "empty strings"]
  )
  def test_database_orm_main_model_initialization(self, id, name, user, type, dateCreated, dateModified, comment,
                                                  expected):
    # Act
    model_instance = DatabaseOrmMainModel(
      id=id,
      name=name,
      user=user,
      type=type,
      dateCreated=dateCreated,
      dateModified=dateModified,
      comment=comment
    )

    # Assert
    assert model_instance.id == id
    assert model_instance.name == name
    assert model_instance.user == user
    assert model_instance.type == type
    assert model_instance.dateCreated == dateCreated
    assert model_instance.dateModified == dateModified
    assert model_instance.comment == comment
