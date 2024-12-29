#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_database_properties_orm_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.database.models.properties_orm_model import PropertiesOrmModel


class TestDatabaseOrmPropertiesModel:
  @pytest.mark.parametrize(
    'id_value, key_value, value_value, unit_value, expected_columns',
    [
      # Happy path test cases
      ('1', 'temperature', '25', 'C', ['id', 'key', 'value', 'unit']),
      ('2', 'pressure', '101.3', 'kPa', ['id', 'key', 'value', 'unit']),

      # Edge cases
      ('', '', None, None, ['id', 'key', 'value', 'unit']),  # Empty strings and None
      ('3', 'humidity', '', '', ['id', 'key', 'value', 'unit']),  # Empty value and unit

      # Error cases
      # Note: Since the class does not have methods that raise exceptions or handle errors,
      # we cannot directly test error cases without modifying the class.
    ],
    ids=[
      'happy_path_temperature',
      'happy_path_pressure',
      'edge_case_empty_strings_and_none',
      'edge_case_empty_value_and_unit',
    ]
  )
  def test_get_table_columns(self, id_value, key_value, value_value, unit_value, expected_columns):
    # Act
    columns = PropertiesOrmModel.get_table_columns()

    # Assert
    assert columns == expected_columns
