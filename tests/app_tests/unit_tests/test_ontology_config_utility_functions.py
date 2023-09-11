#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_utility_functions.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging

import pytest
from PySide6.QtCore import QEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QMessageBox
from cloudant import CouchDB

from pasta_eln.GUI.ontology_configuration.utility_functions import is_click_within_bounds, adjust_ontology_data_to_v3, \
  get_next_possible_structural_level_label, get_db, show_message


class TestOntologyConfigUtilityFunctions(object):

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

  def test_adjust_ontology_data_to_v3_when_empty_document_do_nothing(self,
                                                                     mocker):
    contents = {}
    mock_doc = self.create_mock_doc(contents, mocker)
    assert adjust_ontology_data_to_v3(mock_doc) is None, "adjust_ontology_data_to_v3 should return None"
    assert list(contents.keys()) == ["-version"], "Only version should be added"

    assert adjust_ontology_data_to_v3(None) is None, "adjust_ontology_data_to_v3 should return None"

  def test_adjust_ontology_data_to_v3_when_v2document_given_do_expected(self,
                                                                        mocker):
    # Without attachments
    contents = {
      "-version": 2,
      "x0":
        {
          "label": "",
          "prop": []
        }
    }
    mock_doc = self.create_mock_doc(contents, mocker)
    assert adjust_ontology_data_to_v3(mock_doc) is None, "adjust_ontology_data_to_v3 should return None"
    assert "attachments" in contents["x0"], "attachments should be set"
    assert "prop" in contents["x0"], "prop should be set"
    assert type(contents["x0"]["prop"]) is dict, "prop should be dictionary"
    assert contents["-version"] == 3, "Version must be updated to 3"

    # Without anything much
    contents = {
      "-version": 2,
      "x0": {}
    }
    mock_doc = self.create_mock_doc(contents, mocker)
    assert adjust_ontology_data_to_v3(mock_doc) is None, "adjust_ontology_data_to_v3 should return None"
    assert "attachments" in contents["x0"], "attachments should be set"
    assert "prop" in contents["x0"], "prop should be set"
    assert type(contents["x0"]["prop"]) is dict, "prop should be dictionary"
    assert "default" in contents["x0"]["prop"] and len(
      contents["x0"]["prop"]["default"]) == 0, "default prop list be defined"
    assert contents["-version"] == 3, "Version must be updated to 3"

    # With some content
    contents = {
      "-version": 2,
      "x1":
        {
          "attachments": [{"test": "test", "test1": "test2"}],
          "label": "",
          "prop": {"default": [
            {
              "name": "value",
              "test": "test1"
            }
          ]}
        }
    }
    mock_doc = self.create_mock_doc(contents, mocker)
    assert adjust_ontology_data_to_v3(mock_doc) is None, "adjust_ontology_data_to_v3 should return None"
    assert "attachments" in contents["x1"], "attachments should be set"
    assert "prop" in contents["x1"], "prop should be set"
    assert type(contents["x1"]["prop"]) is dict, "prop should be dictionary"
    assert "default" in contents["x1"]["prop"] and len(
      contents["x1"]["prop"]["default"]) == 1, "default prop list should be the same"
    assert contents["-version"] == 3, "Version must be updated to 3"

  @staticmethod
  def create_mock_doc(contents, mocker):
    mock_doc = mocker.patch('cloudant.document.Document')
    mock_doc.__iter__ = mocker.Mock(return_value=iter(contents))
    mock_doc.__getitem__.side_effect = contents.__getitem__
    mock_doc.__setitem__.side_effect = contents.__setitem__
    return mock_doc

  def test_get_next_possible_structural_level_label_when_null_arg_returns_none(self):
    assert get_next_possible_structural_level_label(None) is None, \
      "get_next_possible_structural_level_label should return True"

  @pytest.mark.parametrize("existing_list, expected_next_level", [
    (None, None),
    ([], "x0"),
    (["x0", "x2"], "x3"),
    (["x0", "xa", "x3", "x-1", "x10"], "x11"),
    (["x0", "xa", "x3", "x-1", "a10", "X23"], "x24"),
    (["a"], "x0")
  ])
  def test_get_next_possible_structural_level_label_when_valid_list_arg_returns_right_result(self,
                                                                                             mocker,
                                                                                             existing_list,
                                                                                             expected_next_level):
    assert get_next_possible_structural_level_label(
      existing_list) == expected_next_level, "get_next_possible_structural_level_label should return as expected"

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
    assert show_message("Valid message") is None, "show_message should return None"
    set_text_spy.assert_called_once_with(
      "Valid message")
    assert mock_msg_box.exec.call_count == 1, "show_message should call exec()"
