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
  # Test IDs for different scenarios
  SUCCESS_PATH_ID = "Success Path"
  EDGE_CASE_ID = "Edge Case"
  ERROR_CASE_ID = "Error Case"

  # Test values for success path
  success_path_params = [
    (SUCCESS_PATH_ID, "1", "rev1", "Project A", "Initial comment", "user1", "2023-01-01", "active", "Research"),
    (SUCCESS_PATH_ID, "2", "rev2", "Project B", "Follow-up comment", "user2", "2023-01-02", "completed", "Development"),
  ]

  # Test values for edge cases
  edge_case_params = [
    (EDGE_CASE_ID, "", "", "", "", "", "", "", ""),
    (EDGE_CASE_ID, None, None, None, None, None, None, None, None),
  ]

  @pytest.mark.parametrize("test_id, _id, _rev, name, comment, user, date, status, objective",
                           success_path_params)
  def test_dataverse_project_model_happy_path(self,
                                              test_id,
                                              _id,
                                              _rev,
                                              name,
                                              comment,
                                              user,
                                              date,
                                              status,
                                              objective):
    # Arrange
    # All input values are provided via test parameters, so we omit the Arrange section.

    # Act
    project = ProjectModel(_id, _rev, name, comment, user, date, status, objective)

    # Assert
    assert project.id == _id
    assert project.rev == _rev
    assert project.name == name
    assert project.comment == comment
    assert project.user == user
    assert project.date == date
    assert project.status == status
    assert project.objective == objective

  @pytest.mark.parametrize("test_id, _id, _rev, name, comment, user, date, status, objective", edge_case_params)
  def test_dataverse_project_model_edge_cases(self,
                                              test_id,
                                              _id,
                                              _rev,
                                              name,
                                              comment,
                                              user,
                                              date,
                                              status,
                                              objective):
    # Arrange
    # All input values are provided via test parameters, so we omit the Arrange section.

    # Act
    project = ProjectModel(_id, _rev, name, comment, user, date, status, objective)

    # Assert
    assert project.id == _id
    assert project.rev == _rev
    assert project.name == name
    assert project.comment == comment
    assert project.user == user
    assert project.date == date
    assert project.status == status
    assert project.objective == objective

  @pytest.mark.parametrize("test_id, attribute, value, expected_exception", [
    ("ERR-1", "name", 123, IncorrectParameterError),
    ("ERR-2", "comment", 123.45, IncorrectParameterError),
    ("ERR-3", "user", ["user1"], IncorrectParameterError),
    # Add more test cases as needed
  ])
  def test_project_model_error_cases(self, test_id, attribute, value, expected_exception):
    # Arrange
    kwargs = {
      "_id": "123",
      "_rev": "rev1",
      "name": "Project Alpha",
      "comment": "Initial phase",
      "user": "user1",
      "date": "2023-01-01",
      "status": "active",
      "objective": "Research",
      attribute: value,
    }
    # Act / Assert
    with pytest.raises(expected_exception):
      ProjectModel(**kwargs)
