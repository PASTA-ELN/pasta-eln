#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_terminology_lookup.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import asyncio
import logging

import pytest
from aiohttp import ClientSession

from pasta_eln.GUI.ontology_configuration.terminology_lookup_service import TerminologyLookupService
from tests.app_tests.common.fixtures import terminology_lookup_mock

pytest_plugins = ('pytest_asyncio',)


class TestOntologyConfigTerminologyLookup(object):

  def test_terminology_lookup_instantiation_should_succeed(self,
                                                           mocker):
    mock_logger = mocker.patch('logging.Logger')
    mock_get_logger = mocker.patch.object(logging, 'getLogger', return_value=mock_logger)
    dialog = TerminologyLookupService()
    mock_get_logger.assert_called_once_with('pasta_eln.GUI.ontology_configuration.terminology_lookup_service.TerminologyLookupService')
    assert dialog.logger is mock_logger

  @pytest.mark.parametrize(
    "base_url, request_params, response_string, response_json", [
      ('https://example.com', {"search_term": "pasta"}, "'test': 'testing'", {'test': 'testing'})
    ])
  @pytest.mark.asyncio
  async def test_get_request_should_do_as_expected(self,
                                                   mocker,
                                                   terminology_lookup_mock: terminology_lookup_mock,
                                                   base_url,
                                                   request_params,
                                                   response_string,
                                                   response_json):
    mock_log_info = mocker.patch.object(terminology_lookup_mock.logger, 'info')
    mock_client_session = mocker.patch('aiohttp.client.ClientSession')
    mock_client_response = mocker.patch('aiohttp.client.ClientResponse')
    mock_client_session_constructor = mocker.patch.object(ClientSession, '__aenter__', return_value=mock_client_session)
    mocker.patch.object(mock_client_response, '__aenter__', return_value=mock_client_response)
    mock_client_session_get_response = mocker.patch.object(mock_client_session, 'get',
                                                           return_value=mock_client_response)
    response_future = asyncio.Future()
    response_future.set_result(response_string)
    mock_client_session_get_response_text = mocker.patch.object(mock_client_response, 'text',
                                                                return_value=response_future)
    mock_json_load = mocker.patch('json.loads', return_value=response_json)
    assert await terminology_lookup_mock.get_request(base_url,
                                                     request_params) == response_json, "Valid results must be returned"
    mock_log_info.assert_any_call("Requesting url: %s, params: %s", base_url,
                                  request_params)
    mock_client_session_constructor.assert_called_once_with()
    mock_client_session_get_response.assert_called_once_with(base_url, params=request_params)
    mock_client_session_get_response_text.assert_called_once_with()
    mock_json_load.assert_called_once_with(response_string)

  @pytest.mark.asyncio
  async def test_do_lookup_should_do_as_expected(self,
                                                 mocker,
                                                 terminology_lookup_mock: terminology_lookup_mock):
    mock_log_info = mocker.patch.object(terminology_lookup_mock.logger, 'info')
    assert await terminology_lookup_mock.do_lookup('pasta') is not None, "Valid results must be returned"
    mock_log_info.assert_any_call('Searching for term: %s', 'pasta')
