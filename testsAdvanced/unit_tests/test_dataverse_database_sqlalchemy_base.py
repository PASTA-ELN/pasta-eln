#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_database_sqlalchemy_base.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Any, Optional

import pytest
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from pasta_eln.dataverse.database_sqlalchemy_base import DatabaseModelBase


# Mock class to test DatabaseModelBase
class MockDatabaseModel(DatabaseModelBase):
  __tablename__ = "mock_table"
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[Optional[str]]
  data: Mapped[Optional[dict[str, Any]]]

  def __init__(self, id: int, name: str, data: dict[str, Any], **kw: Any):
    super().__init__(**kw)
    self.id = id
    self.name = name
    self.data = data

  @classmethod
  def get_table_columns(cls) -> list[str]:
    return ['id', 'name', 'data']


class TestDatabaseModelBase:
  @pytest.mark.parametrize(
    "instance, expected_output",
    [
      pytest.param(MockDatabaseModel(1, "Test", {"key": "value"}),
                   [("id", 1), ("name", "Test"), ("data", {"key": "value"})],
                   id="happy_path_with_valid_data"),
      pytest.param(MockDatabaseModel(0, "", {}),
                   [("id", 0), ("name", ""), ("data", {})],
                   id="edge_case_with_empty_values"),
    ]
  )
  def test_iter_method(self, instance, expected_output):
    # Act
    result = list(iter(instance))

    # Assert
    assert result == expected_output

  @pytest.mark.parametrize(
    "cls, expected_columns",
    [
      pytest.param(MockDatabaseModel, ["id", "name", "data"], id="happy_path_with_mock_class"),
      pytest.param(DatabaseModelBase, [], id="base_class_with_no_columns"),
    ]
  )
  def test_get_table_columns(self, cls, expected_columns):
    # Act
    columns = cls.get_table_columns()

    # Assert
    assert columns == expected_columns

  def test_type_annotation_map(self):
    # Arrange
    expected_map = {dict[str, Any]: JSON}

    # Act
    actual_map = DatabaseModelBase.type_annotation_map

    # Assert
    assert actual_map == expected_map
