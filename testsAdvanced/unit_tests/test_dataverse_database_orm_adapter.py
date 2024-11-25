#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_database_orm_adapter.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest
from _pytest.mark import param

from pasta_eln.database.models.config_model import ConfigModel
from pasta_eln.database.models.config_orm_model import ConfigOrmModel
from pasta_eln.database.models.data_hierarchy_model import DataHierarchyModel
from pasta_eln.database.models.data_hierarchy_orm_model import DataHierarchyOrmModel
from pasta_eln.database.models.main_orm_model import MainOrmModel
from pasta_eln.database.database_orm_adapter import DatabaseOrmAdapter
from pasta_eln.database.models.upload_orm_model import UploadOrmModel
from pasta_eln.database.models.project_model import ProjectModel
from pasta_eln.database.models.upload_model import UploadModel


class TestDataverseDatabaseORMAdapter:
  @pytest.mark.parametrize(
    "input_data, expected_output",
    [
      # Happy path tests
      param({"metadata": {"key": "value"}, "project_upload_items": {"key": "value"}},
            {"metadata_info": {"key": "value"}, "project_upload_items": {"key": "value"}},
            id="happy_path_basic"),
      param({"metadata": {"key": "value"}, "project_upload_items": {"key": "value"},
             "dataverse_login_info": {"key1": "value1"}},
            {"metadata_info": {"key": "value"}, "project_upload_items": {"key": "value"},
             "dataverse_login_info": {"key1": "value1"}},
            id="happy_path_varied_types"),

      # Edge cases
      param({"metadata": {}},
            {"metadata_info": {}},
            id="edge_empty_metadata"),
      param({"metadata": None},
            {"metadata_info": None},
            id="edge_none_metadata"),
      param({"metadata": {"key": "value"}, "project_upload_items": None},
            {"metadata_info": {"key": "value"}, "project_upload_items": None},
            id="edge_none_field"),
      param({"project_upload_items": {"key": "value"}},
            {"metadata_info": None, "project_upload_items": {"key": "value"}},
            id="edge_missing_metadata"),
    ],
    ids=lambda x: x[2]
  )
  def test_get_orm_config_model(self, input_data, expected_output):
    # Arrange
    model = ConfigModel(**input_data)

    # Act
    if isinstance(expected_output, dict):
      result = DatabaseOrmAdapter.get_orm_config_model(model)

      # Assert
      for key, value in dict(ConfigOrmModel(**expected_output)).items():
        assert getattr(result, key) == value
    else:
      # Assert
      with expected_output:
        DatabaseOrmAdapter.get_orm_config_model(model)

  @pytest.mark.parametrize(
    "upload_model_data, expected_orm_model_data",
    [
      # Happy path tests
      param({"project_name": "value1", "_id": 123},
            {"project_name": "value1", "_id": 123, "data_type": 'dataverse_upload', "log": ''}, id="happy_path_1"),
      param({"project_name": "another_value", "_id": 456},
            {"project_name": "another_value", "_id": 456, "data_type": 'dataverse_upload', "log": ''},
            id="happy_path_2"),

      # Edge cases
      param({"project_name": "", "_id": 0}, {"project_name": "", "_id": 0, "data_type": 'dataverse_upload', "log": ''},
            id="edge_case_empty_string_and_zero"),
      param({"project_name": None, "_id": None},
            {"project_name": None, "_id": None, "data_type": 'dataverse_upload', "log": ''},
            id="edge_case_none_values"),

      # Error cases
      param({"project_name": "value1"}, {"project_name": "value1", "data_type": 'dataverse_upload', "log": ''},
            id="missing_field_error"),
      # Assuming DatabaseOrmUploadModel requires more fields
      param({"project_name": "value1", "_id": "not_an_int"},
            {"project_name": "value1", "_id": "not_an_int", "data_type": 'dataverse_upload', "log": ''},
            id="type_error"),
      # Assuming type mismatch
    ],
    ids=lambda x: x[2]
  )
  def test_get_orm_upload_model(self, upload_model_data, expected_orm_model_data, request):
    # Arrange
    upload_model = UploadModel(**upload_model_data)

    # Act
    try:
      orm_model = DatabaseOrmAdapter.get_orm_upload_model(upload_model)
    except Exception as e:
      orm_model = e

    # Assert
    if isinstance(orm_model, Exception):
      assert isinstance(orm_model, (TypeError, ValueError)), f"Unexpected exception type for {request.node.callspec.id}"
    else:
      if "_id" in expected_orm_model_data:
        expected_orm_model_data["id"] = expected_orm_model_data.pop("_id")
      assert dict(orm_model) == dict(
        UploadOrmModel(**expected_orm_model_data)), f"Failed for {request.node.callspec.id}"

  @pytest.mark.parametrize(
    "model_data, expected_attributes",
    [
      # Happy path test cases
      ({"name": "Project A", "comment": "A sample project"},
       {"name": "Project A", "comment": "A sample project"}),
      (
          {"name": "Project B", "comment": "Another project"}, {"name": "Project B", "comment": "Another project"}),

      # Edge case test cases
      ({"name": "", "comment": ""}, {"name": "", "comment": ""}),  # Empty strings
      ({"name": " ", "comment": " "}, {"name": " ", "comment": " "}),  # Strings with spaces
      ({"name": None, "comment": "Valid description"}, {"name": None, "comment": "Valid description"}),
      # None as a value
      ({"name": "Valid name", "comment": None}, {"name": "Valid name", "comment": None}),  # None as a value
    ],
    ids=[
      "happy_path_project_a",
      "happy_path_project_b",
      "edge_case_empty_strings",
      "edge_case_spaces",
      "edge_case_name_none",
      "edge_case_description_none",
    ]
  )
  def test_get_orm_project_model(self, model_data, expected_attributes):
    # Arrange
    model = ProjectModel(**model_data)

    # Act
    orm_model = DatabaseOrmAdapter.get_orm_project_model(model)

    # Assert
    for attr, value in expected_attributes.items():
      assert getattr(orm_model, attr) == value

  @pytest.mark.parametrize(
    "model_data, expected_attributes",
    [
      # Happy path test cases
      pytest.param(
        {"doc_type": "value1", "IRI": "value2"},
        {"doc_type": "value1", "IRI": "value2"},
        id="happy_path_basic"
      ),
      # Edge case test cases
      pytest.param(
        {},
        {},
        id="edge_case_empty_model"
      ),
      pytest.param(
        {"doc_type": None},
        {"doc_type": None},
        id="edge_case_none_value"
      )
    ]
  )
  def test_get_orm_data_hierarchy_model(self, model_data, expected_attributes):
    # Arrange
    model = DataHierarchyModel(**model_data)

    # Act
    orm_model = DatabaseOrmAdapter.get_orm_data_hierarchy_model(model)

    # Assert
    for attr, value in expected_attributes.items():
      assert getattr(orm_model, attr) == value

  @pytest.mark.parametrize(
    "input_data, expected_output",
    [
      # Happy path test cases
      param({"id": 1, "metadata_info": {"key": "value"}, "project_upload_items": {"key": "value"}},
            ConfigModel(_id=1, metadata={"key": "value"}, project_upload_items={"key": "value"}),
            id="happy_path_basic"),
      param({"id": 42, "metadata_info": {"key": "value"}, "project_upload_items": {"key": "value"},
             "dataverse_login_info": {"key": "value"}},
            ConfigModel(_id=42, metadata={"key": "value"}, project_upload_items={"key": "value"},
                        dataverse_login_info={"key": "value"}),
            id="happy_path_with_extra_field"),

      # Edge case test cases
      param({"id": 0, "metadata_info": None, "project_upload_items": None},
            ConfigModel(_id=0, metadata=None, project_upload_items=None),
            id="edge_case_empty_metadata"),
    ],
    ids=lambda x: x[2]
  )
  def test_get_config_model(self, input_data, expected_output):
    # Act
    if isinstance(expected_output, ConfigModel):
      # Act
      result = DatabaseOrmAdapter.get_config_model(ConfigOrmModel(**input_data))

      # Assert
      assert dict(result) == dict(expected_output)
    else:
      # Act and Assert
      with expected_output:
        DatabaseOrmAdapter.get_config_model(ConfigOrmModel(**input_data))

  @pytest.mark.parametrize(
    "input_data, expected_output",
    [
      # Happy path tests
      param({"id": 1, "project_name": "Test Model", "status": "100"},
            {"_id": 1, "project_name": "Test Model", "status": "100", "log": None}, id="happy_path_1"),
      param(
        {"id": 2, "created_date_time": "Another Model", "dataverse_url": "200"},
        {"_id": 2, "created_date_time": "Another Model", "dataverse_url": "200", "log": None},
        id="happy_path_2"),

      # Edge cases
      param({"id": 0, "project_name": "", "status": ""}, {"_id": 0, "project_name": "", "status": "", "log": None},
            id="edge_case_empty_string"),

      # Error cases
      param({"name": "Missing ID"}, None, id="error_case_missing_id"),
    ],
    ids=lambda x: x[2]
  )
  def test_get_upload_model(self, input_data, expected_output):
    # Arrange
    if "id" in input_data:
      model = UploadOrmModel(**input_data)
    else:
      model = None

    # Act
    if model:
      result = DatabaseOrmAdapter.get_upload_model(model)
    else:
      result = None

    # Assert
    if expected_output is not None:
      assert dict(result) == dict(UploadModel(**expected_output))
    else:
      with pytest.raises(Exception):
        DatabaseOrmAdapter.get_upload_model(model)

  @pytest.mark.parametrize(
    "model, expected_project_model",
    [
      # Happy path test cases
      param(
        (MainOrmModel(id=1, dateCreated="2023-01-01", dateModified="2023-01-02", type="example"), "active",
         "Research"),
        ProjectModel(_id=1, date_created="2023-01-01", date_modified="2023-01-02", status="active",
                     objective="Research"),
        id="happy_path_1"
      ),
      param(
        (MainOrmModel(id=2, dateCreated="2023-02-01", dateModified="2023-02-02", type="example"), "completed",
         "Development"),
        ProjectModel(_id=2, date_created="2023-02-01", date_modified="2023-02-02", status="completed",
                     objective="Development"),
        id="happy_path_2"
      ),
      # Edge case test cases
      param(
        (MainOrmModel(id=0, dateCreated="", dateModified="", type="example"), "", ""),
        ProjectModel(_id=0, date_created="", date_modified="", status="", objective=""),
        id="edge_case_empty_strings"
      ),
      param(
        (MainOrmModel(id=-1, dateCreated="2023-01-01", dateModified="2023-01-02", type="example"), "inactive",
         "Testing"),
        ProjectModel(_id=-1, date_created="2023-01-01", date_modified="2023-01-02", status="inactive",
                     objective="Testing"),
        id="edge_case_negative_id"
      )
    ],
    ids=lambda x: x[2]
  )
  def test_get_project_model(self, model, expected_project_model, request):
    # Act
    if request.node.callspec.id.startswith("error_case"):
      with pytest.raises(KeyError):
        result = DatabaseOrmAdapter.get_project_model(model)
    else:
      result = DatabaseOrmAdapter.get_project_model(model)

    # Assert
    if not request.node.callspec.id.startswith("error_case"):
      assert dict(result) == dict(expected_project_model)

  @pytest.mark.parametrize(
    "model_data, expected",
    [
      # Happy path tests
      param({"doc_type": "value1", "IRI": "value2"}, DataHierarchyModel(doc_type="value1", IRI="value2"),
            id="happy_path_1"),
      param({"title": "value3", "icon": "value4"}, DataHierarchyModel(title="value3", icon="value4"),
            id="happy_path_2"),

      # Edge cases
      param({}, DataHierarchyModel(), id="empty_model"),
      param({"shortcut": None, "view": "value"}, DataHierarchyModel(shortcut=None, view="value"),
            id="none_field_value"),
    ],
    ids=lambda x: x[2]
  )
  def test_get_data_hierarchy_model(self, model_data, expected, request):
    # Arrange
    model = DataHierarchyOrmModel(**model_data)

    # Act
    if request.node.callspec.id == "unexpected_field":
      with pytest.raises(TypeError):
        result = DatabaseOrmAdapter.get_data_hierarchy_model(model)
    else:
      result = DatabaseOrmAdapter.get_data_hierarchy_model(model)

    # Assert
    if request.node.callspec.id != "unexpected_field":
      assert dict(result) == dict(expected)
