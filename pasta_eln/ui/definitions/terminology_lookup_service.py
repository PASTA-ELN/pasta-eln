""" Terminology Lookup service """
#  PASTA-ELN and all its sub-parts are covered by the MIT license
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: terminology_lookup_service.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import reduce
from os import getcwd
from os.path import dirname, join, realpath
from typing import Any
import requests
from PySide6.QtGui import QPixmap
from .terminology_lookup_config import lookupConfig


class TerminologyLookupService:
  """
  Terminology Lookup service which allows user to query for a search term online
  A list of online portals (lookupConfig) are queried for the search term
  and the results (dict(information, iri)) are returned
  """
  def __init__(self) -> None:
    self.sessionTimeout = 10                 # Timeout in seconds for the requests send to the lookup services


  async def doLookup(self, searchTerm: str) -> list[dict[str, Any]]:
    """
    Do the lookup for the search term using the services in the lookupConfig
    Args:
      searchTerm (str): Search term used for the lookup

    Returns: List of IRI information for the search term crawled online using the services in the lookupConfig
    In case of error, an empty list is returned and errors is updated with failures
    """
    if not searchTerm.strip():
      return []
    errors = []
    results = []

    # Define a function to perform the HTTP request
    def fetchService(service: dict[str, Any]) -> dict[str, str] | None:
      try:
        service['request_params'][service['search_term_key']] = searchTerm
        response = requests.get(service['url'], params=service['request_params'], headers=service.get('header',{}),
                                timeout=self.sessionTimeout)
        if response.status_code == 200:
          webResult = response.json()
          return self.parseWebResult(searchTerm, webResult, service)
        else:
          errors.append(f"Error querying {service['name']}: {response.status_code} {response.reason}")
      except requests.RequestException as e:
        errors.append(f"Exception querying {service['name']}: {str(e)}")
      return None

    # Use ThreadPoolExecutor to run requests in parallel
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
      tasks = [loop.run_in_executor(executor, fetchService, service) for service in lookupConfig]
      fetchedResults = await asyncio.gather(*tasks)
    # Collect valid results
    for result in fetchedResults:
      if result:
        results.append(result)
    # Log any errors
    if errors:
      logging.error('Session request errors: %s', errors, exc_info=True)
    return results


  def parseWebResult(self, searchTerm: str, webResult: dict[str, Any], lookupService: dict[str, Any]) -> dict[str, Any]:
    """
    Parse the web result returned by querying the lookup service for the search term
    Args:
      searchTerm (str): Search term used for the lookup
      webResult (dict[str, Any]): Web result returned by querying the lookup service
      lookupService (dict[str, Any]): Lookup service taken from the lookupConfig

    Returns (dict[str, Any]): Dictionary containing the name, search term and results which is a list of dict(iri, information)
    """
    if (not searchTerm or not webResult or not lookupService):
      logging.error('Invalid search term or web result or lookup service!', exc_info=True)
      return {}
    retrievedResults: dict[str, Any] = {'name': lookupService['name'], 'search_term': searchTerm, 'results': []}
    # Get mandatory attributes
    resultKeys = lookupService['search_criteria']['results_keys']
    descKeys = lookupService['search_criteria']['description_keys']
    idKey = lookupService['search_criteria']['id_key']
    # Get non mandatory attributes
    duplicateOntologyNames = lookupService.get('duplicate_ontology_names')
    skipDesc = lookupService.get('skip_description')
    duplicateOntologyKey = lookupService['search_criteria'].get('ontology_name_key')
    results = reduce(lambda d, key: d.get(key) if d else None, resultKeys,  webResult)# type: ignore[arg-type, return-value]
    for item in results or []:
      description = reduce(lambda d, key: d.get(key) if d else '', descKeys, item)# type: ignore[attr-defined]
      isDuplicate = (item[duplicateOntologyKey] in duplicateOntologyNames) if duplicateOntologyKey else False# type: ignore[operator]
      if (description and description != skipDesc and not isDuplicate):
        retrievedResults['results'].append({
            'iri': f"{lookupService['iri_prefix']}{item[idKey]}"
            if lookupService.get('iri_prefix') else item[idKey],
            'information': ','.join(description) if isinstance(description, list)
            else description})
    return retrievedResults


  def getIconDict(self) -> dict[str, QPixmap]:
    """
    Get the icon names for the lookup services
    Returns (list[str]): List of icon names for the lookup services
    """
    currentPath = realpath(join(getcwd(), dirname(__file__)))
    resourcesPath = join(currentPath, '../../Resources/Icons')
    return {data['name'] : QPixmap(join(resourcesPath, f'{data["icon_name"]}')).scaledToWidth(50)
            for data in lookupConfig}
