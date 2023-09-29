#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: terminology_lookup.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import json
import logging
import os
from typing import Any

from aiohttp import ClientSession


class TerminologyLookup(object):

  def __init__(self):
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

  async def get_request(self,
                        base_url: str,
                        request_params: dict[str, Any] = None) -> dict[str, Any]:
    """
    Send get request to the given url and parameters
    Args:
      base_url (str): Base url
      request_params (dict[str, Any]): Request parameters for the get request

    Returns: The response text for the request is returned

    """
    self.logger.info("Requesting url: {0}, params: {1}", base_url, request_params)
    async with ClientSession() as session:
      async with session.get(base_url, params=request_params) as response:
        return json.loads(await response.text())

  async def do_lookup(self, search_term: str) -> list[dict[str, Any]]:
    """

    Args:


    Returns:

    """
    self.logger.info("Searching for term: %s", search_term)
    current_path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    lookup_data = json.load(open(os.path.join(current_path, 'terminology_lookup_config.json')))
    results = list[dict[str, Any]]()
    for lookup_service in lookup_data:
      lookup_service['request_params'][lookup_service['search_term_key']] = search_term
      results.append(await self.get_request(lookup_service['url'], lookup_service['request_params']))
    return results
