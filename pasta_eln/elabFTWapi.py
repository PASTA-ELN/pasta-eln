""" API for accessing an elabFTW server. That's API is inconvenient, complicated, ..."""
import base64, json, copy, mimetypes
from pathlib import Path
from typing import Any
import requests  # only requirement; could be replaced with urllib to eliminate requirements

VERIFYSSL = False

class ElabFTWApi:
  """ API for accessing an elabFTW server. That's API is inconvenient, complicated, ..."""

  def __init__(self, url:str='', apiKey:str=''):
    '''
    initiate an elab instance to allow for syncing

    Args:
      url (str): url
      apiKey (str): API key
    '''
    if not url and not apiKey:
      url = input('Please enter the url: ').strip()
      url = url if url.startswith('htt') else f'https://{url}'
      url = url if url.endswith('/')     else f'{url}/'
      print('Log-in to elabFTW server.')
      print(f'Go to website: {url}ucp.php?tab=4, enter a name and as permission: read/write. Create the API key')
      apiKey = input('Copy-paste the api-key: ').strip()
    self.url = url
    self.headers = {'Content-type': 'application/json', 'Authorization': apiKey, 'Accept': 'text/plain'}
    # test server
    response = requests.get(f'{self.url}info', headers=self.headers, verify=VERIFYSSL, timeout=60)
    if response.status_code == 200:
      elabVersion = int(json.loads(response.content.decode('utf-8')).get('elabftw_version','0.0.0').split('.')[0])
      if elabVersion<5:
        print('**ERROR old elab-ftw version')
    else:
      print('**ERROR not an elab-ftw server')
    return


  def create(self, entry:str, content:str='') -> bool:
    """
    create something

    Args:
      entry (str): entry to create, e.g. experiments, items, items_types
      content (str): content to create

    Returns:
      bool: success of operation
    """
    response = requests.post(self.url+entry, headers=self.headers, verify=VERIFYSSL, timeout=60)
    print("**TODO", content)
    if response.status_code == 201:
      return True
    print(f"**ERROR occurred in create of url {entry}: {response.json}")
    return False

  def read(self, entry:str, identifier:int=-1) -> list[dict[str,Any]]:
    """
    read something

    Args:
      entry (str): entry to create, e.g. experiments, items, items_types
      identifier (int): elabFTW's identifier

    Returns:
      dict: content read
    """
    url = f'{self.url}{entry}' if identifier==-1 else f'{self.url}{entry}/{identifier}'
    response = requests.get(url, headers=self.headers, verify=VERIFYSSL, timeout=60)
    if response.status_code == 200:
      return json.loads(response.content.decode('utf-8'))
    print(f"**ERROR occurred in get of url {entry} / {identifier}")
    return [{}]

  def update(self, entry:str, identifier:int, content:dict[str,Any]={}) -> bool:
    """
    update something

    Args:
      entry (str): entry to create, e.g. experiments, items, items_types
      identifier (int): elabFTW's identifier
      content (dict): content to update

    Returns:
      bool: success of operation
    """
    response = requests.patch(f'{self.url}{entry}/{identifier}', headers=self.headers, data=json.dumps(content), verify=VERIFYSSL, timeout=60)
    return response.status_code == 200

  def delete(self, entry:str, identifier:int) -> bool:
    """
    delete something

    Args:
      entry (str): entry to create, e.g. experiments, items, items_types
      identifier (int): elabFTW's identifier

    Returns:
      bool: success of operation
    """
    response = requests.delete(f'{self.url}{entry}/{identifier}', headers=self.headers, verify=VERIFYSSL, timeout=60)
    if response.status_code == 204:
      return True
    print(f"**ERROR occurred in delete of url {entry}")
    return False

  def touch(self, entry:str, content:dict[str,Any]={}) -> int:
    """
    create something, without much content

    Args:
      entry (str): entry to create, e.g. experiments, items, items_types
      content (dict): content to create

    Returns:
      int: elabFTW id
    """
    response = requests.post(self.url+entry, headers=self.headers, data=json.dumps(content), verify=VERIFYSSL, timeout=60)
    if response.status_code == 201:
      return int(response.headers['Location'].split('/')[-1])
    if response.status_code == 400:
      print(f"**ERROR occurred in touch of url '{entry}': {json.loads(response.content.decode('utf-8'))['description']}")
    return -1


  def upload(self, entry_type:str, identifier:int, content:str='', fileName:str='', comment:str='') -> bool:
    """
    upload a file

    Args:
      entry_type (str): entry_type to which to attach the upload
      identifier (int): elab's identifier
      content (str): base64 content, if given, it is used
      fileName (str): if content is not given, this filename is used
      comment (str): optional comment

    Returns:
      bool: success
    """
    data:dict[str,Any] = {}
    if content.startswith('<?xml'):
      data = {'comment':comment, 'file': ('thumbnail.svg', content.encode(), 'image/svg')}
    elif content.startswith('data:image/png'):
      data = {'comment':comment, 'file': ('thumbnail.png', base64.b64decode(content[22:]) , 'image/png')}
    elif content.startswith('data:image/jpg'):
      data = {'comment':comment, 'file': ('thumbnail.jpg', base64.b64decode(content[22:]) , 'image/jpg')}
    elif fileName:
      with open(fileName,'rb') as fIn:
        try:
          mime = mimetypes.types_map[Path(fileName).suffix]
        except Exception:
          mime = 'application/octet-stream'
        data = {'comment':comment, 'file': (Path(fileName).name, fIn.read(), mime)}
    else:  #default for fast testing
      data = {'comment':comment, 'file': ('README.md', b'Read me!\n', 'text/markdown')}
    headers = copy.deepcopy(self.headers)
    del headers['Content-type'] #will automatically become 'multipart/form-data'
    response = requests.post(f'{self.url}{entry_type}/{identifier}/uploads', headers=headers, files=data, verify=VERIFYSSL, timeout=60)
    if response.status_code == 201:
      return True
    print(f"**ERROR occurred in touch of url '{entry_type}/{identifier}': {json.loads(response.content.decode('utf-8'))['description']}")
    return False
