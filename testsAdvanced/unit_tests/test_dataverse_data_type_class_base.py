#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_data_type_class_base.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout

from pasta_eln.GUI.dataverse.data_type_class_base import DataTypeClass
from pasta_eln.GUI.dataverse.data_type_class_context import DataTypeClassContext


class ConcreteDataTypeClass(DataTypeClass):
  def add_new_entry(self) -> None:
    raise NotImplementedError

  def populate_entry(self) -> None:
    raise NotImplementedError

  def save_modifications(self) -> None:
    raise NotImplementedError


@pytest.fixture
def valid_context(mocker):
  return DataTypeClassContext(
    mocker.MagicMock(spec=QVBoxLayout),
    mocker.MagicMock(spec=QPushButton),
    mocker.MagicMock(spec=QFrame),
    {})


class TestConcreteDataTypeClass:

  @pytest.mark.parametrize(
    'context, expected_exception',
    [
      ('valid_context', None),
      (None, TypeError),
      ('invalid_context', TypeError),
    ],
    ids=['valid_context', 'none_context', 'string_context']
  )
  def test_init(self, context, expected_exception, request):
    # Act and Assert
    if expected_exception:
      with pytest.raises(expected_exception):
        ConcreteDataTypeClass(context)
    else:
      instance = ConcreteDataTypeClass(request.getfixturevalue(context))
      assert instance.context == request.getfixturevalue(context)

  @pytest.mark.parametrize(
    'args, kwargs, expected_type',
    [
      ((), {}, ConcreteDataTypeClass),
      ((1, 2, 3), {}, ConcreteDataTypeClass),
      ((), {'key': 'value'}, ConcreteDataTypeClass),
    ],
    ids=['no_args', 'positional_args', 'keyword_args']
  )
  def test_new(self, args, kwargs, expected_type):
    # Act
    instance = ConcreteDataTypeClass.__new__(ConcreteDataTypeClass, *args, **kwargs)

    # Assert
    assert isinstance(instance, expected_type)

  def test_abstract_methods(self, valid_context):
    # Arrange
    instance = ConcreteDataTypeClass(valid_context)

    # Act and Assert
    with pytest.raises(NotImplementedError):
      instance.add_new_entry()

    with pytest.raises(NotImplementedError):
      instance.populate_entry()

    with pytest.raises(NotImplementedError):
      instance.save_modifications()
