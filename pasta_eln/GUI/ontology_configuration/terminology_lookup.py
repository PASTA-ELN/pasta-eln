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

import aiohttp


class TerminologyLookup(object):

  def __init__(self):
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

  async def get_request(self,
                        base_url: str,
                        request_params: dict[str, Any] = None) -> str:
    """
    Send get request to the given url and parameters
    Args:
      base_url (str): Base url
      request_params (dict[str, Any]): Request parameters for the get request

    Returns: The response text for the request is returned

    """
    self.logger.info("Requesting url: {0}, params: {1}", base_url, request_params)
    async with aiohttp.ClientSession() as session:
      async with session.get(base_url, params=request_params) as response:
        return await response.text()

  async def do_lookup(self, search_term: str) -> str:
      """

      Args:


      Returns:

      """
      self.logger.info("Searching for term: %s", search_term)
      current_path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
      lookup_data = json.load(open(os.path.join(current_path, 'terminology_lookup_config.json')))
      for item in lookup_data:
        item['request_params'][item['search_term_key']] = search_term
        test = await self.get_request(item['url'], item['request_params'])


