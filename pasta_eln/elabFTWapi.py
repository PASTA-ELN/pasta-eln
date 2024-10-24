import json
import requests
from typing import Any

VERIFYSSL = False

class ElabFTWApi:

  def __init__(self, url:str, apiKey:str):
    '''
    initiate an elab instance to allow for syncing

    Args:
      url (str): url
      apiKey (str): API key
    '''
    self.url = url
    self.headers = {'Content-type': 'application/json', 'Authorization': apiKey, 'Accept': 'text/plain'}
    # test server
    elabVersion = int(self.read('info').get('elabftw_version','0.0.0').split('.')[0])
    if elabVersion<5:
      print('**ERROR old elab-ftw version')
      return
    return


  def create(self, urlSuffix:str, content:str='') -> bool:
    """
    create something

    Args:
      urlSuffix (str): suffix of url, e.g. starting with experiments
      content (str): content to create

    Returns:
      bool: success of operation
    """
    response = requests.post(self.url+urlSuffix, headers=self.headers, verify=VERIFYSSL)
    print("**TODO")
    if response.status_code == 201:
      return True
    print(f"**ERROR occurred in create of url {urlSuffix}: {response.json}")
    return False

  def read(self, urlSuffix:str) -> dict[str,Any]:
    """
    read something

    Args:
      urlSuffix (str): suffix of url, e.g. starting with experiments

    Returns:
      dict: content read
    """
    response = requests.get(self.url+urlSuffix, headers=self.headers, verify=VERIFYSSL)
    if response.status_code == 200:
      return json.loads(response.content.decode('utf-8'))
    print(f"**ERROR occurred in get of url {urlSuffix}")
    return {}

  def update(self, urlSuffix:str, content:dict[str,Any]={}) -> bool:
    """
    update something

    Args:
      urlSuffix (str): suffix of url, e.g. starting with experiments
      content (dict): content to update

    Returns:
      bool: success of operation
    """
    response = requests.patch(self.url+urlSuffix, headers=self.headers, data=json.dumps(content), verify=VERIFYSSL)
    return response.status_code == 200

  def delete(self, urlSuffix:str) -> bool:
    """
    delete something

    Args:
      urlSuffix (str): suffix of url, e.g. starting with experiments

    Returns:
      bool: success of operation
    """
    response = requests.delete(self.url+urlSuffix, headers=self.headers, verify=VERIFYSSL)
    if response.status_code == 204:
      return True
    print(f"**ERROR occurred in delete of url {urlSuffix}")
    return False

  def touch(self, urlSuffix:str, content:dict[str,str]={}) -> int:
    """
    create something, without much content

    Args:
      urlSuffix (str): suffix of url, e.g. starting with experiments
      content (dict): content to create

    Returns:
      int: elabFTW id
    """
    response = requests.post(self.url+urlSuffix, headers=self.headers, data=json.dumps(content), verify=VERIFYSSL)
    if response.status_code == 201:
      return int(response.headers['Location'].split('/')[-1])
    print(f"**ERROR occurred in create of url {self.url}: {response.content} {response.headers}")
    return -1
