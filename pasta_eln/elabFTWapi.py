import base64, json, requests, copy
from typing import Any

VERIFYSSL = False

class ElabFTWApi:

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
    elabVersion = int(self.read('info').get('elabftw_version','0.0.0').split('.')[0])
    if elabVersion<5:
      print('**ERROR old elab-ftw version')
      return
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
    response = requests.post(self.url+entry, headers=self.headers, verify=VERIFYSSL)
    print("**TODO")
    if response.status_code == 201:
      return True
    print(f"**ERROR occurred in create of url {entry}: {response.json}")
    return False

  def read(self, entry:str, identifier:int=-1) -> dict[str,Any]:
    """
    read something

    Args:
      entry (str): entry to create, e.g. experiments, items, items_types
      identifier (int): elabFTW's identifier

    Returns:
      dict: content read
    """
    url = f'{self.url}{entry}' if identifier==-1 else f'{self.url}{entry}/{identifier}'
    response = requests.get(url, headers=self.headers, verify=VERIFYSSL)
    if response.status_code == 200:
      return json.loads(response.content.decode('utf-8'))
    print(f"**ERROR occurred in get of url {entry} / {identifier}")
    return {}

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
    response = requests.patch(f'{self.url}{entry}/{identifier}', headers=self.headers, data=json.dumps(content), verify=VERIFYSSL)
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
    response = requests.delete(self.url+entry, headers=self.headers, verify=VERIFYSSL)
    if response.status_code == 204:
      return True
    print(f"**ERROR occurred in delete of url {entry}")
    return False

  def touch(self, entry:str, content:dict[str,str]={}) -> int:
    """
    create something, without much content

    Args:
      entry (str): entry to create, e.g. experiments, items, items_types
      content (dict): content to create

    Returns:
      int: elabFTW id
    """
    response = requests.post(self.url+entry, headers=self.headers, data=json.dumps(content), verify=VERIFYSSL)
    if response.status_code == 201:
      return int(response.headers['Location'].split('/')[-1])
    if response.status_code == 400:
      print(f"**ERROR occurred in touch of url '{entry}': {json.loads(response.content.decode('utf-8'))['description']}")
    return -1

  def upload(self, entry_type, identifier, content):
    print(content[:25])
    if content.startswith('<?xml'):
      return
    fIn = open('/home/steffen/Temporary/Ruomeng/region03.tif','rb')
    data = fIn.read()
    headers = copy.deepcopy(self.headers)
    headers['Content-type'] = 'multipart/form-data'
    response = requests.post(f'{self.url}{entry_type}/{identifier}/uploads', headers=headers, file=data, verify=VERIFYSSL)
    print(response.content)
