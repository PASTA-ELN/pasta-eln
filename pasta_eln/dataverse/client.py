""" Client for communicating with Dataverse Server via REST API """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: client.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from datetime import datetime
from json import dumps, load
from os import getcwd
from os.path import basename, dirname, join, realpath
from typing import Any
from xml.etree.ElementTree import ElementTree, fromstring

from aiohttp import BasicAuth, FormData

from pasta_eln.utils import handle_dataverse_exception_async
from pasta_eln.webclient.http_client import AsyncHttpClient


class DataverseClient:
  """
  Client for communicating with Dataverse Server via REST API
  """

  def __init__(self,
               server_url: str,
               api_token: str, ) -> None:
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.api_token = api_token
    self.server_url = server_url
    self.http_client = AsyncHttpClient(5)

  @handle_dataverse_exception_async
  async def check_if_token_expired(self) -> bool:
    """
    Check if the API token has expired
    Returns:
      True if the token has expired, False otherwise
    """
    self.logger.info("Checking token expiry, Server: %s", self.server_url)
    resp = await self.http_client.get(
      f"{self.server_url}/api/users/token",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': self.api_token})
    if not resp and self.http_client.session_request_errors:
      return False
    if resp["status"] == 200 and resp["reason"] == 'OK':
      expiry_message = resp["result"].get('data').get('message')
      expiry_time_string = expiry_message.replace(f"Token {self.api_token} expires on ", '')
      expiry_time = datetime.strptime(expiry_time_string, '%Y-%m-%d %H:%M:%S.%f')
      return expiry_time < datetime.now()
    error = (f"Error checking token expiration, Server: "
             f"{self.server_url}, Reason: {resp['reason']}, Info: {resp['result']}")
    self.logger.error(error)
    return False

  @handle_dataverse_exception_async
  async def recreate_api_token(self) -> str | Any:
    """
    Recreates the API token using existing token.

    Returns:
        str | Any: The new API token or any error message if the token recreation fails.
    """
    self.logger.info("Recreate token, Server: %s", self.server_url)
    resp = await self.http_client.post(
      f"{self.server_url}/api/users/token/recreate",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': self.api_token})
    if not resp and self.http_client.session_request_errors:
      return self.http_client.session_request_errors
    if resp["status"] == 200 and resp["reason"] == 'OK':
      token_message = resp["result"].get('data').get('message')
      return token_message.replace("New token for dataverseAdmin is ", '')
    error = (f"Error recreating the token, Server: {self.server_url}, "
             f"Reason: {resp['reason']}, Info: {resp['result']}")
    self.logger.error(error)
    return error

  @handle_dataverse_exception_async
  async def create_and_publish_dataverse(self,
                                         dv_parent: str,
                                         dv_name: str,
                                         dv_description: str,
                                         dv_alias: str,
                                         dv_contact_email_list: list[dict[str, str]],
                                         dv_affiliation: str,
                                         dv_type: str) -> dict[Any, Any] | Any:
    """
    Creates and publishes a dataverse
    Args:
      dv_parent (str): The name of the parent dataverse
      dv_name (str): The name of the dataverse
      dv_description (str): The description of the dataverse
      dv_alias (str): The alias of the dataverse
      dv_contact_email_list (list[dict[str, str]]): The list of contact emails which must be provided in the following format:
        [{"contactEmail": "example1@example.edu"}, {"contactEmail": "example2@example.edu"}]
      dv_affiliation (str): The affiliation of the dataverse
      dv_type (str): The type of the dataverse which must be one of the following:
        DEPARTMENT
        JOURNALS
        LABORATORY
        ORGANIZATIONS_INSTITUTIONS
        RESEARCHERS
        RESEARCH_GROUP
        RESEARCH_PROJECTS
        TEACHING_COURSES
        UNCATEGORIZED

    Returns(dict[Any, Any] | Any):
      A dictionary representing the created and published dataverse, or an error message.
    """

    dv_json = {
      "name": dv_name,
      "alias": dv_alias,
      "dataverseContacts": dv_contact_email_list,
      "affiliation": dv_affiliation,
      "description": dv_description,
      "dataverseType": dv_type
    }

    self.logger.info("Creating dataverse, Server: %s Alias: %s", self.server_url, dv_alias)
    # Create the data-verse
    resp = await self.http_client.post(
      f"{self.server_url}/api/dataverses/{dv_parent}",
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token},
      data=dumps(dv_json))
    if not resp and self.http_client.session_request_errors:
      return self.http_client.session_request_errors
    if resp["status"] == 201 and resp["reason"] == 'Created':  # Success
      pub_resp = await self.http_client.post(
        f"{self.server_url}/api/dataverses/{resp['result'].get('data').get('alias')}/actions/:publish",
        request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token})
      if not pub_resp and self.http_client.session_request_errors:
        return self.http_client.session_request_errors
      if pub_resp["status"] == 200 and pub_resp["reason"] == 'OK':
        return pub_resp["result"].get('data')
      error = (f"Error publishing dataverse, "
               f"Server: {self.server_url}, "
               f"Status: {pub_resp['status']}, "
               f"Reason: {pub_resp['reason']}, "
               f"Info: {pub_resp['result'].get('message')}")
      self.logger.error(error)
      return error
    error = (f"Error creating dataverse, "
             f"Server: {self.server_url}, "
             f"Status: {resp['status']}, "
             f"Reason: {resp['reason']}, "
             f"Info: {resp['result'].get('message')}")
    self.logger.error(error)
    return error

  @handle_dataverse_exception_async
  async def check_if_dataverse_server_reachable(self) -> tuple[bool, Any]:
    """
    Checks if the data-verse server is reachable
    Returns (tuple(bool, Any)):
      A tuple of (is_reachable, a message) is returned
    """
    self.logger.info("Check if data-verse is reachable, Server: %s", self.server_url)
    resp = await self.http_client.get(
      f"{self.server_url}/api/info/version",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': self.api_token})
    if not resp and self.http_client.session_request_errors:
      return False, self.http_client.session_request_errors
    is_reachable = (resp["status"] == 200
                    and resp["reason"] == 'OK'
                    and resp["result"].get('data').get('version') is not None)
    return (is_reachable, "Dataverse is reachable") \
      if is_reachable \
      else (is_reachable,
            f"Dataverse isn't reachable, "
            f"Server: {self.server_url}, "
            f"Status: {resp['status']}, "
            f"Reason: {resp['reason']}, "
            f"Info: {resp['result'].get('message')}")

  @handle_dataverse_exception_async
  async def get_dataverse_list(self) -> dict[Any, Any] | Any:
    """
    Gets the list of data verses
    Returns:
      A dictionary of dataverses (identifier & title) for successful request, otherwise the error message is returned.
    """
    self.logger.info("Getting dataverse list for server: %s", self.server_url)
    resp: dict[str, Any] = await self.http_client.get(
      f"{self.server_url}/dvn/api/data-deposit/v1.1/swordv2/service-document",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': self.api_token},
      auth=BasicAuth(self.api_token, ''))
    if not resp and self.http_client.session_request_errors:
      return self.http_client.session_request_errors
    if resp["status"] == 200 and resp["reason"] == "OK":
      element_tree: ElementTree = ElementTree(fromstring(resp["result"]))
      dataverse_list: list[dict[str, str]] = []
      for element in element_tree.getroot().findall(
          ".//{http://www.w3.org/2007/app}collection"):
        title = element.find(".//{http://www.w3.org/2005/Atom}title")
        if title is not None:
          title_val = title.text if title.text is not None else ""
          dataverse_list.append(
            {
              "id": element.attrib["href"].split('/')[-1],
              "title": title_val
            }
          )
      dataverse_list.sort(key=lambda x: x['title'])
      return dataverse_list
    error = (f"Error getting dataverse list, "
             f"Server: {self.server_url}, "
             f"Status: {resp['status']}, "
             f"Reason: {resp['reason']}, "
             f"Info: {resp['result']}")
    self.logger.error(error)
    return error

  @handle_dataverse_exception_async
  async def get_dataverse_contents(self,
                                   identifier: str) -> dict[Any, Any] | Any:
    """
    Retrieves the contents of a dataverse.
    Args:
      identifier (str): The identifier of the dataverse

    Returns (dict[Any, Any] | Any):
      A dictionary of dataverse contents for successful request, otherwise the error message is returned.
    """
    self.logger.info("Retrieving dataverse contents, Server: %s, Dataverse identifier: %s", self.server_url,
                     identifier)
    resp = await self.http_client.get(
      f"{self.server_url}/api/dataverses/{identifier}/contents",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': self.api_token})
    if not resp and self.http_client.session_request_errors:
      return self.http_client.session_request_errors
    if resp["status"] == 200 and resp["reason"] == 'OK':
      return resp["result"].get("data")
    error = (f"Error retrieving the contents for data verse, "
             f"Id: {identifier}, "
             f"Reason: {resp['reason']}, "
             f"Info: {resp['result']}")
    self.logger.error(error)
    return error

  @handle_dataverse_exception_async
  async def get_dataverse_size(self,
                               identifier: str) -> str | Any:
    """
    Retrieves the size of a dataverse.
    Args:
      identifier (str): The identifier of the dataverse

    Returns (str):
      Dataverse size in bytes for successful request, otherwise the error message is returned.
    """
    self.logger.info("Retrieving dataverse size, Server: %s, Dataverse identifier: %s", self.server_url, identifier)
    resp = await self.http_client.get(
      f"{self.server_url}/api/dataverses/{identifier}/storagesize",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': self.api_token})
    if not resp and self.http_client.session_request_errors:
      return self.http_client.session_request_errors
    if resp["status"] == 200 and resp["reason"] == 'OK':
      return (resp["result"]
              .get("data")
              .get("message")
              .replace("Total size of the files stored in this dataverse: ", ""))
    error = (f"Error retrieving the size for data verse, "
             f"Id: {identifier}, "
             f"Reason: {resp['reason']}, "
             f"Info: {resp['result']}")
    self.logger.error(error)
    return error

  @handle_dataverse_exception_async
  async def create_and_publish_dataset(self,
                                       parent_dataverse_id: str,
                                       ds_metadata: dict[str, Any],
                                       ds_validate_metadata: bool = False
                                       ) -> dict[Any, Any] | Any:
    """
    Creates and publishes a dataset to the parent dataverse.
    Args:
      parent_dataverse_id (str): The identifier of the parent dataverse.
      ds_metadata (dict[str, Any]): The dataset metadata.
        Refer the https://guides.dataverse.org/en/latest/_downloads/4e04c8120d51efab20e480c6427f139c/dataset-create-new-all-default-fields.json for the default values to be used in the metadata.
        The type names to be used in the metadata along with the values can be found in the metadata blocks and should correspond to the dataset-create-new-all-default-fields.json.
      ds_validate_metadata (bool): Whether to validate the metadata.

    Returns:
      A dictionary of dataset metadata with the persistent identifier for successful request, otherwise the error message is returned.
    """
    self.logger.info("Creating dataset, Alias: %s on server: %s", ds_metadata["title"], self.server_url)
    current_path = realpath(join(getcwd(), dirname(__file__)))
    with open(join(current_path, "dataset-create-new-all-default-fields.json"), encoding="utf-8") as config_file:
      metadata = load(config_file)
      if 'license' in ds_metadata:
        metadata['datasetVersion']['license'] = ds_metadata['license']
      else:
        del metadata['datasetVersion']['license']
      for _, metablock in metadata['datasetVersion']['metadataBlocks'].items():
        field_copy = metablock['fields'].copy()
        del metablock['displayName']
        metablock['fields'].clear()
        for field in field_copy:
          if field['typeName'] in ds_metadata:
            field['value'] = ds_metadata[field['typeName']]
            metablock['fields'].append(field)
      # Request to create the dataset
      resp = await self.http_client.post(
        f"{self.server_url}/api/dataverses/{parent_dataverse_id}/datasets",
        request_params={'doNotValidate': str(not ds_validate_metadata)},
        request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token},
        json=metadata)
      if not resp and self.http_client.session_request_errors:
        return self.http_client.session_request_errors
      if resp["status"] == 201 and resp["reason"] == 'Created':
        # Request to publish the dataset
        resp = await self.http_client.post(
          f"{self.server_url}/api/datasets/:persistentId/actions/:publish",
          request_params={'persistentId': resp["result"].get('data').get('persistentId'), 'type': 'major'},
          request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token})
        if not resp and self.http_client.session_request_errors:
          return self.http_client.session_request_errors
        if resp["status"] == 200 and resp["reason"] == 'OK':
          return resp.get("result").get("data")
        error = (f"Error publishing dataset, "
                 f"Alias: {ds_metadata['title']}, "
                 f"Server: {self.server_url},  "
                 f"Reason: {resp['reason']}, "
                 f"Info: {resp['result']}")
        self.logger.error(error)
        return error
      error = (f"Error creating dataset, "
               f"Alias: {ds_metadata['title']}, "
               f"Server: {self.server_url},  "
               f"Reason: {resp['reason']}, "
               f"Info: {resp['result']}")
      self.logger.error(error)
      return error

  @handle_dataverse_exception_async
  async def upload_file(self,
                        ds_pid: str,
                        df_file_path: str,
                        df_description: str,
                        df_categories: list[str]
                        ) -> dict[Any, Any] | Any:
    """
    Uploads a file to a dataset.
    Args:
      ds_pid (str): The identifier of the dataset.
      df_file_path (str): The absolute path to the file to be uploaded.
      df_description (str): The description of the file.
      df_categories (list[str]): The categories/tags for the file.

    Returns:
      {
          'file_upload_result': file_upload_response,
          'dataset_publish_result': dataset_publish_response
      } for successful request, otherwise the error message is returned.
    """

    self.logger.info("Uploading file: %s to Dataset: %s on server: %s",
                     df_file_path,
                     ds_pid,
                     self.server_url)
    filename = basename(df_file_path)
    metadata = dumps({"description": df_description, "categories": df_categories})
    data = FormData()
    with open(df_file_path, 'rb') as file_stream:
      data.add_field('file',
                     file_stream,
                     filename=filename,
                     content_type='multipart/form-data')
      data.add_field('jsonData', metadata, content_type='application/json')
      # Request to add the file to dataset
      resp = await self.http_client.post(
        f"{self.server_url}/api/datasets/:persistentId/add",
        request_params={'persistentId': ds_pid},
        request_headers={'X-Dataverse-key': self.api_token},
        data=data,
        timeout=0)
      if not resp and self.http_client.session_request_errors:
        return self.http_client.session_request_errors
      if resp["status"] == 200 and resp["reason"] == 'OK':
        # Request to publish the dataset
        pub_resp = await self.http_client.post(
          f"{self.server_url}/api/datasets/:persistentId/actions/:publish",
          request_params={'persistentId': ds_pid, 'type': 'major'},
          request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token})
        if not pub_resp and self.http_client.session_request_errors:
          return self.http_client.session_request_errors
        if pub_resp["status"] == 200 and pub_resp["reason"] == 'OK':
          return {
            'file_upload_result': resp.get('result').get('data'),
            'dataset_publish_result': pub_resp.get('result').get('data')
          }
        error = (f"Error publishing dataset: {ds_pid} "
                 f"as part of file ({df_file_path}) upload on server: {self.server_url}, "
                 f"Reason: {pub_resp['reason']}, "
                 f"Info: {pub_resp['result']}")
        self.logger.error(error)
        return error
      error = (f"Error uploading file: {df_file_path} "
               f"to dataset: {ds_pid} "
               f"on server: {self.server_url}, "
               f"Reason: {resp['reason']}, "
               f"Info: {resp['result']}")
      self.logger.error(error)
      return error

  @handle_dataverse_exception_async
  async def get_dataset_info_json(self,
                                  ds_persistent_id: str,
                                  version: str = ":latest-published") -> dict[Any, Any] | Any:
    """
    Fetch JSON representation of a dataset.
    Args:
      ds_persistent_id (str): The identifier of the dataset.
      version (str): The version of the dataset.
        Note dataset versions can be referred to as:
          :draft the draft version, if any
          :latest either a draft (if exists) or the latest published version.
          :latest-published the latest published version
          x.y a specific version, where x is the major version number and y is the minor version number.
          x same as x.0

    Returns:
      JSON representation of the dataset for successful request, otherwise the error message is returned.
    """
    self.logger.info("Fetching JSON representation of a dataset: %s for server: %s", ds_persistent_id,
                     self.server_url)
    resp = await self.http_client.get(
      f"{self.server_url}/api/datasets/:persistentId/versions/{version}?persistentId={ds_persistent_id}",
      request_params={'Accept': 'application/json'},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token})
    if not resp and self.http_client.session_request_errors:
      return self.http_client.session_request_errors
    if resp["status"] == 200 and resp["reason"] == 'OK':
      return resp.get('result').get('data')
    error = (f"Error fetching JSON representation of dataset: {ds_persistent_id} "
             f"on server: {self.server_url}, "
             f"Reason: {resp['reason']}, "
             f"Info: {resp['result']}")
    self.logger.error(error)
    return error

  @handle_dataverse_exception_async
  async def get_dataset_versions(self,
                                 ds_persistent_id: str) -> dict[Any, Any] | Any:
    """
    Fetch the version list for dataset.
    Args:
      ds_persistent_id (str): The identifier of the dataset.

    Returns:
      Version list for the dataset for successful request, otherwise the error message is returned.
    """
    self.logger.info("Fetching version list for dataset: %s for server: %s", ds_persistent_id,
                     self.server_url)
    resp = await self.http_client.get(
      f"{self.server_url}/api/datasets/:persistentId/versions?persistentId={ds_persistent_id}",
      request_params={'Accept': 'application/json'},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token})
    if not resp and self.http_client.session_request_errors:
      return self.http_client.session_request_errors
    if resp["status"] == 200 and resp["reason"] == 'OK':
      return resp.get('result').get('data')
    error = (f"Error fetching version list for dataset: {ds_persistent_id} "
             f"on server: {self.server_url}, "
             f"Reason: {resp['reason']}, "
             f"Info: {resp['result']}")
    self.logger.error(error)
    return error

  @handle_dataverse_exception_async
  async def get_dataset_files(self,
                              ds_persistent_id: str,
                              version: str = ":latest-published") -> dict[Any, Any] | Any:
    """
    Fetch the file list for dataset.
    Args:
      ds_persistent_id (str): The identifier of the dataset.
      version (str): The version of the dataset.
        Note dataset versions can be referred to as:
          :draft the draft version, if any
          :latest either a draft (if exists) or the latest published version.
          :latest-published the latest published version
          x.y a specific version, where x is the major version number and y is the minor version number.
          x same as x.0

    Returns:
      File list for the dataset for successful request, otherwise the error message is returned.
    """
    self.logger.info("Fetching file list for dataset: %s for server: %s",
                     ds_persistent_id,
                     self.server_url)
    resp = await self.http_client.get(
      f"{self.server_url}/api/datasets/:persistentId/versions/{version}/files?persistentId={ds_persistent_id}",
      request_params={'Accept': 'application/json'},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token})
    if not resp and self.http_client.session_request_errors:
      return self.http_client.session_request_errors
    if resp["status"] == 200 and resp["reason"] == 'OK':
      return resp.get('result').get('data')
    error = (f"Error fetching file list for dataset: {ds_persistent_id} "
             f"on server: {self.server_url}, "
             f"Reason: {resp['reason']}, "
             f"Info: {resp['result']}")
    self.logger.error(error)
    return error

  @handle_dataverse_exception_async
  async def get_dataset_metadata_block(self,
                                       ds_persistent_id: str,
                                       version: str = ":latest-published") -> dict[Any, Any] | Any:
    """
    Fetch the metadata block for dataset.
    Args:
      ds_persistent_id (str): The identifier of the dataset.
      version (str): The version of the dataset.
        Note dataset versions can be referred to as:
          :draft the draft version, if any
          :latest either a draft (if exists) or the latest published version.
          :latest-published the latest published version
          x.y a specific version, where x is the major version number and y is the minor version number.
          x same as x.0

    Returns:
      Metadata block for the dataset for successful request, otherwise the error message is returned.
    """
    self.logger.info("Fetching Metadata-block for dataset: %s for server: %s",
                     ds_persistent_id,
                     self.server_url)
    resp = await self.http_client.get(
      f"{self.server_url}/api/datasets/:persistentId/versions/{version}/metadata?persistentId={ds_persistent_id}",
      request_params={'Accept': 'application/json'},
      request_headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token})
    if not resp and self.http_client.session_request_errors:
      return self.http_client.session_request_errors
    if resp["status"] == 200 and resp["reason"] == 'OK':
      return resp.get('result').get('data')
    error = (f"Error fetching metadata block for dataset: {ds_persistent_id} "
             f"on server: {self.server_url}, "
             f"Reason: {resp['reason']}, "
             f"Info: {resp['result']}")
    self.logger.error(error)
    return error

  @handle_dataverse_exception_async
  async def delete_empty_dataverse(self,
                                   dv_identifier: str) -> str | Any:
    """
    Deletes an empty dataverse.
    Args:
      dv_identifier (str): The identifier of the dataverse.

    Returns:
      Message for successful request, otherwise the error message is returned.
    """
    self.logger.info("Deleting empty dataverse, Server: %s, identifier: %s",
                     self.server_url,
                     dv_identifier)
    resp = await self.http_client.delete(
      f"{self.server_url}/api/dataverses/{dv_identifier}",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': self.api_token})
    if not resp and self.http_client.session_request_errors:
      return self.http_client.session_request_errors
    if resp["status"] == 200 and resp["reason"] == 'OK':
      return resp.get("result").get("data").get("message")
    error = (f"Error deleting dataverse, "
             f"Id: {dv_identifier}, on server: {self.server_url}, "
             f"Reason: {resp['reason']}, "
             f"Info: {resp['result']}")
    self.logger.error(error)
    return error

  @handle_dataverse_exception_async
  async def delete_published_dataset(self,
                                     ds_persistent_id: str) -> str | Any:
    """
    Deletes a published dataset.
    Note: The method fails presently due to a bug in dataverse API.
          Every time the API returns 403 errors saying the user needs to be superuser.
    Args:
      ds_persistent_id (str): The identifier of the dataset.

    Returns:
      Message for successful request, otherwise the error message is returned.
    """
    self.logger.info("Deleting published dataset, Server: %s, Dataset: %s",
                     self.server_url,
                     ds_persistent_id)
    resp = await self.http_client.delete(
      f"{self.server_url}/api/datasets/:persistentId/destroy/",
      request_params={'persistentId': ds_persistent_id},
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': self.api_token})
    if not resp and self.http_client.session_request_errors:
      return self.http_client.session_request_errors
    if resp["status"] == 200 and resp["reason"] == 'OK':
      return resp["result"].get("data").get("message")
    error = (f"Error deleting dataset, "
             f"Server: {self.server_url}, "
             f"Id: {ds_persistent_id}, "
             f"Reason: {resp['reason']}, "
             f"Info: {resp['result']}")
    self.logger.error(error)
    return error

  @handle_dataverse_exception_async
  async def delete_non_empty_dataverse(self,
                                       dv_identifier: str) -> str | Any:
    """
    Deletes a non-empty dataverse.

    Note: The method fails presently due to a bug in dataverse API while invoking the delete_published_dataset method.
    Args:
      dv_identifier (str): The identifier of the dataverse.

    Returns:
      Message for successful request, otherwise the error message is returned.
    """
    self.logger.info("Deleting dataverse, Server: %s, Dataverse Id: %s",
                     self.server_url,
                     dv_identifier)
    contents = await self.get_dataverse_contents(dv_identifier)
    for content in contents:
      if content.get('type') == 'dataset':
        await self.delete_published_dataset(
          f"{content.get('protocol')}:{content.get('authority')}/{content.get('identifier')}")
      elif content.get('type') == 'dataverse':
        await self.delete_non_empty_dataverse(content.get('id'))
      else:
        self.logger.error("Unknown content type: %s "
                          "while deleting dataverse: %s on server: %s ",
                          content.type,
                          dv_identifier,
                          self.server_url)
    resp = await self.http_client.delete(
      f"{self.server_url}/api/dataverses/{dv_identifier}",
      request_headers={'Accept': 'application/json', 'X-Dataverse-key': self.api_token})
    if not resp and self.http_client.session_request_errors:
      return self.http_client.session_request_errors
    if resp["status"] == 200 and resp["reason"] == 'OK':
      return resp["result"].get("data").get("message")
    error = (f"Error deleting dataverse, "
             f"Id: {dv_identifier}, "
             f"Reason: {resp['reason']}, "
             f"Info: {resp['result']}")
    self.logger.error(error)
    return error
