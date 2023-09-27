#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_delegate_funcs_common.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Union

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton, QStyleOptionButton, QApplication, QStyle

from pasta_eln.GUI.ontology_configuration.delete_column_delegate import DeleteColumnDelegate
from pasta_eln.GUI.ontology_configuration.reorder_column_delegate import ReorderColumnDelegate
from tests.app_tests.common.fixtures import delete_delegate, reorder_delegate


def delegate_paint_common(mocker,
                          delegate: Union[delete_delegate, reorder_delegate],
                          button_icon):
  mock_painter = mocker.patch("PySide6.QtGui.QPainter")
  mock_option = mocker.patch("PySide6.QtWidgets.QStyleOptionViewItem")
  mock_index = mocker.patch("PySide6.QtCore.QModelIndex")
  mock_push_button = mocker.patch("PySide6.QtWidgets.QPushButton")
  mock_button_option = mocker.patch("PySide6.QtWidgets.QStyleOptionButton")
  mock_icon_size = mocker.patch("PySide6.QtCore.QSize")
  mock_icon = mocker.patch("PySide6.QtGui.QIcon")
  mocker.patch.object(QPushButton, "__new__",
                      lambda x: mock_push_button)
  mocker.patch.object(QStyleOptionButton, "__new__",
                      lambda x: mock_button_option)
  mocker.patch.object(QSize, "__new__",
                      lambda x, y, z: mock_icon_size)
  mock_style = mocker.patch("PySide6.QtWidgets.QStyle")
  draw_control_spy = mocker.spy(mock_style, 'drawControl')
  standard_icon_spy = mocker.patch.object(mock_style, 'standardIcon', return_value=mock_icon)
  mocker.patch.object(QApplication, "style",
                      lambda: mock_style)

  delegate.paint(mock_painter, mock_option, mock_index)
  draw_control_spy.assert_called_once_with(QStyle.CE_PushButton, mock_button_option, mock_painter, mock_push_button)
  assert mock_button_option.rect == mock_option.rect, "rect should be the same as the option passed"
  standard_icon_spy.assert_called_once_with(button_icon)
  assert mock_button_option.iconSize == mock_icon_size, "icon size should be the same as the size passed"
  assert mock_button_option.icon == mock_icon, "icon should be the same as the icon passed"
  assert mock_button_option.state == QStyle.State_Active | QStyle.State_Enabled, "button state should be active and enabled"


def delegate_editor_method_common(delegate: Union[delete_delegate, reorder_delegate],
                                  mocker):
  mock_painter = mocker.patch("PySide6.QtGui.QPainter")
  mock_option = mocker.patch("PySide6.QtWidgets.QStyleOptionViewItem")
  mock_index = mocker.patch("PySide6.QtCore.QModelIndex")
  assert delegate.createEditor(mock_painter,
                               mock_option,
                               mock_index) is None, "create editor should return None"


def delegate_editor_event_common(delegate: Union[delete_delegate, reorder_delegate],
                                 mocker,
                                 is_click_within_bounds):
  mock_event = mocker.patch("PySide6.QtCore.QEvent")
  mock_model = mocker.patch("PySide6.QtCore.QAbstractItemModel")
  mock_index = mocker.patch("PySide6.QtCore.QModelIndex")
  mock_option = mocker.patch("PySide6.QtWidgets.QStyleOptionViewItem")
  mocker.patch.object(mock_index, "row",
                      mocker.MagicMock(return_value=2))
  emit_spy = None
  if type(delegate) is DeleteColumnDelegate:
    delegate.delete_clicked_signal = mocker.patch("PySide6.QtCore.Signal")
    emit_spy = mocker.spy(delegate.delete_clicked_signal, 'emit')
  elif type(delegate) is ReorderColumnDelegate:
    delegate.re_order_signal = mocker.patch("PySide6.QtCore.Signal")
    emit_spy = mocker.spy(delegate.re_order_signal, 'emit')
  assert delegate.editorEvent(mock_event,
                              mock_model,
                              mock_option,
                              mock_index) is is_click_within_bounds, "editorEvent should return True"
  row_call_count = 1 if is_click_within_bounds else 0
  assert mock_index.row.call_count == row_call_count, f"index.row should be called {row_call_count} times"
  assert emit_spy, "emit should be set"
  if is_click_within_bounds:
    emit_spy.assert_called_once_with(2)
  else:
    assert emit_spy.call_count == 0, "emit should not be called"
