#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_data_type_info.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.dataverse.data_type_info import DataTypeInfo
from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError


class TestDataHierarchyDataTypeInfo:
  def test_init(self):
    data_type_info = DataTypeInfo()
    assert data_type_info.datatype == ""
    assert data_type_info.title == ""
    assert data_type_info.iri == ""
    assert data_type_info.icon == ""
    assert data_type_info.shortcut == ""

  @pytest.mark.parametrize(
    "datatype, title, iri, icon, shortcut",
    [
      ("type1", "Title1", "http://example.com/iri1", "icon1", "shortcut1"),
      ("type2", "Title2", "http://example.com/iri2", "icon2", "shortcut2"),
      ("type3", "Title3", "http://example.com/iri3", "icon3", "shortcut3"),
    ],
    ids=["case1", "case2", "case3"]
  )
  def test_data_type_info_happy_path(self, datatype, title, iri, icon, shortcut):
    # Arrange
    data_type_info = DataTypeInfo()

    # Act
    data_type_info.datatype = datatype
    data_type_info.title = title
    data_type_info.iri = iri
    data_type_info.icon = icon
    data_type_info.shortcut = shortcut

    # Assert
    assert data_type_info.datatype == datatype
    assert data_type_info.title == title
    assert data_type_info.iri == iri
    assert data_type_info.icon == icon
    assert data_type_info.shortcut == shortcut

  @pytest.mark.parametrize(
    "attribute, value, expected_exception",
    [
      ("datatype", 123, IncorrectParameterError),
      ("title", 123, IncorrectParameterError),
      ("iri", 123, IncorrectParameterError),
      ("icon", 123, IncorrectParameterError),
      ("shortcut", 123, IncorrectParameterError),
    ],
    ids=["datatype_int", "title_int", "iri_int", "icon_int", "shortcut_int"]
  )
  def test_data_type_info_error_cases(self, attribute, value, expected_exception):
    # Arrange
    data_type_info = DataTypeInfo()

    # Act & Assert
    with pytest.raises(expected_exception):
      setattr(data_type_info, attribute, value)

  @pytest.mark.parametrize(
    "attribute, value",
    [
      ("datatype", ""),
      ("title", None),
      ("iri", None),
      ("icon", None),
      ("shortcut", None),
    ],
    ids=["empty_datatype", "none_title", "none_iri", "none_icon", "none_shortcut"]
  )
  def test_data_type_info_edge_cases(self, attribute, value):
    # Arrange
    data_type_info = DataTypeInfo()

    # Act
    setattr(data_type_info, attribute, value)

    # Assert
    assert getattr(data_type_info, attribute) == value

  def test_data_type_info_iteration(self):
    # Arrange
    data_type_info = DataTypeInfo()
    data_type_info.datatype = "type1"
    data_type_info.title = "Title1"
    data_type_info.iri = "http://example.com/iri1"
    data_type_info.icon = "icon1"
    data_type_info.shortcut = "shortcut1"

    # Act
    items = list(data_type_info)

    # Assert
    expected_items = [
      ("datatype", "type1"),
      ("title", "Title1"),
      ("iri", "http://example.com/iri1"),
      ("icon", "icon1"),
      ("shortcut", "shortcut1"),
    ]
    assert items == expected_items
