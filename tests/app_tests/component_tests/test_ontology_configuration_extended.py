#   PASTA-ELN and all its sub-parts are covered by the MIT license.
#  #
#   Copyright (c) 2023
#  #
#   Author: Jithu Murugan
#   Filename: test_ontology_configuration_extended.py
#  #
#   You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QCheckBox, QMessageBox
from pytestqt.qtbot import QtBot

from pasta_eln.GUI.ontology_configuration.lookup_iri_action import LookupIriAction
from pasta_eln.GUI.ontology_configuration.ontology_configuration_extended import OntologyConfigurationForm
from pasta_eln.GUI.ontology_configuration.utility_functions import adapt_type, get_types_for_display
from tests.app_tests.common.fixtures import attachments_column_names, ontology_doc_mock, ontology_editor_gui, \
  pasta_db_mock, props_column_names


class TestOntologyConfigurationExtended(object):

  def test_component_launch_should_display_all_ui_elements(self,
                                                           pasta_db_mock: pasta_db_mock,
                                                           # Added to import fixture by other tests
                                                           ontology_editor_gui: tuple[
                                                             QApplication,
                                                             QtWidgets.QDialog,
                                                             OntologyConfigurationForm,
                                                             QtBot]):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.headerLabel is not None, "Header not loaded!"
    assert ui_form.typeLabel is not None, "Data type label not loaded!"
    assert ui_form.saveOntologyPushButton is not None, "Save button not loaded!"
    assert ui_form.helpPushButton is not None, "Help button not loaded!"
    assert ui_form.typePropsTableView is not None, "Properties table view not loaded!"
    assert ui_form.typeAttachmentsTableView is not None, "Type table view not loaded!"
    assert ui_form.addAttachmentPushButton is not None, "Add attachment button not loaded!"
    assert ui_form.addTypePushButton is not None, "Add type button not loaded!"
    assert ui_form.addPropsRowPushButton is not None, "Add property row button not loaded!"
    assert ui_form.addPropsCategoryPushButton is not None, "Add property category button not loaded!"
    assert ui_form.cancelPushButton is not None, "Cancel button not loaded!"
    assert ui_form.typeLabelLineEdit is not None, "Data type line edit not loaded!"
    assert ui_form.typeIriLineEdit is not None, "Data type IRI line edit not loaded!"
    assert ui_form.addPropsCategoryLineEdit is not None, "Property category line edit not loaded!"
    assert ui_form.typeComboBox is not None, "Data type combo box not loaded!"
    assert ui_form.propsCategoryComboBox is not None, "Property category combo box not loaded!"
    assert ui_form.typeAttachmentsTableView.isHidden() is True, "Type attachments table view should not be shown!"
    assert ui_form.addAttachmentPushButton.isHidden() is True, "addAttachmentPushButton should not be shown!"

  @pytest.mark.parametrize(
    "type_to_select, category_selected, properties", [
      ('Structure level 0', 'default', ['-name', 'status', 'objective', '-tags', 'comment']),
      ('Structure level 1', 'default', ['-name', '-tags', 'comment']),
      ('Structure level 2', 'default', ['-name', '-tags', 'comment']),
      ('measurement', 'default', ['-name', '-tags', 'comment', '-type', 'image', '#_curated', 'sample', 'procedure']),
      ('sample', 'default', ['-name', 'chemistry', '-tags', 'comment', 'qrCode']),
      ('procedure', 'default', ['-name', '-tags', 'comment', 'content']),
      ('instrument', 'default', ['-name', '-tags', 'comment', 'vendor'])
    ])
  def test_type_select_should_load_data_and_update_ui_elements(self,
                                                               ontology_editor_gui: tuple[
                                                                 QApplication,
                                                                 QtWidgets.QDialog,
                                                                 OntologyConfigurationForm,
                                                                 QtBot],
                                                               type_to_select: str,
                                                               category_selected: str,
                                                               properties: list):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    ui_form.typeComboBox.setCurrentText(type_to_select)
    assert ui_form.typeComboBox.currentText() == type_to_select, "Type combo box not selected!"
    assert ui_form.propsCategoryComboBox.currentText() == category_selected, "Property category combo box not selected!"
    selected_props = []
    model = ui_form.typePropsTableView.model()
    for i in range(model.rowCount()):
      selected_props.append(model.data(model.index(i, 0), Qt.DisplayRole))
    assert properties == selected_props, "Selected properties not as expected!"

  def test_component_launch_should_load_ontology_data(self,
                                                      ontology_editor_gui: tuple[
                                                        QApplication,
                                                        QtWidgets.QDialog,
                                                        OntologyConfigurationForm,
                                                        QtBot],
                                                      ontology_doc_mock: ontology_doc_mock,
                                                      props_column_names: props_column_names,
                                                      attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ([ui_form.typeComboBox.itemText(i) for i in range(ui_form.typeComboBox.count())]
            == get_types_for_display(ontology_doc_mock.types_list())), "Type combo box not loaded!"
    assert (adapt_type(ui_form.typeComboBox.currentText())
            == ontology_doc_mock.types_list()[0]), "Type combo box should be selected to first item"
    selected_type = ontology_doc_mock.types()[adapt_type(ui_form.typeComboBox.currentText())]
    assert (ui_form.typeLabelLineEdit.text() ==
            selected_type["label"]), "Data type label line edit not loaded!"
    assert (ui_form.typeIriLineEdit.text() ==
            selected_type["IRI"]), "Data type IRI line edit not loaded!"

    categories = list(selected_type["prop"].keys())
    assert ([ui_form.propsCategoryComboBox.itemText(i) for i in range(ui_form.propsCategoryComboBox.count())]
            == categories), "propsCategoryComboBox combo box not loaded!"
    assert (ui_form.propsCategoryComboBox.currentText()
            == categories[0]), "propsCategoryComboBox should be selected to first item"
    self.check_table_contents(attachments_column_names, props_column_names, selected_type, ui_form)

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

  def check_table_contents(self, attachments_column_names, props_column_names, selected_type, ui_form):
    categories = list(selected_type["prop"].keys())
    # Assert if the properties are loaded in the table view
    model = ui_form.typePropsTableView.model()
    self.check_table_view_model(model, props_column_names, selected_type["prop"][categories[0]])
    # Assert if the attachments are loaded in the table view
    model = ui_form.typeAttachmentsTableView.model()
    self.check_table_view_model(model, attachments_column_names, selected_type["attachments"])

  def test_component_add_new_type_with_loaded_ontology_should_display_create_new_type_window(self,
                                                                                             ontology_editor_gui: tuple[
                                                                                               QApplication,
                                                                                               QtWidgets.QDialog,
                                                                                               OntologyConfigurationForm,
                                                                                               QtBot],
                                                                                             ontology_doc_mock: ontology_doc_mock):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog not shown!"

  def test_component_delete_new_type_without_ontology_loaded_should_show_error_message(self,
                                                                                       ontology_editor_gui: tuple[
                                                                                         QApplication,
                                                                                         QtWidgets.QDialog,
                                                                                         OntologyConfigurationForm,
                                                                                         QtBot],
                                                                                       ontology_doc_mock: ontology_doc_mock,
                                                                                       mocker):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    mock_show_message = mocker.patch(
      "pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.show_message")
    mocker.patch.object(ui_form, "ontology_loaded", False)
    # Select a non-structural type in the type combo box, in order to enable the delete button
    ui_form.typeComboBox.setCurrentText("measurement")
    assert ui_form.typeComboBox.currentText() == "measurement", "Data type combo box should be selected to measurement"
    qtbot.mouseClick(ui_form.deleteTypePushButton, Qt.LeftButton)
    mock_show_message.assert_called_once_with("Load the ontology data first....", QMessageBox.Warning)
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"

  def test_component_delete_selected_type_with_loaded_ontology_should_delete_and_update_ui(self,
                                                                                           ontology_editor_gui:
                                                                                           tuple[
                                                                                             QApplication,
                                                                                             QtWidgets.QDialog,
                                                                                             OntologyConfigurationForm,
                                                                                             QtBot],
                                                                                           ontology_doc_mock: ontology_doc_mock,
                                                                                           props_column_names: props_column_names,
                                                                                           attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"
    # Select a non-structural type in the type combo box, in order to enable the "delete" button
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
    assert adapt_type(ui_form.typeComboBox.currentText()) == ontology_doc_mock.types_list()[0], \
      "Type combo box should be selected to first structural item"
    selected_type = ontology_doc_mock.types()[adapt_type(ui_form.typeComboBox.currentText())]
    assert ui_form.typeLabelLineEdit.text() == selected_type["label"], \
      "Type label line edit should be selected to first structural item"
    assert ui_form.typeIriLineEdit.text() == selected_type["IRI"], \
      "Type label line edit should be selected to first structural item"
    assert ui_form.propsCategoryComboBox.currentText() == list(selected_type["prop"].keys())[0], \
      "Type label line edit should be selected to first structural item"
    self.check_table_contents(attachments_column_names, props_column_names, selected_type, ui_form)

  def test_component_add_new_type_button_click_should_display_create_new_type_window(self,
                                                                                     ontology_editor_gui:
                                                                                     tuple[
                                                                                       QApplication,
                                                                                       QtWidgets.QDialog,
                                                                                       OntologyConfigurationForm,
                                                                                       QtBot],
                                                                                     ontology_doc_mock: ontology_doc_mock,
                                                                                     props_column_names: props_column_names,
                                                                                     attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=500):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog not shown!"

  def test_component_create_new_type_structural_type_should_add_new_type_with_label(self,
                                                                                    ontology_editor_gui:
                                                                                    tuple[
                                                                                      QApplication,
                                                                                      QtWidgets.QDialog,
                                                                                      OntologyConfigurationForm,
                                                                                      QtBot],
                                                                                    ontology_doc_mock: ontology_doc_mock,
                                                                                    props_column_names: props_column_names,
                                                                                    attachments_column_names: attachments_column_names):

    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      ui_form.create_type_dialog.structuralLevelCheckBox.setChecked(True)
      ui_form.create_type_dialog.labelLineEdit.setText("test")
      assert ui_form.create_type_dialog.titleLineEdit.text() == ui_form.create_type_dialog.next_struct_level.replace(
        'x', 'Structure level '), "title should be set to 'Structure level 3'"
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.typeComboBox.currentText() == "Structure level 3", "Data type combo box should be newly added structural item"
    assert ui_form.typeLabelLineEdit.text() == "test", "Data type label should be newly added label"

  def test_component_create_new_type_normal_type_should_add_new_type_with_label(self,
                                                                                ontology_editor_gui:
                                                                                tuple[
                                                                                  QApplication,
                                                                                  QtWidgets.QDialog,
                                                                                  OntologyConfigurationForm,
                                                                                  QtBot],
                                                                                ontology_doc_mock: ontology_doc_mock,
                                                                                props_column_names: props_column_names,
                                                                                attachments_column_names: attachments_column_names):

    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      assert ui_form.create_type_dialog.structuralLevelCheckBox.isChecked() is False, "structuralLevelCheckBox should be unchecked"
      ui_form.create_type_dialog.titleLineEdit.setText("title")
      ui_form.create_type_dialog.labelLineEdit.setText("label")
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.typeComboBox.currentText() == "title", "Data type combo box should be newly added type title"
    assert ui_form.typeLabelLineEdit.text() == "label", "Data type combo box should be newly added type label"

  def test_component_create_new_type_normal_type_with_empty_title_should_warn_user(self,
                                                                                   mocker,
                                                                                   ontology_editor_gui:
                                                                                   tuple[
                                                                                     QApplication,
                                                                                     QtWidgets.QDialog,
                                                                                     OntologyConfigurationForm,
                                                                                     QtBot],
                                                                                   ontology_doc_mock: ontology_doc_mock,
                                                                                   props_column_names: props_column_names,
                                                                                   attachments_column_names: attachments_column_names):

    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
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
      ui_form.create_type_dialog.labelLineEdit.setText("label")
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    ui_form.logger.warning.assert_called_once_with("Enter non-null/valid title!!.....")
    ui_form.message_box.setText.assert_called_once_with('Enter non-null/valid title!!.....')
    ui_form.message_box.exec.assert_called_once_with()
    ui_form.message_box.setIcon.assert_called_once_with(QtWidgets.QMessageBox.Warning)
    assert ui_form.typeComboBox.currentText() != "", "Data type combo box should not be empty title"
    assert ui_form.typeLabelLineEdit.text() != "label", "Data type combo box should not be newly added type label"

    # Checking with None title
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      assert ui_form.create_type_dialog.structuralLevelCheckBox.isChecked() is False, "structuralLevelCheckBox should be unchecked"
      ui_form.create_type_dialog.titleLineEdit.setText(None)
      ui_form.create_type_dialog.labelLineEdit.setText("label")
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
    assert ui_form.typeLabelLineEdit.text() != "label", "Data type combo box should not be newly added type label"

  def test_component_create_new_type_reject_should_not_add_new_type_with_label(self,
                                                                               ontology_editor_gui:
                                                                               tuple[
                                                                                 QApplication,
                                                                                 QtWidgets.QDialog,
                                                                                 OntologyConfigurationForm,
                                                                                 QtBot],
                                                                               ontology_doc_mock: ontology_doc_mock,
                                                                               props_column_names: props_column_names,
                                                                               attachments_column_names: attachments_column_names):

    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      assert ui_form.create_type_dialog.structuralLevelCheckBox.isChecked() is False, "structuralLevelCheckBox should be unchecked"
      ui_form.create_type_dialog.titleLineEdit.setText("title")
      ui_form.create_type_dialog.labelLineEdit.setText("label")
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Cancel),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.typeComboBox.currentText() != "title", "Data type combo box should not be newly added type title"
    assert ui_form.typeLabelLineEdit.text() != "label", "Data type combo box should not be newly added type label"

  def test_component_cancel_button_click_after_delete_category_should_not_modify_ontology_document_data(self,
                                                                                                        ontology_editor_gui:
                                                                                                        tuple[
                                                                                                          QApplication,
                                                                                                          QtWidgets.QDialog,
                                                                                                          OntologyConfigurationForm,
                                                                                                          QtBot],
                                                                                                        ontology_doc_mock: ontology_doc_mock,
                                                                                                        props_column_names: props_column_names,
                                                                                                        attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"
    current_selected_type_category = ui_form.propsCategoryComboBox.currentText()
    previous_types_category_count = ui_form.propsCategoryComboBox.count()
    qtbot.mouseClick(ui_form.deletePropsCategoryPushButton, Qt.LeftButton)
    assert (current_selected_type_category not in [ui_form.propsCategoryComboBox.itemText(i)
                                                   for i in range(ui_form.propsCategoryComboBox.count())]), \
      f"Deleted category: {current_selected_type_category} should not exist in combo list!"
    assert (previous_types_category_count - 1 == ui_form.propsCategoryComboBox.count()), \
      f"Combo list should have {previous_types_category_count - 1} items!"
    qtbot.mouseClick(ui_form.cancelPushButton, Qt.LeftButton)
    assert ontology_doc_mock.types() != ui_form.ontology_types, "Ontology document should not be modified!"

  def test_component_delete_type_after_creation_of_new_structural_type_should_succeed(self,
                                                                                      ontology_editor_gui:
                                                                                      tuple[
                                                                                        QApplication,
                                                                                        QtWidgets.QDialog,
                                                                                        OntologyConfigurationForm,
                                                                                        QtBot],
                                                                                      ontology_doc_mock: ontology_doc_mock,
                                                                                      props_column_names: props_column_names,
                                                                                      attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog button box should not be shown!"
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
      assert ui_form.create_type_dialog.instance.isVisible() is True, "Create new type dialog should be shown!"
      assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog button box should be shown!"
      ui_form.create_type_dialog.structuralLevelCheckBox.setChecked(True)
      ui_form.create_type_dialog.labelLineEdit.setText("test")
      assert ui_form.create_type_dialog.titleLineEdit.text() == ui_form.create_type_dialog.next_struct_level.replace(
        'x', 'Structure level '), "title should be set to 'Structure level 3'"
    qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                     Qt.LeftButton)
    assert ui_form.create_type_dialog.instance.isVisible() is False, "Create new type dialog should not be shown!"
    assert ui_form.typeComboBox.currentText() == "Structure level 3", "Data type combo box should be newly added structural item"
    assert ui_form.typeLabelLineEdit.text() == "test", "Data type label should be newly added label"
    current_selected_type = ui_form.typeComboBox.currentText()
    previous_types_count = ui_form.typeComboBox.count()
    qtbot.mouseClick(ui_form.deleteTypePushButton, Qt.LeftButton)
    assert (current_selected_type not in [ui_form.typeComboBox.itemText(i)
                                          for i in range(ui_form.typeComboBox.count())]), \
      f"Deleted type:{current_selected_type} should not exist in combo list!"
    assert (previous_types_count - 1 == ui_form.typeComboBox.count()), \
      f"Combo list should have {previous_types_count - 1} items!"
    assert adapt_type(ui_form.typeComboBox.currentText()) == ontology_doc_mock.types_list()[0], \
      "Type combo box should be selected to first structural item"
    selected_type = ontology_doc_mock.types()[adapt_type(ui_form.typeComboBox.currentText())]
    assert ui_form.typeLabelLineEdit.text() == selected_type["label"], \
      "Type label line edit should be selected to first structural item"
    assert ui_form.typeIriLineEdit.text() == selected_type["IRI"], \
      "Type label line edit should be selected to first structural item"
    assert ui_form.propsCategoryComboBox.currentText() == list(selected_type["prop"].keys())[0], \
      "Type label line edit should be selected to first structural item"
    self.check_table_contents(attachments_column_names, props_column_names, selected_type, ui_form)

  def test_component_save_button_click_after_delete_category_should_modify_ontology_document_data(self,
                                                                                                  mocker,
                                                                                                  ontology_editor_gui:
                                                                                                  tuple[
                                                                                                    QApplication,
                                                                                                    QtWidgets.QDialog,
                                                                                                    OntologyConfigurationForm,
                                                                                                    QtBot],
                                                                                                  ontology_doc_mock: ontology_doc_mock,
                                                                                                  props_column_names: props_column_names,
                                                                                                  attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"
    mock_show_message = mocker.patch(
      'pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.show_message', return_value=QMessageBox.Yes)
    current_selected_type_category = ui_form.propsCategoryComboBox.currentText()
    previous_types_category_count = ui_form.propsCategoryComboBox.count()
    qtbot.mouseClick(ui_form.deletePropsCategoryPushButton, Qt.LeftButton)
    assert (current_selected_type_category not in [ui_form.propsCategoryComboBox.itemText(i)
                                                   for i in range(ui_form.propsCategoryComboBox.count())]), \
      f"Deleted category: {current_selected_type_category} should not exist in combo list!"
    assert (previous_types_category_count - 1 == ui_form.propsCategoryComboBox.count()), \
      f"Combo list should have {previous_types_category_count - 1} items!"
    qtbot.mouseClick(ui_form.saveOntologyPushButton, Qt.LeftButton)
    assert ontology_doc_mock.types() == ui_form.ontology_types, "Ontology document should be modified!"
    mock_show_message.assert_called_once_with('Save will close the tool and restart the Pasta Application (Yes/No?)',
                                              QMessageBox.Question,
                                              QMessageBox.No | QMessageBox.Yes,
                                              QMessageBox.Yes)

  def test_component_iri_lookup_button_click_should_show_ontology_lookup_dialog_and_set_iris_on_accept(self,
                                                                                                       ontology_editor_gui:
                                                                                                       tuple[
                                                                                                         QApplication,
                                                                                                         QtWidgets.QDialog,
                                                                                                         OntologyConfigurationForm,
                                                                                                         QtBot],
                                                                                                       ontology_doc_mock: ontology_doc_mock,
                                                                                                       props_column_names: props_column_names,
                                                                                                       attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.typeIriLineEdit.text() == 'http://url.com', "typeIriLineEdit should be default test value"
    iri_lookup_action = None
    for act in ui_form.typeIriLineEdit.actions():
      if isinstance(act, LookupIriAction):
        iri_lookup_action = act
        act.trigger()
    lookup_dialog = iri_lookup_action.terminology_lookup_dialog
    assert lookup_dialog.selected_iris == [], "Selected IRIs should be empty"
    with qtbot.waitExposed(lookup_dialog.instance, timeout=500):
      assert lookup_dialog.instance.isVisible() is True, "Ontology lookup dialog should be visible"
      assert lookup_dialog.terminologyLineEdit.text() == "Projects", "Search term should be 'Projects'"
      assert lookup_dialog.errorConsoleTextEdit.isVisible() is False, "Error console should not be visible"
      assert lookup_dialog.scrollAreaWidgetContents.isVisible() is True, "Scroll area should be visible"
      assert lookup_dialog.scrollAreaContentsVerticalLayout.count() == 0, "Scroll area should be empty"
      qtbot.mouseClick(lookup_dialog.terminologySearchPushButton, Qt.LeftButton)
      assert lookup_dialog.scrollAreaContentsVerticalLayout.count() in [11,12], "Scroll area should be populated with 11 or 12 items"
      for pos in range(lookup_dialog.scrollAreaContentsVerticalLayout.count()):
        check_box = lookup_dialog.scrollAreaContentsVerticalLayout.itemAt(pos).widget().findChildren(QCheckBox)[0]
        assert check_box is not None and check_box.isChecked() is False, "Checkbox should not be checked"
        check_box.setChecked(True)
        assert check_box.isChecked() is True, "Checkbox should be checked"
    qtbot.mouseClick(lookup_dialog.buttonBox.button(lookup_dialog.buttonBox.Ok), Qt.LeftButton)
    assert lookup_dialog.instance.isVisible() is False, "Ontology lookup dialog should be accepted and closed"
    assert len(lookup_dialog.selected_iris) == 11, "IRIs should be set"
    assert ui_form.typeIriLineEdit.text() == " ".join(
      lookup_dialog.selected_iris), "typeIriLineEdit should contain all selected IRIs"

  def test_component_iri_lookup_button_click_should_show_ontology_lookup_dialog_and_should_not_set_iris_on_cancel(self,
                                                                                                                  ontology_editor_gui:
                                                                                                                  tuple[
                                                                                                                    QApplication,
                                                                                                                    QtWidgets.QDialog,
                                                                                                                    OntologyConfigurationForm,
                                                                                                                    QtBot],
                                                                                                                  ontology_doc_mock: ontology_doc_mock,
                                                                                                                  props_column_names: props_column_names,
                                                                                                                  attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.typeIriLineEdit.text() == 'http://url.com', "typeIriLineEdit should be default test value"
    iri_lookup_action = None
    for act in ui_form.typeIriLineEdit.actions():
      if isinstance(act, LookupIriAction):
        iri_lookup_action = act
        act.trigger()
    lookup_dialog = iri_lookup_action.terminology_lookup_dialog
    assert lookup_dialog.selected_iris == [], "Selected IRIs should be empty"
    with qtbot.waitExposed(lookup_dialog.instance, timeout=500):
      assert lookup_dialog.instance.isVisible() is True, "Ontology lookup dialog should be visible"
      assert lookup_dialog.terminologyLineEdit.text() == "Projects", "Search term should be 'Projects'"
      assert lookup_dialog.errorConsoleTextEdit.isVisible() is False, "Error console should not be visible"
      assert lookup_dialog.scrollAreaWidgetContents.isVisible() is True, "Scroll area should be visible"
      assert lookup_dialog.scrollAreaContentsVerticalLayout.count() == 0, "Scroll area should be empty"
      qtbot.mouseClick(lookup_dialog.terminologySearchPushButton, Qt.LeftButton)
      assert lookup_dialog.scrollAreaContentsVerticalLayout.count() in [11,12], "Scroll area should be populated with 11 or 12 items"
      for pos in range(lookup_dialog.scrollAreaContentsVerticalLayout.count()):
        check_box = lookup_dialog.scrollAreaContentsVerticalLayout.itemAt(pos).widget().findChildren(QCheckBox)[0]
        assert check_box is not None and check_box.isChecked() is False, "Checkbox should not be checked"
        check_box.setChecked(True)
        assert check_box.isChecked() is True, "Checkbox should be checked"
    qtbot.mouseClick(lookup_dialog.buttonBox.button(lookup_dialog.buttonBox.Cancel), Qt.LeftButton)
    assert lookup_dialog.instance.isVisible() is False, "Ontology lookup dialog should be cancelled and closed"
    assert lookup_dialog.selected_iris == [], "IRIs should not be set"
    assert ui_form.typeIriLineEdit.text() == 'http://url.com', "typeIriLineEdit should be default test value after the cancellation"

  def test_delete_type_button_must_be_disabled_for_every_structural_level_except_the_last(self,
                                                                                          ontology_editor_gui:
                                                                                          tuple[
                                                                                            QApplication,
                                                                                            QtWidgets.QDialog,
                                                                                            OntologyConfigurationForm,
                                                                                            QtBot],
                                                                                          ontology_doc_mock: ontology_doc_mock,
                                                                                          props_column_names: props_column_names,
                                                                                          attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
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
      ui_form.create_type_dialog.labelLineEdit.setText("test")
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
      ui_form.create_type_dialog.labelLineEdit.setText("test")
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
                                                                                                ontology_editor_gui:
                                                                                                tuple[
                                                                                                  QApplication,
                                                                                                  QtWidgets.QDialog,
                                                                                                  OntologyConfigurationForm,
                                                                                                  QtBot],
                                                                                                ontology_doc_mock: ontology_doc_mock,
                                                                                                props_column_names: props_column_names,
                                                                                                attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.typeComboBox.currentText() == "Structure level 0", "Initial loaded type must be 'Structure level 0'"
    assert ui_form.deleteTypePushButton.isEnabled() is False, "Delete type button must be disabled for 'Structure level 0'"
    # Add 5 structural types
    for i in range(5):
      qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
      with qtbot.waitExposed(ui_form.create_type_dialog.instance, timeout=200):
        ui_form.create_type_dialog.structuralLevelCheckBox.setChecked(True)
        ui_form.create_type_dialog.labelLineEdit.setText("test")
      qtbot.mouseClick(ui_form.create_type_dialog.buttonBox.button(ui_form.create_type_dialog.buttonBox.Ok),
                       Qt.LeftButton)

    # Read the loaded types
    loaded_types = []
    for i in range(ui_form.typeComboBox.count()):
      loaded_types.append(ui_form.typeComboBox.itemText(i))

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

    # Delete the structural types from UI
    structural_types = list(filter(lambda k: 'Structure level' in k, loaded_types))
    structural_types.sort()
    assert structural_types == loaded_types, "All normal types must be deleted from UI, hence only structural types are left!"
    for i in range(len(structural_types)):
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
                                                             ontology_editor_gui:
                                                             tuple[
                                                               QApplication,
                                                               QtWidgets.QDialog,
                                                               OntologyConfigurationForm,
                                                               QtBot],
                                                             ontology_doc_mock: ontology_doc_mock,
                                                             props_column_names: props_column_names,
                                                             attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
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

  def test_add_category_with_empty_name_should_warn_user(self,
                                                         ontology_editor_gui:
                                                         tuple[
                                                           QApplication,
                                                           QtWidgets.QDialog,
                                                           OntologyConfigurationForm,
                                                           QtBot],
                                                         ontology_doc_mock: ontology_doc_mock,
                                                         props_column_names: props_column_names,
                                                         attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.addPropsCategoryPushButton.isHidden() is False, "addPropsCategoryPushButton should be visible now!"
    ui_form.addPropsCategoryLineEdit.setText("")
    qtbot.mouseClick(ui_form.addPropsCategoryPushButton, Qt.LeftButton)
    ui_form.message_box.setText.assert_called_once_with('Enter non-null/valid category name!!.....')
    ui_form.message_box.setIcon.assert_called_once_with(QtWidgets.QMessageBox.Warning)
    ui_form.message_box.exec.assert_called_once_with()

  def test_add_category_with_valid_name_should_successfully_add_category_with_default_properties(self,
                                                                                                 ontology_editor_gui:
                                                                                                 tuple[
                                                                                                   QApplication,
                                                                                                   QtWidgets.QDialog,
                                                                                                   OntologyConfigurationForm,
                                                                                                   QtBot],
                                                                                                 ontology_doc_mock: ontology_doc_mock,
                                                                                                 props_column_names: props_column_names,
                                                                                                 attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.addPropsCategoryPushButton.isHidden() is False, "addPropsCategoryPushButton should be visible now!"
    categories = []
    initial_categories = []
    newly_added_categories = []
    for i in range(ui_form.propsCategoryComboBox.count()):
      initial_categories.append(ui_form.propsCategoryComboBox.itemText(i))

    # Add 10 categories and check if the category combo-box is updated and also the property-table too
    for index in range(10):
      new_category = f"new category {index}"
      categories.clear()
      for i in range(ui_form.propsCategoryComboBox.count()):
        categories.append(ui_form.propsCategoryComboBox.itemText(i))
      assert new_category not in categories, f"{new_category} should not exist in combo list!"
      ui_form.addPropsCategoryLineEdit.setText(new_category)
      qtbot.mouseClick(ui_form.addPropsCategoryPushButton, Qt.LeftButton)
      assert ui_form.propsCategoryComboBox.currentText() == new_category, f"propsCategoryComboBox.currentText() should be {new_category}!"
      newly_added_categories.append(new_category)
      model = ui_form.typePropsTableView.model()
      assert model.rowCount() == 2, "Minimum of two required properties must be added"
      assert model.data(model.index(0, 0), Qt.DisplayRole) == '-name', "Name property must be added!"
      assert model.data(model.index(1, 0), Qt.DisplayRole) == '-tags', "Tags property must be added!"

    # Check finally if all the newly added categories are present apart from the initial categories
    categories.clear()
    for i in range(ui_form.propsCategoryComboBox.count()):
      categories.append(ui_form.propsCategoryComboBox.itemText(i))
    assert [c for c in categories if
            c not in initial_categories] == newly_added_categories, "Present - Initial must give newly added categories!"

  def test_add_category_with_valid_name_and_delete_should_successfully_delete_categories_with_properties(self,
                                                                                                         ontology_editor_gui:
                                                                                                         tuple[
                                                                                                           QApplication,
                                                                                                           QtWidgets.QDialog,
                                                                                                           OntologyConfigurationForm,
                                                                                                           QtBot],
                                                                                                         ontology_doc_mock: ontology_doc_mock,
                                                                                                         props_column_names: props_column_names,
                                                                                                         attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.addPropsCategoryPushButton.isHidden() is False, "addPropsCategoryPushButton should be visible now!"

    # Add 10 categories
    for index in range(10):
      new_category = f"new category {index}"
      ui_form.addPropsCategoryLineEdit.setText(new_category)
      qtbot.mouseClick(ui_form.addPropsCategoryPushButton, Qt.LeftButton)
      assert ui_form.propsCategoryComboBox.currentText() == new_category, f"propsCategoryComboBox.currentText() should be {new_category}!"

    categories = []
    for i in range(ui_form.propsCategoryComboBox.count()):
      categories.append(ui_form.propsCategoryComboBox.itemText(i))

    reversed_categories = list(reversed(categories))
    for idx, cat in enumerate(reversed_categories):
      assert ui_form.propsCategoryComboBox.currentText() == cat, f"propsCategoryComboBox.currentText() should be {cat}!"
      qtbot.mouseClick(ui_form.deletePropsCategoryPushButton, Qt.LeftButton)
      assert ui_form.propsCategoryComboBox.currentText() != cat, f"propsCategoryComboBox.currentText() should be {cat}!"
      if idx == len(categories) - 1:
        # ALl property categories are deleted, hence the property table should be empty!
        assert ui_form.propsCategoryComboBox.currentText() == "", \
          f"propsCategoryComboBox.currentText() should be empty string!"
        model = ui_form.typePropsTableView.model()
        assert model.rowCount() == 0, "Property table should be empty!"
      else:
        assert ui_form.propsCategoryComboBox.currentText() == reversed_categories[
          idx + 1], f"propsCategoryComboBox.currentText() should be {reversed_categories[idx + 1]}!"
        model = ui_form.typePropsTableView.model()
        assert model.rowCount() >= 2, "Minimum of two required properties must be present"

  def test_add_properties_to_table_should_succeed(self,
                                                  ontology_editor_gui:
                                                  tuple[
                                                    QApplication,
                                                    QtWidgets.QDialog,
                                                    OntologyConfigurationForm,
                                                    QtBot],
                                                  ontology_doc_mock: ontology_doc_mock,
                                                  props_column_names: props_column_names,
                                                  attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.addPropsCategoryPushButton.isHidden() is False, "addPropsCategoryPushButton should be visible now!"
    ui_form.addPropsCategoryLineEdit.setText("new category")
    qtbot.mouseClick(ui_form.addPropsCategoryPushButton, Qt.LeftButton)
    ui_form.propsCategoryComboBox.setCurrentText("new category")
    model = ui_form.typePropsTableView.model()
    assert model.rowCount() == 2, "Minimum of two required properties must be present"
    assert model.data(model.index(0, 0), Qt.DisplayRole) == '-name', "Name property must be present!"
    assert model.data(model.index(1, 0), Qt.DisplayRole) == '-tags', "Tags property must be present!"
    qtbot.mouseClick(ui_form.addPropsRowPushButton, Qt.LeftButton)
    assert model.rowCount() == 3, "Three properties must be present after addition!"
    model.setData(model.index(2, 0), "Test name", Qt.UserRole)
    model.setData(model.index(2, 1), "Test query", Qt.UserRole)

    ui_form.propsCategoryComboBox.setCurrentText("default")
    assert ui_form.propsCategoryComboBox.currentText() == "default", f"propsCategoryComboBox.currentText() should be default!"
    model = ui_form.typePropsTableView.model()
    assert model.rowCount() == 5, "5 properties must be present in default category"

    ui_form.propsCategoryComboBox.setCurrentText("new category")
    assert ui_form.propsCategoryComboBox.currentText() == "new category", f"propsCategoryComboBox.currentText() should be default!"
    model = ui_form.typePropsTableView.model()
    assert model.rowCount() == 3, "Three properties must be present after addition!"
    assert model.data(model.index(0, 0), Qt.DisplayRole) == '-name', "Name property must be present!"
    assert model.data(model.index(1, 0), Qt.DisplayRole) == '-tags', "Tags property must be present!"
    assert model.data(model.index(2, 0), Qt.DisplayRole) == 'Test name', "Test name property must be present!"
    assert model.data(model.index(2, 1), Qt.DisplayRole) == 'Test query', "Test query property must be present!"

  def test_delete_property_from_table_should_work(self,
                                                  ontology_editor_gui:
                                                  tuple[
                                                    QApplication,
                                                    QtWidgets.QDialog,
                                                    OntologyConfigurationForm,
                                                    QtBot],
                                                  ontology_doc_mock: ontology_doc_mock,
                                                  props_column_names: props_column_names,
                                                  attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    ui_form.propsCategoryComboBox.setCurrentText("default")
    assert ui_form.propsCategoryComboBox.currentText() == "default", f"propsCategoryComboBox.currentText() should be default!"
    model = ui_form.typePropsTableView.model()
    assert model.rowCount() == 5, "5 properties must be present before deletion!"
    row_count = model.rowCount()
    for i in range(model.rowCount()):
      last_row_delete_index = ui_form.typePropsTableView.model().index(
        ui_form.typePropsTableView.model().rowCount() - 1,
        ui_form.typePropsTableView.model().columnCount() - 2)
      rect = ui_form.typePropsTableView.visualRect(last_row_delete_index)
      qtbot.mouseClick(ui_form.typePropsTableView.viewport(), Qt.LeftButton, pos=rect.center())
      assert model.rowCount() == row_count - 1, f"{row_count - 1} properties must be present after deletion!"
      row_count -= 1
    assert model.rowCount() == 0, "After full deletion, nothing must exist!"

  def test_re_order_property_table_should_work_as_expected(self,
                                                           ontology_editor_gui:
                                                           tuple[
                                                             QApplication,
                                                             QtWidgets.QDialog,
                                                             OntologyConfigurationForm,
                                                             QtBot],
                                                           ontology_doc_mock: ontology_doc_mock,
                                                           props_column_names: props_column_names,
                                                           attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    ui_form.propsCategoryComboBox.setCurrentText("default")
    assert ui_form.propsCategoryComboBox.currentText() == "default", f"propsCategoryComboBox.currentText() should be default!"
    model = ui_form.typePropsTableView.model()
    assert model.rowCount() == 5, "5 properties must be present before deletion!"
    # Initial data order
    init_data_order = ['-name', 'status', 'objective', '-tags', 'comment']
    post_reorder_data_order1 = ['-name', 'status', 'objective', 'comment', '-tags']
    post_reorder_data_order2 = ['status', '-name', 'objective', 'comment', '-tags']
    data_order = []
    for i in range(model.rowCount()):
      data_order.append(model.data(model.index(i, 0), Qt.DisplayRole))
    assert init_data_order == data_order, "Initial data order is not as expected!"

    # Click re-order for the last row
    last_row_re_order_index = ui_form.typePropsTableView.model().index(
      ui_form.typePropsTableView.model().rowCount() - 1,
      ui_form.typePropsTableView.model().columnCount() - 1)
    rect = ui_form.typePropsTableView.visualRect(last_row_re_order_index)
    qtbot.mouseClick(ui_form.typePropsTableView.viewport(), Qt.LeftButton, pos=rect.center())
    data_order.clear()
    for i in range(model.rowCount()):
      data_order.append(model.data(model.index(i, 0), Qt.DisplayRole))
    assert post_reorder_data_order1 == data_order, "Post reorder data order is not as expected!"

    # Click re-order for the second row
    second_row_re_order_index = ui_form.typePropsTableView.model().index(
      1,
      ui_form.typePropsTableView.model().columnCount() - 1)
    rect = ui_form.typePropsTableView.visualRect(second_row_re_order_index)
    qtbot.mouseClick(ui_form.typePropsTableView.viewport(), Qt.LeftButton, pos=rect.center())
    data_order.clear()
    for i in range(model.rowCount()):
      data_order.append(model.data(model.index(i, 0), Qt.DisplayRole))
    assert post_reorder_data_order2 == data_order, "Post reorder data order is not as expected!"

  def test_add_attachments_to_table_should_succeed(self,
                                                   ontology_editor_gui:
                                                   tuple[
                                                     QApplication,
                                                     QtWidgets.QDialog,
                                                     OntologyConfigurationForm,
                                                     QtBot],
                                                   ontology_doc_mock: ontology_doc_mock,
                                                   props_column_names: props_column_names,
                                                   attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
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
    assert model.data(model.index(0, 0), Qt.DisplayRole) == 'Test description', "Description property must be present!"
    assert model.data(model.index(0, 1), Qt.DisplayRole) == 'Test location', "Location property must be present!"

  def test_delete_attachments_from_table_should_succeed(self,
                                                        ontology_editor_gui:
                                                        tuple[
                                                          QApplication,
                                                          QtWidgets.QDialog,
                                                          OntologyConfigurationForm,
                                                          QtBot],
                                                        ontology_doc_mock: ontology_doc_mock,
                                                        props_column_names: props_column_names,
                                                        attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
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
                                                          ontology_editor_gui:
                                                          tuple[
                                                            QApplication,
                                                            QtWidgets.QDialog,
                                                            OntologyConfigurationForm,
                                                            QtBot],
                                                          ontology_doc_mock: ontology_doc_mock,
                                                          props_column_names: props_column_names,
                                                          attachments_column_names: attachments_column_names):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
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
