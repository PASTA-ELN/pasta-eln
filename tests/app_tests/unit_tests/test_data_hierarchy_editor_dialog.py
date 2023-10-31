#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_editor_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QMessageBox

from pasta_eln.GUI.data_hierarchy.create_type_dialog import CreateTypeDialog
from pasta_eln.GUI.data_hierarchy.delete_column_delegate import DeleteColumnDelegate
from pasta_eln.GUI.data_hierarchy.generic_exception import GenericException
from pasta_eln.GUI.data_hierarchy.key_not_found_exception import \
  KeyNotFoundException
from pasta_eln.GUI.data_hierarchy.constants import ATTACHMENT_TABLE_DELETE_COLUMN_INDEX, \
  ATTACHMENT_TABLE_REORDER_COLUMN_INDEX, METADATA_TABLE_DELETE_COLUMN_INDEX, \
  METADATA_TABLE_IRI_COLUMN_INDEX, METADATA_TABLE_REORDER_COLUMN_INDEX, METADATA_TABLE_REQUIRED_COLUMN_INDEX
from pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog import DataHierarchyEditorDialog, get_gui
from pasta_eln.GUI.data_hierarchy.document_null_exception import DocumentNullException
from pasta_eln.GUI.data_hierarchy.reorder_column_delegate import ReorderColumnDelegate
from pasta_eln.GUI.data_hierarchy.mandatory_column_delegate import MandatoryColumnDelegate
from pasta_eln.GUI.data_hierarchy.utility_functions import generate_empty_type, generate_mandatory_metadata, \
  get_types_for_display
from tests.app_tests.common.fixtures import configuration_extended, data_hierarchy_doc_mock


