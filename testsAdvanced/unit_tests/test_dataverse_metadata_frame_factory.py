#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_metadata_frame_factory.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Any
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QFrame
from _pytest.mark import param

from pasta_eln.GUI.dataverse.controlled_vocab_frame import ControlledVocabFrame
from pasta_eln.GUI.dataverse.data_type_class_names import DataTypeClassName
from pasta_eln.GUI.dataverse.metadata_frame_base import MetadataFrame
from pasta_eln.GUI.dataverse.metadata_frame_factory import MetadataFrameFactory, make_controlled_vocab_frame, \
  make_primitive_compound_frame
from pasta_eln.GUI.dataverse.primitive_compound_frame import PrimitiveCompoundFrame


# Mock functions to simulate the behavior of the actual frame creation functions
def mock_make_primitive_compound_frame(metadata_field: dict[str, Any]) -> MetadataFrame:
  return MetadataFrame(MagicMock(spec=QFrame))


def mock_make_controlled_vocab_frame(metadata_field: dict[str, Any]) -> MetadataFrame:
  return MetadataFrame(MagicMock(spec=QFrame))


@pytest.fixture
def metadata_frame_factory(mocker):
  mocker.patch("pasta_eln.GUI.dataverse.metadata_frame_factory.make_primitive_compound_frame",
               side_effect=mock_make_primitive_compound_frame)
  mocker.patch("pasta_eln.GUI.dataverse.metadata_frame_factory.make_controlled_vocab_frame",
               side_effect=mock_make_controlled_vocab_frame)
  return MetadataFrameFactory()


class TestMetadataFrameFactory:

  @pytest.mark.parametrize(
    "class_name, metadata_field, expected_type",
    [
      (DataTypeClassName.PRIMITIVE, {"field1": "value1"}, MetadataFrame),
      (DataTypeClassName.COMPOUND, {"field2": "value2"}, MetadataFrame),
      (DataTypeClassName.CONTROLLED_VOCAB, {"field3": "value3"}, MetadataFrame),
    ],
    ids=["primitive", "compound", "controlled_vocab"]
  )
  def test_make_metadata_frame_happy_path(self, metadata_frame_factory, class_name, metadata_field, expected_type):
    # Act
    result = metadata_frame_factory.make_metadata_frame(class_name, metadata_field)

    # Assert
    assert isinstance(result, expected_type)

  @pytest.mark.parametrize(
    "class_name, metadata_field",
    [
      (DataTypeClassName.PRIMITIVE, {}),
      (DataTypeClassName.COMPOUND, {"field": None}),
      (DataTypeClassName.CONTROLLED_VOCAB, {"field": ""}),
    ],
    ids=["primitive_empty", "compound_none", "controlled_vocab_empty"]
  )
  def test_make_metadata_frame_edge_cases(self, metadata_frame_factory, class_name, metadata_field):
    # Act
    result = metadata_frame_factory.make_metadata_frame(class_name, metadata_field)

    # Assert
    assert isinstance(result, MetadataFrame)

  @pytest.mark.parametrize(
    "class_name, metadata_field, expected_exception, expected_message",
    [
      ("INVALID_CLASS", {"field": "value"}, ValueError, "Invalid data type class name: INVALID_CLASS"),
      (None, {"field": "value"}, ValueError, "Invalid data type class name: None"),
    ],
    ids=["invalid_class", "none_class"]
  )
  def test_make_metadata_frame_error_cases(self, metadata_frame_factory, class_name, metadata_field, expected_exception,
                                           expected_message):
    # Act and Assert
    with pytest.raises(expected_exception) as exc_info:
      metadata_frame_factory.make_metadata_frame(class_name, metadata_field)

    assert str(exc_info.value) == expected_message

  @pytest.mark.parametrize(
    "metadata_field, expected_type",
    [
      param({"key1": "value1"}, PrimitiveCompoundFrame, id="simple_dict"),
      param({"key2": 123, "key3": [1, 2, 3]}, PrimitiveCompoundFrame, id="complex_dict"),
      param({}, PrimitiveCompoundFrame, id="empty_dict"),
    ],
    ids=["simple_dict", "complex_dict", "empty_dict"]
  )
  def test_make_primitive_compound_frame_happy_path(self, mocker, metadata_field, expected_type):
    # Arrange
    mocker.patch("pasta_eln.GUI.dataverse.metadata_frame_factory.PrimitiveCompoundFrame",
                 return_value=MagicMock(spec=PrimitiveCompoundFrame, metadata_field=metadata_field))

    # Act
    result = make_primitive_compound_frame(metadata_field)

    # Assert
    assert isinstance(result, expected_type)
    assert result.metadata_field == metadata_field

  @pytest.mark.parametrize(
    "metadata_field, expected_type",
    [
      # Happy path tests
      param({"field1": "value1"}, ControlledVocabFrame, id="simple_dict"),
      param({"field1": 123, "field2": [1, 2, 3]}, ControlledVocabFrame, id="complex_dict"),
      param({"field1": None}, ControlledVocabFrame, id="none_value"),

      # Edge cases
      param({}, ControlledVocabFrame, id="empty_dict"),
      param({"field1": ""}, ControlledVocabFrame, id="empty_string_value"),
      param({"field1": " "}, ControlledVocabFrame, id="whitespace_string_value"),
    ],
    ids=lambda x: x[2]
  )
  def test_make_controlled_vocab_frame(self, mocker, metadata_field, expected_type):
    # Arrange
    mocker.patch("pasta_eln.GUI.dataverse.metadata_frame_factory.ControlledVocabFrame",
                 return_value=MagicMock(spec=ControlledVocabFrame, metadata_field=metadata_field))
    # Act
    result = make_controlled_vocab_frame(metadata_field)

    # Assert
    assert isinstance(result, expected_type)
