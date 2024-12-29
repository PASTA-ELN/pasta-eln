""" Data type class context. """
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


class DataTypeClassContext:
  """
  Context class for a DataTypeClass instance
  """

  def __init__(self,
               main_vertical_layout: QVBoxLayout,
               add_push_button: QPushButton,
               parent_frame: QFrame,
               meta_field: dict[str, Any]) -> None:
    """
    DataTypeClassContext constructor used by DataTypeClassFactory
    Args:
      main_vertical_layout (QVBoxLayout): Main vertical layout in the parent frame
      add_push_button (QPushButton): Add push button in the parent frame
      parent_frame (QFrame): Parent frame
      meta_field (meta_field): Meta field of the data type class
    """
    super().__init__()
    if isinstance(main_vertical_layout, QVBoxLayout):
      self.main_vertical_layout = main_vertical_layout
    else:
      raise ValueError('main_vertical_layout must be a QVBoxLayout!')
    if isinstance(add_push_button, QPushButton):
      self.add_push_button = add_push_button
    else:
      raise ValueError('add_push_button must be a QPushButton!')
    if isinstance(parent_frame, QFrame):
      self.parent_frame = parent_frame
    else:
      raise ValueError('parent_frame must be a QFrame!')
    if isinstance(meta_field, dict):
      self.meta_field = meta_field
    else:
      raise ValueError('meta_field must be a dict!')
