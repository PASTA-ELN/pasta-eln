#!/usr/bin/python3
"""Exercise API clients and the administrative command-line tools."""
import json
import logging
import warnings
from pathlib import Path

from pasta_eln.backend_worker.dataverse import DataverseClient
from pasta_eln.backend_worker.elab_ftw_api import ElabFTWApi
from pasta_eln.backend_worker.zenodo import ZenodoClient
from pasta_eln.installation_tools import exampleData
from pasta_eln.misc_tools import getConfiguration
from pasta_eln.tools import Tools


def test_api_and_tools(caplog):
  """Exercise configured remote clients and local administrative commands."""
  warnings.filterwarnings('ignore', category=ResourceWarning, module='PIL')
  logging.getLogger('urllib3').setLevel(logging.WARNING)
  testingConfigPath = Path.home()/'.pastaELN_testing.json'
  if not testingConfigPath.exists():
    print('**ERROR**: No testing configuration file found.')
    return
  configuration = json.loads(testingConfigPath.read_text())
  applicationConfiguration, _ = getConfiguration('research')

  # Recreate the disposable local data used by the administrative commands.
  exampleData(True, None, 'research', '')
  tools = Tools()
  tools.run(['research', 'h', 'ha', 's', 'v', 'q'])

  # Exercise the non-destructive local repair commands.
  tools.run(['research', 'rS', 'rp2', 'q'])

  # Check the configured eLabFTW API and read its project-group item.
  remote = applicationConfiguration['projectGroups']['research']['remote']
  elab = ElabFTWApi(remote['url'], remote['key'])
  assert elab.url
  assert elab.readEntry('items', remote['config']['id'])

  # Check the configured repository clients and metadata preparation paths.
  repositories = configuration['repositories']
  zenodo = ZenodoClient(repositories['zenodo']['url'], repositories['zenodo']['key'])
  assert zenodo.checkServer()[0]
  metadata = {'author': {'first': 'Coverage', 'last': 'Test', 'orcid': '',
                         'email': 'coverage@example.com',
                         'organizations': [{'organization': 'PASTA-ELN'}]},
              'title': 'Coverage test', 'description': 'Coverage test',
              'keywords': ['coverage'], 'category': 'computer-science', 'additional': {}}
  assert zenodo.prepareMetadata(metadata)
  dataverse = DataverseClient(repositories['dataverse']['url'], repositories['dataverse']['key'],
                              repositories['dataverse']['dataverse'])
  assert dataverse.checkServer()[0]
  assert dataverse.prepareMetadata(metadata)

  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f'Logging errors found: {[record.getMessage() for record in errors]}'
