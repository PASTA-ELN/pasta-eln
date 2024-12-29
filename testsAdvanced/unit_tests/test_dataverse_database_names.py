#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_database_names.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.dataverse.database_names import DatabaseNames


class TestDatabaseNames:
  @pytest.mark.parametrize('db_name, expected_value', [
    (DatabaseNames.DataverseDatabase, 1),
    (DatabaseNames.PastaProjectGroupDatabase, 2),
  ], ids=[
    'DataverseDatabase has value 1',
    'PastaProjectGroupDatabase has value 2'
  ])
  def test_database_names_enum_values(self, db_name, expected_value):
    # Act
    result = db_name.value

    # Assert
    assert result == expected_value

  @pytest.mark.parametrize('db_name, expected_name', [
    (DatabaseNames.DataverseDatabase, 'DataverseDatabase'),
    (DatabaseNames.PastaProjectGroupDatabase, 'PastaProjectGroupDatabase'),
  ], ids=[
    "DataverseDatabase has name 'DataverseDatabase'",
    "PastaProjectGroupDatabase has name 'PastaProjectGroupDatabase'"
  ])
  def test_database_names_enum_names(self, db_name, expected_name):
    # Act
    result = db_name.name

    # Assert
    assert result == expected_name

  @pytest.mark.parametrize('invalid_value', [
    0,
    3,
    'DataverseDatabase',
    None
  ], ids=[
    'Invalid value 0',
    'Invalid value 3',
    "Invalid string 'DataverseDatabase'",
    'None as invalid value'
  ])
  def test_database_names_invalid_cases(self, invalid_value):
    # Act and Assert
    with pytest.raises(ValueError):
      DatabaseNames(invalid_value)
