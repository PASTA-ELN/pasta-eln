""" Client for communicating with Dataverse Server via REST API
- Author: Jithu Murugan, Steffen Brinckmann
"""
import logging
from datetime import datetime
from json import dumps
from os.path import basename
from typing import Any
from xml.etree.ElementTree import ElementTree, fromstring
# Dataverse: remember to always publish everything before using it!!
import requests
from requests.auth import HTTPBasicAuth
from .dataverseDefaultDict import DATAVERSE_METADATA
from .repository import RepositoryClient


class DataverseClient(RepositoryClient):
  """ Client for communicating with Dataverse Server via REST API """

  def __init__(self, server_url: str, api_token: str, identifier:str) -> None:
    """
    Initializes the client

    Args:
        server_url (str): The URL of the server
        api_token (str): The API token for authentication
        identifier (str): sub-dataverse, category; use '' for void
    """
    super().__init__(server_url, api_token)
    self.identifier = identifier
    self.headers = {'Accept': 'application/json', 'X-Dataverse-key': self.api_token}


  def recreateAPIKey(self) -> str | Any:
    """
    Recreates the API token using existing token

    Returns:
        str | Any: The new API token or any error message if the token recreation fails
    """
    resp = requests.post(f"{self.server_url}/api/users/token/recreate", headers=self.headers, timeout=10)
    if resp.status_code == 200:
      token_message = resp.json().get('data').get('message')
      return token_message.replace('New token for dataverseAdmin is ', '')
    return f"Error recreating the token, Info: {resp.text}"


  def checkServer(self) -> tuple[bool, str]:
    """
    Checks if the data-verse server is reachable

    Returns (tuple(bool, Any)):
      A tuple of (success, a message) is returned
    """
    resp = requests.get(f"{self.server_url}/api/info/version", headers={'Accept': 'application/json'}, timeout=10)
    success = (resp.status_code == 200 and resp.json().get('data').get('version') is not None)
    return (success, 'Dataverse is reachable') \
      if success \
      else (success, f"Cannot reach server: {self.server_url}, Status: {resp.status_code}, json: {resp.json()}")


  def checkAPIKey(self) -> bool:
    """
    Checks if the given API token is valid

    Explanation:
        This method checks if the provided API token is valid by making a request to the server
        It logs the server URL and sends a GET request to the token endpoint with the API token
        It returns True if the response is successful and the status code is not 401, 403, or 500

    Args:
        self: The instance of the class

    Returns:
        bool: True if the API token is valid, False otherwise
    """
    resp = requests.get(f"{self.server_url}/api/users/token", headers=self.headers, timeout=10)
    return (bool(resp) and resp.status_code is not None
            and resp.status_code not in [401, 403, 500])


  def checkAPIKeyExpired(self) -> bool:
    """
    Check if the API token has expired
    Returns:
      True if the token has expired, False otherwise
    """
    resp = requests.get(f"{self.server_url}/api/users/token", headers=self.headers, timeout=10)
    if resp.status_code == 200:
      expiry_message = resp.json().get('data').get('message')
      expiry_time_string = expiry_message.replace(f"Token {self.api_token} expires on ", '')
      expiry_time = datetime.strptime(expiry_time_string, '%Y-%m-%d %H:%M:%S.%f')
      return expiry_time < datetime.now()
    print(f"Error checking token expiration, Info: {resp.text}")
    return False


  ################ DATAVERSE #######################
  def createDataverse(self, dv_parent: str, dv_name: str, dv_description: str, dv_alias: str,
                      dv_contact_email_list: list[dict[str, str]], dv_affiliation: str, dv_type: str) -> dict[Any, Any] | Any:
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
      A dictionary representing the created and published dataverse, or an error message
    """
    dv_json = {
      'name': dv_name,
      'alias': dv_alias,
      'dataverseContacts': dv_contact_email_list,
      'affiliation': dv_affiliation,
      'description': dv_description,
      'dataverseType': dv_type
    }
    # Create the data-verse
    resp = requests.post(f"{self.server_url}/api/dataverses/{dv_parent}",
      headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token},
      data=dumps(dv_json), timeout=10)
    if resp.status_code == 201:                                                                      # Success
      pub_resp = requests.post(f"{self.server_url}/api/dataverses/{resp.json().get('data').get('alias')}/actions/:publish",
        headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token}, timeout=10)
      if pub_resp.status_code == 200:
        return pub_resp.json().get('data')
      return f"Error publishing dataverse, Status: {pub_resp.status_code}, Info: {pub_resp.text}"
    return f"Error creating dataverse, Status: {resp.status_code}, Info: {resp.text}"


  def getDataverseList(self) -> dict[Any, Any] | Any:
    """
    Gets the list of data verses
    Returns:
      A dictionary of dataverses (identifier & title) for successful request,
      otherwise the error message is returned
    """
    resp = requests.get(f"{self.server_url}/dvn/api/data-deposit/v1.1/swordv2/service-document",
      headers={'Accept': 'application/json', 'X-Dataverse-key': self.api_token},
      auth=HTTPBasicAuth(self.api_token, ''), timeout=10)
    if resp.status_code == 200:
      element_tree: ElementTree = ElementTree(fromstring(resp.text))
      dataverse_list: list[dict[str, str]] = []
      root = element_tree.getroot()
      if root is not None:
        for element in root.findall('.//{http://www.w3.org/2007/app}collection'):
          title = element.find('.//{http://www.w3.org/2005/Atom}title')
          if title is not None:
            title_val = title.text if title.text is not None else ''
            dataverse_list.append({'id': element.attrib['href'].split('/')[-1],'title': title_val})
        dataverse_list.sort(key=lambda x: x['title'])
        return dataverse_list
    return f"Error get dataverse list, Server:{self.server_url},  Status:{resp.status_code}"


  def getDataverseContent(self) -> dict[Any, Any] | Any:
    """
    Retrieves the contents of a dataverse

    Returns (dict[Any, Any] | Any):
      A dictionary of dataverse contents for successful request, otherwise the error message is returned
    """
    resp = requests.get(f"{self.server_url}/api/dataverses/{self.identifier}/contents", headers=self.headers,
                        timeout=10)
    return resp.json() if resp.status_code == 200 else \
      f"Error retrieving the contents of dataverse, Id: {self.identifier}, Info: {resp.json()}"


  def getDataverseSize(self) -> str | Any:
    """
    Retrieves the size of a dataverse
    Returns (str):
      Dataverse size in bytes for successful request, otherwise the error message is returned
    """
    resp = requests.get(f"{self.server_url}/api/dataverses/{self.identifier}/storagesize", headers=self.headers,
                        timeout=10)
    if resp.status_code == 200:
      return (resp.json().get('data').get('message').replace('Total size of the files stored in this dataverse: ', ''))
    return f"Error retrieving the size for data verse, Id: {self.identifier}, Info: {resp.json()}"


  def getDataverseInfo(self) -> str | Any:
    """
    Retrieves information about a dataverse

    Returns:
        str | Any: The data associated with the dataverse if the request is successful, otherwise an error message
    """
    resp = requests.get(f"{self.server_url}/api/dataverses/{self.identifier}", headers=self.headers,
                        timeout=10)
    if resp.status_code:
      return resp.json().get('data')
    return f"Error retrieving the info for data verse, Id: {self.identifier}, Info: {resp.text}"


  ################ DATASET #######################
  def createDataset(self, ds_metadata: dict[str, Any], ds_validate_metadata: bool = False
                                       ) -> dict[Any, Any] | Any:
    """
    Creates and publishes a dataset to the parent dataverse
    Args:
      ds_metadata (dict[str, Any]): The dataset metadata
        Refer the https://guides.dataverse.org/en/latest/_downloads/4e04c8120d51efab20e480c6427f139c/dataset-create-new-all-default-fields.json for the default values to be used in the metadata
        The type names to be used in the metadata along with the values can be found in the metadata blocks and should correspond to the dataset-create-new-all-default-fields.json
      ds_validate_metadata (bool): Whether to validate the metadata

    Returns:
      A dictionary of dataset metadata with the persistent identifier for successful request, otherwise the error message is returned
    """
    metadata = DATAVERSE_METADATA
    if 'license' in ds_metadata:
      metadata['datasetVersion']['license'] = ds_metadata['license']
    else:
      del metadata['datasetVersion']['license']
    for _, metablock in metadata['datasetVersion']['metadataBlocks'].items():      # type:ignore[attr-defined]
      field_copy = metablock['fields'].copy()
      del metablock['displayName']
      metablock['fields'].clear()
      for field in field_copy:
        if field['typeName'] in ds_metadata:
          field['value'] = ds_metadata[field['typeName']]
          metablock['fields'].append(field)
    # Request to create the dataset
    resp = requests.post(f"{self.server_url}/api/dataverses/{self.identifier}/datasets",
      params={'doNotValidate': str(not ds_validate_metadata)}, timeout=10,
      headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token}, json=metadata)
    if resp.status_code == 201:
      # Request to publish the dataset
      resp = requests.post(f"{self.server_url}/api/datasets/:persistentId/actions/:publish",
        params={'persistentId': resp.json().get('data').get('persistentId'), 'type': 'major'},
        headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token}, timeout=10)
      if resp.status_code == 200:
        return resp.json().get('data')
      return f"Error publishing dataset, Info: {resp.text}"
    return f"Error creating dataset, Info: {resp.text}"


  def uploadFile(self, ds_pid: str, df_file_path: str, df_description: str, df_categories: list[str]) -> dict[Any, Any] | Any:
    """
    Uploads a file to a dataset
    Args:
      ds_pid (str): The identifier of the dataset
      df_file_path (str): The absolute path to the file to be uploaded
      df_description (str): The description of the file
      df_categories (list[str]): The categories/tags for the file

    Returns:
      {   'file_upload_result': file_upload_response,
          'dataset_publish_result': dataset_publish_response
      } for successful request, otherwise the error message is returned
    """
    filename = basename(df_file_path)
    metadata = dumps({'description': df_description, 'categories': df_categories})
    data:Any = {}
    with open(df_file_path, 'rb') as file_stream:
      data['file'] = (filename, file_stream, 'multipart/form-data')
      data['jsonData'] = (None, metadata, 'application/json')
      # Request to add the file to dataset
      resp = requests.post(
        f"{self.server_url}/api/datasets/:persistentId/add",
        params={'persistentId': ds_pid},
        headers={'X-Dataverse-key': self.api_token},
        files=data,
        timeout=5)
      if resp.status_code == 200:
        # Request to publish the dataset
        pub_resp = requests.post(
          f"{self.server_url}/api/datasets/:persistentId/actions/:publish",
          params={'persistentId': ds_pid, 'type': 'major'}, timeout=10,
          headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token})
        if pub_resp.status_code == 200:
          return {'file_upload_result': resp.json().get('data'),
                  'dataset_publish_result': pub_resp.json().get('data')}
        return f"Error publishing dataset: {ds_pid} as part of file ({df_file_path}) upload on server: "\
               f"{self.server_url}, Info: {pub_resp.json()}"
      return f"Error uploading file: {df_file_path} to dataset: {ds_pid} Info: {resp.json()}"


  def uploadRepository(self, metadata:dict[str,Any], file_path:str) -> tuple[bool, str]:
    """
    Uploads a file and metadata to become a dataset

    Args:
      metadata (dict): metadata to this file according to dataverse standard
      file_path (str): The absolute path to the file to be uploaded

    Returns:
      tuple: success of function, message
    """
    res= self.createDataset(metadata)
    if isinstance(res, str):
      return False, f'Error publishing the dataset: {res}'
    doi = f"{res['protocol']}:{res['authority']}/{res['identifier']}"
    reply = self.uploadFile(doi, file_path, '.eln file', ['file'])
    if isinstance(reply, str):
      return False, 'Error publishing the file'
    return True, f'Published: {doi}, {res["persistentUrl"]}'


  def getDatasetInfo(self, ds_persistent_id: str, version: str = ':latest-published') -> dict[Any, Any] | Any:
    """
    Fetch JSON representation of a dataset
    Args:
      ds_persistent_id (str): The identifier of the dataset
      version (str): The version of the dataset
        Note dataset versions can be referred to as:
          :draft the draft version, if any
          :latest either a draft (if exists) or the latest published version
          :latest-published the latest published version
          x.y a specific version, where x is the major version number and y is the minor version number
          x same as x.0

    Returns:
      JSON representation of the dataset for successful request, otherwise the error message is returned
    """
    resp = requests.get(
      f"{self.server_url}/api/datasets/:persistentId/versions/{version}?persistentId={ds_persistent_id}",
      params={'Accept': 'application/json'}, timeout=10,
      headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token})
    if resp.status_code == 200:
      return resp.json().get('data')
    return f"Error fetching JSON representation of dataset: {ds_persistent_id} Info: {resp.json()}"


  def getDatasetVersions(self, ds_persistent_id: str) -> dict[Any, Any] | Any:
    """
    Fetch the version list for dataset
    Args:
      ds_persistent_id (str): The identifier of the dataset

    Returns:
      Version list for the dataset for successful request, otherwise the error message is returned
    """
    resp = requests.get(
      f"{self.server_url}/api/datasets/:persistentId/versions?persistentId={ds_persistent_id}",
      params={'Accept': 'application/json'}, timeout=10,
      headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token})
    if resp.status_code == 200:
      return resp.json().get('data')
    return f"Error fetching version list for dataset: {ds_persistent_id} Info: {resp.json()}"


  def getDatasetLocks(self, ds_persistent_id: str) -> dict[Any, Any] | Any:
    """
    Fetches locks for a dataset

    Explanation:
        This method fetches the locks for a dataset identified by the persistent ID
        It makes an asynchronous HTTP GET request to retrieve the locks information and handles exceptions

    Args:
        ds_persistent_id (str): The persistent ID of the dataset to fetch locks for

    Returns:
        dict[Any, Any] | Any: A dictionary containing the locks information if successful, or an error message
    """
    resp = requests.get(
      f"{self.server_url}/api/datasets/:persistentId/locks?persistentId={ds_persistent_id}",
      params={'Accept': 'application/json'}, timeout=10,
      headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token})
    if resp.status_code == 200:
      return {'locks': resp.json().get('data')}
    return f"Error fetching locks for dataset: {ds_persistent_id}  Info: {resp.json()}"


  def getDatasetFiles(self, ds_persistent_id: str, version: str = ':latest-published') -> dict[Any, Any] | Any:
    """
    Fetch the file list for dataset
    Args:
      ds_persistent_id (str): The identifier of the dataset
      version (str): The version of the dataset
        Note dataset versions can be referred to as:
          :draft the draft version, if any
          :latest either a draft (if exists) or the latest published version
          :latest-published the latest published version
          x.y a specific version, where x is the major version number and y is the minor version number
          x same as x.0

    Returns:
      File list for the dataset for successful request, otherwise the error message is returned
    """
    resp = requests.get(
      f"{self.server_url}/api/datasets/:persistentId/versions/{version}/files?persistentId={ds_persistent_id}",
      params={'Accept': 'application/json'}, timeout=10,
      headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token})
    if resp.status_code == 200:
      return resp.json().get('data')
    return f"Error fetching file list for dataset: {ds_persistent_id}  Info: {resp.json()}"


  def getDatasetMetadata(self, ds_persistent_id: str, version: str = ':latest-published') -> dict[Any, Any] | Any:
    """
    Fetch the metadata block for dataset
    Args:
      ds_persistent_id (str): The identifier of the dataset
      version (str): The version of the dataset
        Note dataset versions can be referred to as:
          :draft the draft version, if any
          :latest either a draft (if exists) or the latest published version
          :latest-published the latest published version
          x.y a specific version, where x is the major version number and y is the minor version number
          x same as x.0

    Returns:
      Metadata block for the dataset for successful request, otherwise the error message is returned
    """
    resp = requests.get(
      f"{self.server_url}/api/datasets/:persistentId/versions/{version}/metadata?persistentId={ds_persistent_id}",
      params={'Accept': 'application/json'}, timeout=10,
      headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.api_token})
    if resp.status_code == 200:
      return resp.json().get('data')
    return f"Error fetching metadata block for dataset: {ds_persistent_id}  Info: {resp.json()}"


  def deleteEmptyDataverse(self) -> str | Any:
    """
    Deletes an empty dataverse

    Returns:
      Message for successful request, otherwise the error message is returned
    """
    resp = requests.delete(f"{self.server_url}/api/dataverses/{self.identifier}", headers=self.headers, timeout=10)
    if resp.status_code == 200:
      return resp.json().get('data').get('message')
    return f"Error deleting dataverse,  Info: {resp.json()}"


  def deletePublishedDataset(self, ds_persistent_id: str) -> str | Any:
    """
    Deletes a published dataset
    Note: The method fails presently due to a bug in dataverse API
          Every time the API returns 403 errors saying the user needs to be superuser
    Args:
      ds_persistent_id (str): The identifier of the dataset

    Returns:
      Message for successful request, otherwise the error message is returned
    """
    resp = requests.delete(
      f"{self.server_url}/api/datasets/:persistentId/destroy/",
      params={'persistentId': ds_persistent_id},
      headers=self.headers, timeout=10)
    if resp.status_code == 200:
      return resp.json().get('data').get('message')
    return f"Error deleting dataset, Id: {ds_persistent_id}, Info: {resp.json()}"


  def deleteNonEmptyDataverse(self) -> str | Any:
    """
    Deletes a non-empty dataverse

    Note: The method fails presently due to a bug in dataverse API while invoking the delete_published_dataset method

    Returns:
      Message for successful request, otherwise the error message is returned
    """
    contents = self.getDataverseContent()
    for content in contents:
      if content.get('type') == 'dataset':
        self.deletePublishedDataset(f"{content.get('protocol')}:{content.get('authority')}/{content.get('identifier')}")
      elif content.get('type') == 'dataverse':
        self.deleteNonEmptyDataverse()
      else:
        logging.error('Unknown content type: %s while deleting dataverse: %s on server: %s ', content.type,
                      self.identifier, self.server_url, exc_info=True)
    resp = requests.delete(f"{self.server_url}/api/dataverses/{self.identifier}", headers=self.headers, timeout=10)
    if resp.status_code == 200:
      return resp.json().get('data').get('message')
    return f"Error deleting dataverse, Id: {self.identifier}, Info: {resp.json()}"


  def prepareMetadata(self, metadata:dict[str,Any]) -> dict[str,Any]:
    """
    Prepares the metadata for uploading

    Args:
        metadata (dict): The metadata to be prepared

    Returns:
        dict: The prepared metadata
    """
    author = metadata['author']
    fields = [{'typeName': 'title', 'value': metadata['title'], 'typeClass': 'primitive'},
              {'typeName': 'author', 'value': [{'authorName': {'value': f"{author['last']}, {author['first']}"},
                'authorIdentifier': {'value': author['orcid']},
                'authorAffiliation': {'value': author['organizations'][0]['organization']}}], 'typeClass': 'compound'},
              {'typeName': 'datasetContact', 'value': [{'datasetContactEmail': {'value': author['email']},
                'datasetContactName': {'value': f"{author['last']}, {author['first']}"}}], 'typeClass': 'compound'},
              {'typeName': 'keywords', 'value': metadata['keywords'], 'typeClass': 'primitive'},
              {'typeName': 'publicationDate', 'value': datetime.now().strftime('%Y-%m-%d'), 'typeClass': 'primitive'},
              {'typeName': 'dsDescription', 'value': [{'dsDescriptionValue': {'value': metadata['description']}}],
                'typeClass': 'compound'},
              {'typeName': 'subject', 'value': [metadata['category']], 'typeClass': 'controlledVocabulary'}
            ] + metadata['additional']
    return {'metadata': {'datasetVersion': {'metadataBlocks': {'citation': {'fields': fields}}}}}
