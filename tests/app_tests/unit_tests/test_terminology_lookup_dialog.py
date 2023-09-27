#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_terminology_lookup_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging

from PySide6 import QtCore

from pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog import TerminologyLookupDialog
from pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog_base import Ui_TerminologyLookupDialogBase
from tests.app_tests.common.fixtures import terminology_lookup_dialog_mock


class TestTerminologyLookupDialog(object):

  def test_terminology_lookup_dialog_instantiation_should_succeed(self,
                                                                  mocker):
    mock_logger = mocker.patch('logging.Logger')
    mock_get_logger = mocker.patch.object(logging, 'getLogger', return_value=mock_logger)
    mock_dialog = mocker.MagicMock()
    mock_q_dialog_constructor = mocker.patch('PySide6.QtWidgets.QDialog', return_value=mock_dialog)
    mock_base_setup = mocker.patch.object(Ui_TerminologyLookupDialogBase, 'setupUi')
    dialog = TerminologyLookupDialog()
    mock_q_dialog_constructor.assert_called_once_with()
    mock_base_setup.assert_called_once_with(mock_dialog)
    mock_get_logger.assert_called_once_with(
      'pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog.TerminologyLookupDialog')
    assert dialog.instance is mock_dialog, "dialog instance should be returned"
    assert dialog.logger is mock_logger, "logger should be set"

  def test_terminology_lookup_dialog_show_should_do_as_expected(self,
                                                                mocker,
                                                                terminology_lookup_dialog_mock: terminology_lookup_dialog_mock):
    mock_show = mocker.patch.object(terminology_lookup_dialog_mock.instance, 'show')
    mock_set_window_modality = mocker.patch.object(terminology_lookup_dialog_mock.instance, 'setWindowModality')
    assert terminology_lookup_dialog_mock.show() is None, "show should return None"
    mock_set_window_modality.assert_called_once_with(QtCore.Qt.ApplicationModal)
    mock_show.assert_called_once_with()
