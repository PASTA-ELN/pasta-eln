#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_terminology_lookup.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging

import pytest

from  pasta_eln.GUI.ontology_configuration.terminology_lookup import TerminologyLookup
from tests.app_tests.common.fixtures import terminology_lookup_mock

pytest_plugins = ('pytest_asyncio',)
class TestOntologyConfigTerminologyLookup(object):

    def test_terminology_lookup_instantiation_should_succeed(self,
                                                             mocker):
        mock_logger = mocker.patch('logging.Logger')
        mock_get_logger = mocker.patch.object(logging, 'getLogger', return_value=mock_logger)
        dialog = TerminologyLookup()
        mock_get_logger.assert_called_once_with('pasta_eln.GUI.ontology_configuration.terminology_lookup.TerminologyLookup')
        assert dialog.logger is mock_logger

    @pytest.mark.asyncio
    async def test_do_lookup_should_do_as_expected(self,
                                                             mocker,
                                                             terminology_lookup_mock: terminology_lookup_mock):
        mock_log_info = mocker.patch.object(terminology_lookup_mock.logger, 'info')
        assert await terminology_lookup_mock.do_lookup('pasta') is None, "Nothing should be returned"
        mock_log_info.assert_called_with('Searching for term: %s', 'pasta')


