import json
from typing import Any
import requests
from .backend import Backend

def create(backend:Backend, projectGroup:str, urlSuffix:str) -> dict[str,Any]:
  return

def read(backend:Backend, projectGroup:str, urlSuffix:str) -> dict[str,Any]:
  """
  """
  url = backend.configuration['projectGroups'][projectGroup]['remote']['url']
  apiKey = backend.configuration['projectGroups'][projectGroup]['remote']['key']
  headers = {'Content-type': 'application/json', 'Authorization': apiKey}
  response = requests.get(url+urlSuffix, headers=headers, verify=False)
  return json.loads(response.content.decode('utf-8'))


def update(backend:Backend, projectGroup:str, urlSuffix:str) -> dict[str,Any]:
  return

def delete(backend:Backend, projectGroup:str, urlSuffix:str) -> dict[str,Any]:
  return



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
  url = 'experiments/1'  #full detail
  print('\nExperiment1',json.dumps(read(backend, projectGroup, url), indent=2))

  url = 'info'  #version number
  print('\nINFO',json.dumps(read(backend, projectGroup, url), indent=2))

  url = 'experiments'  #summary
  print('\nExperiments',json.dumps(read(backend, projectGroup, url), indent=2))

  url = 'items'  #summary
  print('\nItems',json.dumps(read(backend, projectGroup, url), indent=2))

  url = 'items_types'  #all types incl. default
  print('\nItemTypes',json.dumps(read(backend, projectGroup, url), indent=2))
  return True


