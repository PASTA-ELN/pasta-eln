#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_primitive_compound_frame.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout

from pasta_eln.GUI.dataverse.data_type_class_context import DataTypeClassContext
from pasta_eln.GUI.dataverse.data_type_class_names import DataTypeClassName
from pasta_eln.GUI.dataverse.primitive_compound_frame import PrimitiveCompoundFrame


@pytest.fixture
def mock_data_type_class_factory():
  with patch('pasta_eln.GUI.dataverse.primitive_compound_frame.DataTypeClassFactory') as mock_factory:
    yield mock_factory


@pytest.fixture
def mock_data_type_class():
  with patch('pasta_eln.GUI.dataverse.primitive_compound_frame.DataTypeClass') as mock_class:
    yield mock_class


@pytest.fixture
def mock_qframe():
  with patch('pasta_eln.GUI.dataverse.primitive_compound_frame.QFrame') as mock_frame:
    mock_frame.return_value = MagicMock(spec=QFrame)
    yield mock_frame


@pytest.fixture
def mock_logger():
  with patch('pasta_eln.GUI.dataverse.primitive_compound_frame.logging.getLogger') as mock_logger:
    yield mock_logger


@pytest.fixture
def mock_primitive_compound_frame(mocker, mock_logger, mock_data_type_class_factory, mock_data_type_class, mock_qframe):
  mocker.patch(
    "pasta_eln.GUI.dataverse.primitive_compound_controlled_frame_base.Ui_PrimitiveCompoundControlledFrameBase.setupUi")
  mocker.patch.object(PrimitiveCompoundFrame, 'addPushButton', MagicMock(spec=QPushButton), create=True)
  mocker.patch.object(PrimitiveCompoundFrame, 'mainVerticalLayout', MagicMock(spec=QVBoxLayout), create=True)
  frame = PrimitiveCompoundFrame({"typeClass": "primitive", "multiple": False, "value": "test_value"})
  mocker.resetall()
  yield frame


