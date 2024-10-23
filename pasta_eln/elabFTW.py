import json, copy
from typing import Any
from anytree import PostOrderIter
import requests
from .backend import Backend
"""
# Pasta sync: Ask Nico
1. feasible: create resources: instruments, samples, procedures, folders
	- a project folder is first created and then references (as link) the content (experiments)
1. info: reduce the experiment to measurement: attachment is the ONE measurement file and a thumbnail of the measurement
1. question: samples have as one of their extra fields a qr-code: can I create a liist of all qr-codes: via API can I create a list of all extra-fileds of a specific resoruce type?
	- or should I create another resource: list: which then includes the qr-code list
	- go to search page as a API request q=parameter=%

## Other topics
- chatGPT-Scholar: only tool

https://doc.elabftw.net/api/elabapi-html/#api-Items-postItem
"""

VERIFYSSL = False

class Pasta2Elab:

  def __init__(self, backend:Backend, projectGroup:str):
    '''
    initiate an elab instance to allow for syncing: save data-hierarchy information
    - cannot save pasta's measurement data hierarchy in any other docTypes; hence, makes no sense to save any data hierarchy
      into any elab-item-types metadata

    Args:
      backend (backend): backend
      projectGroup (str): name of project group

    Returns:
      bool: success
    '''
    self.backend = backend
    self.projectGroup = projectGroup
    self.url = self.backend.configuration['projectGroups'][self.projectGroup]['remote']['url']
    apiKey = self.backend.configuration['projectGroups'][self.projectGroup]['remote']['key']
    self.headers = {'Content-type': 'application/json', 'Authorization': apiKey, 'Accept': 'text/plain'}
    # test server
    elabVersion = int(self.read('info').get('elabftw_version','0.0.0').split('.')[0])
    if elabVersion<5:
      print('**ERROR old elab-ftw version')
      return
    #try body and metadata: compare, write
    docTypesElab  = {i['title']:i['id'] for i in self.read('items_types')}
    docTypesPasta = {i.capitalize() for i in backend.db.dataHierarchy('','') if not i.startswith('x')} |{'Folder','Project','Pasta_Metadata'}
    for docType in docTypesPasta.difference({'Measurement'}|docTypesElab.keys()):  # do not create measurements, use 'experiments'
      self.touch('items_types', {"title": docType})
    #verify nothing extraneous
    docTypesElab  = {i['title']:i['id'] for i in self.read('items_types')}
    if set(docTypesElab.keys()).difference(docTypesPasta|{'Default','Pasta_Metadata'}):
      print('**ERROR: some items exist that should not:', set(docTypesElab.keys()).difference(docTypesPasta|{'Default'}))
    listMetadata = self.read('items?q=category%3APasta_Metadata')
    dataHierarchy = []
    for docType in backend.db.dataHierarchy('',''):
        dataHierarchy += copy.deepcopy([dict(i) for i in backend.db.dataHierarchy(docType,'meta')])
    if not listMetadata:
      itemId = self.touch('items', {"category_id":int(docTypesElab["Pasta_Metadata"])})
    else:
      itemId = listMetadata[0]["id"]
    self.update(f'items/{itemId}', {"title":"data hierarchy", "metadata":json.dumps(dataHierarchy), "body":"<p>DO NOT CHANGE ANYTHING</p>"})
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


  def pasta2elab(self) -> bool:
    '''
    import .eln file from other ELN or from PASTA

    Args:
      backend (backend): backend
      projectGroup (str): name of project group

    Returns:
      bool: success
    '''
    print('\nItems',json.dumps(self.read('items'), indent=2))
    # for projID in self.backend.db.getView('viewDocType/x0')['id'].values:
    #   proj = self.backend.db.getHierarchy(projID)
    #   for node in PostOrderIter(proj):
    #     print(node.name)
    return True

# New that works
# print('\nItems types',json.dumps(self.read('items_types'), indent=2))
# self.delete('items_types/10')

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
