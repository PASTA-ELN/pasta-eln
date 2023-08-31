#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_table_view_data_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest
from PySide6.QtCore import Qt

from tests.app_tests.common.fixtures import table_model, props_table_model, attachments_table_model


class TestOntologyConfigTableViewDataModel(object):

  def test_data_models_basic(self,
                             table_model: table_model,
                             qtmodeltester):
    items = {i: str(i) for i in range(4)}
    table_model.update(items)
    qtmodeltester.check(table_model)

  def test_data_models_property_table_model(self,
                                            props_table_model: props_table_model,
                                            qtmodeltester):

    props_items = [
      {"name": "name", "query": "query", "list": "list", "link": "link", "required": "required", "unit": "unit"},
      {"name": "name", "query": "query", "list": "list", "link": "link", "required": "required", "unit": "unit"}
    ]
    props_table_model.update(props_items)
    with pytest.raises(AssertionError):
      qtmodeltester.check(props_table_model, force_py=True)

  def test_data_models_attachments_table_model(self,
                                               attachments_table_model: attachments_table_model,
                                               qtmodeltester):
    attachments = [
      {"location": "location"},
      {"location": "location"},
      {"location": "location"},
      {"location": "location"}
    ]
    attachments_table_model.update(attachments)
    with pytest.raises(AssertionError):
      qtmodeltester.check(attachments_table_model, force_py=True)

  def test_data_models_basic_has_children_returns_false(self,
                                                        table_model: table_model,
                                                        mocker):
    assert table_model.hasChildren(mocker.MagicMock(spec="PySide6.QtCore.QModelIndex")) is False, \
      "hasChildren() should return False"

  @pytest.mark.parametrize(
    "is_valid, flag_combination", [
      (False, None),
      (True, Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
    ])
  def test_data_models_basic_get_flags_returns_expected(self,
                                                        table_model: table_model,
                                                        mocker,
                                                        is_valid,
                                                        flag_combination):
    mock_index = mocker.patch("PySide6.QtCore.QModelIndex")
    mocker.patch.object(mock_index, "isValid",
                        mocker.MagicMock(return_value=is_valid))
    assert table_model.flags(mock_index) == flag_combination, \
      f"flags() should return {flag_combination}"

  @pytest.mark.parametrize(
    "is_valid, data_to_be_set, display_role, index_data, data_name_map, data_set, data_set_success", [
      (False, 23233, Qt.EditRole, (0, 0), {0: "name", 1: "query"}, [{"name": "name", "query": "query"}] * 35, False),
      (False, 43432, Qt.UserRole, (1, 1), {0: "name", 1: "query"}, [{"name": "name", "query": "query"}] * 35, False),
      (True, 562332, Qt.EditRole, (34, 1), {0: "name", 1: "query"}, [{"name": "name", "query": "query"}] * 35, True),
      (True, 765322, Qt.UserRole, (4, 0), {0: "name", 1: "query"}, [{"name": "name", "query": "query"}] * 35, True),
      (True, "as12", Qt.UserRole, (6, 1), {0: "name", 1: "query"}, [{"name": "name", "query": "query"}] * 35, True),
      (True, "test", Qt.EditRole, (9, 0), {0: "name", 1: "query"}, [{"name": "name", "query": "query"}] * 35, True)
    ])
  def test_data_models_basic_set_data_should_return_expected(self,
                                                             table_model: table_model,
                                                             mocker,
                                                             is_valid,
                                                             data_to_be_set,
                                                             display_role,
                                                             index_data,
                                                             data_name_map,
                                                             data_set,
                                                             data_set_success):

    mock_index = mocker.patch("PySide6.QtCore.QModelIndex")
    mock_data_changed = mocker.patch("PySide6.QtCore.SignalInstance")
    mocker.patch.object(mock_index, "isValid",
                        mocker.MagicMock(return_value=is_valid))
    mocker.patch.object(mock_index, "row",
                        mocker.MagicMock(return_value=index_data[0]))
    mocker.patch.object(mock_index, "column",
                        mocker.MagicMock(return_value=index_data[1]))
    mock_data_name_map = mocker.MagicMock()
    mock_data_name_map.__getitem__.side_effect = data_name_map.__getitem__
    mock_data_name_map.__setitem__.side_effect = data_name_map.__setitem__
    mock_data_name_map.get.side_effect = data_name_map.get
    mock_data_set = mocker.MagicMock()
    mock_data_set.__getitem__.side_effect = data_set.__getitem__
    mock_data_set.__setitem__.side_effect = data_set.__setitem__
    mocker.patch.object(table_model, "data_name_map", mock_data_name_map)
    mocker.patch.object(table_model, "data_set", mock_data_set)
    table_model.dataChanged = mock_data_changed
    data_name_map_get_spy = mocker.spy(mock_data_name_map, 'get')
    data_changed_emit_spy = mocker.spy(mock_data_changed, 'emit')
    assert table_model.setData(mock_index, data_to_be_set, display_role) is data_set_success, \
      f"setData() should return {data_set_success}"
    assert mock_index.isValid.call_count == 1, "isValid() should be called once"
    if data_set_success:
      assert mock_index.row.call_count == 1, "row() should be called once"
      assert mock_index.column.call_count == 1, "column() should be called once"
      assert data_set[index_data[0]][data_name_map[index_data[1]]] == data_to_be_set, "data should be set"
      data_name_map_get_spy.assert_called_once_with(index_data[1])
      data_changed_emit_spy.assert_called_once_with(mock_index, mock_index, display_role)

  @pytest.mark.parametrize("is_valid, display_role, index_data, data_name_map, data_set, data_retrieved", [
    (False, Qt.EditRole, (0, 0), {0: "name", 1: "query"}, [{"name": "name", "query": "query"}] * 35, None),
    (False, Qt.UserRole, (1, 1), {0: "name", 1: "query"}, [{"name": "name", "query": "query"}] * 35, None),
    (True, Qt.EditRole, (34, 1), {0: "name", 1: "query"}, [{"name": "name", "query": "25"}] * 35, "25"),
    (True, Qt.UserRole, (4, 0), {0: "name", 1: "query"}, [{"name": "tom", "query": "query"}] * 35, "tom"),
    (True, Qt.DisplayRole, (6, 1), {0: "name", 1: "query"}, [{"name": "name", "query": "1234"}] * 35, "1234"),
    (True, Qt.EditRole, (9, 0), {0: "name", 1: "query"}, [{"name": "2&§%&%&", "query": "query"}] * 35, "2&§%&%&")
  ])
  def test_data_models_basic_get_data_should_return_expected(self,
                                                             table_model: table_model,
                                                             mocker,
                                                             is_valid,
                                                             display_role,
                                                             index_data,
                                                             data_name_map,
                                                             data_set,
                                                             data_retrieved):

    mock_index = mocker.patch("PySide6.QtCore.QModelIndex")
    mocker.patch.object(mock_index, "isValid",
                        mocker.MagicMock(return_value=is_valid))
    mocker.patch.object(mock_index, "row",
                        mocker.MagicMock(return_value=index_data[0]))
    mocker.patch.object(mock_index, "column",
                        mocker.MagicMock(return_value=index_data[1]))
    mock_data_name_map = mocker.MagicMock()
    mock_data_name_map.__getitem__.side_effect = data_name_map.__getitem__
    mock_data_name_map.__setitem__.side_effect = data_name_map.__setitem__
    mock_data_name_map.get.side_effect = data_name_map.get
    mock_data_set = mocker.MagicMock()
    mock_data_set.__getitem__.side_effect = data_set.__getitem__
    mock_data_set.__setitem__.side_effect = data_set.__setitem__
    mocker.patch.object(table_model, "data_name_map", mock_data_name_map)
    mocker.patch.object(table_model, "data_set", mock_data_set)
    data_name_map_get_spy = mocker.spy(mock_data_name_map, 'get')
    assert table_model.data(mock_index, display_role) is data_retrieved, \
      f"data() should return {data_retrieved}"
    assert mock_index.isValid.call_count == 1, "isValid() should be called once"
    if data_retrieved:
      assert mock_index.row.call_count == 1, "row() should be called once"
      assert mock_index.column.call_count == 1, "column() should be called once"
      data_name_map_get_spy.assert_called_once_with(index_data[1])

  @pytest.mark.parametrize("data_set, data_set_modified", [
    ([{"name": "name", "query": "query"}] * 4, [{"name": "name", "query": "query"}] * 4 + [{}]),
    ([{"name": "name", "query": "query"}] * 10, [{"name": "name", "query": "query"}] * 10 + [{}]),
    ([{"name": "name", "query": "query"}] * 33, [{"name": "name", "query": "query"}] * 33 + [{}]),
    ([{"name": "name", "query": "query"}] * 41, [{"name": "name", "query": "query"}] * 41 + [{}])
  ])
  def test_data_models_basic_slot_add_data_should_do_expected(self,
                                                              table_model: table_model,
                                                              mocker,
                                                              data_set,
                                                              data_set_modified):

    mock_data_set = mocker.MagicMock()
    mock_layout_changed = mocker.patch("PySide6.QtCore.SignalInstance")
    mock_data_set.__getitem__.side_effect = data_set.__getitem__
    mock_data_set.__setitem__.side_effect = data_set.__setitem__
    mocker.patch('pasta_eln.ontology_configuration.ontology_tableview_data_model.len', lambda x: len(data_set))
    mock_data_set.insert.side_effect = data_set.insert
    mocker.patch.object(table_model, "data_set", mock_data_set)
    data_set_insert_spy = mocker.spy(mock_data_set, 'insert')
    layout_changed_emit_spy = mocker.spy(mock_layout_changed, 'emit')
    table_model.layoutChanged = mock_layout_changed
    assert table_model.add_data_row() is None, \
      f"add_data_row() should return none"
    assert data_set == data_set_modified, "data_set should be set to expected value"
    data_set_insert_spy.assert_called_once_with(len(data_set) - 1, {})
    assert layout_changed_emit_spy.call_count == 1, "layout_changed_emit() should be called once"

  @pytest.mark.parametrize("data_set, delete_position, data_set_modified", [
    ([{"name": "name", "query": "query"}] * 4 + [{"name": "delete", "query": "delete"}] + [
      {"name": "name", "query": "query"}] * 4,
     4,
     [{"name": "name", "query": "query"}] * 8),
    ([{"name": "name", "query": "query"}] * 7 + [{"name": "delete", "query": "delete"}] + [
      {"name": "name", "query": "query"}] * 3,
     7,
     [{"name": "name", "query": "query"}] * 10),
    ([{"name": "name", "query": "query"}] * 27 + [{"name": "delete", "query": "delete"}] + [
      {"name": "name", "query": "query"}] * 6,
     27,
     [{"name": "name", "query": "query"}] * 33),
    ([{"name": "name", "query": "query"}] * 40 + [{"name": "delete", "query": "delete"}],
     40,
     [{"name": "name", "query": "query"}] * 40),
    ([{"name": "delete", "query": "delete"}] + [{"name": "name", "query": "query"}] * 27,
     0,
     [{"name": "name", "query": "query"}] * 27),
    ([{"name": "delete", "query": "delete"}] + [{"name": "name", "query": "query"}] * 27,
     -40,  # Out of range delete position
     [{"name": "delete", "query": "delete"}] + [{"name": "name", "query": "query"}] * 27),
    ([{"name": "delete", "query": "delete"}] + [{"name": "name", "query": "query"}] * 27,
     30,  # Out of range delete position
     [{"name": "delete", "query": "delete"}] + [{"name": "name", "query": "query"}] * 27)
  ])
  def test_data_models_basic_slot_delete_data_should_do_expected(self,
                                                                 table_model: table_model,
                                                                 mocker,
                                                                 data_set,
                                                                 delete_position,
                                                                 data_set_modified):

    mock_data_set = mocker.MagicMock()
    mock_layout_changed = mocker.patch("PySide6.QtCore.SignalInstance")
    mock_logger = mocker.patch("logging.Logger")
    mock_data_set.__getitem__.side_effect = data_set.__getitem__
    mock_data_set.__setitem__.side_effect = data_set.__setitem__
    mock_data_set.pop.side_effect = data_set.pop
    mock_data_set.insert.side_effect = data_set.insert
    mocker.patch.object(table_model, "data_set", mock_data_set)
    data_set_pop_spy = mocker.spy(mock_data_set, 'pop')
    layout_changed_emit_spy = mocker.spy(mock_layout_changed, 'emit')
    logger_info_spy = mocker.spy(mock_logger, 'info')
    logger_warning_spy = mocker.spy(mock_logger, 'warning')
    table_model.layoutChanged = mock_layout_changed
    table_model.logger = mock_logger
    data_to_be_deleted = data_set[delete_position] if 0 <= delete_position < len(data_set) else None
    assert table_model.delete_data(delete_position) is None, \
      f"add_data_row() should return none"
    assert data_set == data_set_modified, "data_set should be set to expected value"
    if data_to_be_deleted:
      data_set_pop_spy.assert_called_once_with(delete_position)
      logger_info_spy.assert_called_once_with(f"Deleted (row: {delete_position}, data: {data_to_be_deleted})...")
      assert layout_changed_emit_spy.call_count == 1, "layout_changed_emit() should be called once"
    else:
      logger_warning_spy.assert_called_once_with(f"Invalid position: {delete_position}")

  @pytest.mark.parametrize("data_set, re_order_position, data_set_modified", [
    ([{"name": "name", "query": "query"}] * 4 + [{"name": "reorder", "query": "reorder"}] + [
      {"name": "name", "query": "query"}] * 4,
     4,
     [{"name": "name", "query": "query"}] * 3 + [{"name": "reorder", "query": "reorder"}] + [
       {"name": "name", "query": "query"}] * 5),
    ([{"name": "name", "query": "query"}] * 7 + [{"name": "reorder", "query": "reorder"}] + [
      {"name": "name", "query": "query"}] * 3,
     7,
     [{"name": "name", "query": "query"}] * 6 + [{"name": "reorder", "query": "reorder"}] + [
       {"name": "name", "query": "query"}] * 4),
    ([{"name": "name", "query": "query"}] * 27 + [{"name": "reorder", "query": "reorder"}] + [
      {"name": "name", "query": "query"}] * 6,
     27,
     [{"name": "name", "query": "query"}] * 26 + [{"name": "reorder", "query": "reorder"}] + [
       {"name": "name", "query": "query"}] * 7),
    ([{"name": "name", "query": "query"}] * 40 + [{"name": "reorder", "query": "reorder"}],
     40,
     [{"name": "name", "query": "query"}] * 39 + [{"name": "reorder", "query": "reorder"}] + [
       {"name": "name", "query": "query"}] * 1),
    ([{"name": "reorder", "query": "reorder"}] + [{"name": "name", "query": "query"}] * 27,
     0,
     [{"name": "reorder", "query": "reorder"}] + [{"name": "name", "query": "query"}] * 27),
    ([{"name": "reorder", "query": "reorder"}] + [{"name": "name", "query": "query"}] * 27,
     -40,  # Out of range re-order position
     [{"name": "reorder", "query": "reorder"}] + [{"name": "name", "query": "query"}] * 27),
    ([{"name": "reorder", "query": "reorder"}] + [{"name": "name", "query": "query"}] * 27,
     30,  # Out of range re-order position
     [{"name": "reorder", "query": "reorder"}] + [{"name": "name", "query": "query"}] * 27)
  ])
  def test_data_models_basic_slot_re_order_data_should_do_expected(self,
                                                                   table_model: table_model,
                                                                   mocker,
                                                                   data_set,
                                                                   re_order_position,
                                                                   data_set_modified):

    mock_data_set = mocker.MagicMock()
    mock_layout_changed = mocker.patch("PySide6.QtCore.SignalInstance")
    mock_logger = mocker.patch("logging.Logger")
    mock_data_set.__getitem__.side_effect = data_set.__getitem__
    mock_data_set.__setitem__.side_effect = data_set.__setitem__
    mock_data_set.pop.side_effect = data_set.pop
    mock_data_set.insert.side_effect = data_set.insert
    mocker.patch.object(table_model, "data_set", mock_data_set)
    data_set_pop_spy = mocker.spy(mock_data_set, 'pop')
    data_set_insert_spy = mocker.spy(mock_data_set, 'insert')
    layout_changed_emit_spy = mocker.spy(mock_layout_changed, 'emit')
    logger_info_spy = mocker.spy(mock_logger, 'info')
    logger_warning_spy = mocker.spy(mock_logger, 'warning')
    table_model.layoutChanged = mock_layout_changed
    table_model.logger = mock_logger
    data_to_be_ordered = data_set[re_order_position] if 0 <= re_order_position < len(data_set) else None
    assert table_model.re_order_data(re_order_position) is None, \
      f"re_order_data() should return none"
    assert data_set == data_set_modified, "data_set should be set to expected value"
    if data_to_be_ordered:
      data_set_pop_spy.assert_called_once_with(re_order_position)
      shift_position = re_order_position - 1 if re_order_position > 0 else re_order_position
      data_set_insert_spy.assert_called_once_with(shift_position, data_to_be_ordered)
      logger_info_spy.assert_called_once_with(f"Reordered the data, Actual position: {re_order_position}, "
                                              f"New Position: {shift_position}, "
                                              f"data: {data_to_be_ordered})")
      assert layout_changed_emit_spy.call_count == 1, "layout_changed_emit() should be called once"
    else:
      logger_warning_spy.assert_called_once_with(f"Invalid position: {re_order_position}")