class TestDataHierarchyEditorDialog(object):

  def test_instantiation_should_succeed(self,
                                        mocker):
    mock_database = mocker.patch('pasta_eln.database.Database')
    mocker.patch('pasta_eln.GUI.data_hierarchy.create_type_dialog.logging.getLogger')
    mock_setup_ui = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog_base.Ui_DataHierarchyEditorDialogBase.setupUi')
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.adjust_data_hierarchy_data_to_v3')
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.LookupIriAction')
    mock_metadata_table_view_model = mocker.MagicMock()
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.MetadataTableViewModel',
                 lambda: mock_metadata_table_view_model)
    column_widths: dict[int, int] = {
      0: 100,
      1: 300,
    }
    mock_metadata_table_view_model.column_widths = column_widths
    mock_attachments_table_view_model = mocker.MagicMock()
    mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.AttachmentsTableViewModel',
      lambda: mock_attachments_table_view_model)
    mock_attachments_table_view_model.column_widths = column_widths
    mock_required_column_delegate = mocker.MagicMock()
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.MandatoryColumnDelegate',
                 lambda: mock_required_column_delegate)
    mock_create_type_dialog = mocker.MagicMock()
    mock_create = mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.CreateTypeDialog',
                               return_value=mock_create_type_dialog)
    mock_delete_column_delegate = mocker.MagicMock()
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.DeleteColumnDelegate',
                 lambda: mock_delete_column_delegate)
    mock_reorder_column_delegate = mocker.MagicMock()
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.ReorderColumnDelegate',
                 lambda: mock_reorder_column_delegate)
    mock_iri_column_delegate = mocker.MagicMock()
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.IriColumnDelegate',
                 lambda: mock_iri_column_delegate)
    mock_signal = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.DataHierarchyEditorDialog.type_changed_signal')
    mock_dialog = mocker.MagicMock()
    mocker.patch.object(QDialog, '__new__', lambda _: mock_dialog)
    mocker.patch.object(MandatoryColumnDelegate, '__new__', lambda _: mocker.MagicMock())
    mocker.patch.object(DeleteColumnDelegate, '__new__', lambda _: mocker.MagicMock())
    mocker.patch.object(ReorderColumnDelegate, '__new__', lambda _: mocker.MagicMock())
    mocker.patch.object(DataHierarchyEditorDialog, 'typeMetadataTableView', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'typeAttachmentsTableView', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'addMetadataRowPushButton', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'addAttachmentPushButton', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'saveDataHierarchyPushButton', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'addMetadataGroupPushButton', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'deleteMetadataGroupPushButton', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'deleteTypePushButton', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'addTypePushButton', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'cancelPushButton', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'helpPushButton', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'attachmentsShowHidePushButton', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'typeComboBox', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'metadataGroupComboBox', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'typeDisplayedTitleLineEdit', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'typeIriLineEdit', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'delete_column_delegate_metadata_table', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'reorder_column_delegate_metadata_table', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'delete_column_delegate_attach_table', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'reorder_column_delegate_attach_table', create=True)
    mock_setup_slots = mocker.patch.object(DataHierarchyEditorDialog, 'setup_slots', create=True)
    mock_load_data_hierarchy_data = mocker.patch.object(DataHierarchyEditorDialog, 'load_data_hierarchy_data', create=True)
    mocker.patch.object(CreateTypeDialog, '__new__')
    config_instance = DataHierarchyEditorDialog(mock_database)
    assert config_instance, "DataHierarchyEditorDialog should be created"
    assert config_instance.type_changed_signal == mock_signal, "Signal should be created"
    mock_setup_ui.assert_called_once_with(mock_dialog)
    assert config_instance.database is mock_database, "Database should be set"
    config_instance.database.db.__getitem__.assert_called_once_with('-ontology-')
    assert config_instance.data_hierarchy_document is config_instance.database.db.__getitem__.return_value, "Data Hierarchy document should be set"
    assert config_instance.metadata_table_data_model == mock_metadata_table_view_model, "Metadata table data model should be set"
    assert config_instance.attachments_table_data_model == mock_attachments_table_view_model, "Attachments table data model should be set"
    assert config_instance.required_column_delegate_metadata_table == mock_required_column_delegate, "Required column delegate should be set"
    assert config_instance.delete_column_delegate_metadata_table == mock_delete_column_delegate, "Delete column delegate should be set"
    assert config_instance.reorder_column_delegate_metadata_table == mock_reorder_column_delegate, "Reorder column delegate should be set"
    assert config_instance.iri_column_delegate_metadata_table == mock_iri_column_delegate, "Iri column delegate should be set"
    assert config_instance.delete_column_delegate_attach_table == mock_delete_column_delegate, "Delete column delegate should be set"
    assert config_instance.reorder_column_delegate_attach_table == mock_reorder_column_delegate, "Reorder column delegate should be set"
    config_instance.typeMetadataTableView.setItemDelegateForColumn.assert_any_call(
      METADATA_TABLE_REQUIRED_COLUMN_INDEX,
      mock_required_column_delegate
    )
    config_instance.typeMetadataTableView.setItemDelegateForColumn.assert_any_call(
      METADATA_TABLE_DELETE_COLUMN_INDEX,
      mock_delete_column_delegate
    )
    config_instance.typeMetadataTableView.setItemDelegateForColumn.assert_any_call(
      METADATA_TABLE_REORDER_COLUMN_INDEX,
      mock_reorder_column_delegate
    )
    config_instance.typeMetadataTableView.setItemDelegateForColumn.assert_any_call(
      METADATA_TABLE_IRI_COLUMN_INDEX,
      mock_iri_column_delegate
    )
    config_instance.typeMetadataTableView.setModel.assert_called_once_with(mock_metadata_table_view_model)
    for column_index, width in column_widths.items():
      config_instance.typeMetadataTableView.setColumnWidth.assert_any_call(column_index, width)
    (config_instance.typeMetadataTableView.horizontalHeader()
     .setSectionResizeMode.assert_called_once_with(1, QtWidgets.QHeaderView.Stretch))

    config_instance.typeAttachmentsTableView.setItemDelegateForColumn.assert_any_call(
      ATTACHMENT_TABLE_DELETE_COLUMN_INDEX,
      mock_delete_column_delegate)
    config_instance.typeAttachmentsTableView.setItemDelegateForColumn.assert_any_call(
      ATTACHMENT_TABLE_REORDER_COLUMN_INDEX,
      mock_reorder_column_delegate)
    config_instance.typeAttachmentsTableView.setModel.assert_any_call(mock_attachments_table_view_model)

    for column_index, width in config_instance.attachments_table_data_model.column_widths.items():
      config_instance.typeAttachmentsTableView.setColumnWidth.assert_any_call(column_index, width)
    config_instance.typeAttachmentsTableView.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

    mock_create.assert_called_once_with(config_instance.create_type_accepted_callback,
                                        config_instance.create_type_rejected_callback)
    assert config_instance.create_type_dialog == mock_create_type_dialog, "CreateTypeDialog should be set"
    mock_setup_slots.assert_called_once_with()

    config_instance.addAttachmentPushButton.hide.assert_called_once_with()
    config_instance.typeAttachmentsTableView.hide.assert_called_once_with()
    mock_load_data_hierarchy_data.assert_called_once_with()

  def test_instantiation_with_null_database_should_throw_exception(self,
                                                                   mocker):
    mocker.patch('pasta_eln.GUI.data_hierarchy.create_type_dialog.logging.getLogger')
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.Ui_DataHierarchyEditorDialogBase.setupUi')
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.adjust_data_hierarchy_data_to_v3')
    mocker.patch.object(QDialog, '__new__')
    with pytest.raises(GenericException, match="Null database instance passed to the initializer"):
      DataHierarchyEditorDialog(None)

  def test_instantiation_with_database_with_null_document_should_throw_exception(self,
                                                                                 mocker):
    mocker.patch('pasta_eln.GUI.data_hierarchy.create_type_dialog.logging.getLogger')
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.Ui_DataHierarchyEditorDialogBase.setupUi')
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.adjust_data_hierarchy_data_to_v3')
    mocker.patch.object(QDialog, '__new__')
    mock_db = mocker.patch('pasta_eln.database.Database')
    mocker.patch.object(mock_db, 'db', {'-ontology-': None}, create=True)
    with pytest.raises(DocumentNullException, match="Null data_hierarchy document in db instance"):
      DataHierarchyEditorDialog(mock_db)

  @pytest.mark.parametrize("new_type_selected, mock_data_hierarchy_types", [
    ("x0", {
      "x0": {
        "displayedTitle": "x0",
        "IRI": "url",
        "metadata": {
          "default": [
            {
              "key": "key",
              "value": "value"}
          ],
          "metadata group1": [
            {
              "key": "key",
              "value": "value"
            }
          ]
        },
        "attachments": []
      },
      "x1": {
        "displayedTitle": "x0",
        "IRI": "url",
        "metadata": {
          "default": [
            {
              "key": "key",
              "value": "value"}
          ],
          "metadata group1": [
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
        "displayedTitle": "x0",
        "IRI": "url",
        "metadata": {
          "default": [
            {
              "key": "key",
              "value": "value"}
          ],
          "metadata group1": [
            {
              "key": "key",
              "value": "value"
            }
          ]
        },
        "attachments": []
      },
      "x1": {
        "displayedTitle": "x0",
        "IRI": "url",
        "metadata": {
          "default": [
            {
              "key": "key",
              "value": "value"}
          ],
          "metadata group1": [
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
    ("x0", {"x0": {"displayedTitle": None, "IRI": None, "metadata": None, "attachments": None}}),
    ("x0", {"x0": {"displayedTitle": None, "IRI": None, "metadata": {"": None}, "attachments": [{"": None}]}}),
    ("x0", {"x0": {"": None, "§": None, "metadata": {"": None}, "attachment": [{"": None}]}})
  ])
  def test_type_combo_box_changed_should_do_expected(self,
                                                     mocker,
                                                     configuration_extended: configuration_extended,
                                                     new_type_selected,
                                                     mock_data_hierarchy_types):
    logger_info_spy = mocker.spy(configuration_extended.logger, 'info')
    mock_signal = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.DataHierarchyEditorDialog.type_changed_signal')
    mocker.patch.object(configuration_extended, 'addMetadataGroupLineEdit', create=True)
    mocker.patch.object(configuration_extended, 'data_hierarchy_types', mock_data_hierarchy_types, create=True)
    mocker.patch.object(configuration_extended, 'typeDisplayedTitleLineEdit', create=True)
    mocker.patch.object(configuration_extended, 'typeIriLineEdit', create=True)
    mocker.patch.object(configuration_extended, 'attachments_table_data_model', create=True)
    mocker.patch.object(configuration_extended, 'metadataGroupComboBox', create=True)
    mocker.patch.object(configuration_extended, 'type_changed_signal', mock_signal, create=True)
    set_text_displayed_title_line_edit_spy = mocker.spy(configuration_extended.typeDisplayedTitleLineEdit, 'setText')
    set_text_iri_line_edit_spy = mocker.spy(configuration_extended.typeIriLineEdit, 'setText')
    set_current_index_metadata_group_combo_box_spy = mocker.spy(configuration_extended.metadataGroupComboBox,
                                                          'setCurrentIndex')
    clear_add_metadata_metadata_group_line_edit_spy = mocker.spy(configuration_extended.addMetadataGroupLineEdit, 'clear')
    clear_metadata_group_combo_box_spy = mocker.spy(configuration_extended.metadataGroupComboBox, 'clear')
    add_items_metadata_group_combo_box_spy = mocker.spy(configuration_extended.metadataGroupComboBox, 'addItems')
    update_attachment_table_model_spy = mocker.spy(configuration_extended.attachments_table_data_model, 'update')
    if mock_data_hierarchy_types is not None and len(
        mock_data_hierarchy_types) > 0 and new_type_selected not in mock_data_hierarchy_types:
      with pytest.raises(KeyNotFoundException,
                         match=f"Key {new_type_selected} not found in data_hierarchy_types"):
        assert configuration_extended.type_combo_box_changed(
          new_type_selected) is not None, "Nothing should be returned"

    if (mock_data_hierarchy_types
        and new_type_selected
        and new_type_selected in mock_data_hierarchy_types):
      assert configuration_extended.type_combo_box_changed(new_type_selected) is None, "Nothing should be returned"
      mock_signal.emit.assert_called_once_with(new_type_selected)
      logger_info_spy.assert_called_once_with("New type selected in UI: {%s}", new_type_selected)
      clear_add_metadata_metadata_group_line_edit_spy.assert_called_once_with()
      set_text_displayed_title_line_edit_spy.assert_called_once_with(mock_data_hierarchy_types.get(new_type_selected).get('displayedTitle'))
      set_text_iri_line_edit_spy.assert_called_once_with(mock_data_hierarchy_types.get(new_type_selected).get('IRI'))
      set_current_index_metadata_group_combo_box_spy.assert_called_once_with(0)
      clear_metadata_group_combo_box_spy.assert_called_once_with()
      add_items_metadata_group_combo_box_spy.assert_called_once_with(
        list(mock_data_hierarchy_types.get(new_type_selected).get('metadata').keys())
        if mock_data_hierarchy_types.get(new_type_selected).get('metadata') else [])
      update_attachment_table_model_spy.assert_called_once_with(
        mock_data_hierarchy_types.get(new_type_selected).get('attachments'))

  @pytest.mark.parametrize("new_selected_metadata_group, selected_type_metadata", [
    (None, {}),
    ("default", {}),
    ("default", {"default": [], "metadata group1": [], "metadata group2": []}),
    ("metadata group1", {"default": [], "metadata group1": [], "metadata group2": []}),
    ("default", {"default": [], "metadata group1": [], "metadata group2": []}),
    ("metadata group1", {"default": [], "metadata group1": [], "metadata group2": []}),
    ("metadata group2", {"default": [], "metadata group1": [], "metadata group2": []}),
    ("metadata group2", {"default": [], "metadata group1": [{"name": "key", "value": "value"}], "metadata group2": []}),
    ("metadata group1", {"default": [], "metadata group1": [{"name": None, "value": None}], "metadata group2": None}),
    ("metadata group2", {"default": [], "metadata group1": [{"name": None, "value": None}], "metadata group2": None}),
    ("metadata group3", {"default": [], "metadata group1": [], "metadata group2": []}),
  ])
  def test_type_metadata_group_combo_box_changed_should_do_expected(self,
                                                              mocker,
                                                              configuration_extended: configuration_extended,
                                                              new_selected_metadata_group,
                                                              selected_type_metadata):
    logger_info_spy = mocker.spy(configuration_extended.logger, 'info')
    mocker.patch.object(configuration_extended, 'selected_type_metadata', selected_type_metadata, create=True)
    mocker.patch.object(configuration_extended, 'metadata_table_data_model', create=True)
    update_metadata_table_model_spy = mocker.spy(configuration_extended.metadata_table_data_model, 'update')
    assert configuration_extended.metadata_group_combo_box_changed(
      new_selected_metadata_group) is None, "Nothing should be returned"
    logger_info_spy.assert_called_once_with("New metadata group selected in UI: {%s}", new_selected_metadata_group)
    if new_selected_metadata_group and selected_type_metadata:
      update_metadata_table_model_spy.assert_called_once_with(selected_type_metadata.get(new_selected_metadata_group))

  @pytest.mark.parametrize("new_metadata_group, data_hierarchy_types, selected_type_metadata", [
    (None, None, {}),
    ("default", None, {}),
    (None, {0: "x0"}, {"default": [], "metadata group1": [], "metadata group2": []}),
    ("default", {0: "x0"}, {"default": [], "metadata group1": [], "metadata group2": []}),
    ("metadata group1", {0: "x0"}, {"default": [], "metadata group1": [], "metadata group2": []}),
    ("default", {0: "x0"}, {"default": [], "metadata group1": [], "metadata group2": []}),
    ("metadata group1", {0: "x0"}, {"default": [], "metadata group1": [], "metadata group2": []}),
    ("metadata group2", {0: "x0"}, {"default": [], "metadata group1": [], "metadata group2": []}),
    ("metadata group2", {0: "x0"}, {"default": [], "metadata group1": [{"name": "key", "value": "value"}], "metadata group2": []}),
    ("metadata group1", {0: "x0"}, {"default": [], "metadata group1": [{"name": None, "value": None}], "metadata group2": None}),
    ("metadata group2", {0: "x0"}, {"default": [], "metadata group1": [{"name": None, "value": None}], "metadata group2": None}),
    ("metadata group3", {0: "x0"}, {"default": [], "metadata group1": [], "metadata group2": []}),
  ])
  def test_add_new_metadata_group_should_do_expected(self,
                                                     mocker,
                                                     configuration_extended: configuration_extended,
                                                     new_metadata_group,
                                                     data_hierarchy_types,
                                                     selected_type_metadata):
    logger_info_spy = mocker.spy(configuration_extended.logger, 'info')
    mocker.patch.object(configuration_extended, 'addMetadataGroupLineEdit', create=True)
    mocker.patch.object(configuration_extended.addMetadataGroupLineEdit, 'text', return_value=new_metadata_group)
    mocker.patch.object(configuration_extended, 'data_hierarchy_types', data_hierarchy_types, create=True)
    mocker.patch.object(configuration_extended, 'metadataGroupComboBox', create=True)
    mocker.patch.object(configuration_extended, 'data_hierarchy_loaded', create=True)
    add_items_selected_spy = mocker.spy(configuration_extended.metadataGroupComboBox, 'addItems')
    clear_metadata_group_combo_box_spy = mocker.spy(configuration_extended.metadataGroupComboBox, 'clear')
    set_current_index_metadata_group_combo_box_spy = mocker.spy(configuration_extended.metadataGroupComboBox,
                                                          'setCurrentIndex')
    mocker.patch.object(configuration_extended, 'selected_type_metadata', create=True)
    configuration_extended.selected_type_metadata.__setitem__.side_effect = selected_type_metadata.__setitem__
    configuration_extended.selected_type_metadata.__getitem__.side_effect = selected_type_metadata.__getitem__
    configuration_extended.selected_type_metadata.__iter__.side_effect = selected_type_metadata.__iter__
    configuration_extended.selected_type_metadata.keys.side_effect = selected_type_metadata.keys
    set_items_selected_spy = mocker.spy(configuration_extended.selected_type_metadata, '__setitem__')
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.len',
                 lambda x: len(selected_type_metadata.keys()))
    mock_show_message = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.show_message')

    if not new_metadata_group:
      assert configuration_extended.add_new_metadata_group() is None, "Nothing should be returned"
      mock_show_message.assert_called_once_with("Enter non-null/valid metadata group name!!.....", QMessageBox.Warning)
      return
    if not data_hierarchy_types:
      assert configuration_extended.add_new_metadata_group() is None, "Nothing should be returned"
      mock_show_message.assert_called_once_with("Load the data hierarchy data first....", QMessageBox.Warning)
      return

    if new_metadata_group in selected_type_metadata:
      assert configuration_extended.add_new_metadata_group() is None, "Nothing should be returned"
      mock_show_message.assert_called_once_with("Metadata group already exists....", QMessageBox.Warning)
    else:
      if new_metadata_group:
        assert configuration_extended.add_new_metadata_group() is None, "Nothing should be returned"
        logger_info_spy.assert_called_once_with("User added new metadata group: {%s}", new_metadata_group)
        set_items_selected_spy.assert_called_once_with(new_metadata_group, generate_mandatory_metadata())
        set_current_index_metadata_group_combo_box_spy.assert_called_once_with(len(selected_type_metadata.keys()) - 1)
        clear_metadata_group_combo_box_spy.assert_called_once_with()
        add_items_selected_spy.assert_called_once_with(
          list(selected_type_metadata.keys())
        )
      else:
        assert configuration_extended.add_new_metadata_metadata_group() is None, "Nothing should be returned"
        mock_show_message.assert_called_once_with("Enter non-null/valid metadata group name!!.....")

  @pytest.mark.parametrize("selected_metadata_group, selected_type_metadata", [
    (None, {}),
    ("default", {}),
    ("default", None),
    (None, {"default": [], "metadata group1": [], "metadata group2": []}),
    ("default", {"default": [], "metadata group1": [], "metadata group2": []}),
    ("metadata group1", {"default": [], "metadata group1": [], "metadata group2": []}),
    ("default", {"default": [], "metadata group1": [], "metadata group2": []}),
    ("metadata group1", {"default": [], "metadata group1": [], "metadata group2": []}),
    ("metadata group2", {"default": [], "metadata group1": [], "metadata group2": []}),
    ("metadata group2", {"default": [], "metadata group1": [{"name": "key", "value": "value"}], "metadata group2": []}),
    ("metadata group1", {"default": [], "metadata group1": [{"name": None, "value": None}], "metadata group2": None}),
    ("metadata group2", {"default": [], "metadata group1": [{"name": None, "value": None}], "metadata group2": None}),
    ("metadata group3", {"default": [], "metadata group1": [], "metadata group2": []}),
  ])
  def test_delete_selected_metadata_group_should_do_expected(self,
                                                       mocker,
                                                       configuration_extended: configuration_extended,
                                                       selected_metadata_group,
                                                       selected_type_metadata):
    logger_info_spy = mocker.spy(configuration_extended.logger, 'info')
    mocker.patch.object(configuration_extended, 'metadataGroupComboBox', create=True)
    current_text_metadata_group_combo_box_spy = mocker.patch.object(configuration_extended.metadataGroupComboBox,
                                                              'currentText', return_value=selected_metadata_group)
    add_items_selected_spy = mocker.spy(configuration_extended.metadataGroupComboBox, 'addItems')
    clear_metadata_group_combo_box_spy = mocker.spy(configuration_extended.metadataGroupComboBox, 'clear')
    set_current_index_metadata_group_combo_box_spy = mocker.spy(configuration_extended.metadataGroupComboBox,
                                                          'setCurrentIndex')
    mocker.patch.object(configuration_extended, 'selected_type_metadata', create=True)
    mock_show_message = mocker.patch(
      "pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.show_message")
    if selected_type_metadata:
      configuration_extended.selected_type_metadata.__setitem__.side_effect = selected_type_metadata.__setitem__
      configuration_extended.selected_type_metadata.__getitem__.side_effect = selected_type_metadata.__getitem__
      configuration_extended.selected_type_metadata.pop.side_effect = selected_type_metadata.pop
      configuration_extended.selected_type_metadata.keys.side_effect = selected_type_metadata.keys
    pop_items_selected_spy = mocker.spy(configuration_extended.selected_type_metadata, 'pop')
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.len',
                 lambda x: len(selected_type_metadata.keys()))

    if selected_type_metadata is None:
      mocker.patch.object(configuration_extended, 'selected_type_metadata', None)
      assert configuration_extended.delete_selected_metadata_group() is None, "Nothing should be returned"
      mock_show_message.assert_called_once_with("Load the data hierarchy data first....", QMessageBox.Warning)
      return
    if selected_type_metadata and selected_metadata_group in selected_type_metadata:
      assert configuration_extended.delete_selected_metadata_group() is None, "Nothing should be returned"
      current_text_metadata_group_combo_box_spy.assert_called_once_with()
      logger_info_spy.assert_called_once_with("User deleted the selected metadata group: {%s}", selected_metadata_group)
      pop_items_selected_spy.assert_called_once_with(selected_metadata_group)
      clear_metadata_group_combo_box_spy.assert_called_once_with()
      add_items_selected_spy.assert_called_once_with(
        list(selected_type_metadata.keys())
      )
      set_current_index_metadata_group_combo_box_spy.assert_called_once_with(len(selected_type_metadata.keys()) - 1)

  @pytest.mark.parametrize("modified_type_displayed_title, current_type, data_hierarchy_types", [
    (None, None, None),
    ("new_displayed_title_1", None, None),
    (None, "x0", {"x0": {"displayedTitle": "x0"}, "x1": {"displayedTitle": "x1"}}),
    ("new_displayed_title_2", "x1", {"x0": {"displayedTitle": "x0"}, "x1": {"displayedTitle": "x1"}}),
    ("new_displayed_title_2", "instrument", {"x0": {"displayedTitle": "x0"}, "instrument": {"displayedTitle": "x1"}}),
    ("type_new_displayed_title", "subtask4", {"x0": {"displayedTitle": "x0"}, "subtask5": {"displayedTitle": "x1"}}),
  ])
  def test_update_structure_displayed_title_should_do_expected(self,
                                                     mocker,
                                                     configuration_extended: configuration_extended,
                                                     modified_type_displayed_title,
                                                     current_type,
                                                     data_hierarchy_types):
    mocker.patch.object(configuration_extended, 'typeComboBox', create=True)
    mocker.patch.object(configuration_extended, 'set_iri_lookup_action', create=True)
    mocker.patch.object(configuration_extended.typeComboBox, 'currentText', return_value=current_type)

    mocker.patch.object(configuration_extended, 'data_hierarchy_types', create=True)
    if data_hierarchy_types:
      configuration_extended.data_hierarchy_types.__setitem__.side_effect = data_hierarchy_types.__setitem__
      configuration_extended.data_hierarchy_types.__getitem__.side_effect = data_hierarchy_types.__getitem__
      configuration_extended.data_hierarchy_types.__iter__.side_effect = data_hierarchy_types.__iter__
      configuration_extended.data_hierarchy_types.__contains__.side_effect = data_hierarchy_types.__contains__
      configuration_extended.data_hierarchy_types.get.side_effect = data_hierarchy_types.get
      configuration_extended.data_hierarchy_types.keys.side_effect = data_hierarchy_types.keys

    get_data_hierarchy_types_spy = mocker.spy(configuration_extended.data_hierarchy_types, 'get')

    if modified_type_displayed_title:
      assert configuration_extended.update_type_displayed_title(modified_type_displayed_title) is None, "Nothing should be returned"
      if data_hierarchy_types is not None and current_type in data_hierarchy_types:
        get_data_hierarchy_types_spy.assert_called_once_with(current_type)
        assert data_hierarchy_types[current_type]["displayedTitle"] == modified_type_displayed_title
        configuration_extended.set_iri_lookup_action.assert_called_once_with(modified_type_displayed_title)

  @pytest.mark.parametrize("modified_type_iri, current_type, data_hierarchy_types", [
    (None, None, None),
    ("new_url", None, None),
    (None, "x0", {"x0": {"displayedTitle": "x0"}, "x1": {"displayedTitle": "x1"}}),
    ("new_url_2", "x1", {"x0": {"displayedTitle": "x0"}, "x1": {"displayedTitle": "x1"}}),
    ("new_url_2", "instrument", {"x0": {"displayedTitle": "x0"}, "instrument": {"displayedTitle": "x1"}}),
    ("type_new_url", "subtask4", {"x0": {"displayedTitle": "x0"}, "subtask5": {"displayedTitle": "x1"}}),
  ])
  def test_update_type_iri_should_do_expected(self,
                                              mocker,
                                              configuration_extended: configuration_extended,
                                              modified_type_iri,
                                              current_type,
                                              data_hierarchy_types):
    mocker.patch.object(configuration_extended, 'typeComboBox', create=True)
    mocker.patch.object(configuration_extended.typeComboBox, 'currentText', return_value=current_type)

    mocker.patch.object(configuration_extended, 'data_hierarchy_types', create=True)
    if data_hierarchy_types:
      configuration_extended.data_hierarchy_types.__setitem__.side_effect = data_hierarchy_types.__setitem__
      configuration_extended.data_hierarchy_types.__getitem__.side_effect = data_hierarchy_types.__getitem__
      configuration_extended.data_hierarchy_types.__iter__.side_effect = data_hierarchy_types.__iter__
      configuration_extended.data_hierarchy_types.__contains__.side_effect = data_hierarchy_types.__contains__
      configuration_extended.data_hierarchy_types.get.side_effect = data_hierarchy_types.get
      configuration_extended.data_hierarchy_types.keys.side_effect = data_hierarchy_types.keys

    get_data_hierarchy_types_spy = mocker.spy(configuration_extended.data_hierarchy_types, 'get')

    if modified_type_iri:
      assert configuration_extended.update_type_iri(modified_type_iri) is None, "Nothing should be returned"
      if data_hierarchy_types is not None and current_type in data_hierarchy_types:
        get_data_hierarchy_types_spy.assert_called_once_with(current_type)
        assert data_hierarchy_types[current_type]["IRI"] == modified_type_iri

  @pytest.mark.parametrize("selected_type, data_hierarchy_types, data_hierarchy_document", [
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
                                                   data_hierarchy_types,
                                                   data_hierarchy_document):
    mock_signal = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.DataHierarchyEditorDialog.type_changed_signal')
    mocker.patch.object(configuration_extended, 'typeComboBox', create=True)
    mocker.patch.object(configuration_extended.typeComboBox, 'currentText', return_value=selected_type)
    mocker.patch.object(configuration_extended, 'type_changed_signal', mock_signal, create=True)

    mocker.patch.object(configuration_extended, 'data_hierarchy_types', create=True)
    mocker.patch.object(configuration_extended, 'data_hierarchy_document', create=True)
    clear_type_combo_box_spy = mocker.spy(configuration_extended.typeComboBox, 'clear')
    set_current_index_type_combo_box_spy = mocker.spy(configuration_extended.typeComboBox, 'setCurrentIndex')
    add_items_selected_spy = mocker.spy(configuration_extended.typeComboBox, 'addItems')
    logger_info_spy = mocker.spy(configuration_extended.logger, 'info')
    mock_show_message = mocker.patch(
      "pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.show_message")
    mocker.patch.object(configuration_extended, 'data_hierarchy_loaded', True, create=True)
    if data_hierarchy_document:
      original_data_hierarchy_document = data_hierarchy_document.copy()
      configuration_extended.data_hierarchy_document.__setitem__.side_effect = data_hierarchy_document.__setitem__
      configuration_extended.data_hierarchy_document.__getitem__.side_effect = data_hierarchy_document.__getitem__
      configuration_extended.data_hierarchy_document.__iter__.side_effect = data_hierarchy_document.__iter__
      configuration_extended.data_hierarchy_document.__contains__.side_effect = data_hierarchy_document.__contains__
      configuration_extended.data_hierarchy_document.get.side_effect = data_hierarchy_document.get
      configuration_extended.data_hierarchy_document.keys.side_effect = data_hierarchy_document.keys
      configuration_extended.data_hierarchy_document.pop.side_effect = data_hierarchy_document.pop
    if data_hierarchy_types:
      original_data_hierarchy_types = data_hierarchy_types.copy()
      configuration_extended.data_hierarchy_types.__setitem__.side_effect = data_hierarchy_types.__setitem__
      configuration_extended.data_hierarchy_types.__getitem__.side_effect = data_hierarchy_types.__getitem__
      configuration_extended.data_hierarchy_types.__iter__.side_effect = data_hierarchy_types.__iter__
      configuration_extended.data_hierarchy_types.__contains__.side_effect = data_hierarchy_types.__contains__
      configuration_extended.data_hierarchy_types.get.side_effect = data_hierarchy_types.get
      configuration_extended.data_hierarchy_types.keys.side_effect = data_hierarchy_types.keys
      configuration_extended.data_hierarchy_types.pop.side_effect = data_hierarchy_types.pop
    pop_items_selected_data_hierarchy_types_spy = mocker.spy(configuration_extended.data_hierarchy_types, 'pop')

    if data_hierarchy_document is None or data_hierarchy_types is None:
      mocker.patch.object(configuration_extended, 'data_hierarchy_types', data_hierarchy_types)
      mocker.patch.object(configuration_extended, 'data_hierarchy_document', data_hierarchy_document)
      assert configuration_extended.delete_selected_type() is None, "Nothing should be returned"
      mock_show_message.assert_called_once_with("Load the data hierarchy data first....", QMessageBox.Warning)
      return
    if selected_type:
      assert configuration_extended.delete_selected_type() is None, "Nothing should be returned"
      if selected_type and selected_type in original_data_hierarchy_types:
        logger_info_spy.assert_called_once_with("User deleted the selected type: {%s}", selected_type)
        pop_items_selected_data_hierarchy_types_spy.assert_called_once_with(selected_type)
        clear_type_combo_box_spy.assert_called_once_with()
        add_items_selected_spy.assert_called_once_with(
          get_types_for_display(data_hierarchy_types.keys())
        )
        set_current_index_type_combo_box_spy.assert_called_once_with(0)
        assert selected_type not in data_hierarchy_types and data_hierarchy_document, "selected_type should be deleted"
      else:
        logger_info_spy.assert_not_called()
        logger_info_spy.assert_not_called()
        pop_items_selected_data_hierarchy_types_spy.assert_not_called()
        clear_type_combo_box_spy.assert_not_called()
        add_items_selected_spy.assert_not_called()
        set_current_index_type_combo_box_spy.assert_not_called()

  @pytest.mark.parametrize("new_title, new_displayed_title, is_structure_level", [
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
                                                            new_displayed_title,
                                                            is_structure_level):
    mocker.patch.object(configuration_extended, 'create_type_dialog', create=True)
    mocker.patch.object(configuration_extended.create_type_dialog, 'titleLineEdit', create=True)
    mocker.patch.object(configuration_extended.create_type_dialog, 'next_struct_level', new_title, create=True)
    mock_check_box = mocker.patch.object(configuration_extended.create_type_dialog, 'structuralLevelCheckBox',
                                         create=True)
    mocker.patch.object(mock_check_box, 'isChecked', return_value=is_structure_level, create=True)
    mocker.patch.object(configuration_extended.create_type_dialog.titleLineEdit, 'text', return_value=new_title)
    mocker.patch.object(configuration_extended.create_type_dialog, 'displayedTitleLineEdit', create=True)
    mocker.patch.object(configuration_extended.create_type_dialog.displayedTitleLineEdit, 'text', return_value=new_displayed_title)
    clear_ui_spy = mocker.patch.object(configuration_extended.create_type_dialog, 'clear_ui', create=True)
    create_new_type_spy = mocker.patch.object(configuration_extended, 'create_new_type', create=True)
    text_title_line_edit_text_spy = mocker.spy(configuration_extended.create_type_dialog.titleLineEdit, 'text')
    text_displayed_title_line_edit_text_spy = mocker.spy(configuration_extended.create_type_dialog.displayedTitleLineEdit, 'text')

    assert configuration_extended.create_type_accepted_callback() is None, "Nothing should be returned"
    if not is_structure_level:
      text_title_line_edit_text_spy.assert_called_once_with()
    text_displayed_title_line_edit_text_spy.assert_called_once_with()
    clear_ui_spy.assert_called_once_with()
    create_new_type_spy.assert_called_once_with(
      new_title, new_displayed_title
    )

  def test_create_type_rejected_callback_should_do_expected(self,
                                                            mocker,
                                                            configuration_extended: configuration_extended):
    mocker.patch.object(configuration_extended, 'create_type_dialog', create=True)
    clear_ui_spy = mocker.patch.object(configuration_extended.create_type_dialog, 'clear_ui', create=True)
    assert configuration_extended.create_type_rejected_callback() is None, "Nothing should be returned"
    clear_ui_spy.assert_called_once_with()

  @pytest.mark.parametrize("new_structural_title, data_hierarchy_types", [
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
                                                      data_hierarchy_types):
    mocker.patch.object(configuration_extended, 'create_type_dialog', create=True)
    mocker.patch.object(configuration_extended, 'data_hierarchy_types', create=True)
    set_structural_level_title_spy = mocker.patch.object(configuration_extended.create_type_dialog,
                                                         'set_structural_level_title', create=True)
    mocker.patch.object(configuration_extended, 'data_hierarchy_loaded', create=True)
    show_create_type_dialog_spy = mocker.patch.object(configuration_extended.create_type_dialog, 'show', create=True)
    show_message_spy = mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.show_message')
    get_next_possible_structural_level_title_spy = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.get_next_possible_structural_level_title',
      return_value=new_structural_title)
    if data_hierarchy_types is not None:
      configuration_extended.data_hierarchy_types.__setitem__.side_effect = data_hierarchy_types.__setitem__
      configuration_extended.data_hierarchy_types.__getitem__.side_effect = data_hierarchy_types.__getitem__
      configuration_extended.data_hierarchy_types.__iter__.side_effect = data_hierarchy_types.__iter__
      configuration_extended.data_hierarchy_types.__contains__.side_effect = data_hierarchy_types.__contains__
      configuration_extended.data_hierarchy_types.get.side_effect = data_hierarchy_types.get
      configuration_extended.data_hierarchy_types.keys.side_effect = data_hierarchy_types.keys
      configuration_extended.data_hierarchy_types.pop.side_effect = data_hierarchy_types.pop
    else:
      mocker.patch.object(configuration_extended, 'data_hierarchy_types', None)

    assert configuration_extended.show_create_type_dialog() is None, "Nothing should be returned"
    if data_hierarchy_types is not None:
      get_next_possible_structural_level_title_spy.assert_called_once_with(data_hierarchy_types.keys())
      set_structural_level_title_spy.assert_called_once_with(new_structural_title)
      show_create_type_dialog_spy.assert_called_once_with()
    else:
      show_message_spy.assert_called_once_with("Load the data hierarchy data first...", QMessageBox.Warning)
      get_next_possible_structural_level_title_spy.assert_not_called()
      set_structural_level_title_spy.assert_not_called()
      show_create_type_dialog_spy.assert_not_called()

  def test_initialize_should_setup_slots_and_should_do_expected(self,
                                                                configuration_extended: configuration_extended):
    configuration_extended.logger.info.assert_any_call("Setting up slots for the editor..")
    configuration_extended.logger.info.assert_any_call("User loaded the data hierarchy data in UI")
    configuration_extended.addMetadataRowPushButton.clicked.connect.assert_called_once_with(
      configuration_extended.metadata_table_data_model.add_data_row)
    configuration_extended.addAttachmentPushButton.clicked.connect.assert_called_once_with(
      configuration_extended.attachments_table_data_model.add_data_row)
    configuration_extended.saveDataHierarchyPushButton.clicked.connect.assert_called_once_with(
      configuration_extended.save_data_hierarchy)
    configuration_extended.addMetadataGroupPushButton.clicked.connect.assert_called_once_with(
      configuration_extended.add_new_metadata_group)
    configuration_extended.deleteMetadataGroupPushButton.clicked.connect.assert_called_once_with(
      configuration_extended.delete_selected_metadata_group)
    configuration_extended.deleteTypePushButton.clicked.connect.assert_called_once_with(
      configuration_extended.delete_selected_type)
    configuration_extended.addTypePushButton.clicked.connect.assert_called_once_with(
      configuration_extended.show_create_type_dialog)

    # Slots for the combo-boxes
    configuration_extended.typeComboBox.currentTextChanged.connect.assert_called_once_with(
      configuration_extended.type_combo_box_changed)
    configuration_extended.metadataGroupComboBox.currentTextChanged.connect.assert_called_once_with(
      configuration_extended.metadata_group_combo_box_changed)

    # Slots for line edits
    configuration_extended.typeDisplayedTitleLineEdit.textChanged[str].connect.assert_called_once_with(
      configuration_extended.update_type_displayed_title)
    configuration_extended.typeIriLineEdit.textChanged[str].connect.assert_called_once_with(
      configuration_extended.update_type_iri)

    # Slots for the delegates
    configuration_extended.delete_column_delegate_metadata_table.delete_clicked_signal.connect.assert_called_once_with(
      configuration_extended.metadata_table_data_model.delete_data)
    configuration_extended.reorder_column_delegate_metadata_table.re_order_signal.connect.assert_called_once_with(
      configuration_extended.metadata_table_data_model.re_order_data)

    configuration_extended.delete_column_delegate_attach_table.delete_clicked_signal.connect.assert_called_once_with(
      configuration_extended.attachments_table_data_model.delete_data)
    configuration_extended.reorder_column_delegate_attach_table.re_order_signal.connect.assert_called_once_with(
      configuration_extended.attachments_table_data_model.re_order_data)

  @pytest.mark.parametrize("data_hierarchy_document", [
    'data_hierarchy_doc_mock',
    None,
    {"x0": {"IRI": "x0"}, "": {"IRI": "x1"}},
    {"x0": {"IRI": "x0"}, "": {"IRI": "x1"}, 23: "test", "__id": "test"},
    {"test": ["test1", "test2", "test3"]}
  ])
  def test_load_data_hierarchy_data_should_with_variant_types_of_doc_should_do_expected(self,
                                                                                  mocker,
                                                                                  data_hierarchy_document,
                                                                                  configuration_extended: configuration_extended,
                                                                                  request):
    doc = request.getfixturevalue(data_hierarchy_document) \
      if data_hierarchy_document and type(data_hierarchy_document) is str \
      else data_hierarchy_document
    mocker.patch.object(configuration_extended, 'data_hierarchy_document', doc, create=True)
    if data_hierarchy_document is None:
      with pytest.raises(GenericException, match="Null data_hierarchy_document, erroneous app state"):
        assert configuration_extended.load_data_hierarchy_data() is None, "Nothing should be returned"
      return
    assert configuration_extended.load_data_hierarchy_data() is None, "Nothing should be returned"
    assert configuration_extended.typeComboBox.clear.call_count == 2, "Clear should be called twice"
    assert configuration_extended.typeComboBox.addItems.call_count == 2, "addItems should be called twice"
    configuration_extended.typeComboBox.addItems.assert_called_with(
      get_types_for_display(configuration_extended.data_hierarchy_types.keys()))
    assert configuration_extended.typeComboBox.setCurrentIndex.call_count == 2, "setCurrentIndex should be called twice"
    configuration_extended.typeComboBox.setCurrentIndex.assert_called_with(0)
    for data in data_hierarchy_document:
      if type(data) is dict:
        assert data in configuration_extended.data_hierarchy_types, "Data should be loaded"

  @pytest.mark.parametrize("data_hierarchy_document",
                           [None,
                            {"x0": {"IRI": "x0"}, "": {"IRI": "x1"}},
                            {"x0": {"IRI": "x0"}, "": {"IRI": "x1"}, 23: "test", "__id": "test"},
                            {"test": ["test1", "test2", "test3"]}
                            ])
  def test_save_data_hierarchy_should_do_expected(self,
                                            mocker,
                                            data_hierarchy_document,
                                            configuration_extended: configuration_extended,
                                            request):
    doc = request.getfixturevalue(data_hierarchy_document) \
      if data_hierarchy_document and type(data_hierarchy_document) is str \
      else data_hierarchy_document
    mocker.patch.object(configuration_extended, 'data_hierarchy_document', create=True)
    if doc:
      mocker.patch.object(configuration_extended, 'data_hierarchy_types', dict(data_hierarchy_document), create=True)
      configuration_extended.data_hierarchy_document.__setitem__.side_effect = doc.__setitem__
      configuration_extended.data_hierarchy_document.__getitem__.side_effect = doc.__getitem__
      configuration_extended.data_hierarchy_document.__iter__.side_effect = doc.__iter__
      configuration_extended.data_hierarchy_document.__contains__.side_effect = doc.__contains__
      configuration_extended.data_hierarchy_document.__delitem__.side_effect = doc.__delitem__
      configuration_extended.data_hierarchy_document.keys.side_effect = doc.keys

    mocker.patch.object(configuration_extended.logger, 'info')
    mock_show_message = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.show_message', return_value=QMessageBox.Yes)
    mock_is_instance = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.isinstance')
    mock_check_data_hierarchy_types = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.check_data_hierarchy_types',
      return_value=(None, None))
    mock_db_init_views = mocker.patch.object(configuration_extended.database,
                                             'initDocTypeViews', return_value=None)
    assert configuration_extended.save_data_hierarchy() is None, "Nothing should be returned"

    if doc:
      for item in doc:
        mock_is_instance.assert_any_call(doc[item], dict)
        if isinstance(doc[item], dict):
          configuration_extended.data_hierarchy_document.__delitem__.assert_any_call(item)
      for item in configuration_extended.data_hierarchy_types:
        configuration_extended.data_hierarchy_document.__setitem__.assert_any_call(item,
                                                                             configuration_extended.data_hierarchy_types[
                                                                               item])
    mock_check_data_hierarchy_types.assert_called_once_with(configuration_extended.data_hierarchy_types)
    configuration_extended.logger.info.assert_called_once_with("User clicked the save button..")
    configuration_extended.data_hierarchy_document.save.assert_called_once()
    mock_db_init_views.assert_called_once_with(16)
    mock_show_message.assert_called_once_with('Save will close the tool and restart the Pasta Application (Yes/No?)',
                                               QMessageBox.Question,
                                               QMessageBox.No | QMessageBox.Yes,
                                               QMessageBox.Yes)

  @pytest.mark.parametrize("data_hierarchy_document",
                           [None,
                            {"x0": {"IRI": "x0"}, "": {"IRI": "x1"}},
                            {"x0": {"IRI": "x0"}, "": {"IRI": "x1"}, 23: "test", "__id": "test"},
                            {"test": ["test1", "test2", "test3"]}
                            ])
  def test_cancel_save_data_hierarchy_should_do_expected(self,
                                            mocker,
                                            data_hierarchy_document,
                                            configuration_extended: configuration_extended,
                                            request):
    doc = request.getfixturevalue(data_hierarchy_document) \
      if data_hierarchy_document and type(data_hierarchy_document) is str \
      else data_hierarchy_document
    mocker.patch.object(configuration_extended, 'data_hierarchy_document', create=True)
    if doc:
      mocker.patch.object(configuration_extended, 'data_hierarchy_types', dict(data_hierarchy_document), create=True)
      configuration_extended.data_hierarchy_document.__setitem__.side_effect = doc.__setitem__
      configuration_extended.data_hierarchy_document.__getitem__.side_effect = doc.__getitem__
      configuration_extended.data_hierarchy_document.__iter__.side_effect = doc.__iter__
      configuration_extended.data_hierarchy_document.__contains__.side_effect = doc.__contains__
      configuration_extended.data_hierarchy_document.__delitem__.side_effect = doc.__delitem__
      configuration_extended.data_hierarchy_document.keys.side_effect = doc.keys

    mocker.patch.object(configuration_extended.logger, 'info')
    mock_show_message = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.show_message', return_value=QMessageBox.No)
    mock_is_instance = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.isinstance')
    mock_check_data_hierarchy_types = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.check_data_hierarchy_types',
      return_value=(None, None))
    mock_db_init_views = mocker.patch.object(configuration_extended.database,
                                             'initDocTypeViews', return_value=None)
    assert configuration_extended.save_data_hierarchy() is None, "Nothing should be returned"

    if doc:
      for item in doc:
        mock_is_instance.assert_not_called()
        if isinstance(doc[item], dict):
          configuration_extended.data_hierarchy_document.__delitem__.assert_not_called()
      for item in configuration_extended.data_hierarchy_types:
        configuration_extended.data_hierarchy_document.__setitem__.assert_not_called()
    mock_check_data_hierarchy_types.assert_called_once_with(configuration_extended.data_hierarchy_types)
    configuration_extended.logger.info.assert_called_once_with("User clicked the save button..")
    configuration_extended.data_hierarchy_document.save.assert_not_called()
    mock_db_init_views.assert_not_called()
    mock_show_message.assert_called_once_with('Save will close the tool and restart the Pasta Application (Yes/No?)',
                                               QMessageBox.Question,
                                               QMessageBox.No | QMessageBox.Yes,
                                               QMessageBox.Yes)

  def test_save_data_hierarchy_with_missing_metadata_should_skip_save_and_show_message(self,
                                                                                   mocker,
                                                                                   data_hierarchy_doc_mock,
                                                                                   configuration_extended: configuration_extended):
    mocker.patch.object(configuration_extended, 'data_hierarchy_types', create=True)
    configuration_extended.data_hierarchy_document.__setitem__.side_effect = data_hierarchy_doc_mock.__setitem__
    configuration_extended.data_hierarchy_document.__getitem__.side_effect = data_hierarchy_doc_mock.__getitem__
    configuration_extended.data_hierarchy_document.__iter__.side_effect = data_hierarchy_doc_mock.__iter__
    configuration_extended.data_hierarchy_document.__contains__.side_effect = data_hierarchy_doc_mock.__contains__

    log_info_spy = mocker.patch.object(configuration_extended.logger, 'info')
    log_warn_spy = mocker.patch.object(configuration_extended.logger, 'warning')
    mock_show_message = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.show_message')
    missing_metadata = ({
                       'Structure level 0': {'metadata group1': ['-tags']},
                       'Structure level 1': {'default': ['-tags']},
                       'Structure level 2': {'default': ['-tags']},
                       'instrument': {'default': ['-tags']}},
                     {
                       'Structure level 0': ['metadata group1', '-tags'],
                       'instrument': ['metadata group1', '-tags']
                     })
    mock_check_data_hierarchy_document_types = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.check_data_hierarchy_types',
      return_value=missing_metadata)
    mock_get_missing_metadata_message = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.get_missing_metadata_message',
      return_value="Missing message")
    assert configuration_extended.save_data_hierarchy() is None, "Nothing should be returned"
    log_info_spy.assert_called_once_with("User clicked the save button..")
    mock_check_data_hierarchy_document_types.assert_called_once_with(configuration_extended.data_hierarchy_types)
    mock_get_missing_metadata_message.assert_called_once_with(missing_metadata[0], missing_metadata[1])
    mock_show_message.assert_called_once_with("Missing message", QMessageBox.Warning)
    log_warn_spy.assert_called_once_with("Missing message")

  @pytest.mark.parametrize("new_title, new_displayed_title, data_hierarchy_document, data_hierarchy_types", [
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
                                              new_displayed_title,
                                              data_hierarchy_document,
                                              data_hierarchy_types,
                                              configuration_extended: configuration_extended):
    mocker.patch.object(configuration_extended, 'data_hierarchy_document', create=True)
    mocker.patch.object(configuration_extended, 'data_hierarchy_types', create=True)
    mock_show_message = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.show_message')
    mock_log_info = mocker.patch.object(configuration_extended.logger, 'info')
    mock_log_error = mocker.patch.object(configuration_extended.logger, 'error')
    mock_log_warn = mocker.patch.object(configuration_extended.logger, 'warning')
    if data_hierarchy_document:
      configuration_extended.data_hierarchy_document.__setitem__.side_effect = data_hierarchy_document.__setitem__
      configuration_extended.data_hierarchy_document.__getitem__.side_effect = data_hierarchy_document.__getitem__
      configuration_extended.data_hierarchy_document.__iter__.side_effect = data_hierarchy_document.__iter__
      configuration_extended.data_hierarchy_document.__contains__.side_effect = data_hierarchy_document.__contains__
      configuration_extended.data_hierarchy_document.get.side_effect = data_hierarchy_document.get
      configuration_extended.data_hierarchy_document.keys.side_effect = data_hierarchy_document.keys
      configuration_extended.data_hierarchy_document.pop.side_effect = data_hierarchy_document.pop
    if data_hierarchy_types is not None:
      configuration_extended.data_hierarchy_types.__setitem__.side_effect = data_hierarchy_types.__setitem__
      configuration_extended.data_hierarchy_types.__getitem__.side_effect = data_hierarchy_types.__getitem__
      configuration_extended.data_hierarchy_types.__iter__.side_effect = data_hierarchy_types.__iter__
      configuration_extended.data_hierarchy_types.__contains__.side_effect = data_hierarchy_types.__contains__
      configuration_extended.data_hierarchy_types.get.side_effect = data_hierarchy_types.get
      configuration_extended.data_hierarchy_types.keys.side_effect = data_hierarchy_types.keys
      configuration_extended.data_hierarchy_types.pop.side_effect = data_hierarchy_types.pop
      configuration_extended.data_hierarchy_types.__len__.side_effect = data_hierarchy_types.__len__

    if data_hierarchy_document is None:
      mocker.patch.object(configuration_extended, 'data_hierarchy_document', None, create=True)
    if data_hierarchy_types is None:
      mocker.patch.object(configuration_extended, 'data_hierarchy_types', None, create=True)

    if data_hierarchy_document is None or data_hierarchy_types is None or new_title in data_hierarchy_document:
      if data_hierarchy_document is None or data_hierarchy_types is None:
        with pytest.raises(GenericException,
                           match="Null data_hierarchy_document/data_hierarchy_types, erroneous app state"):
          assert configuration_extended.create_new_type(new_title, new_displayed_title) is None, "Nothing should be returned"
          mock_log_error.assert_called_once_with("Null data_hierarchy_document/data_hierarchy_types, erroneous app state")
      else:
        assert configuration_extended.create_new_type(new_title, new_displayed_title) is None, "Nothing should be returned"
        mock_show_message.assert_called_once_with(f"Type (title: {new_title} "
                                                  f"displayed title: {new_displayed_title}) cannot be added "
                                                  f"since it exists in DB already....", QMessageBox.Warning)
    else:
      if new_title is None:
        assert configuration_extended.create_new_type(None, new_displayed_title) is None, "Nothing should be returned"
        mock_show_message.assert_called_once_with("Enter non-null/valid title!!.....", QMessageBox.Warning)
        mock_log_warn.assert_called_once_with("Enter non-null/valid title!!.....")
      else:
        assert configuration_extended.create_new_type(new_title, new_displayed_title) is None, "Nothing should be returned"
        mock_log_info.assert_called_once_with("User created a new type and added "
                                              "to the data_hierarchy document: Title: {%s}, Displayed Title: {%s}", new_title,
                                              new_displayed_title)

        (configuration_extended.data_hierarchy_types
         .__setitem__.assert_called_once_with(new_title, generate_empty_type(new_displayed_title)))
        assert configuration_extended.typeComboBox.clear.call_count == 2, "ComboBox should be cleared twice"
        assert configuration_extended.typeComboBox.addItems.call_count == 2, "ComboBox addItems should be called twice"
        configuration_extended.typeComboBox.addItems.assert_called_with(
          get_types_for_display(configuration_extended.data_hierarchy_types.keys()))

  @pytest.mark.parametrize("instance_exists", [True, False])
  def test_get_gui_should_do_expected(self,
                                      mocker,
                                      configuration_extended: configuration_extended,
                                      instance_exists):
    mock_form = mocker.MagicMock()
    mock_sys_argv = mocker.patch(
      "pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.sys.argv")
    mock_new_app_inst = mocker.patch("PySide6.QtWidgets.QApplication")
    mock_exist_app_inst = mocker.patch("PySide6.QtWidgets.QApplication")
    mock_form_instance = mocker.patch("PySide6.QtWidgets.QDialog")
    mock_database = mocker.patch("pasta_eln.database.Database")

    mocker.patch.object(QApplication, 'instance', return_value=mock_exist_app_inst if instance_exists else None)
    mocker.patch.object(mock_form, 'instance', mock_form_instance, create=True)
    spy_new_app_inst = mocker.patch.object(QApplication, '__new__', return_value=mock_new_app_inst)
    spy_form_inst = mocker.patch.object(DataHierarchyEditorDialog, '__new__', return_value=mock_form)

    (app, form_inst, form) = get_gui(mock_database)
    spy_form_inst.assert_called_once_with(DataHierarchyEditorDialog, mock_database)
    if instance_exists:
      assert app is mock_exist_app_inst, "Should return existing instance"
      assert form_inst is mock_form_instance, "Should return existing instance"
      assert form is mock_form, "Should return existing instance"
    else:
      spy_new_app_inst.assert_called_once_with(QApplication, mock_sys_argv)
      assert app is mock_new_app_inst, "Should return new instance"
      assert form_inst is mock_form_instance, "Should return existing instance"
      assert form is mock_form, "Should return existing instance"

  @pytest.mark.parametrize("hidden", [True, False])
  def test_show_hide_attachments_table_do_expected(self,
                                                   mocker,
                                                   configuration_extended: configuration_extended,
                                                   hidden):
    spy_table_view_set_visible = mocker.patch.object(configuration_extended.typeAttachmentsTableView, 'setVisible')
    spy_table_view_is_visible = mocker.patch.object(configuration_extended.typeAttachmentsTableView, 'isVisible',
                                                    return_value=hidden)
    spy_add_attachment_set_visible = mocker.patch.object(configuration_extended.addAttachmentPushButton, 'setVisible')
    spy_add_attachment_is_visible = mocker.patch.object(configuration_extended.addAttachmentPushButton, 'isVisible',
                                                        return_value=hidden)

    assert configuration_extended.show_hide_attachments_table() is None, "Nothing should be returned"
    spy_table_view_set_visible.assert_called_once_with(not hidden)
    spy_table_view_is_visible.assert_called_once_with()
    spy_add_attachment_set_visible.assert_called_once_with(not hidden)
    spy_add_attachment_is_visible.assert_called_once_with()

  def test_set_iri_lookup_action_do_expected(self,
                                             mocker,
                                             configuration_extended: configuration_extended):
    mock_actions = [mocker.MagicMock(), mocker.MagicMock()]
    configuration_extended.typeIriLineEdit.actions.return_value = mock_actions
    mock_is_instance = mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.isinstance',
                                    return_value=True)
    mock_is_lookup_iri_action = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.LookupIriAction')

    assert configuration_extended.set_iri_lookup_action("default") is None, "Nothing should be returned"
    mock_is_instance.assert_has_calls(
      [mocker.call(mock_actions[0], mock_is_lookup_iri_action),
       mocker.call(mock_actions[1], mock_is_lookup_iri_action)])
    mock_is_lookup_iri_action.assert_called_once_with(parent_line_edit=configuration_extended.typeIriLineEdit,
                                                      lookup_term="default")
    configuration_extended.typeIriLineEdit.addAction.assert_called_once_with(mock_is_lookup_iri_action.return_value,
                                                                             QLineEdit.TrailingPosition)

  def test_check_and_disable_delete_button_should_do_expected(self,
                                                              mocker,
                                                              configuration_extended: configuration_extended):
    mock_can_delete_type = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.can_delete_type', return_value=True)
    mock_data_hierarchy_types = mocker.MagicMock()
    mocker.patch.object(configuration_extended, 'data_hierarchy_types', mock_data_hierarchy_types)
    mock_data_hierarchy_types.keys.return_value = ['one', 'two']
    assert configuration_extended.check_and_disable_delete_button("three") is None, "Nothing should be returned"
    configuration_extended.deleteTypePushButton.setEnabled.assert_called_once_with(True)
    mock_can_delete_type.assert_called_once_with(['one', 'two'], "three")
