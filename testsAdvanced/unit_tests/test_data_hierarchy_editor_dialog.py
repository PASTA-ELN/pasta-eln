#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_editor_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from functools import reduce
from unittest.mock import MagicMock, patch

import pytest
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
from _pytest.mark import param

from pasta_eln.GUI.data_hierarchy.attachments_tableview_data_model import AttachmentsTableViewModel
from pasta_eln.GUI.data_hierarchy.constants import ATTACHMENT_TABLE_DELETE_COLUMN_INDEX, \
  ATTACHMENT_TABLE_REORDER_COLUMN_INDEX, METADATA_TABLE_DELETE_COLUMN_INDEX, \
  METADATA_TABLE_IRI_COLUMN_INDEX, METADATA_TABLE_REORDER_COLUMN_INDEX, METADATA_TABLE_REQUIRED_COLUMN_INDEX
from pasta_eln.GUI.data_hierarchy.create_type_dialog import CreateTypeDialog, TypeDialog
from pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog import DataHierarchyEditorDialog, get_gui
from pasta_eln.GUI.data_hierarchy.delete_column_delegate import DeleteColumnDelegate
from pasta_eln.GUI.data_hierarchy.document_null_exception import DocumentNullException
from pasta_eln.GUI.data_hierarchy.generic_exception import GenericException
from pasta_eln.GUI.data_hierarchy.key_not_found_exception import \
  KeyNotFoundException
from pasta_eln.GUI.data_hierarchy.mandatory_column_delegate import MandatoryColumnDelegate
from pasta_eln.GUI.data_hierarchy.metadata_tableview_data_model import MetadataTableViewModel
from pasta_eln.GUI.data_hierarchy.reorder_column_delegate import ReorderColumnDelegate
from pasta_eln.GUI.data_hierarchy.utility_functions import get_types_for_display


@pytest.fixture
def configuration_extended(mocker) -> DataHierarchyEditorDialog:
  mock_pasta_db = mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.DatabaseAPI')
  mock_pasta_db.return_value.get_data_hierarchy_document.return_value = MagicMock()
  mocker.patch('pasta_eln.GUI.data_hierarchy.create_type_dialog.logging.getLogger')
  mocker.patch(
    'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog_base.Ui_DataHierarchyEditorDialogBase.setupUi')
  mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.adjust_data_hierarchy_data_to_v4')
  mocker.patch.object(QDialog, '__new__')
  mocker.patch.object(MetadataTableViewModel, '__new__')
  mocker.patch.object(AttachmentsTableViewModel, '__new__')
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
  mocker.patch.object(DataHierarchyEditorDialog, 'editTypePushButton', create=True)
  mocker.patch.object(DataHierarchyEditorDialog, 'cancelPushButton', create=True)
  mocker.patch.object(DataHierarchyEditorDialog, 'helpPushButton', create=True)
  mocker.patch.object(DataHierarchyEditorDialog, 'attachmentsShowHidePushButton', create=True)
  mocker.patch.object(DataHierarchyEditorDialog, 'typeComboBox', create=True)
  mocker.patch.object(DataHierarchyEditorDialog, 'metadataGroupComboBox', create=True)
  mocker.patch.object(DataHierarchyEditorDialog, 'metadata_table_data_model', create=True)
  mocker.patch.object(DataHierarchyEditorDialog, 'attachments_table_data_model', create=True)
  mocker.patch.object(DataHierarchyEditorDialog, 'webbrowser', create=True)
  mocker.patch.object(DataHierarchyEditorDialog, 'instance', create=True)
  mocker.patch.object(DataHierarchyEditorDialog, 'typeDisplayedTitleLineEdit', create=True)
  mocker.patch.object(DataHierarchyEditorDialog, 'typeIriLineEdit', create=True)
  mocker.patch.object(DataHierarchyEditorDialog, 'delete_column_delegate_metadata_table', create=True)
  mocker.patch.object(DataHierarchyEditorDialog, 'reorder_column_delegate_metadata_table', create=True)
  mocker.patch.object(DataHierarchyEditorDialog, 'delete_column_delegate_attach_table', create=True)
  mocker.patch.object(DataHierarchyEditorDialog, 'reorder_column_delegate_attach_table', create=True)
  mocker.patch.object(TypeDialog, '__new__')
  return DataHierarchyEditorDialog()


