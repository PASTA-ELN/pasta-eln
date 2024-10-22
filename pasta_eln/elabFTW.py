import json
from typing import Any
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
"""

VERIFYSSL = False

def crud(backend:Backend, projectGroup:str, urlSuffix:str, operation:str='read', content:dict[str,Any]={}) -> dict[str,Any] | bool:
  """
  All Create-Read-Update-Delete operations in one function

  Args:
    backend (backend): backend
    projectGroup (str): name of project group
    urlSuffix (str): suffix of url, e.g. starting with experiments
    operation (str): create, read, update, delete
    content (dict): content to write

  Returns:
    dict or bool: content read/updated or success of operation
  """
  url = backend.configuration['projectGroups'][projectGroup]['remote']['url']
  apiKey = backend.configuration['projectGroups'][projectGroup]['remote']['key']
  headers = {'Content-type': 'application/json', 'Authorization': apiKey, 'Accept': 'text/plain'}
  if operation == 'create':
    response = requests.post(url+urlSuffix, headers=headers, data=json.dumps(content), verify=VERIFYSSL)
    if response.status_code == 201:
      return True
    print(f"**ERROR occurred in create of url {url}")
    return False
  elif operation == 'read':
    response = requests.get(url+urlSuffix, headers=headers, verify=VERIFYSSL)
    if response.status_code == 200:
      return json.loads(response.content.decode('utf-8'))
    else:
      print(f"**ERROR occurred in get of url {url}")
      return {}
  elif operation == 'update':
    response = requests.patch(url+urlSuffix, headers=headers, data=json.dumps(content), verify=VERIFYSSL)
    if response.status_code == 200:
      return json.loads(response.content.decode('utf-8'))
    return {}
  elif operation == 'delete':
    response = requests.delete(url+urlSuffix, headers=headers, verify=VERIFYSSL)
    if response.status_code == 204:
      return True
    print(f"**ERROR occurred in delete of url {url}")
    return False
  print('**ERROR occurred')


def initElabFTW(backend:Backend, projectGroup:str) -> bool:
  '''
  import .eln file from other ELN or from PASTA

  Args:
    backend (backend): backend
    elnFileName (str): name of file
    projID (str): project to import data into. If '', create a new project (only available for PastaELN)

  Returns:
    bool: success
  '''
  # test server
  elabVersion = int(crud(backend, projectGroup, 'info').get('elabftw_version','0.0.0').split('.')[0])
  if elabVersion<5:
    print('**ERROR old elab-ftw version')
    return False
  print(json.dumps(crud(backend, projectGroup, f'items_types/5'), indent=2))
  #try body and metadata: compare, write
  docTypesElab  = {i['title'] for i in crud(backend, projectGroup, 'items_types')}
  docTypesPasta = {i.capitalize() for i in backend.db.dataHierarchy('','') if not i.startswith('x')}
  for docType in docTypesPasta.difference(docTypesElab|{'Measurement'}):  # do not create measurements, use 'experiments'
    crud(backend, projectGroup, 'items_types', 'create', {"title": docType})
  return True



# url = 'experiments/1'  #full detail
# print('\nExperiment1',json.dumps(crud(backend, projectGroup, url), indent=2))

# url = 'info'  #version number
# print('\nINFO',json.dumps(crud(backend, projectGroup, url), indent=2))

# url = 'experiments'  #summary
# print('\nExperiments',json.dumps(crud(backend, projectGroup, url), indent=2))

# url = 'items'  #summary
# print('\nItems',json.dumps(crud(backend, projectGroup, url), indent=2))

# url = 'items_types'  #all types incl. default

#CRUD WORKS
# crud(backend, projectGroup, url, 'create', {"title": "Go22Go"})
# print(crud(backend, projectGroup, f'{url}/5', 'update', {"color":"#aabbaa"}))
# print(json.dumps(crud(backend, projectGroup, f'{url}/5'), indent=2))
# print('\nItemTypes',json.dumps(crud(backend, projectGroup, url), indent=2))
# return True


