import requests
from typing import Any
from .repository import RepositoryClient
# TODO
# -test dataverse
# - structure API and Sandboxes
# - stucture Metadata: including communities
# - build GUI

# Zenodo
# - Go to Zenodo.
# - Log in or create an account.
# - Navigate to Applications under your user settings.
# - Generate a new Personal Access Token with deposit:write and deposit:actions permissions.
# - Use the sandbox API (https://sandbox.zenodo.org/api/deposit/depositions) for testing.
# Metadata
# - title (string)
# - upload_type (string, e.g. "dataset", "publication", etc.)
# - description (string)
# - creators (list of dicts: name, affiliation, orcid)
# - keywords (list of strings)
# - publication_date (YYYY-MM-DD)
# - access_right (e.g. "open", "embargoed", "restricted", "closed")
# - license (e.g. "CC-BY-4.0")
# - related_identifiers (list of dicts: identifier, relation, resource_type)
# More notes
# - "keywords": ["machine learning", "neuroscience", "data science"]
# - "communities": [{"identifier": "neuroscience"}]

# Comparison table dataverse - zenodo
# title	title
# author	creators
# datasetContact	Not required (optionally in creators or omitted)
# dsDescription	description
# subject	keywords, communities (approx.)
# keyword	keywords
# publicationDate	publication_date
# license (from termsOfUse)	license
# language	language
# series	No direct match
# relatedPublications	related_identifiers
# productionDate	No direct match
# depositor (internal use)	Not explicitly captured
# distributor	No direct match
# software (if included)	upload_type = software, or related_identifiers
# notesText	description (as additional info)
# fileDescription	File-level metadata (manually added in Zenodo)
# geographicCoverage	No direct match (can go in description or keywords)
# temporalCoverage	No direct match
# dataSources	description (or none)
# methods	description (or none)

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
    """
    Checks if the data-verse server is reachable

    Returns (tuple(bool, Any)):
      A tuple of (success, a message) is returned
    """
    resp = requests.get(f"{self.server_url}/api/info/version", headers=self.headers1)
    success = (resp.status_code == 200 and resp.json().get('data').get('version') is not None)
    return (success, 'Dataverse is reachable') \
      if success \
      else (success, f"Cannot reach server: {self.server_url}, Status: {resp.status_code}, json: {resp.json()}")


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
    resp = requests.get(f"{self.server_url}/api/users/token", headers=self.headers1)
    return (bool(resp) and resp.status_code is not None
            and resp.status_code not in [401, 403, 500])


  def uploadRepository(self, metadata:dict[str,Any], file_path:str) -> bool:
    """
    Uploads a file and metadata to become a dataset.

    Args:
      metadata (dict): metadata to this file according to Zenodo standard
      file_path (str): The absolute path to the file to be uploaded.

    Returns:
      bool: success of function
    """
    # Define the API URLs and headers based on the repository kind
    # Step 1: Create the deposition with metadata
    resp = requests.post(self.server_url, json=metadata, headers=self.headers1)
    if resp.status_code != 201:
      print("**ERROR** creating deposition/dataset:", resp.json(), resp.status_code, resp.text)
      return False
    deposition = resp.json()
    persistentID = deposition["id"]
    print(f"Deposition created: {persistentID}")

    # Define the API URLs and headers based on the repository kind
    files = {"file": open(file_path, "rb")}
    file_upload_url = f"{self.server_url}/{persistentID}/files"
    publish_url = f"{self.server_url}/{persistentID}/actions/publish"

    # Step 2: Upload a file
    resp = requests.post(file_upload_url, files=files, headers=self.headers2)
    if resp.status_code != 201:
      print("**ERROR** uploading file:", resp.json())
      return False
    print("File uploaded successfully:")

    # Step 3: Publish the deposition
    resp = requests.post(publish_url, headers=self.headers1)
    if resp.status_code != 202:
      print("**ERROR** publishing:", resp.json())
      return False
    print("Published:", resp.json()['doi'], resp.json()['doi_url'])
    return True
