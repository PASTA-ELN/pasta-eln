#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_client.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from asyncio import Future
from datetime import datetime
from json import dumps

import pytest
from aiohttp import InvalidURL
from requests.exceptions import ConnectionError, MissingSchema

from pasta_eln.dataverse.client import DataverseClient
from tests.common.fixtures import dataverse_client_mock, dataverse_list_mock, dataverse_tree_mock

pytest_plugins = ('pytest_asyncio',)


class TestDataverseClient(object):

  def test_dataverse_client_initialization_should_succeed(self, mocker):
    mock_logger = mocker.patch('logging.Logger')
    mock_client = mocker.MagicMock()
    mock_get_logger = mocker.patch('pasta_eln.dataverse.client.logging.getLogger', return_value=mock_logger)
    mock_http_client = mocker.patch('pasta_eln.dataverse.client.AsyncHttpClient', return_value=mock_client)
    client = DataverseClient(server_url="test_url", api_token="test_token")
    mock_get_logger.assert_called_once_with('pasta_eln.dataverse.client.DataverseClient')
    mock_http_client.assert_called_once_with(10)
    assert client.logger is mock_logger
    assert client.server_url == "test_url"
    assert client.api_token == "test_token"
    assert client.http_client is mock_client

  @pytest.mark.asyncio
  async def test_check_if_token_expired_success_returns_true(self, mocker,
                                                             dataverse_client_mock: dataverse_client_mock):
    mock_get_token_info = {'status': 200, 'reason': 'OK', 'result': {'status': 'OK',
                                                                     'data': {
                                                                       'message': f'Token {dataverse_client_mock.api_token} expires on 2024-12-04 14:18:49.967'}}}
    result_future = Future()
    result_future.set_result(mock_get_token_info)

    date_time_mock = mocker.patch('pasta_eln.dataverse.client.datetime')
    date_time_mock.now.return_value = datetime.strptime("2024-01-04 14:18:49.967", '%Y-%m-%d %H:%M:%S.%f')
    date_time_mock.strptime.return_value = datetime.strptime("2024-12-04 14:18:49.967", '%Y-%m-%d %H:%M:%S.%f')

    mocker.patch.object(dataverse_client_mock.http_client, 'get', return_value=result_future)
    assert await dataverse_client_mock.check_if_token_expired() == False, "Must return false"
    dataverse_client_mock.logger.info.assert_called_once_with("Checking token expiry, Server: %s",
                                                              dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_once_with(f"{dataverse_client_mock.server_url}/api/users/token",
                                                                  request_headers={'Accept': 'application/json',
                                                                                   'X-Dataverse-key': dataverse_client_mock.api_token})
    date_time_mock.now.assert_called_once()
    date_time_mock.strptime.assert_called_once_with("2024-12-04 14:18:49.967", '%Y-%m-%d %H:%M:%S.%f')

  @pytest.mark.asyncio
  async def test_check_if_token_expired_not_expired_returns_false(self, mocker,
                                                                  dataverse_client_mock: dataverse_client_mock):
    mock_get_token_info = {'status': 200, 'reason': 'OK', 'result': {'status': 'OK',
                                                                     'data': {
                                                                       'message': f'Token {dataverse_client_mock.api_token} expires on 2024-01-04 14:18:49.967'}}}
    result_future = Future()
    result_future.set_result(mock_get_token_info)

    date_time_mock = mocker.patch('pasta_eln.dataverse.client.datetime')
    date_time_mock.now.return_value = datetime.strptime("2024-12-04 14:18:49.967", '%Y-%m-%d %H:%M:%S.%f')
    date_time_mock.strptime.return_value = datetime.strptime("2024-01-04 14:18:49.967", '%Y-%m-%d %H:%M:%S.%f')

    mocker.patch.object(dataverse_client_mock.http_client, 'get', return_value=result_future)
    assert await dataverse_client_mock.check_if_token_expired() == True, "Must return True"
    dataverse_client_mock.logger.info.assert_called_once_with("Checking token expiry, Server: %s",
                                                              dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_once_with(f"{dataverse_client_mock.server_url}/api/users/token",
                                                                  request_headers={'Accept': 'application/json',
                                                                                   'X-Dataverse-key': dataverse_client_mock.api_token})
    date_time_mock.now.assert_called_once()
    date_time_mock.strptime.assert_called_once_with("2024-01-04 14:18:49.967", '%Y-%m-%d %H:%M:%S.%f')

  @pytest.mark.asyncio
  async def test_check_if_token_expired_for_unauthorized_token_returns_false(self, mocker,
                                                                             dataverse_client_mock: dataverse_client_mock):
    mocked_fail_result = {'status': 401, 'reason': 'Unauthorized',
                          'result': {'status': 'ERROR', 'message': 'Bad API key'}}
    result_future = Future()
    result_future.set_result(mocked_fail_result)
    mocker.patch.object(dataverse_client_mock.http_client, 'get', return_value=result_future)
    assert await dataverse_client_mock.check_if_token_expired() == False, "Must return False!"
    dataverse_client_mock.logger.error.assert_called_once_with(
      "Error checking token expiration, Server: test_url, Reason: "
      "Unauthorized, Info: {'status': ""'ERROR', 'message': 'Bad API key'}")
    dataverse_client_mock.logger.info.assert_called_with("Checking token expiry, Server: %s",
                                                         dataverse_client_mock.server_url)

  @pytest.mark.asyncio
  async def test_check_if_token_expired_when_request_fails_returns_error(self, mocker,
                                                                         dataverse_client_mock: dataverse_client_mock):
    future = Future()
    future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'get', side_effect=[future])
    dataverse_client_mock.http_client.session_request_errors = [
      "ClientConnectorError for url (url) with error: Cannot connect to host localhost:8080 ssl:default [Connect call failed ('127.0.0.1', 8080)]"]
    result = await dataverse_client_mock.check_if_token_expired()
    assert result == False, "Not expected result!"
    dataverse_client_mock.logger.info.assert_called_with("Checking token expiry, Server: %s",
                                                         dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_with(f"{dataverse_client_mock.server_url}/api/users/token",
                                                             request_headers={'Accept': 'application/json',
                                                                              'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_recreate_api_token_for_valid_token_should_succeed_return_new_token(self, mocker,
                                                                                    dataverse_client_mock: dataverse_client_mock):
    mocked_new_token_result = {'status': 200, 'reason': 'OK',
                               'result': {'status': 'OK',
                                          'data': {'message': 'New token for dataverseAdmin is new_token'}}}
    result_future = Future()
    result_future.set_result(mocked_new_token_result)
    mocker.patch.object(dataverse_client_mock.http_client, 'post', return_value=result_future)
    assert "new_token" == await dataverse_client_mock.recreate_api_token(), "Must return new token"
    dataverse_client_mock.logger.info.assert_called_once_with("Recreate token, Server: %s",
                                                              dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.post.assert_called_once_with(
      f"{dataverse_client_mock.server_url}/api/users/token/recreate",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token}, )

  @pytest.mark.asyncio
  async def test_recreate_api_token_for_invalid_token_should_succeed_return_error(self, mocker,
                                                                                  dataverse_client_mock: dataverse_client_mock):
    mocked_fail_result = {'status': 401, 'reason': 'Unauthorized',
                          'result': {'status': 'ERROR', 'message': 'Bad API key'}}
    result_future = Future()
    result_future.set_result(mocked_fail_result)
    mocker.patch.object(dataverse_client_mock.http_client, 'post', return_value=result_future)
    assert (
        "Error recreating the token, Server: test_url, Reason: Unauthorized, Info: {'status': 'ERROR', 'message': 'Bad API key'}" == await dataverse_client_mock.recreate_api_token()), "Must return new token"
    dataverse_client_mock.logger.info.assert_called_once_with("Recreate token, Server: %s",
                                                              dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.post.assert_called_once_with(
      f"{dataverse_client_mock.server_url}/api/users/token/recreate",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token}, )
    dataverse_client_mock.logger.error.assert_called_once_with(
      "Error recreating the token, Server: test_url, Reason: Unauthorized, "
      "Info: {'status': 'ERROR', 'message': 'Bad API key'}")

  @pytest.mark.asyncio
  async def test_recreate_api_token_when_request_fails_returns_error(self, mocker,
                                                                     dataverse_client_mock: dataverse_client_mock):
    future = Future()
    future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'post', side_effect=[future])
    dataverse_client_mock.http_client.session_request_errors = [
      "ClientConnectorError for url (url) with error: Cannot connect to host localhost:8080 ssl:default [Connect call failed ('127.0.0.1', 8080)]"]
    result = await dataverse_client_mock.recreate_api_token()
    assert result == dataverse_client_mock.http_client.session_request_errors, "Not expected result!"
    dataverse_client_mock.logger.info.assert_called_with("Recreate token, Server: %s", dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.post.assert_called_with(
      f"{dataverse_client_mock.server_url}/api/users/token/recreate",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_data_verse_creation_publish_when_succeeds_returns_expected1(self, mocker,
                                                                             dataverse_client_mock: dataverse_client_mock):
    dataverse_client = DataverseClient("http://localhost:8080", "a663931d-a8f9-467c-9fcf-fcf9523b7fa0")
    result = await dataverse_client.create_and_publish_dataverse(":root", dv_name="DataverseInstitute1234",
                                                                 dv_description="Rest", dv_alias="§§1234",
                                                                 dv_contact_email_list=[
                                                                   {"contactEmail": "pi@example.edu"}],
                                                                 dv_affiliation="Scientific Research University",
                                                                 dv_type="RESEARCH_PROJECTS")
    assert result is not None, "Dataverse not created!"
    pass

  @pytest.mark.asyncio
  async def test_data_verse_creation_publish_when_succeeds_returns_expected(self, mocker,
                                                                            dataverse_client_mock: dataverse_client_mock):
    test_name = "test_name"
    test_alias_name = "test_alias_name"
    mock_create_dataverse_response = {'status': 201, 'reason': 'Created', 'result': {'status': 'OK',
                                                                                     'data': {'id': 2107245,
                                                                                              'alias': test_alias_name,
                                                                                              'name': test_name,
                                                                                              'affiliation': 'Scientific Research University',
                                                                                              'dataverseContacts': [
                                                                                                {'displayOrder': 0,
                                                                                                 'contactEmail': 'pi@example.edu'}],
                                                                                              'permissionRoot': True,
                                                                                              'description': 'Rest',
                                                                                              'dataverseType': 'RESEARCH_PROJECTS',
                                                                                              'ownerId': 1,
                                                                                              'creationDate': '2023-11-13T11:57:44Z'}}}

    mock_publish_dataverse_response = {'status': 200, 'reason': 'OK', 'result': {'status': 'OK',
                                                                                 'data': {'id': 2107245,
                                                                                          'alias': test_alias_name,
                                                                                          'name': test_name,
                                                                                          'affiliation': 'Scientific Research University',
                                                                                          'dataverseContacts': [
                                                                                            {'displayOrder': 0,
                                                                                             'contactEmail': 'pi@example.edu'}],
                                                                                          'permissionRoot': True,
                                                                                          'description': 'Rest',
                                                                                          'dataverseType': 'RESEARCH_PROJECTS',
                                                                                          'ownerId': 1,
                                                                                          'creationDate': '2023-11-13T11:57:44Z'}}}
    metadata = {"name": "test_name", "alias": "test_alias_name",
                "dataverseContacts": [{"contactEmail": "pi@example.edu"}],
                "affiliation": "Scientific Research University",
                "description": "Rest", "dataverseType": "RESEARCH_PROJECTS"}
    metadata_json = dumps(metadata)
    mock_dumps = mocker.patch('pasta_eln.dataverse.client.dumps', return_value=metadata_json)
    create_future = Future()
    create_future.set_result(mock_create_dataverse_response)
    publish_future = Future()
    publish_future.set_result(mock_publish_dataverse_response)
    mocker.patch.object(dataverse_client_mock.http_client, 'post', side_effect=[create_future, publish_future])

    result = await dataverse_client_mock.create_and_publish_dataverse(dv_parent=":root", dv_name=test_name,
                                                                      dv_description="Rest", dv_alias=test_alias_name,
                                                                      dv_contact_email_list=[
                                                                        {"contactEmail": "pi@example.edu"}],
                                                                      dv_affiliation="Scientific Research University",
                                                                      dv_type="RESEARCH_PROJECTS")
    assert result["name"] == test_name
    assert result["alias"] == test_alias_name
    assert result["dataverseType"] == "RESEARCH_PROJECTS"
    assert result["affiliation"] == "Scientific Research University"
    assert result["description"] == "Rest"
    assert result["dataverseContacts"][0]["contactEmail"] == "pi@example.edu"
    assert result["alias"] == test_alias_name
    assert result["id"], "Dataverse id not found"
    assert result["creationDate"], "Dataverse date not found"
    assert result['ownerId'], "Dataverse owner Id not found"
    assert result['permissionRoot'], "Dataverse root permission not found"
    dataverse_client_mock.logger.info.assert_called_once_with('Creating dataverse, Server: %s Alias: %s', 'test_url',
                                                              'test_alias_name')
    dataverse_client_mock.http_client.post.assert_has_calls([
      mocker.call(f"{dataverse_client_mock.server_url}/api/dataverses/:root",
                  request_headers={'Content-Type': 'application/json',
                                   'X-Dataverse-key': dataverse_client_mock.api_token}, data=metadata_json),
      mocker.call(f"{dataverse_client_mock.server_url}/api/dataverses/test_alias_name/actions/:publish",
                  request_headers={'Content-Type': 'application/json',
                                   'X-Dataverse-key': dataverse_client_mock.api_token})])
    mock_dumps.assert_called_once_with(metadata)

  @pytest.mark.parametrize(
    "create_data_verse_response_status, publish_dataverse_response_status, create_result, publish_result, return_value",
    [([404, 'Not Found'], [200, 'OK'], {}, {},
      'Error creating dataverse, Server: test_url, Status: 404, Reason: Not Found, Info: None'), (
         [500, 'Internal Server Error'], [200, 'OK'], {"status": "ERROR", "message": "Invalid alias name.."}, {},
         'Error creating dataverse, Server: test_url, Status: 500, Reason: Internal Server Error, Info: Invalid alias name..'),
     ([201, 'Not Found'], [200, 'OK'], {}, {},
      'Error creating dataverse, Server: test_url, Status: 201, Reason: Not Found, Info: None'), (
         [201, 'Created'], [400, 'Publish failed..'], {'data': {'alias': 'test_alias_name'}},
         {'data': {'alias': 'test_alias_name'}},
         'Error publishing dataverse, Server: test_url, Status: 400, Reason: Publish failed.., Info: None'), ])
  @pytest.mark.asyncio
  async def test_dataverse_create_and_publish_throw_exceptions_return_error(self, mocker,
                                                                            dataverse_client_mock: dataverse_client_mock,
                                                                            create_data_verse_response_status,
                                                                            publish_dataverse_response_status,
                                                                            create_result, publish_result,
                                                                            return_value):
    test_name = "test_name"
    test_alias_name = "test_alias_name"
    mock_create_dataverse_response = {'status': create_data_verse_response_status[0],
                                      'reason': create_data_verse_response_status[1], 'result': create_result}

    mock_publish_dataverse_response = {'status': publish_dataverse_response_status[0],
                                       'reason': publish_dataverse_response_status[1], 'result': publish_result}
    metadata = {"name": "test_name", "alias": "test_alias_name",
                "dataverseContacts": [{"contactEmail": "pi@example.edu"}],
                "affiliation": "Scientific Research University",
                "description": "Rest", "dataverseType": "RESEARCH_PROJECTS"}
    metadata_json = dumps(metadata)
    mock_dumps = mocker.patch('pasta_eln.dataverse.client.dumps', return_value=metadata_json)
    create_future = Future()
    create_future.set_result(mock_create_dataverse_response)
    publish_future = Future()
    publish_future.set_result(mock_publish_dataverse_response)

    mocker.patch.object(dataverse_client_mock.http_client, 'post', side_effect=[create_future, publish_future])
    result = await dataverse_client_mock.create_and_publish_dataverse(dv_parent=":root", dv_name=test_name,
                                                                      dv_description="Rest", dv_alias=test_alias_name,
                                                                      dv_contact_email_list=[
                                                                        {"contactEmail": "pi@example.edu"}],
                                                                      dv_affiliation="Scientific Research University",
                                                                      dv_type="RESEARCH_PROJECTS")
    assert result == return_value
    dataverse_client_mock.logger.info.assert_called_once_with("Creating dataverse, Server: %s Alias: %s",
                                                              dataverse_client_mock.server_url, test_alias_name)
    mock_post_calls = [mocker.call(f"{dataverse_client_mock.server_url}/api/dataverses/:root",
                                   request_headers={'Content-Type': 'application/json',
                                                    'X-Dataverse-key': dataverse_client_mock.api_token},
                                   data=metadata_json),
                       mocker.call(
                         f"{dataverse_client_mock.server_url}/api/dataverses/test_alias_name/actions/:publish",
                         request_headers={'Content-Type': 'application/json',
                                          'X-Dataverse-key': dataverse_client_mock.api_token})] if create_data_verse_response_status == [
      201, 'Created'] else [mocker.call(f"{dataverse_client_mock.server_url}/api/dataverses/:root",
                                        request_headers={'Content-Type': 'application/json',
                                                         'X-Dataverse-key': dataverse_client_mock.api_token},
                                        data=metadata_json)]
    dataverse_client_mock.http_client.post.assert_has_calls(mock_post_calls)
    mock_dumps.assert_called_once_with(metadata)
    dataverse_client_mock.logger.error.assert_called_once_with(result)

  @pytest.mark.asyncio
  async def test_dataverse_create_and_publish_request_failures_should_return_expected_error(self, mocker,
                                                                                            dataverse_client_mock: dataverse_client_mock):
    test_name = "test_name"
    test_alias_name = "test_alias_name"
    metadata = {"name": "test_name", "alias": "test_alias_name",
                "dataverseContacts": [{"contactEmail": "pi@example.edu"}],
                "affiliation": "Scientific Research University",
                "description": "Rest", "dataverseType": "RESEARCH_PROJECTS"}
    metadata_json = dumps(metadata)
    mock_dumps = mocker.patch('pasta_eln.dataverse.client.dumps', return_value=metadata_json)

    dataverse_client_mock.http_client.session_request_errors = [
      "ClientConnectorError for url (url) with error: Cannot connect to host localhost:8080 ssl:default [Connect call failed ('127.0.0.1', 8080)]"]

    upload_future = Future()
    upload_future.set_result({})
    publish_future = Future()
    publish_future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'post', side_effect=[upload_future, publish_future])
    result = await dataverse_client_mock.create_and_publish_dataverse(dv_parent=":root", dv_name=test_name,
                                                                      dv_description="Rest", dv_alias=test_alias_name,
                                                                      dv_contact_email_list=[
                                                                        {"contactEmail": "pi@example.edu"}],
                                                                      dv_affiliation="Scientific Research University",
                                                                      dv_type="RESEARCH_PROJECTS")
    assert result == dataverse_client_mock.http_client.session_request_errors, "session_request_errors must be returned!"
    dataverse_client_mock.http_client.post.assert_has_calls([
      mocker.call(f"{dataverse_client_mock.server_url}/api/dataverses/:root",
                  request_headers={'Content-Type': 'application/json',
                                   'X-Dataverse-key': dataverse_client_mock.api_token},
                  data=metadata_json)])

    upload_future = Future()
    upload_future.set_result({"status": 201, "reason": "Created", "result": {"data": {"alias": test_alias_name}}})
    publish_future = Future()
    publish_future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'post', side_effect=[upload_future, publish_future])
    result = await dataverse_client_mock.create_and_publish_dataverse(dv_parent=":root", dv_name=test_name,
                                                                      dv_description="Rest", dv_alias=test_alias_name,
                                                                      dv_contact_email_list=[
                                                                        {"contactEmail": "pi@example.edu"}],
                                                                      dv_affiliation="Scientific Research University",
                                                                      dv_type="RESEARCH_PROJECTS")
    assert result == dataverse_client_mock.http_client.session_request_errors, "session_request_errors must be returned!"
    dataverse_client_mock.http_client.post.assert_has_calls([
      mocker.call(f"{dataverse_client_mock.server_url}/api/dataverses/:root",
                  request_headers={'Content-Type': 'application/json',
                                   'X-Dataverse-key': dataverse_client_mock.api_token},
                  data=metadata_json),
      mocker.call(f"{dataverse_client_mock.server_url}/api/dataverses/{test_alias_name}/actions/:publish",
                  request_headers={'Content-Type': 'application/json',
                                   'X-Dataverse-key': dataverse_client_mock.api_token})])
    mock_dumps.assert_has_calls([mocker.call(metadata), mocker.call(metadata)])

  @pytest.mark.asyncio
  async def test_check_if_dataverse_reachable_when_succeeds_returns_expected(self, mocker,
                                                                             dataverse_client_mock: dataverse_client_mock):
    mock_version_check_response = {'status': 200, 'reason': "OK",
                                   'result': {'data': {'build': '1512-366fd41', 'version': '6.0'}, 'status': 'OK'}}
    version_check_response_future = Future()
    version_check_response_future.set_result(mock_version_check_response)

    mocker.patch.object(dataverse_client_mock.http_client, 'get', return_value=version_check_response_future)

    assert await dataverse_client_mock.check_if_dataverse_server_reachable() == (True, "Dataverse is reachable")
    dataverse_client_mock.logger.info.assert_called_once_with("Check if data-verse is reachable, Server: %s",
                                                              dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_once_with(
      f"{dataverse_client_mock.server_url}/api/info/version",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_check_if_dataverse_reachable_when_fail_return_error(self, mocker,
                                                                     dataverse_client_mock: dataverse_client_mock):
    mock_version_check_response = {'status': 404, 'reason': "Not found",
                                   'result': {'message': "Error!!", 'status': 'ERROR'}}
    version_check_response_future = Future()
    version_check_response_future.set_result(mock_version_check_response)

    mocker.patch.object(dataverse_client_mock.http_client, 'get', return_value=version_check_response_future)
    assert await dataverse_client_mock.check_if_dataverse_server_reachable() == (False,
                                                                                 f"Dataverse isn't reachable, Server: {dataverse_client_mock.server_url}, Status: 404, Reason: Not found, Info: Error!!")
    dataverse_client_mock.logger.info.assert_called_once_with("Check if data-verse is reachable, Server: %s",
                                                              dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_once_with(
      f"{dataverse_client_mock.server_url}/api/info/version",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_check_if_dataverse_reachable_when_fail_return_error_html(self, mocker,
                                                                          dataverse_client_mock: dataverse_client_mock):
    mock_version_check_response = {'status': 404, 'reason': "Not found", 'result': "<html><body>Error!!</body></html>"}
    version_check_response_future = Future()
    version_check_response_future.set_result(mock_version_check_response)

    mocker.patch.object(dataverse_client_mock.http_client, 'get', return_value=version_check_response_future)
    assert await dataverse_client_mock.check_if_dataverse_server_reachable() == (False,
                                                                                 f"Dataverse isn't reachable, Server: {dataverse_client_mock.server_url}, Status: 404, Reason: Not found, Info: <html><body>Error!!</body></html>")
    dataverse_client_mock.logger.info.assert_called_once_with("Check if data-verse is reachable, Server: %s",
                                                              dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_once_with(
      f"{dataverse_client_mock.server_url}/api/info/version",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.parametrize("exception, error_message", [(ConnectionError(
    "ERROR: POST - Could not establish connection to API: https://demo.dataverse.or/api/v1/dataverses/:root"),
                                                         "ERROR: POST - Could not establish connection to API: https://demo.dataverse.or/api/v1/dataverses/:root"),
    (InvalidURL("Invalid URL 'https:///api/v1/dataverses/:root': No host supplied"),
     "Invalid URL 'https:///api/v1/dataverses/:root': No host supplied"), (
        MissingSchema("No connection adapters were found for 'None/dataverses/:root'"),
        "No connection adapters were found for 'None/dataverses/:root'")])
  @pytest.mark.asyncio
  async def test_check_if_dataverse_reachable_throw_exceptions_return_error(self, mocker,
                                                                            dataverse_client_mock: dataverse_client_mock,
                                                                            exception, error_message):
    # Arrange
    mock_client_session_get_info_response = mocker.patch.object(dataverse_client_mock.http_client, 'get',
                                                                side_effect=exception)
    # Act and asserts
    assert await dataverse_client_mock.check_if_dataverse_server_reachable() == (False, error_message)
    mock_client_session_get_info_response.assert_called_once()
    dataverse_client_mock.logger.info.assert_called_once_with("Check if data-verse is reachable, Server: %s",
                                                              dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_once_with(
      f"{dataverse_client_mock.server_url}/api/info/version",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_check_if_dataverse_reachable_when_request_fails_returns_error(self, mocker,
                                                                               dataverse_client_mock: dataverse_client_mock):
    future = Future()
    future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'get', side_effect=[future])
    dataverse_client_mock.http_client.session_request_errors = [
      "ClientConnectorError for url (url) with error: Cannot connect to host localhost:8080 ssl:default [Connect call failed ('127.0.0.1', 8080)]"]
    result = await dataverse_client_mock.check_if_dataverse_server_reachable()
    assert result == (False, dataverse_client_mock.http_client.session_request_errors), "Not expected result!"
    dataverse_client_mock.logger.info.assert_called_with("Check if data-verse is reachable, Server: %s",
                                                         dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_with(f"{dataverse_client_mock.server_url}/api/info/version",
                                                             request_headers={'Accept': 'application/json',
                                                                              'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_get_dataverse_list_when_success_returns_dataverse_list(self, mocker,
                                                                        dataverse_client_mock: dataverse_client_mock,
                                                                        dataverse_tree_mock: dataverse_tree_mock,
                                                                        dataverse_list_mock: dataverse_list_mock):
    basic_auth = mocker.MagicMock()
    mock_basic_auth = mocker.patch('pasta_eln.dataverse.client.BasicAuth', return_value=basic_auth)
    mock_service_document = {'status': 200, 'reason': 'OK', 'result': 'xml_text'}

    mock_from_string = mocker.patch('pasta_eln.dataverse.client.fromstring', return_value=dataverse_tree_mock)
    mock_element_tree = mocker.patch('pasta_eln.dataverse.client.ElementTree', return_value=dataverse_tree_mock)
    service_doc_response_future = Future()
    service_doc_response_future.set_result(mock_service_document)
    mocker.patch.object(dataverse_client_mock.http_client, 'get', return_value=service_doc_response_future)
    result = await dataverse_client_mock.get_dataverse_list()
    dataverse_client_mock.logger.info.assert_called_once_with('Getting dataverse list for server: %s',
                                                              dataverse_client_mock.server_url)
    assert len(result) == 115, "Result list count is not 115"
    dataverse_client_mock.http_client.get.assert_called_once_with(
      f'{dataverse_client_mock.server_url}/dvn/api/data-deposit/v1.1/swordv2/service-document',
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token},
      auth=mock_basic_auth.return_value)
    mock_basic_auth.assert_called_once_with(dataverse_client_mock.api_token, '')
    assert result == dataverse_list_mock, "Result list is not equal to dataverse_list_mock"
    mock_from_string.assert_called_once_with("xml_text")
    mock_element_tree.assert_called_once_with(dataverse_tree_mock)
    mock_basic_auth.assert_called_once_with(dataverse_client_mock.api_token, '')

  @pytest.mark.asyncio
  async def test_get_dataverse_list_when_fails_returns_error(self, mocker,
                                                             dataverse_client_mock: dataverse_client_mock):
    basic_auth = mocker.MagicMock()
    mock_basic_auth = mocker.patch('pasta_eln.dataverse.client.BasicAuth', return_value=basic_auth)
    service_doc_response_future = Future()
    service_doc_response_future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'get', return_value=service_doc_response_future)
    dataverse_client_mock.http_client.session_request_errors = [
      "ClientConnectorError for url (http://localhost:8080/dvn/api/data-deposit/v1.1/swordv2/service-document) with error: Cannot connect to host localhost:8080 ssl:default [Connect call failed ('127.0.0.1', 8080)]"]

    result = await dataverse_client_mock.get_dataverse_list()
    dataverse_client_mock.logger.info.assert_called_once_with('Getting dataverse list for server: %s',
                                                              dataverse_client_mock.server_url)
    assert result == dataverse_client_mock.http_client.session_request_errors, "Result should be session_request_errors"
    dataverse_client_mock.http_client.get.assert_called_once_with(
      f'{dataverse_client_mock.server_url}/dvn/api/data-deposit/v1.1/swordv2/service-document',
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token},
      auth=mock_basic_auth.return_value)
    mock_basic_auth.assert_called_once_with(dataverse_client_mock.api_token, '')

  @pytest.mark.asyncio
  async def test_get_dataverse_list_when_returns_error_status_must_returns_error(self, mocker,
                                                                                 dataverse_client_mock: dataverse_client_mock):
    basic_auth = mocker.MagicMock()
    mock_basic_auth = mocker.patch('pasta_eln.dataverse.client.BasicAuth', return_value=basic_auth)
    mock_service_document = {'status': 404, 'reason': 'Error', 'result': 'Failed!'}
    service_doc_response_future = Future()
    service_doc_response_future.set_result(mock_service_document)
    mocker.patch.object(dataverse_client_mock.http_client, 'get', return_value=service_doc_response_future)

    result = await dataverse_client_mock.get_dataverse_list()
    dataverse_client_mock.logger.info.assert_called_once_with('Getting dataverse list for server: %s',
                                                              dataverse_client_mock.server_url)
    assert result == 'Error getting dataverse list, Server: test_url, Status: 404, Reason: Error, Info: Failed!', "Result should be session_request_errors"
    dataverse_client_mock.http_client.get.assert_called_once_with(
      f'{dataverse_client_mock.server_url}/dvn/api/data-deposit/v1.1/swordv2/service-document',
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token},
      auth=mock_basic_auth.return_value)
    mock_basic_auth.assert_called_once_with(dataverse_client_mock.api_token, '')

  @pytest.mark.asyncio
  async def test_get_dataverse_list_when_request_fails_returns_error(self, mocker,
                                                                     dataverse_client_mock: dataverse_client_mock):
    future = Future()
    future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'get', side_effect=[future])
    basic_auth = mocker.MagicMock()
    mock_basic_auth = mocker.patch('pasta_eln.dataverse.client.BasicAuth', return_value=basic_auth)
    dataverse_client_mock.http_client.session_request_errors = [
      "ClientConnectorError for url (url) with error: Cannot connect to host localhost:8080 ssl:default [Connect call failed ('127.0.0.1', 8080)]"]
    result = await dataverse_client_mock.get_dataverse_list()
    assert result == dataverse_client_mock.http_client.session_request_errors, "Not expected result!"
    dataverse_client_mock.logger.info.assert_called_with("Getting dataverse list for server: %s",
                                                         dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_with(
      f"{dataverse_client_mock.server_url}/dvn/api/data-deposit/v1.1/swordv2/service-document",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token},
      auth=basic_auth)
    mock_basic_auth.assert_called_once_with(dataverse_client_mock.api_token, '')

  @pytest.mark.asyncio
  async def test_get_dataverse_contents_for_valid_id_must_returns_valid_content(self, mocker,
                                                                                dataverse_client_mock: dataverse_client_mock):
    dataverse_content = {'status': 200, 'reason': 'OK', 'result': {'status': 'OK',
                                                                   'data': [{'type': 'dataverse', 'id': 95,
                                                                             'title': 'Dataverse Admin Dataverse'},
                                                                            {'id': 44, 'identifier': 'FK2/3BQJ5B',
                                                                             'persistentUrl': 'https://doi.org/10.5072/FK2/3BQJ5B',
                                                                             'protocol': 'doi', 'authority': '10.5072',
                                                                             'publisher': 'Root',
                                                                             'publicationDate': '2023-11-29',
                                                                             'storageIdentifier': 'local://10.5072/FK2/3BQJ5B',
                                                                             'type': 'dataset'},
                                                                            {'id': 45, 'identifier': 'FK2/6E9KJQ',
                                                                             'persistentUrl': 'https://doi.org/10.5072/FK2/6E9KJQ',
                                                                             'protocol': 'doi', 'authority': '10.5072',
                                                                             'publisher': 'Root',
                                                                             'publicationDate': '2023-11-29',
                                                                             'storageIdentifier': 'local://10.5072/FK2/6E9KJQ',
                                                                             'type': 'dataset'},
                                                                            {'id': 58, 'identifier': 'FK2/RN7AIV',
                                                                             'persistentUrl': 'https://doi.org/10.5072/FK2/RN7AIV',
                                                                             'protocol': 'doi', 'authority': '10.5072',
                                                                             'publisher': 'Root',
                                                                             'storageIdentifier': 'local://10.5072/FK2/RN7AIV',
                                                                             'type': 'dataset'},
                                                                            {'id': 64, 'identifier': 'FK2/P9JWB4',
                                                                             'persistentUrl': 'https://doi.org/10.5072/FK2/P9JWB4',
                                                                             'protocol': 'doi', 'authority': '10.5072',
                                                                             'publisher': 'Root',
                                                                             'storageIdentifier': 'local://10.5072/FK2/P9JWB4',
                                                                             'type': 'dataset'},
                                                                            {'id': 65, 'identifier': 'FK2/PI1EPG',
                                                                             'persistentUrl': 'https://doi.org/10.5072/FK2/PI1EPG',
                                                                             'protocol': 'doi', 'authority': '10.5072',
                                                                             'publisher': 'Root',
                                                                             'storageIdentifier': 'local://10.5072/FK2/PI1EPG',
                                                                             'type': 'dataset'},
                                                                            {'id': 66, 'identifier': 'FK2/QJQ4YY',
                                                                             'persistentUrl': 'https://doi.org/10.5072/FK2/QJQ4YY',
                                                                             'protocol': 'doi', 'authority': '10.5072',
                                                                             'publisher': 'Root',
                                                                             'storageIdentifier': 'local://10.5072/FK2/QJQ4YY',
                                                                             'type': 'dataset'},
                                                                            {'id': 67, 'identifier': 'FK2/VCADSB',
                                                                             'persistentUrl': 'https://doi.org/10.5072/FK2/VCADSB',
                                                                             'protocol': 'doi', 'authority': '10.5072',
                                                                             'publisher': 'Root',
                                                                             'storageIdentifier': 'local://10.5072/FK2/VCADSB',
                                                                             'type': 'dataset'},
                                                                            {'id': 68, 'identifier': 'FK2/ZWOINS',
                                                                             'persistentUrl': 'https://doi.org/10.5072/FK2/ZWOINS',
                                                                             'protocol': 'doi', 'authority': '10.5072',
                                                                             'publisher': 'Root',
                                                                             'storageIdentifier': 'local://10.5072/FK2/ZWOINS',
                                                                             'type': 'dataset'},
                                                                            {'id': 69, 'identifier': 'FK2/JRRO5W',
                                                                             'persistentUrl': 'https://doi.org/10.5072/FK2/JRRO5W',
                                                                             'protocol': 'doi', 'authority': '10.5072',
                                                                             'publisher': 'Root',
                                                                             'publicationDate': '2023-12-05',
                                                                             'storageIdentifier': 'local://10.5072/FK2/JRRO5W',
                                                                             'type': 'dataset'},
                                                                            {'id': 70, 'identifier': 'FK2/AMYNKF',
                                                                             'persistentUrl': 'https://doi.org/10.5072/FK2/AMYNKF',
                                                                             'protocol': 'doi', 'authority': '10.5072',
                                                                             'publisher': 'Root',
                                                                             'publicationDate': '2023-12-01',
                                                                             'storageIdentifier': 'local://10.5072/FK2/AMYNKF',
                                                                             'type': 'dataset'},
                                                                            {'id': 71, 'identifier': 'FK2/S5X6JS',
                                                                             'persistentUrl': 'https://doi.org/10.5072/FK2/S5X6JS',
                                                                             'protocol': 'doi', 'authority': '10.5072',
                                                                             'publisher': 'Root',
                                                                             'publicationDate': '2023-12-01',
                                                                             'storageIdentifier': 'local://10.5072/FK2/S5X6JS',
                                                                             'type': 'dataset'},
                                                                            {'id': 72, 'identifier': 'FK2/LJQT5M',
                                                                             'persistentUrl': 'https://doi.org/10.5072/FK2/LJQT5M',
                                                                             'protocol': 'doi', 'authority': '10.5072',
                                                                             'publisher': 'Root',
                                                                             'storageIdentifier': 'local://10.5072/FK2/LJQT5M',
                                                                             'type': 'dataset'},
                                                                            {'id': 73, 'identifier': 'FK2/SD5OT9',
                                                                             'persistentUrl': 'https://doi.org/10.5072/FK2/SD5OT9',
                                                                             'protocol': 'doi', 'authority': '10.5072',
                                                                             'publisher': 'Root',
                                                                             'publicationDate': '2023-12-01',
                                                                             'storageIdentifier': 'local://10.5072/FK2/SD5OT9',
                                                                             'type': 'dataset'},
                                                                            {'id': 74, 'identifier': 'FK2/3N5ALJ',
                                                                             'persistentUrl': 'https://doi.org/10.5072/FK2/3N5ALJ',
                                                                             'protocol': 'doi', 'authority': '10.5072',
                                                                             'publisher': 'Root',
                                                                             'publicationDate': '2023-12-01',
                                                                             'storageIdentifier': 'local://10.5072/FK2/3N5ALJ',
                                                                             'type': 'dataset'}]}}
    dataverse_content_future = Future()
    dataverse_content_future.set_result(dataverse_content)
    mocker.patch.object(dataverse_client_mock.http_client, 'get', return_value=dataverse_content_future)

    result = await dataverse_client_mock.get_dataverse_contents("valid_id")
    dataverse_client_mock.logger.info.assert_called_once_with(
      "Retrieving dataverse contents, Server: %s, Dataverse identifier: %s", dataverse_client_mock.server_url,
      "valid_id")
    assert result == dataverse_content.get("result").get("data"), "Expected result should be returned!"
    dataverse_client_mock.http_client.get.assert_called_once_with(
      f"{dataverse_client_mock.server_url}/api/dataverses/valid_id/contents",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_get_dataverse_contents_for_unknown_id_must_returns_error(self, mocker,
                                                                          dataverse_client_mock: dataverse_client_mock):
    dataverse_content = {'status': 404, 'reason': 'Not Found',
                         'result': {'status': 'ERROR', 'message': "Can't find dataverse with identifier='unknown'"}}
    dataverse_content_future = Future()
    dataverse_content_future.set_result(dataverse_content)
    mocker.patch.object(dataverse_client_mock.http_client, 'get', return_value=dataverse_content_future)

    result = await dataverse_client_mock.get_dataverse_contents("unknown")
    dataverse_client_mock.logger.info.assert_called_once_with(
      "Retrieving dataverse contents, Server: %s, Dataverse identifier: %s", dataverse_client_mock.server_url,
      "unknown")
    assert result == "Error retrieving the contents for data verse, Id: unknown, Reason: Not Found, Info: {'status': 'ERROR', 'message': \"Can't find dataverse with identifier='unknown'\"}", "Result should be expected error"
    dataverse_client_mock.http_client.get.assert_called_once_with(
      f"{dataverse_client_mock.server_url}/api/dataverses/unknown/contents",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})
    dataverse_client_mock.logger.error.assert_called_once_with(
      "Error retrieving the contents for data verse, Id: unknown, Reason: Not Found, Info: {'status': 'ERROR', 'message': \"Can't find dataverse with identifier='unknown'\"}")

  @pytest.mark.asyncio
  async def test_get_dataverse_contents_when_request_throws_exception_returns_error(self, mocker,
                                                                                    dataverse_client_mock: dataverse_client_mock):
    service_doc_response_future = Future()
    service_doc_response_future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'get', return_value=service_doc_response_future)
    dataverse_client_mock.http_client.session_request_errors = [
      "ClientConnectorError for url (url) with error: Cannot connect to host localhost:8080 ssl:default [Connect call failed ('127.0.0.1', 8080)]"]

    result = await dataverse_client_mock.get_dataverse_contents("valid_id")
    dataverse_client_mock.logger.info.assert_called_once_with(
      "Retrieving dataverse contents, Server: %s, Dataverse identifier: %s", dataverse_client_mock.server_url,
      "valid_id")
    assert result == dataverse_client_mock.http_client.session_request_errors, "Result should be session_request_errors"
    dataverse_client_mock.http_client.get.assert_called_once_with(
      f"{dataverse_client_mock.server_url}/api/dataverses/valid_id/contents",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_get_dataverse_size_for_valid_id_must_returns_valid_content(self, mocker,
                                                                            dataverse_client_mock: dataverse_client_mock):
    dataverse_size = {'status': 200, 'reason': 'OK', 'result': {'status': 'OK',
                                                                'data': {
                                                                  'message': 'Total size of the files stored in this dataverse: 720,190,291 bytes'}}}
    dataverse_content_future = Future()
    dataverse_content_future.set_result(dataverse_size)
    mocker.patch.object(dataverse_client_mock.http_client, 'get', return_value=dataverse_content_future)

    result = await dataverse_client_mock.get_dataverse_size("valid_id")
    dataverse_client_mock.logger.info.assert_called_once_with(
      "Retrieving dataverse size, Server: %s, Dataverse identifier: %s", dataverse_client_mock.server_url, "valid_id")
    assert result == "720,190,291 bytes", f"Expected result should be returned!"
    dataverse_client_mock.http_client.get.assert_called_once_with(
      f"{dataverse_client_mock.server_url}/api/dataverses/valid_id/storagesize",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_get_dataverse_size_for_unknown_id_must_returns_error(self, mocker,
                                                                      dataverse_client_mock: dataverse_client_mock):
    dataverse_size = {'status': 404, 'reason': 'Not Found',
                      'result': {'status': 'ERROR', 'message': "Can't find dataverse with identifier='unknown'"}}
    dataverse_content_future = Future()
    dataverse_content_future.set_result(dataverse_size)
    mocker.patch.object(dataverse_client_mock.http_client, 'get', return_value=dataverse_content_future)

    result = await dataverse_client_mock.get_dataverse_size("unknown")
    dataverse_client_mock.logger.info.assert_called_once_with(
      "Retrieving dataverse size, Server: %s, Dataverse identifier: %s", dataverse_client_mock.server_url, "unknown")
    assert result == "Error retrieving the size for data verse, Id: unknown, Reason: Not Found, Info: {'status': 'ERROR', 'message': \"Can't find dataverse with identifier='unknown'\"}", "Result should be expected error"
    dataverse_client_mock.http_client.get.assert_called_once_with(
      f"{dataverse_client_mock.server_url}/api/dataverses/unknown/storagesize",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})
    dataverse_client_mock.logger.error.assert_called_once_with(
      "Error retrieving the size for data verse, Id: unknown, Reason: Not Found, Info: {'status': 'ERROR', 'message': \"Can't find dataverse with identifier='unknown'\"}")

  @pytest.mark.asyncio
  async def test_get_dataverse_size_when_request_throws_exception_returns_error(self, mocker,
                                                                                dataverse_client_mock: dataverse_client_mock):
    service_doc_response_future = Future()
    service_doc_response_future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'get', return_value=service_doc_response_future)
    dataverse_client_mock.http_client.session_request_errors = [
      "ClientConnectorError for url (url) with error: Cannot connect to host localhost:8080 ssl:default [Connect call failed ('127.0.0.1', 8080)]"]

    result = await dataverse_client_mock.get_dataverse_size("valid_id")
    dataverse_client_mock.logger.info.assert_called_once_with(
      "Retrieving dataverse size, Server: %s, Dataverse identifier: %s", dataverse_client_mock.server_url, "valid_id")
    assert result == dataverse_client_mock.http_client.session_request_errors, "Result should be session_request_errors"
    dataverse_client_mock.http_client.get.assert_called_once_with(
      f"{dataverse_client_mock.server_url}/api/dataverses/valid_id/storagesize",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_create_dataset_succeed_should_return_expected_result(self, mocker,
                                                                      dataverse_client_mock: dataverse_client_mock):
    dataset_create_response = {"status": 201, "reason": "Created",
                               "result": {"status": "OK",
                                          "data": {"id": 105, "persistentId": "doi:10.5072/FK2/KTE31V"}}}
    dataset_publish_response = {"status": 200, "reason": "OK", "result": {"status": "OK",
                                                                          "data": {"id": 105,
                                                                                   "identifier": "FK2/KTE31V",
                                                                                   "persistentUrl": "https://doi.org/10.5072/FK2/KTE31V",
                                                                                   "protocol": "doi",
                                                                                   "authority": "10.5072",
                                                                                   "publisher": "Root",
                                                                                   "storageIdentifier": "local://10.5072/FK2/KTE31V"}}}

    create_future = Future()
    create_future.set_result(dataset_create_response)
    publish_future = Future()
    publish_future.set_result(dataset_publish_response)

    mocker.patch.object(dataverse_client_mock.http_client, 'post', side_effect=[create_future, publish_future])

    subjects = ["Engineering", "Chemistry"]
    author = [
      {"authorName": {"typeName": "authorName", "multiple": False, "typeClass": "primitive", "value": "Steven, Jacob"},
       "authorAffiliation": {"typeName": "authorAffiliation", "multiple": False, "typeClass": "primitive",
                             "value": "FZJ"},
       "authorIdentifierScheme": {"typeName": "authorIdentifierScheme", "multiple": False,
                                  "typeClass": "controlledVocabulary", "value": "ORCID"},
       "authorIdentifier": {"typeName": "authorIdentifier", "multiple": False, "typeClass": "primitive",
                            "value": "1234-5678-9012-3456"}}, {
        "authorName": {"typeName": "authorName", "multiple": False, "typeClass": "primitive",
                       "value": "Leslie, Suzanne"},
        "authorAffiliation": {"typeName": "authorAffiliation", "multiple": False, "typeClass": "primitive",
                              "value": "FZJ"},
        "authorIdentifierScheme": {"typeName": "authorIdentifierScheme", "multiple": False,
                                   "typeClass": "controlledVocabulary", "value": "ISNI"},
        "authorIdentifier": {"typeName": "authorIdentifier", "multiple": False, "typeClass": "primitive",
                             "value": "4567-8901-2345-6789"}}]
    dataset_contact = [{
      "datasetContactName": {"typeName": "datasetContactName", "multiple": False, "typeClass": "primitive",
                             "value": "Rashid, Muhammed"},
      "datasetContactAffiliation": {"typeName": "datasetContactAffiliation", "multiple": False,
                                    "typeClass": "primitive", "value": "test Affiliation"},
      "datasetContactEmail": {"typeName": "datasetContactEmail", "multiple": False, "typeClass": "primitive",
                              "value": "test@test.com"}}]
    dataset_description = [{
      "dsDescriptionValue": {"typeName": "dsDescriptionValue", "multiple": False, "typeClass": "primitive",
                             "value": "Description 1"},
      "dsDescriptionDate": {"typeName": "dsDescriptionDate", "multiple": False, "typeClass": "primitive",
                            "value": "2020-11-10"}}, {
      "dsDescriptionValue": {"typeName": "dsDescriptionValue", "multiple": False, "typeClass": "primitive",
                             "value": "Description 2"},
      "dsDescriptionDate": {"typeName": "dsDescriptionDate", "multiple": False, "typeClass": "primitive",
                            "value": "201-12-25"}}]
    metadata = {"title": "Test Data Set", "subject": subjects, "author": author, "datasetContact": dataset_contact,
                "dsDescription": dataset_description,
                "license": {"name": "CC0 1.0", "uri": "http://creativecommons.org/publicdomain/zero/1.0"},
                "language": ["English", "German"], "astroType": ["Mosaic"], "astroFacility": ["AIK-2", "AIK-3"],
                "otherReferences": ["Ref1", "Ref2", "Ref3"], "geographicCoverage": [
        {"country": {"typeName": "country", "multiple": False, "typeClass": "controlledVocabulary", "value": "Albania"},
         "state": {"typeName": "state", "multiple": False, "typeClass": "primitive", "value": "AlbaniaState"},
         "city": {"typeName": "city", "multiple": False, "typeClass": "primitive", "value": "AlbaniaCity"},
         "otherGeographicCoverage": {"typeName": "otherGeographicCoverage", "multiple": False,
                                     "typeClass": "primitive", "value": "CoverageOther"}}],
                "studyDesignType": ["Case Control", "Cross Sectional"],
                "studyAssayOrganism": ["Arabidopsis thaliana", "Bos taurus", "Zea mays"], "journalVolumeIssue": [{
        "journalVolume": {"typeName": "journalVolume", "multiple": False, "typeClass": "primitive",
                          "value": "2333.444"},
        "journalIssue": {"typeName": "journalIssue", "multiple": False, "typeClass": "primitive",
                         "value": "Journal3.4"},
        "journalPubDate": {"typeName": "journalPubDate", "multiple": False, "typeClass": "primitive",
                           "value": "2021-10-10"}}], "researchInstrument": "Instruments1",
                "studyAssayCellType": ["CellType1", "CellType2"]}

    restructured_metadata = {
      "datasetVersion": {
        "license": {
          "name": "CC0 1.0",
          "uri": "http://creativecommons.org/publicdomain/zero/1.0"
        },
        "metadataBlocks": {
          "citation": {
            "fields": [
              {
                "typeName": "title",
                "multiple": False,
                "typeClass": "primitive",
                "value": "Test Data Set"
              },
              {
                "typeName": "author",
                "multiple": True,
                "typeClass": "compound",
                "value": [
                  {
                    "authorName": {
                      "typeName": "authorName",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "Steven, Jacob"
                    },
                    "authorAffiliation": {
                      "typeName": "authorAffiliation",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "FZJ"
                    },
                    "authorIdentifierScheme": {
                      "typeName": "authorIdentifierScheme",
                      "multiple": False,
                      "typeClass": "controlledVocabulary",
                      "value": "ORCID"
                    },
                    "authorIdentifier": {
                      "typeName": "authorIdentifier",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "1234-5678-9012-3456"
                    }
                  },
                  {
                    "authorName": {
                      "typeName": "authorName",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "Leslie, Suzanne"
                    },
                    "authorAffiliation": {
                      "typeName": "authorAffiliation",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "FZJ"
                    },
                    "authorIdentifierScheme": {
                      "typeName": "authorIdentifierScheme",
                      "multiple": False,
                      "typeClass": "controlledVocabulary",
                      "value": "ISNI"
                    },
                    "authorIdentifier": {
                      "typeName": "authorIdentifier",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "4567-8901-2345-6789"
                    }
                  }
                ]
              },
              {
                "typeName": "datasetContact",
                "multiple": True,
                "typeClass": "compound",
                "value": [
                  {
                    "datasetContactName": {
                      "typeName": "datasetContactName",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "Rashid, Muhammed"
                    },
                    "datasetContactAffiliation": {
                      "typeName": "datasetContactAffiliation",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "test Affiliation"
                    },
                    "datasetContactEmail": {
                      "typeName": "datasetContactEmail",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "test@test.com"
                    }
                  }
                ]
              },
              {
                "typeName": "dsDescription",
                "multiple": True,
                "typeClass": "compound",
                "value": [
                  {
                    "dsDescriptionValue": {
                      "typeName": "dsDescriptionValue",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "Description 1"
                    },
                    "dsDescriptionDate": {
                      "typeName": "dsDescriptionDate",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "2020-11-10"
                    }
                  },
                  {
                    "dsDescriptionValue": {
                      "typeName": "dsDescriptionValue",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "Description 2"
                    },
                    "dsDescriptionDate": {
                      "typeName": "dsDescriptionDate",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "201-12-25"
                    }
                  }
                ]
              },
              {
                "typeName": "subject",
                "multiple": True,
                "typeClass": "controlledVocabulary",
                "value": [
                  "Engineering",
                  "Chemistry"
                ]
              },
              {
                "typeName": "language",
                "multiple": True,
                "typeClass": "controlledVocabulary",
                "value": [
                  "English",
                  "German"
                ]
              },
              {
                "typeName": "otherReferences",
                "multiple": True,
                "typeClass": "primitive",
                "value": [
                  "Ref1",
                  "Ref2",
                  "Ref3"
                ]
              }
            ]
          },
          "geospatial": {
            "fields": [
              {
                "typeName": "geographicCoverage",
                "multiple": True,
                "typeClass": "compound",
                "value": [
                  {
                    "country": {
                      "typeName": "country",
                      "multiple": False,
                      "typeClass": "controlledVocabulary",
                      "value": "Albania"
                    },
                    "state": {
                      "typeName": "state",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "AlbaniaState"
                    },
                    "city": {
                      "typeName": "city",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "AlbaniaCity"
                    },
                    "otherGeographicCoverage": {
                      "typeName": "otherGeographicCoverage",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "CoverageOther"
                    }
                  }
                ]
              }
            ]
          },
          "socialscience": {
            "fields": [
              {
                "typeName": "researchInstrument",
                "multiple": False,
                "typeClass": "primitive",
                "value": "Instruments1"
              }
            ]
          },
          "astrophysics": {
            "fields": [
              {
                "typeName": "astroType",
                "multiple": True,
                "typeClass": "controlledVocabulary",
                "value": [
                  "Mosaic"
                ]
              },
              {
                "typeName": "astroFacility",
                "multiple": True,
                "typeClass": "primitive",
                "value": [
                  "AIK-2",
                  "AIK-3"
                ]
              }
            ]
          },
          "biomedical": {
            "fields": [
              {
                "typeName": "studyDesignType",
                "multiple": True,
                "typeClass": "controlledVocabulary",
                "value": [
                  "Case Control",
                  "Cross Sectional"
                ]
              },
              {
                "typeName": "studyAssayOrganism",
                "multiple": True,
                "typeClass": "controlledVocabulary",
                "value": [
                  "Arabidopsis thaliana",
                  "Bos taurus",
                  "Zea mays"
                ]
              },
              {
                "typeName": "studyAssayCellType",
                "multiple": True,
                "typeClass": "primitive",
                "value": [
                  "CellType1",
                  "CellType2"
                ]
              }
            ]
          },
          "journal": {
            "fields": [
              {
                "typeName": "journalVolumeIssue",
                "multiple": True,
                "typeClass": "compound",
                "value": [
                  {
                    "journalVolume": {
                      "typeName": "journalVolume",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "2333.444"
                    },
                    "journalIssue": {
                      "typeName": "journalIssue",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "Journal3.4"
                    },
                    "journalPubDate": {
                      "typeName": "journalPubDate",
                      "multiple": False,
                      "typeClass": "primitive",
                      "value": "2021-10-10"
                    }
                  }
                ]
              }
            ]
          }
        }
      }
    }
    result = await dataverse_client_mock.create_and_publish_dataset("parent_dataverse_id", metadata)
    assert isinstance(result, dict), "Invalid result type, data set creation failed!"
    assert result['id'], "id must exist in result"
    assert result['authority'], "authority must exist in result"
    assert result['identifier'], "identifier must exist in result"
    assert result['persistentUrl'], "persistentUrl must exist in result"
    assert result['protocol'], "protocol must exist in result"
    assert result['publisher'], "publisher must exist in result"
    assert result['storageIdentifier'], "storageIdentifier must exist in result"
    assert result == dataset_publish_response.get("result").get(
      "data"), "result must be equal to mock_publish_result['data']"
    dataverse_client_mock.logger.info.assert_called_once_with("Creating dataset, Alias: %s on server: %s",
                                                              metadata["title"], dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.post.assert_has_calls([
      mocker.call(f"{dataverse_client_mock.server_url}/api/dataverses/parent_dataverse_id/datasets",
                  request_params={'doNotValidate': 'True'},
                  request_headers={'Content-Type': 'application/json',
                                   'X-Dataverse-key': dataverse_client_mock.api_token},
                  json=restructured_metadata),
      mocker.call(f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/actions/:publish",
                  request_params={'persistentId': 'doi:10.5072/FK2/KTE31V', 'type': 'major'},
                  request_headers={'Content-Type': 'application/json',
                                   'X-Dataverse-key': dataverse_client_mock.api_token})])

  @pytest.mark.asyncio
  async def test_create_dataset_json_validation_failure_should_return_error(self, mocker,
                                                                            dataverse_client_mock: dataverse_client_mock):
    validation_error = {"status": 400, "reason": "Bad Request", "result": {"status": "ERROR",
                                                                           "message": "Error parsing Json: incorrect  typeClass for field: authorName, should be primitive"}}

    create_future = Future()
    create_future.set_result(validation_error)

    restructured_metadata = {"datasetVersion": {"metadataBlocks": {"citation": {
      "fields": [{"typeName": "title", "multiple": False, "typeClass": "primitive", "value": "Test Data Set"}]},
      "geospatial": {"fields": [

      ]}, "socialscience": {"fields": [

      ]}, "astrophysics": {"fields": [

      ]}, "biomedical": {"fields": [

      ]}, "journal": {"fields": [

      ]}}}}

    mocker.patch.object(dataverse_client_mock.http_client, "post", return_value=create_future)
    result = await dataverse_client_mock.create_and_publish_dataset("parent_dataverse_id", {"title": "Test Data Set"},
                                                                    True)
    assert result == (f"Error creating dataset, Alias: Test Data Set, Server: {dataverse_client_mock.server_url},  "
                      f"Reason: Bad Request, Info: {validation_error['result']}"), "result must be equal to mock_publish_result['data']"
    dataverse_client_mock.logger.info.assert_called_once_with("Creating dataset, Alias: %s on server: %s",
                                                              "Test Data Set", dataverse_client_mock.server_url)
    dataverse_client_mock.logger.error.assert_called_once_with(f"Error creating dataset, Alias: Test Data Set, Server: "
                                                               f"{dataverse_client_mock.server_url},  "
                                                               f"Reason: {validation_error['reason']}, "
                                                               f"Info: {validation_error['result']}")
    dataverse_client_mock.http_client.post.assert_called_once_with(
      f"{dataverse_client_mock.server_url}/api/dataverses/parent_dataverse_id/datasets",
      request_params={'doNotValidate': str(not True)},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token},
      json=restructured_metadata)

  @pytest.mark.asyncio
  async def test_create_dataset__request_failures_should_return_expected_error(self, mocker,
                                                                               dataverse_client_mock: dataverse_client_mock):
    dataverse_client_mock.http_client.session_request_errors = [
      "ClientConnectorError for url (url) with error: Cannot connect to host localhost:8080 ssl:default [Connect call failed ('127.0.0.1', 8080)]"]
    restructured_metadata = {"datasetVersion": {"metadataBlocks": {"citation": {
      "fields": [{"typeName": "title", "multiple": False, "typeClass": "primitive", "value": "Test Data Set"}]},
      "geospatial": {"fields": [

      ]}, "socialscience": {"fields": [

      ]}, "astrophysics": {"fields": [

      ]}, "biomedical": {"fields": [

      ]}, "journal": {"fields": [

      ]}}}}

    upload_future = Future()
    upload_future.set_result({})
    publish_future = Future()
    publish_future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'post', side_effect=[upload_future, publish_future])
    result = await dataverse_client_mock.create_and_publish_dataset("parent_dataverse_id", {"title": "Test Data Set"},
                                                                    True)
    assert result == dataverse_client_mock.http_client.session_request_errors, "session_request_errors must be returned!"
    dataverse_client_mock.http_client.post.assert_has_calls([
      mocker.call(f"{dataverse_client_mock.server_url}/api/dataverses/parent_dataverse_id/datasets",
                  request_params={'doNotValidate': 'False'},
                  request_headers={'Content-Type': 'application/json',
                                   'X-Dataverse-key': dataverse_client_mock.api_token},
                  json=restructured_metadata)])

    upload_future = Future()
    upload_future.set_result({"status": 201, "reason": "Created", "result": {"data": {"persistentId": "id"}}})
    publish_future = Future()
    publish_future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'post', side_effect=[upload_future, publish_future])
    result = await dataverse_client_mock.create_and_publish_dataset("parent_dataverse_id", {"title": "Test Data Set"},
                                                                    True)
    assert result == dataverse_client_mock.http_client.session_request_errors, "session_request_errors must be returned!"
    dataverse_client_mock.http_client.post.assert_has_calls([
      mocker.call(f"{dataverse_client_mock.server_url}/api/dataverses/parent_dataverse_id/datasets",
                  request_params={'doNotValidate': 'False'},
                  request_headers={'Content-Type': 'application/json',
                                   'X-Dataverse-key': dataverse_client_mock.api_token},
                  json=restructured_metadata),
      mocker.call(f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/actions/:publish",
                  request_params={'persistentId': "id", 'type': 'major'},
                  request_headers={'Content-Type': 'application/json',
                                   'X-Dataverse-key': dataverse_client_mock.api_token})])

  @pytest.mark.asyncio
  async def test_publish_dataset_failure_should_return_error(self, mocker,
                                                             dataverse_client_mock: dataverse_client_mock):
    dataset_create_response = {"status": 201, "reason": "Created",
                               "result": {"status": "OK",
                                          "data": {"id": 105, "persistentId": "doi:10.5072/FK2/KTE31V"}}}
    dataset_publish_response = {"status": 404, "reason": "Error",
                                "result": {"status": "Error", "message": "Publish failed!!"}}

    create_future = Future()
    create_future.set_result(dataset_create_response)
    publish_future = Future()
    publish_future.set_result(dataset_publish_response)

    mocker.patch.object(dataverse_client_mock.http_client, 'post', side_effect=[create_future, publish_future])
    restructured_metadata = {"datasetVersion": {"metadataBlocks": {"citation": {
      "fields": [{"typeName": "title", "multiple": False, "typeClass": "primitive", "value": "Test Data Set"}]},
      "geospatial": {"fields": [

      ]}, "socialscience": {"fields": [

      ]}, "astrophysics": {"fields": [

      ]}, "biomedical": {"fields": [

      ]}, "journal": {"fields": [

      ]}}}}

    result = await dataverse_client_mock.create_and_publish_dataset("parent_dataverse_id", {"title": "Test Data Set"},
                                                                    True)
    assert result == (f"Error publishing dataset, Alias: Test Data Set, Server: {dataverse_client_mock.server_url},  "
                      f"Reason: {dataset_publish_response['reason']}, Info: {dataset_publish_response['result']}"), "result must be equal to mock_publish_result['data']"
    dataverse_client_mock.logger.info.assert_called_once_with("Creating dataset, Alias: %s on server: %s",
                                                              "Test Data Set", dataverse_client_mock.server_url)
    dataverse_client_mock.logger.error.assert_called_once_with(
      f"Error publishing dataset, Alias: Test Data Set, Server: "
      f"{dataverse_client_mock.server_url},  "
      f"Reason: {dataset_publish_response['reason']}, "
      f"Info: {dataset_publish_response['result']}")

    dataverse_client_mock.http_client.post.assert_has_calls([
      mocker.call(f"{dataverse_client_mock.server_url}/api/dataverses/parent_dataverse_id/datasets",
                  request_params={'doNotValidate': str(not True)},
                  request_headers={'Content-Type': 'application/json',
                                   'X-Dataverse-key': dataverse_client_mock.api_token},
                  json=restructured_metadata),
      mocker.call(f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/actions/:publish",
                  request_params={'persistentId': "doi:10.5072/FK2/KTE31V", 'type': 'major'},
                  request_headers={'Content-Type': 'application/json',
                                   'X-Dataverse-key': dataverse_client_mock.api_token})])

  @pytest.mark.asyncio
  async def test_dataset_upload_file_fails_with_error_should_return_expected_error(self, mocker,
                                                                                   dataverse_client_mock: dataverse_client_mock):
    test_file_path = "/home/user/test.txt"
    test_file_name = "test.txt"
    test_ds_pid = "doi:10.5072/FK2/KTE31V"
    test_desc = "Test description ##"
    test_categories = ["Test tag1", "Test tag2"]

    mock_basename = mocker.patch('pasta_eln.dataverse.client.basename')
    mock_basename.return_value = test_file_name
    mock_dumps = mocker.patch('pasta_eln.dataverse.client.dumps')
    mock_file = mocker.MagicMock()
    mock_file_open = mocker.patch('pasta_eln.dataverse.client.open', return_value=mock_file)
    mocker.patch.object(mock_file, '__enter__', return_value=mock_file)
    mock_dumps.return_value = {"test": "test"}
    mock_form_data = mocker.patch('pasta_eln.dataverse.client.FormData')

    upload_response = {"status": 500, "reason": "Internal Server Error",
                       "result": {"status": "ERROR", "message": {"message": "This file is invalid!!. "}}}

    upload_future = Future()
    upload_future.set_result(upload_response)

    mocker.patch.object(dataverse_client_mock.http_client, 'post', side_effect=[upload_future])
    result = await dataverse_client_mock.upload_file(test_ds_pid, test_file_path, test_desc, test_categories)

    expected_error = (f"Error uploading file: {test_file_path} "
                      f"to dataset: {test_ds_pid} "
                      f"on server: {dataverse_client_mock.server_url}, "
                      f"Reason: {upload_response['reason']}, "
                      f"Info: {upload_response['result']}")

    assert result == expected_error, "Upload result not as expected!"
    dataverse_client_mock.logger.info.assert_called_once_with("Uploading file: %s to Dataset: %s on server: %s",
                                                              test_file_path, test_ds_pid,
                                                              dataverse_client_mock.server_url)
    dataverse_client_mock.logger.error.assert_called_once_with(expected_error)
    mock_basename.assert_called_once_with(test_file_path)
    mock_dumps.assert_called_once_with(dict(description=test_desc, categories=test_categories))
    mock_form_data.assert_called_once()
    mock_form_data.return_value.add_field.assert_has_calls(
      [mocker.call('file', mock_file, filename=test_file_name, content_type='multipart/form-data'),
       mocker.call('jsonData', mock_dumps.return_value, content_type='application/json')])
    dataverse_client_mock.http_client.post.assert_has_calls([
      mocker.call(f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/add",
                  request_params={'persistentId': test_ds_pid},
                  request_headers={'X-Dataverse-key': dataverse_client_mock.api_token},
                  data=mock_form_data.return_value,
                  timeout=0)])
    mock_file_open.assert_called_once_with(test_file_path, 'rb')

  @pytest.mark.asyncio
  async def test_dataset_upload_file_succeed_should_return_expected_result(self, mocker,
                                                                           dataverse_client_mock: dataverse_client_mock):
    test_file_path = "/home/user/test.txt"
    test_file_name = "test.txt"
    test_ds_pid = "doi:10.5072/FK2/KTE31V"
    test_desc = "Test description ##"
    test_categories = ["Test tag1", "Test tag2"]

    mock_basename = mocker.patch('pasta_eln.dataverse.client.basename')
    mock_basename.return_value = test_file_name
    mock_dumps = mocker.patch('pasta_eln.dataverse.client.dumps')
    mock_file = mocker.MagicMock()
    mock_file_open = mocker.patch('pasta_eln.dataverse.client.open', return_value=mock_file)
    mocker.patch.object(mock_file, '__enter__', return_value=mock_file)
    mock_dumps.return_value = {"test": "test"}
    mock_form_data = mocker.patch('pasta_eln.dataverse.client.FormData')

    upload_response = {"status": 200, "reason": "OK", "result": {"status": "OK",
                                                                 "message": {
                                                                   "message": "This file has the same content as ds_file.txt that is in the dataset. "},
                                                                 "data": {
                                                                   "files": [{"description": "Test description ##",
                                                                              "label": "ds_file-1.txt",
                                                                              "restricted": False, "version": 1,
                                                                              "datasetVersionId": 86,
                                                                              "categories": ["Test tag1", "Test tag2"],
                                                                              "dataFile": {"id": 108,
                                                                                           "persistentId": "",
                                                                                           "filename": "ds_file-1.txt",
                                                                                           "contentType": "multipart/form-data",
                                                                                           "friendlyType": "multipart/form-data",
                                                                                           "filesize": 15,
                                                                                           "description": "Test description ##",
                                                                                           "categories": ["Test tag1",
                                                                                                          "Test tag2"],
                                                                                           "storageIdentifier": "local://18c587171cc-93f2e67da5b5",
                                                                                           "rootDataFileId": -1,
                                                                                           "md5": "13fd6190998e143667614471a36aa701",
                                                                                           "checksum": {"type": "MD5",
                                                                                                        "value": "13fd6190998e143667614471a36aa701"},
                                                                                           "tabularData": False,
                                                                                           "creationDate": "2023-12-11",
                                                                                           "fileAccessRequest": True}}]}}}
    publish_response = {"status": 200, "reason": "OK", "result": {"status": "OK",
                                                                  "data": {"id": 105, "identifier": "FK2/KTE31V",
                                                                           "persistentUrl": "https://doi.org/10.5072/FK2/KTE31V",
                                                                           "protocol": "doi", "authority": "10.5072",
                                                                           "publisher": "Root",
                                                                           "publicationDate": "2023-12-11",
                                                                           "storageIdentifier": "local://10.5072/FK2/KTE31V"}}}
    upload_future = Future()
    upload_future.set_result(upload_response)
    publish_future = Future()
    publish_future.set_result(publish_response)

    mocker.patch.object(dataverse_client_mock.http_client, 'post', side_effect=[upload_future, publish_future])

    result = await dataverse_client_mock.upload_file(test_ds_pid, test_file_path, test_desc, test_categories)

    assert result == {'file_upload_result': upload_response.get('result').get('data'),
                      'dataset_publish_result': publish_response.get('result').get(
                        'data')}, "Upload result not as expected!"
    dataverse_client_mock.logger.info.assert_called_once_with("Uploading file: %s to Dataset: %s on server: %s",
                                                              test_file_path, test_ds_pid,
                                                              dataverse_client_mock.server_url)
    mock_basename.assert_called_once_with(test_file_path)
    mock_dumps.assert_called_once_with(dict(description=test_desc, categories=test_categories))
    mock_form_data.assert_called_once()
    mock_form_data.return_value.add_field.assert_has_calls(
      [mocker.call('file', mock_file, filename=test_file_name, content_type='multipart/form-data'),
       mocker.call('jsonData', mock_dumps.return_value, content_type='application/json')])
    dataverse_client_mock.http_client.post.assert_has_calls([
      mocker.call(f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/add",
                  request_params={'persistentId': test_ds_pid},
                  request_headers={'X-Dataverse-key': dataverse_client_mock.api_token},
                  data=mock_form_data.return_value,
                  timeout=0),
      mocker.call(f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/actions/:publish",
                  request_params={'persistentId': test_ds_pid, 'type': 'major'},
                  request_headers={'Content-Type': 'application/json',
                                   'X-Dataverse-key': dataverse_client_mock.api_token})])
    mock_file_open.assert_called_once_with(test_file_path, 'rb')

  @pytest.mark.asyncio
  async def test_dataset_upload_file_publish_failure_should_return_expected_error(self, mocker,
                                                                                  dataverse_client_mock: dataverse_client_mock):
    test_file_path = "/home/user/test.txt"
    test_file_name = "test.txt"
    test_ds_pid = "doi:10.5072/FK2/KTE31V"
    test_desc = "Test description ##"
    test_categories = ["Test tag1", "Test tag2"]

    mock_basename = mocker.patch('pasta_eln.dataverse.client.basename')
    mock_basename.return_value = test_file_name
    mock_dumps = mocker.patch('pasta_eln.dataverse.client.dumps')
    mock_file = mocker.MagicMock()
    mock_file_open = mocker.patch('pasta_eln.dataverse.client.open', return_value=mock_file)
    mocker.patch.object(mock_file, '__enter__', return_value=mock_file)
    mock_dumps.return_value = {"test": "test"}
    mock_form_data = mocker.patch('pasta_eln.dataverse.client.FormData')

    upload_response = {"status": 200, "reason": "OK", "result": {"status": "OK",
                                                                 "message": {
                                                                   "message": "This file has the same content as ds_file.txt that is in the dataset. "},
                                                                 "data": {
                                                                   "files": [{"description": "Test description ##",
                                                                              "label": "ds_file-1.txt",
                                                                              "restricted": False, "version": 1,
                                                                              "datasetVersionId": 86,
                                                                              "categories": ["Test tag1", "Test tag2"],
                                                                              "dataFile": {"id": 108,
                                                                                           "persistentId": "",
                                                                                           "filename": "ds_file-1.txt",
                                                                                           "contentType": "multipart/form-data",
                                                                                           "friendlyType": "multipart/form-data",
                                                                                           "filesize": 15,
                                                                                           "description": "Test description ##",
                                                                                           "categories": ["Test tag1",
                                                                                                          "Test tag2"],
                                                                                           "storageIdentifier": "local://18c587171cc-93f2e67da5b5",
                                                                                           "rootDataFileId": -1,
                                                                                           "md5": "13fd6190998e143667614471a36aa701",
                                                                                           "checksum": {"type": "MD5",
                                                                                                        "value": "13fd6190998e143667614471a36aa701"},
                                                                                           "tabularData": False,
                                                                                           "creationDate": "2023-12-11",
                                                                                           "fileAccessRequest": True}}]}}}
    publish_response = {"status": 500, "reason": "Internal Server Error",
                        "result": {"status": "OK", "message": "Publish failed!!"}}
    upload_future = Future()
    upload_future.set_result(upload_response)
    publish_future = Future()
    publish_future.set_result(publish_response)

    mocker.patch.object(dataverse_client_mock.http_client, 'post', side_effect=[upload_future, publish_future])

    result = await dataverse_client_mock.upload_file(test_ds_pid, test_file_path, test_desc, test_categories)
    expected_error = (f"Error publishing dataset: {test_ds_pid} "
                      f"as part of file ({test_file_path}) upload on server: {dataverse_client_mock.server_url}, "
                      f"Reason: {publish_response['reason']}, "
                      f"Info: {publish_response['result']}")

    assert result == expected_error, "Upload result not as expected!"
    dataverse_client_mock.logger.info.assert_called_once_with("Uploading file: %s to Dataset: %s on server: %s",
                                                              test_file_path, test_ds_pid,
                                                              dataverse_client_mock.server_url)
    dataverse_client_mock.logger.error.assert_called_once_with(expected_error)
    mock_basename.assert_called_once_with(test_file_path)
    mock_dumps.assert_called_once_with(dict(description=test_desc, categories=test_categories))
    mock_form_data.assert_called_once()
    mock_form_data.return_value.add_field.assert_has_calls(
      [mocker.call('file', mock_file, filename=test_file_name, content_type='multipart/form-data'),
       mocker.call('jsonData', mock_dumps.return_value, content_type='application/json')])
    dataverse_client_mock.http_client.post.assert_has_calls([
      mocker.call(f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/add",
                  request_params={'persistentId': test_ds_pid},
                  request_headers={'X-Dataverse-key': dataverse_client_mock.api_token},
                  data=mock_form_data.return_value,
                  timeout=0),
      mocker.call(f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/actions/:publish",
                  request_params={'persistentId': test_ds_pid, 'type': 'major'},
                  request_headers={'Content-Type': 'application/json',
                                   'X-Dataverse-key': dataverse_client_mock.api_token})])
    mock_file_open.assert_called_once_with(test_file_path, 'rb')

  @pytest.mark.asyncio
  async def test_dataset_upload_file_request_failures_should_return_expected_error(self, mocker,
                                                                                   dataverse_client_mock: dataverse_client_mock):
    test_file_path = "/home/user/test.txt"
    test_file_name = "test.txt"
    test_ds_pid = "doi:10.5072/FK2/KTE31V"
    test_desc = "Test description ##"
    test_categories = ["Test tag1", "Test tag2"]

    mock_basename = mocker.patch('pasta_eln.dataverse.client.basename')
    mock_basename.return_value = test_file_name
    mock_dumps = mocker.patch('pasta_eln.dataverse.client.dumps')
    mock_file = mocker.MagicMock()
    mock_file_open = mocker.patch('pasta_eln.dataverse.client.open', return_value=mock_file)
    mocker.patch.object(mock_file, '__enter__', return_value=mock_file)
    mock_dumps.return_value = {"test": "test"}
    mock_form_data = mocker.patch('pasta_eln.dataverse.client.FormData')

    dataverse_client_mock.http_client.session_request_errors = [
      "ClientConnectorError for url (url) with error: Cannot connect to host localhost:8080 ssl:default [Connect call failed ('127.0.0.1', 8080)]"]

    upload_future = Future()
    upload_future.set_result({})
    publish_future = Future()
    publish_future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'post', side_effect=[upload_future, publish_future])
    result = await dataverse_client_mock.upload_file(test_ds_pid, test_file_path, test_desc, test_categories)
    assert result == dataverse_client_mock.http_client.session_request_errors, "session_request_errors must be returned!"
    dataverse_client_mock.http_client.post.assert_has_calls([
      mocker.call(f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/add",
                  request_params={'persistentId': test_ds_pid},
                  request_headers={'X-Dataverse-key': dataverse_client_mock.api_token},
                  data=mock_form_data.return_value,
                  timeout=0)])

    upload_future = Future()
    upload_future.set_result({"status": 200, "reason": "OK", "message": "Upload successful!"})
    publish_future = Future()
    publish_future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'post', side_effect=[upload_future, publish_future])
    result = await dataverse_client_mock.upload_file(test_ds_pid, test_file_path, test_desc, test_categories)
    assert result == dataverse_client_mock.http_client.session_request_errors, "session_request_errors must be returned!"
    dataverse_client_mock.http_client.post.assert_has_calls([
      mocker.call(f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/add",
                  request_params={'persistentId': test_ds_pid},
                  request_headers={'X-Dataverse-key': dataverse_client_mock.api_token},
                  data=mock_form_data.return_value,
                  timeout=0),
      mocker.call(f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/actions/:publish",
                  request_params={'persistentId': test_ds_pid, 'type': 'major'},
                  request_headers={'Content-Type': 'application/json',
                                   'X-Dataverse-key': dataverse_client_mock.api_token})])
    mock_file_open.assert_has_calls([mocker.call(test_file_path, 'rb'), mocker.call(test_file_path, 'rb')

                                     ])

  @pytest.mark.asyncio
  async def test_get_dataset_info_json_when_succeeds_return_dataset_json(self, mocker,
                                                                         dataverse_client_mock: dataverse_client_mock):
    dataset_info_response = {"status": 200, "reason": "OK", "result": {"status": "OK",
                                                                       "data": {"id": 91, "datasetId": 105,
                                                                                "datasetPersistentId": "doi:10.5072/FK2/KTE31V",
                                                                                "storageIdentifier": "local://10.5072/FK2/KTE31V",
                                                                                "versionNumber": 8,
                                                                                "versionMinorNumber": 0,
                                                                                "versionState": "RELEASED",
                                                                                "lastUpdateTime": "2023-12-11T11:16:14Z",
                                                                                "releaseTime": "2023-12-11T11:16:14Z",
                                                                                "createTime": "2023-12-11T11:15:25Z",
                                                                                "publicationDate": "2023-12-11",
                                                                                "citationDate": "2023-12-11",
                                                                                "license": {"name": "CC0 1.0",
                                                                                            "uri": "http://creativecommons.org/publicdomain/zero/1.0",
                                                                                            "iconUri": "https://licensebuttons.net/p/zero/1.0/88x31.png"},
                                                                                "fileAccessRequest": True,
                                                                                "metadataBlocks": {
                                                                                  "citation": {
                                                                                    "displayName": "Citation Metadata",
                                                                                    "name": "citation",
                                                                                    "fields": [{"typeName": "title",
                                                                                                "multiple": False,
                                                                                                "typeClass": "primitive",
                                                                                                "value": "Test Data Set"},
                                                                                               {"typeName": "author",
                                                                                                "multiple": True,
                                                                                                "typeClass": "compound",
                                                                                                "value": [{
                                                                                                  "authorName": {
                                                                                                    "typeName": "authorName",
                                                                                                    "multiple": False,
                                                                                                    "typeClass": "primitive",
                                                                                                    "value": "Steven, Jacob"},
                                                                                                  "authorAffiliation": {
                                                                                                    "typeName": "authorAffiliation",
                                                                                                    "multiple": False,
                                                                                                    "typeClass": "primitive",
                                                                                                    "value": "FZJ"},
                                                                                                  "authorIdentifierScheme": {
                                                                                                    "typeName": "authorIdentifierScheme",
                                                                                                    "multiple": False,
                                                                                                    "typeClass": "controlledVocabulary",
                                                                                                    "value": "ORCID"},
                                                                                                  "authorIdentifier": {
                                                                                                    "typeName": "authorIdentifier",
                                                                                                    "multiple": False,
                                                                                                    "typeClass": "primitive",
                                                                                                    "value": "1234-5678-9012-3456"}},
                                                                                                  {
                                                                                                    "authorName": {
                                                                                                      "typeName": "authorName",
                                                                                                      "multiple": False,
                                                                                                      "typeClass": "primitive",
                                                                                                      "value": "Leslie, Suzanne"},
                                                                                                    "authorAffiliation": {
                                                                                                      "typeName": "authorAffiliation",
                                                                                                      "multiple": False,
                                                                                                      "typeClass": "primitive",
                                                                                                      "value": "FZJ"},
                                                                                                    "authorIdentifierScheme": {
                                                                                                      "typeName": "authorIdentifierScheme",
                                                                                                      "multiple": False,
                                                                                                      "typeClass": "controlledVocabulary",
                                                                                                      "value": "ISNI"},
                                                                                                    "authorIdentifier": {
                                                                                                      "typeName": "authorIdentifier",
                                                                                                      "multiple": False,
                                                                                                      "typeClass": "primitive",
                                                                                                      "value": "4567-8901-2345-6789"}}]},
                                                                                               {
                                                                                                 "typeName": "datasetContact",
                                                                                                 "multiple": True,
                                                                                                 "typeClass": "compound",
                                                                                                 "value": [{
                                                                                                   "datasetContactName": {
                                                                                                     "typeName": "datasetContactName",
                                                                                                     "multiple": False,
                                                                                                     "typeClass": "primitive",
                                                                                                     "value": "Rashid, Muhammed"},
                                                                                                   "datasetContactAffiliation": {
                                                                                                     "typeName": "datasetContactAffiliation",
                                                                                                     "multiple": False,
                                                                                                     "typeClass": "primitive",
                                                                                                     "value": "test Affiliation"},
                                                                                                   "datasetContactEmail": {
                                                                                                     "typeName": "datasetContactEmail",
                                                                                                     "multiple": False,
                                                                                                     "typeClass": "primitive",
                                                                                                     "value": "test@test.com"}}]},
                                                                                               {
                                                                                                 "typeName": "dsDescription",
                                                                                                 "multiple": True,
                                                                                                 "typeClass": "compound",
                                                                                                 "value": [{
                                                                                                   "dsDescriptionValue": {
                                                                                                     "typeName": "dsDescriptionValue",
                                                                                                     "multiple": False,
                                                                                                     "typeClass": "primitive",
                                                                                                     "value": "Description 1"},
                                                                                                   "dsDescriptionDate": {
                                                                                                     "typeName": "dsDescriptionDate",
                                                                                                     "multiple": False,
                                                                                                     "typeClass": "primitive",
                                                                                                     "value": "2020-11-10"}},
                                                                                                   {
                                                                                                     "dsDescriptionValue": {
                                                                                                       "typeName": "dsDescriptionValue",
                                                                                                       "multiple": False,
                                                                                                       "typeClass": "primitive",
                                                                                                       "value": "Description 2"},
                                                                                                     "dsDescriptionDate": {
                                                                                                       "typeName": "dsDescriptionDate",
                                                                                                       "multiple": False,
                                                                                                       "typeClass": "primitive",
                                                                                                       "value": "201-12-25"}}]},
                                                                                               {"typeName": "subject",
                                                                                                "multiple": True,
                                                                                                "typeClass": "controlledVocabulary",
                                                                                                "value": ["Chemistry",
                                                                                                          "Engineering"]},
                                                                                               {"typeName": "language",
                                                                                                "multiple": True,
                                                                                                "typeClass": "controlledVocabulary",
                                                                                                "value": ["English",
                                                                                                          "German"]},
                                                                                               {
                                                                                                 "typeName": "otherReferences",
                                                                                                 "multiple": True,
                                                                                                 "typeClass": "primitive",
                                                                                                 "value": ["Ref1",
                                                                                                           "Ref2",
                                                                                                           "Ref3"]}]},
                                                                                  "geospatial": {
                                                                                    "displayName": "Geospatial Metadata",
                                                                                    "name": "geospatial", "fields": [
                                                                                      {"typeName": "geographicCoverage",
                                                                                       "multiple": True,
                                                                                       "typeClass": "compound",
                                                                                       "value": [{
                                                                                         "country": {
                                                                                           "typeName": "country",
                                                                                           "multiple": False,
                                                                                           "typeClass": "controlledVocabulary",
                                                                                           "value": "Albania"},
                                                                                         "state": {"typeName": "state",
                                                                                                   "multiple": False,
                                                                                                   "typeClass": "primitive",
                                                                                                   "value": "AlbaniaState"},
                                                                                         "city": {"typeName": "city",
                                                                                                  "multiple": False,
                                                                                                  "typeClass": "primitive",
                                                                                                  "value": "AlbaniaCity"},
                                                                                         "otherGeographicCoverage": {
                                                                                           "typeName": "otherGeographicCoverage",
                                                                                           "multiple": False,
                                                                                           "typeClass": "primitive",
                                                                                           "value": "CoverageOther"}}]}]},
                                                                                  "socialscience": {
                                                                                    "displayName": "Social Science and Humanities Metadata",
                                                                                    "name": "socialscience",
                                                                                    "fields": [
                                                                                      {"typeName": "researchInstrument",
                                                                                       "multiple": False,
                                                                                       "typeClass": "primitive",
                                                                                       "value": "Instruments1"}]},
                                                                                  "astrophysics": {
                                                                                    "displayName": "Astronomy and Astrophysics Metadata",
                                                                                    "name": "astrophysics", "fields": [
                                                                                      {"typeName": "astroType",
                                                                                       "multiple": True,
                                                                                       "typeClass": "controlledVocabulary",
                                                                                       "value": ["Mosaic"]},
                                                                                      {"typeName": "astroFacility",
                                                                                       "multiple": True,
                                                                                       "typeClass": "primitive",
                                                                                       "value": ["AIK-2", "AIK-3"]}]},
                                                                                  "biomedical": {
                                                                                    "displayName": "Life Sciences Metadata",
                                                                                    "name": "biomedical", "fields": [
                                                                                      {"typeName": "studyDesignType",
                                                                                       "multiple": True,
                                                                                       "typeClass": "controlledVocabulary",
                                                                                       "value": ["Case Control",
                                                                                                 "Cross Sectional"]},
                                                                                      {"typeName": "studyAssayOrganism",
                                                                                       "multiple": True,
                                                                                       "typeClass": "controlledVocabulary",
                                                                                       "value": ["Arabidopsis thaliana",
                                                                                                 "Bos taurus",
                                                                                                 "Zea mays"]},
                                                                                      {"typeName": "studyAssayCellType",
                                                                                       "multiple": True,
                                                                                       "typeClass": "primitive",
                                                                                       "value": ["CellType1",
                                                                                                 "CellType2"]}]},
                                                                                  "journal": {
                                                                                    "displayName": "Journal Metadata",
                                                                                    "name": "journal",
                                                                                    "fields": [
                                                                                      {"typeName": "journalVolumeIssue",
                                                                                       "multiple": True,
                                                                                       "typeClass": "compound",
                                                                                       "value": [{
                                                                                         "journalVolume": {
                                                                                           "typeName": "journalVolume",
                                                                                           "multiple": False,
                                                                                           "typeClass": "primitive",
                                                                                           "value": "2333.444"},
                                                                                         "journalIssue": {
                                                                                           "typeName": "journalIssue",
                                                                                           "multiple": False,
                                                                                           "typeClass": "primitive",
                                                                                           "value": "Journal3.4"},
                                                                                         "journalPubDate": {
                                                                                           "typeName": "journalPubDate",
                                                                                           "multiple": False,
                                                                                           "typeClass": "primitive",
                                                                                           "value": "2021-10-10"}}]}]}},
                                                                                "files": [
                                                                                  {"description": "Test description ##",
                                                                                   "label": "ds_file-2.txt",
                                                                                   "restricted": False, "version": 1,
                                                                                   "datasetVersionId": 91,
                                                                                   "categories": ["Test tag1",
                                                                                                  "Test tag2"],
                                                                                   "dataFile": {"id": 109,
                                                                                                "persistentId": "",
                                                                                                "filename": "ds_file-2.txt",
                                                                                                "contentType": "multipart/form-data",
                                                                                                "friendlyType": "multipart/form-data",
                                                                                                "filesize": 15,
                                                                                                "description": "Test description ##",
                                                                                                "categories": [
                                                                                                  "Test tag1",
                                                                                                  "Test tag2"],
                                                                                                "storageIdentifier": "local://18c588e6aed-6470c8026250",
                                                                                                "rootDataFileId": -1,
                                                                                                "md5": "13fd6190998e143667614471a36aa701",
                                                                                                "checksum": {
                                                                                                  "type": "MD5",
                                                                                                  "value": "13fd6190998e143667614471a36aa701"},
                                                                                                "tabularData": False,
                                                                                                "creationDate": "2023-12-11",
                                                                                                "publicationDate": "2023-12-11",
                                                                                                "fileAccessRequest": True}},
                                                                                  {"description": "Test description ##",
                                                                                   "label": "trials_after_couch_db_re_install.webm",
                                                                                   "restricted": False,
                                                                                   "version": 1, "datasetVersionId": 91,
                                                                                   "categories": ["Test tag1",
                                                                                                  "Test tag2"],
                                                                                   "dataFile": {"id": 111,
                                                                                                "persistentId": "",
                                                                                                "filename": "trials_after_couch_db_re_install.webm",
                                                                                                "contentType": "multipart/form-data",
                                                                                                "friendlyType": "multipart/form-data",
                                                                                                "filesize": 132505595,
                                                                                                "description": "Test description ##",
                                                                                                "categories": [
                                                                                                  "Test tag1",
                                                                                                  "Test tag2"],
                                                                                                "storageIdentifier": "local://18c5890e6ac-258ade1533f6",
                                                                                                "rootDataFileId": -1,
                                                                                                "md5": "67c1921cc78d5314d031351f763d4cfa",
                                                                                                "checksum": {
                                                                                                  "type": "MD5",
                                                                                                  "value": "67c1921cc78d5314d031351f763d4cfa"},
                                                                                                "tabularData": False,
                                                                                                "creationDate": "2023-12-11",
                                                                                                "publicationDate": "2023-12-11",
                                                                                                "fileAccessRequest": True}}]}}}
    info_future = Future()
    info_future.set_result(dataset_info_response)
    mocker.patch.object(dataverse_client_mock.http_client, 'get', side_effect=[info_future])
    result = await dataverse_client_mock.get_dataset_info_json("doi:10.5072/FK2/KTE31V", "2.0")
    assert result == dataset_info_response.get('result').get('data'), "Invalid result!"
    dataverse_client_mock.logger.info.assert_called_once_with(
      "Fetching JSON representation of a dataset: %s for server: %s", "doi:10.5072/FK2/KTE31V",
      dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_once_with(
      f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/versions/2.0?persistentId=doi:10.5072/FK2/KTE31V",
      request_params={'Accept': 'application/json'},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_get_dataset_info_for_invalid_id_returns_error(self, mocker,
                                                               dataverse_client_mock: dataverse_client_mock):
    error = {"status": 404, "reason": "Not Found",
             "result": {"status": "ERROR", "message": "Dataset with Persistent ID doi:10.5072/FK2/KTE31V3 not found."}}

    info_future = Future()
    info_future.set_result(error)
    mocker.patch.object(dataverse_client_mock.http_client, 'get', side_effect=[info_future])
    result = await dataverse_client_mock.get_dataset_info_json("invalid", "2.0")
    error = (f"Error fetching JSON representation of dataset: invalid "
             f"on server: {dataverse_client_mock.server_url}, "
             f"Reason: {error['reason']}, "
             f"Info: {error['result']}")
    assert result == error, "Invalid result!"
    dataverse_client_mock.logger.info.assert_called_once_with(
      "Fetching JSON representation of a dataset: %s for server: %s", "invalid", dataverse_client_mock.server_url)
    dataverse_client_mock.logger.error.assert_called_once_with(error)
    dataverse_client_mock.http_client.get.assert_called_once_with(
      f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/versions/2.0?persistentId=invalid",
      request_params={'Accept': 'application/json'},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_get_dataset_info_request_fails_returns_error(self, mocker,
                                                              dataverse_client_mock: dataverse_client_mock):
    info_future = Future()
    info_future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'get', side_effect=[info_future])
    dataverse_client_mock.http_client.session_request_errors = [
      "ClientConnectorError for url (url) with error: Cannot connect to host localhost:8080 ssl:default [Connect call failed ('127.0.0.1', 8080)]"]
    result = await dataverse_client_mock.get_dataset_info_json("invalid", "2.0")
    assert result == dataverse_client_mock.http_client.session_request_errors, "Invalid result!"
    dataverse_client_mock.http_client.get.assert_called_once_with(
      f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/versions/2.0?persistentId=invalid",
      request_params={'Accept': 'application/json'},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_get_dataset_versions_when_succeeds_returns_expected(self, mocker,
                                                                     dataverse_client_mock: dataverse_client_mock):
    version_info = {"status": 200, "reason": "OK", "result": {"status": "OK", "data": [
      {"id": 92, "datasetId": 69, "datasetPersistentId": "doi:10.5072/FK2/JRRO5W",
       "storageIdentifier": "local://10.5072/FK2/JRRO5W", "versionNumber": 2, "versionMinorNumber": 0,
       "versionState": "RELEASED", "lastUpdateTime": "2023-12-11T14:53:50Z", "releaseTime": "2023-12-11T14:53:50Z",
       "createTime": "2023-12-11T14:53:44Z", "publicationDate": "2023-12-05", "citationDate": "2023-12-05",
       "license": {"name": "CC0 1.0", "uri": "http://creativecommons.org/publicdomain/zero/1.0",
                   "iconUri": "https://licensebuttons.net/p/zero/1.0/88x31.png"}, "fileAccessRequest": True, "files": [
        {"description": "Test ##", "label": "Notes.txt", "restricted": False, "version": 1, "datasetVersionId": 92,
         "dataFile": {"id": 113, "persistentId": "", "filename": "Notes.txt", "contentType": "text/plain",
                      "friendlyType": "Plain Text", "filesize": 2, "description": "Test ##",
                      "storageIdentifier": "local://18c595e4abb-c356831b7061", "rootDataFileId": -1,
                      "md5": "d784fa8b6d98d27699781bd9a7cf19f0",
                      "checksum": {"type": "MD5", "value": "d784fa8b6d98d27699781bd9a7cf19f0"}, "tabularData": False,
                      "creationDate": "2023-12-11", "publicationDate": "2023-12-11", "fileAccessRequest": True}}]},
      {"id": 61, "datasetId": 69, "datasetPersistentId": "doi:10.5072/FK2/JRRO5W",
       "storageIdentifier": "local://10.5072/FK2/JRRO5W", "versionNumber": 1, "versionMinorNumber": 0,
       "versionState": "RELEASED", "lastUpdateTime": "2023-12-05T12:43:51Z", "releaseTime": "2023-12-05T12:43:51Z",
       "createTime": "2023-12-01T13:24:16Z", "publicationDate": "2023-12-05", "citationDate": "2023-12-05",
       "license": {"name": "CC0 1.0", "uri": "http://creativecommons.org/publicdomain/zero/1.0",
                   "iconUri": "https://licensebuttons.net/p/zero/1.0/88x31.png"}, "fileAccessRequest": True, "files": [

      ]}]}}
    info_future = Future()
    info_future.set_result(version_info)
    mocker.patch.object(dataverse_client_mock.http_client, 'get', side_effect=[info_future])
    result = await dataverse_client_mock.get_dataset_versions("test_id")
    assert result == version_info.get("result").get("data"), "Not expected result!"
    dataverse_client_mock.logger.info.assert_called_with("Fetching version list for dataset: %s for server: %s",
                                                         "test_id", dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_with(
      f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/versions?persistentId=test_id",
      request_params={'Accept': 'application/json'},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_get_dataset_versions_when_fails_returns_error(self, mocker,
                                                               dataverse_client_mock: dataverse_client_mock):
    version_info = {"status": 404, "reason": "Not Found",
                    "result": {"status": "ERROR",
                               "message": "Dataset with Persistent ID doi:10.5072/FK2/JRRO5W4 not found."}}
    info_future = Future()
    info_future.set_result(version_info)
    mocker.patch.object(dataverse_client_mock.http_client, 'get', side_effect=[info_future])
    result = await dataverse_client_mock.get_dataset_versions("test_id")
    error = (f"Error fetching version list for dataset: test_id "
             f"on server: {dataverse_client_mock.server_url}, "
             f"Reason: {version_info['reason']}, "
             f"Info: {version_info['result']}")
    assert result == error, "Not expected result!"
    dataverse_client_mock.logger.info.assert_called_with("Fetching version list for dataset: %s for server: %s",
                                                         "test_id", dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_with(
      f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/versions?persistentId=test_id",
      request_params={'Accept': 'application/json'},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})
    dataverse_client_mock.logger.error.assert_called_once_with(error)

  @pytest.mark.asyncio
  async def test_get_dataset_versions_when_request_fails_returns_error(self, mocker,
                                                                       dataverse_client_mock: dataverse_client_mock):
    info_future = Future()
    info_future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'get', side_effect=[info_future])
    dataverse_client_mock.http_client.session_request_errors = [
      "ClientConnectorError for url (url) with error: Cannot connect to host localhost:8080 ssl:default [Connect call failed ('127.0.0.1', 8080)]"]
    result = await dataverse_client_mock.get_dataset_versions("test_id")
    assert result == dataverse_client_mock.http_client.session_request_errors, "Not expected result!"
    dataverse_client_mock.logger.info.assert_called_with("Fetching version list for dataset: %s for server: %s",
                                                         "test_id", dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_with(
      f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/versions?persistentId=test_id",
      request_params={'Accept': 'application/json'},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_get_dataset_files_when_succeeds_returns_expected(self, mocker,
                                                                  dataverse_client_mock: dataverse_client_mock):
    files_list_info = {"status": 200, "reason": "OK", "result": {"status": "OK", "data": [
      {"description": "Test ##", "label": "Notes.txt", "restricted": False, "version": 1, "datasetVersionId": 92,
       "dataFile": {"id": 113, "persistentId": "", "filename": "Notes.txt", "contentType": "text/plain",
                    "friendlyType": "Plain Text", "filesize": 2, "description": "Test ##",
                    "storageIdentifier": "local://18c595e4abb-c356831b7061", "rootDataFileId": -1,
                    "md5": "d784fa8b6d98d27699781bd9a7cf19f0",
                    "checksum": {"type": "MD5", "value": "d784fa8b6d98d27699781bd9a7cf19f0"}, "tabularData": False,
                    "creationDate": "2023-12-11", "publicationDate": "2023-12-11", "fileAccessRequest": True}}]}}
    info_future = Future()
    info_future.set_result(files_list_info)
    mocker.patch.object(dataverse_client_mock.http_client, 'get', side_effect=[info_future])
    result = await dataverse_client_mock.get_dataset_files("test_id", "version")
    assert result == files_list_info.get("result").get("data"), "Not expected result!"
    dataverse_client_mock.logger.info.assert_called_with("Fetching file list for dataset: %s for server: %s", "test_id",
                                                         dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_with(
      f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/versions/version/files?persistentId=test_id",
      request_params={'Accept': 'application/json'},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_get_dataset_files_when_fails_returns_error(self, mocker, dataverse_client_mock: dataverse_client_mock):
    error_files_info = {"status": 404, "reason": "Not Found",
                        "result": {"status": "ERROR",
                                   "message": "Dataset with Persistent ID doi:10.5072/FK2/JRRO5W4 not found."}}

    info_future = Future()
    info_future.set_result(error_files_info)
    mocker.patch.object(dataverse_client_mock.http_client, 'get', side_effect=[info_future])
    result = await dataverse_client_mock.get_dataset_files("test_id", "version")
    error = (f"Error fetching file list for dataset: test_id "
             f"on server: {dataverse_client_mock.server_url}, "
             f"Reason: {error_files_info['reason']}, "
             f"Info: {error_files_info['result']}")
    assert result == error, "Not expected result!"
    dataverse_client_mock.logger.info.assert_called_with("Fetching file list for dataset: %s for server: %s", "test_id",
                                                         dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_with(
      f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/versions/version/files?persistentId=test_id",
      request_params={'Accept': 'application/json'},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})
    dataverse_client_mock.logger.error.assert_called_once_with(error)

  @pytest.mark.asyncio
  async def test_get_dataset_files_when_request_fails_returns_error(self, mocker,
                                                                    dataverse_client_mock: dataverse_client_mock):
    info_future = Future()
    info_future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'get', side_effect=[info_future])
    dataverse_client_mock.http_client.session_request_errors = [
      "ClientConnectorError for url (url) with error: Cannot connect to host localhost:8080 ssl:default [Connect call failed ('127.0.0.1', 8080)]"]
    result = await dataverse_client_mock.get_dataset_files("test_id", "version")
    assert result == dataverse_client_mock.http_client.session_request_errors, "Not expected result!"
    dataverse_client_mock.logger.info.assert_called_with("Fetching file list for dataset: %s for server: %s", "test_id",
                                                         dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_with(
      f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/versions/version/files?persistentId=test_id",
      request_params={'Accept': 'application/json'},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_get_dataset_metadata_block_when_succeeds_returns_expected(self, mocker,
                                                                           dataverse_client_mock: dataverse_client_mock):
    metadata_info = {"status": 200, "reason": "OK", "result": {"status": "OK",
                                                               "data": {"biomedical:studyAssayCellType": ["CellType1",
                                                                                                          "CellType2"],
                                                                        "language": ["English", "German"],
                                                                        "socialscience:researchInstrument": "Instruments1",
                                                                        "biomedical:studyDesignType": ["Case Control",
                                                                                                       "Cross Sectional"],
                                                                        "biomedical:studyAssayOrganism": [
                                                                          "Arabidopsis thaliana", "Bos taurus",
                                                                          "Zea mays"],
                                                                        "otherReferences": ["Ref1", "Ref2", "Ref3"],
                                                                        "astrophysics:astroFacility": ["AIK-2",
                                                                                                       "AIK-3"],
                                                                        "astrophysics:astroType": "Mosaic",
                                                                        "subject": ["Chemistry", "Engineering"],
                                                                        "title": "Test Data Set",
                                                                        "geospatial:geographicCoverage": {
                                                                          "geospatial:country": "Albania",
                                                                          "geospatial:state": "AlbaniaState",
                                                                          "geospatial:city": "AlbaniaCity",
                                                                          "geospatial:otherGeographicCoverage": "CoverageOther"},
                                                                        "journal:journalVolumeIssue": {
                                                                          "journal:journalVolume": "2333.444",
                                                                          "journal:journalIssue": "Journal3.4",
                                                                          "journal:journalPubDate": "2021-10-10"},
                                                                        "citation:datasetContact": {
                                                                          "citation:datasetContactName": "Rashid, Muhammed",
                                                                          "citation:datasetContactAffiliation": "test Affiliation",
                                                                          "citation:datasetContactEmail": "test@test.com"},
                                                                        "author": [
                                                                          {"citation:authorName": "Steven, Jacob",
                                                                           "citation:authorAffiliation": "FZJ",
                                                                           "authorIdentifierScheme": "ORCID",
                                                                           "authorIdentifier": "1234-5678-9012-3456"},
                                                                          {"citation:authorName": "Leslie, Suzanne",
                                                                           "citation:authorAffiliation": "FZJ",
                                                                           "authorIdentifierScheme": "ISNI",
                                                                           "authorIdentifier": "4567-8901-2345-6789"}],
                                                                        "citation:dsDescription": [
                                                                          {
                                                                            "citation:dsDescriptionValue": "Description 1",
                                                                            "citation:dsDescriptionDate": "2020-11-10"},
                                                                          {
                                                                            "citation:dsDescriptionValue": "Description 2",
                                                                            "citation:dsDescriptionDate": "201-12-25"}],
                                                                        "@id": "https://doi.org/10.5072/FK2/JRRO5W",
                                                                        "@type": ["ore:Aggregation", "schema:Dataset"],
                                                                        "schema:version": "2.0",
                                                                        "schema:name": "Test Data Set",
                                                                        "schema:dateModified": "Mon Dec 11 14:53:50 UTC 2023",
                                                                        "schema:datePublished": "2023-12-05",
                                                                        "schema:creativeWorkStatus": "RELEASED",
                                                                        "schema:license": "http://creativecommons.org/publicdomain/zero/1.0",
                                                                        "dvcore:fileTermsOfAccess": {
                                                                          "dvcore:fileRequestAccess": True},
                                                                        "schema:includedInDataCatalog": "Root",
                                                                        "schema:isPartOf": {
                                                                          "schema:name": "newDataVerse3",
                                                                          "@id": "http://localhost:8080/dataverse/newDataVerse3",
                                                                          "schema:description": "newDS",
                                                                          "schema:isPartOf": {"schema:name": "Root",
                                                                                              "@id": "http://localhost:8080/dataverse/root",
                                                                                              "schema:description": "The root dataverse."}},
                                                                        "@context": {
                                                                          "astrophysics": "http://localhost:8080/schema/astrophysics#",
                                                                          "author": "http://purl.org/dc/terms/creator",
                                                                          "authorIdentifier": "http://purl.org/spar/datacite/AgentIdentifier",
                                                                          "authorIdentifierScheme": "http://purl.org/spar/datacite/AgentIdentifierScheme",
                                                                          "biomedical": "http://localhost:8080/schema/biomedical#",
                                                                          "citation": "https://dataverse.org/schema/citation/",
                                                                          "dcterms": "http://purl.org/dc/terms/",
                                                                          "dvcore": "https://dataverse.org/schema/core#",
                                                                          "geospatial": "http://localhost:8080/schema/geospatial#",
                                                                          "journal": "http://localhost:8080/schema/journal#",
                                                                          "language": "http://purl.org/dc/terms/language",
                                                                          "ore": "http://www.openarchives.org/ore/terms/",
                                                                          "otherReferences": "http://purl.org/dc/terms/references",
                                                                          "schema": "http://schema.org/",
                                                                          "socialscience": "http://localhost:8080/schema/socialscience#",
                                                                          "subject": "http://purl.org/dc/terms/subject",
                                                                          "title": "http://purl.org/dc/terms/title"}}}}
    info_future = Future()
    info_future.set_result(metadata_info)
    mocker.patch.object(dataverse_client_mock.http_client, 'get', side_effect=[info_future])
    result = await dataverse_client_mock.get_dataset_metadata_block("test_id", "version")
    assert result == metadata_info.get("result").get("data"), "Not expected result!"
    dataverse_client_mock.logger.info.assert_called_with("Fetching Metadata-block for dataset: %s for server: %s",
                                                         "test_id", dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_with(
      f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/versions/version/metadata?persistentId=test_id",
      request_params={'Accept': 'application/json'},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_get_dataset_metadata_block_when_fails_returns_error(self, mocker,
                                                                     dataverse_client_mock: dataverse_client_mock):
    metadata_error_info = {"status": 404, "reason": "Not Found",
                           "result": {"status": "ERROR",
                                      "message": "Dataset with Persistent ID doi:10.5072/FK2/JRRO5W3 not found."}}

    info_future = Future()
    info_future.set_result(metadata_error_info)
    mocker.patch.object(dataverse_client_mock.http_client, 'get', side_effect=[info_future])
    result = await dataverse_client_mock.get_dataset_metadata_block("test_id", "version")
    error = (f"Error fetching metadata block for dataset: test_id "
             f"on server: {dataverse_client_mock.server_url}, "
             f"Reason: {metadata_error_info['reason']}, "
             f"Info: {metadata_error_info['result']}")
    assert result == error, "Not expected result!"
    dataverse_client_mock.logger.info.assert_called_with("Fetching Metadata-block for dataset: %s for server: %s",
                                                         "test_id", dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_with(
      f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/versions/version/metadata?persistentId=test_id",
      request_params={'Accept': 'application/json'},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})
    dataverse_client_mock.logger.error.assert_called_once_with(error)

  @pytest.mark.asyncio
  async def test_get_dataset_metadata_block_when_request_fails_returns_error(self, mocker,
                                                                             dataverse_client_mock: dataverse_client_mock):
    info_future = Future()
    info_future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'get', side_effect=[info_future])
    dataverse_client_mock.http_client.session_request_errors = [
      "ClientConnectorError for url (url) with error: Cannot connect to host localhost:8080 ssl:default [Connect call failed ('127.0.0.1', 8080)]"]
    result = await dataverse_client_mock.get_dataset_metadata_block("test_id", "version")
    assert result == dataverse_client_mock.http_client.session_request_errors, "Not expected result!"
    dataverse_client_mock.logger.info.assert_called_with("Fetching Metadata-block for dataset: %s for server: %s",
                                                         "test_id", dataverse_client_mock.server_url)
    dataverse_client_mock.http_client.get.assert_called_with(
      f"{dataverse_client_mock.server_url}/api/datasets/:persistentId/versions/version/metadata?persistentId=test_id",
      request_params={'Accept': 'application/json'},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  async def test_delete_non_empty_dataverse_when_succeeds_returns_expected(self, mocker,
                                                                           dataverse_client_mock: dataverse_client_mock):
    delete_info = {"status": 200, "reason": "OK",
                   "result": {"status": "OK", "data": {"message": "Dataverse dv_test deleted"}}}
    delete_future = Future()
    delete_future.set_result(delete_info)
    mocker.patch.object(dataverse_client_mock.http_client, 'delete', side_effect=[delete_future])
    result = await dataverse_client_mock.delete_empty_dataverse("dv_test")
    assert result == delete_info.get("result").get("data").get("message"), "Not expected result!"
    dataverse_client_mock.logger.info.assert_called_with("Deleting empty dataverse, Server: %s, identifier: %s",
                                                         dataverse_client_mock.server_url, "dv_test")
    (dataverse_client_mock.http_client.delete.assert_called_with(
      f"{dataverse_client_mock.server_url}/api/dataverses/dv_test",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token}))

  @pytest.mark.asyncio
  async def test_delete_non_empty_dataverse_when_fails_returns_error(self, mocker,
                                                                     dataverse_client_mock: dataverse_client_mock):
    delete_info_error = {"status": 404, "reason": "Not Found",
                         "result": {"status": "ERROR",
                                    "message": "Can't find dataverse with identifier='dataverse12344'"}}
    delete_future = Future()
    delete_future.set_result(delete_info_error)
    mocker.patch.object(dataverse_client_mock.http_client, 'delete', side_effect=[delete_future])
    result = await dataverse_client_mock.delete_empty_dataverse("dv_test")
    error = (f"Error deleting dataverse, "
             f"Id: dv_test, on server: {dataverse_client_mock.server_url}, "
             f"Reason: {delete_info_error['reason']}, "
             f"Info: {delete_info_error['result']}")
    assert result == error, "Not expected result!"
    dataverse_client_mock.logger.info.assert_called_with("Deleting empty dataverse, Server: %s, identifier: %s",
                                                         dataverse_client_mock.server_url, "dv_test")
    dataverse_client_mock.http_client.delete.assert_called_with(
      f"{dataverse_client_mock.server_url}/api/dataverses/dv_test",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})
    dataverse_client_mock.logger.error.assert_called_with(error)

  @pytest.mark.asyncio
  async def test_delete_non_empty_dataverse_when_request_fails_returns_error(self, mocker,
                                                                             dataverse_client_mock: dataverse_client_mock):
    info_future = Future()
    info_future.set_result({})
    mocker.patch.object(dataverse_client_mock.http_client, 'delete', side_effect=[info_future])
    dataverse_client_mock.http_client.session_request_errors = [
      "ClientConnectorError for url (url) with error: Cannot connect to host localhost:8080 ssl:default [Connect call failed ('127.0.0.1', 8080)]"]
    result = await dataverse_client_mock.delete_empty_dataverse("dv_test")
    assert result == dataverse_client_mock.http_client.session_request_errors, "Not expected result!"
    dataverse_client_mock.logger.info.assert_called_with("Deleting empty dataverse, Server: %s, identifier: %s",
                                                         dataverse_client_mock.server_url, "dv_test")
    dataverse_client_mock.http_client.delete.assert_called_with(
      f"{dataverse_client_mock.server_url}/api/dataverses/dv_test",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})

  @pytest.mark.asyncio
  @pytest.mark.parametrize("server_url, api_token, response_status, response_body, expected_result, test_id",
                           [  # Success path tests with various realistic test values
                             ("https://test-dataverse.org", "valid-token", 200, {"status": "OK"}, True,
                              "success-path-valid"),
                             ("https://prod-dataverse.org", "another-valid-token", 200, {"status": "OK"}, True,
                              "success-path-another-valid"),

                             # Edge cases
                             ("https://edge-case-dataverse.org", "", 401, {"status": "OK"}, False,
                              "edge-case-empty-token"),
                             ("https://edge-case-dataverse.org", "valid-token", None, {}, False, "edge-case-no-status"),

                             # Error cases
                             ("https://error-dataverse.org", "invalid-token", 401, {"status": "Unauthorized"}, False,
                              "error-case-unauthorized"),
                             ("https://error-dataverse.org", "forbidden-token", 403, {"status": "Forbidden"}, False,
                              "error-case-forbidden"), (
                               "https://error-dataverse.org", "valid-token", 500, {"status": "Server Error"}, False,
                               "error-case-server-error"), ], )
  async def test_check_if_api_token_is_valid(self, mocker, dataverse_client_mock: dataverse_client_mock, server_url,
                                             api_token, response_status, response_body, expected_result, test_id):
    # Arrange
    mocker.patch.object(dataverse_client_mock, 'server_url', server_url)
    mocker.patch.object(dataverse_client_mock, 'api_token', api_token)

    # Mocking the get method of http_client to return a response with specified status and body
    info_future = Future()
    info_future.set_result({"status": response_status, "body": response_body})
    mocker.patch.object(dataverse_client_mock.http_client, 'get', side_effect=[info_future])

    # Act
    result = await dataverse_client_mock.check_if_api_token_is_valid()

    # Assert
    assert result == expected_result
    dataverse_client_mock.logger.info.assert_called_with("Check if API token is valid, Server: %s", server_url)
    dataverse_client_mock.http_client.get.assert_called_once_with(f"{server_url}/api/users/token",
                                                                  request_headers={'Accept': 'application/json',
                                                                                   'X-Dataverse-key': api_token})

  @pytest.mark.asyncio
  @pytest.mark.parametrize("ds_persistent_id, mock_response, expected_result, test_id", [
    ("valid_id_1", {"status": 200, "reason": "OK", "result": {"data": {"lock1": "data1"}}},
     {'locks': {"lock1": "data1"}}, "success_path_1"),
    ("valid_id_2", {"status": 200, "reason": "OK", "result": {"data": {}}}, {'locks': {}}, "success_path_2"),
    ("invalid_id_1", {"status": 404, "reason": "Not Found", "result": "Dataset not found"},
     "Error fetching locks for dataset: invalid_id_1 on server: test_server, Reason: Not Found, Info: Dataset not found",
     "error_case_1"),
    ("invalid_id_2", None, "Session request error", "error_case_2")
    # Assuming session_request_errors is a string for simplicity
  ], ids=["success_path_1", "success_path_2", "error_case_1", "error_case_2"])
  async def test_get_dataset_locks(self, mocker, dataverse_client_mock: dataverse_client_mock, ds_persistent_id,
                                   mock_response, expected_result, test_id):
    # Arrange
    dataverse_client_mock.server_url = "test_server"
    dataverse_client_mock.api_token = "test_token"
    dataverse_client_mock.http_client = mocker.AsyncMock()
    dataverse_client_mock.http_client.get.return_value = mock_response
    dataverse_client_mock.http_client.session_request_errors = "Session request error" if mock_response is None else None

    # Act
    result = await dataverse_client_mock.get_dataset_locks(ds_persistent_id)

    # Assert
    dataverse_client_mock.logger.info("Fetching locks for dataset: %s for server: %s", ds_persistent_id,
                                      "test_server")
    assert result == expected_result
    if mock_response and mock_response["status"] == 200:
      dataverse_client_mock.logger.info.assert_called()
    if mock_response and mock_response["status"] != 200:
      dataverse_client_mock.logger.error.assert_called()

  @pytest.mark.asyncio
  @pytest.mark.parametrize("ds_persistent_id, server_url, api_token, response, expected", [
    # Success path tests
    ("ds001", "http://testserver.com", "testtoken",
     {"status": 200, "reason": "OK", "result": {"data": {"message": "Dataset deleted successfully"}}},
     "Dataset deleted successfully"),
    # Edge cases
    ("", "http://testserver.com", "testtoken",
     {"status": 200, "reason": "OK", "result": {"data": {"message": "Dataset deleted successfully"}}},
     "Dataset deleted successfully"),
    # Error cases
    ("ds002", "http://testserver.com", "testtoken",
     {"status": 403, "reason": "Forbidden", "result": "User needs to be superuser"},
     "Error deleting dataset, Server: http://testserver.com, Id: ds002, Reason: Forbidden, Info: User needs to be superuser"),
    ("invalid", "invalid", "invalid", None, ["Invalid server url or api token"]),
  ], ids=["success-path", "edge-case-empty-id", "error-forbidden", "error-invalid-input"])
  async def test_delete_published_dataset(self, mocker, dataverse_client_mock: dataverse_client_mock, ds_persistent_id,
                                          server_url, api_token, response, expected):
    # Arrange
    dataverse_client_mock.server_url = server_url
    dataverse_client_mock.api_token = api_token
    dataverse_client_mock.http_client.delete = mocker.AsyncMock(return_value=response)
    dataverse_client_mock.logger = mocker.AsyncMock()
    dataverse_client_mock.http_client.session_request_errors = [
      "Invalid server url or api token"] if response is None else None

    # Act
    result = await dataverse_client_mock.delete_published_dataset(ds_persistent_id)

    # Assert
    dataverse_client_mock.logger.info.assert_called_with("Deleting published dataset, Server: %s, Dataset: %s",
                                                         server_url,
                                                         ds_persistent_id)
    assert result == expected
    if response and response["status"] == 200:
      dataverse_client_mock.logger.info.assert_called()
    if response and response["status"] != 200:
      dataverse_client_mock.logger.error.assert_called()

  # @pytest.mark.asyncio
  # @pytest.mark.parametrize("dv_identifier, contents, delete_response, expected", [
  #     # Happy path tests
  #     ("dv123", [{"type": "dataset", "protocol": "doi", "authority": "10.1234", "identifier": "xyz123"}], {"status": 200, "reason": "OK", "result": {"data": {"message": "Dataverse deleted successfully"}}}, "Dataverse deleted successfully"),
  #     ("dv456", [{"type": "dataverse", "id": "dv789"}], {"status": 200, "reason": "OK", "result": {"data": {"message": "Dataverse deleted successfully"}}}, "Dataverse deleted successfully"),
  #     # Edge case: Empty dataverse
  #     ("dvEmpty", [], {"status": 200, "reason": "OK", "result": {"data": {"message": "Dataverse deleted successfully"}}}, "Dataverse deleted successfully"),
  #     # Error cases
  #     ("dvError", [{"type": "unknown"}], {"status": 400, "reason": "Bad Request", "result": "Error deleting dataverse"}, "Error deleting dataverse, Id: dvError, Reason: Bad Request, Info: Error deleting dataverse"),
  # ], ids=["success-path-dataset", "success-path-dataverse", "edge-case-empty", "error-unknown-type"])
  # async def test_delete_non_empty_dataverse(self, mocker, dataverse_client_mock: dataverse_client_mock, dv_identifier, contents, delete_response, expected):
  #     # Arrange
  #     dataverse_client_mock.get_dataverse_contents = mocker.AsyncMock(return_value=contents)
  #     dataverse_client_mock.delete_published_dataset = mocker.AsyncMock()
  #     dataverse_client_mock.http_client.delete = mocker.AsyncMock(return_value=delete_response)
  #
  #     # Act
  #     result = await dataverse_client_mock.delete_non_empty_dataverse(dv_identifier)
  #
  #     # Assert
  #     assert result == expected
  #     dataverse_client_mock.get_dataverse_contents.assert_awaited_with(dv_identifier)
  #     if contents and contents[0].get("type") == "dataset":
  #         dataverse_client_mock.delete_published_dataset.assert_awaited()
  #     elif contents and contents[0].get("type") == "dataverse":
  #         dataverse_client_mock.delete_non_empty_dataverse.assert_awaited()
  #     dataverse_client_mock.http_client.delete.assert_awaited_with(f"{dataverse_client_mock.server_url}/api/dataverses/{dv_identifier}", request_headers={'Accept': 'application/json', 'X-Dataverse-key': dataverse_client_mock.api_token})
