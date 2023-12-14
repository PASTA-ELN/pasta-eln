#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_http_client.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import asyncio
from asyncio import CancelledError, IncompleteReadError, InvalidStateError, LimitOverrunError, \
  TimeoutError as AsyncTimeoutError
from json import JSONDecodeError

import pytest
from aiohttp import ClientConnectorError, ClientSession, InvalidURL
from aiohttp.client_reqrep import ConnectionKey

from pasta_eln.webclient.http_client import AsyncHttpClient, prepare_result
from tests.app_tests.common.fixtures import http_client_mock
from tests.app_tests.common.test_utils import are_json_equal

pytest_plugins = ('pytest_asyncio',)


class TestAsyncHttpClient(object):

  def test_http_client_initialization_should_succeed(self,
                                                     mocker):
    mock_logger = mocker.patch('logging.Logger')
    mock_get_logger = mocker.patch('pasta_eln.webclient.http_client.logging.getLogger',
                                   return_value=mock_logger)
    service = AsyncHttpClient()
    mock_get_logger.assert_called_once_with(
      'pasta_eln.webclient.http_client.AsyncHttpClient')
    assert service.logger is mock_logger
    assert service.session_timeout == 5, "session_timeout should be set to 5"
    assert service.session_request_errors == [], "session_request_errors should be empty"

  @pytest.mark.parametrize(
    "status, headers, reason, result", [
      (200, {'Content-Type': 'application/json'}, "OK", "testing"),
      (400, {'Content-Type': 'application/json'}, "Bad Request", "testing"),
      (500, {'Content-Type': 'application/json'}, "Internal Server Error", "testing"),
      (200, {'Content-Type': 'text/plain'}, "OK", "testing"),
      (400, {'Content-Type': 'text/plain'}, "Bad Request", "testing"),
      (500, {'Content-Type': 'application/json;charset=UTF-8'}, "Internal Server Error", "testing")
    ])
  @pytest.mark.asyncio
  async def test_prepare_result_when_succeed_should_do_as_expected(self,
                                                                   mocker,
                                                                   status,
                                                                   headers,
                                                                   reason,
                                                                   result):
    # Arrange
    mock_client_response = mocker.patch('aiohttp.client.ClientResponse')
    mock_client_response.headers = headers
    mock_client_response.status = status
    mock_client_response.reason = reason
    response_future = asyncio.Future()
    response_future.set_result(result)
    if "json" in headers.get('Content-Type'):
      mock_client_response.json.return_value = response_future
    else:
      mock_client_response.text.return_value = response_future

    assert await prepare_result(
      mock_client_response
    ) == {"status": status, "reason": reason, 'result': result, 'headers': headers}, "Should return expected result"
    if "json" in headers.get('Content-Type'):
      mock_client_response.json.assert_called_once()
    else:
      mock_client_response.text.assert_called_once()

  @pytest.mark.parametrize(
    "base_url, request_params, request_headers, response", [
      ('https://example.com', {'param_key': 'param_value'}, {'Accept': 'application/text'},
       {"status": 200, "reason": "OK", 'result': 'test'}),
      ('https://example.com', {'param_key': 'param_value'}, {'Accept': 'application/json'},
       {"status": 200, "reason": "OK", 'result': 'testing'}),
      ('https://example.com', {}, {}, {"status": 200, "reason": "OK", 'result': 'test'})
    ])
  @pytest.mark.asyncio
  async def test_get_request_when_succeed_should_do_as_expected(self,
                                                                mocker,
                                                                http_client_mock: http_client_mock,
                                                                base_url,
                                                                request_params,
                                                                request_headers,
                                                                response):
    # Arrange
    mock_log_info = mocker.patch.object(http_client_mock.logger, 'info')
    mock_client_session = mocker.patch('aiohttp.client.ClientSession')
    mock_client_response = mocker.patch('aiohttp.client.ClientResponse')
    mock_authorization = mocker.MagicMock()
    mock_client_session_constructor = mocker.patch.object(ClientSession, '__aenter__', return_value=mock_client_session)
    mocker.patch.object(mock_client_response, '__aenter__', return_value=mock_client_response)
    mock_client_session_get_response = mocker.patch.object(mock_client_session, 'get',
                                                           return_value=mock_client_response)
    response_future = asyncio.Future()
    response_future.set_result(response["result"])
    mock_client_session_get_response_json = mocker.patch.object(mock_client_response, 'json',
                                                                return_value=response_future)
    mock_client_response.headers.get.return_value = 'application/json'
    mock_client_response.status = 200
    mock_client_response.reason = 'OK'
    response["headers"] = mock_client_response.headers
    # Act and asserts
    assert await http_client_mock.get(base_url,
                                      request_params,
                                      request_headers,
                                      mock_authorization) == response, "Valid results must be returned"
    mock_log_info.assert_any_call("Get url: %s", base_url)
    mock_client_session_constructor.assert_called_once_with()
    mock_client_session_get_response.assert_called_once_with(base_url,
                                                             params=request_params,
                                                             headers=request_headers,
                                                             timeout=http_client_mock.session_timeout,
                                                             auth=mock_authorization)
    mock_client_session_get_response_json.assert_called_once_with()
    mock_client_response.headers.get.assert_called_once_with('Content-Type')

  @pytest.mark.parametrize(
    "exception, error_message, url", [
      (AsyncTimeoutError("Timeout error occurred"),
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
                                                                  http_client_mock: http_client_mock,
                                                                  exception,
                                                                  error_message,
                                                                  url):
    # Arrange
    mock_log_error = mocker.patch.object(http_client_mock.logger, 'error')
    mock_client_session = mocker.patch('aiohttp.client.ClientSession')
    mock_client_response = mocker.patch('aiohttp.client.ClientResponse')
    mock_auth = mocker.MagicMock()
    mock_client_session_constructor = mocker.patch.object(ClientSession, '__aenter__', return_value=mock_client_session)
    mocker.patch.object(mock_client_response, '__aenter__', return_value=mock_client_response)
    mock_client_session_get_response = mocker.patch.object(mock_client_session, 'get',
                                                           side_effect=exception)

    # Act and asserts
    assert await http_client_mock.get(base_url=url,
                                      request_params="request_params",
                                      request_headers="request_headers",
                                      auth=mock_auth,
                                      timeout=http_client_mock.session_timeout) == {}, "Valid results must be returned"
    http_client_mock.logger.info.assert_any_call("Get url: %s", url)
    mock_client_session_constructor.assert_called_once_with()
    mock_client_session_get_response.assert_called_once_with(url,
                                                             params="request_params",
                                                             headers="request_headers",
                                                             timeout=http_client_mock.session_timeout,
                                                             auth=mock_auth)
    mock_log_error.assert_called_once_with(error_message)
    assert http_client_mock.session_request_errors[
             0] == error_message, "session_request_error message must be set!"

  @pytest.mark.parametrize(
    "exception, error_message, url", [
      (AsyncTimeoutError("Timeout error occurred"),
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
  async def test_post_request_when_exception_should_do_as_expected(self,
                                                                   mocker,
                                                                   http_client_mock: http_client_mock,
                                                                   exception,
                                                                   error_message,
                                                                   url):
    # Arrange
    mock_headers = mocker.MagicMock()
    mock_params = mocker.MagicMock()
    mock_json = mocker.MagicMock()
    mock_data = mocker.MagicMock()
    mock_auth = mocker.MagicMock()
    mock_log_info = mocker.patch.object(http_client_mock.logger, 'info')
    mock_log_error = mocker.patch.object(http_client_mock.logger, 'error')
    mock_client_session = mocker.patch('aiohttp.client.ClientSession')
    mock_client_response = mocker.patch('aiohttp.client.ClientResponse')
    mock_client_session_constructor = mocker.patch.object(ClientSession, '__aenter__', return_value=mock_client_session)
    mocker.patch.object(mock_client_response, '__aenter__', return_value=mock_client_response)
    mock_client_session_get_response = mocker.patch.object(mock_client_session, 'post',
                                                           side_effect=exception)
    # Act and asserts
    assert await http_client_mock.post(base_url=url,
                                       request_params=mock_params,
                                       json=mock_json,
                                       data=mock_data,
                                       auth=mock_auth,
                                       request_headers=mock_headers,
                                       timeout=http_client_mock.session_timeout) == {}, "Valid results must be returned"
    mock_log_info.assert_any_call('Post url: %s', url)
    mock_client_session_constructor.assert_called_once_with()
    mock_client_session_get_response.assert_called_once_with(url,
                                                             headers=mock_headers,
                                                             params=mock_params,
                                                             timeout=http_client_mock.session_timeout,
                                                             json=mock_json,
                                                             data=mock_data,
                                                             auth=mock_auth)
    mock_log_error.assert_called_once_with(error_message)
    assert http_client_mock.session_request_errors[
             0] == error_message, "session_request_error message must be set!"

  @pytest.mark.asyncio
  async def test_post_request_when_succeed_should_do_as_expected(self,
                                                                 mocker,
                                                                 http_client_mock: http_client_mock):
    # Arrange
    mock_headers = mocker.MagicMock()
    mock_params = mocker.MagicMock()
    mock_json = mocker.MagicMock()
    mock_data = mocker.MagicMock()
    mock_auth = mocker.MagicMock()
    mock_log_info = mocker.patch.object(http_client_mock.logger, 'info')
    mock_client_session = mocker.patch('aiohttp.client.ClientSession')
    mock_client_response = mocker.patch('aiohttp.client.ClientResponse')
    mock_client_session_constructor = mocker.patch.object(ClientSession, '__aenter__', return_value=mock_client_session)
    mocker.patch.object(mock_client_response, '__aenter__', return_value=mock_client_response)
    mock_client_session_post_response = mocker.patch.object(mock_client_session, 'post',
                                                            return_value=mock_client_response)
    response_future = asyncio.Future()
    response_future.set_result({"status": 200, 'result': 'test'})
    mock_client_session_get_response_json = mocker.patch.object(mock_client_response, 'json',
                                                                return_value=response_future)
    mock_client_response.headers.get.return_value = 'application/json'
    mock_client_response.status = 200
    mock_client_response.reason = 'OK'
    # Act and asserts
    ret = await http_client_mock.post(base_url="base_url",
                                      request_params=mock_params,
                                      json=mock_json,
                                      data=mock_data,
                                      auth=mock_auth,
                                      request_headers=mock_headers,
                                      timeout=http_client_mock.session_timeout)
    assert ret, "Valid results must be returned"
    assert ret.get("status") == 200, "Response status should be as expected"
    assert ret.get("headers") == mock_client_response.headers, "Response headers should not be none"
    assert ret.get("reason") == "OK", "Response reason should be as expected"
    assert ret.get("result") == {"status": 200, 'result': 'test'}, "Response result should be as expected"

    mock_log_info.assert_any_call("Post url: %s", "base_url")
    mock_client_session_constructor.assert_called_once_with()
    mock_client_session_post_response.assert_called_once_with("base_url",
                                                              headers=mock_headers,
                                                              params=mock_params,
                                                              timeout=http_client_mock.session_timeout,
                                                              json=mock_json,
                                                              data=mock_data,
                                                              auth=mock_auth)
    mock_client_session_get_response_json.assert_called_once_with()
    mock_client_response.headers.get.assert_called_once_with('Content-Type')

  @pytest.mark.asyncio
  async def test_delete_request_when_succeed_should_do_as_expected(self,
                                                                   mocker,
                                                                   http_client_mock: http_client_mock):
    # Arrange
    mock_headers = mocker.MagicMock()
    mock_params = mocker.MagicMock()
    mock_json = mocker.MagicMock()
    mock_data = mocker.MagicMock()
    mock_auth = mocker.MagicMock()
    mock_client_session = mocker.patch('aiohttp.client.ClientSession')
    mock_client_response = mocker.patch('aiohttp.client.ClientResponse')
    mock_client_session_constructor = mocker.patch.object(ClientSession, '__aenter__', return_value=mock_client_session)
    mocker.patch.object(mock_client_response, '__aenter__', return_value=mock_client_response)
    mock_client_session_delete_response = mocker.patch.object(mock_client_session, 'delete',
                                                              return_value=mock_client_response)
    response_future = asyncio.Future()
    response_future.set_result({"status": 200, 'message': 'deleted'})
    mock_client_session_get_response_json = mocker.patch.object(mock_client_response, 'json',
                                                                return_value=response_future)
    mock_client_response.headers.get.return_value = 'application/json'
    mock_client_response.status = 200
    mock_client_response.reason = 'OK'
    # Act and asserts
    ret = await http_client_mock.delete(base_url="base_url",
                                        request_params=mock_params,
                                        json=mock_json,
                                        data=mock_data,
                                        auth=mock_auth,
                                        request_headers=mock_headers,
                                        timeout=http_client_mock.session_timeout)
    assert ret, "Valid results must be returned"
    assert ret.get("status") == 200, "Response status should be as expected"
    assert ret.get("headers") == mock_client_response.headers, "Response headers should not be none"
    assert ret.get("reason") == "OK", "Response reason should be as expected"
    assert ret.get("result") == {"status": 200, 'message': 'deleted'}, "Response result should be as expected"

    http_client_mock.logger.info.assert_any_call("Delete url: %s", "base_url")
    mock_client_session_constructor.assert_called_once_with()
    mock_client_session_delete_response.assert_called_once_with("base_url",
                                                                headers=mock_headers,
                                                                params=mock_params,
                                                                timeout=http_client_mock.session_timeout,
                                                                json=mock_json,
                                                                data=mock_data,
                                                                auth=mock_auth)
    mock_client_session_get_response_json.assert_called_once_with()
    mock_client_response.headers.get.assert_called_once_with('Content-Type')

  @pytest.mark.asyncio
  async def test_get_request_invalid_url_should_fail(self):
    client = AsyncHttpClient(10)
    ret = await client.get("invalid_url")
    assert client.session_request_errors == [
      'Client session InvalidURL for url (invalid_url) with error: invalid_url'], "Error must be set"
    assert not ret, "Response should be empty"

  @pytest.mark.parametrize(
    "base_url, request_params, content", [
      ('https://www.google.com', {'Accept': 'application/text'}, None),
      ('https://jsonplaceholder.typicode.com/todos/1', {'Accept': 'application/json'},
       {"userId": 1, "id": 1, "title": "delectus aut autem", "completed": False}),
      ('https://data.fz-juelich.de/api/search', {'Accept': 'application/json', 'q': 'data'},
       {'status': 'OK', 'data': {'q': 'data', 'total_count': 3472, 'start': 0, 'spelling_alternatives': {}, 'items': [
         {'name': 'Metabolic Networks', 'type': 'dataverse',
          'url': 'https://data.fz-juelich.de/dataverse/metabolic_networks', 'identifier': 'metabolic_networks',
          'description': 'This dataverse contains models and data related to metabolic networks and fluxomics.',
          'published_at': '2020-12-18T21:32:24Z'},
         {'name': 'CLaMS Dataverse', 'type': 'dataverse', 'url': 'https://data.fz-juelich.de/dataverse/clams',
          'identifier': 'clams',
          'description': 'Data sets with regard to the Chemical Lagrangian Model of the Stratosphere (CLaMS)',
          'published_at': '2020-11-18T13:02:23Z'}, {'name': 'Waves and Dynamics Dataverse', 'type': 'dataverse',
                                                    'url': 'https://data.fz-juelich.de/dataverse/waves',
                                                    'identifier': 'waves',
                                                    'description': 'Data sets with regard to the Remote Sensing Group of IEK-7',
                                                    'published_at': '2021-04-12T14:28:19Z'},
         {'name': 'Campus Collection', 'type': 'dataverse', 'url': 'https://data.fz-juelich.de/dataverse/campus',
          'identifier': 'campus',
          'description': 'A "catch all" like collection of datasets for research data not fitting elsewhere.',
          'published_at': '2020-05-27T13:37:24Z'},
         {'name': 'Earth System Science', 'type': 'dataverse', 'url': 'https://data.fz-juelich.de/dataverse/ess',
          'identifier': 'ess',
          'description': 'Collection of Earth system science data sets generated at JSC or in collaboration with JSC',
          'published_at': '2020-11-18T14:14:40Z'},
         {'name': 'Dynamics of Complex Fluids and Interfaces', 'type': 'dataverse',
          'url': 'https://data.fz-juelich.de/dataverse/compflu', 'identifier': 'compflu',
          'description': 'Research data of the Dept. Dynamics of Complex Fluids and Interfaces at HI ERN (IEK-11)',
          'published_at': '2020-11-23T08:40:07Z'},
         {'name': 'Raman data.7z', 'type': 'file', 'url': 'https://data.fz-juelich.de/api/access/datafile/12892',
          'file_id': '12892',
          'description': 'A folder with a collection of Raman datasets (in .txt format) of barite crystallization from bulk solution as function of time.\r\n\r\n',
          'published_at': '2023-10-12T15:14:39Z', 'file_type': '7Z Archive',
          'file_content_type': 'application/x-7z-compressed', 'size_in_bytes': 22858,
          'checksum': {'type': 'SHA-256', 'value': 'eba801f1d145a1ce72b6a9b057a74aca8201de5f7e1e66321e751c839c9864bb'},
          'dataset_name': 'Experimental data for Microfluidic investigation of pore-size dependency of barite nucleation',
          'dataset_id': '12889', 'dataset_persistent_id': 'doi:10.26165/JUELICH-DATA/2SCFCA',
          'dataset_citation': 'Poonoosamy, Jenna; Obaied, Abdulmonem; Deissmann, Guido; Prasianakis, Nikolaos I.; Kindelmann, Moritz; Wollenhaupt, Bastian; Bosbach, Dirk; Curti, Enzo, 2023, "Experimental data for Microfluidic investigation of pore-size dependency of barite nucleation", https://doi.org/10.26165/JUELICH-DATA/2SCFCA, Jülich DATA, V1'},
         {'name': 'data.csv', 'type': 'file', 'url': 'https://data.fz-juelich.de/api/access/datafile/2232',
          'file_id': '2232', 'published_at': '2020-08-28T10:42:11Z', 'file_type': 'Comma Separated Values',
          'file_content_type': 'text/csv', 'size_in_bytes': 44643,
          'checksum': {'type': 'SHA-256', 'value': '69d0ad11f6a0667d85dfef622a1f3ac67a7d6da908131d09c505ca5fcaccfa90'},
          'file_persistent_id': 'doi:10.26165/JUELICH-DATA/TVWUUP/CTU4AV',
          'dataset_name': 'ELPVPower: A dataset for large scale PV power prediction using EL images of cells',
          'dataset_id': '1100', 'dataset_persistent_id': 'doi:10.26165/JUELICH-DATA/TVWUUP',
          'dataset_citation': 'Hoffmann, Mathis; Buerhop-Lutz, Claudia; Reeb, Luca; Pickel, Tobias; Winkler, Thilo; Doll, Bernd; Würfl, Tobias; Peters, Ian Marius; Brabec, Christoph J.; Maier, Andreas; Christlein, Vincent, 2020, "ELPVPower: A dataset for large scale PV power prediction using EL images of cells", https://doi.org/10.26165/JUELICH-DATA/TVWUUP, Jülich DATA, V1'},
         {'name': 'Source-Data-GeTe-Nanowires.xlsx', 'type': 'file',
          'url': 'https://data.fz-juelich.de/api/access/datafile/3028', 'file_id': '3028',
          'description': 'Flux periodic oscillations and phase-coherent transport in GeTe nanowire-based devices: Source data underlying Figs. 1-4 and Supplementary Figs. S3, S6, and S8. ',
          'published_at': '2020-12-16T06:20:53Z', 'file_type': 'MS Excel Spreadsheet',
          'file_content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          'size_in_bytes': 1598762,
          'checksum': {'type': 'SHA-256', 'value': '60dc3f3e9c729366803a0332ad5768c1ce0904afe9e606d7cca0766e6694a406'},
          'dataset_name': 'Data for: Flux periodic oscillations and phase-coherent transport in GeTe nanowire-based devices',
          'dataset_id': '3027', 'dataset_persistent_id': 'doi:10.26165/JUELICH-DATA/M1IQVG',
          'dataset_citation': 'Zhang, Jinzhong; Tse, Pok-Lam; Jalil, Abdur-Rehman; Kölzer, Jonas; Rosenbach, Daniel; Luysberg, Martina; Panaitov, Gergory; Lüth, Hans; Hu, Zhigao; Grützmacher, Detlev; Lüth, Hans; Lu, Jia Grace; Schäpers, Thomas, 2020, "Data for: Flux periodic oscillations and phase-coherent transport in GeTe nanowire-based devices", https://doi.org/10.26165/JUELICH-DATA/M1IQVG, Jülich DATA, V1'},
         {'name': 'Experimental data of 226Ra sorption kinetics.xlsx', 'type': 'file',
          'url': 'https://data.fz-juelich.de/api/access/datafile/12861', 'file_id': '12861',
          'description': 'Table A5. Experimental data of 226Ra sorption kinetics on sandy Opalinus Clay at pH 7.6 and I = 0.39 mol·L-1 (cf. Fig. 9).\r\n',
          'published_at': '2023-10-10T06:24:41Z', 'file_type': 'MS Excel Spreadsheet',
          'file_content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          'size_in_bytes': 11510,
          'checksum': {'type': 'SHA-256', 'value': '01f2a3b2a3d71435aa89cb61e48b33b7d76370ce3c3c45903fef266bb61fb062'},
          'dataset_name': 'Experimental data for: Retention of 226Ra in the sandy Opalinus Clay facies from the Mont Terri rock laboratory, Switzerland',
          'dataset_id': '12855', 'dataset_persistent_id': 'doi:10.26165/JUELICH-DATA/IFD1I9',
          'dataset_citation': 'Ait Mouheb, Naila; Yang, Yuankai; Deissmann, Guido; Klinkenberg, Martina; Poonoosamy, Jenna; Vinograd, Victor; Van Loon, Luc R.; Bosbach, Dirk, 2023, "Experimental data for: Retention of 226Ra in the sandy Opalinus Clay facies from the Mont Terri rock laboratory, Switzerland", https://doi.org/10.26165/JUELICH-DATA/IFD1I9, Jülich DATA, V1'}],
                                 'count_in_response': 10}})
    ])
  @pytest.mark.asyncio
  async def test_client_get_request_for_valid_urls_should_succeed(self,
                                                                  base_url,
                                                                  request_params,
                                                                  content):
    client = AsyncHttpClient(10)
    ret = await client.get(base_url, request_params)
    assert ret, "Response should not be empty"
    assert isinstance(ret, dict), "Response type should be as expected"
    assert ret.get("result") == content if content else ret.get("result"), "Response should be as expected"
    assert ret.get("status") == 200, "Response status should be as expected"
    assert ret.get("headers") is not None, "Response headers should be as expected"
    assert ret.get("reason") == "OK", "Response reason should be as expected"
    assert client.session_request_errors == [], "session_request_errors should be empty"

  @pytest.mark.parametrize(
    "base_url, request_params, response_key, content", [
      ('https://httpbin.org/post', {'Content-Type': 'application/json', 'Accept': 'application/json'}, 'json',
       {"userId": 1, "id": 1, "title": "delectus aut autem", "completed": False}),
      ('https://httpbin.org/post', {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'},
       'form', {"userId": "1", "id": "1", "title": "delectus aut autem", "completed": "False"}),
    ])
  @pytest.mark.asyncio
  async def test_client_post_request_should_succeed(self,
                                                    base_url,
                                                    request_params,
                                                    response_key,
                                                    content):
    client = AsyncHttpClient(10)
    ret = await client.post(base_url,
                            request_params,
                            json=content if "json" == response_key else None,
                            data=content if "form" == response_key else None)
    assert ret, "Response should not be empty"
    assert ret.get("status") == 200, "Response status should be as expected"
    assert ret.get("headers") is not None, "Response headers should not be none"
    assert ret.get("reason") == "OK", "Response reason should be as expected"
    assert client.session_request_errors == [], "session_request_errors should be empty"
    assert are_json_equal(content, ret.get("result").get(response_key)), "Response should be as expected"
