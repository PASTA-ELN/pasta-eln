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
from testsAdvanced.common.fixtures import http_client_mock
from testsAdvanced.common.test_utils import are_json_equal

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
    assert service.session_timeout == 5, 'session_timeout should be set to 5'
    assert service.session_request_errors == [], 'session_request_errors should be empty'

  @pytest.mark.parametrize(
    'status, headers, reason, result', [
      (200, {'Content-Type': 'application/json'}, 'OK', 'testing'),
      (400, {'Content-Type': 'application/json'}, 'Bad Request', 'testing'),
      (500, {'Content-Type': 'application/json'}, 'Internal Server Error', 'testing'),
      (200, {'Content-Type': 'text/plain'}, 'OK', 'testing'),
      (400, {'Content-Type': 'text/plain'}, 'Bad Request', 'testing'),
      (500, {'Content-Type': 'application/json;charset=UTF-8'}, 'Internal Server Error', 'testing')
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
    if 'json' in headers.get('Content-Type'):
      mock_client_response.json.return_value = response_future
    else:
      mock_client_response.text.return_value = response_future

    assert await prepare_result(
      mock_client_response
    ) == {'status': status, 'reason': reason, 'result': result, 'headers': headers}, 'Should return expected result'
    if 'json' in headers.get('Content-Type'):
      mock_client_response.json.assert_called_once()
    else:
      mock_client_response.text.assert_called_once()

  @pytest.mark.parametrize(
    'base_url, request_params, request_headers, response', [
      ('https://example.com', {'param_key': 'param_value'}, {'Accept': 'application/text'},
       {'status': 200, 'reason': 'OK', 'result': 'test'}),
      ('https://example.com', {'param_key': 'param_value'}, {'Accept': 'application/json'},
       {'status': 200, 'reason': 'OK', 'result': 'testing'}),
      ('https://example.com', {}, {}, {'status': 200, 'reason': 'OK', 'result': 'test'})
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
    mock_client_timeout = mocker.patch('pasta_eln.webclient.http_client.ClientTimeout')
    mock_authorization = mocker.MagicMock()
    mock_client_session_constructor = mocker.patch.object(ClientSession, '__aenter__', return_value=mock_client_session)
    mocker.patch.object(mock_client_response, '__aenter__', return_value=mock_client_response)
    mock_client_session_get_response = mocker.patch.object(mock_client_session, 'get',
                                                           return_value=mock_client_response)
    response_future = asyncio.Future()
    response_future.set_result(response['result'])
    mock_client_session_get_response_json = mocker.patch.object(mock_client_response, 'json',
                                                                return_value=response_future)
    mock_client_response.headers.get.return_value = 'application/json'
    mock_client_response.status = 200
    mock_client_response.reason = 'OK'
    response['headers'] = mock_client_response.headers
    # Act and asserts
    assert await http_client_mock.get(base_url,
                                      request_params,
                                      request_headers,
                                      mock_authorization) == response, 'Valid results must be returned'
    mock_log_info.assert_any_call('Get url: %s', base_url)
    mock_client_session_constructor.assert_called_once_with()
    mock_client_timeout.assert_called_once_with(total=http_client_mock.session_timeout)
    mock_client_session_get_response.assert_called_once_with(base_url,
                                                             params=request_params,
                                                             headers=request_headers,
                                                             timeout=mock_client_timeout.return_value,
                                                             auth=mock_authorization)
    mock_client_session_get_response_json.assert_called_once_with()
    mock_client_response.headers.get.assert_called_once_with('Content-Type')

  @pytest.mark.parametrize(
    'exception, error_message, url', [
      (AsyncTimeoutError('Timeout error occurred'),
       'Client session request timeout for url (http://url.com) with error: Timeout error occurred',
       'http://url.com'),
      (CancelledError('Request cancelled'),
       'Client session request cancelled for url (http://url.com) with error: Request cancelled',
       'http://url.com'),
      (InvalidStateError('Invalid state'),
       'Client session request in invalid state for url (http://url.com) with error: Invalid state',
       'http://url.com'),
      (IncompleteReadError(b'Partial', expected=20),
       'Client session request incomplete read for url (http://url.com) with error: 7 bytes read on a total of 20 expected bytes',
       'http://url.com'),
      (LimitOverrunError('Limit overrun', 1),
       'Client session request limit overrun for url (http://url.com) with error: Limit overrun',
       'http://url.com'),
      (TypeError('TypeError occurred'),
       'Client session type error for url (http://url.com) with error: TypeError occurred',
       'http://url.com'),
      (ClientConnectorError(
        connection_key=ConnectionKey(ssl=False, host='url.com', port=443, is_ssl=False, proxy=None, proxy_auth=None,
                                     proxy_headers_hash=0), os_error=OSError()),
       'ClientConnectorError for url (http://url.com) with error: Cannot connect to host url.com:443 ssl:False [None]',
       'http://url.com'),
      (InvalidURL('InvalidURL occurred'),
       'Client session InvalidURL for url (None) with error: InvalidURL occurred',
       'None'),
      (InvalidURL('InvalidURL occurred'),
       'Client session InvalidURL for url (None) with error: InvalidURL occurred',
       None),
      (JSONDecodeError('JSONDecodeError occurred', doc='test', pos=9),
       'Client session JSONDecodeError for url (http://url.com) with error: JSONDecodeError occurred: line 1 column 10 (char 9)',
       'http://url.com'),
      (TypeError('Constructor parameter should be str'),
       'Client session type error for url (None) with error: Constructor parameter should be str',
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
    mock_client_timeout = mocker.patch('pasta_eln.webclient.http_client.ClientTimeout')
    mock_auth = mocker.MagicMock()
    mock_client_session_constructor = mocker.patch.object(ClientSession, '__aenter__', return_value=mock_client_session)
    mocker.patch.object(mock_client_response, '__aenter__', return_value=mock_client_response)
    mock_client_session_get_response = mocker.patch.object(mock_client_session, 'get',
                                                           side_effect=exception)

    # Act and asserts
    assert await http_client_mock.get(base_url=url,
                                      request_params='request_params',
                                      request_headers='request_headers',
                                      auth=mock_auth,
                                      timeout=mock_client_timeout.return_value) == {}, 'Valid results must be returned'
    http_client_mock.logger.info.assert_any_call('Get url: %s', url)
    mock_client_session_constructor.assert_called_once_with()
    mock_client_session_get_response.assert_called_once_with(url,
                                                             params='request_params',
                                                             headers='request_headers',
                                                             timeout=mock_client_timeout.return_value,
                                                             auth=mock_auth)
    mock_log_error.assert_called_once_with(error_message)
    assert http_client_mock.session_request_errors[
             0] == error_message, 'session_request_error message must be set!'

  @pytest.mark.parametrize(
    'exception, error_message, url', [
      (AsyncTimeoutError('Timeout error occurred'),
       'Client session request timeout for url (http://url.com) with error: Timeout error occurred',
       'http://url.com'),
      (CancelledError('Request cancelled'),
       'Client session request cancelled for url (http://url.com) with error: Request cancelled',
       'http://url.com'),
      (InvalidStateError('Invalid state'),
       'Client session request in invalid state for url (http://url.com) with error: Invalid state',
       'http://url.com'),
      (IncompleteReadError(b'Partial', expected=20),
       'Client session request incomplete read for url (http://url.com) with error: 7 bytes read on a total of 20 expected bytes',
       'http://url.com'),
      (LimitOverrunError('Limit overrun', 1),
       'Client session request limit overrun for url (http://url.com) with error: Limit overrun',
       'http://url.com'),
      (TypeError('TypeError occurred'),
       'Client session type error for url (http://url.com) with error: TypeError occurred',
       'http://url.com'),
      (ClientConnectorError(
        connection_key=ConnectionKey(ssl=False, host='url.com', port=443, is_ssl=False, proxy=None, proxy_auth=None,
                                     proxy_headers_hash=0), os_error=OSError()),
       'ClientConnectorError for url (http://url.com) with error: Cannot connect to host url.com:443 ssl:False [None]',
       'http://url.com'),
      (InvalidURL('InvalidURL occurred'),
       'Client session InvalidURL for url (None) with error: InvalidURL occurred',
       'None'),
      (InvalidURL('InvalidURL occurred'),
       'Client session InvalidURL for url (None) with error: InvalidURL occurred',
       None),
      (JSONDecodeError('JSONDecodeError occurred', doc='test', pos=9),
       'Client session JSONDecodeError for url (http://url.com) with error: JSONDecodeError occurred: line 1 column 10 (char 9)',
       'http://url.com'),
      (TypeError('Constructor parameter should be str'),
       'Client session type error for url (None) with error: Constructor parameter should be str',
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
    mock_client_timeout = mocker.patch('pasta_eln.webclient.http_client.ClientTimeout')
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
                                       timeout=mock_client_timeout.return_value) == {}, 'Valid results must be returned'
    mock_log_info.assert_any_call('Post url: %s', url)
    mock_client_session_constructor.assert_called_once_with()
    mock_client_session_get_response.assert_called_once_with(url,
                                                             headers=mock_headers,
                                                             params=mock_params,
                                                             timeout=mock_client_timeout.return_value,
                                                             json=mock_json,
                                                             data=mock_data,
                                                             auth=mock_auth)
    mock_log_error.assert_called_once_with(error_message)
    assert http_client_mock.session_request_errors[
             0] == error_message, 'session_request_error message must be set!'

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
    mock_client_timeout = mocker.patch('pasta_eln.webclient.http_client.ClientTimeout')
    mock_client_session_constructor = mocker.patch.object(ClientSession, '__aenter__', return_value=mock_client_session)
    mocker.patch.object(mock_client_response, '__aenter__', return_value=mock_client_response)
    mock_client_session_post_response = mocker.patch.object(mock_client_session, 'post',
                                                            return_value=mock_client_response)
    response_future = asyncio.Future()
    response_future.set_result({'status': 200, 'result': 'test'})
    mock_client_session_get_response_json = mocker.patch.object(mock_client_response, 'json',
                                                                return_value=response_future)
    mock_client_response.headers.get.return_value = 'application/json'
    mock_client_response.status = 200
    mock_client_response.reason = 'OK'
    # Act and asserts
    ret = await http_client_mock.post(base_url='base_url',
                                      request_params=mock_params,
                                      json=mock_json,
                                      data=mock_data,
                                      auth=mock_auth,
                                      request_headers=mock_headers,
                                      timeout=mock_client_timeout.return_value)
    assert ret, 'Valid results must be returned'
    assert ret.get('status') == 200, 'Response status should be as expected'
    assert ret.get('headers') == mock_client_response.headers, 'Response headers should not be none'
    assert ret.get('reason') == 'OK', 'Response reason should be as expected'
    assert ret.get('result') == {'status': 200, 'result': 'test'}, 'Response result should be as expected'

    mock_log_info.assert_any_call('Post url: %s', 'base_url')
    mock_client_session_constructor.assert_called_once_with()
    mock_client_session_post_response.assert_called_once_with('base_url',
                                                              headers=mock_headers,
                                                              params=mock_params,
                                                              timeout=mock_client_timeout.return_value,
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
    mock_client_timeout = mocker.patch('pasta_eln.webclient.http_client.ClientTimeout')
    mock_client_session_constructor = mocker.patch.object(ClientSession, '__aenter__', return_value=mock_client_session)
    mocker.patch.object(mock_client_response, '__aenter__', return_value=mock_client_response)
    mock_client_session_delete_response = mocker.patch.object(mock_client_session, 'delete',
                                                              return_value=mock_client_response)
    response_future = asyncio.Future()
    response_future.set_result({'status': 200, 'message': 'deleted'})
    mock_client_session_get_response_json = mocker.patch.object(mock_client_response, 'json',
                                                                return_value=response_future)
    mock_client_response.headers.get.return_value = 'application/json'
    mock_client_response.status = 200
    mock_client_response.reason = 'OK'
    # Act and asserts
    ret = await http_client_mock.delete(base_url='base_url',
                                        request_params=mock_params,
                                        json=mock_json,
                                        data=mock_data,
                                        auth=mock_auth,
                                        request_headers=mock_headers,
                                        timeout=mock_client_timeout.return_value)
    assert ret, 'Valid results must be returned'
    assert ret.get('status') == 200, 'Response status should be as expected'
    assert ret.get('headers') == mock_client_response.headers, 'Response headers should not be none'
    assert ret.get('reason') == 'OK', 'Response reason should be as expected'
    assert ret.get('result') == {'status': 200, 'message': 'deleted'}, 'Response result should be as expected'

    http_client_mock.logger.info.assert_any_call('Delete url: %s', 'base_url')
    mock_client_session_constructor.assert_called_once_with()
    mock_client_session_delete_response.assert_called_once_with('base_url',
                                                                headers=mock_headers,
                                                                params=mock_params,
                                                                timeout=mock_client_timeout.return_value,
                                                                json=mock_json,
                                                                data=mock_data,
                                                                auth=mock_auth)
    mock_client_session_get_response_json.assert_called_once_with()
    mock_client_response.headers.get.assert_called_once_with('Content-Type')

  @pytest.mark.asyncio
  async def test_get_request_invalid_url_should_fail(self):
    client = AsyncHttpClient(10)
    ret = await client.get('invalid_url')
    assert client.session_request_errors == [
      'Client session InvalidURL for url (invalid_url) with error: invalid_url'], 'Error must be set'
    assert not ret, 'Response should be empty'
