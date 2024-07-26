#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: data_type_class_context.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Any

from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout


class DataTypeClassContext(object):

  def __init__(self,
               main_vertical_layout: QVBoxLayout,
               add_push_button: QPushButton,
               parent_frame: QFrame,
               meta_field: dict[str, Any]) -> None:
    super().__init__()
    if not isinstance(main_vertical_layout, QVBoxLayout):
      raise ValueError("main_vertical_layout must be a QVBoxLayout!")
    else:
      self.main_vertical_layout = main_vertical_layout
    if not isinstance(add_push_button, QPushButton):
      raise ValueError("add_push_button must be a QPushButton!")
    else:
      self.add_push_button = add_push_button
    if not isinstance(parent_frame, QFrame):
      raise ValueError("parent_frame must be a QFrame!")
    else:
      self.parent_frame = parent_frame
    if not isinstance(meta_field, dict):
      raise ValueError("meta_field must be a dict!")
    else:
      self.meta_field = meta_field
