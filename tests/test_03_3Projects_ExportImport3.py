#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create 3 projects; simplified form of testTutorialComplex """
import os, shutil, logging, json
import warnings
import unittest
from pathlib import Path
from typing import Any
from zipfile import ZipFile, ZIP_DEFLATED
import pytest
from pasta_eln.backend import Backend
from pasta_eln.inputOutput import exportELN, importELN
from pasta_eln.miscTools import outputString
from pasta_eln.miscTools import DummyProgressBar


class TestStringMethods(unittest.TestCase):
  """
  derived class for this test
  """
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.be = None
    self.dirName = ''

  @pytest.mark.skip(
    reason="Disabled for github since cannot create couchdb instance during actions")
  def test_main(self):
    """
    main function
    """
    ####### testELNFile to be the same in all tests that export/import
    def testELNFile(fileName:str, verbose=True) -> None:
      """
      an test that is similar to the test of TheELNConsortium
      - copied here for portability

      Args:
        fileName (str): file name of .eln to test
      """
      # global variables worth discussion
      ROCRATE_NOTE_MANDATORY = ['version','sdPublisher']
      DATASET_MANDATORY = ['name']
      DATASET_SUGGESTED = ['author','mentions',  'dateCreated', 'dateModified', 'identifier', 'text', 'keywords']
      FILE_MANDATORY = ['name']
      FILE_SUGGESTED = ['sha256', 'encodingFormat', 'contentSize', 'description']

      # runtime global variables
      METADATA_FILE = 'ro-crate-metadata.json'
      OUTPUT_INFO = False
      OUTPUT_COUNTS = True
      KNOWN_KEYS = DATASET_MANDATORY+DATASET_SUGGESTED+FILE_MANDATORY+FILE_SUGGESTED+['@id', '@type']

      logJson = {}
      def processNode(graph: list[dict[str,Any]], nodeID:str) -> bool:
        """
        recursive function call to process each node

        Args:
        graph: full graph
        nodeID: id of node in graph
        """
        globalSuccess = True
        nodes = [i for i in graph if '@id' in i and i['@id'] == nodeID]
        if len(nodes)!=1:
          print('**ERROR: all entries must only occur once in crate. check:', nodeID)
          return False
        node = nodes[0]
        # CHECK IF MANDATORY AND SUGGESTED KEYWORDS ARE PRESENT
        if '@type' not in node:
          print('**ERROR: all nodes must have @type. check:', nodeID)
        if node['@type'] == 'Dataset':
          for key in DATASET_MANDATORY:
            if not key in node:
              print(f'**ERROR in dataset: "{key}" not in @id={node["@id"]}')
              globalSuccess = False
          for key in DATASET_SUGGESTED:
            if not key in node and OUTPUT_INFO and verbose:
              print(f'**INFO for dataset: "{key}" not in @id={node["@id"]}')
        elif node['@type'] == 'File':
          for key in FILE_MANDATORY:
            if not key in node:
              print(f'**ERROR in file: "{key}" not in @id={node["@id"]}')
              globalSuccess = False
          for key in FILE_SUGGESTED:
            if not key in node and OUTPUT_INFO and verbose:
                print(f'**INFO for file: "{key}" not in @id={node["@id"]}')
        # CHECK PROPERTIES FOR ALL KEYS
        if any(str(i).strip()=='' for i in node.values()):
          print(f'**WARNING: {nodeID} contains empty values in the key-value pairs', node)
        # SPECIFIC CHECKS ON CERTAIN KEYS
        if isinstance(node.get('keywords', ''), list):
          print(f'**ERROR: {nodeID} contains an array of keywords. Use comma or space separated string')
          globalSuccess = False
        # recurse to children
        children = node.pop('hasPart') if 'hasPart' in node else []
        for child in children:
          globalSuccess = processNode(graph, child['@id']) and globalSuccess
        return globalSuccess

      if verbose:
        print(f'\n\nParse: {fileName}')
      with ZipFile(fileName, 'r', compression=ZIP_DEFLATED) as elnFile:
        success = True
        metadataJsonFile = [i for i in elnFile.namelist() if i.endswith(METADATA_FILE)][0]
        with elnFile.open(metadataJsonFile) as roCrateFile:
          metadataContent = json.loads(roCrateFile.read())
        graph = metadataContent["@graph"]
        # find information from master node
        ro_crate_nodes = [i for i in graph if i["@id"] == METADATA_FILE]
        if len(ro_crate_nodes) == 1:
          for key in ROCRATE_NOTE_MANDATORY:
            if not key in ro_crate_nodes[0]:
              print(f'**ERROR: "{key}" not in @id={METADATA_FILE}')
        else:
          print(f'**ERROR: @id={METADATA_FILE} does not uniquely exist ')
          success = False
        main_node = [i for i in graph if i["@id"] == "./"][0]

        # iteratively go through graph
        for partI in main_node['hasPart']:
          success = processNode(graph, partI['@id']) and success
        if fileName not in logJson:
          logJson[fileName] = {'params_metadata_json':success}
        else:
          logJson[fileName] = logJson[fileName] | {'params_metadata_json':success}

        # count occurrences of all keys
        counts:dict[str,int] = {}
        for node in graph:
          if node['@id'] in ['./',METADATA_FILE]:
            continue
          for key in node.keys():
            if key in counts:
              counts[key] += 1
            else:
              counts[key] = 1
        view = [ (v,k) for k,v in counts.items() ]
        view.sort(reverse=True)
        if OUTPUT_COUNTS:
          if verbose:
            print('===== Counts (* unspecified)')
          for v,k in view:
            prefix = '   ' if k in KNOWN_KEYS else ' * '
            if verbose:
              print(f'{prefix}{k:15}: {v}')
      if verbose:
        print('\n\nSuccess:', success)
      return
    #### End testELNFile

    # main test function: create stuff, test, ...
    outputFormat = 'print'
    # initialization: create database, destroy on filesystem and database and then create new one
    warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
    warnings.filterwarnings('ignore', message='invalid escape sequence')
    warnings.filterwarnings('ignore', category=ResourceWarning, module='PIL')
    warnings.filterwarnings('ignore', category=ImportWarning)
    projectGroup = 'research'
    self.be = Backend(projectGroup, initConfig=False)

    # change documents
    docIDs = [i.split('|')[-1].strip() for i in self.be.output('procedure',True).split('\n')[2:-1]]
    docIDs +=[i.split('|')[-1].strip() for i in self.be.output('sample',True).split('\n')[2:-1]]
    for idx,docID in enumerate(docIDs):
      doc = self.be.db.getDoc(docID)
      doc['comment'] = f'Test string {idx}'
      self.be.editData(doc)

    # export
    viewProj = self.be.db.getView('viewDocType/x0')
    idProjects  = [i['id'] for i in viewProj]
    self.fileName = str(Path.home()/'temporary_pastaTest.eln')
    status = exportELN(self.be, idProjects, self.fileName, ['procedure','measurement','sample'])
    print(f'Export to: {self.fileName}\n{status}')
    self.assertEqual(status[:21],'Success: exported 17 ','Export unsuccessful')

    # verify eln
    print('\n\nEnd export\n----------------------\nStart verification')
    testELNFile(self.fileName, False)

    # IMPORT NOT IMPLEMENTED YET
    # # remove old
    # docProj = self.be.db.getDoc(idProj)
    # oldPath = self.be.basePath/docProj['-branch'][0]['path']
    # shutil.rmtree(oldPath)
    # allDocs = self.be.db.getView('viewHierarchy/viewHierarchy',    startKey=idProj)
    # for doc in allDocs:
    #   self.be.db.remove(doc['id'])

    # # import
    # print('\n\n---------------\nImport')
    # status = importELN(self.be, self.fileName)
    # print(status)
    # self.assertEqual(status[:7],'Success','Import unsuccessful')

    #test / verify
    print('Number of documents', len(self.be.db.getView('viewHierarchy/viewHierarchy')))
    outputString(outputFormat,'h2','VERIFY DATABASE INTEGRITY')
    outputString(outputFormat,'info', self.be.checkDB(outputStyle='text'))
    outputString(outputFormat,'h2','DONE WITH VERIFY')
    fileCount = 0
    for _, _, files in os.walk(self.be.basePath):
      fileCount+=len(files)
    print(f'Number of files 16 (should be) = {fileCount} (are)')
    self.assertEqual(fileCount, 16, 'Imported entries are not 16, as they should.')
    return

  def tearDown(self):
    logging.info('End Export-import test')
    # Path(self.fileName).unlink()  #remove file
    return


if __name__ == '__main__':
  unittest.main()
