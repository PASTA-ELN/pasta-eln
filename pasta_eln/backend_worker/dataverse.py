""" Client for communicating with Dataverse Server via REST API
- Author: Jithu Murugan, Steffen Brinckmann
"""
from datetime import datetime
from json import dumps
from os.path import basename
from typing import Any
from xml.etree.ElementTree import ElementTree, fromstring
# Dataverse: remember to always publish everything before using it!!
import requests
from requests.auth import HTTPBasicAuth
from .dataverse_default_dict import DATAVERSE_METADATA
from .repository import RepositoryClient


class DataverseClient(RepositoryClient):
  """ Client for communicating with Dataverse Server via REST API """

  def __init__(self, serverUrl: str, apiToken: str, identifier:str) -> None:
    """
    Initializes the client

    Args:
        server_url (str): The URL of the server
        api_token (str): The API token for authentication
        identifier (str): sub-dataverse, category; use '' for void
    """
    super().__init__(serverUrl, apiToken)
    self.identifier = identifier
    self.headers = {'Accept': 'application/json', 'X-Dataverse-key': self.apiToken}


  def checkServer(self) -> tuple[bool, str]:
    """
    Checks if the data-verse server is reachable

    Returns (tuple(bool, Any)):
      A tuple of (success, a message) is returned
    """
    resp = requests.get(f"{self.serverUrl}/api/info/version", headers={'Accept': 'application/json'}, timeout=10)
    success = (resp.status_code == 200 and resp.json().get('data').get('version') is not None)
    return (success, 'Dataverse is reachable') \
      if success \
      else (success, f"Cannot reach server: {self.serverUrl}, Status: {resp.status_code}, json: {resp.json()}")


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
    resp = requests.get(f"{self.serverUrl}/api/users/token", headers=self.headers, timeout=10)
    return resp.ok


  def getDataverseList(self) -> dict[Any, Any] | Any:
    """
    Gets the list of data verses
    Returns:
      A dictionary of dataverses (identifier & title) for successful request,
      otherwise the error message is returned
    """
    resp = requests.get(f"{self.serverUrl}/dvn/api/data-deposit/v1.1/swordv2/service-document",
      headers={'Accept': 'application/json', 'X-Dataverse-key': self.apiToken},
      auth=HTTPBasicAuth(self.apiToken, ''), timeout=10)
    if resp.status_code == 200:
      elementTree: ElementTree = ElementTree(fromstring(resp.text))
      root = elementTree.getroot()
      if root is not None:
        dataverseList: list[dict[str, str]] = []
        for element in root.findall('.//{http://www.w3.org/2007/app}collection'):
          title = element.find('.//{http://www.w3.org/2005/Atom}title')
          if title is not None:
            titleVal = title.text if title.text is not None else ''
            dataverseList.append({'id': element.attrib['href'].split('/')[-1],'title': titleVal})
        dataverseList.sort(key=lambda x: x['title'])
        return dataverseList
    return f"Error get dataverse list, Server:{self.serverUrl},  Status:{resp.status_code}"


  def createDataset(self, dsMetadata: dict[str, Any], dsValidateMetadata: bool = False
                                        ) -> dict[Any, Any] | Any:
    """
    Creates and publishes a dataset to the parent dataverse
    Args:
      dsMetadata (dict[str, Any]): The dataset metadata
        Refer the https://guides.dataverse.org/en/latest/_downloads/4e04c8120d51efab20e480c6427f139c/dataset-create-new-all-default-fields.json for the default values to be used in the metadata
        The type names to be used in the metadata along with the values can be found in the metadata blocks and should correspond to the dataset-create-new-all-default-fields.json
      dsValidateMetadata (bool): Whether to validate the metadata

    Returns:
      A dictionary of dataset metadata with the persistent identifier for successful request, otherwise the error message is returned
    """
    metadata = DATAVERSE_METADATA
    if 'license' in dsMetadata:
      metadata['datasetVersion']['license'] = dsMetadata['license']
    else:
      del metadata['datasetVersion']['license']
    for _, metablock in metadata['datasetVersion']['metadataBlocks'].items():      # type:ignore[attr-defined]
      fieldCopy = metablock['fields'].copy()
      del metablock['displayName']
      metablock['fields'].clear()
      for field in fieldCopy:
        if field['typeName'] in dsMetadata:
          field['value'] = dsMetadata[field['typeName']]
          metablock['fields'].append(field)
    # Request to create the dataset
    resp = requests.post(f"{self.serverUrl}/api/dataverses/{self.identifier}/datasets",
      params={'doNotValidate': str(not dsValidateMetadata)}, timeout=10,
      headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.apiToken}, json=metadata)
    if resp.status_code == 201:
      # Request to publish the dataset
      resp = requests.post(f"{self.serverUrl}/api/datasets/:persistentId/actions/:publish",
        params={'persistentId': resp.json().get('data').get('persistentId'), 'type': 'major'},
        headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.apiToken}, timeout=10)
      if resp.status_code == 200:
        return resp.json().get('data')
      return f"Error publishing the project in the repository. Info: {resp.text}"
    return f"Error creating the project in the repository. Info: {resp.text}"


  def uploadFile(self, dsPid: str, dfFilePath: str, dfDescription: str, dfCategories: list[str]) -> dict[Any, Any] | Any:
    """
    Uploads a file to a dataset
    Args:
      dsPid (str): The identifier of the dataset
      dfFilePath (str): The absolute path to the file to be uploaded
      dfDescription (str): The description of the file
      dfCategories (list[str]): The categories/tags for the file

    Returns:
      {   'file_upload_result': file_upload_response,
          'dataset_publish_result': dataset_publish_response
      } for successful request, otherwise the error message is returned
    """
    filename = basename(dfFilePath)
    metadata = dumps({'description': dfDescription, 'categories': dfCategories})
    data:Any = {}
    with open(dfFilePath, 'rb') as fileStream:
      data['file'] = (filename, fileStream, 'multipart/form-data')
      data['jsonData'] = (None, metadata, 'application/json')
      # Request to add the file to dataset
      resp = requests.post(
        f"{self.serverUrl}/api/datasets/:persistentId/add",
        params={'persistentId': dsPid},
        headers={'X-Dataverse-key': self.apiToken},
        files=data,
        timeout=5)
      if resp.status_code == 200:
        # Request to publish the dataset
        pubResp = requests.post(
          f"{self.serverUrl}/api/datasets/:persistentId/actions/:publish",
          params={'persistentId': dsPid, 'type': 'major'}, timeout=10,
          headers={'Content-Type': 'application/json', 'X-Dataverse-key': self.apiToken})
        if pubResp.status_code == 200:
          return {'file_upload_result': resp.json().get('data'),
                  'dataset_publish_result': pubResp.json().get('data')}
        return f"Error publishing dataset: {dsPid} as part of file ({dfFilePath}) upload on server: "\
               f"{self.serverUrl}, Info: {pubResp.json()}"
      return f"Error uploading file: {dfFilePath} to dataset: {dsPid}. Info: {resp.json()}"


  def uploadRepository(self, metadata:dict[str,Any], filePath:str) -> tuple[bool, str]:
    """
    Uploads a file and metadata to become a dataset

    Args:
      metadata (dict): metadata to this file according to dataverse standard
      filePath (str): The absolute path to the file to be uploaded

    Returns:
      tuple: success of function, message
    """
    res= self.createDataset(metadata)
    if isinstance(res, str):
      return False, f'Error publishing the project in the repository: {res}'
    doi = f"{res['protocol']}:{res['authority']}/{res['identifier']}"
    reply = self.uploadFile(doi, filePath, 'ELN file', ['file'])
    if isinstance(reply, str):
      return False, 'Error publishing the file'
    return True, f'Published: {doi}, {res["persistentUrl"]}'


  def prepareMetadata(self, metadata:dict[str,Any]) -> dict[str,Any]:
    """
    Prepares the metadata for uploading

    Args:
        metadata (dict): The metadata to be prepared

    Returns:
        dict: The prepared metadata
    """
    author = metadata['author']
    additional = metadata.get('additional') or []
    if isinstance(additional, dict):
      additional = [additional]
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
            ] + additional
    return {'metadata': {'datasetVersion': {'metadataBlocks': {'citation': {'fields': fields}}}}}
