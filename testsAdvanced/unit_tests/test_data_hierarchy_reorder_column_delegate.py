#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_reorder_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from PySide6.QtWidgets import QStyle

from tests.common.fixtures import reorder_delegate
from tests.common.test_delegate_funcs_common import delegate_editor_event_common, delegate_editor_method_common, \
  delegate_paint_common


class TestDataHierarchyReorderColumnDelegate(object):
  def test_delegate_paint_method(self, mocker, reorder_delegate: reorder_delegate):
    delegate_paint_common(mocker, reorder_delegate, QStyle.StandardPixmap.SP_ArrowUp)

  def test_delegate_create_editor_method(self, mocker, reorder_delegate: reorder_delegate):
    delegate_editor_method_common(reorder_delegate, mocker)

  def test_delegate_create_editor_event_method_when_clicked_within_bounds_returns_true(self, mocker,
                                                                                       reorder_delegate: reorder_delegate):
    mocker.patch('pasta_eln.GUI.data_hierarchy.reorder_column_delegate.is_click_within_bounds', return_value=True)
    delegate_editor_event_common(reorder_delegate, mocker, is_click_within_bounds=True)

  def test_delegate_create_editor_event_method_when_clicked_outside_bounds_returns_false(self, mocker,
                                                                                         reorder_delegate: reorder_delegate):
    mocker.patch('pasta_eln.GUI.data_hierarchy.reorder_column_delegate.is_click_within_bounds', return_value=False)
    delegate_editor_event_common(reorder_delegate, mocker, is_click_within_bounds=False)
