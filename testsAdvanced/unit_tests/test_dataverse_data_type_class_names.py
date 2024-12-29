#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_data_type_class_names.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.GUI.dataverse.data_type_class_names import DataTypeClassName


class TestDataTypeClassName:
  @pytest.mark.parametrize(
    'data_type, expected_str',
    [
      (DataTypeClassName.PRIMITIVE, 'primitive'),
      (DataTypeClassName.COMPOUND, 'compound'),
      (DataTypeClassName.CONTROLLED_VOCAB, 'controlledVocabulary'),
    ],
    ids=[
      'primitive_str',
      'compound_str',
      'controlled_vocab_str'
    ]
  )
  def test_data_type_class_name_str(self, data_type, expected_str):
    # Act
    result = str(data_type)

    # Assert
    assert result == expected_str

  @pytest.mark.parametrize(
    'data_type, expected_value',
    [
      (DataTypeClassName.PRIMITIVE, 'primitive'),
      (DataTypeClassName.COMPOUND, 'compound'),
      (DataTypeClassName.CONTROLLED_VOCAB, 'controlledVocabulary'),
    ],
    ids=[
      'primitive_value',
      'compound_value',
      'controlled_vocab_value'
    ]
  )
  def test_data_type_class_name_value(self, data_type, expected_value):
    # Act
    result = data_type.value

    # Assert
    assert result == expected_value

  @pytest.mark.parametrize(
    'invalid_value',
    [
      'simple',
      'complex',
      'vocabulary',
    ],
    ids=[
      'invalid_simple',
      'invalid_complex',
      'invalid_vocabulary'
    ]
  )
  def test_data_type_class_name_invalid(self, invalid_value):
    # Act and Assert
    with pytest.raises(ValueError):
      DataTypeClassName(invalid_value)
