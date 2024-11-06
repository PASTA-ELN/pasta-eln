# mypy: disable-error-code="arg-type"
""" API for accessing an elabFTW server. That's API is inconvenient, complicated, ..."""
import base64, json, copy, mimetypes
from pathlib import Path
from typing import Any
import requests  # only requirement; could be replaced with urllib to eliminate requirements

class ElabFTWApi:
  """ API for accessing an elabFTW server. That's API is inconvenient, complicated, ..."""

  def __init__(self, url:str='', apiKey:str='', verifySSL:bool=True):
    '''
    initiate an elab instance to allow for syncing

    Args:
      url (str): url
      apiKey (str): API key
      veifySSL (bool): verify SSL certificate
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
    self.param = {'headers':self.headers, 'verify':verifySSL, 'timeout':60}
    # test server
    try:
      response = requests.get(f'{self.url}info', **self.param)
      if response.status_code == 200:
        elabVersion = int(json.loads(response.content.decode('utf-8')).get('elabftw_version','0.0.0').split('.')[0])
        if elabVersion<5:
          print('**ERROR old elab-ftw version')
      else:
        print('**ERROR not an elab-ftw server')
    except requests.ConnectionError:
      try:
        response = requests.get('https://www.google.com', headers={'Content-type': 'application/json'}, timeout=60)
        print('**ERROR not an elab-ftw server')
      except requests.ConnectionError:
        print("**ERROR: cannot connect to google. You are not online")
        self.url = ''
        self.headers = {}
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
    response = requests.post(self.url+entry, **self.param)
    print("**TODO", content)
    if response.status_code == 201:
      return True
    print(f"**ERROR occurred in create of url {entry}: {response.json}")
    return False


  def createLink(self, entryType:str, identifier:int, targetType:str, linkTarget:int) -> bool:
    """
    create a link

    Args:
      entryType (str): entry type to modify (items, experiments)
      identifier (int): entry to change
      targetType (str): entry type to link to (items, experiments)
      linkTarget (int): target of the link

    Returns:
      bool: success of operation
    """
    response = requests.post(f'{self.url}{entryType}/{identifier}/{targetType}_links/{linkTarget}', **self.param)
    if response.status_code == 201:
      return True
    print(f"**ERROR occurred in create of url f'{self.url}{entryType}/{identifier}/{targetType}_links/{linkTarget}': {response.json}")
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
    response = requests.get(url, **self.param)
    if response.status_code == 200:
      res = json.loads(response.content.decode('utf-8'))
      return res if identifier == -1 else [res]
    print(f"**ERROR occurred in get of url {entry} / {identifier}")
    return [{}]

  def update(self, entryType:str, identifier:int, content:dict[str,Any]={}) -> bool:
    """
    update something

    Args:
      entryType (str): entryType to create, e.g. experiments, items, items_types
      identifier (int): elabFTW's identifier
      content (dict): content to update

    Returns:
      bool: success of operation
    """
    tags = content.pop('tags',[])
    response = requests.patch(f'{self.url}{entryType}/{identifier}', data=json.dumps(content), **self.param)
    if response.status_code not in {200, 400}:
      return False
    # separate tags handling
    response = requests.get(f'{self.url}{entryType}/{identifier}/tags', **self.param)
    for tag in tags:
      response = requests.post(f'{self.url}{entryType}/{identifier}/tags', data=json.dumps({'tag':tag}), **self.param)
    return response.status_code == 201


  def delete(self, entry:str, identifier:int) -> bool:
    """
    delete something

    Args:
      entry (str): entry to create, e.g. experiments, items, items_types
      identifier (int): elabFTW's identifier

    Returns:
      bool: success of operation
    """
    response = requests.delete(f'{self.url}{entry}/{identifier}', **self.param)
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
    response = requests.post(self.url+entry, data=json.dumps(content), **self.param)
    if response.status_code == 201:
      return int(response.headers['Location'].split('/')[-1])
    if response.status_code == 400:
      print(f"**ERROR occurred in touch of url '{entry}': {json.loads(response.content.decode('utf-8'))['description']}")
    return -1


  def upload(self, entryType:str, identifier:int, content:str='', fileName:str='', jsonContent:str='', comment:str='') -> int:
    """
    upload a file

    Args:
      entryType (str): entryType to which to attach the upload
      identifier (int): elab's identifier
      content (str): base64 content, if given, it is used
      fileName (str): if content is not given, this filename is used
      jsonContent (str): if given, this json is content is used to create a json file
      comment (str): optional comment

    Returns:
      int: id of upload; -1 on failure
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
    elif jsonContent:
      data = {'comment':comment, 'file': ('do_not_change.json', jsonContent.encode(), 'text/json')}
    else:  #default for fast testing
      data = {'comment':comment, 'file': ('README.md', b'Read me!\n', 'text/markdown')}
    headers = copy.deepcopy(self.headers)
    del headers['Content-type'] #will automatically become 'multipart/form-data'
    response = requests.post(f'{self.url}{entryType}/{identifier}/uploads', headers=headers,
                             files=data, verify=self.param['verify'], timeout=60)
    if response.status_code == 201:
      return int(response.headers['Location'].split('/')[-1])
    print(f"**ERROR occurred in upload of url '{entryType}/{identifier}': {json.loads(response.content.decode('utf-8'))['description']}")
    return -1


  def purgeExperimentsItems(self) -> None:
    """ Remove all documents and items on server """
    for entityType in {'experiments','items'}:
      response = requests.get(f'{self.url}{entityType}?archived=on', **self.param)
      for identifier in [i['id'] for i in json.loads(response.content.decode('utf-8'))]:
        response = requests.delete(f'{self.url}{entityType}/{identifier}', **self.param)
        if response.status_code != 204:
          print(f'**ERROR purge delete {entityType}: {identifier}')
    return


  def upLoadUpdate(self, entryType:str, identifier:int, uploadID:int, content:dict[str,Any]={}) -> bool:
    """
    update something

    Args:
      entryType (str): entry to create, e.g. experiments, items, items_types
      identifier (int): elabFTW's identifier
      uploadID (int): identifier of the upload
      content (dict): content to update

    Returns:
      bool: success of operation
    """
    url = f'{self.url}{entryType}/{identifier}/uploads/{uploadID}'
    print(url)
    response = requests.patch(url, data=json.dumps(content), **self.param)
    return response.status_code == 200


  def uploadDelete(self, entryType:str, identifier:int, uploadID:int) -> bool:
    """
    delete an upload

    Args:
      entryType (str): entryType to create, e.g. experiments, items, items_types
      identifier (int): elabFTW's identifier
      uploadID (int): identifier of the upload

    Returns:
      bool: success of operation
    """
    response = requests.delete(f'{self.url}{entryType}/{identifier}/uploads/{uploadID}', **self.param)
    if response.status_code == 204:
      return True
    print(f"**ERROR occurred in upload delete of url {entryType}/{identifier}/uploads/{uploadID}")
    return False


  def download(self, entryType:str, identifier:int, elabData:dict[str,str]) -> dict[str,Any]:
    """ Download a file, aka previous upload

    Args:
      entryType (str): entryType to create, e.g. experiments, items, items_types
      identifier (int): elabFTW's identifier
      elabData (dict): elabFTW's data of the upload

    Returns:
      str: downloaded content str or byte-array
    """
    url = f"{self.url}{entryType}/{identifier}/uploads/{elabData['id']}?format='binary'"
    response = requests.get(url, **self.param)
    if response.status_code == 200:
      if elabData["real_name"]== "do_not_change.json":
        return json.loads(response.content.decode('utf-8'))
      print('**ERROR I do not know what to do')
    print(elabData,response.status_code, url)
    return {}


# TO TEST API

# New that works
# print('\nItems types',json.dumps(self.api.read('items_types'), indent=2))
# self.api.delete('items_types/10')

# OLD ---
# print(json.dumps(crud(backend, projectGroup, 'items_types/4'), indent=2))
# #print(crud(backend, projectGroup, 'items_types/4', 'update', {"body":"some json string"}))
# url = 'experiments/1'  #full detail
# print('\nExperiment1',json.dumps(crud(backend, projectGroup, url), indent=2))
# url = 'info'  #version number
# print('\nINFO',json.dumps(crud(backend, projectGroup, url), indent=2))
# url = 'experiments'  #summary
# print('\nExperiments',json.dumps(crud(backend, projectGroup, url), indent=2))
# url = 'items'  #summary
# print('\nItems',json.dumps(crud(backend, projectGroup, url), indent=2))
# url = 'items_types'  #all types incl. default
# crud(backend, projectGroup, url, 'create', {"title": "Go22Go"})
# print(crud(backend, projectGroup, f'{url}/5', 'update', {"color":"#aabbaa"}))
# print(json.dumps(crud(backend, projectGroup, f'{url}/5'), indent=2))
# print('\nItemTypes',json.dumps(crud(backend, projectGroup, url), indent=2))
