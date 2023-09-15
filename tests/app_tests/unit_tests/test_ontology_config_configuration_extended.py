#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_configuration_extended.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest
from PySide6.QtWidgets import QApplication, QDialog

from pasta_eln.GUI.ontology_configuration.create_type_dialog_extended import CreateTypeDialog
from pasta_eln.GUI.ontology_configuration.delete_column_delegate import DeleteColumnDelegate
from pasta_eln.GUI.ontology_configuration.ontology_attachments_tableview_data_model import \
  OntologyAttachmentsTableViewModel
from pasta_eln.GUI.ontology_configuration.ontology_config_generic_exception import OntologyConfigGenericException
from pasta_eln.GUI.ontology_configuration.ontology_config_key_not_found_exception import \
  OntologyConfigKeyNotFoundException
from pasta_eln.GUI.ontology_configuration.ontology_configuration_extended import OntologyConfigurationForm, get_gui
from pasta_eln.GUI.ontology_configuration.ontology_document_null_exception import OntologyDocumentNullException
from pasta_eln.GUI.ontology_configuration.ontology_props_tableview_data_model import OntologyPropsTableViewModel
from pasta_eln.GUI.ontology_configuration.reorder_column_delegate import ReorderColumnDelegate
from pasta_eln.GUI.ontology_configuration.required_column_delegate import RequiredColumnDelegate
from pasta_eln.GUI.ontology_configuration.utility_functions import get_types_for_display, generate_empty_type
from tests.app_tests.common.fixtures import configuration_extended, ontology_doc_mock


