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
from functools import reduce
from json import load, loads
from os import getcwd
from os.path import dirname, join, realpath
from typing import Any

from aiohttp import ClientSession


class TerminologyLookupService:
  """
  Terminology Lookup service which allows user to query for a search term online
  A list of online portals (terminology_lookup_config.json) are queried for the search term
  and the results (dict(information, iri)) are returned
  """

  def __init__(self) -> None:
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.session_timeout = 10  # Timeout in seconds for the requests send to the lookup services

  async def get_request(self,
                        base_url: str,
                        request_params: dict[str, Any] = {}) -> dict[str, Any]:
    """
    Send get request to the given url and parameters
    Args:
      base_url (str): Base url
      request_params (dict[str, Any]): Request parameters for the get request

    Returns: The response text for the request is returned

    """
    self.logger.info("Requesting url: %s, params: %s", base_url, request_params)
    async with ClientSession() as session:
      try:
        async with session.get(base_url,
                               params=request_params,
                               timeout=self.session_timeout) as response:
          return loads(await response.text())
      except asyncio.exceptions.TimeoutError as e:
        self.logger.error("Client session timeout for url (%s) with error: %s",
                          base_url,
                          e)
        return {}
      except TypeError as e:
        self.logger.error("Client session type error for url (%s) with error: %s",
                          base_url,
                          e)
        return {}

  async def do_lookup(self,
                      search_term: str) -> list[dict[str, Any]]:
    """
    Do the lookup for the search term using the services in the terminology_lookup_config.json
    Args:
      search_term (str): Search term used for the lookup

    Returns: List of IRI information for the search term crawled online using the services in the terminology_lookup_config.json

    """
    self.logger.info("Searching for term: %s", search_term)
    current_path = realpath(join(getcwd(), dirname(__file__)))
    results = list[dict[str, Any]]()
    with open(join(current_path, "terminology_lookup_config.json"), encoding="utf-8") as config_file:
      for lookup_service in load(config_file):
        lookup_service['request_params'][lookup_service['search_term_key']] = search_term
        web_result = await self.get_request(lookup_service['url'], lookup_service['request_params'])
        result = self.parse_web_result(search_term,
                                       web_result,
                                       lookup_service)
        results.append(result)
    return results

  def parse_web_result(self,
                       search_term: str,
                       web_result: dict[str, Any],
                       lookup_service: dict[str, Any]) -> dict[str, Any]:
    """
    Parse the web result returned by querying the lookup service for the search term
    Args:
      search_term (str): Search term used for the lookup
      web_result (dict[str, Any]): Web result returned by querying the lookup service
      lookup_service (dict[str, Any]): Lookup service taken from the terminology_lookup_config.json

    Returns (dict[str, Any]): Dictionary containing the name, search term and results which is a list of dict(iri, information)

    """
    self.logger.info("Searching term: %s for online service: %s",
                     search_term,
                     lookup_service.get('name'))
    retrieved_results: dict[str, Any] = {
      "name": lookup_service.get('name'),
      "search_term": search_term,
      "results": []
    }
    duplicate_ontology_names = lookup_service.get('duplicate_ontology_names')
    result_keys = lookup_service.get('search_criteria').get('results_keys')  # type: ignore[union-attr]
    desc_keys = lookup_service.get('search_criteria').get('description_keys')  # type: ignore[union-attr]
    id_key = lookup_service.get('search_criteria').get('id_key')  # type: ignore[union-attr]
    duplicate_ontology_key = lookup_service.get('search_criteria').get('ontology_name_key')  # type: ignore[union-attr]
    results = reduce(lambda d, key: d.get(key) if d else None, result_keys,  # type: ignore[arg-type,return-value]
                     web_result)
    for item in results if results else []:
      description = reduce(lambda d, key: d.get(key) if d else None, desc_keys, item)  # type: ignore[attr-defined]
      is_duplicate = (item.get(duplicate_ontology_key)  # type: ignore[attr-defined,operator]
                      in duplicate_ontology_names) if duplicate_ontology_key else False
      if (description
          and description != lookup_service.get('skip_description')
          and not is_duplicate):
        retrieved_results["results"].append(
          {
            "iri": f"{lookup_service.get('iri_prefix')}{item.get(id_key)}"  # type: ignore[attr-defined]
            if lookup_service.get('iri_prefix') else item.get(id_key),  # type: ignore[attr-defined]
            "information": ",".join(description) if isinstance(description, list)
            else description
          }
        )
    return retrieved_results
