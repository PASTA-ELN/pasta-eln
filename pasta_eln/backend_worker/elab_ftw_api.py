""" API for accessing an elabFTW server. That's API is inconvenient, complicated, ..."""
import base64
import copy
import json
import logging
import mimetypes
from pathlib import Path
from typing import Any
import requests  # only requirement; could be replaced with urllib to eliminate requirements


class ElabFTWApi:
  """ API for accessing an elabFTW server. That's API is inconvenient, complicated, ..."""


  def __init__(self, url:str='invalid', apiKey:str='', verifySSL:bool=True):
    '''
    initiate an elab instance to allow for syncing
    - test success by testing for self.url being set

    Args:
      url (str): url
      apiKey (str): API key
      veifySSL (bool): verify SSL certificate
    '''
    if url=='invalid':
      url = input('Please enter the url: ').strip()
      url = url if url.startswith('htt') else f'https://{url}'
      url = url if url.endswith('/')     else f'{url}/'
      print('Log-in to elabFTW server.')
      print(f'Go to website: {url}ucp.php?tab=4, enter a name and as permission: read/write. Create the API key')
      apiKey = input('Copy-paste the api-key: ').strip()

    # test server
    self.url = ''                                          #initialize: indicator if initialization successful
    self.headers = {'Content-type': 'application/json', 'Authorization': apiKey, 'Accept': 'text/plain'}
    self.param:dict[str,Any] = {'headers':self.headers, 'verify':verifySSL, 'timeout':10}
    self.session = requests.Session()
    try:
      response = self.session.get(f'{url}info', **self.param)
      if response.status_code == 200:
        elabVersion = int(json.loads(response.content.decode('utf-8')).get('elabftw_version','0.0.0').split('.')[0])
        if elabVersion<5:
          logging.error('Old elab-ftw version', exc_info=True)
        else:
          self.url   = url
      else:
        logging.error('Not an elab-ftw server', exc_info=True)
    except requests.ConnectionError:
      try:
        response = requests.get('https://www.google.com', headers={'Content-type': 'application/json'}, timeout=60)
        logging.error('Not an elab-ftw server or cannot connect to that server.', exc_info=True)
      except requests.ConnectionError:
        logging.error('Cannot connect to google. You are not online', exc_info=True)
    return


  def touchEntry(self, entryType:str, content:dict[str,Any] | None=None) -> int:
    """
    create entry of type: experiment, item/resource, without much content

    Args:
      entryType (str): entryType to create, e.g. experiments, items, items_types
      content (dict): content to create

    Returns:
      int: elabFTW id
    """
    response = self.session.post(self.url+entryType, data=json.dumps({} if content is None else content), **self.param)
    if response.status_code == 201:
      return int(response.headers['Location'].split('/')[-1])
    if response.status_code == 400:
      logging.error("Occurred in touch of url '%s': %s",entryType, json.loads(response.content.decode('utf-8'))
                    ['description'], exc_info=True)
    return -1


  def readEntry(self, entryType:str, identifier:int=-1) -> list[dict[str,Any]]:
    """
    read entry or all entries (use identifier=-1 in the latter case)
    - can also be used to read custom command: do not use identifier and give custom command as entryType

    Args:
      entryType (str): entryType to create, e.g. experiments, items, items_types, teams
      identifier (int): elabFTW's identifier; list all if none is given

    Returns:
      dict: content read
    """
    url = f'{self.url}{entryType}' if identifier==-1 else f'{self.url}{entryType}/{identifier}'
    response = self.session.get(url, **self.param)
    if response.status_code == 200:
      res = json.loads(response.content.decode('utf-8'))
      return res if identifier == -1 else [res]
    logging.error('Occurred in get of url %s / %s',entryType, identifier, exc_info=True)
    return [{}]


  def updateEntry(self, entryType:str, identifier:int, content:dict[str,Any] | None=None) -> bool:
    """
    update entry: experiment, item/resource

    Args:
      entryType (str): entryType to create, e.g. experiments, items, items_types
      identifier (int): elabFTW's identifier
      content (dict): content to update

    Returns:
      bool: success of operation
    """
    content = {} if content is None else content.copy()
    tags = content.pop('tags',[])
    response = self.session.patch(f'{self.url}{entryType}/{identifier}', data=json.dumps(content), **self.param)
    if response.status_code != 200:
      logging.error('Update failed for %s/%s: HTTP %s: %s. Content: %s', entryType, identifier,
                    response.status_code, response.text, {k: len(json.dumps(v)) for k, v in content.items()},)
      return False
    # separate tags handling
    # response = requests.get(f'{self.url}{entryType}/{identifier}/tags', **self.param) #allow to check existing tags
    for tag in tags:
      response = self.session.post(f'{self.url}{entryType}/{identifier}/tags', data=json.dumps({'tag':tag}),
                                   **self.param)
      if response.status_code != 201:
        logging.error('Tag update failed for %s/%s tag=%s: HTTP %s: %s', entryType, identifier, tag,
                      response.status_code, response.text)
        return False
    return True


  def deleteEntry(self, entryType:str, identifier:int) -> bool:
    """
    delete entry of type: experiment, item/resource

    Args:
      entryType (str): entryType to create, e.g. experiments, items, items_types
      identifier (int): elabFTW's identifier

    Returns:
      bool: success of operation
    """
    response = self.session.delete(f'{self.url}{entryType}/{identifier}', **self.param)
    if response.status_code == 204:
      return True
    logging.error('Occurred in delete of url %s', entryType, exc_info=True)
    return False


  ### ---------------------------------------------
  ### LINKS
  ### ---------------------------------------------
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
    response = self.session.post(f'{self.url}{entryType}/{identifier}/{targetType}_links/{linkTarget}', **self.param)
    if response.status_code == 201:
      return True
    logging.error('Occurred in create of url %s%s/%s/%s_links/%s : %s',self.url,entryType,identifier,targetType,
                  linkTarget,response.json, exc_info=True)
    return False



  ### ---------------------------------------------
  ### UPLOADS
  ### ---------------------------------------------
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
    # prepare upload data
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
    else:                                                                            #default for fast testing
      data = {'comment':comment, 'file': ('README.md', b'Read me!\n', 'text/markdown')}
    # upload that data
    headers = copy.deepcopy(self.headers)
    del headers['Content-type']                               #will automatically become 'multipart/form-data'
    response = self.session.post(f'{self.url}{entryType}/{identifier}/uploads', headers=headers,
                                 files=data, verify=self.param['verify'], timeout=60)
    if response.status_code == 201:
      return int(response.headers['Location'].split('/')[-1])
    logging.error('occurred in upload of url %s/%s : %s',entryType,identifier,
                  json.loads(response.content.decode('utf-8'))['description'], exc_info=True)
    return -1


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
    response = self.session.delete(f'{self.url}{entryType}/{identifier}/uploads/{uploadID}', **self.param)
    if response.status_code == 204:
      return True
    logging.error('occurred in upload delete of url %s/%s/uploads/%s',entryType,identifier,uploadID, exc_info=True)
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
    response = self.session.get(url, **self.param)
    if response.status_code == 200:
      if elabData['real_name']== 'do_not_change.json':
        return json.loads(response.content.decode('utf-8'))
      return {'data':response.content}
    return {}
