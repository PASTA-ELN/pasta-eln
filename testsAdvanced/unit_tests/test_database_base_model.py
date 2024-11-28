#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_database_base_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest

from pasta_eln.database.incorrect_parameter_error import IncorrectParameterError
from pasta_eln.database.models.base_model import BaseModel


class TestDatabaseBaseModel:
  # Success path tests with various realistic test values
  @pytest.mark.parametrize("test_id, _id", [
    ("Success01", "123"),
    ("Success02", None),
    ("Success03", "unique-id"),
  ])
  def test_base_model_init_success_path(self, test_id, _id):
    # Arrange

    # Act
    model = BaseModel(_id=_id)

    # Assert
    assert model._id == _id

  # Various edge cases
  @pytest.mark.parametrize("test_id, _id", [
    ("EC01", "",),  # Empty strings
  ])
  def test_base_model_init_edge_cases(self, test_id, _id):
    # Arrange

    # Act
    model = BaseModel(_id=_id)

    # Assert
    assert model._id == _id

  # Various error cases
  @pytest.mark.parametrize("test_id, _id, expected_exception", [
    ("ERR01", object(), IncorrectParameterError),
    ("ERR02", ["123"], IncorrectParameterError),
  ])
  def test_base_model_init_error_cases(self, test_id, _id, expected_exception):
    # Arrange

    # Act / Assert
    with pytest.raises(expected_exception):
      BaseModel(_id=_id)

  # Test __iter__ method
  @pytest.mark.parametrize("test_id, _id, expected_output", [
    ("ITER01", "123", [('id', '123')]),
    ("ITER02", None, [('id', None)]),
  ])
  def test_base_model_iter(self, test_id, _id, expected_output):
    # Arrange
    model = BaseModel(_id=_id)

    # Act
    output = list(model.__iter__())

    # Assert
    assert output == expected_output

  # Test property and setter for id
  @pytest.mark.parametrize("test_id, initial_id, new_id", [
    ("PROP01", "123", "456"),
    ("PROP02", None, "new-id"),
  ])
  def test_base_model_id_property_and_setter(self, test_id, initial_id, new_id):
    # Arrange
    model = BaseModel(_id=initial_id)

    # Act
    model.id = new_id

    # Assert
    assert model.id == new_id

  # Test deleter for id
  @pytest.mark.parametrize("test_id, initial_id", [
    ("DEL01", "123"),
    ("DEL02", "delete-me"),
  ])
  def test_base_model_id_deleter(self, test_id, initial_id):
    # Arrange
    model = BaseModel(_id=initial_id)

    # Act
    del model.id

    # Assert
    assert not hasattr(model, 'id')
