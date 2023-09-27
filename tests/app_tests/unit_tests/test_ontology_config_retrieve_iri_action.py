#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_retrieve_iri_action.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging

from PySide6.QtGui import QAction, QIcon

from pasta_eln.GUI.ontology_configuration.retrieve_iri_action import RetrieveIriAction
from tests.app_tests.common.fixtures import retrieve_iri_action


class TestOntologyConfigRetrieveIriAction(object):

  def test_retrieve_iri_action_init_returns_expected(self, mocker):
    mock_base_init = mocker.patch.object(QAction, '__init__')
    mocker.patch.object(QAction, 'triggered', create=True)
    mock_base_triggered_connect = mocker.patch.object(QAction.triggered, 'connect', create=True)
    mock_icon = mocker.patch('PySide6.QtGui.QIcon')
    mock_icon_from_theme = mocker.patch.object(QIcon, 'fromTheme', return_value=mock_icon)
    mock_parent = mocker.patch('PySide6.QtWidgets.QWidget')
    mock_logger = mocker.patch('logging.Logger')
    mock_get_logger = mocker.patch.object(logging, 'getLogger', return_value=mock_logger)
    mock_dialog = mocker.MagicMock()
    mock_terminology_lookup_dialog = mocker.patch(
      'pasta_eln.GUI.ontology_configuration.retrieve_iri_action.TerminologyLookupDialog', return_value=mock_dialog)
    action = RetrieveIriAction(mock_parent)
    mock_base_init.assert_called_once_with(
      icon=mock_icon,
      text="Lookup IRI online",
      parent=mock_parent
    )
    mock_base_triggered_connect.assert_called_once_with(action.retrieve_iris)
    mock_get_logger.assert_called_once_with(
      'pasta_eln.GUI.ontology_configuration.retrieve_iri_action.RetrieveIriAction')
    mock_icon_from_theme.assert_called_once_with("go-next")
    mock_terminology_lookup_dialog.assert_called_once_with()
    assert action.logger is mock_logger, "logger should be set"
    assert action.terminology_lookup_dialog is mock_dialog, "dialog should be set"

  def test_retrieve_iris_invoke_should_show_terminology_lookup_dialog(self,
                                                                      mocker,
                                                                      retrieve_iri_action: retrieve_iri_action):
    mocker.patch.object(QAction, 'triggered', create=True)
    mock_log_info = mocker.patch.object(retrieve_iri_action.logger, 'info')
    mock_show = mocker.patch.object(retrieve_iri_action.terminology_lookup_dialog, 'show')
    assert retrieve_iri_action.retrieve_iris() is None, "Nothing should be returned"
    mock_log_info.assert_called_once_with("IRI lookup initiated..")
    mock_show.assert_called_once_with()
