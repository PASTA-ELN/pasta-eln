"""Parent class to repository classes"""
from abc import ABC, abstractmethod
from typing import Any


class RepositoryClient(ABC):
  """Required interface shared by repository clients."""
  def __init__(self, serverUrl: str, apiToken: str) -> None:
    """
    Initializes the client

    Args:
        serverUrl (str): The URL of the server
        apiToken (str): The API token for authentication
    """
    self.apiToken = apiToken
    self.serverUrl = serverUrl


  @abstractmethod
  def checkServer(self) -> tuple[bool, str]:
    """
    Checks if the data-verse server is reachable

    Returns (tuple(bool, Any)):
      A tuple of (success, a message) is returned
    """


  @abstractmethod
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


  @abstractmethod
  def uploadRepository(self, metadata:dict[str,Any], filePath:str) -> tuple[bool, str]:
    """
    Uploads a file and metadata to become a dataset

    Args:
      metadata (dict): metadata to this file according to its standard
      filePath (str): The absolute path to the file to be uploaded

    Returns:
      tuple: success of function, message
    """


  @abstractmethod
  def prepareMetadata(self, metadata:dict[str,Any]) -> dict[str,Any]:
    """
    Prepares the metadata for uploading

    Args:
        metadata (dict): The metadata to be prepared

    Returns:
        dict: The prepared metadata
    """
