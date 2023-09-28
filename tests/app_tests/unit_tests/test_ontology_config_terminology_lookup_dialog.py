#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_terminology_lookup_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging

from PySide6 import QtCore
from PySide6.QtWidgets import QCheckBox, QLabel

from pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog import TerminologyLookupDialog
from pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog_base import Ui_TerminologyLookupDialogBase
from tests.app_tests.common.fixtures import terminology_lookup_dialog_mock


class TestOntologyConfigTerminologyLookupDialog(object):

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

  def test_add_scroll_area_entry_should_do_as_expected(self,
                                                       mocker,
                                                       terminology_lookup_dialog_mock: terminology_lookup_dialog_mock):
    mock_scroll_area_layout = mocker.patch('PySide6.QtWidgets.QHBoxLayout')
    mock_pixmap = mocker.patch('PySide6.QtGui.QPixmap')
    mock_entry_checkbox = mocker.patch('PySide6.QtWidgets.QCheckBox')
    mock_entry_label = mocker.patch('PySide6.QtWidgets.QLabel')
    mock_logger_info = mocker.patch.object(terminology_lookup_dialog_mock.logger, 'info')

    mock_layout = mocker.MagicMock()
    mock_entry_layout_constructor = mocker.patch(
      'pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog.QHBoxLayout', return_value=mock_layout)
    mock_entry_widget = mocker.MagicMock()
    mock_entry_widget_constructor = mocker.patch(
      'pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog.QWidget', return_value=mock_entry_widget)

    mocker.patch.object(QCheckBox, '__init__', return_value=None)
    mocker.patch.object(QLabel, '__init__', return_value=None)
    mock_entry_label_constructor = mocker.patch.object(QLabel, '__new__', return_value=mock_entry_label)
    mock_entry_layout_add_widget = mocker.patch.object(mock_layout, 'addWidget')
    mock_entry_layout_add_stretch = mocker.patch.object(mock_layout, 'addStretch')
    mock_entry_widget_set_layout = mocker.patch.object(mock_entry_widget, 'setLayout')

    mocker.patch.object(terminology_lookup_dialog_mock, 'scrollAreaContentsVerticalLayout', mock_scroll_area_layout,
                        create=True)
    mock_scroll_area_layout_add_widget = mocker.patch.object(
      terminology_lookup_dialog_mock.scrollAreaContentsVerticalLayout, 'addWidget')

    assert terminology_lookup_dialog_mock.add_scroll_area_entry(mock_pixmap,
                                                                "Checkbox Text") is None, "show should return None"
    mock_entry_layout_constructor.assert_called_once_with()
    mock_entry_widget_constructor.assert_called_once_with()
    mock_entry_layout_add_widget.asser_called_anytime(mock_entry_checkbox)
    mock_entry_label_constructor.assert_called_once_with(QLabel, pixmap=mock_pixmap)
    mock_entry_layout_add_widget.asser_called_anytime(mock_entry_label)
    mock_entry_layout_add_stretch.asser_called_once_with(1)
    mock_entry_widget_set_layout.assert_called_once_with(mock_layout)
    mock_scroll_area_layout_add_widget.assert_called_once_with(mock_entry_widget)
    mock_logger_info.assert_called_once_with("Adding entry to scroll area, checkbox_text: %s", "Checkbox Text")

  def test_clear_scroll_area_should_do_as_expected(self,
                                                   mocker,
                                                   terminology_lookup_dialog_mock: terminology_lookup_dialog_mock):
    mock_widget = mocker.patch('PySide6.QtWidgets.QWidget')
    mock_scroll_area_layout = mocker.patch('PySide6.QtWidgets.QHBoxLayout')
    mock_logger_info = mocker.patch.object(terminology_lookup_dialog_mock.logger, 'info')
    mocker.patch.object(terminology_lookup_dialog_mock,
                        'scrollAreaContentsVerticalLayout',
                        mock_scroll_area_layout,
                        create=True)
    mock_scroll_area_layout_count = mocker.patch.object(mock_scroll_area_layout, 'count', return_value=5)
    item_layout = mocker.MagicMock()
    mock_item_at = mocker.patch.object(mock_scroll_area_layout, 'itemAt', return_value=item_layout)
    mock_get_widget = mocker.patch.object(item_layout, 'widget', return_value=mock_widget)
    mock_set_parent = mocker.patch.object(mock_widget, 'setParent')

    assert terminology_lookup_dialog_mock.clear_scroll_area() is None, "show should return None"
    mock_scroll_area_layout_count.assert_called_once_with()
    mock_item_at.assert_has_calls(
      [mocker.call(4), mocker.call(3), mocker.call(2), mocker.call(1), mocker.call(0)])
    assert mock_get_widget.has_calls(
      [mocker.call(), mocker.call(), mocker.call(), mocker.call(), mocker.call()])
    mock_set_parent.assert_has_calls(
      [mocker.call(None), mocker.call(None), mocker.call(None), mocker.call(None), mocker.call(None)])
    mock_logger_info.assert_called_once_with("Clearing scroll area..")
