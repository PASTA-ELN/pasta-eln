#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_mandatory_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest
from PySide6.QtCore import QEvent, QRect, Qt
from PySide6.QtWidgets import QApplication, QRadioButton, QStyle, QStyleOptionButton, QStyledItemDelegate

from tests.common.fixtures import mandatory_delegate
from tests.common.test_delegate_funcs_common import delegate_editor_method_common


class TestDataHierarchyMandatoryColumnDelegate(object):
  def test_delegate_paint_method(self, mocker, mandatory_delegate: mandatory_delegate):
    # When data set if True, the mandatory radio box is checked
    self.verify_delegate_paint_method(mocker, mandatory_delegate, 'True')
    # When data set if False, the mandatory radio box is un-checked
    self.verify_delegate_paint_method(mocker, mandatory_delegate, 'False')

  def test_delegate_create_editor_method(self, mocker, mandatory_delegate: mandatory_delegate):
    delegate_editor_method_common(mandatory_delegate, mocker)

  @pytest.mark.parametrize("test_data_value, expected", [(False, True), (True, False)])
  def test_delegate_editor_event_method(self, mocker, mandatory_delegate: mandatory_delegate, test_data_value,
                                        expected):
    mock_option_event = mocker.patch("PySide6.QtCore.QEvent")
    mock_table_model = mocker.patch("PySide6.QtCore.QAbstractItemModel")
    mock_option = mocker.patch("PySide6.QtWidgets.QStyleOptionViewItem")
    mock_index = mocker.patch("PySide6.QtCore.QModelIndex")

    mocker.patch.object(mock_index, "data", mocker.MagicMock(return_value=test_data_value))
    mocker.patch.object(QStyledItemDelegate, "editorEvent", mocker.MagicMock(return_value=expected))
    mocker.patch.object(mock_option_event, "type", mocker.MagicMock(return_value=QEvent.MouseButtonRelease))
    model_set_data_spy = mocker.spy(mock_table_model, 'setData')
    delegate_editor_event_spy = mocker.spy(QStyledItemDelegate, 'editorEvent')
    assert mandatory_delegate.editorEvent(mock_option_event, mock_table_model, mock_option,
                                          mock_index) is expected, "editorEvent should return expected value"

    assert mock_option_event.type.call_count == 1, "editorEvent.type should be called once"
    assert mock_index.data.call_count == 1, "editorEvent.index.data should be called once"
    model_set_data_spy.assert_called_once_with(mock_index, expected, Qt.UserRole)
    delegate_editor_event_spy.assert_called_once_with(mock_option_event, mock_table_model, mock_option, mock_index)

  @staticmethod
  def verify_delegate_paint_method(mocker, mandatory_delegate, editor_data_value):
    mock_painter = mocker.patch("PySide6.QtGui.QPainter")
    mock_option = mocker.patch("PySide6.QtWidgets.QStyleOptionViewItem")
    mock_option_rect = mocker.patch("PySide6.QtCore.QRect")
    mock_index = mocker.patch("PySide6.QtCore.QModelIndex")
    mock_option_widget = mocker.patch("PySide6.QtWidgets.QRadioButton")
    mock_option_radio_button = mocker.patch("PySide6.QtWidgets.QRadioButton")
    mock_button_option = mocker.patch("PySide6.QtWidgets.QStyleOptionButton")
    mock_style = mocker.patch("PySide6.QtWidgets.QStyle")
    mocker.patch.object(QStyleOptionButton, "__new__", lambda x: mock_button_option)
    mocker.patch.object(QRadioButton, "__new__", lambda x: mock_option_radio_button)
    mocker.patch.object(mock_option, "widget", None)
    mocker.patch.object(mock_option, "rect", mock_option_rect)
    mocker.patch.object(mock_option_rect, "left", mocker.MagicMock(return_value=5))
    mocker.patch.object(mock_option_rect, "top", mocker.MagicMock(return_value=5))
    mocker.patch.object(mock_option_rect, "height", mocker.MagicMock(return_value=5))
    mocker.patch.object(mock_option_rect, "width", mocker.MagicMock(return_value=5))
    mocker.patch.object(mock_index, "data", mocker.MagicMock(return_value=editor_data_value))
    mocker.patch.object(QStyle, "State_On", QStyle.State_On)
    mocker.patch.object(QStyle, "State_Off", QStyle.State_Off)
    mocker.patch.object(QApplication, "style", lambda: mock_style)
    mocker.patch.object(mock_option_widget, "style", mocker.MagicMock(return_value=mock_style))
    draw_control_spy = mocker.spy(mock_style, 'drawControl')
    mandatory_delegate.paint(mock_painter, mock_option, mock_index)
    draw_control_spy.assert_called_once_with(QStyle.CE_RadioButton, mock_button_option, mock_painter,
                                             mock_option_radio_button)
    assert mock_option.rect.left.call_count == 1, "rect.left should be called once"
    assert mock_option.rect.top.call_count == 1, "rect.top should be called once"
    assert mock_option.rect.width.call_count == 2, "rect.top should be called twice"
    assert mock_option.rect.height.call_count == 1, "rect.height should be called once"
    assert mock_button_option.rect == QRect(-2, 5, 5, 5), "rect should be the expected QRect(-2, 5, 5, 5)"
    assert mock_button_option.state == QStyle.State_On if editor_data_value == 'True' else QStyle.State_Off, f"button state should be {'on' if editor_data_value == 'True' else 'off'}"
