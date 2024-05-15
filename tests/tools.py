import json
import pytest
from typing import Any
from zipfile import ZipFile, ZIP_DEFLATED

@pytest.mark.skip(
    reason="Disabled for github since cannot create couchdb instance during actions")
def testELNFile(fileName:str) -> None:
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
        if not key in node and OUTPUT_INFO:
          print(f'**INFO for dataset: "{key}" not in @id={node["@id"]}')
    elif node['@type'] == 'File':
      for key in FILE_MANDATORY:
        if not key in node:
          print(f'**ERROR in file: "{key}" not in @id={node["@id"]}')
          globalSuccess = False
      for key in FILE_SUGGESTED:
        if not key in node and OUTPUT_INFO:
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
      print('===== Counts (* unspecified)')
      for v,k in view:
        prefix = '   ' if k in KNOWN_KEYS else ' * '
        print(f'{prefix}{k:15}: {v}')
  print('\n\nSuccess:', success)
  return
