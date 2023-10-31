#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_utility_functions.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QMessageBox
from cloudant import CouchDB

from pasta_eln.GUI.data_hierarchy.utility_functions import adjust_data_hierarchy_data_to_v3, can_delete_type, \
  check_data_hierarchy_types, \
  get_db, get_missing_metadata_message, get_next_possible_structural_level_title, is_click_within_bounds, show_message


class TestDataHierarchyUtilityFunctions(object):

  def test_is_click_within_bounds_when_null_arguments_returns_false(self,
                                                                    mocker):
    assert is_click_within_bounds(mocker.patch('PySide6.QtGui.QSinglePointEvent'),
                                  None) == False, "is_click_within_bounds should return False for null argument"
    assert is_click_within_bounds(None, mocker.patch(
      'PySide6.QtWidgets.QStyleOptionViewItem')) == False, "is_click_within_bounds should return False for null argument"
    assert is_click_within_bounds(None, None) == False, "is_click_within_bounds should return False for null argument"

  def test_is_click_within_bounds_when_within_bounds_returns_true(self,
                                                                  mocker):
    mock_mouse_event = mocker.patch('PySide6.QtGui.QSinglePointEvent')
    mock_mouse_event.type.side_effect = lambda: QEvent.MouseButtonRelease
    mock_mouse_event.x.side_effect = lambda: 10  # left is 5 and right is left + width 5+10=15
    mock_mouse_event.y.side_effect = lambda: 20  # top is 10 and bottom is top + height 10+20=30
    mock_q_style_option_view_item = mocker.patch('PySide6.QtWidgets.QStyleOptionViewItem')
    mock_q_style_option_view_item.rect.left.side_effect = lambda: 5
    mock_q_style_option_view_item.rect.width.side_effect = lambda: 10
    mock_q_style_option_view_item.rect.top.side_effect = lambda: 10
    mock_q_style_option_view_item.rect.height.side_effect = lambda: 20
    mocker.patch.object(QMouseEvent, "__new__",
                        lambda x, y: mock_mouse_event)  # Patch the QMouseEvent instantiation to return the same event
    assert is_click_within_bounds(mock_mouse_event,
                                  mock_q_style_option_view_item) == True, "is_click_within_bounds should return True"
    assert mock_mouse_event.type.call_count == 1, "Event type call count must be 1"
    assert mock_mouse_event.x.call_count == 1, "Event x() call count must be 1"
    assert mock_mouse_event.y.call_count == 1, "Event y() call count must be 1"
    assert mock_q_style_option_view_item.rect.left.call_count == 2, "QStyleOptionViewItem left call count must be two"
    assert mock_q_style_option_view_item.rect.top.call_count == 2, "QStyleOptionViewItem top call count must be two"
    assert mock_q_style_option_view_item.rect.width.call_count == 1, "QStyleOptionViewItem left call count must be 1"
    assert mock_q_style_option_view_item.rect.height.call_count == 1, "QStyleOptionViewItem top call count must be 1"

  def test_is_click_within_bounds_when_outside_bounds_returns_false(self,
                                                                    mocker):
    mock_mouse_event = mocker.patch('PySide6.QtGui.QSinglePointEvent')
    mock_mouse_event.type.side_effect = lambda: QEvent.MouseButtonRelease
    mock_mouse_event.x.side_effect = lambda: 10  # range: 5 -> 15 (within range)
    mock_mouse_event.y.side_effect = lambda: 5  # range: 10 -> 10 (out of range)
    mock_q_style_option_view_item = mocker.patch('PySide6.QtWidgets.QStyleOptionViewItem')
    mock_q_style_option_view_item.rect.left.side_effect = lambda: 5
    mock_q_style_option_view_item.rect.width.side_effect = lambda: 10
    mock_q_style_option_view_item.rect.top.side_effect = lambda: 10
    mock_q_style_option_view_item.rect.height.side_effect = lambda: 20
    mocker.patch.object(QMouseEvent, "__new__",
                        lambda x, y: mock_mouse_event)  # Patch the QMouseEvent instantiation to return the same event
    assert is_click_within_bounds(mock_mouse_event,
                                  mock_q_style_option_view_item) == False, "is_click_within_bounds should return True"
    assert mock_mouse_event.type.call_count == 1, "Event type call count must be 1"
    assert mock_mouse_event.x.call_count == 1, "Event x() call count must be 1"
    assert mock_mouse_event.y.call_count == 1, "Event y() call count must be 1"
    assert mock_q_style_option_view_item.rect.left.call_count == 2, "QStyleOptionViewItem left call count must be two"
    assert mock_q_style_option_view_item.rect.top.call_count == 1, "QStyleOptionViewItem top call count must be one"
    assert mock_q_style_option_view_item.rect.width.call_count == 1, "QStyleOptionViewItem left call count must be 1"
    assert mock_q_style_option_view_item.rect.height.call_count == 0, "QStyleOptionViewItem top call count must be zero"

  def test_adjust_data_hierarchy_data_to_v3_when_empty_document_do_nothing(self,
                                                                     mocker):
    contents = {"-version": 2}
    mock_doc = self.create_mock_doc(contents, mocker)
    assert adjust_data_hierarchy_data_to_v3(mock_doc) is None, "adjust_data_hierarchy_data_to_v3 should return None"
    assert list(contents.keys()) == ["-version"], "Only version should be added"

    assert adjust_data_hierarchy_data_to_v3(None) is None, "adjust_data_hierarchy_data_to_v3 should return None"

  @pytest.mark.parametrize("contents", [
    ({
      "x0":
        {
          "displayedTitle": "",
          "metadata": []
        }
    }),
    ({
      "x1": {}
    }),
    ({
      "x2":
        {
          "attachments": [{"test": "test", "test1": "test2"}],
          "displayedTitle": "",
          "metadata": {"default": [
            {
              "name": "value",
              "test": "test1"
            }
          ]}
        }
    })
  ])
  def test_adjust_data_hierarchy_data_to_v3_when_v2document_given_do_expected(self,
                                                                        contents):
    assert adjust_data_hierarchy_data_to_v3(contents) is None, "adjust_data_hierarchy_data_to_v3 should return None"
    if "x0" in contents:
      assert "attachments" in contents["x0"], "attachments should be set"
      assert "metadata" in contents["x0"], "metadata should be set"
      assert type(contents["x0"]["metadata"]) is dict, "metadata should be dictionary"

    if "x1" in contents:
      assert "attachments" in contents["x1"], "attachments should be set"
      assert "metadata" in contents["x1"], "metadata should be set"
      assert type(contents["x1"]["metadata"]) is dict, "metadata should be dictionary"
      assert "default" in contents["x1"]["metadata"] and len(
        contents["x1"]["metadata"]["default"]) == 0, "default metadata list be defined"

    if "x2" in contents:
      assert "attachments" in contents["x2"], "attachments should be set"
      assert "metadata" in contents["x2"], "metadata should be set"
      assert type(contents["x2"]["metadata"]) is dict, "metadata should be dictionary"
      assert "default" in contents["x2"]["metadata"] and len(
        contents["x2"]["metadata"]["default"]) == 1, "default metadata list should be the same"

  @staticmethod
  def create_mock_doc(contents, mocker):
    mock_doc = mocker.patch('cloudant.document.Document')
    mock_doc.__iter__ = mocker.Mock(return_value=iter(contents))
    mock_doc.__getitem__.side_effect = contents.__getitem__
    mock_doc.__setitem__.side_effect = contents.__setitem__
    return mock_doc

  def test_get_next_possible_structural_level_title_when_null_arg_returns_none(self):
    assert get_next_possible_structural_level_title(None) is None, \
      "get_next_possible_structural_level_title should return True"

  @pytest.mark.parametrize("existing_list, expected_next_level", [
    (None, None),
    ([], "x0"),
    (["x0", "x2"], "x3"),
    (["x0", "xa", "x3", "x-1", "x10"], "x11"),
    (["x0", "xa", "x3", "x-1", "a10", "X23"], "x24"),
    (["a"], "x0")
  ])
  def test_get_next_possible_structural_level_displayed_title_when_valid_list_arg_returns_right_result(self,
                                                                                             mocker,
                                                                                             existing_list,
                                                                                             expected_next_level):
    assert get_next_possible_structural_level_title(
      existing_list) == expected_next_level, "get_next_possible_structural_level_displayed_title should return as expected"

  def test_get_db_with_right_arguments_returns_valid_db_instance(self,
                                                                 mocker):
    mock_client = mocker.MagicMock(spec=CouchDB)
    mock_client.all_dbs.return_value = ["db_name1", "db_name2"]
    db_instances = {"db_name1": mocker.MagicMock(spec=CouchDB), "db_name2": mocker.MagicMock(spec=CouchDB)}
    created_db_instance = mocker.MagicMock(spec=CouchDB)
    mock_client.__getitem__.side_effect = db_instances.__getitem__
    mock_client.create_database.side_effect = mocker.MagicMock(side_effect=(lambda name: created_db_instance))
    mocker.patch.object(CouchDB, "__new__", lambda s, user, auth_token, url, connect: mock_client)
    mocker.patch.object(CouchDB, "__init__", lambda s, user, auth_token, url, connect: None)

    assert get_db("db_name1", "test", "test", "test", None) is db_instances["db_name1"], \
      "get_db should return valid db instance"
    assert mock_client.all_dbs.call_count == 1, "get_db should call all_dbs"
    assert mock_client.__getitem__.call_count == 1, "get_db should call __getitem__"

    assert get_db("db_name2", "test", "test", "test", None) is db_instances["db_name2"], \
      "get_db should return valid db instance"
    assert mock_client.all_dbs.call_count == 2, "get_db should call all_dbs"
    assert mock_client.__getitem__.call_count == 2, "get_db should call __getitem__"

    assert get_db("db_name3", "test", "test", "test", None) is created_db_instance, \
      "get_db should return created db instance"
    assert mock_client.all_dbs.call_count == 3, "get_db should call all_dbs"
    assert mock_client.create_database.call_count == 1, "get_db should call create_database"

  def test_get_db_with_wrong_arguments_throws_exception(self,
                                                        mocker):
    mock_logger = mocker.MagicMock(spec=logging)
    logger_spy = mocker.spy(mock_logger, 'error')
    mocker.patch.object(CouchDB, "__new__", mocker.MagicMock(side_effect=Exception('Database error')))
    mocker.patch.object(CouchDB, "__init__", lambda s, user, auth_token, url, connect: None)
    assert get_db("db_name1", "test", "test", "test", None) is None, \
      "get_db should return None"
    assert mock_logger.error.call_count == 0, "get_db should not call log.error"

    assert get_db("db_name1", "test", "test", "test", mock_logger) is None, \
      "get_db should return None"
    assert mock_logger.error.call_count == 1, "get_db should call log.error"
    logger_spy.assert_called_once_with(
      "Could not connect with username+password to local server, error: Database error")

  def test_show_message_with_none_argument_does_nothing(self):
    assert show_message(None) is None, "show_message should return None"

  def test_show_message_with_valid_argument_shows_message(self,
                                                          mocker):
    mock_msg_box = mocker.patch("PySide6.QtWidgets.QMessageBox")
    set_text_spy = mocker.spy(mock_msg_box, 'setText')
    mocker.patch.object(QMessageBox, "__new__", lambda s: mock_msg_box)
    mock_exec = mocker.MagicMock()
    mocker.patch.object(mock_msg_box, "exec", return_value=mock_exec)
    assert show_message("Valid message") is mock_exec, "show_message should not be None"
    set_text_spy.assert_called_once_with(
      "Valid message")
    mock_msg_box.exec.assert_called_once_with()
    mock_msg_box.setWindowTitle.assert_called_once_with("Data Hierarchy Editor")
    mock_msg_box.setTextFormat.assert_called_once_with(Qt.RichText)
    mock_msg_box.setIcon.assert_called_once_with(QMessageBox.Information)

  def test_show_message_with_error_argument_shows_warning(self,
                                                          mocker):
    mock_msg_box = mocker.patch("PySide6.QtWidgets.QMessageBox")
    set_text_spy = mocker.spy(mock_msg_box, 'setText')
    mocker.patch.object(QMessageBox, "__new__", lambda s: mock_msg_box)
    mock_exec = mocker.MagicMock()
    mocker.patch.object(mock_msg_box, "exec", return_value=mock_exec)
    assert show_message("Error message", QMessageBox.Warning) is mock_exec, "show_message should not be None"
    set_text_spy.assert_called_once_with(
      "Error message")
    mock_msg_box.exec.assert_called_once_with()
    mock_msg_box.setWindowTitle.assert_called_once_with("Data Hierarchy Editor")
    mock_msg_box.setTextFormat.assert_called_once_with(Qt.RichText)
    mock_msg_box.setIcon.assert_called_once_with(QMessageBox.Warning)

  @pytest.mark.parametrize("data_hierarchy_types, expected_result", [
    ({}, ({}, {})),
    ({
       "x0": {
         "metadata": {
           "default": [
             {"name": "name", "query": "What is the name of task?"},
             {"name": "tags", "query": "What is the name of task?"}
           ],
           "metadata_group1": [
             {"name": "name", "query": "What is the name of task?"},
             {"name": "tags", "query": "What is the name of task?"}
           ]
         }
       },
       "x1": {
         "metadata": {
           "default": [
             {"name": "name", "query": "What is the name of task?"},
             {"name": "tags", "query": "What is the name of task?"}
           ],
           "metadata_group2": [
             {"name": "name", "query": "What is the name of task?"},
             {"name": "tags", "query": "What is the name of task?"}
           ]
         }
       }
     },
     ({'Structure level 0': {'metadata_group1': ['-name', '-tags'], 'default': ['-name', '-tags']},
       'Structure level 1': {'metadata_group2': ['-name', '-tags'], 'default': ['-name', '-tags']}},
      {}
      )),
    ({
       "x0": {
         "metadata": {
           "default": [
             {"name": "name", "query": "What is the name of task?"},
             {"name": "-tags", "query": "What is the name of task?"},
             {"name": "    ", "query": "What is the name of task?"},
             {"name": None, "query": "What is the name of task?"}
           ],
           "metadata_group1": [
             {"name": "-name", "query": "What is the name of task?"},
             {"name": "tags", "query": "What is the name of task?"},
             {"name": "", "query": "What is the name of task?"}
           ]
         }
       },
       "x1": {
         "metadata": {
           "default": [
             {"name": "-name", "query": "What is the name of task?"},
             {"name": "-tags", "query": "What is the name of task?"}
           ],
           "metadata_group2": [
             {"name": "name", "query": "What is the name of task?"},
             {"name": "-tags", "query": "What is the name of task?"}
           ],
           "metadata_group3": [
             {"name": "name", "query": "What is the name of task?"},
             {"name": "-tags", "query": "What is the name of task?"},
             {"name": "   ", "query": "What is the name of task?"}
           ]
         }
       }
     },
     ({'Structure level 0': {'metadata_group1': ['-tags'], 'default': ['-name']},
       'Structure level 1': {'metadata_group2': ['-name'], 'metadata_group3': ['-name']}},
      {'Structure level 0': ['default', 'metadata_group1'],
       'Structure level 1': ['metadata_group3']})),
    ({
       "x0": {
         "metadata": {
           "default": [
             {"name": "-name", "query": "What is the name of task?"},
             {"name": "-tags", "query": "What is the name of task?"}
           ],
           "metadata_group1": [
             {"name": "-name", "query": "What is the name of task?"},
             {"name": "-tags", "query": "What is the name of task?"}
           ],
           "metadata_group2": []
         }
       },
       "x1": {
         "metadata": {
           "default": [
             {"name": "-name", "query": "What is the name of task?"},
             {"name": "-tags", "query": "What is the name of task?"}
           ],
           "metadata_group2": [
             {"name": "-name", "query": "What is the name of task?"},
             {"name": "-tags", "query": "What is the name of task?"}
           ]
         }
       }
     },
     ({'Structure level 0': {'metadata_group2': ['-name', '-tags']}}, {})),

    ({
       "x0": {
         "metadata": {
           "default": [
             {"name": "-name", "query": "What is the name of task?"},
             {"name": "-tags", "query": "What is the name of task?"},
             {"name": None, "query": "What is the name of task?"}

           ],
           "metadata_group1": [
             {"name": "-name", "query": "What is the name of task?"},
             {"name": "-tags", "query": "What is the name of task?"},
             {"name": None, "query": "What is the name of task?"}
           ]
         }
       },
       "x1": {
         "metadata": {
           "default": [
             {"name": "-name", "query": "What is the name of task?"},
             {"name": "-tags", "query": "What is the name of task?"},
             {"name": "", "query": "What is the name of task?"}
           ],
           "metadata_group2": [
             {"name": "-name", "query": "What is the name of task?"},
             {"name": "-tags", "query": "What is the name of task?"},
             {"name": " ", "query": "What is the name of task?"}
           ]
         }
       }
     },
     ({},
      {'Structure level 0': ['default', 'metadata_group1'],
       'Structure level 1': ['default', 'metadata_group2']})),
    ({
       "x0": {
       },
       "x1": {
         "metadata": {
           "default": [
             {"name": "name", "query": "What is the name of task?"},
             {"name": "-tags", "query": "What is the name of task?"}
           ],
           "metadata_group2": [
             {"name": "-name", "query": "What is the name of task?"},
             {"name": "-tags", "query": "What is the name of task?"}
           ]
         }
       },
       "test": {
         "metadata": {
           "default": [
             {"name": "-name", "query": "What is the name of task?"},
             {"name": "", "query": "What is the name of task?"},
           ]
         }
       }
     },
     ({'Structure level 1': {'default': ['-name']}, 'test': {'default': ['-tags']}},
      {'test': ['default']})),
    ({
       "x0": {
       },
       "x1": {
         "metadata": {
           "default": [
             {"name": "name", "query": "What is the name of task?"},
             {"name": "-tags", "query": "What is the name of task?"},
             {},
             {}
           ],
           "metadata_group2": [
             {"name": "-name", "query": "What is the name of task?"},
             {"name": "-tags", "query": "What is the name of task?"},
             {"query": "What is the name of task?"}
           ]
         }
       },
       "test": {
         "metadata": {
           "default": [
             {"name": "-name", "query": "What is the name of task?"},
           ]
         }
       }
     },
     ({'Structure level 1': {'default': ['-name']}, 'test': {'default': ['-tags']}},
      {'Structure level 1': ['default', 'metadata_group2']}))
  ])
  def test_check_data_hierarchy_document_with_full_and_missing_metadata_returns_expected_result(self,
                                                                                            data_hierarchy_types,
                                                                                            expected_result):
    assert check_data_hierarchy_types(data_hierarchy_types) == expected_result, "show_message should return None"

  def test_check_data_hierarchy_document_with_null_doc_returns_empty_tuple(self):
    assert check_data_hierarchy_types(None) == ({}, {}), "check_data_hierarchy_document should return empty tuple"

  @pytest.mark.parametrize("missing_metadata, missing_names, expected_message", [
    ({}, {}, ""),
    ({'Structure level 0': {'metadata_group1': ['-name', '-tags'], 'default': ['-name', '-tags']},
      'Structure level 1': {'metadata_group2': ['-name', '-tags'], 'default': ['-name', '-tags']}},
     {'Structure level 0': ['default', 'metadata_group1'],
      'Structure level 1': ['default', 'metadata_group2']},
     "<html><b>Missing mandatory metadata: </b><ul><li>Type: <i style=\"color:Crimson\">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">metadata_group1</i>&nbsp;&nbsp;Metadata Name: <i style=\"color:Crimson\">-name</i></li><li>Type: <i style=\"color:Crimson\">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">metadata_group1</i>&nbsp;&nbsp;Metadata Name: <i style=\"color:Crimson\">-tags</i></li><li>Type: <i style=\"color:Crimson\">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">default</i>&nbsp;&nbsp;Metadata Name: <i style=\"color:Crimson\">-name</i></li><li>Type: <i style=\"color:Crimson\">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">default</i>&nbsp;&nbsp;Metadata Name: <i style=\"color:Crimson\">-tags</i></li><li>Type: <i style=\"color:Crimson\">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">metadata_group2</i>&nbsp;&nbsp;Metadata Name: <i style=\"color:Crimson\">-name</i></li><li>Type: <i style=\"color:Crimson\">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">metadata_group2</i>&nbsp;&nbsp;Metadata Name: <i style=\"color:Crimson\">-tags</i></li><li>Type: <i style=\"color:Crimson\">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">default</i>&nbsp;&nbsp;Metadata Name: <i style=\"color:Crimson\">-name</i></li><li>Type: <i style=\"color:Crimson\">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">default</i>&nbsp;&nbsp;Metadata Name: <i style=\"color:Crimson\">-tags</i></li></ul><b>Missing metadata names:</b><ul><li>Type: <i style=\"color:Crimson\">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">default</i></li><li>Type: <i style=\"color:Crimson\">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">metadata_group1</i></li><li>Type: <i style=\"color:Crimson\">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">default</i></li><li>Type: <i style=\"color:Crimson\">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">metadata_group2</i></li></ul></html>"),
    ({'Structure level 0': {'metadata_group1': ['-name', '-tags'], 'default': ['-name', '-tags']},
      'Structure level 1': {'metadata_group2': ['-name', '-tags'], 'default': ['-name', '-tags']}},
     {},
     "<html><b>Missing mandatory metadata: </b><ul><li>Type: <i style=\"color:Crimson\">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">metadata_group1</i>&nbsp;&nbsp;Metadata Name: <i style=\"color:Crimson\">-name</i></li><li>Type: <i style=\"color:Crimson\">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">metadata_group1</i>&nbsp;&nbsp;Metadata Name: <i style=\"color:Crimson\">-tags</i></li><li>Type: <i style=\"color:Crimson\">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">default</i>&nbsp;&nbsp;Metadata Name: <i style=\"color:Crimson\">-name</i></li><li>Type: <i style=\"color:Crimson\">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">default</i>&nbsp;&nbsp;Metadata Name: <i style=\"color:Crimson\">-tags</i></li><li>Type: <i style=\"color:Crimson\">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">metadata_group2</i>&nbsp;&nbsp;Metadata Name: <i style=\"color:Crimson\">-name</i></li><li>Type: <i style=\"color:Crimson\">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">metadata_group2</i>&nbsp;&nbsp;Metadata Name: <i style=\"color:Crimson\">-tags</i></li><li>Type: <i style=\"color:Crimson\">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">default</i>&nbsp;&nbsp;Metadata Name: <i style=\"color:Crimson\">-name</i></li><li>Type: <i style=\"color:Crimson\">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">default</i>&nbsp;&nbsp;Metadata Name: <i style=\"color:Crimson\">-tags</i></li></ul></html>"),
    ({},
     {'Structure level 0': ['default', 'metadata_group1'],
      'Structure level 1': ['default', 'metadata_group2']},
     "<html><b>Missing metadata names:</b><ul><li>Type: <i style=\"color:Crimson\">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">default</i></li><li>Type: <i style=\"color:Crimson\">Structure level 0</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">metadata_group1</i></li><li>Type: <i style=\"color:Crimson\">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">default</i></li><li>Type: <i style=\"color:Crimson\">Structure level 1</i>&nbsp;&nbsp;Metadata Group: <i style=\"color:Crimson\">metadata_group2</i></li></ul></html>")
  ])
  def test_get_formatted_missing_metadata_message_returns_expected_message(self,
                                                                        missing_metadata,
                                                                        missing_names,
                                                                        expected_message):
    assert get_missing_metadata_message(
      missing_metadata, missing_names) == expected_message, "get_missing_metadata_message should return expected"

  @pytest.mark.parametrize("existing_types, selected_type, expected_result", [
    (["x0", "x1", "x3", "samples", "instruments"], "test", True),
    (["x0", "x1", "x3", "x4", "instruments"], "x5", False),
    (["x0", "x1", "x3", "x4", "instruments"], "x0", False),
    (["x0", "x1", "x3", "x4", "instruments"], "x4", True),
    (["x0", "x1", "x3", "x4", "instruments"], "x3", False),
    (["x0", "x1", "x3", "x4", "instruments"], "x0", False),
    (["x0", "x1", "x3", "x4", "instruments"], "x1", False),
    (["x0", "x1", "x3", "x4", "instruments"], "instruments", True),
    (["x2", "x3", "x5", "x0", "instruments"], "x5", True),
    (["x2", "x3", "x5", "x0", "x7", "", "samples"], "x7", True),
    (["x2", "x3", "x5", "x0", "x7", "", "samples"], "x8", False),
    (["x2", "x3", "x5", "x0", "x7", "", None], "x8", False),
    (["x2", "x3", "x5", "x0", "x7", "", None], None, False)
  ])
  def test_can_delete_type_returns_expected(self,
                                            existing_types,
                                            selected_type,
                                            expected_result):
    assert can_delete_type(
      existing_types, selected_type) == expected_result, "can_delete_type should return expected"
