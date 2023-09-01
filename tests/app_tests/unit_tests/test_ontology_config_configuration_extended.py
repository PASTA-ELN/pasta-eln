#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_configuration_extended.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.ontology_configuration.exceptions.ontology_config_generic_exception import OntologyConfigGenericException
from pasta_eln.ontology_configuration.exceptions.ontology_config_key_not_found_exception import \
  OntologyConfigKeyNotFoundException
from tests.app_tests.common.fixtures import configuration_extended


class TestOntologyConfigConfiguration(object):
  @pytest.mark.parametrize("new_type_selected, mock_ontology_types", [
    ("x0", {
      "x0": {
        "label": "x0",
        "link": "url",
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
        "link": "url",
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
        "link": "url",
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
        "link": "url",
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
    ("x0", {"x0": {"label": None, "link": None, "prop": None, "attachments": None}}),
    ("x0", {"x0": {"label": None, "link": None, "prop": {"": None}, "attachments": [{"": None}]}}),
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
    mocker.patch.object(configuration_extended, 'typeLinkLineEdit', create=True)
    mocker.patch.object(configuration_extended, 'attachments_table_data_model', create=True)
    mocker.patch.object(configuration_extended, 'propsCategoryComboBox', create=True)
    set_text_label_line_edit_spy = mocker.spy(configuration_extended.typeLabelLineEdit, 'setText')
    set_text_link_line_edit_spy = mocker.spy(configuration_extended.typeLinkLineEdit, 'setText')
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
      logger_info_spy.assert_called_once_with(f"New type selected in UI: {new_type_selected}")
      clear_add_props_category_line_edit_spy.assert_called_once_with()
      set_text_label_line_edit_spy.assert_called_once_with(mock_ontology_types.get(new_type_selected).get('label'))
      set_text_link_line_edit_spy.assert_called_once_with(mock_ontology_types.get(new_type_selected).get('link'))
      set_current_index_category_combo_box_spy.assert_called_once_with(0)
      clear_category_combo_box_spy.assert_called_once_with()
      add_items_category_combo_box_spy.assert_called_once_with(
        mock_ontology_types.get(new_type_selected).get('prop').keys()
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
    logger_info_spy.assert_called_once_with(f"New property category selected in UI: {new_selected_prop_category}")
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
    mocker.patch('pasta_eln.ontology_configuration.ontology_configuration_extended.len',
                 lambda x: len(selected_type_properties.keys()))
    mock_show_message = mocker.patch('pasta_eln.ontology_configuration.ontology_configuration_extended.show_message')

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
        logger_info_spy.assert_called_once_with(f"User added new category: {new_category}")
        set_items_selected_spy.assert_called_once_with(new_category, [])
        set_current_index_category_combo_box_spy.assert_called_once_with(len(selected_type_properties.keys()) - 1)
        clear_category_combo_box_spy.assert_called_once_with()
        add_items_selected_spy.assert_called_once_with(
          selected_type_properties.keys()
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
    if selected_type_properties:
      configuration_extended.selected_type_properties.__setitem__.side_effect = selected_type_properties.__setitem__
      configuration_extended.selected_type_properties.__getitem__.side_effect = selected_type_properties.__getitem__
      configuration_extended.selected_type_properties.pop.side_effect = selected_type_properties.pop
      configuration_extended.selected_type_properties.keys.side_effect = selected_type_properties.keys
    pop_items_selected_spy = mocker.spy(configuration_extended.selected_type_properties, 'pop')
    mocker.patch('pasta_eln.ontology_configuration.ontology_configuration_extended.len',
                 lambda x: len(selected_type_properties.keys()))

    if selected_type_properties is None:
      mocker.patch.object(configuration_extended, 'selected_type_properties', None)
      with pytest.raises(OntologyConfigGenericException, match="Null selected_type_properties, erroneous app state"):
        assert configuration_extended.delete_selected_prop_category() is None, "Nothing should be returned"
      return
    if not selected_type_properties and selected_category in selected_type_properties:
      assert configuration_extended.delete_selected_prop_category() is None, "Nothing should be returned"
      current_text_category_combo_box_spy.assert_called_once_with()
      logger_info_spy.assert_called_once_with(f"User deleted the selected category: {selected_category}")
      pop_items_selected_spy.assert_called_once_with(selected_category)
      clear_category_combo_box_spy.assert_called_once_with()
      add_items_selected_spy.assert_called_once_with(
        selected_type_properties.keys()
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
      configuration_extended.ontology_types.get.side_effect = ontology_types.get
      configuration_extended.ontology_types.keys.side_effect = ontology_types.keys

    get_ontology_types_spy = mocker.spy(configuration_extended.ontology_types, 'get')

    if modified_type_label:
      assert configuration_extended.update_structure_label(modified_type_label) is None, "Nothing should be returned"
      if ontology_types is not None and current_type in ontology_types:
        get_ontology_types_spy.assert_called_once_with(current_type)
        assert ontology_types[current_type]["label"] == modified_type_label

  @pytest.mark.parametrize("selected_type, ontology_types, ontology_document", [
    (None, None, None),
    ("x0", None, None),
    (None, {"x0": {"link": "x0"}, "x1": {"link": "x1"}}, {"x0": {"link": "x0"}, "x1": {"link": "x1"}}),
    ("x3", {"x0": {"link": "x0"}, "x1": {"link": "x1"}}, {"x0": {"link": "x0"}, "x1": {"link": "x1"}}),
    ("instrument", {"x0": {"link": "x0"}, "instrument": {"link": "x1"}},
     {"x0": {"link": "x0"}, "instrument": {"link": "x1"}}),
    (
        "subtask5", {"x0": {"link": "x0"}, "subtask5": {"link": "x1"}},
        {"x0": {"link": "x0"}, "subtask5": {"link": "x1"}}),
    ("x0", {"x0": {"link": "x0"}, "subtask5": {"link": "x1"}}, {"subtask5": {"link": "x1"}}),
    ("x0", {"subtask5": {"link": "x1"}}, {"x0": {"link": "x0"}, "subtask5": {"link": "x1"}}),
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
    if ontology_document:
      original_ontology_document = ontology_document.copy()
      configuration_extended.ontology_document.__setitem__.side_effect = ontology_document.__setitem__
      configuration_extended.ontology_document.__getitem__.side_effect = ontology_document.__getitem__
      configuration_extended.ontology_document.__iter__.side_effect = ontology_document.__iter__
      configuration_extended.ontology_document.get.side_effect = ontology_document.get
      configuration_extended.ontology_document.keys.side_effect = ontology_document.keys
      configuration_extended.ontology_document.pop.side_effect = ontology_document.pop
    pop_items_selected_ontology_document_spy = mocker.spy(configuration_extended.ontology_document, 'pop')
    if ontology_types:
      original_ontology_types = ontology_types.copy()
      configuration_extended.ontology_types.__setitem__.side_effect = ontology_types.__setitem__
      configuration_extended.ontology_types.__getitem__.side_effect = ontology_types.__getitem__
      configuration_extended.ontology_types.__iter__.side_effect = ontology_types.__iter__
      configuration_extended.ontology_types.get.side_effect = ontology_types.get
      configuration_extended.ontology_types.keys.side_effect = ontology_types.keys
      configuration_extended.ontology_types.pop.side_effect = ontology_types.pop
    pop_items_selected_ontology_types_spy = mocker.spy(configuration_extended.ontology_types, 'pop')

    if ontology_document is None or ontology_types is None:
      mocker.patch.object(configuration_extended, 'ontology_types', ontology_types)
      mocker.patch.object(configuration_extended, 'ontology_document', ontology_document)
      with pytest.raises(OntologyConfigGenericException,
                         match="Null ontology_types or ontology_document, erroneous app state"):
        assert configuration_extended.delete_selected_type() is None, "Nothing should be returned"
      return
    if selected_type:
      assert configuration_extended.delete_selected_type() is None, "Nothing should be returned"
      if selected_type and selected_type in original_ontology_types and selected_type in original_ontology_document:
        logger_info_spy.assert_called_once_with(f"User deleted the selected type: {selected_type}")
        pop_items_selected_ontology_types_spy.assert_called_once_with(selected_type)
        pop_items_selected_ontology_document_spy.assert_called_once_with(selected_type)
        clear_category_combo_box_spy.assert_called_once_with()
        add_items_selected_spy.assert_called_once_with(
          ontology_types.keys()
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

  @pytest.mark.parametrize("new_title, new_label", [
    (None, None),
    ("x0", None),
    (None, "x2"),
    ("x3", "x3"),
    ("instrument", "new Instrument")
  ])
  def test_create_type_accepted_callback_should_do_expected(self,
                                                            mocker,
                                                            configuration_extended: configuration_extended,
                                                            new_title,
                                                            new_label):
    mocker.patch.object(configuration_extended, 'create_type_dialog', create=True)
    mocker.patch.object(configuration_extended.create_type_dialog, 'titleLineEdit', create=True)
    mocker.patch.object(configuration_extended.create_type_dialog.titleLineEdit, 'text', return_value=new_title)
    mocker.patch.object(configuration_extended.create_type_dialog, 'labelLineEdit', create=True)
    mocker.patch.object(configuration_extended.create_type_dialog.labelLineEdit, 'text', return_value=new_label)
    clear_ui_spy = mocker.patch.object(configuration_extended.create_type_dialog, 'clear_ui', create=True)
    create_new_type_spy = mocker.patch.object(configuration_extended, 'create_new_type', create=True)
    text_title_line_edit_text_spy = mocker.spy(configuration_extended.create_type_dialog.titleLineEdit, 'text')
    text_label_line_edit_text_spy = mocker.spy(configuration_extended.create_type_dialog.labelLineEdit, 'text')

    assert configuration_extended.create_type_accepted_callback() is None, "Nothing should be returned"
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
    (None, {"x0": {"link": "x0"}, "x1": {"link": "x1"}}),
    ("x3", {"x0": {"link": "x0"}, "x1": {"link": "x1"}}),
    ("x7", {"x0": {"link": "x0"}, "instrument": {"link": "x1"}}),
    ("x6", {"x0": {"link": "x0"}, "subtask5": {"link": "x1"}})
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
    show_create_type_dialog_spy = mocker.patch.object(configuration_extended.create_type_dialog, 'show', create=True)
    show_message_spy = mocker.patch('pasta_eln.ontology_configuration.ontology_configuration_extended.show_message')
    get_next_possible_structural_level_label_spy = mocker.patch(
      'pasta_eln.ontology_configuration.ontology_configuration_extended.get_next_possible_structural_level_label',
      return_value=new_structural_title)
    if ontology_types is not None:
      configuration_extended.ontology_types.__setitem__.side_effect = ontology_types.__setitem__
      configuration_extended.ontology_types.__getitem__.side_effect = ontology_types.__getitem__
      configuration_extended.ontology_types.__iter__.side_effect = ontology_types.__iter__
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

  def test_setup_slots_should_do_expected(self,
                                          configuration_extended: configuration_extended):
    configuration_extended.logger.info.assert_called_once_with(f"Setting up slots for the editor..")
    configuration_extended.loadOntologyPushButton.clicked.connect.assert_called_once_with(
      configuration_extended.load_ontology_data)
    configuration_extended.loadOntologyPushButton.clicked.connect.assert_called_once_with(
      configuration_extended.load_ontology_data)
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
      configuration_extended.update_structure_label)
    configuration_extended.typeLinkLineEdit.textChanged[str].connect.assert_called_once_with(
      configuration_extended.update_type_link)

    # Slots for the delegates
    configuration_extended.delete_column_delegate_props_table.delete_clicked_signal.connect.assert_called_once_with(
      configuration_extended.props_table_data_model.delete_data)
    configuration_extended.reorder_column_delegate_props_table.re_order_signal.connect.assert_called_once_with(
      configuration_extended.props_table_data_model.re_order_data)

    configuration_extended.delete_column_delegate_attach_table.delete_clicked_signal.connect.assert_called_once_with(
      configuration_extended.attachments_table_data_model.delete_data)
    configuration_extended.reorder_column_delegate_attach_table.re_order_signal.connect.assert_called_once_with(
      configuration_extended.attachments_table_data_model.re_order_data)

  def test_load_ontology_data_should_do_expected(self,
                                                 mocker,
                                                 configuration_extended: configuration_extended):

    pass
