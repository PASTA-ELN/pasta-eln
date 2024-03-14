#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_controlled_vocab_frame.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest

from pasta_eln.GUI.dataverse.controlled_vocab_frame import ControlledVocabFrame


@pytest.fixture
def qtbot(mocker):
  mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.QFrame')
  mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.QPushButton')
  mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.QHBoxLayout')
  mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.QSizePolicy')
  mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.QSize')
  mocker.patch(
    'pasta_eln.GUI.dataverse.primitive_compound_controlled_frame_base.Ui_PrimitiveCompoundControlledFrameBase.setupUi')
  mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.logging.getLogger')
  mocker.patch.object(ControlledVocabFrame, 'addPushButton', create=True)
  mocker.patch.object(ControlledVocabFrame, 'mainVerticalLayout', create=True)
  mocker.patch.object(ControlledVocabFrame, 'meta_field', create=True)


# Fixture to create a ControlledVocabFrame instance with a mocked parent
@pytest.fixture
def controlled_vocab_frame(qtbot, mocker):
  actual_load_ui = ControlledVocabFrame.load_ui
  mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.ControlledVocabFrame.load_ui')
  type_field = {
    'typeClass': 'primitive',
    'multiple': False,
    'typeName': 'testType',
    'value': 'testValue',
    'valueTemplate': 'testTemplate'
  }
  frame = ControlledVocabFrame(type_field)
  ControlledVocabFrame.load_ui = actual_load_ui
  return frame


