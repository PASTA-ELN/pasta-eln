#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_database_data_hierarchy_orm_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.database.models.data_hierarchy_orm_model import DataHierarchyOrmModel


class TestDatabaseOrmDataHierarchyModel:
  @pytest.mark.parametrize(
    "doc_type, IRI, title, icon, shortcut, view, expected_columns",
    [
      # Happy path test cases
      ("type1", "http://example.com/iri1", "Title 1", "icon1.png", "Ctrl+1", "view1",
       ['doc_type', 'IRI', 'title', 'icon', 'shortcut', 'view', 'definitions']),
      ("type2", None, "Title 2", None, None, "view2",
       ['doc_type', 'IRI', 'title', 'icon', 'shortcut', 'view', 'definitions']),

      # Edge cases
      ("", "", "", "", "", "", ['doc_type', 'IRI', 'title', 'icon', 'shortcut', 'view', 'definitions']),
      ("type3", "http://example.com/iri3", "Title 3", "icon3.png", "Ctrl+3", None,
       ['doc_type', 'IRI', 'title', 'icon', 'shortcut', 'view', 'definitions']),

      # Error cases
      # Assuming that the mapped_column does not enforce any constraints beyond primary_key
      # If there were constraints, we would test invalid inputs here
    ],
    ids=[
      "happy_path_all_fields",
      "happy_path_some_none",
      "edge_case_empty_strings",
      "edge_case_none_view",
    ]
  )
  def test_get_table_columns(self, doc_type, IRI, title, icon, shortcut, view, expected_columns):
    # Act
    columns = DataHierarchyOrmModel.get_table_columns()

    # Assert
    assert columns == expected_columns
