#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_create_type_dialog_extended.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest
from PySide6.QtCore import Qt

from tests.app_tests.common.fixtures import create_type_dialog_mock


class TestOntologyConfigCreateTypeDialog(object):

  @pytest.mark.parametrize("checked, next_level", [
    (True, "x0"),
    (False, "x1")
  ])
  def test_structural_level_checkbox_callback_should_do_expected(self,
                                                                 mocker,
                                                                 create_type_dialog_mock,
                                                                 checked,
                                                                 next_level):
    mock_check_box = mocker.patch('PySide6.QtWidgets.QCheckBox')
    mock_line_edit = mocker.patch('PySide6.QtWidgets.QLineEdit')
    mocker.patch.object(mock_check_box, 'isChecked', return_value=checked)
    mocker.patch.object(create_type_dialog_mock, 'structuralLevelCheckBox', mock_check_box, create=True)
    mocker.patch.object(create_type_dialog_mock, 'titleLineEdit', mock_line_edit, create=True)
    mocker.patch.object(create_type_dialog_mock, 'next_struct_level', next_level, create=True)
    set_text_line_edit_spy = mocker.spy(mock_line_edit, 'setText')
    set_disabled_line_edit_spy = mocker.spy(mock_line_edit, 'setDisabled')
    clear_line_edit_spy = mocker.spy(mock_line_edit, 'clear')
    assert create_type_dialog_mock.structural_level_checkbox_callback() is None, "create_type_dialog_mock.structural_level_checkbox_callback() should return None"
    if checked:
      set_text_line_edit_spy.assert_called_once_with(next_level)
      set_disabled_line_edit_spy.assert_called_once_with(True)
    else:
      clear_line_edit_spy.assert_called_once_with()
      set_disabled_line_edit_spy.assert_called_once_with(False)

  def test_show_callback_should_do_expected(self,
                                            mocker,
                                            create_type_dialog_mock):
    set_window_modality_spy = mocker.spy(create_type_dialog_mock.instance, 'setWindowModality')
    show_spy = mocker.spy(create_type_dialog_mock.instance, 'show')
    assert create_type_dialog_mock.show() is None, "create_type_dialog_mock.show() should return None"
    set_window_modality_spy.assert_called_once_with(Qt.ApplicationModal)
    assert show_spy.call_count == 1, "show() should be called once"

  def test_clear_ui_callback_should_do_expected(self,
                                                mocker,
                                                create_type_dialog_mock):
    mock_check_box = mocker.patch('PySide6.QtWidgets.QCheckBox')
    mock_title_line_edit = mocker.patch('PySide6.QtWidgets.QLineEdit')
    mock_label_line_edit = mocker.patch('PySide6.QtWidgets.QLineEdit')
    mocker.patch.object(create_type_dialog_mock, 'structuralLevelCheckBox', mock_check_box, create=True)
    mocker.patch.object(create_type_dialog_mock, 'titleLineEdit', mock_title_line_edit, create=True)
    mocker.patch.object(create_type_dialog_mock, 'labelLineEdit', mock_label_line_edit, create=True)
    title_line_edit_clear_spy = mocker.spy(mock_title_line_edit, 'clear')
    label_line_edit_clear_spy = mocker.spy(mock_label_line_edit, 'clear')
    check_box_set_checked_spy = mocker.spy(mock_check_box, 'setChecked')
    assert create_type_dialog_mock.clear_ui() is None, "create_type_dialog_mock.clear_ui() should return None"
    assert title_line_edit_clear_spy.call_count == 1, "titleLineEdit.clear() should be called once"
    assert label_line_edit_clear_spy.call_count == 1, "labelLineEdit.clear() should be called once"
    check_box_set_checked_spy.assert_called_once_with(False)

  @pytest.mark.parametrize("next_level", [
    "x0",
    "x1"
  ])
  def test_set_structural_level_title_should_do_expected(self,
                                                         mocker,
                                                         create_type_dialog_mock,
                                                         next_level):
    next_set = None
    mocker.patch.object(create_type_dialog_mock, 'next_struct_level', next_set, create=True)
    logger_info_spy = mocker.spy(create_type_dialog_mock.logger, 'info')
    assert create_type_dialog_mock.set_structural_level_title(
      next_level) is None, "set_structural_level_title() should return None"
    logger_info_spy.assert_called_once_with("Next structural level set: {%s}...", next_level)
    assert create_type_dialog_mock.next_struct_level == next_level, "next_struct_level should be set to next_level"