class TestDataversePrimitiveCompoundFrame:

  @pytest.mark.parametrize("meta_field, expected_type_class", [
    ({"typeClass": "primitive"}, DataTypeClassName("primitive")),
    ({"typeClass": "compound"}, DataTypeClassName("compound")),
    ({"typeClass": "controlledVocabulary"}, DataTypeClassName("controlledVocabulary")),
  ], ids=["type_class_primitive", "type_class_compound", "type_class_controlledVocabulary"])
  def test_primitive_compound_frame_initialization(self, mocker, mock_logger, mock_data_type_class_factory,
                                                   mock_data_type_class, mock_qframe, meta_field, expected_type_class):
    # Arrange
    mock_setup_ui = mocker.patch(
      "pasta_eln.GUI.dataverse.primitive_compound_controlled_frame_base.Ui_PrimitiveCompoundControlledFrameBase.setupUi")
    mock_metadata_frame_init = mocker.patch(
      "pasta_eln.GUI.dataverse.metadata_frame_base.MetadataFrame.__init__")
    mock_data_type_class_context = mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.DataTypeClassContext',
                                                MagicMock(spec=DataTypeClassContext))
    mocker.patch.object(PrimitiveCompoundFrame, 'addPushButton', MagicMock(spec=QPushButton), create=True)
    mocker.patch.object(PrimitiveCompoundFrame, 'mainVerticalLayout', MagicMock(spec=QVBoxLayout), create=True)
    mocker.patch.object(PrimitiveCompoundFrame, 'load_ui')
    mock_logger.reset_mock()

    # Act
    frame = PrimitiveCompoundFrame(meta_field)

    # Assert
    mock_setup_ui.assert_called_once_with(mock_qframe.return_value)
    mock_metadata_frame_init.assert_called_once_with(mock_qframe.return_value)
    mock_data_type_class_context.assert_called_once_with(frame.mainVerticalLayout, frame.addPushButton, frame.instance,
                                                         meta_field)
    mock_data_type_class_factory.assert_called_once_with(mock_data_type_class_context.return_value)
    mock_logger.assert_called_once_with('pasta_eln.GUI.dataverse.primitive_compound_frame.PrimitiveCompoundFrame')
    mock_qframe.assert_called_once()
    assert frame.meta_field == meta_field
    frame.data_type_class_factory.make_data_type_class.assert_called_once_with(
      DataTypeClassName(meta_field['typeClass'])
    )
    frame.addPushButton.clicked.connect.assert_called_once_with(frame.add_button_click_handler)
    frame.load_ui.assert_called_once()

  @pytest.mark.parametrize("meta_field, expected_error", [
    ({}, KeyError),
    ({"typeClass": ""}, ValueError),
    ({"typeClass": None}, ValueError),
  ], ids=["empty_meta_field", "empty_type_class", "none_type_class"])
  def test_primitive_compound_frame_initialization_edge_cases(self, mocker, mock_logger, mock_data_type_class_factory,
                                                              mock_data_type_class, mock_qframe, meta_field,
                                                              expected_error):
    # Arrange
    mocker.patch(
      "pasta_eln.GUI.dataverse.primitive_compound_controlled_frame_base.Ui_PrimitiveCompoundControlledFrameBase.setupUi")
    mocker.patch(
      "pasta_eln.GUI.dataverse.metadata_frame_base.MetadataFrame.__init__")
    mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.DataTypeClassContext',
                 MagicMock(spec=DataTypeClassContext))
    mocker.patch.object(PrimitiveCompoundFrame, 'addPushButton', MagicMock(spec=QPushButton), create=True)
    mocker.patch.object(PrimitiveCompoundFrame, 'mainVerticalLayout', MagicMock(spec=QVBoxLayout), create=True)
    mocker.patch.object(PrimitiveCompoundFrame, 'load_ui')

    # Act
    with pytest.raises(expected_error):
      PrimitiveCompoundFrame(meta_field)

  @pytest.mark.parametrize("meta_field", [
    ({"typeClass": "InvalidTypeClass"}),
  ], ids=["invalid_type_class"])
  def test_primitive_compound_frame_initialization_error_cases(self, mocker, mock_logger, mock_data_type_class_factory,
                                                               mock_data_type_class, mock_qframe, meta_field):
    # Arrange
    mocker.patch(
      "pasta_eln.GUI.dataverse.primitive_compound_controlled_frame_base.Ui_PrimitiveCompoundControlledFrameBase.setupUi")
    mocker.patch(
      "pasta_eln.GUI.dataverse.metadata_frame_base.MetadataFrame.__init__")
    mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.DataTypeClassContext',
                 MagicMock(spec=DataTypeClassContext))
    mocker.patch.object(PrimitiveCompoundFrame, 'addPushButton', MagicMock(spec=QPushButton), create=True)
    mocker.patch.object(PrimitiveCompoundFrame, 'mainVerticalLayout', MagicMock(spec=QVBoxLayout), create=True)
    mocker.patch.object(PrimitiveCompoundFrame, 'load_ui')
    # Act
    with pytest.raises(ValueError):
      PrimitiveCompoundFrame(meta_field)

  @pytest.mark.parametrize(
    "meta_field, expected_log_message",
    [
      ({"typeClass": "primitive", "multiple": False, "value": "test_value"},
       "Loading UI for {'typeClass': 'primitive', 'multiple': False, 'value': 'test_value'}"),
      ({"typeClass": "compound", "multiple": True, "value": []},
       "Loading UI for {'typeClass': 'compound', 'multiple': True, 'value': []}"),
      ({"typeClass": "unknown", "multiple": False, "value": None},
       "Loading UI for {'typeClass': 'unknown', 'multiple': False, 'value': None}")
    ],
    ids=["primitive_single", "compound_multiple_empty", "unknown_type"]
  )
  def test_load_ui(self, mock_primitive_compound_frame, meta_field, expected_log_message):
    # Arrange
    mock_primitive_compound_frame.logger.reset_mock()
    mock_primitive_compound_frame.data_type.reset_mock()
    mock_primitive_compound_frame.meta_field = meta_field

    # Act
    mock_primitive_compound_frame.load_ui()

    # Assert
    mock_primitive_compound_frame.logger.info.assert_called_once_with("Loading UI for %s", meta_field)
    mock_primitive_compound_frame.data_type.populate_entry.assert_called_once()

  @pytest.mark.parametrize(
    "meta_field, expected_log_message",
    [
      ({"typeClass": "primitive", "multiple": True, "typeName": "test_name"},
       "Adding new entry of type primitive, name: test_name"),
      ({"typeClass": "compound", "multiple": False, "typeName": "test_name"},
       "Adding new entry of type compound, name: test_name"),
      ({"typeClass": "unknown", "multiple": True, "typeName": "test_name"},
       "Adding new entry of type unknown, name: test_name")
    ],
    ids=["primitive_multiple", "compound_single", "unknown_type"]
  )
  def test_add_button_click_handler(self, mock_primitive_compound_frame, meta_field, expected_log_message):
    # Arrange
    mock_primitive_compound_frame.meta_field = meta_field

    # Act
    mock_primitive_compound_frame.add_button_click_handler()

    # Assert
    mock_primitive_compound_frame.logger.info.assert_called_with("Adding new entry of type %s, name: %s",
                                                                 meta_field.get('typeClass', ''),
                                                                 meta_field.get('typeName', ''))
    if not meta_field.get('multiple'):
      mock_primitive_compound_frame.logger.error.assert_called_with(
        "Add operation not supported for non-multiple entries")
    else:
      mock_primitive_compound_frame.data_type.add_new_entry.assert_called_once()

  @pytest.mark.parametrize(
    "meta_field, expected_log_message",
    [
      ({"typeClass": "primitive", "typeName": "test_name"},
       "Saving changes to meta_field for type, name: test_name, class: primitive"),
      ({"typeClass": "compound", "typeName": "test_name"},
       "Saving changes to meta_field for type, name: test_name, class: compound"),
      ({"typeClass": "unknown", "typeName": "test_name"},
       "Saving changes to meta_field for type, name: test_name, class: unknown")
    ],
    ids=["primitive", "compound", "unknown_type"]
  )
  def test_save_modifications(self, mock_primitive_compound_frame, meta_field, expected_log_message):
    # Arrange
    mock_primitive_compound_frame.meta_field = meta_field

    # Act
    mock_primitive_compound_frame.save_modifications()

    # Assert
    mock_primitive_compound_frame.logger.info.assert_called_with(
      "Saving changes to meta_field for type, name: %s, class: %s", meta_field.get('typeName'),
      meta_field.get('typeClass'))
    mock_primitive_compound_frame.data_type.save_modifications.assert_called_once()
