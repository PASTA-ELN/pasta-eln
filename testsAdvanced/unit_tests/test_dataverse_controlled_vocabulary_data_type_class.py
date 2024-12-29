#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_controlled_vocabulary_data_type_class.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QPushButton, QVBoxLayout
from _pytest.mark import param

from pasta_eln.GUI.dataverse.controlled_vocabulary_data_type_class import ControlledVocabularyDataTypeClass
from pasta_eln.GUI.dataverse.data_type_class_context import DataTypeClassContext


@pytest.fixture
def mock_controlled_vocabulary_data_type_class(mocker):
  context = mocker.MagicMock(spec=DataTypeClassContext)
  context.main_vertical_layout = mocker.MagicMock(spec=QVBoxLayout)
  context.add_push_button = mocker.MagicMock(spec=QPushButton)
  context.parent_frame = mocker.MagicMock(spec=QFrame)
  context.meta_field = {}
  mocker.patch('pasta_eln.GUI.dataverse.controlled_vocabulary_data_type_class.logging.getLogger')
  return ControlledVocabularyDataTypeClass(context)


class TestControlledVocabularyDataTypeClass:

  @pytest.mark.parametrize(
    'context, expected_logger_name',
    [
      (DataTypeClassContext(MagicMock(spec=QVBoxLayout), MagicMock(spec=QPushButton), MagicMock(spec=QFrame), {}),
       'pasta_eln.GUI.dataverse.controlled_vocabulary_data_type_class.ControlledVocabularyDataTypeClass'),
      (DataTypeClassContext(MagicMock(spec=QVBoxLayout), MagicMock(spec=QPushButton), MagicMock(spec=QFrame), {}),
       'pasta_eln.GUI.dataverse.controlled_vocabulary_data_type_class.ControlledVocabularyDataTypeClass'),
    ],
    ids=['default_context', 'another_default_context']
  )
  def test_init_success_path(self, context, expected_logger_name):
    # Act
    instance = ControlledVocabularyDataTypeClass(context)

    # Assert
    assert instance.logger.name == expected_logger_name

  @pytest.mark.parametrize(
    'context, expected_exception',
    [
      (None, TypeError),
    ],
    ids=['context_is_none']
  )
  def test_init_edge_cases(self, context, expected_exception):
    # Act and Assert
    with pytest.raises(expected_exception):
      ControlledVocabularyDataTypeClass(context)

  @pytest.mark.parametrize(
    'context, expected_exception',
    [
      ('invalid_context', TypeError),
    ],
    ids=['context_is_invalid_type']
  )
  def test_init_error_cases(self, context, expected_exception):
    # Act and Assert
    with pytest.raises(expected_exception):
      ControlledVocabularyDataTypeClass(context)

  @pytest.mark.parametrize(
    'meta_field, expected_entry, expected_value',
    [
      pytest.param(
        {'valueTemplate': ['template1'], 'multiple': True},
        ['template1'], 'template1',
        id='multiple_true_with_valueTemplate'
      ),
      pytest.param(
        {'valueTemplate': [], 'multiple': True},
        [], None,
        id='multiple_true_empty_valueTemplate'
      ),
      pytest.param(
        {'valueTemplate': 'template1', 'multiple': False},
        ['No Value', 'template1'], 'template1',
        id='multiple_false_with_valueTemplate'
      ),
      pytest.param(
        {'valueTemplate': [], 'multiple': False},
        ['No Value'], 'No Value',
        id='multiple_false_empty_valueTemplate'
      ),
      pytest.param(
        {'valueTemplate': None, 'multiple': False},
        ['No Value'], 'No Value',
        id='multiple_false_none_valueTemplate'
      ),
    ]
  )
  def test_add_new_entry(self, mock_controlled_vocabulary_data_type_class, meta_field, expected_entry, expected_value):
    # Arrange
    mock_controlled_vocabulary_data_type_class.context.meta_field = meta_field
    mock_controlled_vocabulary_data_type_class.add_new_vocab_entry = MagicMock()
    # Act
    mock_controlled_vocabulary_data_type_class.add_new_entry()

    # Assert
    mock_controlled_vocabulary_data_type_class.add_new_vocab_entry.assert_called_once_with(expected_entry,
                                                                                           expected_value)

  @pytest.mark.parametrize(
    'meta_field, expected_entries',
    [
      # Success path tests
      ({'value': ['val1', 'val2'], 'valueTemplate': 'template', 'multiple': True},
       [('template', 'val1'), ('template', 'val2')]),
      ({'value': None, 'valueTemplate': 'template', 'multiple': True}, [('template', None)]),
      ({'value': 'single_value', 'valueTemplate': 'template', 'multiple': False},
       [(['No Value', 'template'], 'single_value')]),
      ({'value': None, 'valueTemplate': 'template', 'multiple': False}, [(['No Value', 'template'], 'No Value')]),
      ({'value': None, 'valueTemplate': None, 'multiple': False}, [(['No Value'], 'No Value')]),

      # Edge cases
      ({'value': [], 'valueTemplate': 'template', 'multiple': True}, [('template', None)]),
      ({'value': [], 'valueTemplate': '', 'multiple': False}, [(['No Value'], 'No Value')]),
      ({'value': ['val1'], 'valueTemplate': '', 'multiple': True}, [('', 'val1')]),
      ({'value': ['val1'], 'valueTemplate': None, 'multiple': True}, [(None, 'val1')])
    ],
    ids=[
      'multiple_values_with_template',
      'no_value_with_template_multiple',
      'single_value_with_template',
      'no_value_with_template_single',
      'no_value_no_template_single',
      'empty_value_list_with_template_multiple',
      'empty_value_list_with_empty_template_single',
      'single_value_with_empty_template_multiple',
      'single_value_with_none_template_multiple'
    ]
  )
  def test_populate_entry(self, mocker, mock_controlled_vocabulary_data_type_class, meta_field, expected_entries):
    # Arrange
    mock_controlled_vocabulary_data_type_class.context.meta_field = meta_field
    mock_controlled_vocabulary_data_type_class.add_new_vocab_entry = MagicMock()
    # Act
    mock_controlled_vocabulary_data_type_class.populate_entry()

    # Assert
    mock_controlled_vocabulary_data_type_class.add_new_vocab_entry.assert_has_calls(
      [mocker.call(e[0], e[1]) for e in expected_entries], any_order=True)

  @pytest.mark.parametrize(
    'meta_field, layout_exists, layout, expected_log, expected_warning, expected_error',
    [
      # Happy path: multiple entries
      ({'multiple': True}, False, None,
       ('Saved multiple entry modifications successfully, value: %s', {'multiple': True}), False, False),

      # Happy path: single entry with correct layout
      ({'multiple': False}, True, MagicMock(spec=QHBoxLayout),
       ('Saved single entry modification successfully, value: %s', {'multiple': False}), False,
       False),

      # Edge case: single entry with incorrect layout type
      ({'multiple': False}, True, MagicMock(spec=QVBoxLayout), None, False, True),

      # Error case: no layout found
      ({'multiple': False}, False, None, None, 'Failed to save modifications, no layout found.', False),
    ],
    ids=[
      'multiple_entries',
      'single_entry_correct_layout',
      'single_entry_incorrect_layout',
      'no_layout_found',
    ]
  )
  def test_save_modifications(self, mocker, mock_controlled_vocabulary_data_type_class, meta_field, layout_exists,
                              layout, expected_log, expected_warning, expected_error):

    # Arrange
    mock_controlled_vocabulary_data_type_class.save_multiple_entries = mocker.MagicMock()
    mock_controlled_vocabulary_data_type_class.save_single_entry = mocker.MagicMock()
    mock_controlled_vocabulary_data_type_class.context.meta_field = meta_field
    mock_controlled_vocabulary_data_type_class.context.main_vertical_layout.findChild.return_value = layout if layout_exists else None

    # Act
    mock_controlled_vocabulary_data_type_class.save_modifications()

    # Assert
    if expected_log:
      mock_controlled_vocabulary_data_type_class.logger.info.assert_called_once_with(*expected_log)
      if meta_field.get('multiple'):
        mock_controlled_vocabulary_data_type_class.save_multiple_entries.assert_called_once_with()
      else:
        mock_controlled_vocabulary_data_type_class.save_single_entry.assert_called_once_with(layout)
    else:
      mock_controlled_vocabulary_data_type_class.logger.info.assert_not_called()

    if expected_warning:
      mock_controlled_vocabulary_data_type_class.logger.warning.assert_called_once_with(expected_warning)
    else:
      mock_controlled_vocabulary_data_type_class.logger.warning.assert_not_called()

    if expected_error:
      mock_controlled_vocabulary_data_type_class.logger.error.assert_called_once_with(
        'vocabHorizontalLayout not found!')
    else:
      mock_controlled_vocabulary_data_type_class.logger.error.assert_not_called()

  @pytest.mark.parametrize(
    'combo_text, expected_value, log_error_called',
    [
      ('Valid Value', 'Valid Value', False),  # success path
      ('No Value', None, False),  # edge case: 'No Value'
      ('', None, False),  # edge case: empty string
      (None, None, True),  # error case: combo box not found
      (None, None, True),  # error case: combo box not found
      ('Another Value', 'Another Value', False),  # success path with another value
    ],
    ids=[
      'valid_value',
      'no_value',
      'empty_string',
      'combo_box_not_found1',
      'combo_box_not_found2',
      'another_valid_value',
    ]
  )
  def test_save_single_entry(self, mocker, mock_controlled_vocabulary_data_type_class, combo_text, expected_value,
                             log_error_called, request):
    # Arrange
    layout = mocker.MagicMock(spec=QHBoxLayout)
    combo_box = mocker.MagicMock(spec=QComboBox)
    combo_box.currentText.return_value = combo_text
    layout.itemAt.return_value.widget.return_value = combo_box if combo_text is not None else (
      MagicMock() if request.node.callspec.id == 'combo_box_not_found2' else None)

    # Act
    mock_controlled_vocabulary_data_type_class.save_single_entry(layout)

    # Assert
    if expected_value:
      assert mock_controlled_vocabulary_data_type_class.context.meta_field['value'] == expected_value
    else:
      assert mock_controlled_vocabulary_data_type_class.logger.error.called == log_error_called

    if log_error_called:
      mock_controlled_vocabulary_data_type_class.logger.error.assert_called_once_with('Combo box not found!')
    else:
      mock_controlled_vocabulary_data_type_class.logger.error.assert_not_called()

    if combo_text is not None:
      combo_box.currentText.assert_called_once_with()
    else:
      combo_box.currentText.assert_not_called()

  @pytest.mark.parametrize(
    'initial_value, combo_texts, expected_value',
    [
      param([], ['Value1', 'Value2'], ['Value1', 'Value2'], id='success_path_with_two_values'),
      param([], ['No Value', 'No Value', 'Value1'], ['Value1'], id='success_path_with_no_value'),
      param([], ['Value1', 'Value1'], ['Value1'], id='success_path_with_duplicate_values'),
      param([], [], [], id='success_path_with_no_comboboxes'),
      param([], ['No Value', 'No Value'], [], id='success_path_with_only_no_value'),
      param([], ['Value1', 'Value2', 'Value3'], ['Value1', 'Value2', 'Value3'], id='success_path_with_three_values'),
      param([], ['Value1', 'Value2', 'Value1', None], ['Value1', 'Value2'],
            id='success_path_with_duplicate_and_unique_values'),
      param(None, ['Value1'], [], id='error_case_value_not_list'),
    ],
    ids=lambda val: val[-1]
  )
  def test_save_multiple_entries(self, mocker, mock_controlled_vocabulary_data_type_class, initial_value, combo_texts,
                                 expected_value):
    # Arrange
    mock_controlled_vocabulary_data_type_class.context.meta_field['value'] = initial_value
    mock_controlled_vocabulary_data_type_class.context.main_vertical_layout.count.return_value = len(combo_texts)

    layouts = []
    for text in combo_texts:
      vocab_horizontal_layout = mocker.MagicMock(spec=QHBoxLayout)
      combo_box = MagicMock(spec=QComboBox)
      combo_box.currentText.return_value = text
      vocab_horizontal_layout.addWidget(combo_box)
      vocab_horizontal_layout.itemAt.return_value.widget.return_value = combo_box
      vocab_horizontal_layout.layout.return_value = vocab_horizontal_layout
      layouts.append(vocab_horizontal_layout)
    mock_controlled_vocabulary_data_type_class.context.main_vertical_layout.itemAt.side_effect = layouts

    # Act
    mock_controlled_vocabulary_data_type_class.save_multiple_entries()

    # Assert
    if initial_value is None:
      mock_controlled_vocabulary_data_type_class.logger.error.assert_called_once_with('Value is not a list')
    else:
      assert set(mock_controlled_vocabulary_data_type_class.context.meta_field['value']) == set(expected_value)
      mock_controlled_vocabulary_data_type_class.logger.error.assert_not_called()

  @pytest.mark.parametrize(
    'controlled_vocabulary, value, expected_items, expected_text',
    [
      param(['option1', 'option2'], 'option1', ['option1', 'option2'], 'option1', id='success_path_with_value'),
      param(['option1', 'option2'], None, ['option1', 'option2'], '', id='success_path_without_value'),
      param([], 'option1', [], 'option1', id='empty_vocabulary_with_value'),
      param(None, None, [], '', id='empty_vocabulary_without_value'),
    ],
    ids=['success_path_with_value', 'success_path_without_value', 'empty_vocabulary_with_value',
         'empty_vocabulary_without_value']
  )
  def test_add_new_vocab_entry(self, mocker, mock_controlled_vocabulary_data_type_class, controlled_vocabulary, value,
                               expected_items, expected_text):
    # Arrange
    mock_qh_box_layout = mocker.patch('pasta_eln.GUI.dataverse.controlled_vocabulary_data_type_class.QHBoxLayout')
    mock_qc_box = mocker.patch('pasta_eln.GUI.dataverse.controlled_vocabulary_data_type_class.QComboBox')
    mock_add_clear_button = mocker.patch(
      'pasta_eln.GUI.dataverse.controlled_vocabulary_data_type_class.add_clear_button')
    mock_add_delete_button = mocker.patch(
      'pasta_eln.GUI.dataverse.controlled_vocabulary_data_type_class.add_delete_button')

    # Act
    mock_controlled_vocabulary_data_type_class.add_new_vocab_entry(controlled_vocabulary, value)

    # Assert
    mock_qh_box_layout.assert_called_once()
    mock_qh_box_layout.return_value.setObjectName.assert_called_once_with('vocabHorizontalLayout')
    mock_qc_box.assert_called_once_with(parent=mock_controlled_vocabulary_data_type_class.context.parent_frame)
    mock_qc_box.return_value.setObjectName.assert_called_once_with('vocabComboBox')
    mock_qc_box.return_value.setToolTip.assert_called_once_with('Select the controlled vocabulary.')
    mock_qc_box.return_value.addItems.assert_called_once_with(controlled_vocabulary or [])
    mock_qc_box.return_value.setCurrentText.assert_called_once_with(value or '')
    mock_qh_box_layout.return_value.addWidget.assert_called_once_with(mock_qc_box.return_value)
    mock_add_clear_button(mock_controlled_vocabulary_data_type_class.context.parent_frame,
                          mock_qh_box_layout.return_value)
    mock_add_delete_button(mock_controlled_vocabulary_data_type_class.context.parent_frame,
                           mock_qh_box_layout.return_value)
    mock_controlled_vocabulary_data_type_class.context.main_vertical_layout.addLayout.assert_called_once_with(
      mock_qh_box_layout.return_value)
