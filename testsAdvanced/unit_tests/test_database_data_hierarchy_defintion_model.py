#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_database_data_hierarchy_defintion_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.database.incorrect_parameter_error import IncorrectParameterError
from pasta_eln.database.models.data_hierarchy_definition_model import DataHierarchyDefinitionModel

# Test data for happy path
happy_path_data = [
  ("doc_type_1", "doc_class_1", "index_1", "name_1", "query_1", "unit_1", "IRI_1", "mandatory_1", ["meta1", "meta2"],
   "happy_path_1"),
  (None, None, None, None, None, None, None, None, None, "happy_path_2"),
]

# Test data for edge cases
edge_case_data = [
  ("", "", "", "", "", "", "", "", [], "empty_strings"),
  ("a" * 1000, "b" * 1000, "c" * 1000, "d" * 1000, "e" * 1000, "f" * 1000, "g" * 1000, "h" * 1000, ["i" * 1000],
   "long_strings"),
]

# Test data for error cases
error_case_data = [
  (123, "doc_class", "index", "name", "query", "unit", "IRI", "mandatory", ["meta"], "non_string_doc_type"),
  ("doc_type", 456, "index", "name", "query", "unit", "IRI", "mandatory", ["meta"], "non_string_doc_class"),
  ("doc_type", "doc_class", 789, "name", "query", "unit", "IRI", "mandatory", ["meta"], "non_string_index"),
  ("doc_type", "doc_class", "index", 101112, "query", "unit", "IRI", "mandatory", ["meta"], "non_string_name"),
  ("doc_type", "doc_class", "index", "name", 131415, "unit", "IRI", "mandatory", ["meta"], "non_string_query"),
  ("doc_type", "doc_class", "index", "name", "query", 161718, "IRI", "mandatory", ["meta"], "non_string_unit"),
  ("doc_type", "doc_class", "index", "name", "query", "unit", 192021, "mandatory", ["meta"], "non_string_IRI"),
  ("doc_type", "doc_class", "index", "name", "query", "unit", "IRI", 222324, ["meta"], "non_string_mandatory"),
  ("doc_type", "doc_class", "index", "name", "query", "unit", "IRI", "mandatory", "not_a_list", "non_list_meta_list"),
]


class TestDatabaseDataHierarchyDefinitionModel:

  @pytest.mark.parametrize("doc_type, doc_class, index, name, query, unit, IRI, mandatory, meta_list, test_id",
                           happy_path_data, ids=[x[-1] for x in happy_path_data])
  def test_data_hierarchy_definition_model_happy_path(self, doc_type, doc_class, index, name, query, unit, IRI,
                                                      mandatory, meta_list, test_id):
    # Act
    model = DataHierarchyDefinitionModel(doc_type, doc_class, index, name, query, unit, IRI, mandatory, meta_list)

    # Assert
    assert model.doc_type == doc_type
    assert model.doc_class == doc_class
    assert model.index == index
    assert model.name == name
    assert model.query == query
    assert model.unit == unit
    assert model.IRI == IRI
    assert model.mandatory == mandatory
    assert model.meta_list == meta_list

  @pytest.mark.parametrize("doc_type, doc_class, index, name, query, unit, IRI, mandatory, meta_list, test_id",
                           edge_case_data, ids=[x[-1] for x in edge_case_data])
  def test_data_hierarchy_definition_model_edge_cases(self, doc_type, doc_class, index, name, query, unit, IRI,
                                                      mandatory, meta_list, test_id):
    # Act
    model = DataHierarchyDefinitionModel(doc_type, doc_class, index, name, query, unit, IRI, mandatory, meta_list)

    # Assert
    assert model.doc_type == doc_type
    assert model.doc_class == doc_class
    assert model.index == index
    assert model.name == name
    assert model.query == query
    assert model.unit == unit
    assert model.IRI == IRI
    assert model.mandatory == mandatory
    assert model.meta_list == meta_list

  @pytest.mark.parametrize("doc_type, doc_class, index, name, query, unit, IRI, mandatory, meta_list, test_id",
                           error_case_data, ids=[x[-1] for x in error_case_data])
  def test_data_hierarchy_definition_model_error_cases(self, doc_type, doc_class, index, name, query, unit, IRI,
                                                       mandatory, meta_list, test_id):
    # Act & Assert
    with pytest.raises(IncorrectParameterError):
      DataHierarchyDefinitionModel(doc_type, doc_class, index, name, query, unit, IRI, mandatory, meta_list)
