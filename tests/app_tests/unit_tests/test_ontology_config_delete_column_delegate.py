#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_delete_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from tests.app_tests.common.fixtures import delete_delegate
from tests.app_tests.common.test_delegate_funcs_common import delegate_paint_common, delegate_editor_method_common, \
  delegate_editor_event_common


class TestOntologyConfigDeleteColumnDelegate(object):

  def test_delegate_paint_method(self,
                                 mocker,
                                 delete_delegate: delete_delegate):
    delegate_paint_common(mocker, delete_delegate, "Delete")

  def test_delegate_create_editor_method(self,
                                         mocker,
                                         delete_delegate: delete_delegate):
    delegate_editor_method_common(delete_delegate, mocker)

  def test_delegate_create_editor_event_method_when_clicked_within_bounds_returns_true(self,
                                                                                       mocker,
                                                                                       delete_delegate: delete_delegate):
    mocker.patch('pasta_eln.ontology_configuration.delete_column_delegate.is_click_within_bounds',
                 return_value=True)
    delegate_editor_event_common(delete_delegate, mocker, is_click_within_bounds=True)

  def test_delegate_create_editor_event_method_when_clicked_outside_bounds_returns_false(self,
                                                                                         mocker,
                                                                                         delete_delegate: delete_delegate):
    mocker.patch('pasta_eln.ontology_configuration.delete_column_delegate.is_click_within_bounds',
                 return_value=False)
    delegate_editor_event_common(delete_delegate, mocker, is_click_within_bounds=False)
