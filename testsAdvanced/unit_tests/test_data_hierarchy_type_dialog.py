#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_type_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from unittest.mock import MagicMock, patch

import pytest
from PySide6 import QtWidgets
from PySide6.QtWidgets import QDialogButtonBox, QLineEdit, QMessageBox
from _pytest.mark import param

from pasta_eln.GUI.data_hierarchy.data_type_info_validator import DataTypeInfoValidator
from pasta_eln.GUI.data_hierarchy.lookup_iri_action import LookupIriAction
from pasta_eln.GUI.data_hierarchy.type_dialog import TypeDialog


@pytest.fixture
def type_dialog(mocker):
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.logging.getLogger')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.iconFontCollectionComboBox', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.iconComboBox', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.typeDisplayedTitleLineEdit', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.typeLineEdit', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.iriLineEdit', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.shortcutLineEdit', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.buttonBox', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QDialog')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.LookupIriAction')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.show_message')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QTAIconsFactory',
               MagicMock(font_collections=['Font1', 'Font2']))
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog_base.Ui_TypeDialogBase.setupUi')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.DataTypeInfo')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QRegularExpression')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QRegularExpressionValidator')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QTAIconsFactory',
               MagicMock(font_collections=['Font1', 'Font2']))
  return TypeDialog(MagicMock(), MagicMock())


