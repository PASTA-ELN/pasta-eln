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
from tests.app_tests.common.fixtures import ontology_editor_gui, ontology_doc_mock


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
                                                                 ontology_doc_mock: ontology_doc_mock):
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

    props_selected = selected_type["prop"][categories[0]]
    props_column_names = {
      0: "name",
      1: "query",
      2: "list",
      3: "link",
      4: "required",
      5: "unit"
    }

    # Assert if the properties are loaded in the table view
    model = ui_form.typePropsTableView.model()
    for row in range(model.rowCount()):
      prop = props_selected[row]
      for column in range(model.columnCount() - 2):
        index = model.index(row, column)
        if props_column_names[column] in prop:
          assert (model.data(index, Qt.DisplayRole)
                  == str(prop[props_column_names[column]])), f"{props_column_names[column]} not loaded!"
        else:
          assert model.data(index, Qt.DisplayRole) == "", f"{props_column_names[column]} should be null string!"

    attachments_selected = selected_type["attachments"]

    attachments_column_names = {
      0: "location",
      1: "link"
    }
    # Assert if the attachments are loaded in the table view
    model = ui_form.typeAttachmentsTableView.model()
    for row in range(model.rowCount()):
      prop = attachments_selected[row]
      for column in range(model.columnCount() - 2):
        index = model.index(row, column)
        if attachments_column_names[column] in prop:
          assert model.data(index, Qt.DisplayRole) == str(prop[attachments_column_names[column]]), \
            f"{attachments_column_names[column]} not loaded!"
        else:
          assert model.data(index, Qt.DisplayRole) == "", \
            f"{attachments_column_names[column]} should be null string!"
