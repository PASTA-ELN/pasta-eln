#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_required_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from tests.app_tests.common.fixtures import required_delegate
from tests.app_tests.common.test_delegate_funcs_common import delegate_editor_method_common


class TestOntologyConfigRequiredColumnDelegate(object):
  def test_delegate_create_editor_method(self, mocker, required_delegate: required_delegate):
    delegate_editor_method_common(required_delegate, mocker)