class TestDataHierarchyTypeDialog:

  def test_init(self, mocker):
    # Arrange
    accepted_callback = MagicMock()
    rejected_callback = MagicMock()
    mock_get_logger = mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.logging.getLogger')
    mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.iconFontCollectionComboBox', create=True)
    mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.iconComboBox', create=True)
    mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.typeDisplayedTitleLineEdit', create=True)
    mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.typeLineEdit', create=True)
    mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.iriLineEdit', create=True)
    mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.shortcutLineEdit', create=True)
    mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.buttonBox', create=True)
    mock_setup_slots = mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.setup_slots')
    mock_q_dialog = mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QDialog')
    mock_data_type_info = mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.DataTypeInfo')
    mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.LookupIriAction')
    mock_regular_expression_validator = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.type_dialog.QRegularExpressionValidator')
    mock_regular_expression = mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QRegularExpression')
    mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.show_message')
    mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.populate_icons')
    mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.set_iri_lookup_action')
    mock_qta_icons_singleton = mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QTAIconsFactory',
                                            MagicMock(font_collections=['Font1', 'Font2']))
    mock_setup_ui = mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog_base.Ui_TypeDialogBase.setupUi')

    # Act
    type_dialog = TypeDialog(accepted_callback, rejected_callback)

    # Assert
    mock_get_logger.assert_called_with('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog')
    mock_data_type_info.assert_called_once()
    mock_q_dialog.assert_called_once()
    mock_setup_ui.assert_called_once_with(mock_q_dialog.return_value)
    mock_qta_icons_singleton.get_instance.assert_called_once()
    mock_setup_slots.assert_called_once()
    assert type_dialog.accepted_callback_parent == accepted_callback
    assert type_dialog.rejected_callback_parent == rejected_callback

    type_dialog.iconFontCollectionComboBox.addItems.assert_called_once_with(type_dialog.qta_icons.font_collections)
    type_dialog.populate_icons.assert_called_once_with(type_dialog.qta_icons.font_collections[0])
    mock_regular_expression.assert_called_once_with('(?=^[^Ax])(?=[^ ]*)')
    mock_regular_expression_validator.assert_called_once_with(mock_regular_expression.return_value)
    type_dialog.typeLineEdit.setValidator.assert_called_once_with(mock_regular_expression_validator.return_value)
    type_dialog.iconComboBox.completer().setCompletionMode.assert_called_once_with(
      QtWidgets.QCompleter.CompletionMode.PopupCompletion)
    type_dialog.set_iri_lookup_action.assert_called_once_with('')

  @pytest.mark.parametrize(
    'type_info, validator_side_effect, expected_valid, log_error_called',
    [
      # Success path tests
      param({'key': 'value'}, None, True, False, id='valid_type_info'),
      param({'another_key': 'another_value'}, None, True, False, id='another_valid_type_info'),

      # Edge cases
      param({}, None, True, False, id='empty_type_info'),
      param({'key': None}, None, True, False, id='none_value_in_type_info'),

      # Error cases
      param({'key': 'value'}, TypeError('Invalid type'), False, True, id='type_error'),
      param({'key': 'value'}, ValueError('Invalid value'), False, True, id='value_error'),
    ],
    ids=lambda x: x[-1]
  )
  def test_validate_type_info(self, type_info, type_dialog, validator_side_effect, expected_valid, log_error_called):
    # Arrange
    type_dialog.type_info = type_info

    with patch.object(DataTypeInfoValidator, 'validate', side_effect=validator_side_effect):
      with patch('pasta_eln.GUI.data_hierarchy.type_dialog.show_message') as mock_show_message:

        # Act
        result = type_dialog.validate_type_info()

        # Assert
        assert result == expected_valid
        if validator_side_effect:
          mock_show_message.assert_called_once_with(str(validator_side_effect), QMessageBox.Icon.Warning)
          type_dialog.logger.error.assert_called_once_with(str(validator_side_effect))
        else:
          mock_show_message.assert_not_called()
          type_dialog.logger.error.assert_not_called()

  def test_setup_slots(self, type_dialog):
    # Act
    type_dialog.setup_slots()

    # Assert
    assert type_dialog.iconFontCollectionComboBox.currentTextChanged[str].isConnected()
    assert type_dialog.typeDisplayedTitleLineEdit.textChanged[str].isConnected()
    assert type_dialog.typeLineEdit.textChanged[str].isConnected()
    assert type_dialog.iriLineEdit.textChanged[str].isConnected()
    assert type_dialog.shortcutLineEdit.textChanged[str].isConnected()
    assert type_dialog.iconComboBox.currentTextChanged[str].isConnected()
    assert type_dialog.buttonBox.rejected.isConnected()
    assert type_dialog.buttonBox.button(QDialogButtonBox.StandardButton.Ok).clicked.isConnected()

  @pytest.mark.parametrize(
    'lookup_term, existing_actions, expected_action_count',
    [
      ('http://example.com/iri1', [], 1),  # success path with no existing actions
      ('http://example.com/iri2',
       [MagicMock(spec=LookupIriAction, lookup_term=None, parent_line_edit='http://example.com/iri1')], 1),
      # success path with one existing action
      ('', [], 1),  # edge case with empty lookup term
      ('http://example.com/iri3', [MagicMock()], 2),  # edge case with non-LookupIriAction existing action
    ],
    ids=[
      'success_path_no_existing_actions',
      'success_path_with_existing_action',
      'edge_case_empty_lookup_term',
      'edge_case_non_lookupiri_action_existing'
    ]
  )
  def test_set_iri_lookup_action(self, mocker, type_dialog, lookup_term, existing_actions, expected_action_count):
    # Arrange
    mocker.resetall()
    mock_lookup_action = mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.LookupIriAction')
    mock_isinstance = mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.isinstance', return_value=True)

    type_dialog.iriLineEdit.actions.return_value = existing_actions

    # Act
    type_dialog.set_iri_lookup_action(lookup_term)

    # Assert
    type_dialog.iriLineEdit.actions.assert_called_once()
    if expected_action_count == 1:
      mock_lookup_action.assert_called_once_with(
        parent_line_edit=type_dialog.iriLineEdit,
        lookup_term=lookup_term
      )
      (type_dialog.iriLineEdit.addAction
       .assert_called_once_with(mock_lookup_action.return_value,
                                QLineEdit.ActionPosition.TrailingPosition))
      for act in existing_actions:
        mock_isinstance.assert_called_with(act, mock_lookup_action)
        act.deleteLater.assert_called_once()

  @pytest.mark.parametrize(
    'lookup_term, existing_actions',
    [
      ('http://example.com/iri4', None),  # error case with None as existing actions
    ],
    ids=[
      'error_case_none_existing_actions'
    ]
  )
  def test_set_iri_lookup_action_errors(self, type_dialog, lookup_term, existing_actions):
    # Arrange
    type_dialog.iriLineEdit.actions.return_value = existing_actions

    # Act and Assert
    with pytest.raises(TypeError):
      type_dialog.set_iri_lookup_action(lookup_term)

  def test_clear_ui(self, type_dialog):

    # Act
    type_dialog.clear_ui()

    # Assert
    type_dialog.typeLineEdit.clear.assert_called_once()
    type_dialog.typeDisplayedTitleLineEdit.clear.assert_called_once()
    type_dialog.iriLineEdit.clear.assert_called_once()
    type_dialog.shortcutLineEdit.clear.assert_called_once()
    type_dialog.iconFontCollectionComboBox.setCurrentIndex.assert_called_once_with(0)
    type_dialog.iconComboBox.setCurrentIndex.assert_called_once_with(0)

  def test_show(self, type_dialog):
    # Act
    with patch.object(type_dialog.instance, 'show') as mock_show:
      type_dialog.show()

    # Assert
    mock_show.assert_called_once()

  def test_title_modified(self, type_dialog):
    # Arrange
    new_title = 'New Title'

    # Act
    with patch.object(type_dialog, 'set_iri_lookup_action') as mock_set_iri_lookup_action:
      type_dialog.title_modified(new_title)

    # Assert
    mock_set_iri_lookup_action.assert_called_once_with(new_title)

  @pytest.mark.parametrize('test_id, font_collection', [
    ('success_path_1', 'font_collection_1'),
    ('success_path_2', 'font_collection_2'),
    ('empty_font_collection', ''),
    ('special_characters', '!@#$%^&*()'),
    ('long_string', 'a' * 1000),
    ('none_font_collection', None),
  ], ids=['success_path_1', 'success_path_2', 'empty_font_collection', 'special_characters', 'long_string',
          'none_font_collection'])
  def test_icon_font_collection_changed(self, type_dialog, test_id, font_collection):
    # Arrange
    type_dialog.populate_icons = MagicMock()
    # Act
    type_dialog.icon_font_collection_changed(font_collection)

    # Assert
    type_dialog.iconComboBox.clear.assert_called_once()
    type_dialog.populate_icons.assert_called_once_with(font_collection)

  @pytest.mark.parametrize(
    'font_collection, expected_calls, log_warning',
    [
      ('font1', [('icon1',), ('icon2', 'icon2'), ('icon3', 'icon3')], False),
      ('font2', [('iconA',), ('iconB', 'iconB')], False),
      ('', [], True),
      (None, [], True),
      ('nonexistent_font', [], True),
    ],
    ids=[
      'valid_font1',
      'valid_font2',
      'empty_string',
      'none_value',
      'nonexistent_font'
    ]
  )
  def test_populate_icons(self, mocker, type_dialog, font_collection, expected_calls, log_warning):
    # Arrange
    mocker.resetall()
    mock_qta = mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.qta')
    type_dialog.qta_icons.icon_names = {'font1': ['icon1', 'icon2', 'icon3'], 'font2': ['iconA', 'iconB']}
    expected_calls_modified = []
    for item in expected_calls:
      if len(item) == 2:
        expected_calls_modified.append(mocker.call(mock_qta.icon(item[0]), item[1]))
      else:
        expected_calls_modified.append(mocker.call(item[0]))

    # Act
    type_dialog.populate_icons(font_collection)

    # Assert
    if log_warning:
      type_dialog.logger.warning.assert_called_once_with('Invalid font collection!')
    else:
      type_dialog.logger.warning.assert_not_called()

    assert type_dialog.iconComboBox.addItem.call_count == len(expected_calls)
    for call, expected_call in zip(type_dialog.iconComboBox.addItem.call_args_list, expected_calls_modified):
      assert call == expected_call

  @pytest.mark.parametrize(
    'datatype, expected',
    [
      ('text', 'text'),  # happy path with a common string
      ('123', '123'),  # happy path with numeric string
      ('', ''),  # edge case with empty string
      ('a' * 1000, 'a' * 1000),  # edge case with very long string
    ],
    ids=[
      'common_string',
      'numeric_string',
      'empty_string',
      'very_long_string'
    ]
  )
  def test_set_data_type(self, type_dialog, datatype, expected):
    # Act
    if datatype is None:
      with pytest.raises(TypeError):
        type_dialog.set_data_type(datatype)
    else:
      type_dialog.set_data_type(datatype)

    # Assert
    if datatype is not None:
      assert type_dialog.type_info.datatype == expected

  @pytest.mark.parametrize(
    'title, expected_title',
    [
      ('Sample Title', 'Sample Title'),  # happy path
      ('', ''),  # edge case: empty string
      ('A' * 1000, 'A' * 1000),  # edge case: very long string
      ('1234567890', '1234567890'),  # edge case: numeric string
      ('!@#$%^&*()', '!@#$%^&*()'),  # edge case: special characters
    ],
    ids=[
      'happy_path_sample_title',
      'edge_case_empty_string',
      'edge_case_very_long_string',
      'edge_case_numeric_string',
      'edge_case_special_characters',
    ]
  )
  def test_set_type_title(self, type_dialog, title, expected_title):
    # Arrange

    # Act
    type_dialog.set_type_title(title)

    # Assert
    assert type_dialog.type_info.title == expected_title

  @pytest.mark.parametrize(
    'iri, expected_iri',
    [
      param('http://example.com/type1', 'http://example.com/type1', id='success_path_1'),
      param('http://example.com/type2', 'http://example.com/type2', id='success_path_2'),
      param('', '', id='edge_case_empty_string'),
      param('http://example.com/very/long/iri/with/many/segments',
            'http://example.com/very/long/iri/with/many/segments', id='edge_case_long_iri'),
      param(None, None, id='error_case_none'),
    ],
    ids=lambda x: x[-1]
  )
  def test_set_type_iri(self, type_dialog, iri, expected_iri):
    # Arrange

    # Act
    type_dialog.set_type_iri(iri)

    # Assert
    if iri is not None:
      assert type_dialog.type_info.iri == expected_iri

  @pytest.mark.parametrize(
    'shortcut, expected',
    [
      ('ctrl+c', 'ctrl+c'),  # happy path with common shortcut
      ('ctrl+v', 'ctrl+v'),  # happy path with another common shortcut
      ('', ''),  # edge case with empty string
      ('a' * 1000, 'a' * 1000),  # edge case with very long string
      ('ctrl+shift+alt+del', 'ctrl+shift+alt+del'),  # edge case with complex shortcut
    ],
    ids=[
      'common-shortcut-copy',
      'common-shortcut-paste',
      'empty-string',
      'very-long-string',
      'complex-shortcut'
    ]
  )
  def test_set_type_shortcut(self, type_dialog, shortcut, expected):
    # Arrange

    # Act
    type_dialog.set_type_shortcut(shortcut)

    # Assert
    assert type_dialog.type_info.shortcut == expected

  @pytest.mark.parametrize(
    'icon, expected_icon',
    [
      ('icon1.png', 'icon1.png'),  # happy path with a typical icon name
      ('', ''),  # edge case with an empty string
      ('a' * 255, 'a' * 255),  # edge case with a very long string
      ('icon_with_special_chars_!@#.png', 'icon_with_special_chars_!@#.png'),  # edge case with special characters
    ],
    ids=[
      'typical_icon_name',
      'empty_string',
      'very_long_string',
      'special_characters'
    ]
  )
  def test_set_type_icon(self, type_dialog, icon, expected_icon):
    # Arrange

    # Act
    type_dialog.set_type_icon(icon)

    # Assert
    assert type_dialog.type_info.icon == expected_icon
