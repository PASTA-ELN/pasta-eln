#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_base_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest

from pasta_eln.dataverse.base_model import BaseModel
from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError


class TestDataverseBaseModel:
  # Success path tests with various realistic test values
  @pytest.mark.parametrize("test_id, _id, _rev", [
    ("Success01", "123", "abc"),
    ("Success02", None, None),
    ("Success03", "unique-id", "rev-001"),
  ])
  def test_base_model_init_success_path(self, test_id, _id, _rev):
    # Arrange

    # Act
    model = BaseModel(_id=_id, _rev=_rev)

    # Assert
    assert model._id == _id
    assert model._rev == _rev

  # Various edge cases
  @pytest.mark.parametrize("test_id, _id, _rev", [
    ("EC01", "", ""),  # Empty strings
  ])
  def test_base_model_init_edge_cases(self, test_id, _id, _rev):
    # Arrange

    # Act
    model = BaseModel(_id=_id, _rev=_rev)

    # Assert
    assert model._id == _id
    assert model._rev == _rev

  # Various error cases
  @pytest.mark.parametrize("test_id, _id, _rev, expected_exception", [
    ("ERR01", 123, "abc", IncorrectParameterError),
    ("ERR02", "123", 456, IncorrectParameterError),
  ])
  def test_base_model_init_error_cases(self, test_id, _id, _rev, expected_exception):
    # Arrange

    # Act / Assert
    with pytest.raises(expected_exception):
      BaseModel(_id=_id, _rev=_rev)

  # Test __iter__ method
  @pytest.mark.parametrize("test_id, _id, _rev, expected_output", [
    ("ITER01", "123", "abc", [('_id', '123'), ('_rev', 'abc')]),
    ("ITER02", None, None, [('_id', None), ('_rev', None)]),
  ])
  def test_base_model_iter(self, test_id, _id, _rev, expected_output):
    # Arrange
    model = BaseModel(_id=_id, _rev=_rev)

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

  # Test property and setter for rev
  @pytest.mark.parametrize("test_id, initial_rev, new_rev", [
    ("PROP_REV01", "abc", "def"),
    ("PROP_REV02", None, "new-rev"),
  ])
  def test_base_model_rev_property_and_setter(self, test_id, initial_rev, new_rev):
    # Arrange
    model = BaseModel(_rev=initial_rev)

    # Act
    model.rev = new_rev

    # Assert
    assert model.rev == new_rev

  # Test deleter for rev
  @pytest.mark.parametrize("test_id, initial_rev", [
    ("DEL_REV01", "abc"),
    ("DEL_REV02", "delete-rev"),
  ])
  def test_base_model_rev_deleter(self, test_id, initial_rev):
    # Arrange
    model = BaseModel(_rev=initial_rev)

    # Act
    del model.rev

    # Assert
    assert not hasattr(model, 'rev')
