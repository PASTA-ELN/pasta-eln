#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_table_view_data_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.ontology_configuration.ontology_attachments_tableview_data_model import OntologyAttachmentsTableViewModel
from pasta_eln.ontology_configuration.ontology_props_tableview_data_model import OntologyPropsTableViewModel
from pasta_eln.ontology_configuration.ontology_tableview_data_model import OntologyTableViewModel


class TestOntologyConfigTableViewDataModel(object):

  def test_data_models_basic(self,
                             qtmodeltester):
    base_model = OntologyTableViewModel()
    base_model.setObjectName("OntologyTableViewModel")
    items = {i: str(i) for i in range(4)}
    base_model.update(items)
    qtmodeltester.check(base_model)

  def test_data_models_property_table_model(self,
                                            qtmodeltester):
    props_model = OntologyPropsTableViewModel()
    props_model.setObjectName("OntologyPropsTableViewModel")
    props_items = {
      0: {"name": "name", "query": "query", "list": "list", "link": "link", "required": "required", "unit": "unit"},
      1: {"name": "name", "query": "query", "list": "list", "link": "link", "required": "required", "unit": "unit"}
    }
    props_model.update(props_items)
    with pytest.raises(AssertionError):
      qtmodeltester.check(props_model, force_py=True)

  def test_data_models_attachments_table_model(self,
                                               qtmodeltester):
    attachments_model = OntologyAttachmentsTableViewModel()
    attachments_model.setObjectName("OntologyAttachmentsTableViewModel")
    attachments = {
      0: {"location": "location"},
      1: {"location": "location"},
      2: {"location": "location"},
      3: {"location": "location"}
    }
    attachments_model.update(attachments)
    with pytest.raises(AssertionError):
      qtmodeltester.check(attachments_model, force_py=True)