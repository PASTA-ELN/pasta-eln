#   PASTA-ELN and all its sub-parts are covered by the MIT license.
#  #
#   Copyright (c) 2023
#  #
#   Author: Jithu Murugan
#   Filename: test_data_hierarchy_editor_dialog.py
#  #
#   You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QCheckBox, QMessageBox
from pytestqt.qtbot import QtBot

from pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog import DataHierarchyEditorDialog
from pasta_eln.GUI.data_hierarchy.lookup_iri_action import LookupIriAction
from pasta_eln.GUI.data_hierarchy.utility_functions import adapt_type, get_types_for_display
from tests.app_tests.common.fixtures import attachments_column_names, data_hierarchy_doc_mock, \
  data_hierarchy_editor_gui, metadata_column_names, pasta_db_mock


class TestDataHierarchyEditorDialog(object):

  def test_component_launch_should_display_all_ui_elements(self,
                                                           pasta_db_mock: pasta_db_mock,
                                                           # Added to import fixture by other tests
                                                           data_hierarchy_editor_gui: tuple[
                                                             QApplication,
                                                             QtWidgets.QDialog,
                                                             DataHierarchyEditorDialog,
                                                             QtBot]):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.headerLabel is not None, "Header not loaded!"
    assert ui_form.typeLabel is not None, "Data type label not loaded!"
    assert ui_form.saveDataHierarchyPushButton is not None, "Save button not loaded!"
    assert ui_form.helpPushButton is not None, "Help button not loaded!"
    assert ui_form.typeMetadataTableView is not None, "metadata table view not loaded!"
    assert ui_form.typeAttachmentsTableView is not None, "Type table view not loaded!"
    assert ui_form.addAttachmentPushButton is not None, "Add attachment button not loaded!"
    assert ui_form.addTypePushButton is not None, "Add type button not loaded!"
    assert ui_form.addMetadataRowPushButton is not None, "Add metadata row button not loaded!"
    assert ui_form.addMetadataGroupPushButton is not None, "Add metadata Group button not loaded!"
    assert ui_form.cancelPushButton is not None, "Cancel button not loaded!"
    assert ui_form.typeDisplayedTitleLineEdit is not None, "Data type line edit not loaded!"
    assert ui_form.typeIriLineEdit is not None, "Data type IRI line edit not loaded!"
    assert ui_form.addMetadataGroupLineEdit is not None, "metadata Group line edit not loaded!"
    assert ui_form.typeComboBox is not None, "Data type combo box not loaded!"
    assert ui_form.metadataGroupComboBox is not None, "metadata Group combo box not loaded!"
    assert ui_form.typeAttachmentsTableView.isHidden() is True, "Type attachments table view should not be shown!"
    assert ui_form.addAttachmentPushButton.isHidden() is True, "addAttachmentPushButton should not be shown!"

  @pytest.mark.parametrize(
    "type_to_select, metadata_group_selected, metadata", [
      ('Structure level 0', 'default', ['-name', 'status', 'objective', '-tags', 'comment']),
      ('Structure level 1', 'default', ['-name', '-tags', 'comment']),
      ('Structure level 2', 'default', ['-name', '-tags', 'comment']),
      ('measurement', 'default', ['-name', '-tags', 'comment', '-type', 'image', '#_curated', 'sample', 'procedure']),
      ('sample', 'default', ['-name', 'chemistry', '-tags', 'comment', 'qrCode']),
      ('procedure', 'default', ['-name', '-tags', 'comment', 'content']),
      ('instrument', 'default', ['-name', '-tags', 'comment', 'vendor'])
    ])
  def test_type_select_should_load_data_and_update_ui_elements(self,
                                                               data_hierarchy_editor_gui: tuple[
                                                                 QApplication,
                                                                 QtWidgets.QDialog,
                                                                 DataHierarchyEditorDialog,
                                                                 QtBot],
                                                               type_to_select: str,
                                                               metadata_group_selected: str,
                                                               metadata: list):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    ui_form.typeComboBox.setCurrentText(type_to_select)
    assert ui_form.typeComboBox.currentText() == type_to_select, "Type combo box not selected!"
    assert ui_form.metadataGroupComboBox.currentText() == metadata_group_selected, "Metadata group combo box not selected!"
    selected_metadata = []
    model = ui_form.typeMetadataTableView.model()
    for i in range(model.rowCount()):
      selected_metadata.append(model.data(model.index(i, 0), Qt.DisplayRole))
    assert metadata == selected_metadata, "Selected metadata not as expected!"

  def test_component_launch_should_load_data_hierarchy_data(self,
                                                            data_hierarchy_editor_gui: tuple[
                                                              QApplication,
                                                              QtWidgets.QDialog,
                                                              DataHierarchyEditorDialog,
                                                              QtBot],
                                                            data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                            metadata_column_names: metadata_column_names,
                                                            attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ([ui_form.typeComboBox.itemText(i) for i in range(ui_form.typeComboBox.count())]
            == get_types_for_display(data_hierarchy_doc_mock.types_list())), "Type combo box not loaded!"
    assert (adapt_type(ui_form.typeComboBox.currentText())
            == data_hierarchy_doc_mock.types_list()[0]), "Type combo box should be selected to first item"
    selected_type = data_hierarchy_doc_mock.types()[adapt_type(ui_form.typeComboBox.currentText())]
    assert (ui_form.typeDisplayedTitleLineEdit.text() ==
            selected_type["title"]), "Data type displayedTitle line edit not loaded!"
    assert (ui_form.typeIriLineEdit.text() ==
            selected_type["IRI"]), "Data type IRI line edit not loaded!"

    categories = list(selected_type["meta"].keys())
    assert ([ui_form.metadataGroupComboBox.itemText(i) for i in range(ui_form.metadataGroupComboBox.count())]
            == categories), "metadataGroupComboBox not loaded!"
    assert (ui_form.metadataGroupComboBox.currentText()
            == categories[0]), "metadataGroupComboBox should be selected to first item"
    self.check_table_contents(attachments_column_names, metadata_column_names, selected_type, ui_form)

  @staticmethod
  def check_table_view_model(model, column_names, data_selected):
    for row in range(model.rowCount()):
      data = data_selected[row]
      for column in range(model.columnCount() - 2):
        index = model.index(row, column)
        if column_names[column] in data:
          cell_data = data[column_names[column]]
          assert (model.data(index, Qt.DisplayRole)
                  == ','.join(cell_data) if isinstance(cell_data, list) else cell_data), \
            f"{column_names[column]} not loaded!"
        else:
          assert model.data(index, Qt.DisplayRole) is None, f"{column_names[column]} should be None!"

  def check_table_contents(self, attachments_column_names, metadata_column_names, selected_type, ui_form):
    categories = list(selected_type["meta"].keys())
    # Assert if the metadata loaded in the table view
    model = ui_form.typeMetadataTableView.model()
    self.check_table_view_model(model, metadata_column_names, selected_type["meta"][categories[0]])
    # Assert if the attachments are loaded in the table view
    model = ui_form.typeAttachmentsTableView.model()
    self.check_table_view_model(model, attachments_column_names, selected_type["attachments"])

  def test_component_add_new_type_with_loaded_data_hierarchy_should_display_create_new_type_window(self,
                                                                                                   data_hierarchy_editor_gui:
                                                                                                   tuple[
                                                                                                     QApplication,
                                                                                                     QtWidgets.QDialog,
                                                                                                     DataHierarchyEditorDialog,
                                                                                                     QtBot],
                                                                                                   data_hierarchy_doc_mock: data_hierarchy_doc_mock):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog not shown!"

  def test_component_delete_new_type_without_data_hierarchy_loaded_should_show_error_message(self,
                                                                                             data_hierarchy_editor_gui:
                                                                                             tuple[
                                                                                               QApplication,
                                                                                               QtWidgets.QDialog,
                                                                                               DataHierarchyEditorDialog,
                                                                                               QtBot],
                                                                                             data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                                                             mocker):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    mock_show_message = mocker.patch(
      "pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.show_message")
    mocker.patch.object(ui_form, "data_hierarchy_loaded", False)
    # Select a non-structural type in the type combo box, in order to enable the delete button
    ui_form.typeComboBox.setCurrentText("measurement")
    assert ui_form.typeComboBox.currentText() == "measurement", "Data type combo box should be selected to measurement"
    qtbot.mouseClick(ui_form.deleteTypePushButton, Qt.LeftButton)
    mock_show_message.assert_called_once_with("Load the data hierarchy data first....", QMessageBox.Warning)
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"

  def test_component_delete_selected_type_with_loaded_data_hierarchy_should_delete_and_update_ui(self,
                                                                                                 data_hierarchy_editor_gui:
                                                                                                 tuple[
                                                                                                   QApplication,
                                                                                                   QtWidgets.QDialog,
                                                                                                   DataHierarchyEditorDialog,
                                                                                                   QtBot],
                                                                                                 data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                                                                 metadata_column_names: metadata_column_names,
                                                                                                 attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"
    # Select a non-structural type in the type combo box, in-order to enable the "delete" button
    ui_form.typeComboBox.setCurrentText("measurement")
    assert ui_form.typeComboBox.currentText() == "measurement", "Data type combo box should be selected to measurement"
    current_selected_type = ui_form.typeComboBox.currentText()
    previous_types_count = ui_form.typeComboBox.count()
    qtbot.mouseClick(ui_form.deleteTypePushButton, Qt.LeftButton)
    assert (current_selected_type not in [ui_form.typeComboBox.itemText(i)
                                          for i in range(ui_form.typeComboBox.count())]), \
      f"Deleted type:{current_selected_type} should not exist in combo list!"
    assert (previous_types_count - 1 == ui_form.typeComboBox.count()), \
      f"Combo list should have {previous_types_count - 1} items!"
    assert adapt_type(ui_form.typeComboBox.currentText()) == data_hierarchy_doc_mock.types_list()[0], \
      "Type combo box should be selected to first structural item"
    selected_type = data_hierarchy_doc_mock.types()[adapt_type(ui_form.typeComboBox.currentText())]
    assert ui_form.typeDisplayedTitleLineEdit.text() == selected_type["title"], \
      "Type title line edit should be selected to first structural item"
    assert ui_form.typeIriLineEdit.text() == selected_type["IRI"], \
      "Type IRI line edit should be selected to selected type IRI"
    assert ui_form.metadataGroupComboBox.currentText() == list(selected_type["meta"].keys())[0], \
      "Type metadata group combo box should be selected to first item in the selected type"
    self.check_table_contents(attachments_column_names, metadata_column_names, selected_type, ui_form)

  def test_component_add_new_type_button_click_should_display_create_new_type_window(self,
                                                                                     data_hierarchy_editor_gui:
                                                                                     tuple[
                                                                                       QApplication,
                                                                                       QtWidgets.QDialog,
                                                                                       DataHierarchyEditorDialog,
                                                                                       QtBot],
                                                                                     data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                                                     metadata_column_names: metadata_column_names,
                                                                                     attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=500):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog not shown!"

  def test_component_create_new_type_structural_type_should_add_new_type_with_displayed_title(self,
                                                                                              data_hierarchy_editor_gui:
                                                                                              tuple[
                                                                                                QApplication,
                                                                                                QtWidgets.QDialog,
                                                                                                DataHierarchyEditorDialog,
                                                                                                QtBot],
                                                                                              data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                                                              metadata_column_names: metadata_column_names,
                                                                                              attachments_column_names: attachments_column_names):

    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=500):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      ui_form.create_type_dialog.structuralLevelCheckBox.setChecked(True)
      ui_form.create_type_dialog.displayedTitleLineEdit.setText("test")
      assert ui_form.create_type_dialog.titleLineEdit.text() == ui_form.create_type_dialog.next_struct_level.replace(
        'x', 'Structure level '), "title should be set to 'Structure level 3'"
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.typeComboBox.currentText() == "Structure level 3", "Data type combo box should be newly added structural item"
    assert ui_form.typeDisplayedTitleLineEdit.text() == "test", "Data type displayedTitle should be newly added displayedTitle"

  def test_component_create_new_type_normal_type_should_add_new_type_with_displayed_title(self,
                                                                                          data_hierarchy_editor_gui:
                                                                                          tuple[
                                                                                            QApplication,
                                                                                            QtWidgets.QDialog,
                                                                                            DataHierarchyEditorDialog,
                                                                                            QtBot],
                                                                                          data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                                                          metadata_column_names: metadata_column_names,
                                                                                          attachments_column_names: attachments_column_names):

    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      assert ui_form.create_type_dialog.structuralLevelCheckBox.isChecked() is False, "structuralLevelCheckBox should be unchecked"
      ui_form.create_type_dialog.titleLineEdit.setText("Title")
      ui_form.create_type_dialog.displayedTitleLineEdit.setText("Displayed Title")
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.typeComboBox.currentText() == "Title", "Data type combo box should be newly added type title"
    assert ui_form.typeDisplayedTitleLineEdit.text() == "Displayed Title", "Data type combo box should be newly added type displayedTitle"

  def test_component_create_new_type_normal_type_with_empty_title_should_warn_user(self,
                                                                                   mocker,
                                                                                   data_hierarchy_editor_gui:
                                                                                   tuple[
                                                                                     QApplication,
                                                                                     QtWidgets.QDialog,
                                                                                     DataHierarchyEditorDialog,
                                                                                     QtBot],
                                                                                   data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                                                   metadata_column_names: metadata_column_names,
                                                                                   attachments_column_names: attachments_column_names):

    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    mocker.patch.object(ui_form.logger, 'warning')

    # Checking with empty title
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      assert ui_form.create_type_dialog.structuralLevelCheckBox.isChecked() is False, "structuralLevelCheckBox should be unchecked"
      ui_form.create_type_dialog.titleLineEdit.setText("")
      ui_form.create_type_dialog.displayedTitleLineEdit.setText("title")
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    ui_form.logger.warning.assert_called_once_with("Enter non-null/valid title!!.....")
    ui_form.message_box.setText.assert_called_once_with('Enter non-null/valid title!!.....')
    ui_form.message_box.exec.assert_called_once_with()
    ui_form.message_box.setIcon.assert_called_once_with(QtWidgets.QMessageBox.Warning)
    assert ui_form.typeComboBox.currentText() != "", "Data type combo box should not be empty title"
    assert ui_form.typeDisplayedTitleLineEdit.text() != "displayedTitle", "Data type combo box should not be newly added type displayedTitle"

    # Checking with None title
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      assert ui_form.create_type_dialog.structuralLevelCheckBox.isChecked() is False, "structuralLevelCheckBox should be unchecked"
      ui_form.create_type_dialog.titleLineEdit.setText(None)
      ui_form.create_type_dialog.displayedTitleLineEdit.setText("displayedTitle")
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    ui_form.logger.warning.assert_has_calls([
      mocker.call("Enter non-null/valid title!!....."),
      mocker.call("Enter non-null/valid title!!.....")])
    ui_form.message_box.setText.assert_has_calls([
      mocker.call("Enter non-null/valid title!!....."),
      mocker.call("Enter non-null/valid title!!.....")])
    ui_form.message_box.exec.assert_has_calls([
      mocker.call(),
      mocker.call()])
    ui_form.message_box.setIcon.assert_has_calls([
      mocker.call(QtWidgets.QMessageBox.Warning),
      mocker.call(QtWidgets.QMessageBox.Warning)])
    assert ui_form.typeComboBox.currentText() != None, "Data type combo box should not be None"
    assert ui_form.typeDisplayedTitleLineEdit.text() != "displayedTitle", "Data type combo box should not be newly added type displayedTitle"

  def test_component_create_new_type_reject_should_not_add_new_type_with_displayed_title(self,
                                                                                         data_hierarchy_editor_gui:
                                                                                         tuple[
                                                                                           QApplication,
                                                                                           QtWidgets.QDialog,
                                                                                           DataHierarchyEditorDialog,
                                                                                           QtBot],
                                                                                         data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                                                         metadata_column_names: metadata_column_names,
                                                                                         attachments_column_names: attachments_column_names):

    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=300):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      assert ui_form.create_type_dialog.structuralLevelCheckBox.isChecked() is False, "structuralLevelCheckBox should be unchecked"
      ui_form.create_type_dialog.titleLineEdit.setText("title")
      ui_form.create_type_dialog.displayedTitleLineEdit.setText("displayedTitle")
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Cancel),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.typeComboBox.currentText() != "title", "Data type combo box should not be newly added type title"
    assert ui_form.typeDisplayedTitleLineEdit.text() != "displayedTitle", "Data type combo box should not be newly added type displayedTitle"

  def test_component_cancel_button_click_after_delete_group_should_not_modify_data_hierarchy_document_data(self,
                                                                                                           data_hierarchy_editor_gui:
                                                                                                           tuple[
                                                                                                             QApplication,
                                                                                                             QtWidgets.QDialog,
                                                                                                             DataHierarchyEditorDialog,
                                                                                                             QtBot],
                                                                                                           data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                                                                           metadata_column_names: metadata_column_names,
                                                                                                           attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"
    current_selected_type_metadata_group = ui_form.metadataGroupComboBox.currentText()
    previous_types_metadata_group_count = ui_form.metadataGroupComboBox.count()
    qtbot.mouseClick(ui_form.deleteMetadataGroupPushButton, Qt.LeftButton)
    assert (current_selected_type_metadata_group not in [ui_form.metadataGroupComboBox.itemText(i)
                                                         for i in range(ui_form.metadataGroupComboBox.count())]), \
      f"Deleted group: {current_selected_type_metadata_group} should not exist in combo list!"
    assert (previous_types_metadata_group_count - 1 == ui_form.metadataGroupComboBox.count()), \
      f"Combo list should have {previous_types_metadata_group_count - 1} items!"
    qtbot.mouseClick(ui_form.cancelPushButton, Qt.LeftButton)
    assert data_hierarchy_doc_mock.types() != ui_form.data_hierarchy_types, "Data Hierarchy Document should not be modified!"

  def test_component_delete_type_after_creation_of_new_structural_type_should_succeed(self,
                                                                                      data_hierarchy_editor_gui:
                                                                                      tuple[
                                                                                        QApplication,
                                                                                        QtWidgets.QDialog,
                                                                                        DataHierarchyEditorDialog,
                                                                                        QtBot],
                                                                                      data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                                                      metadata_column_names: metadata_column_names,
                                                                                      attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      ui_form.create_type_dialog.structuralLevelCheckBox.setChecked(True)
      ui_form.create_type_dialog.displayedTitleLineEdit.setText("test")
      assert ui_form.create_type_dialog.titleLineEdit.text() == ui_form.create_type_dialog.next_struct_level.replace(
        'x', 'Structure level '), "title should be set to 'Structure level 3'"
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.typeComboBox.currentText() == "Structure level 3", "Data type combo box should be newly added structural item"
    assert ui_form.typeDisplayedTitleLineEdit.text() == "test", "Data type displayedTitle should be newly added displayedTitle"
    current_selected_type = ui_form.typeComboBox.currentText()
    previous_types_count = ui_form.typeComboBox.count()
    qtbot.mouseClick(ui_form.deleteTypePushButton, Qt.LeftButton)
    assert (current_selected_type not in [ui_form.typeComboBox.itemText(i)
                                          for i in range(ui_form.typeComboBox.count())]), \
      f"Deleted type:{current_selected_type} should not exist in combo list!"
    assert (previous_types_count - 1 == ui_form.typeComboBox.count()), \
      f"Combo list should have {previous_types_count - 1} items!"
    assert adapt_type(ui_form.typeComboBox.currentText()) == data_hierarchy_doc_mock.types_list()[0], \
      "Type combo box should be selected to first structural item"
    selected_type = data_hierarchy_doc_mock.types()[adapt_type(ui_form.typeComboBox.currentText())]
    assert ui_form.typeDisplayedTitleLineEdit.text() == selected_type["title"], \
      "Type displayedTitle line edit should be selected to first structural item"
    assert ui_form.typeIriLineEdit.text() == selected_type["IRI"], \
      "Type IRI line edit should be selected to IRI in selected type"
    assert ui_form.metadataGroupComboBox.currentText() == list(selected_type["meta"].keys())[0], \
      "Type metadata group combo box should be selected to first metadata group"
    self.check_table_contents(attachments_column_names, metadata_column_names, selected_type, ui_form)

  def test_component_save_button_click_after_delete_group_should_modify_data_hierarchy_document_data(self,
                                                                                                     mocker,
                                                                                                     data_hierarchy_editor_gui:
                                                                                                     tuple[
                                                                                                       QApplication,
                                                                                                       QtWidgets.QDialog,
                                                                                                       DataHierarchyEditorDialog,
                                                                                                       QtBot],
                                                                                                     data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                                                                     metadata_column_names: metadata_column_names,
                                                                                                     attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"
    mock_show_message = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.show_message', return_value=QMessageBox.Yes)
    current_selected_type_metadata_group = ui_form.metadataGroupComboBox.currentText()
    previous_types_metadata_group_count = ui_form.metadataGroupComboBox.count()
    qtbot.mouseClick(ui_form.deleteMetadataGroupPushButton, Qt.LeftButton)
    assert (current_selected_type_metadata_group not in [ui_form.metadataGroupComboBox.itemText(i)
                                                         for i in range(ui_form.metadataGroupComboBox.count())]), \
      f"Deleted group : {current_selected_type_metadata_group} should not exist in combo list!"
    assert (previous_types_metadata_group_count - 1 == ui_form.metadataGroupComboBox.count()), \
      f"Combo list should have {previous_types_metadata_group_count - 1} items!"
    qtbot.mouseClick(ui_form.saveDataHierarchyPushButton, Qt.LeftButton)
    assert data_hierarchy_doc_mock.types() == ui_form.data_hierarchy_types, "data_hierarchy document should be modified!"
    mock_show_message.assert_called_once_with('Save will close the tool and restart the Pasta Application (Yes/No?)',
                                              QMessageBox.Question,
                                              QMessageBox.No | QMessageBox.Yes,
                                              QMessageBox.Yes)

  def test_component_iri_lookup_button_click_should_show_data_hierarchy_lookup_dialog_and_set_iris_on_accept(self,
                                                                                                             data_hierarchy_editor_gui:
                                                                                                             tuple[
                                                                                                               QApplication,
                                                                                                               QtWidgets.QDialog,
                                                                                                               DataHierarchyEditorDialog,
                                                                                                               QtBot],
                                                                                                             data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                                                                             metadata_column_names: metadata_column_names,
                                                                                                             attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.typeIriLineEdit.text() == 'http://url.com', "typeIriLineEdit should be default test value"
    iri_lookup_action = None
    for act in ui_form.typeIriLineEdit.actions():
      if isinstance(act, LookupIriAction):
        iri_lookup_action = act
        act.trigger()
    lookup_dialog = iri_lookup_action.terminology_lookup_dialog
    assert lookup_dialog.selected_iris == [], "Selected IRIs should be empty"
    with qtbot.waitExposed(lookup_dialog.instance, timeout=500):
      assert lookup_dialog.instance.isVisible() is True, "Data Hierarchy lookup dialog should be visible"
      assert lookup_dialog.terminologyLineEdit.text() == "Projects", "Search term should be 'Projects'"
      assert lookup_dialog.errorConsoleTextEdit.isVisible() is False, "Error console should not be visible"
      assert lookup_dialog.scrollAreaWidgetContents.isVisible() is True, "Scroll area should be visible"
      assert lookup_dialog.scrollAreaContentsVerticalLayout.count() == 0, "Scroll area should be empty"
      qtbot.mouseClick(lookup_dialog.terminologySearchPushButton, Qt.LeftButton)
      assert lookup_dialog.scrollAreaContentsVerticalLayout.count() > 5, "Scroll area should be populated with more than 5 items"
      for pos in range(lookup_dialog.scrollAreaContentsVerticalLayout.count()):
        check_box = lookup_dialog.scrollAreaContentsVerticalLayout.itemAt(pos).widget().findChildren(QCheckBox)[0]
        assert check_box is not None and check_box.isChecked() is False, "Checkbox should not be checked"
        check_box.setChecked(True)
        assert check_box.isChecked() is True, "Checkbox should be checked"
    qtbot.mouseClick(lookup_dialog.buttonBox.button(lookup_dialog.buttonBox.Ok), Qt.LeftButton)
    assert lookup_dialog.instance.isVisible() is False, "Data Hierarchy lookup dialog should be accepted and closed"
    assert len(lookup_dialog.selected_iris) >= 5, "IRIs should be set"
    assert ui_form.typeIriLineEdit.text() == " ".join(
      lookup_dialog.selected_iris), "typeIriLineEdit should contain all selected IRIs"

  def test_component_iri_lookup_button_click_should_show_data_hierarchy_lookup_dialog_and_should_not_set_iris_on_cancel(
      self,
      data_hierarchy_editor_gui:
      tuple[
        QApplication,
        QtWidgets.QDialog,
        DataHierarchyEditorDialog,
        QtBot],
      data_hierarchy_doc_mock: data_hierarchy_doc_mock,
      metadata_column_names: metadata_column_names,
      attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.typeIriLineEdit.text() == 'http://url.com', "typeIriLineEdit should be default test value"
    iri_lookup_action = None
    for act in ui_form.typeIriLineEdit.actions():
      if isinstance(act, LookupIriAction):
        iri_lookup_action = act
        act.trigger()
    lookup_dialog = iri_lookup_action.terminology_lookup_dialog
    assert lookup_dialog.selected_iris == [], "Selected IRIs should be empty"
    with qtbot.waitExposed(lookup_dialog.instance, timeout=500):
      assert lookup_dialog.instance.isVisible() is True, "Data Hierarchy lookup dialog should be visible"
      assert lookup_dialog.terminologyLineEdit.text() == "Projects", "Search term should be 'Projects'"
      assert lookup_dialog.errorConsoleTextEdit.isVisible() is False, "Error console should not be visible"
      assert lookup_dialog.scrollAreaWidgetContents.isVisible() is True, "Scroll area should be visible"
      assert lookup_dialog.scrollAreaContentsVerticalLayout.count() == 0, "Scroll area should be empty"
      qtbot.mouseClick(lookup_dialog.terminologySearchPushButton, Qt.LeftButton)
      assert lookup_dialog.scrollAreaContentsVerticalLayout.count() > 5, "Scroll area should be populated with more than 5 items"
      for pos in range(lookup_dialog.scrollAreaContentsVerticalLayout.count()):
        check_box = lookup_dialog.scrollAreaContentsVerticalLayout.itemAt(pos).widget().findChildren(QCheckBox)[0]
        assert check_box is not None and check_box.isChecked() is False, "Checkbox should not be checked"
        check_box.setChecked(True)
        assert check_box.isChecked() is True, "Checkbox should be checked"
    qtbot.mouseClick(lookup_dialog.buttonBox.button(lookup_dialog.buttonBox.Cancel), Qt.LeftButton)
    assert lookup_dialog.instance.isVisible() is False, "data_hierarchy lookup dialog should be cancelled and closed"
    assert lookup_dialog.selected_iris == [], "IRIs should not be set"
    assert ui_form.typeIriLineEdit.text() == 'http://url.com', "typeIriLineEdit should be default test value after the cancellation"

  def test_delete_type_button_must_be_disabled_for_every_structural_level_except_the_last(self,
                                                                                          data_hierarchy_editor_gui:
                                                                                          tuple[
                                                                                            QApplication,
                                                                                            QtWidgets.QDialog,
                                                                                            DataHierarchyEditorDialog,
                                                                                            QtBot],
                                                                                          data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                                                          metadata_column_names: metadata_column_names,
                                                                                          attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.typeComboBox.currentText() == "Structure level 0", "Initial loaded type must be 'Structure level 0'"
    assert ui_form.deleteTypePushButton.isEnabled() is False, "Delete type button must be disabled for 'Structure level 0'"
    loaded_types = []
    for i in range(ui_form.typeComboBox.count()):
      loaded_types.append(ui_form.typeComboBox.itemText(i))
    enabled_structural_type = max(filter(lambda k: 'Structure level' in k, loaded_types))
    ui_form.typeComboBox.setCurrentText(enabled_structural_type)
    assert ui_form.deleteTypePushButton.isEnabled() is True, f"Delete type button must be enabled for only enabled structural type: '{enabled_structural_type}'"
    loaded_types.remove(enabled_structural_type)
    for loaded_type in loaded_types:
      ui_form.typeComboBox.setCurrentText(loaded_type)
      if "Structure level" in loaded_type:
        assert ui_form.deleteTypePushButton.isEnabled() is False, f"Delete type button must be disabled for '{loaded_type}'"
      else:
        assert ui_form.deleteTypePushButton.isEnabled() is True, "Delete type button must be enabled for normal types"

    # Add a new structural type and check if the delete button is disabled for the previously enabled type
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      ui_form.create_type_dialog.structuralLevelCheckBox.setChecked(True)
      ui_form.create_type_dialog.displayedTitleLineEdit.setText("test")
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)
    ui_form.typeComboBox.setCurrentText(enabled_structural_type)
    assert ui_form.deleteTypePushButton.isEnabled() is False, f"Delete type button must be disabled for only previously enabled structural type: '{enabled_structural_type}'"

    # Reload the types and check after the addition of new type and check if the delete button is enabled/disabled
    loaded_types.clear()
    for i in range(ui_form.typeComboBox.count()):
      loaded_types.append(ui_form.typeComboBox.itemText(i))
    enabled_structural_type = max(filter(lambda k: 'Structure level' in k, loaded_types))
    ui_form.typeComboBox.setCurrentText(enabled_structural_type)
    assert ui_form.deleteTypePushButton.isEnabled() is True, f"Delete type button must be enabled for only enabled structural type: '{enabled_structural_type}'"
    loaded_types.remove(enabled_structural_type)
    for loaded_type in loaded_types:
      ui_form.typeComboBox.setCurrentText(loaded_type)
      if "Structure level" in loaded_type:
        assert ui_form.deleteTypePushButton.isEnabled() is False, f"Delete type button must be disabled for '{loaded_type}'"
      else:
        assert ui_form.deleteTypePushButton.isEnabled() is True, "Delete type button must be enabled for normal types"

    # Add a normal type and check if the delete button is disabled correctly for the structural types
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      ui_form.create_type_dialog.titleLineEdit.setText("new type")
      ui_form.create_type_dialog.displayedTitleLineEdit.setText("test")
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)

    # Reload the types and check after the addition of new type and check if the delete button is enabled/disabled
    loaded_types.clear()
    for i in range(ui_form.typeComboBox.count()):
      loaded_types.append(ui_form.typeComboBox.itemText(i))
    enabled_structural_type = max(filter(lambda k: 'Structure level' in k, loaded_types))
    ui_form.typeComboBox.setCurrentText(enabled_structural_type)
    assert ui_form.deleteTypePushButton.isEnabled() is True, f"Delete type button must be enabled for only enabled structural type: '{enabled_structural_type}'"
    loaded_types.remove(enabled_structural_type)
    for loaded_type in loaded_types:
      ui_form.typeComboBox.setCurrentText(loaded_type)
      if "Structure level" in loaded_type:
        assert ui_form.deleteTypePushButton.isEnabled() is False, f"Delete type button must be disabled for '{loaded_type}'"
      else:
        assert ui_form.deleteTypePushButton.isEnabled() is True, "Delete type button must be enabled for normal types'"

  def test_delete_of_structural_type_possible_from_xn_to_x1_must_succeed_and_x0_delete_disabled(self,
                                                                                                data_hierarchy_editor_gui:
                                                                                                tuple[
                                                                                                  QApplication,
                                                                                                  QtWidgets.QDialog,
                                                                                                  DataHierarchyEditorDialog,
                                                                                                  QtBot],
                                                                                                data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                                                                metadata_column_names: metadata_column_names,
                                                                                                attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.typeComboBox.currentText() == "Structure level 0", "Initial loaded type must be 'Structure level 0'"
    assert ui_form.deleteTypePushButton.isEnabled() is False, "Delete type button must be disabled for 'Structure level 0'"
    # Add 5 structural types
    for _ in range(5):
      qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
      with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=300):
        ui_form.create_type_dialog.structuralLevelCheckBox.setChecked(True)
        ui_form.create_type_dialog.displayedTitleLineEdit.setText("test")
      qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                       Qt.LeftButton)

    loaded_types = [
      ui_form.typeComboBox.itemText(i)
      for i in range(ui_form.typeComboBox.count())
    ]
    # Delete the normal types from UI
    normal_types = list(filter(lambda k: 'Structure level' not in k, loaded_types))
    for normal_type in normal_types:
      ui_form.typeComboBox.setCurrentText(normal_type)
      assert ui_form.deleteTypePushButton.isEnabled() is True, f"Delete type button must be enabled for only enabled structural type: '{normal_type}'"
      qtbot.mouseClick(ui_form.deleteTypePushButton, Qt.LeftButton)
      for i in range(ui_form.typeComboBox.count()):
        assert ui_form.typeComboBox.itemText(
          i) != normal_type, f"Deleted type:{normal_type} should not exist in combo list!"
      loaded_types.remove(normal_type)

    structural_types = sorted(
      filter(lambda k: 'Structure level' in k, loaded_types))
    assert structural_types == loaded_types, "All normal types must be deleted from UI, hence only structural types are left!"
    for _ in range(len(structural_types)):
      enabled_structural_type = max(structural_types)
      if enabled_structural_type == 'Structure level 0':
        break
      for structural_type in list(structural_types):
        if structural_type == enabled_structural_type:
          ui_form.typeComboBox.setCurrentText(structural_type)
          assert ui_form.deleteTypePushButton.isEnabled() is True, f"Delete type button must be enabled for only enabled structural type: '{structural_type}'"
          qtbot.mouseClick(ui_form.deleteTypePushButton, Qt.LeftButton)
          for j in range(ui_form.typeComboBox.count()):
            assert ui_form.typeComboBox.itemText(
              j) != structural_type, f"Deleted type:{structural_type} should not exist in combo list!"
          structural_types.remove(structural_type)
          loaded_types.remove(structural_type)
        else:
          ui_form.typeComboBox.setCurrentText(structural_type)
          assert ui_form.deleteTypePushButton.isEnabled() is False, f"Delete type button must be disabled for '{structural_type}'"
    assert structural_types == loaded_types == [
      "Structure level 0"], "All structural types must be deleted from UI except 'Structure level 0'"

  def test_hide_show_attachments_table_should_do_as_expected(self,
                                                             data_hierarchy_editor_gui:
                                                             tuple[
                                                               QApplication,
                                                               QtWidgets.QDialog,
                                                               DataHierarchyEditorDialog,
                                                               QtBot],
                                                             data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                             metadata_column_names: metadata_column_names,
                                                             attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.typeAttachmentsTableView.isHidden() is True, "Attachments table should not be visible initially!"
    assert ui_form.addAttachmentPushButton.isHidden() is True, "addAttachmentPushButton should not be visible initially!"

    qtbot.mouseClick(ui_form.attachmentsShowHidePushButton,
                     Qt.LeftButton)
    assert ui_form.typeAttachmentsTableView.isHidden() is False, "Attachments table should be visible now!"
    assert ui_form.addAttachmentPushButton.isHidden() is False, "addAttachmentPushButton should be visible now!"
    qtbot.mouseClick(ui_form.attachmentsShowHidePushButton,
                     Qt.LeftButton)
    assert ui_form.typeAttachmentsTableView.isVisible() is False, "Attachments table should not be visible now!"
    assert ui_form.addAttachmentPushButton.isVisible() is False, "addAttachmentPushButton should not be visible now!"

    qtbot.mouseClick(ui_form.attachmentsShowHidePushButton,
                     Qt.LeftButton)
    assert ui_form.typeAttachmentsTableView.isHidden() is False, "Attachments table should be visible now!"
    assert ui_form.addAttachmentPushButton.isHidden() is False, "addAttachmentPushButton should be visible now!"

    qtbot.mouseClick(ui_form.attachmentsShowHidePushButton,
                     Qt.LeftButton)
    assert ui_form.typeAttachmentsTableView.isVisible() is False, "Attachments table should not be visible now!"
    assert ui_form.addAttachmentPushButton.isVisible() is False, "addAttachmentPushButton should not be visible now!"

  def test_add_group_with_empty_name_should_warn_user(self,
                                                      data_hierarchy_editor_gui:
                                                      tuple[
                                                        QApplication,
                                                        QtWidgets.QDialog,
                                                        DataHierarchyEditorDialog,
                                                        QtBot],
                                                      data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                      metadata_column_names: metadata_column_names,
                                                      attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.addMetadataGroupPushButton.isHidden() is False, "addMetadataGroupPushButton should be visible now!"
    ui_form.addMetadataGroupLineEdit.setText("")
    qtbot.mouseClick(ui_form.addMetadataGroupPushButton, Qt.LeftButton)
    ui_form.message_box.setText.assert_called_once_with('Enter non-null/valid metadata group name!!.....')
    ui_form.message_box.setIcon.assert_called_once_with(QtWidgets.QMessageBox.Warning)
    ui_form.message_box.exec.assert_called_once_with()

  def test_add_metadata_group_with_valid_name_should_successfully_add_group_with_default_metadata(self,
                                                                                                  data_hierarchy_editor_gui:
                                                                                                  tuple[
                                                                                                    QApplication,
                                                                                                    QtWidgets.QDialog,
                                                                                                    DataHierarchyEditorDialog,
                                                                                                    QtBot],
                                                                                                  data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                                                                  metadata_column_names: metadata_column_names,
                                                                                                  attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.addMetadataGroupPushButton.isHidden() is False, "addMetadataGroupPushButton should be visible now!"
    groups = []
    initial_groups = []
    newly_added_groups = []
    for i in range(ui_form.metadataGroupComboBox.count()):
      initial_groups.append(ui_form.metadataGroupComboBox.itemText(i))

    # Add 10 groups and check if the group combo-box is updated and also the metadata-table too
    for index in range(10):
      new_group = f"new group {index}"
      groups.clear()
      for i in range(ui_form.metadataGroupComboBox.count()):
        groups.append(ui_form.metadataGroupComboBox.itemText(i))
      assert new_group not in groups, f"{new_group} should not exist in combo list!"
      ui_form.addMetadataGroupLineEdit.setText(new_group)
      qtbot.mouseClick(ui_form.addMetadataGroupPushButton, Qt.LeftButton)
      assert ui_form.metadataGroupComboBox.currentText() == new_group, f"metadataGroupComboBox.currentText() should be {new_group}!"
      newly_added_groups.append(new_group)
      model = ui_form.typeMetadataTableView.model()
      assert model.rowCount() == 0, "Metadata table should be empty now!"

    # Check finally if all the newly added groups are present apart from the initial metadata groups
    groups.clear()
    for i in range(ui_form.metadataGroupComboBox.count()):
      groups.append(ui_form.metadataGroupComboBox.itemText(i))
    assert [c for c in groups if
            c not in initial_groups] == newly_added_groups, "Present - Initial must give newly added groups!"

  def test_add_group_with_valid_name_and_delete_should_successfully_delete_categories_with_metadata(self,
                                                                                                    data_hierarchy_editor_gui:
                                                                                                    tuple[
                                                                                                      QApplication,
                                                                                                      QtWidgets.QDialog,
                                                                                                      DataHierarchyEditorDialog,
                                                                                                      QtBot],
                                                                                                    data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                                                                    metadata_column_names: metadata_column_names,
                                                                                                    attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.addMetadataGroupPushButton.isHidden() is False, "addMetadataGroupPushButton should be visible now!"

    # Add 10 categories
    for index in range(10):
      new_group = f"new group {index}"
      ui_form.addMetadataGroupLineEdit.setText(new_group)
      qtbot.mouseClick(ui_form.addMetadataGroupPushButton, Qt.LeftButton)
      assert ui_form.metadataGroupComboBox.currentText() == new_group, f"metadataGroupComboBox.currentText() should be {new_group}!"

    categories = []
    for i in range(ui_form.metadataGroupComboBox.count()):
      categories.append(ui_form.metadataGroupComboBox.itemText(i))

    reversed_categories = list(reversed(categories))
    for idx, cat in enumerate(reversed_categories):
      assert ui_form.metadataGroupComboBox.currentText() == cat, f"metadataGroupComboBox.currentText() should be {cat}!"
      qtbot.mouseClick(ui_form.deleteMetadataGroupPushButton, Qt.LeftButton)
      assert ui_form.metadataGroupComboBox.currentText() != cat, f"metadataGroupComboBox.currentText() should be {cat}!"
      if idx == len(categories) - 1:
        # ALl metadata group are deleted, hence the metadata table should be empty!
        assert ui_form.metadataGroupComboBox.currentText() == "", \
          f"metadataGroupComboBox.currentText() should be empty string!"
        model = ui_form.typeMetadataTableView.model()
        assert model.rowCount() == 0, "Metadata table should be empty!"
      else:
        assert ui_form.metadataGroupComboBox.currentText() == reversed_categories[
          idx + 1], f"metadataGroupComboBox.currentText() should be {reversed_categories[idx + 1]}!"
        model = ui_form.typeMetadataTableView.model()
        assert model.rowCount() >= 0, "Metadata table can be empty or not!"

  def test_add_metadata_to_table_should_succeed(self,
                                                data_hierarchy_editor_gui:
                                                tuple[
                                                  QApplication,
                                                  QtWidgets.QDialog,
                                                  DataHierarchyEditorDialog,
                                                  QtBot],
                                                data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                metadata_column_names: metadata_column_names,
                                                attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.addMetadataGroupPushButton.isHidden() is False, "addMetadataGroupPushButton should be visible now!"
    ui_form.addMetadataGroupLineEdit.setText("new Group")
    qtbot.mouseClick(ui_form.addMetadataGroupPushButton, Qt.LeftButton)
    assert "new Group" == ui_form.metadataGroupComboBox.currentText(), "metadataGroupComboBox.currentText() should be new Group!"
    model = ui_form.typeMetadataTableView.model()
    assert model.rowCount() == 0, "Metadata table should be empty!"
    qtbot.mouseClick(ui_form.addMetadataRowPushButton, Qt.LeftButton)
    assert model.rowCount() == 1, "Single metadata must be present after addition!"
    model.setData(model.index(0, 0), "Test name", Qt.UserRole)
    model.setData(model.index(0, 1), "Test query", Qt.UserRole)

    ui_form.metadataGroupComboBox.setCurrentText("default")
    assert ui_form.metadataGroupComboBox.currentText() == "default", f"metadataGroupComboBox.currentText() should be default!"
    model = ui_form.typeMetadataTableView.model()
    assert model.rowCount() == 5, "5 metadata must be present in default Group"

    ui_form.metadataGroupComboBox.setCurrentText("new Group")
    assert ui_form.metadataGroupComboBox.currentText() == "new Group", f"metadataGroupComboBox.currentText() should be default!"
    model = ui_form.typeMetadataTableView.model()
    assert model.rowCount() == 1, "Single metadata must be present after addition!"
    assert model.data(model.index(0, 0), Qt.DisplayRole) == 'Test name', "Test name metadata must be present!"
    assert model.data(model.index(0, 1), Qt.DisplayRole) == 'Test query', "Test query metadata must be present!"

  def test_delete_metadata_from_table_should_work(self,
                                                  data_hierarchy_editor_gui:
                                                  tuple[
                                                    QApplication,
                                                    QtWidgets.QDialog,
                                                    DataHierarchyEditorDialog,
                                                    QtBot],
                                                  data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                  metadata_column_names: metadata_column_names,
                                                  attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    ui_form.metadataGroupComboBox.setCurrentText("default")
    assert ui_form.metadataGroupComboBox.currentText() == "default", f"metadataGroupComboBox.currentText() should be default!"
    model = ui_form.typeMetadataTableView.model()
    assert model.rowCount() == 5, "5 metadata must be present before deletion!"
    row_count = model.rowCount()
    for i in range(model.rowCount()):
      last_row_delete_index = ui_form.typeMetadataTableView.model().index(
        ui_form.typeMetadataTableView.model().rowCount() - 1,
        ui_form.typeMetadataTableView.model().columnCount() - 2)
      rect = ui_form.typeMetadataTableView.visualRect(last_row_delete_index)
      qtbot.mouseClick(ui_form.typeMetadataTableView.viewport(), Qt.LeftButton, pos=rect.center())
      assert model.rowCount() == row_count - 1, f"{row_count - 1} metadata must be present after deletion!"
      row_count -= 1
    assert model.rowCount() == 0, "After full deletion, nothing must exist!"

  def test_re_order_metadata_table_should_work_as_expected(self,
                                                           data_hierarchy_editor_gui:
                                                           tuple[
                                                             QApplication,
                                                             QtWidgets.QDialog,
                                                             DataHierarchyEditorDialog,
                                                             QtBot],
                                                           data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                           metadata_column_names: metadata_column_names,
                                                           attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    ui_form.metadataGroupComboBox.setCurrentText("default")
    assert ui_form.metadataGroupComboBox.currentText() == "default", f"metadataGroupComboBox.currentText() should be default!"
    model = ui_form.typeMetadataTableView.model()
    assert model.rowCount() == 5, "5 metadata must be present before deletion!"
    # Initial data order
    init_data_order = ['-name', 'status', 'objective', '-tags', 'comment']
    post_reorder_data_order1 = ['-name', 'status', 'objective', 'comment', '-tags']
    post_reorder_data_order2 = ['status', '-name', 'objective', 'comment', '-tags']
    data_order = []
    for i in range(model.rowCount()):
      data_order.append(model.data(model.index(i, 0), Qt.DisplayRole))
    assert init_data_order == data_order, "Initial data order is not as expected!"

    # Click re-order for the last row
    last_row_re_order_index = ui_form.typeMetadataTableView.model().index(
      ui_form.typeMetadataTableView.model().rowCount() - 1,
      ui_form.typeMetadataTableView.model().columnCount() - 1)
    rect = ui_form.typeMetadataTableView.visualRect(last_row_re_order_index)
    qtbot.mouseClick(ui_form.typeMetadataTableView.viewport(), Qt.LeftButton, pos=rect.center())
    data_order.clear()
    for i in range(model.rowCount()):
      data_order.append(model.data(model.index(i, 0), Qt.DisplayRole))
    assert post_reorder_data_order1 == data_order, "Post reorder data order is not as expected!"

    # Click re-order for the second row
    second_row_re_order_index = ui_form.typeMetadataTableView.model().index(
      1,
      ui_form.typeMetadataTableView.model().columnCount() - 1)
    rect = ui_form.typeMetadataTableView.visualRect(second_row_re_order_index)
    qtbot.mouseClick(ui_form.typeMetadataTableView.viewport(), Qt.LeftButton, pos=rect.center())
    data_order.clear()
    for i in range(model.rowCount()):
      data_order.append(model.data(model.index(i, 0), Qt.DisplayRole))
    assert post_reorder_data_order2 == data_order, "Post reorder data order is not as expected!"

  def test_add_attachments_to_table_should_succeed(self,
                                                   data_hierarchy_editor_gui:
                                                   tuple[
                                                     QApplication,
                                                     QtWidgets.QDialog,
                                                     DataHierarchyEditorDialog,
                                                     QtBot],
                                                   data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                   metadata_column_names: metadata_column_names,
                                                   attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.addAttachmentPushButton.isHidden() is True, "addAttachmentPushButton should be hidden initially!"
    qtbot.mouseClick(ui_form.attachmentsShowHidePushButton, Qt.LeftButton)
    assert ui_form.addAttachmentPushButton.isHidden() is False, "addAttachmentPushButton should be shown after clicking attachmentsShowHidePushButton!"

    selected_type = ui_form.typeComboBox.currentText()

    model = ui_form.typeAttachmentsTableView.model()
    assert model.rowCount() == 0, "Initially the table must be empty!"

    qtbot.mouseClick(ui_form.addAttachmentPushButton, Qt.LeftButton)

    assert model.rowCount() == 1, "One row should be added!"
    model.setData(model.index(0, 0), "Test description", Qt.UserRole)
    model.setData(model.index(0, 1), "Test location", Qt.UserRole)

    ui_form.typeComboBox.setCurrentText("Structure level 1")

    model = ui_form.typeAttachmentsTableView.model()
    assert model.rowCount() == 0, "'Structure level 1' attachment table must be empty!"

    ui_form.typeComboBox.setCurrentText(selected_type)

    model = ui_form.typeAttachmentsTableView.model()
    assert model.data(model.index(0, 0), Qt.DisplayRole) == 'Test description', "Description metadata must be present!"
    assert model.data(model.index(0, 1), Qt.DisplayRole) == 'Test location', "Location metadata must be present!"

  def test_delete_attachments_from_table_should_succeed(self,
                                                        data_hierarchy_editor_gui:
                                                        tuple[
                                                          QApplication,
                                                          QtWidgets.QDialog,
                                                          DataHierarchyEditorDialog,
                                                          QtBot],
                                                        data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                        metadata_column_names: metadata_column_names,
                                                        attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.addAttachmentPushButton.isHidden() is True, "addAttachmentPushButton should be hidden initially!"
    qtbot.mouseClick(ui_form.attachmentsShowHidePushButton, Qt.LeftButton)
    assert ui_form.addAttachmentPushButton.isHidden() is False, "addAttachmentPushButton should be shown after clicking attachmentsShowHidePushButton!"

    selected_type = ui_form.typeComboBox.currentText()

    model = ui_form.typeAttachmentsTableView.model()
    assert model.rowCount() == 0, "Initially the table must be empty!"

    qtbot.mouseClick(ui_form.addAttachmentPushButton, Qt.LeftButton)
    qtbot.mouseClick(ui_form.addAttachmentPushButton, Qt.LeftButton)

    assert model.rowCount() == 2, "Two attachments should be added!"
    model.setData(model.index(0, 0), "Test description1", Qt.UserRole)
    model.setData(model.index(0, 1), "Test location1", Qt.UserRole)
    model.setData(model.index(1, 0), "Test description2", Qt.UserRole)
    model.setData(model.index(1, 1), "Test location2", Qt.UserRole)

    ui_form.typeComboBox.setCurrentText("Structure level 1")

    model = ui_form.typeAttachmentsTableView.model()
    assert model.rowCount() == 0, "'Structure level 1' attachment table must be empty!"

    ui_form.typeComboBox.setCurrentText(selected_type)

    first_row_delete_index = ui_form.typeAttachmentsTableView.model().index(
      0,
      ui_form.typeAttachmentsTableView.model().columnCount() - 2)

    rect = ui_form.typeAttachmentsTableView.visualRect(first_row_delete_index)
    qtbot.mouseClick(ui_form.typeAttachmentsTableView.viewport(), Qt.LeftButton, pos=rect.center())

    assert model.rowCount() == 1, "One attachment should be present!"
    model.setData(model.index(0, 0), "Test description2", Qt.UserRole)
    model.setData(model.index(0, 1), "Test location2", Qt.UserRole)

  def test_re_order_attachments_from_table_should_succeed(self,
                                                          data_hierarchy_editor_gui:
                                                          tuple[
                                                            QApplication,
                                                            QtWidgets.QDialog,
                                                            DataHierarchyEditorDialog,
                                                            QtBot],
                                                          data_hierarchy_doc_mock: data_hierarchy_doc_mock,
                                                          metadata_column_names: metadata_column_names,
                                                          attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = data_hierarchy_editor_gui
    assert ui_form.addAttachmentPushButton.isHidden() is True, "addAttachmentPushButton should be hidden initially!"
    qtbot.mouseClick(ui_form.attachmentsShowHidePushButton, Qt.LeftButton)
    assert ui_form.addAttachmentPushButton.isHidden() is False, "addAttachmentPushButton should be shown after clicking attachmentsShowHidePushButton!"

    selected_type = ui_form.typeComboBox.currentText()

    model = ui_form.typeAttachmentsTableView.model()
    assert model.rowCount() == 0, "Initially the table must be empty!"

    qtbot.mouseClick(ui_form.addAttachmentPushButton, Qt.LeftButton)
    qtbot.mouseClick(ui_form.addAttachmentPushButton, Qt.LeftButton)

    assert model.rowCount() == 2, "Two attachments should be added!"
    model.setData(model.index(0, 0), "Test description1", Qt.UserRole)
    model.setData(model.index(0, 1), "Test location1", Qt.UserRole)
    model.setData(model.index(1, 0), "Test description2", Qt.UserRole)
    model.setData(model.index(1, 1), "Test location2", Qt.UserRole)

    ui_form.typeComboBox.setCurrentText("Structure level 1")

    model = ui_form.typeAttachmentsTableView.model()
    assert model.rowCount() == 0, "'Structure level 1' attachment table must be empty!"

    ui_form.typeComboBox.setCurrentText(selected_type)

    second_row_re_order_index = ui_form.typeAttachmentsTableView.model().index(
      1,
      ui_form.typeAttachmentsTableView.model().columnCount() - 1)

    rect = ui_form.typeAttachmentsTableView.visualRect(second_row_re_order_index)
    qtbot.mouseClick(ui_form.typeAttachmentsTableView.viewport(), Qt.LeftButton, pos=rect.center())

    assert model.rowCount() == 2, "Two attachments should be present!"
    assert model.index(0, 0).data(Qt.UserRole) == "Test description2", "After re-order data order is not as expected!"
    assert model.index(0, 1).data(Qt.UserRole) == "Test location2", "After re-order data order is not as expected!"
    assert model.index(1, 0).data(Qt.UserRole) == "Test description1", "After re-order data order is not as expected!"
    assert model.index(1, 1).data(Qt.UserRole) == "Test location1", "After re-order data order is not as expected!"
