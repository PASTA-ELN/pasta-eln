"""Validate the item-type template format before it reaches SQLite."""
import copy
from typing import Any
import pytest
from pasta_eln.ui.data_hierarchy.editor import _validateItemTypeTemplate

# pylint: disable=invalid-name

TEMPLATE:dict[str, Any] = {
  'format': 'PASTA-ELN item type templates',
  'version': 1,
  'docTypes': [{
    'docType': 'testtype',
    'title': 'Test types',
    'icon': '',
    'shortcut': 't',
    'view': 'name',
    'schema': [
      {'docType': 'testtype', 'class': '', 'idx': '0', 'name': 'name', 'unit': '', 'mandatory': 'T', 'list': '', 'long': ''},
      {'docType': 'testtype', 'class': '', 'idx': '1', 'name': 'comment', 'unit': '', 'mandatory': '', 'list': '', 'long': ''}
    ]
  }]
}


def test_valid_template_is_accepted() -> None:
  """Accept a complete item-type template."""
  assert _validateItemTypeTemplate(TEMPLATE) == TEMPLATE['docTypes']


def test_duplicate_schema_index_is_rejected() -> None:
  """Reject a template that would violate the schema primary key."""
  invalidTemplate = copy.deepcopy(TEMPLATE)
  invalidTemplate['docTypes'][0]['schema'][1]['idx'] = '0'
  with pytest.raises(ValueError, match='duplicate schema fields'):
    _validateItemTypeTemplate(invalidTemplate)
