#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_icon_names.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from unittest.mock import MagicMock, patch

import pytest

from pasta_eln.GUI.data_hierarchy.qtaicons_factory import QTAIconsFactory
from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError


@pytest.fixture
def qta_icons_factory(mocker):
  mocker.patch("pasta_eln.GUI.data_hierarchy.qtaicons_factory.logging")
  iconic_mock = mocker.MagicMock()
  iconic_mock.charmap = {
    'fa': ['value1', 'value2'],
    'fa5': ['value3', 'value4'],
    'fa5s': ['value5', 'value13'],
    'fa5b': ['value6', 'value14'],
    'ei': ['value7', 'value15'],
    'mdi': ['value8', 'value16'],
    'mdi6': ['value9', 'value17'],
    'ph': ['value10', 'value18'],
    'ri': ['value11', 'value19'],
    'msc': ['value12', 'value20'],
  }
  mocker.patch("pasta_eln.GUI.data_hierarchy.qtaicons_factory.qta._resource", {"iconic": iconic_mock})
  return QTAIconsFactory.get_instance()


class TestDataHierarchyQTAIconsFactory:

  @pytest.mark.parametrize("description", [
    pytest.param("First call to get_instance", id="first_call"),
    pytest.param("Subsequent call to get_instance", id="subsequent_call"),
  ])
  def test_get_instance_singleton_behavior(self, description):
    # Act
    instance1 = QTAIconsFactory.get_instance()
    instance2 = QTAIconsFactory.get_instance()

    # Assert
    assert instance1 is instance2, "get_instance should return the same instance on subsequent calls"

  @pytest.mark.parametrize("description", [
    pytest.param("Check instance type", id="check_instance_type"),
  ])
  def test_get_instance_type(self, description):
    # Act
    instance = QTAIconsFactory.get_instance()

    # Assert
    assert isinstance(instance, QTAIconsFactory), "get_instance should return an instance of YourClassName"

  @pytest.mark.parametrize("description", [
    pytest.param("Check instance attribute existence", id="check_instance_attribute"),
  ])
  def test_get_instance_attribute_existence(self, description):
    # Arrange
    QTAIconsFactory.get_instance()

    # Act
    has_instance_attr = hasattr(QTAIconsFactory, '_instance')

    # Assert
    assert has_instance_attr, "Class should have '_instance' attribute after get_instance is called"

  @pytest.mark.parametrize(
    "has_instance",
    [
      (True),
      (False)
    ],
    ids=["instance_attribute_exists_but_not_initialized", "instance_attribute_does_not_exist"]
  )
  def test_init(self, mocker, has_instance):
    mocker.resetall()
    if has_instance:
      QTAIconsFactory._instance = None
    else:
      delattr(QTAIconsFactory, "_instance")
    mock_logging = mocker.patch("pasta_eln.GUI.data_hierarchy.qtaicons_factory.logging")
    mock_set_icon_names = mocker.patch(
      "pasta_eln.GUI.data_hierarchy.qtaicons_factory.QTAIconsFactory.set_icon_names")

    instance = QTAIconsFactory.get_instance()
    mock_logging.getLogger.assert_called_once_with("pasta_eln.GUI.data_hierarchy.qtaicons_factory.QTAIconsFactory")
    mock_set_icon_names.assert_called_once()

    assert instance.icon_names == {}
    assert instance._icons_initialized == False
    assert instance._font_collections == ['fa', 'fa5', 'fa5s', 'fa5b', 'ei', 'mdi', 'mdi6', 'ph', 'ri', 'msc']

  def test_only_one_instance_created(self, qta_icons_factory):
    for _ in range(5):
      instance = QTAIconsFactory.get_instance()
      assert instance is qta_icons_factory

  @pytest.mark.parametrize(
    "font_collections, expected",
    [
      (['fa', 'fa5'], {'fa': ['No value', 'fa.value1', 'fa.value2'], 'fa5': ['No value', 'fa5.value3', 'fa5.value4']}),
      (['mdi'], {'mdi': ['No value', 'mdi.value8', 'mdi.value16']}),
      ([], {}),
    ],
    ids=["two_collections", "one_collection", "empty_collection"]
  )
  def test_set_icon_names(self, qta_icons_factory, font_collections, expected):
    # Arrange
    qta_icons_factory._icons_initialized = False
    qta_icons_factory.font_collections = font_collections

    # Act
    qta_icons_factory.set_icon_names()

    # Assert
    assert qta_icons_factory.icon_names == expected
    assert qta_icons_factory._icons_initialized

  @pytest.mark.parametrize(
    "font_collections, expected_exception",
    [
      (None, IncorrectParameterError),
      ("not_a_list", IncorrectParameterError),
    ],
    ids=["None_type", "string_type"]
  )
  def test_font_collections_setter_invalid(self, qta_icons_factory, font_collections, expected_exception):
    # Act & Assert
    with pytest.raises(expected_exception):
      qta_icons_factory.font_collections = font_collections

  @pytest.mark.parametrize(
    "icon_names, expected_exception",
    [
      (None, IncorrectParameterError),
      ("not_a_dict", IncorrectParameterError),
    ],
    ids=["None_type", "string_type"]
  )
  def test_icon_names_setter_invalid(self, qta_icons_factory, icon_names, expected_exception):
    # Act & Assert
    with pytest.raises(expected_exception):
      qta_icons_factory.icon_names = icon_names

  def test_icon_names_property_initialization(self, qta_icons_factory):
    # Act
    icon_names = qta_icons_factory.icon_names

    # Assert
    assert qta_icons_factory._icons_initialized
    assert icon_names == qta_icons_factory._icon_names

  def test_set_icon_names_already_initialized(self, qta_icons_factory):
    # Arrange
    qta_icons_factory._icons_initialized = True

    # Act
    with patch.object(qta_icons_factory.logger, 'warning') as mock_warning:
      qta_icons_factory.set_icon_names()

    # Assert
    mock_warning.assert_called_once_with("Icons already initialized!")

  def test_set_icon_names_no_font_maps(self, mocker, qta_icons_factory):
    # Arrange
    qta_icons_factory.logger = mocker.MagicMock()
    qta_icons_factory._icons_initialized = False
    mocker.patch("pasta_eln.GUI.data_hierarchy.qtaicons_factory.qta._resource", {"iconic": MagicMock(charmap=None)})

    # Act
    qta_icons_factory.set_icon_names()

    # Assert
    qta_icons_factory.logger.warning.assert_called_once_with("font_maps could not be found!")