class TestControlledVocabFrame:
  @pytest.mark.parametrize("test_id, meta_field", [
    (
        "success_multiple_values_init",
        {"multiple": True, "value": ["entry1", "entry2"], "valueTemplate": ["entry1", "entry2", "entry3"]})
  ])
  def test_ControlledVocabFrame_init(self, mocker, qtbot, test_id, meta_field):
    # Arrange
    mock_load_ui = mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.ControlledVocabFrame.load_ui')
    mock_super_setup_ui = mocker.patch(
      'pasta_eln.GUI.dataverse.primitive_compound_controlled_frame_base.Ui_PrimitiveCompoundControlledFrameBase.setupUi')
    mock_get_logger = mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.logging.getLogger')
    mock_frame_constructor = mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.QFrame')

    # Act
    frame = ControlledVocabFrame(meta_field)

    # Assert
    assert frame is not None
    mock_get_logger.assert_called_once_with("pasta_eln.GUI.dataverse.controlled_vocab_frame.ControlledVocabFrame")
    mock_frame_constructor.assert_called_once_with()
    mock_super_setup_ui.assert_called_once_with(frame.instance)
    assert frame.meta_field == meta_field
    mock_load_ui.assert_called_once()

  @pytest.mark.parametrize("meta_field, expected_calls, test_id", [
    # Happy path tests with various realistic test values
    ({"multiple": True, "value": ["entry1", "entry2"], "valueTemplate": "template"},
     [("template", "entry1"), ("template", "entry2")], "success_multiple_values"),
    ({"multiple": False, "value": "single_entry", "valueTemplate": "template"}, [(["template"], "single_entry")],
     "success_single_value"),

    # Edge cases
    ({"multiple": True, "value": [], "valueTemplate": "template"}, [("template", None)], "edge_no_values"),
    ({"multiple": True, "value": None, "valueTemplate": "template"}, [("template", None)], "edge_none_value"),
    ({"multiple": False, "value": None, "valueTemplate": "template"}, [(["template"], None)], "edge_single_none_value"),

    # Error cases are not defined as the function does not handle any exceptions or error conditions.
    # If there are specific error conditions that should be tested, they need to be defined.
  ])
  def test_load_ui(self, mocker, controlled_vocab_frame, meta_field, expected_calls, test_id):
    # Arrange
    controlled_vocab_frame.meta_field = meta_field
    controlled_vocab_frame.add_new_vocab_entry = mocker.MagicMock()

    # Act
    controlled_vocab_frame.load_ui()

    # Assert
    assert controlled_vocab_frame.add_new_vocab_entry.call_count == len(
      expected_calls), f"Test ID: {test_id} - Incorrect number of calls to add_new_vocab_entry"
    controlled_vocab_frame.add_new_vocab_entry.assert_has_calls([mocker.call(*call) for call in expected_calls],
                                                                any_order=True)
    controlled_vocab_frame.logger.info.assert_called_once_with("Loading controlled vocabulary frame ui..")

  @pytest.mark.parametrize("meta_field, expected_entry, expected_value, test_id", [
    # Happy path tests
    ({"multiple": True, "valueTemplate": ["term1", "term2"]}, ["term1", "term2"], "term1", "happy_multiple_true"),
    ({"multiple": False, "valueTemplate": "term"}, ["term"], "term", "happy_multiple_false"),

    # Edge cases
    ({"multiple": True, "valueTemplate": []}, [], None, "edge_empty_list"),
    ({"multiple": False, "valueTemplate": ""}, [], '', "edge_empty_string"),

    # Error cases
    ({"multiple": True}, None, None, "error_no_valueTemplate_multiple"),
    ({"multiple": False}, [], None, "error_no_valueTemplate_single"),
  ])
  def test_add_button_callback(self, mocker, controlled_vocab_frame, meta_field, expected_entry, expected_value,
                               test_id):
    # Arrange
    controlled_vocab_frame.meta_field = meta_field
    controlled_vocab_frame.add_new_vocab_entry = mocker.MagicMock()

    # Act
    controlled_vocab_frame.add_button_callback()

    # Assert
    controlled_vocab_frame.logger.info.assert_called_once_with("Adding new vocabulary entry, value: %s",
                                                               controlled_vocab_frame.meta_field)
    controlled_vocab_frame.add_new_vocab_entry.assert_called_with(expected_entry, expected_value)

  @pytest.mark.parametrize("controlled_vocabulary, value, test_id", [
    (['term1', 'term2', 'term3'], 'term2', 'happy_path'),
    ([], None, 'empty_list'),
    (None, None, 'none_vocabulary'),
    (['single_term'], 'single_term', 'single_item'),
    (['term1', 'term2'], None, 'no_value_provided'),
    (['term1', 'term2'], 'non_existent_term', 'value_not_in_list'),
  ], ids=lambda test_id: test_id)
  def test_add_new_vocab_entry(self, mocker, controlled_vocab_frame, controlled_vocabulary, value, test_id):
    # Arrange
    mock_button = mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.QPushButton')
    mock_h_layout = mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.QHBoxLayout')
    mock_combobox = mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.QComboBox')
    mock_size_policy = mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.QSizePolicy')
    mock_size = mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.QSize')

    # Act
    controlled_vocab_frame.add_new_vocab_entry(controlled_vocabulary, value)

    # Assert
    mock_h_layout.assert_called_once()
    mock_h_layout.return_value.setObjectName.assert_called_once_with("vocabHorizontalLayout")
    mock_combobox.assert_called_once_with(parent=controlled_vocab_frame.instance)
    mock_combobox.return_value.setObjectName.assert_called_once_with("vocabComboBox")
    mock_combobox.return_value.setToolTip.assert_called_once_with("Select the controlled vocabulary.")
    mock_combobox.return_value.addItems.assert_called_once_with(controlled_vocabulary)
    mock_combobox.return_value.setCurrentText.assert_called_once_with(value)
    mock_h_layout.return_value.addWidget.assert_any_call(mock_combobox.return_value)
    mock_button.assert_called_once_with(parent=controlled_vocab_frame.instance)
    delete_push_button = mock_button.return_value
    delete_push_button.setText.assert_called_once_with("Delete")
    delete_push_button.setToolTip.assert_called_once_with("Delete this particular vocabulary entry.")
    mock_size_policy.assert_called_once_with(mock_size_policy.Policy.Fixed, mock_size_policy.Policy.Fixed)
    size_policy = mock_size_policy.return_value
    size_policy.setHorizontalStretch.assert_called_once_with(0)
    size_policy.setVerticalStretch.assert_called_once_with(0)
    size_policy.setHeightForWidth.assert_called_once_with(delete_push_button.sizePolicy().hasHeightForWidth())
    delete_push_button.setSizePolicy.assert_called_once_with(size_policy)
    mock_size.assert_called_once_with(100, 0)
    delete_push_button.setMinimumSize.assert_called_once_with(mock_size.return_value)
    delete_push_button.setObjectName.assert_called_once_with("deletePushButton")
    mock_h_layout.return_value.addWidget.assert_any_call(delete_push_button)
    delete_push_button.clicked.connect.assert_called_once()
    controlled_vocab_frame.mainVerticalLayout.addLayout.assert_called_once_with(mock_h_layout.return_value)

  @pytest.mark.parametrize("test_id, multiple, layout_count, combo_texts, expected", [
    # ID: SuccessPath-SingleValue
    ("SuccessPath-SingleValue", False, 1, ["Value1"], "Value1"),
    # ID: SuccessPath-MultipleValues
    ("SuccessPath-MultipleValues", True, 2, ["Value1", "Value2"], ["Value1", "Value2"]),
    # ID: EdgeCase-EmptyValues
    ("EdgeCase-EmptyValues", True, 3, ["", "", ""], []),
    # ID: EdgeCase-DuplicateValues
    ("EdgeCase-DuplicateValues", True, 3, ["Value1", "Value1", "Value1"], ["Value1"]),
    # ID: ErrorCase-NoLayout
    ("ErrorCase-NoLayout", False, 0, [], []),
    # ID: ErrorCase-NoComboBox
    ("ErrorCase-NoComboBox", False, 1, None, []),
  ])
  def test_save_modifications(self, mocker, controlled_vocab_frame, test_id, multiple, layout_count, combo_texts,
                              expected):
    # Arrange
    controlled_vocab_frame.meta_field = {'multiple': multiple, 'value': []}
    controlled_vocab_frame.mainVerticalLayout.count.return_value = layout_count
    combo_boxes = [mocker.MagicMock() for _ in range(layout_count)]
    layouts = [mocker.MagicMock() for _ in range(layout_count)]
    for i, combo_box in enumerate(combo_boxes):
      if combo_texts is not None:
        combo_box.currentText.return_value = combo_texts[i]
        layouts[i].itemAt(0).widget.return_value = combo_box
        layouts[i].layout.return_value = layouts[i]
    if controlled_vocab_frame.meta_field['multiple']:
      controlled_vocab_frame.mainVerticalLayout.itemAt = lambda pos: layouts[pos]
    elif test_id == "ErrorCase-NoLayout":
      controlled_vocab_frame.mainVerticalLayout.findChild.return_value = None
    elif test_id == "ErrorCase-NoComboBox":
      controlled_vocab_frame.mainVerticalLayout.findChild.return_value.itemAt(
        0).widget.return_value = None
    else:
      controlled_vocab_frame.mainVerticalLayout.findChild.return_value.itemAt(
        0).widget.return_value = combo_boxes[0] if layout_count else None

    # Act
    controlled_vocab_frame.save_modifications()

    # Assert
    if isinstance(expected, list):
      controlled_vocab_frame.meta_field['value'].sort()
      expected.sort()
    assert controlled_vocab_frame.meta_field['value'] == expected
    controlled_vocab_frame.logger.info.assert_called_once_with("Saved modifications successfully, value: %s",
                                                               controlled_vocab_frame.meta_field)
    if test_id == "ErrorCase-NoLayout":
      controlled_vocab_frame.mainVerticalLayout.addLayout.assert_not_called()
      controlled_vocab_frame.logger.warning.assert_called_once_with("Failed to save modifications, no layout found.")
