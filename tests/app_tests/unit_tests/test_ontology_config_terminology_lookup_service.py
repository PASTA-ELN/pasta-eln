#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_ontology_config_terminology_lookup_service.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import asyncio
import logging
from asyncio import CancelledError, IncompleteReadError, InvalidStateError, LimitOverrunError, TimeoutError
from json import JSONDecodeError
from urllib.parse import urlparse

import pytest
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, InvalidURL
from aiohttp.client_reqrep import ConnectionKey

from pasta_eln.GUI.ontology_configuration.terminology_lookup_service import TerminologyLookupService
from tests.app_tests.common.fixtures import iri_lookup_web_results_name_mock, iri_lookup_web_results_pasta_mock, \
  iri_lookup_web_results_science_mock, retrieved_iri_results_name_mock, retrieved_iri_results_pasta_mock, \
  retrieved_iri_results_science_mock, terminology_lookup_config_mock, terminology_lookup_mock
from tests.app_tests.common.test_utils import are_json_equal

pytest_plugins = ('pytest_asyncio',)


class TestOntologyConfigTerminologyLookup(object):

  def test_terminology_lookup_instantiation_should_succeed(self,
                                                           mocker,
                                                           iri_lookup_web_results_pasta_mock,
                                                           # To enable fixture import used by other tests
                                                           iri_lookup_web_results_science_mock,
                                                           # To enable fixture import used by other tests
                                                           iri_lookup_web_results_name_mock,
                                                           # To enable fixture import used by other tests
                                                           retrieved_iri_results_pasta_mock,
                                                           # To enable fixture import used by other tests
                                                           retrieved_iri_results_science_mock,
                                                           # To enable fixture import used by other tests
                                                           retrieved_iri_results_name_mock):  # To enable fixture import used by other tests
    mock_logger = mocker.patch('logging.Logger')
    mock_get_logger = mocker.patch.object(logging, 'getLogger', return_value=mock_logger)
    service = TerminologyLookupService()
    mock_get_logger.assert_called_once_with(
      'pasta_eln.GUI.ontology_configuration.terminology_lookup_service.TerminologyLookupService')
    assert service.logger is mock_logger
    assert service.session_timeout == 5, "session_timeout should be set to 5"
    assert service.session_request_errors == [], "session_request_errors should be empty"

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

    # Arrange
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
    mock_json_loads = mocker.patch('pasta_eln.GUI.ontology_configuration.terminology_lookup_service.loads',
                                   return_value=response_json)

    # Act and asserts
    assert await terminology_lookup_mock.get_request(base_url,
                                                     request_params) == response_json, "Valid results must be returned"
    mock_log_info.assert_any_call("Requesting url: %s, params: %s", base_url,
                                  request_params)
    mock_client_session_constructor.assert_called_once_with()
    mock_client_session_get_response.assert_called_once_with(base_url, params=request_params,
                                                             timeout=terminology_lookup_mock.session_timeout)
    mock_client_session_get_response_text.assert_called_once_with()
    mock_json_loads.assert_called_once_with(response_string)

  @pytest.mark.parametrize(
    "exception, error_message, url", [
      (TimeoutError("Timeout error occurred"),
       "Client session request timeout for url (http://url.com) with error: Timeout error occurred",
       "http://url.com"),
      (CancelledError("Request cancelled"),
       "Client session request cancelled for url (http://url.com) with error: Request cancelled",
       "http://url.com"),
      (InvalidStateError("Invalid state"),
       "Client session request in invalid state for url (http://url.com) with error: Invalid state",
       "http://url.com"),
      (IncompleteReadError(b"Partial", expected=20),
       "Client session request incomplete read for url (http://url.com) with error: 7 bytes read on a total of 20 expected bytes",
       "http://url.com"),
      (LimitOverrunError("Limit overrun", 1),
       "Client session request limit overrun for url (http://url.com) with error: Limit overrun",
       "http://url.com"),
      (TypeError("TypeError occurred"),
       "Client session type error for url (http://url.com) with error: TypeError occurred",
       "http://url.com"),
      (ClientConnectorError(
        connection_key=ConnectionKey(ssl=False, host='url.com', port=443, is_ssl=False, proxy=None, proxy_auth=None,
                                     proxy_headers_hash=0), os_error=OSError()),
       "ClientConnectorError for url (http://url.com) with error: Cannot connect to host url.com:443 ssl:False [None]",
       "http://url.com"),
      (InvalidURL("InvalidURL occurred"),
       "Client session InvalidURL for url (None) with error: InvalidURL occurred",
       "None"),
      (InvalidURL("InvalidURL occurred"),
       "Client session InvalidURL for url (None) with error: InvalidURL occurred",
       None),
      (JSONDecodeError("JSONDecodeError occurred", doc="test", pos=9),
       "Client session JSONDecodeError for url (http://url.com) with error: JSONDecodeError occurred: line 1 column 10 (char 9)",
       "http://url.com"),
      (TypeError("Constructor parameter should be str"),
       "Client session type error for url (None) with error: Constructor parameter should be str",
       None),
    ]
  )
  @pytest.mark.asyncio
  async def test_get_request_when_exception_should_do_as_expected(self,
                                                                  mocker,
                                                                  terminology_lookup_mock: terminology_lookup_mock,
                                                                  exception,
                                                                  error_message,
                                                                  url):

    # Arrange
    mock_log_info = mocker.patch.object(terminology_lookup_mock.logger, 'info')
    mock_log_error = mocker.patch.object(terminology_lookup_mock.logger, 'error')
    mock_client_session = mocker.patch('aiohttp.client.ClientSession')
    mock_client_response = mocker.patch('aiohttp.client.ClientResponse')
    mock_client_session_constructor = mocker.patch.object(ClientSession, '__aenter__', return_value=mock_client_session)
    mocker.patch.object(mock_client_response, '__aenter__', return_value=mock_client_response)
    mock_client_session_get_response = mocker.patch.object(mock_client_session, 'get',
                                                           side_effect=exception)

    # Act and asserts
    assert await terminology_lookup_mock.get_request(url,
                                                     "request_params") == {}, "Valid results must be returned"
    mock_log_info.assert_any_call('Requesting url: %s, params: %s', url, 'request_params')
    mock_client_session_constructor.assert_called_once_with()
    mock_client_session_get_response.assert_called_once_with(url, params='request_params',
                                                             timeout=terminology_lookup_mock.session_timeout)
    mock_log_error.assert_called_once_with(error_message)
    assert terminology_lookup_mock.session_request_errors[
             0] == error_message, "session_request_error message must be set!"

  def test_do_parse_web_result_for_mocked_wikipedia_web_results_should_do_as_expected(self,
                                                                                      mocker,
                                                                                      terminology_lookup_mock: terminology_lookup_mock,
                                                                                      terminology_lookup_config_mock: terminology_lookup_config_mock,
                                                                                      iri_lookup_web_results_pasta_mock,
                                                                                      retrieved_iri_results_pasta_mock):
    # Arrange
    mock_log_info = mocker.patch.object(terminology_lookup_mock.logger, 'info')

    # Act and asserts
    search_term = 'pasta'
    wikipedia_search_result_mock = iri_lookup_web_results_pasta_mock[0]
    wikipedia_lookup_service_mock = terminology_lookup_config_mock[0]
    wikipedia_return_mock = retrieved_iri_results_pasta_mock[0]
    returned_iri_result = terminology_lookup_mock.parse_web_result(
      search_term,
      wikipedia_search_result_mock,
      wikipedia_lookup_service_mock)
    assert returned_iri_result is not None, "Result must be returned"
    assert are_json_equal(returned_iri_result,
                          wikipedia_return_mock), "Returned results must match with the mocked results"
    mock_log_info.assert_any_call("Searching term: %s for online service: %s",
                                  search_term,
                                  wikipedia_lookup_service_mock.get('name'))

  @pytest.mark.parametrize("search_term, lookup_service, web_result", [
    (None, '', ''),
    ('', None, ''),
    ('', '', None),
    ({}, {}, {})
  ])
  def test_do_parse_web_result_for_null_args_should_do_as_expected(self,
                                                                   mocker,
                                                                   terminology_lookup_mock: terminology_lookup_mock,
                                                                   terminology_lookup_config_mock: terminology_lookup_config_mock,
                                                                   search_term,
                                                                   lookup_service,
                                                                   web_result):
    # Arrange
    mock_log_error = mocker.patch.object(terminology_lookup_mock.logger, 'error')

    # Act and asserts
    assert terminology_lookup_mock.parse_web_result(
      search_term,
      web_result,
      lookup_service) == {}, "Null result must be returned"
    mock_log_error.assert_any_call("Invalid search term or web result or lookup service!")

  @pytest.mark.parametrize("search_term, web_results_fixture_name, results_fixture_name", [
    ('pasta', 'iri_lookup_web_results_pasta_mock', 'retrieved_iri_results_pasta_mock'),
    ('science', 'iri_lookup_web_results_science_mock', 'retrieved_iri_results_science_mock'),
    ('name', 'iri_lookup_web_results_name_mock', 'retrieved_iri_results_name_mock'),
  ])
  def test_do_parse_web_result_with_mocked_web_results_should_do_as_expected(self,
                                                                             mocker,
                                                                             terminology_lookup_mock: terminology_lookup_mock,
                                                                             terminology_lookup_config_mock: terminology_lookup_config_mock,
                                                                             search_term,
                                                                             web_results_fixture_name,
                                                                             results_fixture_name,
                                                                             request):
    # Arrange
    mock_log_info = mocker.patch.object(terminology_lookup_mock.logger, 'info')
    retrieved_iri_results_mock = request.getfixturevalue(results_fixture_name)
    iri_lookup_web_results_mock = request.getfixturevalue(web_results_fixture_name)
    for lookup_service, web_result, retrieved_iri_result in zip(terminology_lookup_config_mock,
                                                                iri_lookup_web_results_mock,
                                                                retrieved_iri_results_mock):
      # Act and asserts
      returned_iri_result = terminology_lookup_mock.parse_web_result(
        search_term,
        web_result,
        lookup_service)
      assert returned_iri_result is not None, "Result must be returned"
      assert are_json_equal(returned_iri_result,
                            retrieved_iri_result), "Returned results must match with the mocked results"
      mock_log_info.assert_any_call("Searching term: %s for online service: %s",
                                    search_term,
                                    lookup_service.get('name'))

  @pytest.mark.parametrize("search_term, results_fixture_name", [
    ('pasta', 'retrieved_iri_results_pasta_mock'),
    ('science', 'retrieved_iri_results_science_mock'),
    ('name', 'retrieved_iri_results_name_mock'),
    (None, ''),
    ('', ''),
    ("    ", '')
  ])
  @pytest.mark.asyncio
  async def test_do_lookup_for_given_search_term_should_do_as_expected(self,
                                                                       mocker,
                                                                       terminology_lookup_mock: terminology_lookup_mock,
                                                                       terminology_lookup_config_mock: terminology_lookup_config_mock,
                                                                       search_term,
                                                                       results_fixture_name,
                                                                       request):

    # Arrange
    retrieved_iri_results = request.getfixturevalue(results_fixture_name) if results_fixture_name else []
    mock_dir_name = mocker.MagicMock()
    mock_cd = mocker.MagicMock()
    mock_join = mocker.MagicMock()
    mock_realpath = mocker.MagicMock()
    mock_open_file = mocker.MagicMock()
    mock_get_request_resp = mocker.MagicMock()
    mocker.patch.object(terminology_lookup_mock, 'session_request_errors')
    mock_session_request_errors_clear = mocker.patch.object(terminology_lookup_mock.session_request_errors, 'clear')
    mock_os_path_dir_name = mocker.patch('pasta_eln.GUI.ontology_configuration.terminology_lookup_service.dirname',
                                         return_value=mock_dir_name)
    mock_os_path_get_cwd = mocker.patch('pasta_eln.GUI.ontology_configuration.terminology_lookup_service.getcwd',
                                        return_value=mock_cd)
    mock_os_path_join = mocker.patch('pasta_eln.GUI.ontology_configuration.terminology_lookup_service.join',
                                     return_value=mock_join)
    mock_os_realpath = mocker.patch('pasta_eln.GUI.ontology_configuration.terminology_lookup_service.realpath',
                                    return_value=mock_realpath)
    mock_os_open = mocker.patch('pasta_eln.GUI.ontology_configuration.terminology_lookup_service.open',
                                return_value=mock_open_file)
    mock_get_request = mocker.patch(
      'pasta_eln.GUI.ontology_configuration.terminology_lookup_service.TerminologyLookupService.get_request',
      return_value=mock_get_request_resp)
    mock_parse_web_result = mocker.patch(
      'pasta_eln.GUI.ontology_configuration.terminology_lookup_service.TerminologyLookupService.parse_web_result')
    mock_parse_web_result.side_effect = retrieved_iri_results
    mocker.patch.object(mock_get_request_resp, '__aenter__', return_value=mock_get_request_resp)
    mocker.patch.object(mock_open_file, '__enter__', return_value=mock_open_file)
    mock_log_info = mocker.patch.object(terminology_lookup_mock.logger, 'info')
    mock_log_error = mocker.patch.object(terminology_lookup_mock.logger, 'error')
    mock_json_load = mocker.patch('pasta_eln.GUI.ontology_configuration.terminology_lookup_service.load',
                                  return_value=terminology_lookup_config_mock)
    for item in terminology_lookup_config_mock:
      assert item['request_params'][item['search_term_key']] == 'searchTerm', \
        "Before lookup search term must not be set, should contain default: 'searchTerm'"

    # Act and asserts
    result = await terminology_lookup_mock.do_lookup(search_term)
    assert result is not None, "Results must be returned"
    assert are_json_equal(result, retrieved_iri_results), "Valid results must be returned"

    if search_term and not search_term.isspace():
      mock_log_info.assert_any_call('Searching for term: %s', search_term)
      mock_session_request_errors_clear.assert_called_once_with()
      mock_json_load.assert_called_once_with(mock_open_file)
      for item in terminology_lookup_config_mock:
        mock_get_request.assert_any_call(item['url'], item['request_params'])
        assert item['request_params'][item['search_term_key']] == search_term, \
          "Search term must be set to 'pasta'"
      mock_os_open.assert_called_once_with(mock_join, encoding="utf-8")
      mock_os_realpath.assert_called_once_with(mock_join)
      mock_os_path_join.assert_any_call(mock_cd, mock_dir_name)
      mock_os_path_join.assert_any_call(mock_realpath, "terminology_lookup_config.json")
      mock_os_path_get_cwd.assert_called_once_with()
      assert mock_os_path_dir_name.call_args.args[0].endswith(
        'pasta_eln/GUI/ontology_configuration/terminology_lookup_service.py'), \
        "Directory name must end with pasta_eln/GUI/ontology_configuration/terminology_lookup_service.py"
    else:
      mock_log_error.assert_called_once_with("Invalid null search term!")

  @pytest.mark.parametrize("search_term",
                           ['pasta', 'science', 'name', 'forschung', 'Glaskeramikfügung', "наука",
                            "производство", "科學"])
  @pytest.mark.asyncio
  async def test_do_lookup_with_actual_lookup_for_term_pasta_should_return_same_stored_results(self,
                                                                                               mocker,
                                                                                               terminology_lookup_mock: terminology_lookup_mock,
                                                                                               terminology_lookup_config_mock: terminology_lookup_config_mock,
                                                                                               search_term):
    # Arrange
    mock_log_info = mocker.patch.object(terminology_lookup_mock.logger, 'info')

    # Act and asserts
    results = await terminology_lookup_mock.do_lookup(search_term)

    mock_log_info.assert_any_call('Searching for term: %s', search_term)

    assert results is not None, "Results must be returned"
    assert isinstance(results, list), "Results must be a list"
    assert terminology_lookup_mock.session_request_errors == [], "Session request errors must be empty"
    assert len(results) == len(
      terminology_lookup_config_mock), "Length of results must be equal to the number of services in terminology_lookup_config.json"
    for iri_result, lookup_service in zip(results, terminology_lookup_config_mock):
      assert isinstance(iri_result, dict), "Each iri_result must be a dictionary"
      assert iri_result['search_term'] == search_term, f"Search term must be set to {search_term}"
      assert iri_result['name'] == lookup_service['name'], f"Name must be set to {lookup_service['name']}"
      assert isinstance(iri_result['results'], list), "Results field in each iri_result must be a list"
      for item in iri_result['results']:
        assert isinstance(item, dict), "Each item in results must be a dictionary"
        assert item['iri'] is not None and validate_url(item['iri']), "Each retrieved results must have a valid IRI"
        assert item['information'] is not None, "Each retrieved results must have a valid information field"


def validate_url(url: str):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
  except:
    return False
