#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_data_type_info_validator.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.GUI.data_hierarchy.data_type_info import DataTypeInfo
from pasta_eln.GUI.data_hierarchy.data_type_info_validator import DataTypeInfoValidator


class TestDataHierarchyDataTypeInfoValidator:

  @pytest.mark.parametrize(
    'data_type_info, expected_exception, test_id',
    [
      # Success path tests
      ({'datatype': 'text', 'title': 'Sample Title'}, None, 'valid_data_type_info'),

      # Edge cases
      ({'datatype': '', 'title': 'Sample Title'}, ValueError, 'missing_datatype'),
      ({'datatype': 'text', 'title': ''}, ValueError, 'missing_title'),

      # Error cases
      (None, TypeError, 'none_data_type_info'),
      ('invalid_type', TypeError, 'string_data_type_info'),
      (123, TypeError, 'integer_data_type_info'),
    ],
    ids=[
      'valid_data_type_info',
      'missing_datatype',
      'missing_title',
      'none_data_type_info',
      'string_data_type_info',
      'integer_data_type_info',
    ]
  )
  def test_validate(self, data_type_info, expected_exception, test_id):
    # Arrange
    if isinstance(data_type_info, dict):
      data_type = DataTypeInfo()
      for key, value in data_type_info.items():
        setattr(data_type, key, value)
      data_type_info = data_type

    # Act
    if expected_exception:
      # Assert
      with pytest.raises(expected_exception):
        DataTypeInfoValidator.validate(data_type_info)
    else:
      # Act
      DataTypeInfoValidator.validate(data_type_info)
      # Assert
      # No exception should be raised
