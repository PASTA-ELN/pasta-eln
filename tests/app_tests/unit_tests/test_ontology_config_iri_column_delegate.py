#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_iri_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging

from PySide6.QtWidgets import QStyledItemDelegate, QLineEdit

from pasta_eln.GUI.ontology_configuration.iri_column_delegate import IriColumnDelegate
from pasta_eln.GUI.ontology_configuration.retrieve_iri_action import RetrieveIriAction
from tests.app_tests.common.fixtures import iri_delegate


class TestOntologyConfigIriColumnDelegate(object):
  def test_instantiate_column_delegate_should_succeed(self, mocker):
    mock_base_init = mocker.patch.object(QStyledItemDelegate, '__init__')
    mock_logger = mocker.patch('logging.Logger')
    mock_get_logger = mocker.patch.object(logging, 'getLogger', return_value=mock_logger)
    delegate = IriColumnDelegate()
    mock_base_init.assert_called_once_with()
    mock_get_logger.assert_called_once_with(
      'pasta_eln.GUI.ontology_configuration.iri_column_delegate.IriColumnDelegate')
    assert delegate.logger is mock_logger, "logger should be set"

  def test_create_editor_should_return_line_edit(self,
                                                 mocker,
                                                 iri_delegate: iri_delegate):
    mock_parent = mocker.patch('PySide6.QtWidgets.QWidget')
    mock_line_edit = mocker.patch('PySide6.QtWidgets.QLineEdit')
    mock_retrieve_iri_action = mocker.patch(
      'pasta_eln.GUI.ontology_configuration.retrieve_iri_action.RetrieveIriAction')
    mock_retrieve_iri_action_construct = mocker.patch.object(RetrieveIriAction, '__new__',
                                                             return_value=mock_retrieve_iri_action)
    mock_line_edit_construct = mocker.patch.object(QLineEdit, '__new__', return_value=mock_line_edit)
    mock_line_edit_add_action = mocker.patch.object(mock_line_edit, 'addAction')
    mock_line_set_clear_button_enabled = mocker.patch.object(mock_line_edit, 'setClearButtonEnabled')
    mock_style_option = mocker.patch('PySide6.QtWidgets.QStyleOptionViewItem')
    mock_model_index = mocker.patch('PySide6.QtCore.QModelIndex')
    line_edit = iri_delegate.createEditor(mock_parent, mock_style_option, mock_model_index)
    assert line_edit is mock_line_edit, "line edit should be returned"
    mock_retrieve_iri_action_construct.assert_called_once_with(RetrieveIriAction, parent=mock_line_edit)
    mock_line_edit_construct.assert_called_once_with(QLineEdit, mock_parent)
    mock_line_edit_add_action.assert_called_once_with(mock_retrieve_iri_action, QLineEdit.TrailingPosition)
    mock_line_set_clear_button_enabled.assert_called_once_with(True)
