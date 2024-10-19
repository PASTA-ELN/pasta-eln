#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_data_type_class_context.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout

from pasta_eln.GUI.dataverse.data_type_class_context import DataTypeClassContext


class TestDataTypeClassContext:
  @pytest.mark.parametrize(
    "main_vertical_layout, add_push_button, parent_frame, meta_field",
    [
      (MagicMock(spec=QVBoxLayout), MagicMock(spec=QPushButton), MagicMock(spec=QFrame), {"key": "value"}),
      (MagicMock(spec=QVBoxLayout), MagicMock(spec=QPushButton), MagicMock(spec=QFrame), {"another_key": 123}),
    ],
    ids=["valid_case_1", "valid_case_2"]
  )
  def test_data_type_class_context_success_path(self, main_vertical_layout, add_push_button, parent_frame, meta_field):
    # Act
    context = DataTypeClassContext(main_vertical_layout, add_push_button, parent_frame, meta_field)

    # Assert
    assert context.main_vertical_layout == main_vertical_layout
    assert context.add_push_button == add_push_button
    assert context.parent_frame == parent_frame
    assert context.meta_field == meta_field

  @pytest.mark.parametrize(
    "main_vertical_layout, add_push_button, parent_frame, meta_field, expected_exception, expected_message",
    [
      (None, MagicMock(spec=QPushButton), MagicMock(spec=QFrame), {"key": "value"}, ValueError,
       "main_vertical_layout must be a QVBoxLayout!"),
      (MagicMock(spec=QVBoxLayout), None, MagicMock(spec=QFrame), {"key": "value"}, ValueError,
       "add_push_button must be a QPushButton!"),
      (MagicMock(spec=QVBoxLayout), MagicMock(spec=QPushButton), None, {"key": "value"}, ValueError,
       "parent_frame must be a QFrame!"),
      (MagicMock(spec=QVBoxLayout), MagicMock(spec=QPushButton), MagicMock(spec=QFrame), None, ValueError,
       "meta_field must be a dict!"),
    ],
    ids=["invalid_main_vertical_layout", "invalid_add_push_button", "invalid_parent_frame", "invalid_meta_field"]
  )
  def test_data_type_class_context_error_cases(self, main_vertical_layout, add_push_button, parent_frame, meta_field,
                                               expected_exception, expected_message):
    # Act and Assert
    with pytest.raises(expected_exception) as exc_info:
      DataTypeClassContext(main_vertical_layout, add_push_button, parent_frame, meta_field)

    assert str(exc_info.value) == expected_message
