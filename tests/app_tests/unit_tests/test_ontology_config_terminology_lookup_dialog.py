#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_terminology_lookup_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging
import textwrap

import pytest
from PySide6 import QtCore
from PySide6.QtWidgets import QCheckBox, QLabel

from pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog import TerminologyLookupDialog
from pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog_base import Ui_TerminologyLookupDialogBase
from tests.app_tests.common.fixtures import retrieved_iri_results_name_mock, retrieved_iri_results_pasta_mock, \
  retrieved_iri_results_science_mock, terminology_lookup_dialog_mock


class TestOntologyConfigTerminologyLookupDialog(object):
  def test_terminology_lookup_dialog_instantiation_should_succeed(self,
                                                                  mocker,
                                                                  retrieved_iri_results_pasta_mock: retrieved_iri_results_pasta_mock,
                                                                  # To enable fixture import used by other tests
                                                                  retrieved_iri_results_name_mock: retrieved_iri_results_name_mock,
                                                                  # To enable fixture import used by other tests
                                                                  retrieved_iri_results_science_mock: retrieved_iri_results_science_mock):  # To enable fixture import used by other tests
    mock_logger = mocker.patch('logging.Logger')
    mock_get_logger = mocker.patch.object(logging, 'getLogger', return_value=mock_logger)
    mock_dialog = mocker.MagicMock()
    mock_q_dialog_constructor = mocker.patch('PySide6.QtWidgets.QDialog', return_value=mock_dialog)
    mock_base_setup = mocker.patch.object(Ui_TerminologyLookupDialogBase, 'setupUi')
    mocker.patch.object(Ui_TerminologyLookupDialogBase, 'terminologySearchPushButton', create=True)
    mocker.patch.object(Ui_TerminologyLookupDialogBase, 'terminologyLineEdit', create=True)

    mock_error_console_push_button = mocker.patch.object(Ui_TerminologyLookupDialogBase, 'errorConsolePushButton',
                                                         create=True)
    mock_search_push_button_clicked = mocker.patch.object(mock_error_console_push_button, 'clicked', create=True)
    mocker.patch.object(mock_search_push_button_clicked, 'connect')

    mock_error_console_text_edit = mocker.patch.object(Ui_TerminologyLookupDialogBase, 'errorConsoleTextEdit',
                                                       create=True)
    mock_error_console_text_edit_hide = mocker.patch.object(mock_error_console_text_edit, 'hide')
    mocker.patch.object(mock_error_console_text_edit, 'isVisible')
    mocker.patch.object(mock_error_console_text_edit, 'setVisible')
    mock_terminology_lookup_service = mocker.patch(
      'pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog.TerminologyLookupService')
    mock_pixmap = mocker.MagicMock()
    mock_pixmap_constructor = mocker.patch('pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog.QPixmap',
                                           return_value=mock_pixmap)
    mock_pixmap_scaled_to_width = mocker.patch.object(mock_pixmap, 'scaledToWidth', return_value=mock_pixmap)

    mock_buttonbox = mocker.MagicMock()
    mocker.patch.object(Ui_TerminologyLookupDialogBase, 'buttonBox', mock_buttonbox, create=True)
    mock_accepted_connect = mocker.patch.object(mock_buttonbox.accepted, 'connect')

    mock_dir_name = mocker.MagicMock()
    mock_cd = mocker.MagicMock()
    mock_join = mocker.MagicMock()
    mock_realpath = mocker.MagicMock()
    mock_os_path_dir_name = mocker.patch('pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog.dirname',
                                         return_value=mock_dir_name)
    mock_os_path_get_cwd = mocker.patch('pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog.getcwd',
                                        return_value=mock_cd)
    mock_os_path_join = mocker.patch('pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog.join',
                                     return_value=mock_join)
    mock_os_realpath = mocker.patch('pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog.realpath',
                                    return_value=mock_realpath)
    mock_accepted_callback = mocker.MagicMock()

    dialog = TerminologyLookupDialog("default", mock_accepted_callback)
    mock_q_dialog_constructor.assert_called_once_with()
    mock_base_setup.assert_called_once_with(mock_dialog)
    mock_get_logger.assert_called_once_with(
      'pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog.TerminologyLookupDialog')
    assert dialog.instance is mock_dialog, "dialog instance should be returned"
    assert dialog.logger is mock_logger, "logger should be set"

    assert mock_os_path_dir_name.call_args.args[0].endswith(
      'pasta_eln/GUI/ontology_configuration/terminology_lookup_dialog.py'), \
      "directory name should contain pasta-eln/src/pasta_eln/GUI/ontology_configuration/terminology_lookup_dialog.py"
    mock_os_path_get_cwd.assert_called_once_with()
    mock_os_path_join.assert_any_call(mock_cd, mock_dir_name)
    mock_os_realpath.assert_called_once_with(mock_join)
    mock_os_path_join.assert_any_call(mock_realpath, "../../Resources/Icons")
    mock_os_path_join.assert_any_call(mock_join, "wikipedia.png")
    mock_os_path_join.assert_any_call(mock_join, "wikidata.png")
    mock_os_path_join.assert_any_call(mock_join, "ols.png")
    mock_os_path_join.assert_any_call(mock_join, "tib.png")
    assert mock_pixmap_constructor.call_count == 4, "pixmap should be created 4 times"
    mock_pixmap_constructor.assert_has_calls(
      [mocker.call(mock_join),
       mocker.call(mock_join),
       mocker.call(mock_join),
       mocker.call(mock_join)])

    assert mock_pixmap_scaled_to_width.call_count == 4, "pixmap should be scaled 4 times"
    mock_pixmap_scaled_to_width.assert_has_calls([
      mocker.call(50),
      mocker.call(50),
      mocker.call(50),
      mocker.call(50)])

    mock_error_console_text_edit_hide.aassert_called_once_with()
    mock_terminology_lookup_service.assert_called_once_with()
    assert dialog.icons_pixmap == {
      "wikipedia": mock_pixmap,
      "wikidata": mock_pixmap,
      "ontology_lookup_service": mock_pixmap,
      "tib_terminology_service": mock_pixmap,
    }, "Icon images should be set"
    mock_accepted_connect.assert_any_call(dialog.set_selected_iris)
    mock_accepted_connect.assert_any_call(mock_accepted_callback)
    dialog.terminologySearchPushButton.clicked.connect.assert_any_call(dialog.terminology_search_button_clicked)
    assert dialog.selected_iris == [], "selected_iris should be initialized to empty list"
    dialog.terminologyLineEdit.setText.assert_called_once_with("default")

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
    mock_entry_cb_constructor = mocker.patch(
      'pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog.QCheckBox', return_value=mock_entry_checkbox)

    mocker.patch.object(QCheckBox, '__init__', return_value=None)
    mocker.patch.object(QLabel, '__init__', return_value=None)
    mock_entry_label_constructor = mocker.patch.object(QLabel, '__new__', return_value=mock_entry_label)
    mock_entry_layout_add_widget = mocker.patch.object(mock_layout, 'addWidget')
    mock_entry_layout_add_stretch = mocker.patch.object(mock_layout, 'addStretch')
    mock_entry_widget_set_layout = mocker.patch.object(mock_entry_widget, 'setLayout')
    mock_cb_set_tool_tip = mocker.patch.object(mock_entry_checkbox, 'setToolTip')

    mocker.patch.object(terminology_lookup_dialog_mock, 'scrollAreaContentsVerticalLayout', mock_scroll_area_layout,
                        create=True)
    mock_scroll_area_layout_add_widget = mocker.patch.object(
      terminology_lookup_dialog_mock.scrollAreaContentsVerticalLayout, 'addWidget')

    assert terminology_lookup_dialog_mock.add_scroll_area_entry(mock_pixmap,
                                                                "Checkbox Text",
                                                                "Checkbox Tooltip") is None, "show should return None"
    mock_entry_layout_constructor.assert_called_once_with()
    mock_entry_widget_constructor.assert_called_once_with()
    mock_entry_layout_add_widget.asser_called_anytime(mock_entry_checkbox)
    mock_entry_label_constructor.assert_called_once_with(QLabel, pixmap=mock_pixmap)
    mock_entry_layout_add_widget.asser_called_anytime(mock_entry_label)
    mock_entry_layout_add_stretch.asser_called_once_with(1)
    mock_entry_widget_set_layout.assert_called_once_with(mock_layout)
    mock_scroll_area_layout_add_widget.assert_called_once_with(mock_entry_widget)
    mock_cb_set_tool_tip.assert_called_once_with("Checkbox Tooltip")
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

  @pytest.mark.parametrize("search_term, results_fixture_name", [
    ('pasta', 'retrieved_iri_results_pasta_mock'),
    ('science', 'retrieved_iri_results_science_mock'),
    ('name', 'retrieved_iri_results_name_mock')
  ])
  def test_search_button_click_with_given_search_term_should_do_as_expected(self,
                                                                            mocker,
                                                                            terminology_lookup_dialog_mock: terminology_lookup_dialog_mock,
                                                                            search_term,
                                                                            results_fixture_name,
                                                                            request):
    retrieved_iri_results = request.getfixturevalue(results_fixture_name) if results_fixture_name else []
    mock_logger_info = mocker.patch.object(terminology_lookup_dialog_mock.logger, 'info')
    mock_reset_ui = mocker.patch.object(terminology_lookup_dialog_mock, 'reset_ui')
    mock_add_scroll_area_entry = mocker.patch.object(terminology_lookup_dialog_mock, 'add_scroll_area_entry')
    mock_bar_set_value = mocker.patch.object(terminology_lookup_dialog_mock.searchProgressBar, 'setValue')
    mock_bar_get_value = mocker.patch.object(terminology_lookup_dialog_mock.searchProgressBar, 'value',
                                             return_value=25)
    mock_terminology_service = mocker.MagicMock()
    mock_terminology_line_edit = mocker.MagicMock()
    mocker.patch.object(terminology_lookup_dialog_mock, 'terminology_lookup_service', mock_terminology_service,
                        create=True)
    mocker.patch.object(terminology_lookup_dialog_mock, 'terminologyLineEdit', mock_terminology_line_edit, create=True)
    mocker.patch.object(mock_terminology_service, 'session_request_errors', None)
    mock_terminology_line_edit_text = mocker.patch.object(mock_terminology_line_edit, 'text', return_value=search_term)

    mock_pixmap = mocker.MagicMock()
    mocker.patch.object(terminology_lookup_dialog_mock, 'icons_pixmap', {
      "wikipedia": mock_pixmap,
      "wikidata": mock_pixmap,
      "ontology_lookup_service": mock_pixmap,
      "tib_terminology_service": mock_pixmap,
    }, create=True)
    mock_do_loop = mocker.MagicMock()
    mocker.patch.object(mock_terminology_service, 'do_lookup', return_value=mock_do_loop)
    mock_event_loop = mocker.MagicMock()
    mock_get_event_loop = mocker.patch('pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog.get_event_loop',
                                       return_value=mock_event_loop)
    mock_run_until_complete = mocker.patch.object(mock_event_loop, 'run_until_complete',
                                                  return_value=retrieved_iri_results)
    assert terminology_lookup_dialog_mock.terminology_search_button_clicked() is None, "show should return None"
    mock_logger_info.assert_called_once_with('Terminology search initiated for term: %s..', search_term)
    mock_terminology_line_edit_text.assert_called_once_with()
    mock_reset_ui.assert_called_once_with()
    mock_bar_set_value.assert_any_call(5)
    mock_get_event_loop.assert_called_once_with()
    mock_run_until_complete.assert_called_once_with(mock_do_loop)
    results_count = 0
    for service in retrieved_iri_results:
      results_count += len(service['results'])
      for result in service['results']:
        mock_add_scroll_area_entry.assert_any_call(mock_pixmap,
                                                   textwrap.fill(result['information'], width=100, max_lines=2),
                                                   result['iri'])
        mock_bar_set_value.assert_any_call((100 - 25) / 2)
    mock_bar_set_value.assert_any_call(100)
    assert mock_bar_set_value.call_count == results_count + 2, f"progress_bar_set_value should be called {results_count + 2} times"
    assert mock_add_scroll_area_entry.call_count == results_count, f"add_scroll_area_entry should be called {results_count} times"
    assert mock_bar_get_value.call_count == results_count, f"progress_bar_get_value should be called {results_count} times"

  @pytest.mark.parametrize("search_term", [None, '', ' ', "        "])
  def test_search_button_click_with_null_search_term_should_warn_user(self,
                                                                      mocker,
                                                                      terminology_lookup_dialog_mock: terminology_lookup_dialog_mock,
                                                                      search_term):
    mock_logger_warning = mocker.patch.object(terminology_lookup_dialog_mock.logger, 'warning')
    mock_reset_ui = mocker.patch.object(terminology_lookup_dialog_mock, 'reset_ui')
    mock_terminology_line_edit = mocker.MagicMock()
    mocker.patch.object(terminology_lookup_dialog_mock, 'terminologyLineEdit', mock_terminology_line_edit, create=True)
    mock_instance = mocker.MagicMock()
    mocker.patch.object(terminology_lookup_dialog_mock, 'instance', mock_instance, create=True)
    mock_terminology_line_edit_text = mocker.patch.object(mock_terminology_line_edit, 'text', return_value=search_term)
    mock_warning = mocker.patch('pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog.QMessageBox.warning')
    assert terminology_lookup_dialog_mock.terminology_search_button_clicked() is None, "show should return None"
    mock_logger_warning.assert_called_once_with("Enter non null search term!")
    mock_terminology_line_edit_text.assert_called_once_with()
    mock_reset_ui.assert_called_once_with()
    mock_warning.assert_called_once_with(mock_instance, "Error", "Enter non null search term!")

  def test_search_button_click_with_lookup_error_should_log_errors(self,
                                                                   mocker,
                                                                   terminology_lookup_dialog_mock: terminology_lookup_dialog_mock):
    mock_logger_info = mocker.patch.object(terminology_lookup_dialog_mock.logger, 'info')
    mock_reset_ui = mocker.patch.object(terminology_lookup_dialog_mock, 'reset_ui')
    mock_bar_set_value = mocker.patch.object(terminology_lookup_dialog_mock.searchProgressBar, 'setValue')
    mock_bar_get_value = mocker.patch.object(terminology_lookup_dialog_mock.searchProgressBar, 'value',
                                             return_value=25)
    mock_terminology_service = mocker.MagicMock()
    mock_terminology_line_edit = mocker.MagicMock()
    mocker.patch.object(terminology_lookup_dialog_mock, 'terminology_lookup_service', mock_terminology_service,
                        create=True)
    mocker.patch.object(terminology_lookup_dialog_mock, 'terminologyLineEdit', mock_terminology_line_edit, create=True)
    mocker.patch.object(mock_terminology_service, 'session_request_errors', None)
    mock_terminology_line_edit_text = mocker.patch.object(mock_terminology_line_edit, 'text',
                                                          return_value="search_term")

    mock_do_loop = mocker.MagicMock()
    mocker.patch.object(mock_terminology_service, 'do_lookup', return_value=mock_do_loop)
    mocker.patch.object(mock_terminology_service, 'session_request_errors', ["error1", "error2", "error3", "error4"])
    mock_event_loop = mocker.MagicMock()
    mock_get_event_loop = mocker.patch('pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog.get_event_loop',
                                       return_value=mock_event_loop)
    mock_run_until_complete = mocker.patch.object(mock_event_loop, 'run_until_complete',
                                                  return_value={})
    mock_clear_error_console_set_text = mocker.patch.object(terminology_lookup_dialog_mock.errorConsoleTextEdit,
                                                            'setText')
    mock_clear_error_console_set_visible = mocker.patch.object(terminology_lookup_dialog_mock.errorConsoleTextEdit,
                                                               'setVisible')
    assert terminology_lookup_dialog_mock.terminology_search_button_clicked() is None, "show should return None"
    mock_logger_info.assert_called_once_with('Terminology search initiated for term: %s..', "search_term")
    mock_terminology_line_edit_text.assert_called_once_with()
    mock_reset_ui.assert_called_once_with()
    mock_bar_set_value.assert_any_call(5)
    mock_get_event_loop.assert_called_once_with()
    mock_run_until_complete.assert_called_once_with(mock_do_loop)
    mock_bar_set_value.assert_any_call(100)
    mock_clear_error_console_set_text.assert_called_once_with('\n'.join(["error1", "error2", "error3", "error4"]))
    mock_clear_error_console_set_visible.assert_called_once_with(True)
    assert mock_bar_set_value.call_count == 2, f"progress_bar_set_value should be called {2} times"
    assert mock_bar_get_value.call_count == 0, f"progress_bar_get_value should be called {0} times"

  def test_reset_ui_should_do_as_expected(self,
                                          mocker,
                                          terminology_lookup_dialog_mock: terminology_lookup_dialog_mock):
    mock_logger_info = mocker.patch.object(terminology_lookup_dialog_mock.logger, 'info')
    mock_clear_scroll_area = mocker.patch.object(terminology_lookup_dialog_mock, 'clear_scroll_area')
    mock_clear_error_console_clear = mocker.patch.object(terminology_lookup_dialog_mock.errorConsoleTextEdit, 'clear')
    mocker.patch.object(terminology_lookup_dialog_mock, 'selected_iris')
    mock_clear_selected_iris_clear = mocker.patch.object(terminology_lookup_dialog_mock.selected_iris, 'clear')
    mock_clear_error_console_set_visible = mocker.patch.object(terminology_lookup_dialog_mock.errorConsoleTextEdit,
                                                               'setVisible')
    mock_clear_bar_set_value = mocker.patch.object(terminology_lookup_dialog_mock.searchProgressBar, 'setValue')

    assert terminology_lookup_dialog_mock.reset_ui() is None, "reset_ui should return None"
    mock_logger_info.assert_called_once_with("Resetting UI..")
    mock_clear_bar_set_value.assert_called_once_with(0)
    mock_clear_scroll_area.assert_called_once_with()
    mock_clear_error_console_clear.assert_called_once_with()
    mock_clear_error_console_set_visible.assert_called_once_with(False)
    mock_clear_selected_iris_clear.assert_called_once_with()

  def test_set_selected_iris_should_do_as_expected(self,
                                                   mocker,
                                                   terminology_lookup_dialog_mock: terminology_lookup_dialog_mock):
    mock_logger_info = mocker.patch.object(terminology_lookup_dialog_mock.logger, 'info')
    mocker.patch.object(Ui_TerminologyLookupDialogBase, 'scrollAreaContentsVerticalLayout', create=True)
    mocker.patch.object(terminology_lookup_dialog_mock.scrollAreaContentsVerticalLayout, 'count', return_value=2)
    mock_range = mocker.patch('pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog.range',
                              return_value=[0, 1])
    mocker.patch.object(terminology_lookup_dialog_mock, 'selected_iris')
    mock_widgets = [mocker.MagicMock(), mocker.MagicMock()]
    mock_checkboxes = [mocker.MagicMock(), mocker.MagicMock()]
    mock_urls = ['url1', 'url2']
    mocker.patch.object(terminology_lookup_dialog_mock.scrollAreaContentsVerticalLayout, 'count', return_value=2)
    mocker.patch.object(mock_widgets[0], 'widget', return_value=mock_widgets[0])
    mocker.patch.object(mock_widgets[0], 'findChildren', return_value=[mock_checkboxes[0]])
    mocker.patch.object(mock_checkboxes[0], 'isChecked', return_value=True)
    mocker.patch.object(mock_checkboxes[0], 'toolTip', return_value=mock_urls[0])
    mocker.patch.object(mock_widgets[1], 'widget', return_value=mock_widgets[1])
    mocker.patch.object(mock_widgets[1], 'findChildren', return_value=[mock_checkboxes[1]])
    mocker.patch.object(mock_checkboxes[1], 'isChecked', return_value=True)
    mocker.patch.object(mock_checkboxes[1], 'toolTip', return_value=mock_urls[0])

    mocker.patch.object(terminology_lookup_dialog_mock.scrollAreaContentsVerticalLayout, 'itemAt',
                        lambda x: mock_widgets[x])

    assert terminology_lookup_dialog_mock.set_selected_iris() is None, "set_selected_iris should return None"
    mock_logger_info.assert_called_once_with("Set IRIs: %s", terminology_lookup_dialog_mock.selected_iris)
    mock_range.assert_called_once_with(2)
    mock_widgets[0].widget.assert_called_once_with()
    mock_widgets[1].widget.assert_called_once_with()
    mock_widgets[0].findChildren.assert_called_once_with(QCheckBox)
    mock_widgets[1].findChildren.assert_called_once_with(QCheckBox)
    mock_checkboxes[0].isChecked.assert_called_once_with()
    mock_checkboxes[0].toolTip.assert_called_once_with()
    mock_checkboxes[1].isChecked.assert_called_once_with()
    mock_checkboxes[1].toolTip.assert_called_once_with()
    terminology_lookup_dialog_mock.selected_iris.clear.assert_called_once_with()
