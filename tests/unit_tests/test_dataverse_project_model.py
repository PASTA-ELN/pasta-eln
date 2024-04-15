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
  @pytest.mark.parametrize("test_id, _id, _rev, name, comment, user, date, status, objective", [
    ("Success-01", "123", "rev1", "Project Alpha", "Initial phase", "user1", "2023-01-01", "Active", "Research"),
    ("Success-02", None, None, None, None, None, None, None, None),  # Testing defaults
    ("Success-03", "456", "rev2", "", "", "", "", "", ""),  # Testing empty strings
  ])
  def test_project_model_creation_happy_path(self, test_id, _id, _rev, name, comment, user, date, status, objective):
    # Arrange - omitted as inputs are provided via test parameters

    # Act
    project = ProjectModel(_id=_id, _rev=_rev, name=name, comment=comment, user=user, date=date, status=status,
                           objective=objective)

    # Assert
    assert project.id == _id
    assert project.rev == _rev
    assert project.name == name
    assert project.comment == comment
    assert project.user == user
    assert project.date == date
    assert project.status == status
    assert project.objective == objective

  # Various edge cases
  @pytest.mark.parametrize("test_id, attribute, value", [
    ("EC-01", "name", 123),  # Non-string value
    ("EC-02", "comment", 456.78),  # Non-string value
    ("EC-03", "user", True),  # Non-string value
    ("EC-04", "date", []),  # Non-string value
    ("EC-05", "status", {}),  # Non-string value
    ("EC-06", "objective", (lambda x: x)),  # Non-string value
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
    ("ERR-04", {"date": []}, "Expected string type for date but got <class 'list'>"),
    ("ERR-05", {"status": {}}, "Expected string type for status but got <class 'dict'>"),
    ("ERR-06", {"objective": lambda x: x}, "Expected string type for objective but got <class 'function'>"),
  ])
  def test_project_model_creation_error_cases(self, test_id, kwargs, expected_exception_message):
    # Arrange - omitted as inputs are provided via test parameters

    # Act and Assert
    with pytest.raises(IncorrectParameterError) as exc_info:
      ProjectModel(**kwargs)
    assert str(exc_info.value) == expected_exception_message
