from typing import Any

class RepositoryClient:
  def __init__(self, server_url: str, api_token: str) -> None:
    """
    Initializes the client.

    Args:
        server_url (str): The URL of the server.
        api_token (str): The API token for authentication.
    """
    self.api_token = api_token
    self.server_url = server_url


  def checkServer(self) -> tuple[bool, str]:
    """
    Checks if the data-verse server is reachable

    Returns (tuple(bool, Any)):
      A tuple of (success, a message) is returned
    """
    return False, ''


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
    return False


  def uploadRepository(self, metadata:dict[str,Any], file_path:str) -> bool:
    """
    Uploads a file and metadata to become a dataset.

    Args:
      metadata (dict): metadata to this file according to its standard
      file_path (str): The absolute path to the file to be uploaded.

    Returns:
      bool: success of function
    """
    print(metadata)
    print(file_path)
    return False
