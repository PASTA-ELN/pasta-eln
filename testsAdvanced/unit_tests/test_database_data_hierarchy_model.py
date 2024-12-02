#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_database_data_hierarchy_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest

from pasta_eln.database.incorrect_parameter_error import IncorrectParameterError
from pasta_eln.database.models.data_hierarchy_model import DataHierarchyModel


class TestDatabaseDataHierarchyModel:
  @pytest.mark.parametrize(
    "doc_type, IRI, title, icon, shortcut, view",
    [
      ("document", "http://example.com", "Example Title", "icon.png", "ctrl+e", "view1"),
      (None, None, None, None, None, None),
      ("", "", "", "", "", ""),
    ],
    ids=[
      "all_valid_strings",
      "all_none",
      "all_empty_strings",
    ]
  )
  def test_data_hierarchy_model_initialization(self, doc_type, IRI, title, icon, shortcut, view):
    # Act
    model = DataHierarchyModel(doc_type, IRI, title, icon, shortcut, view)

    # Assert
    assert model.doc_type == doc_type
    assert model.IRI == IRI
    assert model.title == title
    assert model.icon == icon
    assert model.shortcut == shortcut
    assert model.view == view

  @pytest.mark.parametrize(
    "attribute, value",
    [
      ("doc_type", 123),
      ("IRI", 123),
      ("title", 123),
      ("icon", 123),
      ("shortcut", 123),
      ("view", 123),
    ],
    ids=[
      "invalid_doc_type",
      "invalid_iri",
      "invalid_title",
      "invalid_icon",
      "invalid_shortcut",
      "invalid_view",
    ]
  )
  def test_data_hierarchy_model_initialization_invalid_types(self, attribute, value):
    # Arrange
    kwargs = {attribute: value}

    # Act & Assert
    with pytest.raises(IncorrectParameterError):
      DataHierarchyModel(**kwargs)

  @pytest.mark.parametrize(
    "attribute, initial_value, new_value",
    [
      ("doc_type", "initial", "new"),
      ("IRI", "initial", "new"),
      ("title", "initial", "new"),
      ("icon", "initial", "new"),
      ("shortcut", "initial", "new"),
      ("view", "initial", "new"),
    ],
    ids=[
      "change_doc_type",
      "change_iri",
      "change_title",
      "change_icon",
      "change_shortcut",
      "change_view",
    ]
  )
  def test_data_hierarchy_model_setters(self, attribute, initial_value, new_value):
    # Arrange
    model = DataHierarchyModel(**{attribute: initial_value})

    # Act
    setattr(model, attribute, new_value)

    # Assert
    assert getattr(model, attribute) == new_value

  @pytest.mark.parametrize(
    "attribute, invalid_value",
    [
      ("doc_type", 123),
      ("IRI", 123),
      ("title", 123),
      ("icon", 123),
      ("shortcut", 123),
      ("view", 123),
    ],
    ids=[
      "invalid_set_doc_type",
      "invalid_set_iri",
      "invalid_set_title",
      "invalid_set_icon",
      "invalid_set_shortcut",
      "invalid_set_view",
    ]
  )
  def test_data_hierarchy_model_setters_invalid_types(self, attribute, invalid_value):
    # Arrange
    model = DataHierarchyModel()

    # Act & Assert
    with pytest.raises(IncorrectParameterError):
      setattr(model, attribute, invalid_value)

  @pytest.mark.parametrize(
    "attribute",
    [
      "doc_type",
      "IRI",
      "title",
      "icon",
      "shortcut",
      "view",
    ],
    ids=[
      "delete_doc_type",
      "delete_iri",
      "delete_title",
      "delete_icon",
      "delete_shortcut",
      "delete_view",
    ]
  )
  def test_data_hierarchy_model_deleters(self, attribute):
    # Arrange
    model = DataHierarchyModel(**{attribute: "value"})

    # Act
    delattr(model, attribute)

    # Assert
    with pytest.raises(AttributeError):
      getattr(model, attribute)
