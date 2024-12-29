#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_iri_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QStyledItemDelegate

from pasta_eln.GUI.data_hierarchy.iri_column_delegate import IriColumnDelegate
from pasta_eln.GUI.data_hierarchy.lookup_iri_action import LookupIriAction
from testsAdvanced.common.fixtures import iri_delegate


class TestDataHierarchyIriColumnDelegate(object):
  def test_instantiate_column_delegate_should_succeed(self, mocker):
    mock_base_init = mocker.patch.object(QStyledItemDelegate, '__init__')
    mock_logger = mocker.patch('logging.Logger')
    mock_get_logger = mocker.patch.object(logging, 'getLogger', return_value=mock_logger)
    delegate = IriColumnDelegate()
    mock_base_init.assert_called_once_with()
    mock_get_logger.assert_called_once_with('pasta_eln.GUI.data_hierarchy.iri_column_delegate.IriColumnDelegate')
    assert delegate.logger is mock_logger, 'logger should be set'

  def test_create_editor_should_return_line_edit(self, mocker, iri_delegate: iri_delegate):
    mock_parent = mocker.patch('PySide6.QtWidgets.QWidget')
    mock_line_edit = mocker.patch('PySide6.QtWidgets.QLineEdit')
    mock_lookup_iri_action = mocker.patch('pasta_eln.GUI.data_hierarchy.lookup_iri_action.LookupIriAction')
    mock_lookup_iri_action_construct = mocker.patch.object(LookupIriAction, '__new__',
                                                           return_value=mock_lookup_iri_action)
    mock_line_edit_construct = mocker.patch.object(QLineEdit, '__new__', return_value=mock_line_edit)
    mock_line_edit_add_action = mocker.patch.object(mock_line_edit, 'addAction')
    mock_line_set_clear_button_enabled = mocker.patch.object(mock_line_edit, 'setClearButtonEnabled')
    mock_style_option = mocker.patch('PySide6.QtWidgets.QStyleOptionViewItem')
    mock_model_index = mocker.patch('PySide6.QtCore.QModelIndex')
    mock_model_index.siblingAtColumn.return_value.data.return_value = 'default'
    line_edit = iri_delegate.createEditor(mock_parent, mock_style_option, mock_model_index)
    assert line_edit is mock_line_edit, 'line edit should be returned'
    mock_lookup_iri_action_construct.assert_called_once_with(LookupIriAction, cell_index=mock_model_index,
                                                             lookup_term='default')
    mock_line_edit_construct.assert_called_once_with(QLineEdit, mock_parent)
    mock_line_edit_add_action.assert_called_once_with(mock_lookup_iri_action, QLineEdit.TrailingPosition)
    mock_line_set_clear_button_enabled.assert_called_once_with(True)
    mock_model_index.isValid.assert_called_once_with()
    mock_model_index.siblingAtColumn.assert_called_once_with(0)
    mock_model_index.siblingAtColumn.return_value.data.assert_called_once_with(Qt.UserRole)
