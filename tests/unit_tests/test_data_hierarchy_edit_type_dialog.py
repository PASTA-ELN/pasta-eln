#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_edit_type_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QMessageBox

from pasta_eln.GUI.data_hierarchy.edit_type_dialog import EditTypeDialog


@pytest.fixture
def patch_dependencies(mocker):
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.logging.getLogger')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.iconFontCollectionComboBox', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.iconComboBox', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.typeDisplayedTitleLineEdit', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.typeLineEdit', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.iriLineEdit', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.shortcutLineEdit', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.buttonBox', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QDialog')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.LookupIriAction')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.show_message')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QTAIconsFactory',
               MagicMock(font_collections=['Font1', 'Font2']))
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog_base.Ui_TypeDialogBase.setupUi')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.DataTypeInfo')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QRegularExpression')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QRegularExpressionValidator')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QTAIconsFactory',
               MagicMock(font_collections=['Font1', 'Font2']))


@pytest.fixture
def edit_type_dialog(patch_dependencies):
  return EditTypeDialog(MagicMock(), MagicMock())


class TestDataHierarchyEditTypeDialog:
  @pytest.mark.parametrize(
    "accepted_callback, rejected_callback, expected_title, expected_tooltip",
    [
      # Happy path test case
      pytest.param(
        MagicMock(), MagicMock(), "Edit existing type", "Changing type title disabled for edits!",
        id="success_path"
      ),
      # Edge case: Empty callbacks
      pytest.param(
        None, None, "Edit existing type", "Changing type title disabled for edits!",
        id="empty_callbacks"
      ),
      # Edge case: Callbacks with side effects
      pytest.param(
        lambda: print("Accepted"), lambda: print("Rejected"), "Edit existing type",
        "Changing type title disabled for edits!",
        id="callbacks_with_side_effects"
      ),
    ]
  )
  def test_edit_type_dialog_initialization(self, patch_dependencies, accepted_callback, rejected_callback,
                                           expected_title, expected_tooltip):
    # Act
    dialog = EditTypeDialog(accepted_callback, rejected_callback)

    # Assert
    assert dialog.selected_data_hierarchy_type == {}
    assert dialog.selected_data_hierarchy_type_name == ""
    dialog.instance.setWindowTitle.assert_called_once_with("Edit existing type")
    dialog.typeLineEdit.setDisabled.assert_called_once_with(True)
    dialog.typeLineEdit.setToolTip.assert_called_once_with("Changing type title disabled for edits!")
    dialog.typeDisplayedTitleLineEdit.toolTip.return_value.replace.assert_called_once_with("Enter", "Modify")
    dialog.typeDisplayedTitleLineEdit.setToolTip.assert_called_once_with(
      dialog.typeDisplayedTitleLineEdit.toolTip.return_value.replace.return_value)
    dialog.iriLineEdit.toolTip.return_value.replace.assert_called_once_with("Enter", "Modify")
    dialog.iriLineEdit.setToolTip.assert_called_once_with(dialog.iriLineEdit.toolTip.return_value.replace.return_value)
    dialog.shortcutLineEdit.toolTip.return_value.replace.assert_called_once_with("Enter", "Modify")
    dialog.shortcutLineEdit.setToolTip.assert_called_once_with(
      dialog.shortcutLineEdit.toolTip.return_value.replace.return_value)
    dialog.iconComboBox.currentIndexChanged[int].connect.assert_any_call(dialog.set_icon)
    dialog.typeLineEdit.textChanged[str].connect.assert_any_call(dialog.type_changed)

  @pytest.mark.parametrize(
    "selected_data_hierarchy_type, expected_type, expected_iri, expected_title, expected_shortcut, expected_icon_font, expected_icon",
    [
      # Happy path test cases
      pytest.param(
        {"IRI": "http://example.com/iri", "title": "Example Title", "shortcut": "Ex", "icon": "icon.png"},
        "Example Type", "http://example.com/iri", "Example Title", "Ex", "icon", "icon.png",
        id="success_path_with_icon"
      ),
      pytest.param(
        {"IRI": "http://example.com/iri", "title": "Example Title", "shortcut": "Ex", "icon": ""},
        "Example Type", "http://example.com/iri", "Example Title", "Ex", "", "No value",
        id="success_path_no_icon"
      ),
      # Edge case test cases
      pytest.param(
        {"IRI": "", "title": "", "shortcut": "", "icon": ""},
        "Empty Type", "", "", "", "", "No value",
        id="edge_case_empty_values"
      ),
      # Error case test cases
      pytest.param(
        {"IRI": None, "title": None, "shortcut": None, "icon": None},
        "None Type", "", "", "", "", "No value",
        id="error_case_none_values"
      ),
    ]
  )
  def test_show_v1(self, edit_type_dialog, selected_data_hierarchy_type, expected_type, expected_iri, expected_title,
                   expected_shortcut, expected_icon_font, expected_icon):
    # Arrange
    edit_type_dialog.selected_data_hierarchy_type_name = expected_type
    edit_type_dialog.selected_data_hierarchy_type = selected_data_hierarchy_type

    # Act
    edit_type_dialog.show()

    # Assert
    edit_type_dialog.typeLineEdit.setText.assert_called_once_with(expected_type)
    edit_type_dialog.iriLineEdit.setText.assert_called_once_with(expected_iri)
    edit_type_dialog.typeDisplayedTitleLineEdit.setText.assert_called_once_with(expected_title)
    edit_type_dialog.shortcutLineEdit.setText.assert_called_once_with(expected_shortcut)
    edit_type_dialog.iconFontCollectionComboBox.setCurrentText.assert_called_once_with(expected_icon_font)
    edit_type_dialog.iconComboBox.setCurrentText.assert_called_once_with(expected_icon)

  @pytest.mark.parametrize("test_input", [
    # Happy path with all fields provided
    pytest.param(
      {
        "selected_data_hierarchy_type_name": "Type A",
        "selected_data_hierarchy_type": {
          "IRI": "http://example.com/typeA",
          "title": "Type A Title",
          "shortcut": "TA",
          "icon": "iconA.png"
        }
      },
      id="happy_path_all_fields"
    ),
    # Edge case with missing IRI
    pytest.param(
      {
        "selected_data_hierarchy_type_name": "Type B",
        "selected_data_hierarchy_type": {
          "IRI": None,
          "title": "Type B Title",
          "shortcut": "TB",
          "icon": "iconB.png"
        }
      },
      id="edge_case_missing_IRI"
    ),
    # Edge case with missing title
    pytest.param(
      {
        "selected_data_hierarchy_type_name": "Type C",
        "selected_data_hierarchy_type": {
          "IRI": "http://example.com/typeC",
          "title": None,
          "shortcut": "TC",
          "icon": "iconC.png"
        }
      },
      id="edge_case_missing_title"
    ),
    # Edge case with missing shortcut
    pytest.param(
      {
        "selected_data_hierarchy_type_name": "Type D",
        "selected_data_hierarchy_type": {
          "IRI": "http://example.com/typeD",
          "title": "Type D Title",
          "shortcut": None,
          "icon": "iconD.png"
        }
      },
      id="edge_case_missing_shortcut"
    ),
    # Edge case with missing icon
    pytest.param(
      {
        "selected_data_hierarchy_type_name": "Type E",
        "selected_data_hierarchy_type": {
          "IRI": "http://example.com/typeE",
          "title": "Type E Title",
          "shortcut": "TE",
          "icon": None
        }
      },
      id="edge_case_missing_icon"
    ),
    # Error case with invalid data type
    pytest.param(
      {
        "selected_data_hierarchy_type_name": "Type F",
        "selected_data_hierarchy_type": None
      },
      id="error_case_invalid_data_type"
    ),
  ])
  def test_show_v2(self, mocker, edit_type_dialog, test_input):
    # Arrange
    mocker.resetall()
    edit_type_dialog.selected_data_hierarchy_type_name = test_input["selected_data_hierarchy_type_name"]
    edit_type_dialog.selected_data_hierarchy_type = test_input["selected_data_hierarchy_type"]

    # Act
    edit_type_dialog.show()

    # Assert
    if edit_type_dialog.selected_data_hierarchy_type is None:
      edit_type_dialog.logger.warning.assert_called_once_with(
        "Invalid data type: {%s}", edit_type_dialog.selected_data_hierarchy_type)
    else:
      edit_type_dialog.typeLineEdit.setText.assert_called_once_with(
        edit_type_dialog.selected_data_hierarchy_type_name)
      edit_type_dialog.iriLineEdit.setText.assert_called_once_with(
        edit_type_dialog.selected_data_hierarchy_type["IRI"] or "")
      edit_type_dialog.typeDisplayedTitleLineEdit.setText.assert_called_once_with(
        edit_type_dialog.selected_data_hierarchy_type["title"] or "")
      edit_type_dialog.shortcutLineEdit.setText.assert_called_once_with(
        edit_type_dialog.selected_data_hierarchy_type["shortcut"] or "")
      edit_type_dialog.iconFontCollectionComboBox.setCurrentText.assert_called_once_with(
        edit_type_dialog.selected_data_hierarchy_type["icon"].split(".")[0] if
        edit_type_dialog.selected_data_hierarchy_type[
          "icon"] else "")
      edit_type_dialog.iconComboBox.setCurrentText.assert_called_once_with(
        edit_type_dialog.selected_data_hierarchy_type["icon"] or "No value")

  @pytest.mark.parametrize(
    "validate_type_info, selected_data_hierarchy_type, expected_log, expected_message, test_id",
    [
      # Happy path
      (True, {"key": "value"},
       "User updated the existing type: Datatype: {test_datatype}, Displayed Title: {test_title}", None,
       "success_path"),

      # Edge case: No selected_data_hierarchy_type
      (True, None, None,
       "Error update scenario: Type (datatype: test_datatype displayed title: test_title) does not exists!!....",
       "no_selected_type"),

      # Error case: Validation fails
      (False, {"key": "value"}, None, None, "validation_fails"),
    ],
    ids=["success_path", "no_selected_type", "validation_fails"]
  )
  def test_accepted_callback(self, edit_type_dialog, validate_type_info, selected_data_hierarchy_type, expected_log,
                             expected_message, test_id):
    # Arrange
    edit_type_dialog.type_info = MagicMock(datatype="test_datatype", title="test_title")
    edit_type_dialog.validate_type_info = MagicMock()
    edit_type_dialog.validate_type_info.return_value = validate_type_info
    if selected_data_hierarchy_type:
      edit_type_dialog.selected_data_hierarchy_type = MagicMock()
      edit_type_dialog.selected_data_hierarchy_type.__getitem__.side_effect = selected_data_hierarchy_type.__getitem__
    else:
      edit_type_dialog.selected_data_hierarchy_type = None

    with patch('pasta_eln.GUI.data_hierarchy.edit_type_dialog.show_message') as mock_show_message, \
        patch('pasta_eln.GUI.data_hierarchy.edit_type_dialog.generate_data_hierarchy_type',
              return_value={"key": "updated_value"}) as mock_generate_data_hierarchy_type:
      # Act
      edit_type_dialog.accepted_callback()

      # Assert
      if expected_log:
        edit_type_dialog.logger.info.assert_called_once_with(
          "User updated the existing type: Datatype: {%s}, Displayed Title: {%s}",
          edit_type_dialog.type_info.datatype,
          edit_type_dialog.type_info.title
        )
        mock_generate_data_hierarchy_type.assert_called_once_with(edit_type_dialog.type_info)
        edit_type_dialog.selected_data_hierarchy_type.update.assert_called_once_with({"key": "updated_value"})
        edit_type_dialog.instance.close.assert_called_once()
        edit_type_dialog.accepted_callback_parent.assert_called_once()
      else:
        edit_type_dialog.logger.info.assert_not_called()
        mock_generate_data_hierarchy_type.assert_not_called()
        if selected_data_hierarchy_type:
          edit_type_dialog.selected_data_hierarchy_type.update.assert_not_called()
        edit_type_dialog.instance.close.assert_not_called()
        edit_type_dialog.accepted_callback_parent.assert_not_called()

      if expected_message:
        mock_show_message.assert_called_once_with(
          expected_message,
          QMessageBox.Icon.Warning
        )
      else:
        mock_show_message.assert_not_called()

  @pytest.mark.parametrize(
    "new_index, current_text, expected_warning, expected_icon_call",
    [
      # Happy path tests
      (1, "icon1", None, True),  # valid index and icon name
      (2, "icon2", None, True),  # another valid index and icon name

      # Edge cases
      (0, "icon3", None, True),  # boundary index value
      (1, "No value", None, False),  # valid index but "No value" as icon name

      # Error cases
      (-1, "icon4", "Invalid index: {%s}", False),  # negative index
      (-10, "icon5", "Invalid index: {%s}", False),  # another negative index
    ],
    ids=[
      "valid_index_icon1",
      "valid_index_icon2",
      "boundary_index_icon3",
      "valid_index_no_value",
      "negative_index_icon4",
      "negative_index_icon5",
    ]
  )
  def test_set_icon(self, mocker, edit_type_dialog, new_index, current_text, expected_warning, expected_icon_call):
    # Arrange
    mocker.resetall()
    mock_icon = mocker.patch('pasta_eln.GUI.data_hierarchy.edit_type_dialog.qta.icon')
    edit_type_dialog.iconComboBox.currentText.return_value = current_text

    # Act
    edit_type_dialog.set_icon(new_index)

    # Assert
    if expected_warning:
      edit_type_dialog.logger.warning.assert_called_once_with(expected_warning, new_index)
    else:
      edit_type_dialog.logger.warning.assert_not_called()

    if expected_icon_call:
      mock_icon.assert_called_once_with(current_text)
      edit_type_dialog.iconComboBox.setItemIcon.assert_called_once_with(new_index, mock_icon.return_value)
    else:
      edit_type_dialog.iconComboBox.setItemIcon.assert_not_called()

  @pytest.mark.parametrize(
    "new_data_type, expected_disabled, log_warning_called, test_id",
    [
      ("x0", True, False, "disable_structural_x0"),
      ("x1", True, False, "disable_structural_x1"),
      ("x2", False, False, "enable_non_structural_x2"),
      ("", False, True, "empty_data_type"),
      (None, False, True, "none_data_type"),
    ],
    ids=[
      "disable_structural_x0",
      "disable_structural_x1",
      "enable_non_structural_x2",
      "empty_data_type",
      "none_data_type",
    ]
  )
  def test_type_changed(self, mocker, edit_type_dialog, new_data_type, expected_disabled, log_warning_called, test_id):
    # Arrange
    mocker.resetall()
    # Act
    edit_type_dialog.type_changed(new_data_type)

    # Assert
    assert edit_type_dialog.logger.warning.called == log_warning_called
    if log_warning_called:
      edit_type_dialog.logger.warning.assert_called_with("Invalid data type: {%s}", new_data_type)
      edit_type_dialog.shortcutLineEdit.setDisabled.assert_not_called()
      edit_type_dialog.iconComboBox.setDisabled.assert_not_called()
      edit_type_dialog.iconFontCollectionComboBox.setDisabled.assert_not_called()
    else:
      edit_type_dialog.shortcutLineEdit.setDisabled.assert_called_with(expected_disabled)
      edit_type_dialog.iconComboBox.setDisabled.assert_called_with(expected_disabled)
      edit_type_dialog.iconFontCollectionComboBox.setDisabled.assert_called_with(expected_disabled)

  @pytest.mark.parametrize(
    "data_hierarchy_type, expected, test_id",
    [
      # Happy path tests
      ({"type": "folder", "description": "A folder type"}, {"type": "folder", "description": "A folder type"},
       "success_path_folder"),
      ({"type": "file", "description": "A file type"}, {"type": "file", "description": "A file type"},
       "success_path_file"),

      # Edge cases
      ({}, {}, "empty_dict"),
      ({"type": None}, {"type": None}, "none_type"),
      ({"type": "folder", "extra": "unexpected"}, {"type": "folder", "extra": "unexpected"}, "extra_key"),

      # Error cases
      (None, None, "none_input"),
      ("not_a_dict", "not_a_dict", "string_input"),
      (123, 123, "integer_input"),
    ],
    ids=[
      "success_path_folder",
      "success_path_file",
      "empty_dict",
      "none_type",
      "extra_key",
      "none_input",
      "string_input",
      "integer_input",
    ]
  )
  def test_set_selected_data_hierarchy_type(self, edit_type_dialog, data_hierarchy_type, expected, test_id):
    # Act
    edit_type_dialog.set_selected_data_hierarchy_type(data_hierarchy_type)

    # Assert
    assert edit_type_dialog.selected_data_hierarchy_type == expected

  @pytest.mark.parametrize(
    "datatype, expected, test_id",
    [
      ("TypeA", "TypeA", "success_path_type_a"),
      ("TypeB", "TypeB", "success_path_type_b"),
      ("", "", "edge_case_empty_string"),
      (None, None, "edge_case_none"),
      (123, 123, "edge_case_integer"),
      ([], [], "edge_case_empty_list"),
      (["TypeC"], ["TypeC"], "edge_case_list_with_one_element"),
    ],
    ids=[
      "success_path_type_a",
      "success_path_type_b",
      "edge_case_empty_string",
      "edge_case_none",
      "edge_case_integer",
      "edge_case_empty_list",
      "edge_case_list_with_one_element",
    ]
  )
  def test_set_selected_data_hierarchy_type_name(self, edit_type_dialog, datatype, expected, test_id):

    # Act
    edit_type_dialog.set_selected_data_hierarchy_type_name(datatype)

    # Assert
    assert edit_type_dialog.selected_data_hierarchy_type_name == expected
