#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_document_null_exception.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest

from tests.common.fixtures import doc_null_exception


class TestDataHierarchyDocumentNullException(object):
  @pytest.mark.parametrize('doc_null_exception',
                           [{'message': 'error thrown', 'errors': {'error1': 'error1', 'error2': 'error2'}}],
                           indirect=True)
  def test_data_hierarchy_config_document_null_exception(self, doc_null_exception: doc_null_exception, request):
    assert str(
      doc_null_exception) or doc_null_exception.message == "error thrown", "doc_null_exception) should return error thrown"
    assert doc_null_exception.detailed_errors == {'error1': 'error1',
                                                  'error2': 'error2'}, "doc_null_exception.detailed_errors should return error1 and error2"
