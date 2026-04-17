#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create the default example that all installations create and verify it thoroughly """
import asyncio
import logging
import unittest
import warnings
from pasta_eln.misc_tools import getRORIDLabel, getORCIDName
from pasta_eln.add_ons.definition_autofill import getFirstWikidataEntry
from pasta_eln.ui.definitions.terminology_lookup_service import TerminologyLookupService

class TestStringMethods(unittest.TestCase):
  """
  derived class for this test
  """
  def test_main(self):
    """
    main function
    """
    # initialization: create database, destroy on filesystem and database and then create new one
    warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
    warnings.filterwarnings('ignore', message='invalid escape sequence')
    warnings.filterwarnings('ignore', category=ResourceWarning, module='PIL')
    warnings.filterwarnings('ignore', category=ImportWarning)
    for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib.font_manager']:
      logging.getLogger(package).setLevel(logging.WARNING)
    logging.info('Start 99 test')

    answer = getRORIDLabel('02nv7yv05')
    assert answer=='Forschungszentrum Jülich', f'RORID lookup failed: {answer}'
    answer = getRORIDLabel('042nb2s44')
    assert answer=='Massachusetts Institute of Technology', f'RORID lookup failed: {answer}'

    answer = getORCIDName('0000-0003-0930-082X')
    assert answer==('Steffen','Brinckmann'), f'ORCID lookup failed: {answer}'
    answer = getORCIDName('0000-0001-8940-2361')
    assert answer==('Ruth','Schwaiger'), f'ORCID lookup failed: {answer}'

    # Add-on form-auto.py cannot be tested since it requires secret API key
    answer = getFirstWikidataEntry('water')
    assert answer=='http://www.wikidata.org/entity/Q283', f'Wikidata lookup failed: {answer}'
    answer = getFirstWikidataEntry('glucose')
    assert answer=='http://www.wikidata.org/entity/Q37525', f'Wikidata lookup failed: {answer}'


    # pasta_eln/ui/definitions/terminology_lookup_service.py:
    tsService = TerminologyLookupService()
    for searchTerm in ['force','strain']:  #always use two terms
      answers = []
      successServices = set()
      eventLoop = asyncio.new_event_loop()
      asyncio.set_event_loop(eventLoop)
      if lookupResults := eventLoop.run_until_complete(tsService.doLookup(searchTerm)):
        for service in lookupResults:
          for result in service['results']:
            serviceShort = {'ontology_lookup_service':'OLS  ',
                            'tib_terminology_service':'TIB  ',
                            'wikipedia':'wiki ',
                            'wikidata':'wikiD'
                            }[service['name']]
            answers.append(f"{result['iri'][:30]:<30} {serviceShort}  {result['information'][:100]}")
            successServices.add(serviceShort.strip())
      listStr = '\n - '.join(answers)
      print(f'Search term: {searchTerm} \n - {listStr}')
      print('Services used:', ', '.join(sorted(successServices)),'\n')
      assert successServices=={'wikiD', 'wiki', 'TIB', 'OLS'}


    # elabFTW API is tested in testComplicated since it requires a secret API key. Hence do not test
    # - pasta_eln/ui/config/project_group.py;
    # - pasta_eln/backend_worker/elab_ftw_api.py

    # pasta_eln/backend_worker/input_output.py cannot be tested since it requires a specific location to test, which is known at this point in time

    # zenodo and dataverse API are tested in testComplicated since they require secret API keys