class TestOntologyConfigConfiguration(object):

  def test_instantiation_should_succeed(self,
                                        mocker):
    mock_document = mocker.patch('cloudant.document.Document')
    mocker.patch('pasta_eln.GUI.ontology_configuration.create_type_dialog_extended.logging.getLogger')
    mocker.patch('pasta_eln.GUI.ontology_configuration.ontology_configuration.Ui_OntologyConfigurationBaseForm.setupUi')
    mocker.patch('pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.adjust_ontology_data_to_v3')
    mocker.patch.object(QDialog, '__new__')
    mocker.patch.object(OntologyPropsTableViewModel, '__new__')
    mocker.patch.object(OntologyAttachmentsTableViewModel, '__new__')
    mocker.patch.object(RequiredColumnDelegate, '__new__', lambda _: mocker.MagicMock())
    mocker.patch.object(DeleteColumnDelegate, '__new__', lambda _: mocker.MagicMock())
    mocker.patch.object(ReorderColumnDelegate, '__new__', lambda _: mocker.MagicMock())
    mocker.patch.object(OntologyConfigurationForm, 'typePropsTableView', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'typeAttachmentsTableView', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'addPropsRowPushButton', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'addAttachmentPushButton', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'saveOntologyPushButton', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'addPropsCategoryPushButton', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'deletePropsCategoryPushButton', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'deleteTypePushButton', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'addTypePushButton', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'cancelPushButton', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'typeComboBox', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'propsCategoryComboBox', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'typeLabelLineEdit', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'typeIriLineEdit', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'delete_column_delegate_props_table', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'reorder_column_delegate_props_table', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'delete_column_delegate_attach_table', create=True)
    mocker.patch.object(OntologyConfigurationForm, 'reorder_column_delegate_attach_table', create=True)
    mocker.patch.object(CreateTypeDialog, '__new__')
    config_instance = OntologyConfigurationForm(mock_document)
    assert config_instance, "OntologyConfigurationForm should be created"

  def test_instantiation_with_null_document_should_throw_exception(self,
                                                                   mocker):
    mocker.patch('pasta_eln.GUI.ontology_configuration.create_type_dialog_extended.logging.getLogger')
    mocker.patch('pasta_eln.GUI.ontology_configuration.ontology_configuration.Ui_OntologyConfigurationBaseForm.setupUi')
    mocker.patch('pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.adjust_ontology_data_to_v3')
    mocker.patch.object(QDialog, '__new__')
    with pytest.raises(OntologyDocumentNullException, match="Null document passed for ontology data"):
      OntologyConfigurationForm(None)

  @pytest.mark.parametrize("new_type_selected, mock_ontology_types", [
    ("x0", {
      "x0": {
        "label": "x0",
        "IRI": "url",
        "prop": {
          "default": [
            {
              "key": "key",
              "value": "value"}
          ],
          "category1": [
            {
              "key": "key",
              "value": "value"
            }
          ]
        },
        "attachments": []
      },
      "x1": {
        "label": "x0",
        "IRI": "url",
        "prop": {
          "default": [
            {
              "key": "key",
              "value": "value"}
          ],
          "category1": [
            {
              "key": "key",
              "value": "value"
            }
          ]
        },
        "attachments": []
      }
    }),
    ("x1", {
      "x0": {
        "label": "x0",
        "IRI": "url",
        "prop": {
          "default": [
            {
              "key": "key",
              "value": "value"}
          ],
          "category1": [
            {
              "key": "key",
              "value": "value"
            }
          ]
        },
        "attachments": []
      },
      "x1": {
        "label": "x0",
        "IRI": "url",
        "prop": {
          "default": [
            {
              "key": "key",
              "value": "value"}
          ],
          "category1": [
            {
              "key": "key",
              "value": "value"
            }
          ]
        },
        "attachments": []
      }
    }),
    (None, {}),
    ("x0", {}),
    ("x0", {"x1": {}}),
    ("x0", {"x0": {}}),
    ("x0", {"x0": {"label": None, "IRI": None, "prop": None, "attachments": None}}),
    ("x0", {"x0": {"label": None, "IRI": None, "prop": {"": None}, "attachments": [{"": None}]}}),
    ("x0", {"x0": {"": None, "§": None, "props": {"": None}, "attachment": [{"": None}]}})
  ])
  def test_type_combo_box_changed_should_do_expected(self,
                                                     mocker,
                                                     configuration_extended: configuration_extended,
                                                     new_type_selected,
                                                     mock_ontology_types):
    logger_info_spy = mocker.spy(configuration_extended.logger, 'info')
    mocker.patch.object(configuration_extended, 'addPropsCategoryLineEdit', create=True)
    mocker.patch.object(configuration_extended, 'ontology_types', mock_ontology_types, create=True)
    mocker.patch.object(configuration_extended, 'typeLabelLineEdit', create=True)
    mocker.patch.object(configuration_extended, 'typeIriLineEdit', create=True)
    mocker.patch.object(configuration_extended, 'attachments_table_data_model', create=True)
    mocker.patch.object(configuration_extended, 'propsCategoryComboBox', create=True)
    set_text_label_line_edit_spy = mocker.spy(configuration_extended.typeLabelLineEdit, 'setText')
    set_text_iri_line_edit_spy = mocker.spy(configuration_extended.typeIriLineEdit, 'setText')
    set_current_index_category_combo_box_spy = mocker.spy(configuration_extended.propsCategoryComboBox,
                                                          'setCurrentIndex')
    clear_add_props_category_line_edit_spy = mocker.spy(configuration_extended.addPropsCategoryLineEdit, 'clear')
    clear_category_combo_box_spy = mocker.spy(configuration_extended.propsCategoryComboBox, 'clear')
    add_items_category_combo_box_spy = mocker.spy(configuration_extended.propsCategoryComboBox, 'addItems')
    update_attachment_table_model_spy = mocker.spy(configuration_extended.attachments_table_data_model, 'update')
    if mock_ontology_types is not None and len(
        mock_ontology_types) > 0 and new_type_selected not in mock_ontology_types:
      with pytest.raises(OntologyConfigKeyNotFoundException,
                         match=f"Key {new_type_selected} not found in ontology_types"):
        assert configuration_extended.type_combo_box_changed(
          new_type_selected) is not None, "Nothing should be returned"

    if (mock_ontology_types
        and new_type_selected
        and new_type_selected in mock_ontology_types):
      assert configuration_extended.type_combo_box_changed(new_type_selected) is None, "Nothing should be returned"
      logger_info_spy.assert_called_once_with("New type selected in UI: {%s}", new_type_selected)
      clear_add_props_category_line_edit_spy.assert_called_once_with()
      set_text_label_line_edit_spy.assert_called_once_with(mock_ontology_types.get(new_type_selected).get('label'))
      set_text_iri_line_edit_spy.assert_called_once_with(mock_ontology_types.get(new_type_selected).get('IRI'))
      set_current_index_category_combo_box_spy.assert_called_once_with(0)
      clear_category_combo_box_spy.assert_called_once_with()
      add_items_category_combo_box_spy.assert_called_once_with(
        list(mock_ontology_types.get(new_type_selected).get('prop').keys())
        if mock_ontology_types.get(new_type_selected).get('prop') else [])
      update_attachment_table_model_spy.assert_called_once_with(
        mock_ontology_types.get(new_type_selected).get('attachments'))

  @pytest.mark.parametrize("new_selected_prop_category, selected_type_props", [
    (None, {}),
    ("default", {}),
    ("default", {"default": [], "category1": [], "category2": []}),
    ("category1", {"default": [], "category1": [], "category2": []}),
    ("default", {"default": [], "category1": [], "category2": []}),
    ("category1", {"default": [], "category1": [], "category2": []}),
    ("category2", {"default": [], "category1": [], "category2": []}),
    ("category2", {"default": [], "category1": [{"name": "key", "value": "value"}], "category2": []}),
    ("category1", {"default": [], "category1": [{"name": None, "value": None}], "category2": None}),
    ("category2", {"default": [], "category1": [{"name": None, "value": None}], "category2": None}),
    ("category3", {"default": [], "category1": [], "category2": []}),
  ])
  def test_type_category_combo_box_changed_should_do_expected(self,
                                                              mocker,
                                                              configuration_extended: configuration_extended,
                                                              new_selected_prop_category,
                                                              selected_type_props):
    logger_info_spy = mocker.spy(configuration_extended.logger, 'info')
    mocker.patch.object(configuration_extended, 'selected_type_properties', selected_type_props, create=True)
    mocker.patch.object(configuration_extended, 'props_table_data_model', create=True)
    update_props_table_model_spy = mocker.spy(configuration_extended.props_table_data_model, 'update')
    assert configuration_extended.category_combo_box_changed(
      new_selected_prop_category) is None, "Nothing should be returned"
    logger_info_spy.assert_called_once_with("New property category selected in UI: {%s}", new_selected_prop_category)
    if new_selected_prop_category and selected_type_props:
      update_props_table_model_spy.assert_called_once_with(selected_type_props.get(new_selected_prop_category))

  @pytest.mark.parametrize("new_category, ontology_types, selected_type_properties", [
    (None, None, {}),
    ("default", None, {}),
    (None, {0: "x0"}, {"default": [], "category1": [], "category2": []}),
    ("default", {0: "x0"}, {"default": [], "category1": [], "category2": []}),
    ("category1", {0: "x0"}, {"default": [], "category1": [], "category2": []}),
    ("default", {0: "x0"}, {"default": [], "category1": [], "category2": []}),
    ("category1", {0: "x0"}, {"default": [], "category1": [], "category2": []}),
    ("category2", {0: "x0"}, {"default": [], "category1": [], "category2": []}),
    ("category2", {0: "x0"}, {"default": [], "category1": [{"name": "key", "value": "value"}], "category2": []}),
    ("category1", {0: "x0"}, {"default": [], "category1": [{"name": None, "value": None}], "category2": None}),
    ("category2", {0: "x0"}, {"default": [], "category1": [{"name": None, "value": None}], "category2": None}),
    ("category3", {0: "x0"}, {"default": [], "category1": [], "category2": []}),
  ])
  def test_add_new_prop_category_should_do_expected(self,
                                                    mocker,
                                                    configuration_extended: configuration_extended,
                                                    new_category,
                                                    ontology_types,
                                                    selected_type_properties):
    logger_info_spy = mocker.spy(configuration_extended.logger, 'info')
    mocker.patch.object(configuration_extended, 'addPropsCategoryLineEdit', create=True)
    mocker.patch.object(configuration_extended.addPropsCategoryLineEdit, 'text', return_value=new_category)
    mocker.patch.object(configuration_extended, 'ontology_types', ontology_types, create=True)
    mocker.patch.object(configuration_extended, 'propsCategoryComboBox', create=True)
    mocker.patch.object(configuration_extended, 'ontology_loaded', create=True)
    add_items_selected_spy = mocker.spy(configuration_extended.propsCategoryComboBox, 'addItems')
    clear_category_combo_box_spy = mocker.spy(configuration_extended.propsCategoryComboBox, 'clear')
    set_current_index_category_combo_box_spy = mocker.spy(configuration_extended.propsCategoryComboBox,
                                                          'setCurrentIndex')
    mocker.patch.object(configuration_extended, 'selected_type_properties', create=True)
    configuration_extended.selected_type_properties.__setitem__.side_effect = selected_type_properties.__setitem__
    configuration_extended.selected_type_properties.__getitem__.side_effect = selected_type_properties.__getitem__
    configuration_extended.selected_type_properties.__iter__.side_effect = selected_type_properties.__iter__
    configuration_extended.selected_type_properties.keys.side_effect = selected_type_properties.keys
    set_items_selected_spy = mocker.spy(configuration_extended.selected_type_properties, '__setitem__')
    mocker.patch('pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.len',
                 lambda x: len(selected_type_properties.keys()))
    mock_show_message = mocker.patch(
      'pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.show_message')

    if not new_category:
      assert configuration_extended.add_new_prop_category() is None, "Nothing should be returned"
      mock_show_message.assert_called_once_with("Enter non-null/valid category name!!.....")
      return
    if not ontology_types:
      assert configuration_extended.add_new_prop_category() is None, "Nothing should be returned"
      mock_show_message.assert_called_once_with("Load the ontology data first....")
      return

    if new_category in selected_type_properties:
      assert configuration_extended.add_new_prop_category() is None, "Nothing should be returned"
      mock_show_message.assert_called_once_with("Category already exists....")
    else:
      if new_category:
        assert configuration_extended.add_new_prop_category() is None, "Nothing should be returned"
        logger_info_spy.assert_called_once_with("User added new category: {%s}", new_category)
        set_items_selected_spy.assert_called_once_with(new_category, [])
        set_current_index_category_combo_box_spy.assert_called_once_with(len(selected_type_properties.keys()) - 1)
        clear_category_combo_box_spy.assert_called_once_with()
        add_items_selected_spy.assert_called_once_with(
          list(selected_type_properties.keys())
        )
      else:
        assert configuration_extended.add_new_prop_category() is None, "Nothing should be returned"
        mock_show_message.assert_called_once_with("Enter non-null/valid category name!!.....")

  @pytest.mark.parametrize("selected_category, selected_type_properties", [
    (None, {}),
    ("default", {}),
    ("default", None),
    (None, {"default": [], "category1": [], "category2": []}),
    ("default", {"default": [], "category1": [], "category2": []}),
    ("category1", {"default": [], "category1": [], "category2": []}),
    ("default", {"default": [], "category1": [], "category2": []}),
    ("category1", {"default": [], "category1": [], "category2": []}),
    ("category2", {"default": [], "category1": [], "category2": []}),
    ("category2", {"default": [], "category1": [{"name": "key", "value": "value"}], "category2": []}),
    ("category1", {"default": [], "category1": [{"name": None, "value": None}], "category2": None}),
    ("category2", {"default": [], "category1": [{"name": None, "value": None}], "category2": None}),
    ("category3", {"default": [], "category1": [], "category2": []}),
  ])
  def test_delete_selected_category_should_do_expected(self,
                                                       mocker,
                                                       configuration_extended: configuration_extended,
                                                       selected_category,
                                                       selected_type_properties):
    logger_info_spy = mocker.spy(configuration_extended.logger, 'info')
    mocker.patch.object(configuration_extended, 'propsCategoryComboBox', create=True)
    current_text_category_combo_box_spy = mocker.patch.object(configuration_extended.propsCategoryComboBox,
                                                              'currentText', return_value=selected_category)
    add_items_selected_spy = mocker.spy(configuration_extended.propsCategoryComboBox, 'addItems')
    clear_category_combo_box_spy = mocker.spy(configuration_extended.propsCategoryComboBox, 'clear')
    set_current_index_category_combo_box_spy = mocker.spy(configuration_extended.propsCategoryComboBox,
                                                          'setCurrentIndex')
    mocker.patch.object(configuration_extended, 'selected_type_properties', create=True)
    mock_show_message = mocker.patch(
      "pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.show_message")
    if selected_type_properties:
      configuration_extended.selected_type_properties.__setitem__.side_effect = selected_type_properties.__setitem__
      configuration_extended.selected_type_properties.__getitem__.side_effect = selected_type_properties.__getitem__
      configuration_extended.selected_type_properties.pop.side_effect = selected_type_properties.pop
      configuration_extended.selected_type_properties.keys.side_effect = selected_type_properties.keys
    pop_items_selected_spy = mocker.spy(configuration_extended.selected_type_properties, 'pop')
    mocker.patch('pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.len',
                 lambda x: len(selected_type_properties.keys()))

    if selected_type_properties is None:
      mocker.patch.object(configuration_extended, 'selected_type_properties', None)
      assert configuration_extended.delete_selected_prop_category() is None, "Nothing should be returned"
      mock_show_message.assert_called_once_with("Load the ontology data first....")
      return
    if selected_type_properties and selected_category in selected_type_properties:
      assert configuration_extended.delete_selected_prop_category() is None, "Nothing should be returned"
      current_text_category_combo_box_spy.assert_called_once_with()
      logger_info_spy.assert_called_once_with("User deleted the selected category: {%s}", selected_category)
      pop_items_selected_spy.assert_called_once_with(selected_category)
      clear_category_combo_box_spy.assert_called_once_with()
      add_items_selected_spy.assert_called_once_with(
        list(selected_type_properties.keys())
      )
      set_current_index_category_combo_box_spy.assert_called_once_with(len(selected_type_properties.keys()) - 1)

  @pytest.mark.parametrize("modified_type_label, current_type, ontology_types", [
    (None, None, None),
    ("new_label_1", None, None),
    (None, "x0", {"x0": {"label": "x0"}, "x1": {"label": "x1"}}),
    ("new_label_2", "x1", {"x0": {"label": "x0"}, "x1": {"label": "x1"}}),
    ("new_label_2", "instrument", {"x0": {"label": "x0"}, "instrument": {"label": "x1"}}),
    ("type_new_label", "subtask4", {"x0": {"label": "x0"}, "subtask5": {"label": "x1"}}),
  ])
  def test_update_structure_label_should_do_expected(self,
                                                     mocker,
                                                     configuration_extended: configuration_extended,
                                                     modified_type_label,
                                                     current_type,
                                                     ontology_types):
    mocker.patch.object(configuration_extended, 'typeComboBox', create=True)
    mocker.patch.object(configuration_extended.typeComboBox, 'currentText', return_value=current_type)

    mocker.patch.object(configuration_extended, 'ontology_types', create=True)
    if ontology_types:
      configuration_extended.ontology_types.__setitem__.side_effect = ontology_types.__setitem__
      configuration_extended.ontology_types.__getitem__.side_effect = ontology_types.__getitem__
      configuration_extended.ontology_types.__iter__.side_effect = ontology_types.__iter__
      configuration_extended.ontology_types.__contains__.side_effect = ontology_types.__contains__
      configuration_extended.ontology_types.get.side_effect = ontology_types.get
      configuration_extended.ontology_types.keys.side_effect = ontology_types.keys

    get_ontology_types_spy = mocker.spy(configuration_extended.ontology_types, 'get')

    if modified_type_label:
      assert configuration_extended.update_type_label(modified_type_label) is None, "Nothing should be returned"
      if ontology_types is not None and current_type in ontology_types:
        get_ontology_types_spy.assert_called_once_with(current_type)
        assert ontology_types[current_type]["label"] == modified_type_label

  @pytest.mark.parametrize("modified_type_iri, current_type, ontology_types", [
    (None, None, None),
    ("new_url", None, None),
    (None, "x0", {"x0": {"label": "x0"}, "x1": {"label": "x1"}}),
    ("new_url_2", "x1", {"x0": {"label": "x0"}, "x1": {"label": "x1"}}),
    ("new_url_2", "instrument", {"x0": {"label": "x0"}, "instrument": {"label": "x1"}}),
    ("type_new_url", "subtask4", {"x0": {"label": "x0"}, "subtask5": {"label": "x1"}}),
  ])
  def test_update_type_iri_should_do_expected(self,
                                              mocker,
                                              configuration_extended: configuration_extended,
                                              modified_type_iri,
                                              current_type,
                                              ontology_types):
    mocker.patch.object(configuration_extended, 'typeComboBox', create=True)
    mocker.patch.object(configuration_extended.typeComboBox, 'currentText', return_value=current_type)

    mocker.patch.object(configuration_extended, 'ontology_types', create=True)
    if ontology_types:
      configuration_extended.ontology_types.__setitem__.side_effect = ontology_types.__setitem__
      configuration_extended.ontology_types.__getitem__.side_effect = ontology_types.__getitem__
      configuration_extended.ontology_types.__iter__.side_effect = ontology_types.__iter__
      configuration_extended.ontology_types.__contains__.side_effect = ontology_types.__contains__
      configuration_extended.ontology_types.get.side_effect = ontology_types.get
      configuration_extended.ontology_types.keys.side_effect = ontology_types.keys

    get_ontology_types_spy = mocker.spy(configuration_extended.ontology_types, 'get')

    if modified_type_iri:
      assert configuration_extended.update_type_iri(modified_type_iri) is None, "Nothing should be returned"
      if ontology_types is not None and current_type in ontology_types:
        get_ontology_types_spy.assert_called_once_with(current_type)
        assert ontology_types[current_type]["IRI"] == modified_type_iri

  @pytest.mark.parametrize("selected_type, ontology_types, ontology_document", [
    (None, None, None),
    ("x0", None, None),
    (None, {"x0": {"IRI": "x0"}, "x1": {"IRI": "x1"}}, {"x0": {"IRI": "x0"}, "x1": {"IRI": "x1"}}),
    ("x3", {"x0": {"IRI": "x0"}, "x1": {"IRI": "x1"}}, {"x0": {"IRI": "x0"}, "x1": {"IRI": "x1"}}),
    ("instrument", {"x0": {"IRI": "x0"}, "instrument": {"IRI": "x1"}},
     {"x0": {"IRI": "x0"}, "instrument": {"IRI": "x1"}}),
    (
        "subtask5", {"x0": {"IRI": "x0"}, "subtask5": {"IRI": "x1"}},
        {"x0": {"IRI": "x0"}, "subtask5": {"IRI": "x1"}}),
    ("x0", {"x0": {"IRI": "x0"}, "subtask5": {"IRI": "x1"}}, {"subtask5": {"IRI": "x1"}}),
    ("x0", {"subtask5": {"IRI": "x1"}}, {"x0": {"IRI": "x0"}, "subtask5": {"IRI": "x1"}}),
  ])
  def test_delete_selected_type_should_do_expected(self,
                                                   mocker,
                                                   configuration_extended: configuration_extended,
                                                   selected_type,
                                                   ontology_types,
                                                   ontology_document):
    mocker.patch.object(configuration_extended, 'typeComboBox', create=True)
    mocker.patch.object(configuration_extended.typeComboBox, 'currentText', return_value=selected_type)

    mocker.patch.object(configuration_extended, 'ontology_types', create=True)
    mocker.patch.object(configuration_extended, 'ontology_document', create=True)
    clear_category_combo_box_spy = mocker.spy(configuration_extended.typeComboBox, 'clear')
    set_current_index_category_combo_box_spy = mocker.spy(configuration_extended.typeComboBox, 'setCurrentIndex')
    add_items_selected_spy = mocker.spy(configuration_extended.typeComboBox, 'addItems')
    logger_info_spy = mocker.spy(configuration_extended.logger, 'info')
    mock_show_message = mocker.patch(
      "pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.show_message")
    mocker.patch.object(configuration_extended, 'ontology_loaded', True, create=True)
    if ontology_document:
      original_ontology_document = ontology_document.copy()
      configuration_extended.ontology_document.__setitem__.side_effect = ontology_document.__setitem__
      configuration_extended.ontology_document.__getitem__.side_effect = ontology_document.__getitem__
      configuration_extended.ontology_document.__iter__.side_effect = ontology_document.__iter__
      configuration_extended.ontology_document.__contains__.side_effect = ontology_document.__contains__
      configuration_extended.ontology_document.get.side_effect = ontology_document.get
      configuration_extended.ontology_document.keys.side_effect = ontology_document.keys
      configuration_extended.ontology_document.pop.side_effect = ontology_document.pop
    pop_items_selected_ontology_document_spy = mocker.spy(configuration_extended.ontology_document, 'pop')
    if ontology_types:
      original_ontology_types = ontology_types.copy()
      configuration_extended.ontology_types.__setitem__.side_effect = ontology_types.__setitem__
      configuration_extended.ontology_types.__getitem__.side_effect = ontology_types.__getitem__
      configuration_extended.ontology_types.__iter__.side_effect = ontology_types.__iter__
      configuration_extended.ontology_types.__contains__.side_effect = ontology_types.__contains__
      configuration_extended.ontology_types.get.side_effect = ontology_types.get
      configuration_extended.ontology_types.keys.side_effect = ontology_types.keys
      configuration_extended.ontology_types.pop.side_effect = ontology_types.pop
    pop_items_selected_ontology_types_spy = mocker.spy(configuration_extended.ontology_types, 'pop')

    if ontology_document is None or ontology_types is None:
      mocker.patch.object(configuration_extended, 'ontology_types', ontology_types)
      mocker.patch.object(configuration_extended, 'ontology_document', ontology_document)
      assert configuration_extended.delete_selected_type() is None, "Nothing should be returned"
      mock_show_message.assert_called_once_with("Load the ontology data first....")
      return
    if selected_type:
      assert configuration_extended.delete_selected_type() is None, "Nothing should be returned"
      if selected_type and selected_type in original_ontology_types and selected_type in original_ontology_document:
        logger_info_spy.assert_called_once_with("User deleted the selected type: {%s}", selected_type)
        pop_items_selected_ontology_types_spy.assert_called_once_with(selected_type)
        pop_items_selected_ontology_document_spy.assert_called_once_with(selected_type)
        clear_category_combo_box_spy.assert_called_once_with()
        add_items_selected_spy.assert_called_once_with(
          get_types_for_display(ontology_types.keys())
        )
        set_current_index_category_combo_box_spy.assert_called_once_with(0)
        assert selected_type not in ontology_types and ontology_document, "selected_type should be deleted"
      else:
        logger_info_spy.assert_not_called()
        logger_info_spy.assert_not_called()
        pop_items_selected_ontology_types_spy.assert_not_called()
        pop_items_selected_ontology_document_spy.assert_not_called()
        clear_category_combo_box_spy.assert_not_called()
        add_items_selected_spy.assert_not_called()
        set_current_index_category_combo_box_spy.assert_not_called()

  @pytest.mark.parametrize("new_title, new_label, is_structure_level", [
    (None, None, False),
    ("x0", None, True),
    (None, "x2", True),
    ("x3", "x3", True),
    ("instrument", "new Instrument", False)
  ])
  def test_create_type_accepted_callback_should_do_expected(self,
                                                            mocker,
                                                            configuration_extended: configuration_extended,
                                                            new_title,
                                                            new_label,
                                                            is_structure_level):
    mocker.patch.object(configuration_extended, 'create_type_dialog', create=True)
    mocker.patch.object(configuration_extended.create_type_dialog, 'titleLineEdit', create=True)
    mocker.patch.object(configuration_extended.create_type_dialog, 'next_struct_level', new_title, create=True)
    mock_check_box = mocker.patch.object(configuration_extended.create_type_dialog, 'structuralLevelCheckBox',
                                         create=True)
    mocker.patch.object(mock_check_box, 'isChecked', return_value=is_structure_level, create=True)
    mocker.patch.object(configuration_extended.create_type_dialog.titleLineEdit, 'text', return_value=new_title)
    mocker.patch.object(configuration_extended.create_type_dialog, 'labelLineEdit', create=True)
    mocker.patch.object(configuration_extended.create_type_dialog.labelLineEdit, 'text', return_value=new_label)
    clear_ui_spy = mocker.patch.object(configuration_extended.create_type_dialog, 'clear_ui', create=True)
    create_new_type_spy = mocker.patch.object(configuration_extended, 'create_new_type', create=True)
    text_title_line_edit_text_spy = mocker.spy(configuration_extended.create_type_dialog.titleLineEdit, 'text')
    text_label_line_edit_text_spy = mocker.spy(configuration_extended.create_type_dialog.labelLineEdit, 'text')

    assert configuration_extended.create_type_accepted_callback() is None, "Nothing should be returned"
    if not is_structure_level:
      text_title_line_edit_text_spy.assert_called_once_with()
    text_label_line_edit_text_spy.assert_called_once_with()
    clear_ui_spy.assert_called_once_with()
    create_new_type_spy.assert_called_once_with(
      new_title, new_label
    )

  def test_create_type_rejected_callback_should_do_expected(self,
                                                            mocker,
                                                            configuration_extended: configuration_extended):
    mocker.patch.object(configuration_extended, 'create_type_dialog', create=True)
    clear_ui_spy = mocker.patch.object(configuration_extended.create_type_dialog, 'clear_ui', create=True)
    assert configuration_extended.create_type_rejected_callback() is None, "Nothing should be returned"
    clear_ui_spy.assert_called_once_with()

  @pytest.mark.parametrize("new_structural_title, ontology_types", [
    (None, None),
    ("x0", None),
    (None, {"x0": {"IRI": "x0"}, "x1": {"IRI": "x1"}}),
    ("x3", {"x0": {"IRI": "x0"}, "x1": {"IRI": "x1"}}),
    ("x7", {"x0": {"IRI": "x0"}, "instrument": {"IRI": "x1"}}),
    ("x6", {"x0": {"IRI": "x0"}, "subtask5": {"IRI": "x1"}})
  ])
  def test_show_create_type_dialog_should_do_expected(self,
                                                      mocker,
                                                      configuration_extended: configuration_extended,
                                                      new_structural_title,
                                                      ontology_types):
    mocker.patch.object(configuration_extended, 'create_type_dialog', create=True)
    mocker.patch.object(configuration_extended, 'ontology_types', create=True)
    set_structural_level_title_spy = mocker.patch.object(configuration_extended.create_type_dialog,
                                                         'set_structural_level_title', create=True)
    mocker.patch.object(configuration_extended, 'ontology_loaded', create=True)
    show_create_type_dialog_spy = mocker.patch.object(configuration_extended.create_type_dialog, 'show', create=True)
    show_message_spy = mocker.patch('pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.show_message')
    get_next_possible_structural_level_label_spy = mocker.patch(
      'pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.get_next_possible_structural_level_label',
      return_value=new_structural_title)
    if ontology_types is not None:
      configuration_extended.ontology_types.__setitem__.side_effect = ontology_types.__setitem__
      configuration_extended.ontology_types.__getitem__.side_effect = ontology_types.__getitem__
      configuration_extended.ontology_types.__iter__.side_effect = ontology_types.__iter__
      configuration_extended.ontology_types.__contains__.side_effect = ontology_types.__contains__
      configuration_extended.ontology_types.get.side_effect = ontology_types.get
      configuration_extended.ontology_types.keys.side_effect = ontology_types.keys
      configuration_extended.ontology_types.pop.side_effect = ontology_types.pop
    else:
      mocker.patch.object(configuration_extended, 'ontology_types', None)

    assert configuration_extended.show_create_type_dialog() is None, "Nothing should be returned"
    if ontology_types is not None:
      get_next_possible_structural_level_label_spy.assert_called_once_with(ontology_types.keys())
      set_structural_level_title_spy.assert_called_once_with(new_structural_title)
      show_create_type_dialog_spy.assert_called_once_with()
    else:
      show_message_spy.assert_called_once_with("Load the ontology data first...")
      get_next_possible_structural_level_label_spy.assert_not_called()
      set_structural_level_title_spy.assert_not_called()
      show_create_type_dialog_spy.assert_not_called()

  def test_initialize_should_setup_slots_and_should_do_expected(self,
                                                                configuration_extended: configuration_extended):
    configuration_extended.logger.info.assert_any_call("Setting up slots for the editor..")
    configuration_extended.logger.info.assert_any_call("User loaded the ontology data in UI")
    configuration_extended.addPropsRowPushButton.clicked.connect.assert_called_once_with(
      configuration_extended.props_table_data_model.add_data_row)
    configuration_extended.addAttachmentPushButton.clicked.connect.assert_called_once_with(
      configuration_extended.attachments_table_data_model.add_data_row)
    configuration_extended.saveOntologyPushButton.clicked.connect.assert_called_once_with(
      configuration_extended.save_ontology)
    configuration_extended.addPropsCategoryPushButton.clicked.connect.assert_called_once_with(
      configuration_extended.add_new_prop_category)
    configuration_extended.deletePropsCategoryPushButton.clicked.connect.assert_called_once_with(
      configuration_extended.delete_selected_prop_category)
    configuration_extended.deleteTypePushButton.clicked.connect.assert_called_once_with(
      configuration_extended.delete_selected_type)
    configuration_extended.addTypePushButton.clicked.connect.assert_called_once_with(
      configuration_extended.show_create_type_dialog)

    # Slots for the combo-boxes
    configuration_extended.typeComboBox.currentTextChanged.connect.assert_called_once_with(
      configuration_extended.type_combo_box_changed)
    configuration_extended.propsCategoryComboBox.currentTextChanged.connect.assert_called_once_with(
      configuration_extended.category_combo_box_changed)

    # Slots for line edits
    configuration_extended.typeLabelLineEdit.textChanged[str].connect.assert_called_once_with(
      configuration_extended.update_type_label)
    configuration_extended.typeIriLineEdit.textChanged[str].connect.assert_called_once_with(
      configuration_extended.update_type_iri)

    # Slots for the delegates
    configuration_extended.delete_column_delegate_props_table.delete_clicked_signal.connect.assert_called_once_with(
      configuration_extended.props_table_data_model.delete_data)
    configuration_extended.reorder_column_delegate_props_table.re_order_signal.connect.assert_called_once_with(
      configuration_extended.props_table_data_model.re_order_data)

    configuration_extended.delete_column_delegate_attach_table.delete_clicked_signal.connect.assert_called_once_with(
      configuration_extended.attachments_table_data_model.delete_data)
    configuration_extended.reorder_column_delegate_attach_table.re_order_signal.connect.assert_called_once_with(
      configuration_extended.attachments_table_data_model.re_order_data)

  @pytest.mark.parametrize("ontology_document", [
    'ontology_doc_mock',
    None,
    {"x0": {"IRI": "x0"}, "": {"IRI": "x1"}},
    {"x0": {"IRI": "x0"}, "": {"IRI": "x1"}, 23: "test", "__id": "test"},
    {"test": ["test1", "test2", "test3"]}
  ])
  def test_load_ontology_data_should_with_variant_types_of_doc_should_do_expected(self,
                                                                                  mocker,
                                                                                  ontology_document,
                                                                                  configuration_extended: configuration_extended,
                                                                                  request):
    doc = request.getfixturevalue(ontology_document) \
      if ontology_document and type(ontology_document) is str \
      else ontology_document
    mocker.patch.object(configuration_extended, 'ontology_document', doc, create=True)
    if ontology_document is None:
      with pytest.raises(OntologyConfigGenericException, match="Null ontology_document, erroneous app state"):
        assert configuration_extended.load_ontology_data() is None, "Nothing should be returned"
      return
    assert configuration_extended.load_ontology_data() is None, "Nothing should be returned"
    assert configuration_extended.typeComboBox.clear.call_count == 2, "Clear should be called twice"
    assert configuration_extended.typeComboBox.addItems.call_count == 2, "addItems should be called twice"
    configuration_extended.typeComboBox.addItems.assert_called_with(
      get_types_for_display(configuration_extended.ontology_types.keys()))
    assert configuration_extended.typeComboBox.setCurrentIndex.call_count == 2, "setCurrentIndex should be called twice"
    configuration_extended.typeComboBox.setCurrentIndex.assert_called_with(0)
    for data in ontology_document:
      if type(data) is dict:
        assert data in configuration_extended.ontology_types, "Data should be loaded"

  @pytest.mark.parametrize("ontology_document", [
    'ontology_doc_mock',
    None,
    {"x0": {"IRI": "x0"}, "": {"IRI": "x1"}},
    {"x0": {"IRI": "x0"}, "": {"IRI": "x1"}, 23: "test", "__id": "test"},
    {"test": ["test1", "test2", "test3"]}
  ])
  def test_save_ontology_should_do_expected(self,
                                            mocker,
                                            ontology_document,
                                            configuration_extended: configuration_extended,
                                            request):
    doc = request.getfixturevalue(ontology_document) \
      if ontology_document and type(ontology_document) is str \
      else ontology_document
    mocker.patch.object(configuration_extended, 'ontology_document', create=True)
    if doc:
      configuration_extended.ontology_document.__setitem__.side_effect = doc.__setitem__
      configuration_extended.ontology_document.__getitem__.side_effect = doc.__getitem__
      configuration_extended.ontology_document.__iter__.side_effect = doc.__iter__
      configuration_extended.ontology_document.__contains__.side_effect = doc.__contains__

    mocker.patch.object(configuration_extended.logger, 'info')
    mock_show_message = mocker.patch(
      'pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.show_message')
    assert configuration_extended.save_ontology() is None, "Nothing should be returned"
    configuration_extended.logger.info.assert_called_once_with("User saved the ontology data document!!")
    configuration_extended.ontology_document.save.assert_called_once()
    mock_show_message.assert_called_once_with("Ontology data saved successfully..")

  @pytest.mark.parametrize("new_title, new_label, ontology_document, ontology_types", [
    (None, None, None, None),
    (None, None, {"x0": {"IRI": "x0"}, "x1": {"IRI": "x1"}}, {"x0": {"IRI": "x0"}, "x1": {"IRI": "x1"}}),
    ("x0", None, {"x0": {"IRI": "x0"}, "x1": {"IRI": "x1"}}, {"x0": {"IRI": "x0"}, "x1": {"IRI": "x1"}}),
    (None, "x1", {"x0": {"IRI": "x0"}, "x1": {"IRI": "x1"}}, {"x0": {"IRI": "x0"}, "x1": {"IRI": "x1"}}),
    ("x0", "x1", {"x0": {"IRI": "x0"}, "x1": {"IRI": "x1"}}, {"x0": {"IRI": "x0"}, "x1": {"IRI": "x1"}}),
    ("x0", "x1", None, None),
    ("instrument", "new Instrument", {"x0": {"IRI": "x0"}, "x1": {"IRI": "x1"}},
     {"x0": {"IRI": "x0"}, "x1": {"IRI": "x1"}})
  ])
  def test_create_new_type_should_do_expected(self,
                                              mocker,
                                              new_title,
                                              new_label,
                                              ontology_document,
                                              ontology_types,
                                              configuration_extended: configuration_extended):
    mocker.patch.object(configuration_extended, 'ontology_document', create=True)
    mocker.patch.object(configuration_extended, 'ontology_types', create=True)
    mock_show_message = mocker.patch(
      'pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.show_message')
    mock_log_info = mocker.patch.object(configuration_extended.logger, 'info')
    mock_log_error = mocker.patch.object(configuration_extended.logger, 'error')
    mock_log_warn = mocker.patch.object(configuration_extended.logger, 'warning')
    if ontology_document:
      configuration_extended.ontology_document.__setitem__.side_effect = ontology_document.__setitem__
      configuration_extended.ontology_document.__getitem__.side_effect = ontology_document.__getitem__
      configuration_extended.ontology_document.__iter__.side_effect = ontology_document.__iter__
      configuration_extended.ontology_document.__contains__.side_effect = ontology_document.__contains__
      configuration_extended.ontology_document.get.side_effect = ontology_document.get
      configuration_extended.ontology_document.keys.side_effect = ontology_document.keys
      configuration_extended.ontology_document.pop.side_effect = ontology_document.pop
    if ontology_types is not None:
      configuration_extended.ontology_types.__setitem__.side_effect = ontology_types.__setitem__
      configuration_extended.ontology_types.__getitem__.side_effect = ontology_types.__getitem__
      configuration_extended.ontology_types.__iter__.side_effect = ontology_types.__iter__
      configuration_extended.ontology_types.__contains__.side_effect = ontology_types.__contains__
      configuration_extended.ontology_types.get.side_effect = ontology_types.get
      configuration_extended.ontology_types.keys.side_effect = ontology_types.keys
      configuration_extended.ontology_types.pop.side_effect = ontology_types.pop
      configuration_extended.ontology_types.__len__.side_effect = ontology_types.__len__

    if ontology_document is None:
      mocker.patch.object(configuration_extended, 'ontology_document', None, create=True)
    if ontology_types is None:
      mocker.patch.object(configuration_extended, 'ontology_types', None, create=True)

    if ontology_document is None or ontology_types is None or new_title in ontology_document:
      if ontology_document is None or ontology_types is None:
        with pytest.raises(OntologyConfigGenericException,
                           match="Null ontology_document/ontology_types, erroneous app state"):
          assert configuration_extended.create_new_type(new_title, new_label) is None, "Nothing should be returned"
          mock_log_error.assert_called_once_with("Null ontology_document/ontology_types, erroneous app state")
      else:
        assert configuration_extended.create_new_type(new_title, new_label) is None, "Nothing should be returned"
        mock_show_message.assert_called_once_with(f"Type (title: {new_title} "
                                                  f"label: {new_label}) cannot be added "
                                                  f"since it exists in DB already....")
    else:
      if new_title is None:
        assert configuration_extended.create_new_type(None, new_label) is None, "Nothing should be returned"
        mock_show_message.assert_called_once_with("Enter non-null/valid title!!.....")
        mock_log_warn.assert_called_once_with("Enter non-null/valid title!!.....")
      else:
        assert configuration_extended.create_new_type(new_title, new_label) is None, "Nothing should be returned"
        mock_log_info.assert_called_once_with("User created a new type and added "
                                              "to the ontology document: Title: {%s}, Label: {%s}", new_title,
                                              new_label)

        (configuration_extended.ontology_document
         .__setitem__.assert_called_once_with(new_title, generate_empty_type(new_label)))
        (configuration_extended.ontology_types
         .__setitem__.assert_called_once_with(new_title, generate_empty_type(new_label)))
        assert configuration_extended.typeComboBox.clear.call_count == 2, "ComboBox should be cleared twice"
        assert configuration_extended.typeComboBox.addItems.call_count == 2, "ComboBox addItems should be called twice"
        configuration_extended.typeComboBox.addItems.assert_called_with(
          get_types_for_display(configuration_extended.ontology_types.keys()))
        mock_show_message.assert_called_once_with(f"Type (title: {new_title} label: {new_label}) has been added....")

  @pytest.mark.parametrize("instance_exists", [True, False])
  def test_get_gui_should_do_expected(self,
                                      mocker,
                                      configuration_extended: configuration_extended,
                                      instance_exists):
    mock_form = mocker.MagicMock()
    mock_sys_argv = mocker.patch(
      "pasta_eln.GUI.ontology_configuration.ontology_configuration_extended.sys.argv")
    mock_new_app_inst = mocker.patch("PySide6.QtWidgets.QApplication")
    mock_exist_app_inst = mocker.patch("PySide6.QtWidgets.QApplication")
    mock_form_instance = mocker.patch("PySide6.QtWidgets.QDialog")
    mock_document = mocker.patch("cloudant.document.Document")

    mocker.patch.object(QApplication, 'instance', return_value=mock_exist_app_inst if instance_exists else None)
    mocker.patch.object(mock_form, 'instance', mock_form_instance, create=True)
    spy_new_app_inst = mocker.patch.object(QApplication, '__new__', return_value=mock_new_app_inst)
    spy_form_inst = mocker.patch.object(OntologyConfigurationForm, '__new__', return_value=mock_form)

    (app, form_inst, form) = get_gui(mock_document)
    spy_form_inst.assert_called_once_with(OntologyConfigurationForm, mock_document)
    if instance_exists:
      assert app is mock_exist_app_inst, "Should return existing instance"
      assert form_inst is mock_form_instance, "Should return existing instance"
      assert form is mock_form, "Should return existing instance"
    else:
      spy_new_app_inst.assert_called_once_with(QApplication, mock_sys_argv)
      assert app is mock_new_app_inst, "Should return new instance"
      assert form_inst is mock_form_instance, "Should return existing instance"
      assert form is mock_form, "Should return existing instance"
