#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_utility_functions.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QLabel, QMessageBox

from pasta_eln.GUI.data_hierarchy.utility_functions import adjust_data_hierarchy_data_to_v4, can_delete_type, \
  check_data_hierarchy_types, get_missing_metadata_message, \
  is_click_within_bounds, set_types_missing_required_metadata, set_types_with_duplicate_metadata, \
  set_types_without_name_in_metadata, show_message
from testsAdvanced.common.test_utils import are_json_equal


class TestDataHierarchyUtilityFunctions:

  def test_is_click_within_bounds_when_null_arguments_returns_false(self, mocker):
    assert is_click_within_bounds(mocker.patch('PySide6.QtGui.QSinglePointEvent'),
                                  None) == False, 'is_click_within_bounds should return False for null argument'
    assert is_click_within_bounds(None, mocker.patch(
      'PySide6.QtWidgets.QStyleOptionViewItem')) == False, 'is_click_within_bounds should return False for null argument'
    assert is_click_within_bounds(None, None) == False, 'is_click_within_bounds should return False for null argument'

  def test_is_click_within_bounds_when_within_bounds_returns_true(self, mocker):
    mock_mouse_event = mocker.patch('PySide6.QtGui.QSinglePointEvent')
    mock_is_instance = mocker.patch('pasta_eln.GUI.data_hierarchy.utility_functions.isinstance', return_value=True)
    mock_mouse_event.type.side_effect = lambda: QEvent.MouseButtonRelease
    mock_mouse_event.x.side_effect = lambda: 10  # left is 5 and right is left + width 5+10=15
    mock_mouse_event.y.side_effect = lambda: 20  # top is 10 and bottom is top + height 10+20=30
    mock_q_style_option_view_item = mocker.patch('PySide6.QtWidgets.QStyleOptionViewItem')
    mock_q_style_option_view_item.rect.left.side_effect = lambda: 5
    mock_q_style_option_view_item.rect.width.side_effect = lambda: 10
    mock_q_style_option_view_item.rect.top.side_effect = lambda: 10
    mock_q_style_option_view_item.rect.height.side_effect = lambda: 20
    mocker.patch.object(QMouseEvent, '__new__',
                        lambda x, y: mock_mouse_event)  # Patch the QMouseEvent instantiation to return the same event
    assert is_click_within_bounds(mock_mouse_event,
                                  mock_q_style_option_view_item) == True, 'is_click_within_bounds should return True'
    mock_is_instance.assert_called_once_with(mock_mouse_event, QMouseEvent)
    assert mock_mouse_event.type.call_count == 1, 'Event type call count must be 1'
    assert mock_mouse_event.x.call_count == 1, 'Event x() call count must be 1'
    assert mock_mouse_event.y.call_count == 1, 'Event y() call count must be 1'
    assert mock_q_style_option_view_item.rect.left.call_count == 2, 'QStyleOptionViewItem left call count must be two'
    assert mock_q_style_option_view_item.rect.top.call_count == 2, 'QStyleOptionViewItem top call count must be two'
    assert mock_q_style_option_view_item.rect.width.call_count == 1, 'QStyleOptionViewItem left call count must be 1'
    assert mock_q_style_option_view_item.rect.height.call_count == 1, 'QStyleOptionViewItem top call count must be 1'

  def test_is_click_within_bounds_when_outside_bounds_returns_false(self, mocker):
    mock_mouse_event = mocker.patch('PySide6.QtGui.QSinglePointEvent')
    mock_is_instance = mocker.patch('pasta_eln.GUI.data_hierarchy.utility_functions.isinstance', return_value=True)
    mock_mouse_event.type.side_effect = lambda: QEvent.MouseButtonRelease
    mock_mouse_event.x.side_effect = lambda: 10  # range: 5 -> 15 (within range)
    mock_mouse_event.y.side_effect = lambda: 5  # range: 10 -> 10 (out of range)
    mock_q_style_option_view_item = mocker.patch('PySide6.QtWidgets.QStyleOptionViewItem')
    mock_q_style_option_view_item.rect.left.side_effect = lambda: 5
    mock_q_style_option_view_item.rect.width.side_effect = lambda: 10
    mock_q_style_option_view_item.rect.top.side_effect = lambda: 10
    mock_q_style_option_view_item.rect.height.side_effect = lambda: 20
    mocker.patch.object(QMouseEvent, '__new__',
                        lambda x, y: mock_mouse_event)  # Patch the QMouseEvent instantiation to return the same event
    assert is_click_within_bounds(mock_mouse_event,
                                  mock_q_style_option_view_item) == False, 'is_click_within_bounds should return True'
    mock_is_instance.assert_called_once_with(mock_mouse_event, QMouseEvent)
    assert mock_mouse_event.type.call_count == 1, 'Event type call count must be 1'
    assert mock_mouse_event.x.call_count == 1, 'Event x() call count must be 1'
    assert mock_mouse_event.y.call_count == 1, 'Event y() call count must be 1'
    assert mock_q_style_option_view_item.rect.left.call_count == 2, 'QStyleOptionViewItem left call count must be two'
    assert mock_q_style_option_view_item.rect.top.call_count == 1, 'QStyleOptionViewItem top call count must be one'
    assert mock_q_style_option_view_item.rect.width.call_count == 1, 'QStyleOptionViewItem left call count must be 1'
    assert mock_q_style_option_view_item.rect.height.call_count == 0, 'QStyleOptionViewItem top call count must be zero'

  def test_adjust_data_hierarchy_data_to_v4_when_empty_document_do_nothing(self, mocker):
    contents = {'-version': 2}
    mock_doc = self.create_mock_doc(contents, mocker)
    assert adjust_data_hierarchy_data_to_v4(mock_doc) is None, 'adjust_data_hierarchy_data_to_v4 should return None'
    assert list(contents.keys()) == ['-version'], 'Only version should be added'

    assert adjust_data_hierarchy_data_to_v4(None) is None, 'adjust_data_hierarchy_data_to_v4 should return None'

  @pytest.mark.parametrize('contents, expected_result', [
    (
        {'x0': {'label': '', 'prop': []}},
        {'x0': {'attachments': [], 'title': '', 'meta': {'default': []}}},
    ),
    (
        {'x1': {}},
        {'x1': {'attachments': [], 'title': '', 'meta': {'default': []}}},
    ),
    (
        {
          'x2': {
            'attachments': [{'test': 'test', 'test1': 'test2'}],
            'label': '',
            'prop': {'default': [{'name': 'value', 'test': 'test1'}]},
          }
        },
        {
          'x2': {
            'attachments': [{'test': 'test', 'test1': 'test2'}],
            'title': '',
            'meta': {'default': [{'name': 'value', 'test': 'test1'}]},
          }
        },
    ),
    (
        {
          'x1': {
            'attachments': [{'test': 'test', 'test1': 'test2'}],
            'title': '',
            'meta': {'default': [{'name': 'value', 'test': 'test1'}]},
          }
        },
        {
          'x1': {
            'attachments': [{'test': 'test', 'test1': 'test2'}],
            'title': '',
            'meta': {'default': [{'name': 'value', 'test': 'test1'}]},
          }
        },
    ),
    (
        {'x5': {'attachments': None, 'label': None, 'prop': None}},
        {'x5': {'attachments': None, 'title': None, 'meta': {'default': []}}},
    ),
  ]
                           )
  def test_adjust_data_hierarchy_data_to_v4_given_do_expected(self, contents, expected_result):
    assert adjust_data_hierarchy_data_to_v4(contents) is None, 'adjust_data_hierarchy_data_to_v4 should return None'
    assert are_json_equal(contents, expected_result), 'adjust_data_hierarchy_data_to_v4 should return as expected'

  @staticmethod
  def create_mock_doc(contents, mocker):
    mock_doc = mocker.MagicMock()
    mock_doc.__iter__ = mocker.Mock(return_value=iter(contents))
    mock_doc.__getitem__.side_effect = contents.__getitem__
    mock_doc.__setitem__.side_effect = contents.__setitem__
    return mock_doc

  def test_show_message_with_none_argument_does_nothing(self):
    assert show_message(None) is None, 'show_message should return None'

  def test_show_message_with_valid_argument_shows_message(self, mocker):
    mock_msg_box = mocker.patch('PySide6.QtWidgets.QMessageBox')
    set_text_spy = mocker.spy(mock_msg_box, 'setText')
    mocker.patch.object(QMessageBox, '__new__', lambda s: mock_msg_box)
    mock_exec = mocker.MagicMock()
    mocker.patch.object(mock_msg_box, 'exec', return_value=mock_exec)
    assert show_message('Valid message') is mock_exec, 'show_message should not be None'
    set_text_spy.assert_called_once_with('Valid message')
    mock_msg_box.exec.assert_called_once_with()
    mock_msg_box.setWindowTitle.assert_called_once_with('Data Hierarchy Editor')
    mock_msg_box.setTextFormat.assert_called_once_with(Qt.RichText)
    mock_msg_box.setIcon.assert_called_once_with(QMessageBox.Information)

  def test_show_message_with_error_argument_shows_warning(self, mocker):
    mock_msg_box = mocker.patch('PySide6.QtWidgets.QMessageBox')
    set_text_spy = mocker.spy(mock_msg_box, 'setText')
    mocker.patch.object(QMessageBox, '__new__', lambda s: mock_msg_box)
    mock_exec = mocker.MagicMock()
    mocker.patch.object(mock_msg_box, 'exec', return_value=mock_exec)
    assert show_message('Error message', QMessageBox.Warning) is mock_exec, 'show_message should not be None'
    set_text_spy.assert_called_once_with('Error message')
    mock_msg_box.exec.assert_called_once_with()
    mock_msg_box.setWindowTitle.assert_called_once_with('Data Hierarchy Editor')
    mock_msg_box.setTextFormat.assert_called_once_with(Qt.RichText)
    mock_msg_box.setIcon.assert_called_once_with(QMessageBox.Warning)

  @pytest.mark.parametrize(
    'message, icon, standard_buttons, default_button, expected_result',
    [
      # Happy path tests
      ('Test message', QMessageBox.Icon.Information, QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok,
       QMessageBox.Ok),
      (
          'Another message', QMessageBox.Icon.Warning, QMessageBox.StandardButton.Cancel,
          QMessageBox.StandardButton.Cancel,
          QMessageBox.Cancel),

      # Edge cases
      ('', QMessageBox.Icon.Information, QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok, None),
      # Empty message
      ('Short', QMessageBox.Icon.Critical, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
       QMessageBox.StandardButton.No, QMessageBox.No),

      # Error cases
      ('Invalid icon', None, QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok, None),  # Invalid icon
      ('Invalid buttons', QMessageBox.Icon.Information, None, None, None),  # Invalid buttons
    ],
    ids=[
      'happy_path_info_ok',
      'happy_path_warning_cancel',
      'edge_case_empty_message',
      'edge_case_short_message',
      'error_case_invalid_icon',
      'error_case_invalid_buttons',
    ]
  )
  def test_show_message(self, mocker, message, icon, standard_buttons, default_button, expected_result):
    # Arrange
    mock_message_box = mocker.patch('pasta_eln.GUI.data_hierarchy.utility_functions.QMessageBox')
    mock_message_box.return_value.exec.return_value = expected_result
    mock_message_box.return_value.findChild.return_value = mocker.MagicMock(spec=QLabel)
    # Act
    result = show_message(message, icon, standard_buttons, default_button)

    # Assert
    assert result == expected_result
    if message:
      mock_message_box.return_value.setWindowTitle.assert_called_once_with('Data Hierarchy Editor')
      mock_message_box.return_value.setTextFormat.assert_called_once_with(Qt.TextFormat.RichText)
      mock_message_box.return_value.setIcon.assert_called_once_with(icon)
      mock_message_box.return_value.setText.assert_called_once_with(message)
      mock_message_box.return_value.setStandardButtons.assert_called_once_with(standard_buttons)
      mock_message_box.return_value.setDefaultButton.assert_called_once_with(default_button)
      mock_message_box.return_value.findChild.assert_called_once_with(QLabel, 'qt_msgbox_label')
      mock_message_box.return_value.findChild.return_value.fontMetrics.assert_called_once()
      mock_message_box.return_value.findChild.return_value.fontMetrics.return_value.boundingRect.assert_called_once_with(
        mock_message_box.return_value.findChild.return_value.text.return_value
      )
      mock_message_box.return_value.findChild.return_value.setFixedWidth.assert_called_once_with(
        mock_message_box.return_value.findChild.return_value.fontMetrics.return_value.boundingRect.return_value.width.return_value
      )

  @pytest.mark.parametrize('data_hierarchy_types, expected_result', [
    ({}, ({}, {}, {})),
    (
        {
          'x0': {
            'meta': {
              'default': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
              ],
              'metadata_group1': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
              ],
            }
          },
          'x1': {
            'meta': {
              'default': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
              ],
              'metadata_group2': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
              ],
            }
          },
        },
        (
            {},
            {},
            {
              'Structure level 0': {
                'name': ['default', 'metadata_group1'],
                'tags': ['default', 'metadata_group1'],
              },
              'Structure level 1': {
                'name': ['default', 'metadata_group2'],
                'tags': ['default', 'metadata_group2'],
              },
            },
        ),
    ),
    (
        {
          'x0': {
            'meta': {
              'default': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
                {'name': '    ', 'query': 'What is the name of task?'},
                {'name': None, 'query': 'What is the name of task?'},
              ],
              'metadata_group1': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
                {'name': '', 'query': 'What is the name of task?'},
              ],
            }
          },
          'x1': {
            'meta': {
              'default': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
              ],
              'metadata_group2': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
              ],
              'metadata_group3': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
                {'name': '   ', 'query': 'What is the name of task?'},
              ],
            }
          },
        },
        (
            {},
            {
              'Structure level 0': ['default', 'metadata_group1'],
              'Structure level 1': ['metadata_group3'],
            },
            {
              'Structure level 0': {
                'name': ['metadata_group1', 'default'],
                'tags': ['metadata_group1', 'default'],
              },
              'Structure level 1': {
                'name': ['metadata_group2', 'default', 'metadata_group3'],
                'tags': ['metadata_group2', 'default', 'metadata_group3'],
              },
            },
        ),
    ),
    (
        {
          'x0': {
            'meta': {
              'default': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
              ],
              'metadata_group1': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
              ],
              'metadata_group2': [],
            }
          },
          'x1': {
            'meta': {
              'default': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
              ],
              'metadata_group2': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
              ],
            }
          },
        },
        (
            {},
            {},
            {
              'Structure level 0': {
                'name': ['default', 'metadata_group1'],
                'tags': ['default', 'metadata_group1'],
              },
              'Structure level 1': {
                'name': ['default', 'metadata_group2'],
                'tags': ['default', 'metadata_group2'],
              },
            },
        ),
    ),
    (
        {
          'x0': {
            'meta': {
              'default': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
                {'name': None, 'query': 'What is the name of task?'},
              ],
              'metadata_group1': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
                {'name': None, 'query': 'What is the name of task?'},
              ],
            }
          },
          'x1': {
            'meta': {
              'default': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
                {'name': '', 'query': 'What is the name of task?'},
              ],
              'metadata_group2': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
                {'name': ' ', 'query': 'What is the name of task?'},
              ],
            }
          },
        },
        (
            {},
            {
              'Structure level 0': ['default', 'metadata_group1'],
              'Structure level 1': ['default', 'metadata_group2'],
            },
            {
              'Structure level 0': {
                'name': ['default', 'metadata_group1'],
                'tags': ['default', 'metadata_group1'],
              },
              'Structure level 1': {
                'name': ['default', 'metadata_group2'],
                'tags': ['default', 'metadata_group2'],
              },
            },
        ),
    ),
    (
        {
          'x0': {},
          'x1': {
            'meta': {
              'default': [
                {'name': 'w_name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
              ],
              'metadata_group2': [
                {'name': 'w_name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
              ],
            }
          },
          'test': {
            'meta': {
              'default': [
                {'name': 'name', 'query': 'What is the name of task?'},
                {'name': '', 'query': 'What is the name of task?'},
              ]
            }
          },
        },
        (
            {'Structure level 1': {'default': ['name']}, 'test': {'default': ['tags']}},
            {'test': ['default']},
            {'Structure level 1': {'tags': ['metadata_group2', 'default'], 'w_name': ['metadata_group2', 'default']}},
        ),
    ),
    (
        {
          'x0': {},
          'x1': {
            'meta': {
              'default': [
                {'name': '-name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
                {},
                {},
              ],
              'metadata_group2': [
                {'name': '-name', 'query': 'What is the name of task?'},
                {'name': 'tags', 'query': 'What is the name of task?'},
                {'query': 'What is the name of task?'},
              ],
            }
          },
          'test': {
            'meta': {
              'default': [
                {'name': 'name', 'query': 'What is the name of task?'},
              ]
            }
          },
        },
        (
            {'Structure level 1': {'default': ['name']}, 'test': {'default': ['tags']}},
            {'Structure level 1': ['default', 'metadata_group2']},
            {'Structure level 1': {'-name': ['metadata_group2', 'default'], 'tags': ['metadata_group2', 'default']}},
        ),
    ),
  ]
                           )
  def test_check_data_hierarchy_document_with_full_and_missing_metadata_returns_expected_result(self,
                                                                                                data_hierarchy_types,
                                                                                                expected_result):
    types_with_missing_metadata, types_with_null_name_metadata, types_with_duplicate_metadata = check_data_hierarchy_types(
      data_hierarchy_types)
    assert types_with_missing_metadata == expected_result[
      0], 'check_data_hierarchy_document should return expected types_with_missing_metadata'
    assert types_with_null_name_metadata == expected_result[
      1], 'check_data_hierarchy_document should return expected types_with_null_name_metadata'
    assert len(types_with_duplicate_metadata) == len(
      expected_result[2]), 'check_data_hierarchy_document should return expected types_with_duplicate_metadata'
    for t1, t2 in zip(dict(sorted(types_with_duplicate_metadata.items())).values(),
                      dict(sorted(expected_result[2].items())).values()):
      assert len(t1) == len(t2), 'check_data_hierarchy_document returned types_with_duplicate_metadata length mismatch'
      for d1, d2 in zip(sorted(t1.keys()), (t2.keys())):
        assert d1 == d2, 'check_data_hierarchy_document returned types_with_duplicate_metadata mismatch'
      for g1, g2 in zip(dict(sorted(t1.items())).values(), dict(sorted(t2.items())).values()):
        assert sorted(g1) == sorted(g2), 'check_data_hierarchy_document returned types_with_duplicate_metadata mismatch'

  @pytest.mark.parametrize('type_name, type_value, expected_result', [
    (None, {}, {}),
    (
        'Structure Level 0',
        {
          'meta': {
            'default': [
              {'name': '_name', 'query': 'What is the name of task?'},
              {'name': '_tags', 'query': 'What is the name of task?'},
            ],
            'metadata_group1': [
              {'name': 'name', 'query': 'What is the name of task?'},
              {'name': 'tags', 'query': 'What is the name of task?'},
            ],
          }
        },
        {'Structure Level 0': {'default': ['name', 'tags']}},
    ),
    ('test', {'meta': {'default': []}}, {}),
    ('test1', {'meta': {'default': None}}, {}),
    (
        'Structure Level 0',
        {
          'meta': {
            'default': [
              {'name': 'name', 'query': 'What is the name of task?'},
              {'name': 'tags', 'query': 'What is the name of task?'},
            ],
            'metadata_group1': [
              {'name': 'name', 'query': 'What is the name of task?'},
              {'name': 'tags', 'query': 'What is the name of task?'},
            ],
          }
        },
        {},
    ),
  ]
                           )
  def test_set_types_missing_required_metadata_returns_expected_result(self, type_name, type_value, expected_result):
    types_with_missing_metadata = {}
    assert set_types_missing_required_metadata(type_name, type_value, types_with_missing_metadata) is None
    assert types_with_missing_metadata == expected_result, 'set_types_missing_required_metadata should return expected result'

  @pytest.mark.parametrize('type_name, type_value, expected_result', [
    (None, {}, {}),
    (
        'Structure Level 0',
        {
          'meta': {
            'default': [
              {'name': '', 'query': 'What is the name of task?'},
              {'name': 'tags', 'query': 'What is the name of task?'},
            ],
            'metadata_group1': [
              {'query': 'What is the name of task?'},
              {'name': 'tags', 'query': 'What is the name of task?'},
            ],
          }
        },
        {'Structure Level 0': ['default', 'metadata_group1']},
    ),
    ('test', {'meta': {'default': []}}, {}),
    ('test1', {'meta': {'default': None}}, {}),
    (
        'Structure Level 0',
        {
          'meta': {
            'default': [
              {'name': 'name', 'query': 'What is the name of task?'},
              {'name': None, 'query': 'What is the name of task?'},
              {'name': 'tags', 'query': 'What is the name of task?'},
            ],
            'metadata_group1': [],
          }
        },
        {'Structure Level 0': ['default']},
    ),
    (
        'test',
        {
          'meta': {
            'default': [
              {'name': 'name', 'query': 'What is the name of task?'},
              {'name': None, 'query': 'What is the name of task?'},
              {'name': 'tags', 'query': 'What is the name of task?'},
            ],
            'metadata_group1': [
              {'name': '', 'query': 'What is the name of task?'},
              {'name': None, 'query': 'What is the name of task?'},
              {'name': 'tags', 'query': 'What is the name of task?'},
            ],
          }
        },
        {'test': ['default', 'metadata_group1']},
    ),
    (
        'test1',
        {
          'meta': {
            'default': [
              {'name': 'name', 'query': 'What is the name of task?'},
              {'name': None, 'query': 'What is the name of task?'},
              {'name': 'tags', 'query': 'What is the name of task?'},
            ],
            None: [
              {'name': '', 'query': 'What is the name of task?'},
              {'name': None, 'query': 'What is the name of task?'},
              {'name': 'tags', 'query': 'What is the name of task?'},
            ],
          }
        },
        {'test1': ['default', None]},
    ),
  ])
  def test_set_types_without_name_in_metadata_returns_expected_result(self, type_name, type_value, expected_result):
    types_with_null_name_metadata = {}
    assert set_types_without_name_in_metadata(type_name, type_value, types_with_null_name_metadata) is None
    assert types_with_null_name_metadata == expected_result, 'set_types_without_name_in_metadata should return expected result'

  @pytest.mark.parametrize('type_name, type_value, expected_result',
                           [
                             (None, {}, {}),
                             (None, {'meta': {'default': []}}, {}),
                             (
                                 'Structure Level 0',
                                 {
                                   'meta': {
                                     'default': [
                                       {'name': '', 'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                     ],
                                     'metadata_group1': [
                                       {'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                     ],
                                   }
                                 },
                                 {'Structure Level 0': {'tags': ['default', 'metadata_group1']}},
                             ),
                             ('test', {'meta': {'default': []}}, {}),
                             ('test1', {'meta': {'default': None}}, {}),
                             (
                                 'Structure Level 0',
                                 {
                                   'meta': {
                                     'default': [
                                       {'name': 'name', 'query': 'What is the name of task?'},
                                       {'name': None, 'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                     ],
                                     'metadata_group1': [],
                                   }
                                 },
                                 {},
                             ),
                             (
                                 'test',
                                 {
                                   'meta': {
                                     'default': [
                                       {'name': 'name', 'query': 'What is the name of task?'},
                                       {'name': None, 'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                     ],
                                     'metadata_group1': [
                                       {'name': '', 'query': 'What is the name of task?'},
                                       {'name': None, 'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                     ],
                                   }
                                 },
                                 {'test': {'tags': ['default', 'metadata_group1']}},
                             ),
                             (
                                 'test1',
                                 {
                                   'meta': {
                                     'default': [
                                       {'name': 'name', 'query': 'What is the name of task?'},
                                       {'name': None, 'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                     ],
                                     'test': [
                                       {'name': '', 'query': 'What is the name of task?'},
                                       {'name': None, 'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                     ],
                                   }
                                 },
                                 {'test1': {'tags': ['default', 'test']}},
                             ),
                             (
                                 'test2',
                                 {
                                   'meta': {
                                     'default': [
                                       {'name': 'name', 'query': 'What is the name of task?'},
                                       {
                                         'name': 'duplicate1',
                                         'query': 'What is the name of task?',
                                       },
                                       {
                                         'name': 'duplicate3',
                                         'query': 'What is the name of task?',
                                       },
                                       {
                                         'name': 'duplicate2',
                                         'query': 'What is the name of task?',
                                       },
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                     ],
                                     'group1': [
                                       {'name': '', 'query': 'What is the name of task?'},
                                       {
                                         'name': 'duplicate1',
                                         'query': 'What is the name of task?',
                                       },
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                     ],
                                     'group2': [
                                       {'name': '', 'query': 'What is the name of task?'},
                                       {
                                         'name': 'duplicate1',
                                         'query': 'What is the name of task?',
                                       },
                                       {
                                         'name': 'duplicate2',
                                         'query': 'What is the name of task?',
                                       },
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                     ],
                                     'group3': [
                                       {'name': '', 'query': 'What is the name of task?'},
                                       {
                                         'name': 'duplicate1',
                                         'query': 'What is the name of task?',
                                       },
                                       {
                                         'name': 'duplicate2',
                                         'query': 'What is the name of task?',
                                       },
                                       {
                                         'name': 'duplicate3',
                                         'query': 'What is the name of task?',
                                       },
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                     ],
                                     'group4': [
                                       {'name': '', 'query': 'What is the name of task?'},
                                       {
                                         'name': 'duplicate3',
                                         'query': 'What is the name of task?',
                                       },
                                     ],
                                   }
                                 },
                                 {
                                   'test2': {
                                     'tags': ['group2', 'group3', 'default', 'group1'],
                                     'duplicate1': ['group2', 'group3', 'default', 'group1'],
                                     'duplicate2': ['group2', 'group3', 'default'],
                                     'duplicate3': ['group3', 'default', 'group4'],
                                   }
                                 },
                             ),
                             (
                                 'test',
                                 {
                                   'meta': {
                                     'default': [
                                       {'name': 'name', 'query': 'What is the name of task?'},
                                       {'name': 'name', 'query': 'What is the name of task?'},
                                       {'name': None, 'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                     ],
                                     'metadata_group1': [
                                       {'name': '', 'query': 'What is the name of task?'},
                                       {'name': None, 'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                     ],
                                   }
                                 },
                                 {'test': {'name': ['default'], 'tags': ['default', 'metadata_group1']}},
                             ),
                             (
                                 'test',
                                 {
                                   'meta': {
                                     'default': [
                                       {'name': 'name', 'query': 'What is the name of task?'},
                                       {'name': 'name', 'query': 'What is the name of task?'},
                                       {'name': None, 'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                       {'name': 'new', 'query': 'What is the name of task?'},
                                       {'name': 'new', 'query': 'What is the name of task?'},
                                       {'name': 'new', 'query': 'What is the name of task?'},
                                     ],
                                     'metadata_group1': [
                                       {'name': '', 'query': 'What is the name of task?'},
                                       {'name': None, 'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                     ],
                                   }
                                 },
                                 {
                                   'test': {
                                     'new': ['default'],
                                     'name': ['default'],
                                     'tags': ['default', 'metadata_group1'],
                                   }
                                 },
                             ),
                             (
                                 'test',
                                 {
                                   'meta': {
                                     'default': [
                                       {'name': 'name', 'query': 'What is the name of task?'},
                                       {'name': 'name', 'query': 'What is the name of task?'},
                                       {'name': None, 'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                       {'name': 'new', 'query': 'What is the name of task?'},
                                       {'name': 'new', 'query': 'What is the name of task?'},
                                       {'name': 'new', 'query': 'What is the name of task?'},
                                     ],
                                     'metadata_group1': [
                                       {'name': '', 'query': 'What is the name of task?'},
                                       {'name': None, 'query': 'What is the name of task?'},
                                       {'name': 'test', 'query': 'What is the name of task?'},
                                       {'name': 'test', 'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                     ],
                                     'metadata_group2': [
                                       {'name': '', 'query': 'What is the name of task?'},
                                       {'name': None, 'query': 'What is the name of task?'},
                                       {'name': 'test', 'query': 'What is the name of task?'},
                                       {'name': 'test', 'query': 'What is the name of task?'},
                                       {'name': 'tags', 'query': 'What is the name of task?'},
                                     ],
                                   }
                                 },
                                 {
                                   'test': {
                                     'new': ['default'],
                                     'name': ['default'],
                                     'tags': ['default', 'metadata_group1', 'metadata_group2'],
                                     'test': ['metadata_group1', 'metadata_group2'],
                                   }
                                 },
                             ),
                           ]
                           )
  def test_set_types_with_duplicate_metadata_returns_expected_result(self, type_name, type_value, expected_result):
    types_with_duplicate_metadata = {}
    assert set_types_with_duplicate_metadata(type_name, type_value, types_with_duplicate_metadata) is None
    assert len(types_with_duplicate_metadata) == len(
      expected_result), 'set_types_with_duplicate_metadata should return expected types_with_duplicate_metadata'
    for t1, t2 in zip(dict(sorted(types_with_duplicate_metadata.items())).values(),
                      dict(sorted(expected_result.items())).values()):
      assert len(t1) == len(t2), 'check_data_hierarchy_document returned types_with_duplicate_metadata length mismatch'
      for d1, d2 in zip(sorted(t1.keys()), sorted(t2.keys())):
        assert d1 == d2, 'check_data_hierarchy_document returned types_with_duplicate_metadata mismatch'
      for g1, g2 in zip(dict(sorted(t1.items())).values(), dict(sorted(t2.items())).values()):
        assert sorted(g1) == sorted(g2), 'check_data_hierarchy_document returned types_with_duplicate_metadata mismatch'

  def test_check_data_hierarchy_document_with_null_doc_returns_empty_tuple(self):
    assert check_data_hierarchy_types(None) == ({}, {}, {}), 'check_data_hierarchy_document should return empty tuple'

  @pytest.mark.parametrize('missing_metadata, missing_names, duplicate_metadata, expected_message', [
    ({}, {}, {}, ''),
    (
        {
          'Structure level 0': {
            'metadata_group1': ['name', 'tags'],
            'default': ['name', 'tags'],
          },
          'Structure level 1': {
            'metadata_group2': ['name', 'tags'],
            'default': ['name', 'tags'],
          },
        },
        {
          'Structure level 0': ['default', 'metadata_group1'],
          'Structure level 1': ['default', 'metadata_group2'],
        },
        {
          'Structure level 0': {
            'tags': ['group2', 'group3', 'default', 'group1'],
            'duplicate1': ['group2', 'group3', 'default', 'group1'],
            'duplicate2': ['group2', 'group3', 'default'],
            'duplicate3': ['group3', 'default', 'group4'],
          }
        },
        '<html><b>Missing required metadata: </b><ul><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">metadata_group1</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">name</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">metadata_group1</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">tags</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">name</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">tags</i></li><li>Type: <i style="color:Crimson">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">metadata_group2</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">name</i></li><li>Type: <i style="color:Crimson">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">metadata_group2</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">tags</i></li><li>Type: <i style="color:Crimson">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">name</i></li><li>Type: <i style="color:Crimson">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">tags</i></li></ul><b>Duplicate metadata found: </b><ul><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">group2</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">tags</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">group3</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">tags</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">tags</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">group1</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">tags</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">group2</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">duplicate1</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">group3</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">duplicate1</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">duplicate1</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">group1</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">duplicate1</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">group2</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">duplicate2</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">group3</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">duplicate2</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">duplicate2</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">group3</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">duplicate3</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">duplicate3</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">group4</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">duplicate3</i></li></ul><b>Missing metadata names:</b><ul><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">metadata_group1</i></li><li>Type: <i style="color:Crimson">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i></li><li>Type: <i style="color:Crimson">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">metadata_group2</i></li></ul></html>',
    ),
    (
        {
          'Structure level 0': {
            'metadata_group1': ['name', 'tags'],
            'default': ['name', 'tags'],
          },
          'Structure level 1': {
            'metadata_group2': ['name', 'tags'],
            'default': ['name', 'tags'],
          },
        },
        {},
        {'NewType': {'duplicate3': ['group3', 'default', 'group4']}},
        '<html><b>Missing required metadata: </b><ul><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">metadata_group1</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">name</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">metadata_group1</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">tags</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">name</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">tags</i></li><li>Type: <i style="color:Crimson">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">metadata_group2</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">name</i></li><li>Type: <i style="color:Crimson">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">metadata_group2</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">tags</i></li><li>Type: <i style="color:Crimson">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">name</i></li><li>Type: <i style="color:Crimson">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">tags</i></li></ul><b>Duplicate metadata found: </b><ul><li>Type: <i style="color:Crimson">NewType</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">group3</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">duplicate3</i></li><li>Type: <i style="color:Crimson">NewType</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">duplicate3</i></li><li>Type: <i style="color:Crimson">NewType</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">group4</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">duplicate3</i></li></ul></html>',
    ),
    (
        {},
        {
          'Structure level 0': ['default', 'metadata_group1'],
          'Structure level 1': ['default', 'metadata_group2'],
        },
        {},
        '<html><b>Missing metadata names:</b><ul><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">metadata_group1</i></li><li>Type: <i style="color:Crimson">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i></li><li>Type: <i style="color:Crimson">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">metadata_group2</i></li></ul></html>',
    ),
    (
        {},
        {'Structure level 0': ['default', 'metadata_group1']},
        {
          'Structure level 0': {
            'duplicateName': ['group31', 'default', 'group4']
          }
        },
        '<html><b>Duplicate metadata found: </b><ul><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">group31</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">duplicateName</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">duplicateName</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">group4</i>&nbsp;&nbsp;Metadata Name: <i style="color:Crimson">duplicateName</i></li></ul><b>Missing metadata names:</b><ul><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">default</i></li><li>Type: <i style="color:Crimson">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style="color:Crimson">metadata_group1</i></li></ul></html>',
    ),
  ]
                           )
  def test_get_formatted_missing_or_duplicate_metadata_message_returns_expected_message(self, missing_metadata,
                                                                                        missing_names, expected_message,
                                                                                        duplicate_metadata):
    assert (get_missing_metadata_message(missing_metadata, missing_names,
                                         duplicate_metadata) == expected_message), 'get_missing_metadata_message should return expected'

  @pytest.mark.parametrize(
    'selected_type, expected_result',
    [
      # Success path tests
      ('non_structural', True),  # non-structural type
      ('x1', False),  # structural type but not 'x0'
      ('x0', False),  # structural type 'x0'

      # Edge cases
      ('', False),  # empty string
      (None, False),  # None as input

      # Error cases
      ('x0', False),  # structural type 'x0'
      ('x1', False),  # structural type 'x1'
      ('non_structural', True),  # non-structural type
    ],
    ids=[
      'non_structural_type',
      'structural_type_x1',
      'structural_type_x0',
      'empty_string',
      'none_input',
      'structural_type_x0_error',
      'structural_type_x1_error',
      'non_structural_type_error',
    ]
  )
  def test_can_delete_type(self, mocker, selected_type, expected_result, monkeypatch):
    # Arrange
    mocker.patch('pasta_eln.GUI.data_hierarchy.utility_functions.is_structural_level',
                 side_effect=lambda title: title in {'x0', 'x1'})

    # Act
    result = can_delete_type(selected_type)

    # Assert
    assert result == expected_result
