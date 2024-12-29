#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_metadata_frame_base.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest
from PySide6.QtWidgets import QFrame

from pasta_eln.GUI.dataverse.metadata_frame_base import MetadataFrame


class ConcreteMetadataFrame(MetadataFrame):
  def load_ui(self) -> None:
    pass

  def save_modifications(self) -> None:
    pass


@pytest.fixture
def qframe_instance(mocker):
  return mocker.MagicMock(spec=QFrame)


class TestDataverseMetadataFrame:
  @pytest.mark.parametrize(
    'args, kwargs, expected_type',
    [
      ((), {}, ConcreteMetadataFrame),
      ((1, 2, 3), {}, ConcreteMetadataFrame),
      ((), {'key': 'value'}, ConcreteMetadataFrame),
    ],
    ids=[
      'no_args_no_kwargs',
      'with_args_no_kwargs',
      'no_args_with_kwargs',
    ]
  )
  def test_metadata_frame_new(self, args, kwargs, expected_type):
    # Act
    instance = MetadataFrame.__new__(ConcreteMetadataFrame, *args, **kwargs)

    # Assert
    assert isinstance(instance, expected_type)

  def test_metadata_frame_init(self, qframe_instance):
    # Act
    instance = ConcreteMetadataFrame(qframe_instance)

    # Assert
    assert instance.instance == qframe_instance

  @pytest.mark.parametrize(
    'method_name',
    [
      'load_ui',
      'save_modifications',
    ],
    ids=[
      'load_ui_method',
      'save_modifications_method',
    ]
  )
  def test_abstract_methods_implementation(self, qframe_instance, method_name):
    # Arrange
    instance = ConcreteMetadataFrame(qframe_instance)

    # Act
    method = getattr(instance, method_name)

    # Assert
    assert callable(method)
