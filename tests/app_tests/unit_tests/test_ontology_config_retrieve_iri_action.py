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
    assert action.logger is mock_logger, "logger should be set"
