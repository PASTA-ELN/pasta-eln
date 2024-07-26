#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: metadata_frame.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from abc import abstractmethod
from typing import Any

from PySide6.QtWidgets import QFrame


class MetadataFrame(object):

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates a new instance of the MetadataFrame class.

    Explanation:
        This method creates a new instance of the MetadataFrame class.

    Args:
        *_: Variable length argument list.
        **__: Arbitrary keyword arguments.

    Returns:
        Any: The new instance of the MetadataFrame class.

    """
    return super(MetadataFrame, cls).__new__(cls)

  def __init__(self, instance: QFrame) -> None:
    """
    Initializes a new instance of the MetadataFrame class.

    Explanation:
        This method initializes a new instance of the MetadataFrame class.

    """
    self.instance: QFrame = instance

  @abstractmethod
  def load_ui(self) -> None:
    """
    Loads the UI for the metadata frame.

    Explanation:
        This method loads the UI for the metadata frame.

    """
    pass

  @abstractmethod
  def save_modifications(self) -> None:
    """
    Loads the UI for the metadata frame.

    Explanation:
        This method loads the UI for the metadata frame.

    """
    pass