class TestDataHierarchyEditorDialog(object):

  def test_instantiation_should_succeed(self,
                                        mocker):
    mock_pasta_db = mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.DatabaseAPI')
    mocker.patch('pasta_eln.GUI.data_hierarchy.create_type_dialog.logging.getLogger')
    mock_setup_ui = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog_base.Ui_DataHierarchyEditorDialogBase.setupUi')
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.adjust_data_hierarchy_data_to_v4')
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
    mock_edit_type_dialog = mocker.MagicMock()
    mock_create = mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.CreateTypeDialog',
                               return_value=mock_create_type_dialog)
    mock_edit = mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.EditTypeDialog',
                             return_value=mock_edit_type_dialog)
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
    mocker.patch.object(DataHierarchyEditorDialog, 'type_create_accepted_callback', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'type_create_rejected_callback', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'type_edit_accepted_callback', create=True)
    mocker.patch.object(DataHierarchyEditorDialog, 'type_edit_rejected_callback', create=True)
    mock_setup_slots = mocker.patch.object(DataHierarchyEditorDialog, 'setup_slots', create=True)
    mock_load_data_hierarchy_data = mocker.patch.object(DataHierarchyEditorDialog, 'load_data_hierarchy_data',
                                                        create=True)
    mocker.patch.object(TypeDialog, '__new__')
    config_instance = DataHierarchyEditorDialog()
    assert config_instance, "DataHierarchyEditorDialog should be created"
    assert config_instance.type_changed_signal == mock_signal, "Signal should be created"
    mock_setup_ui.assert_called_once_with(mock_dialog)
    assert config_instance.database is mock_pasta_db.return_value, "Database should be set"
    config_instance.database.get_data_hierarchy_document.assert_called_once()
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

    mock_create.assert_called_once_with(config_instance.type_create_accepted_callback,
                                        config_instance.type_create_rejected_callback)
    assert config_instance.create_type_dialog == mock_create_type_dialog, "CreateTypeDialog should be set"
    mock_edit.assert_called_once_with(config_instance.type_edit_accepted_callback,
                                      config_instance.type_edit_rejected_callback)
    assert config_instance.edit_type_dialog == mock_edit_type_dialog, "EditTypeDialog should be set"
    mock_setup_slots.assert_called_once_with()

    config_instance.addAttachmentPushButton.hide.assert_called_once_with()
    config_instance.typeAttachmentsTableView.hide.assert_called_once_with()
    mock_load_data_hierarchy_data.assert_called_once_with()

  def test_instantiation_with_database_with_null_document_should_throw_exception(self,
                                                                                 mocker):
    mock_pasta_db = mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.DatabaseAPI')
    mocker.patch('pasta_eln.GUI.data_hierarchy.create_type_dialog.logging.getLogger')
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.Ui_DataHierarchyEditorDialogBase.setupUi')
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.adjust_data_hierarchy_data_to_v4')
    mocker.patch.object(QDialog, '__new__')
    mock_pasta_db.return_value.get_data_hierarchy_document.return_value = None
    with pytest.raises(DocumentNullException, match="Null data_hierarchy document in db instance"):
      DataHierarchyEditorDialog()

  @pytest.mark.parametrize(
    "new_type_selected, data_hierarchy_types, expected_metadata_keys, expected_attachments, test_id",
    [
      # Success path test cases
      ("type1", {"type1": {"meta": {"key1": "value1"}, "attachments": ["attachment1"]}}, ["key1"], ["attachment1"],
       "success_path_type1"),
      ("type2", {"type2": {"meta": {"key2": "value2"}, "attachments": ["attachment2"]}}, ["key2"], ["attachment2"],
       "success_path_type2"),

      # Edge case: Empty metadata
      ("type3", {"type3": {"meta": {}, "attachments": []}}, [], [], "edge_case_empty_metadata"),

      # Error case: Key not found
      ("missing_type", {"type1": {"meta": {"key1": "value1"}, "attachments": ["attachment1"]}}, None, None,
       "error_case_key_not_found"),
    ],
    ids=[
      "success_path_type1",
      "success_path_type2",
      "edge_case_empty_metadata",
      "error_case_key_not_found"
    ]
  )
  def test_type_combo_box_changed(self,
                                  mocker,
                                  configuration_extended: configuration_extended,
                                  new_type_selected,
                                  data_hierarchy_types,
                                  expected_metadata_keys,
                                  expected_attachments,
                                  test_id):
    # Arrange
    mocker.resetall()
    configuration_extended.data_hierarchy_types = data_hierarchy_types
    configuration_extended.clear_ui = mocker.MagicMock()
    configuration_extended.type_changed_signal = mocker.MagicMock()
    configuration_extended.attachments_table_data_model = mocker.MagicMock()
    configuration_extended.metadataGroupComboBox = mocker.MagicMock()

    # Act
    if test_id == "error_case_key_not_found":
      with pytest.raises(KeyNotFoundException):
        configuration_extended.type_combo_box_changed(new_type_selected)
    else:
      configuration_extended.type_combo_box_changed(new_type_selected)

      # Assert
      configuration_extended.logger.info.assert_called_once_with("New type selected in UI: {%s}", new_type_selected)
      configuration_extended.clear_ui.assert_called_once()
      configuration_extended.type_changed_signal.emit.assert_called_once_with(new_type_selected)
      configuration_extended.attachments_table_data_model.update.assert_called_once_with(expected_attachments)
      configuration_extended.metadataGroupComboBox.addItems.assert_called_once_with(expected_metadata_keys)
      configuration_extended.metadataGroupComboBox.setCurrentIndex.assert_called_once_with(0)

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
    ("metadata group2", {0: "x0"},
     {"default": [], "metadata group1": [{"name": "key", "value": "value"}], "metadata group2": []}),
    ("metadata group1", {0: "x0"},
     {"default": [], "metadata group1": [{"name": None, "value": None}], "metadata group2": None}),
    ("metadata group2", {0: "x0"},
     {"default": [], "metadata group1": [{"name": None, "value": None}], "metadata group2": None}),
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
    (None, "x0", {"x0": {"title": "x0"}, "x1": {"title": "x1"}}),
    ("new_displayed_title_2", "x1", {"x0": {"title": "x0"}, "x1": {"title": "x1"}}),
    ("new_displayed_title_2", "instrument", {"x0": {"title": "x0"}, "instrument": {"title": "x1"}}),
    ("type_new_displayed_title", "subtask4", {"x0": {"title": "x0"}, "subtask5": {"title": "x1"}}),
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
      assert configuration_extended.update_type_displayed_title(
        modified_type_displayed_title) is None, "Nothing should be returned"
      if data_hierarchy_types is not None and current_type in data_hierarchy_types:
        get_data_hierarchy_types_spy.assert_called_once_with(current_type, {})
        assert data_hierarchy_types[current_type]["title"] == modified_type_displayed_title

  @pytest.mark.parametrize("modified_type_iri, current_type, data_hierarchy_types", [
    (None, None, None),
    ("new_url", None, None),
    (None, "x0", {"x0": {"title": "x0"}, "x1": {"title": "x1"}}),
    ("new_url_2", "x1", {"x0": {"title": "x0"}, "x1": {"title": "x1"}}),
    ("new_url_2", "instrument", {"x0": {"title": "x0"}, "instrument": {"title": "x1"}}),
    ("type_new_url", "subtask4", {"x0": {"title": "x0"}, "subtask5": {"title": "x1"}}),
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
        get_data_hierarchy_types_spy.assert_called_once_with(current_type, {})
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

  @pytest.mark.parametrize(
    "data_hierarchy_types, expected_items, expected_index",
    [
      # Happy path with multiple types
      pytest.param(
        {"type1": {}, "type2": {}, "type3": {}},
        ["type1", "type2", "type3"],
        2,
        id="happy_path_multiple_types"
      ),
      # Edge case with a single type
      pytest.param(
        {"type1": {}},
        ["type1"],
        0,
        id="edge_case_single_type"
      ),
      # Edge case with no types
      pytest.param(
        {},
        [],
        -1,
        id="edge_case_no_types"
      ),
    ]
  )
  def test_type_create_accepted_callback(self,
                                         mocker,
                                         configuration_extended: configuration_extended,
                                         data_hierarchy_types, expected_items, expected_index):
    # Arrange
    mocker.resetall()
    configuration_extended.data_hierarchy_types = data_hierarchy_types

    # Act
    configuration_extended.type_create_accepted_callback()

    # Assert
    configuration_extended.typeComboBox.clear.assert_called_once()
    configuration_extended.typeComboBox.addItems.assert_called_once_with(expected_items)
    configuration_extended.typeComboBox.setCurrentIndex.assert_called_once_with(expected_index)
    configuration_extended.create_type_dialog.clear_ui.assert_called_once()

  @pytest.mark.parametrize(
    "data_hierarchy_types, expected_message, test_id",
    [
      (None, "Load the data hierarchy data first....", "error_case_none"),
      ("not_a_dict", "Load the data hierarchy data first....", "error_case_not_a_dict"),
    ],
    ids=[
      "error_case_none",
      "error_case_not_a_dict"
    ]
  )
  def test_type_create_accepted_callback_error_cases(self,
                                                     mocker,
                                                     configuration_extended: configuration_extended,
                                                     data_hierarchy_types, expected_message, test_id):
    # Arrange
    mocker.resetall()
    configuration_extended.data_hierarchy_types = data_hierarchy_types

    with patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.show_message') as mock_show_message:
      # Act
      configuration_extended.type_create_accepted_callback()

      # Assert
      mock_show_message.assert_called_once_with(expected_message, QMessageBox.Icon.Warning)
      configuration_extended.typeComboBox.clear.assert_not_called()
      configuration_extended.typeComboBox.addItems.assert_not_called()
      configuration_extended.typeComboBox.setCurrentIndex.assert_not_called()
      configuration_extended.create_type_dialog.clear_ui.assert_not_called()

  @pytest.mark.parametrize(
    "clear_ui_side_effect, expected_clear_ui_calls, test_id",
    [
      (None, 1, "success_path"),  # Happy path: clear_ui works without issues
      (Exception("Clear UI failed"), 1, "clear_ui_exception"),  # Edge case: clear_ui raises an exception
    ],
    ids=[
      "success_path",
      "clear_ui_exception"
    ]
  )
  def test_type_create_rejected_callback(self,
                                         configuration_extended: configuration_extended,
                                         clear_ui_side_effect, expected_clear_ui_calls, test_id):
    # Arrange
    configuration_extended.create_type_dialog.clear_ui.side_effect = clear_ui_side_effect

    # Act
    try:
      configuration_extended.type_create_rejected_callback()
    except Exception:
      pass  # We are testing if the method handles exceptions gracefully

    # Assert
    assert configuration_extended.create_type_dialog.clear_ui.call_count == expected_clear_ui_calls

  @pytest.mark.parametrize(
    "mock_dialog, expected_clear_call",
    [
      # Happy path test case
      pytest.param(MagicMock(spec=CreateTypeDialog), True, id="success_path"),

      # Edge case: dialog already cleared
      pytest.param(MagicMock(spec=CreateTypeDialog, clear_ui=MagicMock()), True, id="already_cleared"),

      # Error case: dialog is None
      pytest.param(None, False, id="dialog_none")
    ]
  )
  def test_type_edit_accepted_callback(self,
                                       configuration_extended: configuration_extended, mock_dialog,
                                       expected_clear_call):
    # Arrange
    configuration_extended.create_type_dialog = mock_dialog

    # Act
    if mock_dialog is not None:
      configuration_extended.type_edit_accepted_callback()

    # Assert
    if expected_clear_call:
      mock_dialog.clear_ui.assert_called_once()
    else:
      if mock_dialog is not None:
        mock_dialog.clear_ui.assert_not_called()

  @pytest.mark.parametrize(
    "clear_ui_side_effect, expected_clear_ui_call_count, test_id",
    [
      (None, 1, "success_path"),  # Happy path: clear_ui works without issues
      (Exception("Clear UI failed"), 1, "clear_ui_exception"),  # Edge case: clear_ui raises an exception
    ],
    ids=[
      "success_path",
      "clear_ui_exception"
    ]  # Use the test_id as the parameterized test ID
  )
  def test_type_edit_rejected_callback(self,
                                       configuration_extended: configuration_extended, clear_ui_side_effect,
                                       expected_clear_ui_call_count,
                                       test_id):
    # Arrange
    configuration_extended.create_type_dialog.clear_ui.side_effect = clear_ui_side_effect

    # Act
    try:
      configuration_extended.type_edit_rejected_callback()
    except Exception:
      pass  # Ignore exceptions for this test case

    # Assert
    assert configuration_extended.create_type_dialog.clear_ui.call_count == expected_clear_ui_call_count

  @pytest.mark.parametrize(
    "data_hierarchy_types, data_hierarchy_loaded, expected_message, test_id",
    [
      # Happy path: data hierarchy is loaded and types are available
      (["type1", "type2"], True, None, "success_path_with_types"),

      # Edge case: data hierarchy is loaded but no types are available
      ([], True, None, "edge_case_no_types"),

      # Error case: data hierarchy is not loaded
      (None, False, "Load the data hierarchy data first...", "error_case_not_loaded"),

      # Error case: data hierarchy is loaded but types are None
      (None, True, "Load the data hierarchy data first...", "error_case_types_none"),
    ],
    ids=[
      "success_path_with_types",
      "edge_case_no_types",
      "error_case_not_loaded",
      "error_case_types_none"
    ]
  )
  def test_show_create_type_dialog(self,
                                   configuration_extended: configuration_extended, data_hierarchy_types,
                                   data_hierarchy_loaded, expected_message, test_id):
    # Arrange
    configuration_extended.data_hierarchy_types = data_hierarchy_types
    configuration_extended.data_hierarchy_loaded = data_hierarchy_loaded

    with patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.show_message') as mock_show_message:
      # Act
      configuration_extended.show_create_type_dialog()

      # Assert
      if expected_message:
        mock_show_message.assert_called_once_with(expected_message, QMessageBox.Icon.Warning)
        configuration_extended.create_type_dialog.set_data_hierarchy_types.assert_not_called()
        configuration_extended.create_type_dialog.show.assert_not_called()
      else:
        mock_show_message.assert_not_called()
        configuration_extended.create_type_dialog.set_data_hierarchy_types.assert_called_once_with(data_hierarchy_types)
        configuration_extended.create_type_dialog.show.assert_called_once()

  @pytest.mark.parametrize("data_hierarchy_types, data_hierarchy_loaded, current_text, expected_message, test_id", [
    # Happy path
    ({'type1': 'Type 1 Data'}, True, 'type1', None, "happy_path_type1"),
    ({'type2': 'Type 2 Data'}, True, 'type2', None, "happy_path_type2"),

    # Edge cases
    ({}, True, '', None, "edge_case_empty_type"),
    ({'type1': 'Type 1 Data'}, True, '', None, "edge_case_no_selection"),

    # Error cases
    (None, True, 'type1', "Load the data hierarchy data first...", "error_case_no_data_hierarchy"),
    ({'type1': 'Type 1 Data'}, False, 'type1', "Load the data hierarchy data first...", "error_case_not_loaded"),
  ])
  def test_show_edit_type_dialog(self,
                                 mocker,
                                 configuration_extended: configuration_extended,
                                 data_hierarchy_types, data_hierarchy_loaded,
                                 current_text, expected_message, test_id):
    # Arrange
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.adapt_type', side_effect=lambda x: x)
    mock_show_message = mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.show_message')
    configuration_extended.data_hierarchy_types = data_hierarchy_types
    configuration_extended.data_hierarchy_loaded = data_hierarchy_loaded
    configuration_extended.typeComboBox.currentText.return_value = current_text

    # Act
    configuration_extended.show_edit_type_dialog()

    # Assert
    if expected_message:
      mock_show_message.assert_called_once_with(expected_message, QMessageBox.Icon.Warning)
    else:
      configuration_extended.edit_type_dialog.set_selected_data_hierarchy_type_name.assert_called_once_with(
        current_text)
      configuration_extended.edit_type_dialog.set_selected_data_hierarchy_type.assert_called_once_with(
        data_hierarchy_types.get(current_text, {}))
      configuration_extended.edit_type_dialog.show.assert_called_once()

  @pytest.mark.parametrize("button_name, method_name", [
    ("addMetadataRowPushButton", "metadata_table_data_model.add_data_row"),
    ("addAttachmentPushButton", "attachments_table_data_model.add_data_row"),
    ("saveDataHierarchyPushButton", "save_data_hierarchy"),
    ("addMetadataGroupPushButton", "add_new_metadata_group"),
    ("deleteMetadataGroupPushButton", "delete_selected_metadata_group"),
    ("deleteTypePushButton", "delete_selected_type"),
    ("addTypePushButton", "show_create_type_dialog"),
    ("editTypePushButton", "show_edit_type_dialog"),
    ("cancelPushButton", "instance.close"),
    ("attachmentsShowHidePushButton", "show_hide_attachments_table"),
  ], ids=[
    "Add Metadata Row Button",
    "Add Attachment Button",
    "Save Data Hierarchy Button",
    "Add Metadata Group Button",
    "Delete Metadata Group Button",
    "Delete Type Button",
    "Add Type Button",
    "Edit Type Button",
    "Cancel Button",
    "Show/Hide Attachments Button"
  ])
  def test_button_connections(self, mocker, configuration_extended: configuration_extended, button_name, method_name):
    # Arrange
    mocker.resetall()
    button = getattr(configuration_extended, button_name)
    method = reduce(getattr, method_name.split("."), configuration_extended)

    # Act
    configuration_extended.setup_slots()

    # Assert
    button.clicked.connect.assert_called_once_with(method)

  @pytest.mark.parametrize("combo_box_name, method_name", [
    ("typeComboBox", "type_combo_box_changed"),
    ("metadataGroupComboBox", "metadata_group_combo_box_changed"),
  ], ids=[
    "Type ComboBox",
    "Metadata Group ComboBox"
  ])
  def test_combobox_connections(self, mocker, configuration_extended: configuration_extended, combo_box_name,
                                method_name):
    # Arrange
    mocker.resetall()
    combo_box = getattr(configuration_extended, combo_box_name)
    method = getattr(configuration_extended, method_name)

    # Act
    configuration_extended.setup_slots()

    # Assert
    combo_box.currentTextChanged.connect.assert_called_once_with(method)

  @pytest.mark.parametrize("delegate_name, signal_name, method_name", [
    ("delete_column_delegate_metadata_table", "delete_clicked_signal", "metadata_table_data_model.delete_data"),
    ("reorder_column_delegate_metadata_table", "re_order_signal", "metadata_table_data_model.re_order_data"),
    ("delete_column_delegate_attach_table", "delete_clicked_signal", "attachments_table_data_model.delete_data"),
    ("reorder_column_delegate_attach_table", "re_order_signal", "attachments_table_data_model.re_order_data"),
  ], ids=[
    "Delete Column Delegate Metadata Table",
    "Reorder Column Delegate Metadata Table",
    "Delete Column Delegate Attach Table",
    "Reorder Column Delegate Attach Table"
  ])
  def test_delegate_connections(self, mocker, configuration_extended: configuration_extended, delegate_name,
                                signal_name, method_name):
    # Arrange
    mocker.resetall()
    delegate = getattr(configuration_extended, delegate_name)
    signal = getattr(delegate, signal_name)
    method = reduce(getattr, method_name.split("."), configuration_extended)

    # Act
    configuration_extended.setup_slots()

    # Assert
    signal.connect.assert_any_call(method)

  def test_help_button_connection(self, mocker, configuration_extended: configuration_extended):
    # Arrange
    mocker.resetall()
    # Act
    configuration_extended.setup_slots()
    configuration_extended.helpPushButton.clicked.emit()

    # Assert
    assert configuration_extended.helpPushButton.clicked.connect.call_count == 1

  def test_type_changed_signal_connection(self, mocker, configuration_extended: configuration_extended):
    # Arrange
    mocker.resetall()
    configuration_extended.type_changed_signal = mocker.MagicMock()
    method = configuration_extended.check_and_disable_delete_button

    # Act
    configuration_extended.setup_slots()

    # Assert
    configuration_extended.type_changed_signal.connect.assert_called_once_with(method)

  @pytest.mark.parametrize(
    "data_hierarchy_document, expected_types, expected_items, test_id",
    [
      # Success path with realistic data
      ({"type1": {"key": "value"}, "type2": {"key": "value"}},
       {"type1": {"key": "value"}, "type2": {"key": "value"}},
       ["type1", "type2"],
       "success_path_multiple_types"),

      # Edge case: empty document
      ({},
       {},
       [],
       "edge_case_empty_document"),

      # Edge case: single type
      ({"type1": {"key": "value"}},
       {"type1": {"key": "value"}},
       ["type1"],
       "edge_case_single_type"),

      # Error case: None document
      (None,
       None,
       None,
       "error_case_none_document"),
    ],
    ids=[
      "success_path_multiple_types",
      "edge_case_single_type",
      "edge_case_empty_document",
      "error_case_none_document"
    ]
  )
  def test_load_data_hierarchy_data(self, mocker, configuration_extended: configuration_extended,
                                    data_hierarchy_document, expected_types, expected_items, test_id):
    # Arrange
    mocker.resetall()
    configuration_extended.data_hierarchy_document = data_hierarchy_document

    if data_hierarchy_document is None:
      # Act and Assert
      with pytest.raises(GenericException) as exec_info:
        configuration_extended.load_data_hierarchy_data()
      assert "Null data_hierarchy_document, erroneous app state" in str(exec_info.value)
    else:
      # Act
      with patch(
          'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.adjust_data_hierarchy_data_to_v4') as mock_adjust, \
          patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.get_types_for_display',
                return_value=expected_items) as mock_get_types:
        configuration_extended.load_data_hierarchy_data()

      # Assert
      assert configuration_extended.data_hierarchy_types == expected_types
      assert configuration_extended.data_hierarchy_loaded is True
      configuration_extended.typeComboBox.clear.assert_called_once()
      configuration_extended.typeComboBox.addItems.assert_called_once_with(expected_items)
      configuration_extended.typeComboBox.setCurrentIndex.assert_called_once_with(0)
      mock_adjust.assert_called_once_with(expected_types)
      mock_get_types.assert_called_once_with(list(expected_types.keys()))

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
      return_value=(None, None, None))
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
    configuration_extended.database.save_data_hierarchy_document.assert_called_once_with(
      configuration_extended.data_hierarchy_document)
    mock_show_message.assert_called_once_with("Data hierarchy saved successfully...", QMessageBox.Icon.Information)

  @pytest.mark.parametrize(
    "types_with_missing_metadata, types_with_null_name_metadata, types_with_duplicate_metadata, expected_message, expected_log_warning, expected_log_info",
    [
      # Happy path: No missing, null, or duplicate metadata
      param([], [], [], 'Data hierarchy saved successfully...', False, True,
            id="no_missing_null_duplicate_metadata"),

      # Edge case: Missing metadata
      param(["type1"], [], [], "Missing metadata for types: type1", True, False, id="missing_metadata"),

      # Edge case: Null name metadata
      param([], ["type2"], [], "Null name metadata for types: type2", True, False, id="null_name_metadata"),

      # Edge case: Duplicate metadata
      param([], [], ["type3"], "Duplicate metadata for types: type3", True, False, id="duplicate_metadata"),

      # Error case: All types of metadata issues
      param(["type1"], ["type2"], ["type3"],
            "Missing metadata for types: type1\nNull name metadata for types: type2\nDuplicate metadata for types: type3",
            True, False, id="all_metadata_issues"),
    ]
  )
  def test_save_data_hierarchy_metadata_issues(self,
                                               mocker,
                                               configuration_extended: configuration_extended,
                                               types_with_missing_metadata,
                                               types_with_null_name_metadata,
                                               types_with_duplicate_metadata,
                                               expected_message,
                                               expected_log_warning,
                                               expected_log_info,
                                               request):
    mock_check_data_hierarchy_types = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.check_data_hierarchy_types')
    mock_get_missing_metadata_message = mocker.patch(
      'pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.get_missing_metadata_message')
    mock_show_message = mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.show_message')
    mock_check_data_hierarchy_types.return_value = (
      types_with_missing_metadata, types_with_null_name_metadata, types_with_duplicate_metadata)
    mock_get_missing_metadata_message.return_value = expected_message

    # Act
    configuration_extended.save_data_hierarchy()

    # Assert
    if expected_message:
      if expected_log_info:
        if request.node.callspec.id == "no_missing_null_duplicate_metadata":
          mock_show_message.assert_called_once_with(expected_message, QMessageBox.Icon.Information)
        else:
          mock_show_message.assert_called_once_with(expected_message, QMessageBox.Icon.Question,
                                                    QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
                                                    QMessageBox.StandardButton.Yes)
      else:
        mock_show_message.assert_called_once_with(expected_message, QMessageBox.Icon.Warning)
      if expected_log_warning:
        configuration_extended.logger.warning.assert_called_once_with(expected_message)
    else:
      mock_show_message.assert_not_called()
      configuration_extended.logger.warning.assert_not_called()

  @pytest.mark.parametrize(
    "existing_instance, expected_instance_type, test_id",
    [
      (None, QApplication, "no_existing_qapplication"),
      (MagicMock(spec=QApplication), QApplication, "existing_qapplication"),
    ],
    ids=[
      "no_existing_qapplication",
      "existing_qapplication"
    ]
  )
  def test_get_gui_success_path(self,
                                mocker,
                                configuration_extended: configuration_extended,
                                existing_instance,
                                expected_instance_type,
                                test_id):
    # Arrange
    app_instance = mocker.MagicMock(spec=QApplication)
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.QApplication',
                 return_value=app_instance)
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.QApplication.instance',
                 return_value=existing_instance)
    mock_dialog = mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.DataHierarchyEditorDialog',
                               return_value=mocker.MagicMock(instance=mocker.MagicMock()))

    # Act
    application, dialog_instance, data_hierarchy_form = get_gui()

    # Assert
    assert isinstance(application, expected_instance_type)
    assert dialog_instance == mock_dialog.return_value.instance
    assert data_hierarchy_form == mock_dialog.return_value

  @pytest.mark.parametrize(
    "database, test_id",
    [
      (None, "none_database"),
      ("invalid_database", "invalid_database_type"),
    ],
    ids=[
      "none_database",
      "invalid_database_type"
    ]
  )
  def test_get_gui_error_cases(self,
                               mocker,
                               configuration_extended: configuration_extended,
                               database, test_id):
    # Arrange
    app_instance = mocker.MagicMock(spec=QApplication)
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.QApplication',
                 return_value=app_instance)
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.QApplication.instance',
                 return_value=None)
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.DataHierarchyEditorDialog',
                 side_effect=TypeError)

    # Act & Assert
    with pytest.raises(TypeError):
      get_gui(database)

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

  @pytest.mark.parametrize(
    "selected_type, can_delete, expected_enabled, test_id",
    [
      ("type1", True, True, "success_path_type1"),
      ("type2", False, False, "success_path_type2"),
      ("", False, False, "edge_case_empty_string"),
      ("nonexistent_type", False, False, "edge_case_nonexistent_type"),
      ("type_with_special_chars!@#", True, True, "edge_case_special_chars"),
    ],
    ids=[
      "success_path_type1",
      "success_path_type2",
      "edge_case_empty_string",
      "edge_case_nonexistent_type",
      "edge_case_special_chars",
    ]
  )
  def test_check_and_disable_delete_button(self,
                                           mocker,
                                           configuration_extended: configuration_extended,
                                           selected_type, can_delete, expected_enabled, test_id):
    # Arrange
    mocker.patch('pasta_eln.GUI.data_hierarchy.data_hierarchy_editor_dialog.can_delete_type', return_value=can_delete)

    # Act
    configuration_extended.check_and_disable_delete_button(selected_type)

    # Assert
    configuration_extended.deleteTypePushButton.setEnabled.assert_called_once_with(expected_enabled)
