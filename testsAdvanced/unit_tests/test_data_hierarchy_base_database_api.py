#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_base_database_api.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.GUI.data_hierarchy.base_database_api import BaseDatabaseApi
from pasta_eln.GUI.data_hierarchy.data_hierarchy_document_adapter import DataHierarchyDocumentAdapter


@pytest.fixture
def mock_data_hierarchy_base_database_api(mocker):
  db = BaseDatabaseApi("/home/jmurugan/pasta-eln/data/pastaELN.db")
  db.create_and_bind_db_tables()
  return db


class TestDataHierarchyBaseDatabaseApi:
  def test_get_data_hierarchy_model(self, mock_data_hierarchy_base_database_api):
    test = mock_data_hierarchy_base_database_api.get_data_hierarchy_models()
    dh_doc = {}
    for t in test:
      dh_doc.update(DataHierarchyDocumentAdapter.to_data_hierarchy_document(t))

    test2 = DataHierarchyDocumentAdapter.to_data_hierarchy_model_list(dh_doc)
    for t in test2:
      print(t)

    mock_data_hierarchy_base_database_api.update_data_hierarchy_models(test2)

  def test_get_data_hierarchy_definition_models(self, mock_data_hierarchy_base_database_api):
    test = mock_data_hierarchy_base_database_api.get_data_hierarchy_definition_models()
    for t in test:
      print(t)

  def test_get_joint_data_hierarchy_definition_models(self, mock_data_hierarchy_base_database_api):
    test = mock_data_hierarchy_base_database_api.get_joint_data_hierarchy_definition_models()
    for t in test:
      print(dict(t[0]), (t[1]))
