#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_document_null_exception.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest

from tests.app_tests.common.fixtures import key_not_found_exception


class TestDataHierarchyKeyNotFoundException(object):
  @pytest.mark.parametrize('key_not_found_exception',
                           [{'message': 'error thrown', 'errors': {'error1': 'error1', 'error2': 'error2'}}],
                           indirect=True)
  def test_ontology_config_document_null_exception(self,
                                                   key_not_found_exception,
                                                   request):
    assert str(key_not_found_exception) or key_not_found_exception.message == "error thrown", \
      "key_not_found_exception should return error thrown"
    assert key_not_found_exception.detailed_errors == {'error1': 'error1', 'error2': 'error2'}, \
      "key_not_found_exception.detailed_errors should return error1 and error2"
