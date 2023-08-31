#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_configuration_extended.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from tests.app_tests.common.fixtures import configuration_extended


class TestOntologyConfigConfiguration(object):
  @pytest.mark.parametrize("new_type_selected", [
    "x0",
    "x1"
  ])
  def test_type_combo_box_changed_should_do_expected(self,
                                                     mocker,
                                                     configuration_extended: configuration_extended,
                                                     new_type_selected):
    logger_info_spy = mocker.spy(configuration_extended.logger, 'info')
    mocker.patch.object(configuration_extended, 'addPropsCategoryLineEdit', create=True)
    mock_ontology_types = {
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
    }
    mocker.patch.object(configuration_extended, 'ontology_types', mock_ontology_types, create=True)
    mocker.patch.object(configuration_extended, 'typeLabelLineEdit', create=True)
    mocker.patch.object(configuration_extended, 'typeLinkLineEdit', create=True)
    mocker.patch.object(configuration_extended, 'attachments_table_data_model', create=True)
    mocker.patch.object(configuration_extended, 'propsCategoryComboBox', create=True)
    set_text_label_line_edit_spy = mocker.spy(configuration_extended.typeLabelLineEdit, 'setText')
    set_text_link_line_edit_spy = mocker.spy(configuration_extended.typeLinkLineEdit, 'setText')
    set_current_index_category_combo_box_spy = mocker.spy(configuration_extended.propsCategoryComboBox, 'setCurrentIndex')
    clear_category_combo_box_spy = mocker.spy(configuration_extended.propsCategoryComboBox, 'clear')
    add_items_category_combo_box_spy = mocker.spy(configuration_extended.propsCategoryComboBox, 'addItems')
    update_attachment_table_model_spy = mocker.spy(configuration_extended.attachments_table_data_model, 'update')

    assert configuration_extended.type_combo_box_changed(new_type_selected) is None, "Nothing should be returned"
    logger_info_spy.assert_called_once_with(f"New type selected in UI: {new_type_selected}")
    set_text_label_line_edit_spy.assert_called_once_with(mock_ontology_types.get(new_type_selected).get('label'))
    set_text_link_line_edit_spy.assert_called_once_with(mock_ontology_types.get(new_type_selected).get('link'))
    set_current_index_category_combo_box_spy.assert_called_once_with(0)
    clear_category_combo_box_spy.assert_called_once_with()
    add_items_category_combo_box_spy.assert_called_once_with(mock_ontology_types.get(new_type_selected).get('prop').keys())
    update_attachment_table_model_spy.assert_called_once_with(mock_ontology_types.get(new_type_selected).get('attachments'))

    pass
