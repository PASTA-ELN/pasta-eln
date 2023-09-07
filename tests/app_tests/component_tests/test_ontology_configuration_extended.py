#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_configuration_extended.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: test_ontology_configuration_extended.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from pasta_eln.ontology_configuration.ontology_configuration_extended import OntologyConfigurationForm
from tests.app_tests.common.fixtures import ontology_editor_gui, ontology_doc_mock, props_column_names, \
  attachments_column_names


class TestOntologyConfigurationExtended(object):

  def test_component_launch_should_display_all_ui_elements(self,
                                                           ontology_editor_gui: tuple[
                                                             QApplication,
                                                             QtWidgets.QDialog,
                                                             OntologyConfigurationForm,
                                                             QtBot]):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.headerLabel is not None, "Header not loaded!"
    assert ui_form.typeLabel is not None, "Data type label not loaded!"
    assert ui_form.loadOntologyPushButton is not None, "Bush button not loaded!"
    assert ui_form.saveOntologyPushButton is not None, "Save button not loaded!"
    assert ui_form.helpPushButton is not None, "Help button not loaded!"
    assert ui_form.cancelPushButton is not None, "Cancel button not loaded!"
    assert ui_form.typePropsTableView is not None, "Properties table view not loaded!"
    assert ui_form.typeAttachmentsTableView is not None, "Type table view not loaded!"
    assert ui_form.addAttachmentPushButton is not None, "Add attachment button not loaded!"
    assert ui_form.addTypePushButton is not None, "Add type button not loaded!"
    assert ui_form.addPropsRowPushButton is not None, "Add property row button not loaded!"
    assert ui_form.addPropsCategoryPushButton is not None, "Add property category button not loaded!"
    assert ui_form.typeLabelLineEdit is not None, "Data type line edit not loaded!"
    assert ui_form.typeLinkLineEdit is not None, "Data type link line edit not loaded!"
    assert ui_form.addPropsCategoryLineEdit is not None, "Property category line edit not loaded!"
    assert ui_form.typeComboBox is not None, "Data type combo box not loaded!"
    assert ui_form.propsCategoryComboBox is not None, "Property category combo box not loaded!"

  def test_component_load_button_click_should_load_ontology_data(self,
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
            == []), "Type combo box should not be loaded!"
    assert ui_form.loadOntologyPushButton.click() is None, "Load button not clicked!"
    assert ([ui_form.typeComboBox.itemText(i) for i in range(ui_form.typeComboBox.count())]
            == ontology_doc_mock.types_list()), "Type combo box not loaded!"
    assert (ui_form.typeComboBox.currentText()
            == ontology_doc_mock.types_list()[0]), "Type combo box should be selected to first item"
    selected_type = ontology_doc_mock.types()[ui_form.typeComboBox.currentText()]
    assert (ui_form.typeLabelLineEdit.text() ==
            selected_type["label"]), "Data type label line edit not loaded!"
    assert (ui_form.typeLinkLineEdit.text() ==
            selected_type["link"]), "Data type link line edit not loaded!"

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
          assert (model.data(index, Qt.DisplayRole)
                  == str(data[column_names[column]])), f"{column_names[column]} not loaded!"
        else:
          assert model.data(index, Qt.DisplayRole) == "", f"{column_names[column]} should be null string!"

  def check_table_contents(self, attachments_column_names, props_column_names, selected_type, ui_form):
    categories = list(selected_type["prop"].keys())
    # Assert if the properties are loaded in the table view
    model = ui_form.typePropsTableView.model()
    self.check_table_view_model(model, props_column_names, selected_type["prop"][categories[0]])
    # Assert if the attachments are loaded in the table view
    model = ui_form.typeAttachmentsTableView.model()
    self.check_table_view_model(model, attachments_column_names, selected_type["attachments"])

  def test_component_add_new_type_with_ontology_loaded_should_display_error_message(self,
                                                                                    ontology_editor_gui: tuple[
                                                                                      QApplication,
                                                                                      QtWidgets.QDialog,
                                                                                      OntologyConfigurationForm,
                                                                                      QtBot],
                                                                                    ontology_doc_mock: ontology_doc_mock,
                                                                                    mocker):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    mock_show_message = mocker.patch("pasta_eln.ontology_configuration.ontology_configuration_extended.show_message")
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    mock_show_message.assert_called_once_with("Load the ontology data first...")
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"

  def test_component_add_new_type_with_loaded_ontology_should_display_create_new_type_window(self,
                                                                                             ontology_editor_gui: tuple[
                                                                                               QApplication,
                                                                                               QtWidgets.QDialog,
                                                                                               OntologyConfigurationForm,
                                                                                               QtBot],
                                                                                             ontology_doc_mock: ontology_doc_mock):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    assert ui_form.create_type_dialog.buttonBox.isVisible() is False, "Create new type dialog should not be shown!"
    qtbot.mouseClick(ui_form.loadOntologyPushButton, Qt.LeftButton)
    qtbot.mouseClick(ui_form.addTypePushButton, Qt.LeftButton)
    assert ui_form.create_type_dialog.buttonBox.isVisible() is True, "Create new type dialog not shown!"

  def test_component_delete_new_type_with_ontology_loaded_should_show_error_message(self,
                                                                                    ontology_editor_gui: tuple[
                                                                                      QApplication,
                                                                                      QtWidgets.QDialog,
                                                                                      OntologyConfigurationForm,
                                                                                      QtBot],
                                                                                    ontology_doc_mock: ontology_doc_mock,
                                                                                    mocker):
    app, ui_dialog, ui_form, qtbot = ontology_editor_gui
    mock_show_message = mocker.patch("pasta_eln.ontology_configuration.ontology_configuration_extended.show_message")
    qtbot.mouseClick(ui_form.deleteTypePushButton, Qt.LeftButton)
    mock_show_message.assert_called_once_with("Load the ontology data first....")
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
    qtbot.mouseClick(ui_form.loadOntologyPushButton, Qt.LeftButton)
    current_selected_type = ui_form.typeComboBox.currentText()
    previous_types_count = ui_form.typeComboBox.count()
    qtbot.mouseClick(ui_form.deleteTypePushButton, Qt.LeftButton)
    assert (current_selected_type not in [ui_form.typeComboBox.itemText(i)
                                          for i in range(ui_form.typeComboBox.count())]), \
      f"Deleted type:{current_selected_type} should not exist in combo list!"
    assert (previous_types_count - 1 == ui_form.typeComboBox.count()), \
      f"Combo list should have {previous_types_count - 1} items!"
    assert ui_form.typeComboBox.currentText() == ontology_doc_mock.types_list()[1], \
      "Type combo box should be selected to second item"
    selected_type = ontology_doc_mock.types()[ui_form.typeComboBox.currentText()]
    assert ui_form.typeLabelLineEdit.text() == selected_type["label"], \
      "Type label line edit should be selected to second item"
    assert ui_form.typeLinkLineEdit.text() == selected_type["link"], \
      "Type label line edit should be selected to second item"
    assert ui_form.propsCategoryComboBox.currentText() == list(selected_type["prop"].keys())[0], \
      "Type label line edit should be selected to second item"
    self.check_table_contents(attachments_column_names, props_column_names, selected_type, ui_form)

  def test_component_add_selected_type_with_loaded_ontology_should_delete_and_update_ui(self,
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
    qtbot.mouseClick(ui_form.loadOntologyPushButton, Qt.LeftButton)
    current_selected_type = ui_form.typeComboBox.currentText()
    previous_types_count = ui_form.typeComboBox.count()
    qtbot.mouseClick(ui_form.deleteTypePushButton, Qt.LeftButton)
    assert (current_selected_type not in [ui_form.typeComboBox.itemText(i)
                                          for i in range(ui_form.typeComboBox.count())]), \
      f"Deleted type:{current_selected_type} should not exist in combo list!"
    assert (previous_types_count - 1 == ui_form.typeComboBox.count()), \
      f"Combo list should have {previous_types_count - 1} items!"
    assert ui_form.typeComboBox.currentText() == ontology_doc_mock.types_list()[1], \
      "Type combo box should be selected to second item"
    types = ontology_doc_mock.types()
    text = ui_form.typeComboBox.currentText()
    selected_type = types[text]
    assert ui_form.typeLabelLineEdit.text() == selected_type["label"], \
      "Type label line edit should be selected to second item"
    assert ui_form.typeLinkLineEdit.text() == selected_type["link"], \
      "Type Link line edit should be selected to second item"
    assert ui_form.propsCategoryComboBox.currentText() == list(selected_type["prop"].keys())[0], \
      "Type label line edit should be selected to second item"
    self.check_table_contents(attachments_column_names, props_column_names, selected_type, ui_form)
