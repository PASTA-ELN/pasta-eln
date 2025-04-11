import requests
from typing import Any
from datetime import datetime
from .repository import RepositoryClient

class ZenodoClient(RepositoryClient):
  def __init__(self, server_url: str, api_token: str) -> None:
    """
    Initializes the client.

    Args:
        server_url (str): The URL of the server.
        api_token (str): The API token for authentication.
    """
    super().__init__(server_url, api_token)
    self.headers1 = {"Content-Type": "application/json", "Authorization": f"Bearer {api_token}"}
    self.headers2 = {"Authorization": f"Bearer {api_token}"}

  def checkServer(self) -> tuple[bool, str]:
    """ VOID TEST SINCE ZENODO DOES NOT HAVE A SERVER TEST

    Checks if the data-verse server is reachable

    Returns (tuple(bool, Any)):
      A tuple of (success, a message) is returned
    """
    return True, 'VOID TEST'
    # resp = requests.get(f"{self.server_url}/api/info/version", headers=self.headers1)
    # success = (resp.status_code == 200 and resp.json().get('data').get('version') is not None)
    # return (success, 'Dataverse is reachable') \
    #   if success \
    #   else (success, f"Cannot reach server: {self.server_url}, Status: {resp.status_code}, json: {resp.json()}")


  def checkAPIKey(self) -> bool:
    """
    Checks if the given API token is valid.

    Explanation:
        This method checks if the provided API token is valid by making a request to the server.
        It logs the server URL and sends a GET request to the token endpoint with the API token.
        It returns True if the response is successful and the status code is not 401, 403, or 500.

    Args:
        self: The instance of the class.

    Returns:
        bool: True if the API token is valid, False otherwise.
    """
    server_url = f"{self.server_url}/api/deposit/depositions"
    resp = requests.get(f"{self.server_url}", headers=self.headers1)
    return (bool(resp) and resp.status_code is not None
            and resp.status_code not in [401, 403, 500])


  def uploadRepository(self, metadata:dict[str,Any], file_path:str) -> tuple[bool, str]:
    """
    Uploads a file and metadata to become a dataset.

    Args:
      metadata (dict): metadata to this file according to Zenodo standard
      file_path (str): The absolute path to the file to be uploaded.

    Returns:
      tuple: success of function, message
    """
    server_url = f"{self.server_url}/api/deposit/depositions"
    # Define the API URLs and headers based on the repository kind
    # Step 1: Create the deposition with metadata
    resp = requests.post(server_url, json=metadata, headers=self.headers1)
    if resp.status_code != 201:
      print("**ERROR** creating deposition/dataset:", resp.json(), resp.status_code, resp.text)
      return False, 'Error creating the dataset'
    deposition = resp.json()
    persistentID = deposition["id"]
    # print(f"Deposition created: {persistentID}")

    # Define the API URLs and headers based on the repository kind
    files = {"file": open(file_path, "rb")}
    file_upload_url = f"{server_url}/{persistentID}/files"
    publish_url = f"{server_url}/{persistentID}/actions/publish"

    # Step 2: Upload a file
    resp = requests.post(file_upload_url, files=files, headers=self.headers2)
    if resp.status_code != 201:
      print("**ERROR** uploading file:", resp.json())
      return False, 'Error uploading the file'
    # print("File uploaded successfully:")

    # Step 3: Publish the deposition
    resp = requests.post(publish_url, headers=self.headers1)
    if resp.status_code != 202:
      print("**ERROR** publishing:", resp.json())
      return False, 'Error publishing the dataset'
    return True, f'Published: {resp.json()["doi"]}, {resp.json()["doi_url"]}'


  def prepareMetadata(self, metadata:dict[str,Any]) -> dict[str,Any]:
    """
    Prepares the metadata for uploading.

    Args:
        metadata (dict): The metadata to be prepared.

    Returns:
        dict: The prepared metadata.
    """
    author = metadata['author']
    metadataZenodo = {
        "title": metadata["title"],
        "upload_type": "dataset",
        "description": metadata["description"],
        "creators": [
            {"name": f"{author['last']}, {author['first']}",
             "affiliation": author['organizations'][0]['organization'],
             "orcid": author['orcid'],
             "email": author['email']},
        ],
        "keywords": metadata["keywords"],
        "communities": [
            {"identifier": metadata['category']},
        ],
        "publication_date": datetime.now().strftime("%Y-%m-%d"),
        "access_right": "open",
        "license": "CC-BY-4.0"
      }
    return {"metadata": metadata['additional']|metadataZenodo}
