#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_lookup_iri_action.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon

from pasta_eln.GUI.ontology_configuration.lookup_iri_action import LookupIriAction
from tests.app_tests.common.fixtures import lookup_iri_action


class TestOntologyConfigLookupIriAction(object):

  def test_lookup_iri_action_initialize_should_succeed(self, mocker):
    mock_base_init = mocker.patch.object(QAction, '__init__')
    mocker.patch.object(QAction, 'triggered', create=True)
    mock_base_triggered_connect = mocker.patch.object(QAction.triggered, 'connect', create=True)
    mock_icon = mocker.patch('PySide6.QtGui.QIcon')
    mock_icon_from_theme = mocker.patch.object(QIcon, 'fromTheme', return_value=mock_icon)
    mock_parent = mocker.patch('PySide6.QtWidgets.QLineEdit')
    mock_cell_index = mocker.patch('PySide6.QtCore.QModelIndex')
    mock_logger = mocker.patch('logging.Logger')
    mock_get_logger = mocker.patch.object(logging, 'getLogger', return_value=mock_logger)
    mock_dialog = mocker.MagicMock()
    mock_terminology_lookup_dialog = mocker.patch(
      'pasta_eln.GUI.ontology_configuration.lookup_iri_action.TerminologyLookupDialog', return_value=mock_dialog)
    action = LookupIriAction(lookup_term="default", parent_line_edit=mock_parent, cell_index=mock_cell_index)
    mock_base_init.assert_called_once_with(
      icon=mock_icon,
      text="Lookup IRI online",
      parent=mock_parent
    )
    mock_base_triggered_connect.assert_called_once_with(action.show_terminology_lookup_dialog)
    mock_get_logger.assert_called_once_with(
      'pasta_eln.GUI.ontology_configuration.lookup_iri_action.LookupIriAction')
    mock_icon_from_theme.assert_called_once_with("go-next")
    mock_terminology_lookup_dialog.assert_called_once_with("default", action.terminology_lookup_accepted_callback)
    assert action.logger is mock_logger, "logger should be set"
    assert action.terminology_lookup_dialog is mock_dialog, "dialog should be set"
    assert action.cell_index is mock_cell_index, "cell_index should be set"
    assert action.parent_line_edit is mock_parent, "parent_line_edit should be set"

  def test_lookup_iris_invoke_should_show_terminology_lookup_dialog(self,
                                                                    mocker,
                                                                    lookup_iri_action: lookup_iri_action):
    mocker.patch.object(QAction, 'triggered', create=True)
    mock_log_info = mocker.patch.object(lookup_iri_action.logger, 'info')
    mock_show = mocker.patch.object(lookup_iri_action.terminology_lookup_dialog, 'show')
    assert lookup_iri_action.show_terminology_lookup_dialog() is None, "Nothing should be returned"
    mock_log_info.assert_called_once_with('Lookup dialog shown..')
    mock_show.assert_called_once_with()

  def test_terminology_lookup_accepted_callback_should_do_as_expected(self,
                                                                      mocker,
                                                                      lookup_iri_action: lookup_iri_action):
    mock_line_edit = mocker.patch('PySide6.QtWidgets.QLineEdit')
    mocker.patch.object(lookup_iri_action, 'logger', create=True)
    mocker.patch.object(lookup_iri_action, 'parent_line_edit', mock_line_edit, create=True)
    mocker.patch.object(lookup_iri_action, 'cell_index', create=True)
    mocker.patch.object(lookup_iri_action, 'terminology_lookup_dialog', create=True)
    lookup_iri_action.terminology_lookup_dialog.selected_iris = ['iri1', 'iri2']
    assert lookup_iri_action.terminology_lookup_accepted_callback() is None, "Nothing should be returned"
    lookup_iri_action.logger.info.assert_called_once_with("Accepted IRIs: %s",
                                                          lookup_iri_action.terminology_lookup_dialog.selected_iris)
    iris = " ".join(lookup_iri_action.terminology_lookup_dialog.selected_iris)
    lookup_iri_action.parent_line_edit.setText.assert_called_once_with(iris)
    lookup_iri_action.cell_index.isValid.assert_called_once_with()
    lookup_iri_action.cell_index.model.assert_called_once_with()
    lookup_iri_action.cell_index.model.return_value.setData.assert_called_once_with(lookup_iri_action.cell_index, iris,
                                                                                    Qt.UserRole)
    mock_line_edit.setText.assert_called_once_with(iris)
