#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_project_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError
from pasta_eln.dataverse.project_model import ProjectModel


class TestDataverseProjectModel:
  # Success path tests with various realistic test values
  @pytest.mark.parametrize("test_id, _id, name, comment, user, date_created, date_modified, status, objective", [
    ("Success-01", "123", "Project Alpha", "Initial phase", "user1", "2023-01-01", "2023-01-01", "Active", "Research"),
    ("Success-02", None, None, None, None, None, None, None, None),  # Testing defaults
    ("Success-03", "456", "", "", "", "", "", "", ""),  # Testing empty strings
  ])
  def test_project_model_creation_happy_path(self, test_id, _id, name, comment, user, date_created, date_modified,
                                             status, objective):
    # Arrange - omitted as inputs are provided via test parameters

    # Act
    project = ProjectModel(_id=_id, name=name, comment=comment, user=user, date_created=date_created,
                           date_modified=date_modified, status=status,
                           objective=objective)

    # Assert
    assert project.id == _id
    assert project.name == name
    assert project.comment == comment
    assert project.user == user
    assert project.date_created == date_created
    assert project.date_modified == date_modified
    assert project.status == status
    assert project.objective == objective

  # Various edge cases
  @pytest.mark.parametrize("test_id, attribute, value", [
    ("EC-01", "name", 123),  # Non-string value
    ("EC-02", "comment", 456.78),  # Non-string value
    ("EC-03", "user", True),  # Non-string value
    ("EC-04", "date_created", []),  # Non-string value
    ("EC-05", "status", {}),  # Non-string value
    ("EC-06", "objective", (lambda x: x)),  # Non-string value
    ("EC-07", "date_modified", (lambda x: x)),  # Non-string value
  ])
  def test_project_model_setters_edge_cases(self, test_id, attribute, value):
    project = ProjectModel()

    # Act and Assert
    with pytest.raises(IncorrectParameterError):
      setattr(project, attribute, value)

  # Various error cases for __init__
  @pytest.mark.parametrize("test_id, kwargs, expected_exception_message", [
    ("ERR-01", {"name": 123}, "Expected string type for name but got <class 'int'>"),
    ("ERR-02", {"comment": 456.78}, "Expected string type for comment but got <class 'float'>"),
    ("ERR-03", {"user": True}, "Expected string type for user but got <class 'bool'>"),
    ("ERR-04", {"date_created": []}, "Expected string type for date_created but got <class 'list'>"),
    ("ERR-05", {"status": {}}, "Expected string type for status but got <class 'dict'>"),
    ("ERR-06", {"objective": lambda x: x}, "Expected string type for objective but got <class 'function'>"),
    ("ERR-06", {"date_modified": lambda x: x}, "Expected string type for date_modified but got <class 'function'>"),
  ])
  def test_project_model_creation_error_cases(self, test_id, kwargs, expected_exception_message):
    # Arrange - omitted as inputs are provided via test parameters

    # Act and Assert
    with pytest.raises(IncorrectParameterError) as exc_info:
      ProjectModel(**kwargs)
    assert str(exc_info.value) == expected_exception_message

  @pytest.mark.parametrize("test_input, expected, test_id", [
    ("Project A", "Project A", "normal_string"),
    ("", "", "empty_string"),
    (None, None, "none_value")
  ])
  def test_name_setter_success_path(self, test_input, expected, test_id):
    # Arrange
    project = ProjectModel()

    # Act
    project.name = test_input

    # Assert
    assert project.name == expected, "The name property should correctly reflect the set value."

  @pytest.mark.parametrize("test_input, expected, test_id", [
    ("Comment A", "Comment A", "normal_string"),
    ("", "", "empty_string"),
    (None, None, "none_value")
  ])
  def test_comment_setter_success_path(self, test_input, expected, test_id):
    # Arrange
    project = ProjectModel()

    # Act
    project.comment = test_input

    # Assert
    assert project.comment == expected, "The comment property should correctly reflect the set value."

  @pytest.mark.parametrize("test_input, expected, test_id", [
    ("2024-01-01", "2024-01-01", "normal_string"),
    ("", "", "empty_string"),
    (None, None, "none_value")
  ])
  def test_date_setter_success_path(self, test_input, expected, test_id):
    # Arrange
    project = ProjectModel()

    # Act
    project.date = test_input

    # Assert
    assert project.date == expected, "The date property should correctly reflect the set value."

  @pytest.mark.parametrize("test_input, expected, test_id", [
    ("User A", "User A", "normal_string"),
    ("", "", "empty_string"),
    (None, None, "none_value")
  ])
  def test_user_setter_success_path(self, test_input, expected, test_id):
    # Arrange
    project = ProjectModel()

    # Act
    project.user = test_input

    # Assert
    assert project.user == expected, "The user property should correctly reflect the set value."

  @pytest.mark.parametrize("test_input, expected, test_id", [
    ("Status", "Status", "normal_string"),
    ("", "", "empty_string"),
    (None, None, "none_value")
  ])
  def test_status_setter_success_path(self, test_input, expected, test_id):
    # Arrange
    project = ProjectModel()

    # Act
    project.status = test_input

    # Assert
    assert project.status == expected, "The status property should correctly reflect the set value."

  @pytest.mark.parametrize("test_input, expected, test_id", [
    ("Objective", "Objective", "normal_string"),
    ("", "", "empty_string"),
    (None, None, "none_value")
  ])
  def test_objective_setter_success_path(self, test_input, expected, test_id):
    # Arrange
    project = ProjectModel()

    # Act
    project.objective = test_input

    # Assert
    assert project.objective == expected, "The objective property should correctly reflect the set value."

  # Parametrized test for various error case
  @pytest.mark.parametrize("test_input, attribute, test_id", [
    (123, "name", "name_integer"),
    (12.34, "name", "name_float"),
    ([], "name", "name_empty_list"),
    ({}, "name", "name_empty_dict"),
    (True, "name", "name_boolean"),
    (123, "comment", "comment_integer"),
    (12.34, "comment", "comment_float"),
    ([], "comment", "comment_empty_list"),
    ({}, "comment", "comment_empty_dict"),
    (True, "comment", "comment_boolean"),
    (123, "user", "user_integer"),
    (12.34, "user", "user_float"),
    ([], "user", "user_empty_list"),
    ({}, "user", "user_empty_dict"),
    (True, "user", "user_boolean"),
    (123, "status", "status_integer"),
    (12.34, "status", "status_float"),
    ([], "status", "status_empty_list"),
    ({}, "status", "status_empty_dict"),
    (True, "objective", "objective_boolean"),
    (123, "objective", "objective_integer"),
    (12.34, "objective", "objective_float"),
    ([], "objective", "objective_empty_list"),
    ({}, "objective", "objective_empty_dict"),
    (True, "objective", "objective_boolean"),
    (123, "date_modified", "date_modified_integer"),
    (12.34, "date_modified", "date_modified_float"),
    ([], "date_modified", "date_modified_empty_list"),
    ({}, "date_created", "date_created_empty_dict"),
    (True, "date_created", "date_created_boolean")
  ])
  def test_setter_error_cases(self, test_input, attribute, test_id):
    # Arrange
    project = ProjectModel()

    # Act & Assert
    with pytest.raises(IncorrectParameterError) as exc_info:
      setattr(project, attribute, test_input)
    assert str(exc_info.value) == f"Expected string type for {attribute} but got {type(test_input)}", \
      "An IncorrectParameterError should be raised for non-string inputs."

  @pytest.mark.parametrize("initial_value, attribute, expected_exception", [
    ("Project Alpha", "name", None),
    ("", "name", None),
    ("Comment", "comment", None),
    ("", "comment", None),
    ("User", "user", None),
    ("", "user", None),
    ("Status", "status", None),
    ("", "status", None),
    ("Objective", "objective", None),
    ("", "objective", None),
    ("Date", "date", None),
    ("", "date", None)
  ], ids=["name-success-valid", "name-edge-empty-string",
          "comment-success-valid", "comment-edge-empty-string",
          "user-success-valid", "user-edge-empty-string",
          "status-success-valid", "status-edge-empty-string",
          "objective-success-valid", "objective-edge-empty-string",
          "date-success-valid", "date-edge-empty-string"])
  def test_deleter(self, initial_value, attribute, expected_exception):
    project = ProjectModel()

    # Arrange
    if initial_value is not None:
      setattr(project, attribute, initial_value)

    # Act and Assert
    if expected_exception:
      with pytest.raises(expected_exception):
        delattr(project, attribute)
    else:
      delattr(project, attribute)
      with pytest.raises(AttributeError):  # Asserting that _name is indeed deleted
        _ = getattr(project, attribute)
