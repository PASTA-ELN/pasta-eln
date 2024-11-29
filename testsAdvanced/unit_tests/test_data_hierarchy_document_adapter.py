#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_document_adapter.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest
from _pytest.mark import param

from pasta_eln.GUI.data_hierarchy.data_hierarchy_document_adapter import DataHierarchyDocumentAdapter
from pasta_eln.database.models.data_hierarchy_definition_model import DataHierarchyDefinitionModel
from pasta_eln.database.models.data_hierarchy_model import DataHierarchyModel


class TestDataHierarchyDocumentAdapter:
  @pytest.mark.parametrize(
    "data, expected",
    [
      # Happy path test cases
      pytest.param(
        DataHierarchyModel(
          doc_type="type1",
          IRI="http://example.com/iri1",
          title="Title 1",
          icon="icon1",
          shortcut="shortcut1",
          view="view1",
          definitions=[
            # Assuming definitions have attributes: name, query, mandatory, unit, IRI, meta_list, doc_class
            # Add realistic test values here
          ]
        ),
        {
          "type1": {
            "IRI": "http://example.com/iri1",
            "attachments": [],
            "title": "Title 1",
            "icon": "icon1",
            "shortcut": "shortcut1",
            "view": "view1",
            "meta": {
              # Expected meta structure based on definitions
            }
          }
        },
        id="happy_path_with_definitions"
      ),
      pytest.param(
        DataHierarchyModel(
          doc_type="type2",
          IRI="http://example.com/iri2",
          title="Title 2",
          icon="icon2",
          shortcut="shortcut2",
          view="view2",
          definitions=None
        ),
        {
          "type2": {
            "IRI": "http://example.com/iri2",
            "attachments": [],
            "title": "Title 2",
            "icon": "icon2",
            "shortcut": "shortcut2",
            "view": "view2",
            "meta": {}
          }
        },
        id="happy_path_no_definitions"
      ),
      # Edge case test cases
      pytest.param(
        DataHierarchyModel(
          doc_type=None,
          IRI="http://example.com/iri3",
          title="Title 3",
          icon="icon3",
          shortcut="shortcut3",
          view="view3",
          definitions=[]
        ),
        {},
        id="edge_case_no_doc_type"
      ),
      pytest.param(
        None,
        {},
        id="edge_case_none_data"
      ),
      # Error case test cases
      pytest.param(
        DataHierarchyModel(
          doc_type="type4",
          IRI=None,
          title=None,
          icon=None,
          shortcut=None,
          view=None,
          definitions=[]
        ),
        {
          "type4": {
            "IRI": None,
            "attachments": [],
            "title": None,
            "icon": None,
            "shortcut": None,
            "view": None,
            "meta": {}
          }
        },
        id="error_case_missing_fields"
      ),
    ]
  )
  def test_to_data_hierarchy_document(self, data, expected, request):
    # Act
    result = DataHierarchyDocumentAdapter.to_data_hierarchy_document(data)

    # Assert
    assert result == expected, f"Failed test case: {request.node.callspec.id}"


@pytest.mark.parametrize(
  "data, expected",
  [
    # Happy path test with realistic values
    param(
      {
        "doc1": {
          "meta": {
            "default": [
              {"name": "name1", "query": "query1", "mandatory": True, "unit": "unit1", "list": ["item1"], "IRI": "IRI1"}
            ]
          },
          "IRI": "IRI_doc1",
          "title": "Title 1",
          "icon": "icon1",
          "shortcut": "shortcut1",
          "view": "view1"
        }
      },
      [
        DataHierarchyModel(
          doc_type="doc1",
          IRI="IRI_doc1",
          title="Title 1",
          icon="icon1",
          shortcut="shortcut1",
          view="view1",
          definitions=[
            DataHierarchyDefinitionModel(
              doc_type="doc1",
              doc_class="",
              index="0",
              name="name1",
              query="query1",
              mandatory='T',
              unit="unit1",
              meta_list=["item1"],
              IRI="IRI1"
            )
          ]
        )
      ],
      id="happy_path_single_doc"
    ),
    # Edge case: empty data dictionary
    param(
      {},
      None,
      id="empty_data"
    ),
    # Edge case: missing optional fields
    param(
      {
        "doc2": {
          "meta": {
            "default": [
              {"name": "name2"}
            ]
          }
        }
      },
      [
        DataHierarchyModel(
          doc_type="doc2",
          IRI=None,
          title=None,
          icon=None,
          shortcut=None,
          view=None,
          definitions=[
            DataHierarchyDefinitionModel(
              doc_type="doc2",
              doc_class="",
              index="0",
              name="name2",
              query=None,
              mandatory='F',
              unit=None,
              meta_list=[],
              IRI=None
            )
          ]
        )
      ],
      id="missing_optional_fields"
    ),
    # Error case: invalid meta structure
    param(
      {
        "doc3": {
          "meta": "invalid_structure"
        }
      },
      [],
      id="invalid_meta_structure"
    ),
  ],
  ids=lambda x: x[2]
)
def test_to_data_hierarchy_model_list(data, expected, request):
  # Act
  if request.node.callspec.id == "invalid_meta_structure":
    with pytest.raises(AttributeError):
      DataHierarchyDocumentAdapter.to_data_hierarchy_model_list(data)
  else:
    result = DataHierarchyDocumentAdapter.to_data_hierarchy_model_list(data)
    for i in range(len(result)):
      assert str(result[i]) == str(expected[i])
