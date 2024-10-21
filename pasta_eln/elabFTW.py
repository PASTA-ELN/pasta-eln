import json
from typing import Any
import requests
from .backend import Backend

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
  # url = 'experiments/1'  #full detail
  # print('\nExperiment1',json.dumps(crud(backend, projectGroup, url), indent=2))

  # url = 'info'  #version number
  # print('\nINFO',json.dumps(crud(backend, projectGroup, url), indent=2))

  # url = 'experiments'  #summary
  # print('\nExperiments',json.dumps(crud(backend, projectGroup, url), indent=2))

  # url = 'items'  #summary
  # print('\nItems',json.dumps(crud(backend, projectGroup, url), indent=2))

  url = 'items_types'  #all types incl. default

  #CRUD WORKS
  # crud(backend, projectGroup, url, 'create', {"title": "Go22Go"})
  # crud(backend, projectGroup, f'{url}/6', 'delete')
  # print(crud(backend, projectGroup, f'{url}/5', 'update', {"color":"#aabbaa"}))
  # print(json.dumps(crud(backend, projectGroup, f'{url}/5'), indent=2))
  # print('\nItemTypes',json.dumps(crud(backend, projectGroup, url), indent=2))
  return True


