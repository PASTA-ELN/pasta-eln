#!/usr/bin/python3
"""TEST the form """
import logging, warnings, json
from pathlib import Path
from pasta_eln.backend import Backend
from pasta_eln.GUI.repositories.repository import RepositoryClient
from pasta_eln.GUI.repositories.dataverse import DataverseClient
from pasta_eln.GUI.repositories.zenodo import ZenodoClient
from .misc import verify, handleReport

def test_simple(qtbot):
  """
  main function
  """
  # initialization: create database, destroy on filesystem and database and then create new one
  warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
  warnings.filterwarnings('ignore', message='invalid escape sequence')
  warnings.filterwarnings('ignore', category=ResourceWarning, module='PIL')
  warnings.filterwarnings('ignore', category=ImportWarning)
  logPath = Path.home()/'pastaELN.log'
  logging.basicConfig(filename=logPath, level=logging.INFO, format='%(asctime)s|%(levelname)s:%(message)s',
                      datefmt='%m-%d %H:%M:%S')   #This logging is always info, since for installation only
  for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib.font_manager']:
    logging.getLogger(package).setLevel(logging.WARNING)

  # setup
  backend = Backend('research')
  if not (Path.home()/'.pastaELN_testing.json').exists():
    print('**ERROR**: No testing configuration file found.')
    return
  configuration = json.load(open(Path.home()/'.pastaELN_testing.json', 'r'))
  conf = configuration['repositories']

  # test default: should all fail
  client = RepositoryClient('www.example.com', 'test')
  assert client.checkServer()[0] == False
  assert client.checkAPIKey() == False
  assert client.uploadRepository({'metadata':'some'}, '/home/example/file.txt')[0] == False

  # test zenodo
  metadataZenodo = {
    "metadata": {
        "title": "My Sample Dataset",
        "upload_type": "dataset",
        "description": "This is a test dataset uploaded via the Zenodo API.",
        "creators": [
            {"name": "Doe, John", "affiliation": "Example University"}
        ],
        "keywords": ["test", "zenodo", "api", "python"],
        "publication_date": "2025-04-04",
        "access_right": "open",
        "license": "CC-BY-4.0"
    }
  }
  client = ZenodoClient(conf['zenodo']['url'], conf['zenodo']['key'])
  assert client.checkServer()[0]
  assert client.checkAPIKey()
  res = client.uploadRepository(metadataZenodo, '/home/steffen/workflows.md')  #TODO change
  print(f'Zenodo test {res[1]}')
  assert res[0]

  # test dataverse
  metadataDataverse = {
    "datasetVersion": {
      "metadataBlocks": {
        "citation": {
          "fields": [
            {
              "typeName": "title",
              "value": "Default Dataset Title",
              "typeClass": "primitive"
            },
            {
              "typeName": "author",
              "value": [
                {
                  "authorName": {
                    "value": "Default Author"
                  },
                  "authorAffiliation": {
                    "value": "Default Institution"
                  }
                }
              ],
              "typeClass": "compound"
            },
            {
              "typeName": "datasetContact",
              "value": [
                {
                  "datasetContactEmail": {
                    "value": "contact@example.com"
                  },
                  "datasetContactName": {
                    "value": "Default Contact"
                  }
                }
              ],
              "typeClass": "compound"
            },
            {
              "typeName": "dsDescription",
              "value": [
                {
                  "dsDescriptionValue": {
                    "value": "This is a default description for the dataset."
                  }
                }
              ],
              "typeClass": "compound"
            },
            {
              "typeName": "subject",
              "value": ["Computer and Information Science"],
              "typeClass": "controlledVocabulary"
            }
          ]
        }
      }
    }
  }
  client = DataverseClient(conf['dataverse']['url'], conf['dataverse']['key'], conf['dataverse']['dataverse'])
  assert client.checkServer()[0]
  assert client.checkAPIKey()
  res = client.uploadRepository(metadataDataverse, '/home/steffen/workflows.md')#TODO change
  print(f'Dataverse test {res[1]}')
  assert res[0]
  # other tests
  print('\n\nOther tests:')
  assert client.checkAPIKeyExpired() == False
  # client.recreateAPIKey() #Not tested
  print(client.getDataverseList(),'\n')
  print(client.getDataverseContent(),'\n')
  print(client.getDataverseSize(),'\n')
  print(client.getDataverseInfo(),'\n')
  print('\n\nDataset:')
  # client.createDataverse()  #Not tested
  doi = res[1].split(' ')[1][:-1]
  print(client.getDatasetInfo(doi),'\n')
  print(client.getDatasetVersions(doi),'\n')
  print(client.getDatasetLocks(doi),'\n')
  print(client.getDatasetFiles(doi),'\n')
  print(client.getDatasetMetadata(doi),'\n')
  # print(client.deletePublishedDataset(doi)) #can only be done by superuser
  # print(client.deleteEmptyDataverse()) #not tested
  # print(client.deleteNonEmptyDataverse()) #not tested
