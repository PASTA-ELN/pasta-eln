#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_data_type_class_factory.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout

from pasta_eln.GUI.dataverse.compound_data_type_class import CompoundDataTypeClass
from pasta_eln.GUI.dataverse.controlled_vocabulary_data_type_class import ControlledVocabularyDataTypeClass
from pasta_eln.GUI.dataverse.data_type_class_context import DataTypeClassContext
from pasta_eln.GUI.dataverse.data_type_class_factory import DataTypeClassFactory
from pasta_eln.GUI.dataverse.data_type_class_names import DataTypeClassName
from pasta_eln.GUI.dataverse.primitive_data_type_class import PrimitiveDataTypeClass


@pytest.fixture
def context(mocker):
  return DataTypeClassContext(
    mocker.MagicMock(spec=QVBoxLayout),
    mocker.MagicMock(spec=QPushButton),
    mocker.MagicMock(spec=QFrame),
    {})


@pytest.fixture
def factory(context):
  return DataTypeClassFactory(context)


class TestDataTypeClassFactory:

  @pytest.mark.parametrize('class_name, expected_type', [
    (DataTypeClassName.PRIMITIVE, PrimitiveDataTypeClass),
    (DataTypeClassName.COMPOUND, CompoundDataTypeClass),
    (DataTypeClassName.CONTROLLED_VOCAB, ControlledVocabularyDataTypeClass)
  ], ids=['primitive', 'compound', 'controlled_vocab'])
  def test_make_data_type_class(self, factory, class_name, expected_type):
    # Act
    result = factory.make_data_type_class(class_name)

    # Assert
    assert isinstance(result, expected_type)

  @pytest.mark.parametrize('class_name', [
    'INVALID_CLASS_NAME',
    None,
    123
  ], ids=['invalid_string', 'none', 'integer'])
  def test_make_data_type_class_invalid(self, factory, class_name):
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
      factory.make_data_type_class(class_name)

    assert str(exc_info.value) == f"Invalid data type class name: {class_name}"

  def test_new_instance(self, context):
    # Act
    instance = DataTypeClassFactory(context)

    # Assert
    assert isinstance(instance, DataTypeClassFactory)

  def test_init(self, factory, context):
    # Assert
    assert factory.context == context
    assert DataTypeClassName.PRIMITIVE in factory.factory_map
    assert DataTypeClassName.COMPOUND in factory.factory_map
    assert DataTypeClassName.CONTROLLED_VOCAB in factory.factory_map

  def test_make_primitive_data_type_class(self, factory, context):
    # Act
    result = factory.make_primitive_data_type_class()

    # Assert
    assert isinstance(result, PrimitiveDataTypeClass)
    assert result.context == context

  def test_make_compound_data_type_class(self, factory, context):
    # Act
    result = factory.make_compound_data_type_class()

    # Assert
    assert isinstance(result, CompoundDataTypeClass)
    assert result.context == context

  def test_make_controlled_vocab_data_type_class(self, factory, context):
    # Act
    result = factory.make_controlled_vocab_data_type_class()

    # Assert
    assert isinstance(result, ControlledVocabularyDataTypeClass)
    assert result.context == context
