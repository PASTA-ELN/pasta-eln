""" Terminology Lookup service """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: terminology_lookup_service.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import reduce
from json import load
from os import getcwd
from os.path import dirname, join, realpath
from typing import Any
import requests
from PySide6.QtGui import QPixmap


class TerminologyLookupService:
  """
  Terminology Lookup service which allows user to query for a search term online
  A list of online portals (terminology_lookup_config.json) are queried for the search term
  and the results (dict(information, iri)) are returned
  """

  def __init__(self) -> None:
    self.session_timeout = 10                # Timeout in seconds for the requests send to the lookup services
    current_path = realpath(join(getcwd(), dirname(__file__)))
    self.lookupConfig = join(current_path, 'terminology_lookup_config.json')


  async def do_lookup(self, search_term: str) -> list[dict[str, Any]]:
    """
    Do the lookup for the search term using the services in the terminology_lookup_config.json
    Args:
      search_term (str): Search term used for the lookup

    Returns: List of IRI information for the search term crawled online using the services in the terminology_lookup_config.json
    In case of error, an empty list is returned and errors is updated with failures
    """
    if not search_term.strip():
      return []
    errors = []
    results = []
    # Load the lookup configuration
    with open(self.lookupConfig, encoding='utf-8') as config_file:
      lookup_services = load(config_file)

    # Define a function to perform the HTTP request
    def fetch_service(service: dict[str, Any]) -> dict[str, str] | None:
      try:
        service['request_params'][service['search_term_key']] = search_term
        response = requests.get(service['url'], params=service['request_params'],
          timeout=self.session_timeout)
        if response.status_code == 200:
          web_result = response.json()
          return self.parse_web_result(search_term, web_result, service)
        else:
          errors.append(f"Error querying {service['name']}: {response.status_code} {response.reason}")
      except requests.RequestException as e:
        errors.append(f"Error querying {service['name']}: {str(e)}")
      return None

    # Use ThreadPoolExecutor to run requests in parallel
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
      tasks = [loop.run_in_executor(executor, fetch_service, service) for service in lookup_services]
      fetched_results = await asyncio.gather(*tasks)
    # Collect valid results
    for result in fetched_results:
      if result:
        results.append(result)
    # Log any errors
    if errors:
      logging.error('Session request errors: %s', errors)
    return results


  def parse_web_result(self, search_term: str, web_result: dict[str, Any], lookup_service: dict[str, Any]) -> dict[str, Any]:
    """
    Parse the web result returned by querying the lookup service for the search term
    Args:
      search_term (str): Search term used for the lookup
      web_result (dict[str, Any]): Web result returned by querying the lookup service
      lookup_service (dict[str, Any]): Lookup service taken from the terminology_lookup_config.json

    Returns (dict[str, Any]): Dictionary containing the name, search term and results which is a list of dict(iri, information)
    """
    if (not search_term or not web_result or not lookup_service):
      logging.error('Invalid search term or web result or lookup service!')
      return {}
    retrieved_results: dict[str, Any] = {'name': lookup_service['name'], 'search_term': search_term, 'results': []}
    # Get mandatory attributes
    result_keys = lookup_service['search_criteria']['results_keys']
    desc_keys = lookup_service['search_criteria']['description_keys']
    id_key = lookup_service['search_criteria']['id_key']
    # Get non mandatory attributes
    duplicate_ontology_names = lookup_service.get('duplicate_ontology_names')
    skip_desc = lookup_service.get('skip_description')
    duplicate_ontology_key = lookup_service['search_criteria'].get('ontology_name_key')
    results = reduce(lambda d, key: d.get(key) if d else None, result_keys,  web_result)# type: ignore[arg-type, return-value]
    for item in results or []:
      description = reduce(lambda d, key: d.get(key) if d else '', desc_keys, item)# type: ignore[attr-defined]
      is_duplicate = (item[duplicate_ontology_key] in duplicate_ontology_names) if duplicate_ontology_key else False# type: ignore[operator]
      if (description and description != skip_desc and not is_duplicate):
        retrieved_results['results'].append({
            'iri': f"{lookup_service['iri_prefix']}{item[id_key]}"
            if lookup_service.get('iri_prefix') else item[id_key],
            'information': ','.join(description) if isinstance(description, list)
            else description})
    return retrieved_results


  def getIconDict(self) -> dict[str, QPixmap]:
    """
    Get the icon names for the lookup services
    Returns (list[str]): List of icon names for the lookup services
    """
    current_path = realpath(join(getcwd(), dirname(__file__)))
    resources_path = join(current_path, '../../Resources/Icons')
    iconsPixMap = {}
    with open(self.lookupConfig, encoding='utf-8') as config_file:
      for data in load(config_file):
        iconsPixMap[data['name']] = QPixmap(join(resources_path, f'{data["icon_name"]}')).scaledToWidth(50)
    return iconsPixMap
