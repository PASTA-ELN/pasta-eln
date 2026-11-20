"""Change the format of dictionaries"""
import difflib
import json
import logging
import re
import uuid
from collections.abc import Mapping
from datetime import datetime
from typing import TYPE_CHECKING, Any
from ..constants import SORTED_KEYS, SQLiteTranslation
from .string_changes import isDocID, markdownEqualizer, tuple2text

if TYPE_CHECKING:
  from ..backend_worker.sqlite import SqlLiteDB


def fillDocBeforeCreate(data:dict[str,Any], docType:list[str]) -> dict[str,Any]:
  """ Fill the data before submission to database with common data
  - type, project, children
  - separate comment into tags, fields
  - create id if needed

  used in backend.py and Store.js

  Args:
    data (dict): document to save
    docType (list): type of document, e.g. project=['x0']

  Returns:
    dict: document with common fields filled and nested fields flattened
  """
  protectedKeys = ['comment','tags','image','externalId']
  # Handle the important entries: type, id, dateCreated, branch, gui
  if 'type' not in data:
    data['type'] = docType
  if data['type']==['']:
    data['type']=['-']
  if isinstance(data['type'], str):
    data['type'] = data['type'].split('/')
  if 'id' not in data:                                                 # if new (if not update): create new id
    data['id'] = data['type'][0][0]+'-'+uuid.uuid4().hex
  if 'externalId' not in data:
    data['externalId'] = ''
  if 'dateCreated' not in data:
    data['dateCreated']   = datetime.now().isoformat()
  data['dateModified']  = datetime.now().isoformat()
  if 'branch' not in data:
    logging.warning('Empty branch in data')
    data['branch'] = [{'stack':[], 'path':None, 'child':-1, 'show':[]}]
  if 'show' not in data['branch'] and isinstance(data['branch'], dict):
    data['branch']['show'] = [True]*(len(data['branch']['stack'])+1)
  if 'gui' not in data:
    data['gui'] = [True, True]
  # clean comment and tags
  if 'comment' not in data:
    data['comment'] =''
  if 'tags' not in data:
    data['tags'] = []
  data['tags'] = list(set(data['tags']))                                            #ensure only one is inside
  #other cleaning
  if ('links' in data and isinstance(data['links'], list)) and \
     (len(data['links'])==0 or (len(data['links'])==1 and data['links'][0]=='')):
    del data['links']
  #individual verification of documents
  if data['type'][0]=='sample':
    if 'qrCodes' not in data:
      data['qrCodes']=[]
    if isinstance(data['qrCodes'], str):
      data['qrCodes'] = data['qrCodes'].split(' ')
  # cleaning at end of all changes
  initialKeys = list(data.keys())
  for key in initialKeys:
    value = data[key]
    if isinstance(value, str):
      if value=='' and key not in protectedKeys:
        del data[key]
      else:
        data[key] = value.strip()
    if isinstance(value, dict) and key not in ['metaVendor','metaUser','branch']:
      for subKey,subValue in value.items():
        data[f'{key}.{subKey}'] = subValue
      del data[key]
  return data


def dict2ul(aDict:dict[str,Any], fmt:str='html') -> str:
  """
  convert a dictionary into a corresponding <ul>-html list

  Args:
    aDict (dict): dictionary to be translated
    fmt (str): 'html', 'markdown'

  Returns:
    str: string
  """
  text = '<ul>' if fmt=='html' else '\n'
  for key, value in aDict.items():
    if isinstance(value,str) and value.startswith('{') and value.endswith('}'):
      try:
        value = json.loads(value.replace("'",'"'))
      except ValueError:                                                              # not JSON: show as text
        pass
    if isinstance(value, dict):
      valueString = dict2ul(value, fmt)
    elif isinstance(value, tuple) and len(value)==4:                        #tuple of value, unit, label, PURL
      key, valueString = tuple2text(key, value) if fmt == 'html' else tuple2text(key, value, 'markdown')
    elif isinstance(value, (list, tuple)):
      valueString = ',&nbsp;&nbsp;&nbsp;'.join([str(i) for i in value])
    else:
      valueString = str(value)
    text += f'<li>{key}: {valueString}</li>\n' if fmt=='html' else f'- {key}: {valueString}\n'
  return f'{text}</ul>' if fmt=='html' else f'{text}\n'


def doc2markdown(doc:dict[str,Any], ignoreKeys:list[str], dataHierarchyNode:list[dict[str,str]]) -> str:
  """
  Convert document to markdown representation

  Args:
    doc (dict): document to be converted
    ignoreKeys (list): keys to be ignored
    dataHierarchyNode (dict): data hierarchy node
  Returns:
    str: markdown representation
  """
  markdown = ''
  for key in [i for i in SORTED_KEYS if i in doc]+[i for i in doc if i not in SORTED_KEYS]:
    value = doc[key]
    if key == '' and isinstance(value,dict):                                              #handle only key==''
      markdown += doc2markdown(value, ignoreKeys, dataHierarchyNode)
      continue
    if key in ignoreKeys or not value:
      continue
    try:
      if key=='tags':
        pattern = re.compile(r'^_\d$')
        rating = list(filter(pattern.match, value))
        if len(rating)==1:
          ratingStr = '\u2605'*int(rating[0][1])
          markdown += f'Rating: {ratingStr}     '
        tags = set(value).difference(rating)
        markdown += f'Tags: {" ".join(tags)} \n\n'
      elif (isinstance(value,str) and '\n' in value) or key=='comment':      # long values with /n or comments
        markdown += markdownEqualizer(value)+'\n\n'
      else:
        dataHierarchyItems = [dict(i) for i in dataHierarchyNode if i['name']==key]
        if len(dataHierarchyItems)==1 and 'list' in dataHierarchyItems[0] and dataHierarchyItems[0]['list'] and \
            not isinstance(dataHierarchyItems[0]['list'], list):                         #choice among docType
          if not isinstance(value, tuple):
            logging.critical('Value is not a tuple: %s', value)
            continue
          if not isDocID(value[0]):
            value = value[0]
          elif value[2]:
            value = value[2]
          else:
            logging.warning('Value[2] not given for %s', value)
            value = '\u260D link to entry'                                                          #safeguard
          markdown += f'{key.capitalize()}: {value}\n\n'
          continue
        if isinstance(value, list):
          value = ', '.join([str(i) for i in value])
          markdown += f'{key.capitalize()}: {value}\n\n'
          continue
        if isinstance(value, tuple) and len(value)==4:
          if isDocID(value[0]):
            valueString = value[2] or '☍ link to entry'
          else:
            key, valueString = tuple2text(key, value, 'markdown')
          markdown += f'{key.capitalize()}: {valueString}\n\n'
        elif isinstance(value, dict):
          value = dict2ul({k:(v[0]  if isinstance(v, (list,tuple)) else v) for k,v in value.items()}, 'markdown')
          markdown += f'{key.capitalize()}: {value}'
        else:
          markdown += f'{key.capitalize()}: {value}\n\n'
    except Exception:
      doc.pop('image','')
      logging.error('Could not convert to markdown value: %s\n  doc: %s',value, doc, exc_info=True, stack_info=True)
  return markdown


def flatten(data: dict[Any, Any], keepPastaStruct: bool = False) -> dict[object, Any]:
  """Flatten nested dictionaries and lists using dotted keys
    Args:
      data (dict[Any, Any]): data to process
      keepPastaStruct (bool): whether to retain PASTA-ELN structural keys
    Returns:
      dict[object, Any]: Flattened dictionary with dotted keys
  """
  flattenTypes = (Mapping, list)
  flatDict: dict[object, Any] = {}


  def dotReducer(key1: object, key2: object) -> str | object:
    """Combine a parent key and child key into a dotted key
    Args:
      key1 (object): first dictionary key to combine
      key2 (object): second dictionary key to combine
    Returns:
      str | object: Combined key or the retained key object
    """
    return key2 if key1 is None else f'{key1}.{key2}'


  def flattenValue(value: Mapping[Any, Any] | list[Any], parent: object = None) -> bool:
    """Flatten one nested mapping or list into the enclosing result
    Args:
      value (Mapping[Any, Any] | list[Any]): value to process
      parent (object): parent key for the flattened value
    Returns:
      bool: Whether the value was flattened into the result
    """
    items = enumerate(value) if isinstance(value, list) else value.items()
    hasItem = False
    for key, item in items:
      hasItem = True
      flatKey = dotReducer(parent, key)
      if isinstance(item, flattenTypes):
        hasChild = flattenValue(item, flatKey)
        if hasChild or not isinstance(item, ()):
          continue
      if flatKey in flatDict and parent is not None:
        continue
      flatDict[flatKey] = item
    return hasItem

  backup = {key: data.pop(key, None) for key in ('type', 'branch', 'tags', 'gui', 'qrCodes', '_ids')} \
      if keepPastaStruct else {}
  flattenValue(data)
  return flatDict | {key: value for key, value in backup.items() if value is not None}


def hierarchy(data: dict[str, Any]) -> dict[str, Any]:
  """Reverse dotted-key flattening into nested dictionaries and lists
    Args:
      data (dict[str, Any]): data to process
    Returns:
      dict[str, Any]: Nested dictionary reconstructed from dotted keys
  """
  def nestedSetDict(target: dict[str, Any], keys: tuple[str, ...], value: Any) -> None:
    """Store a value at a nested dictionary key path
    Args:
      target (dict[str, Any]): dictionary receiving nested values
      keys (tuple[str, ...]): nested dictionary key path
      value (Any): value to process
    """
    key = keys[0]
    if len(keys) == 1:
      if key in target:
        raise ValueError(f"duplicated key '{key}'")
      target[key] = value
      return
    nestedSetDict(target.setdefault(key, {}), keys[1:], value)


  def dict2list(value: dict[str, Any]) -> list[dict[str, Any]] | dict[str, Any]:
    """Convert dictionaries with numeric keys into lists recursively
    Args:
      value (dict[str, Any]): value to process
    Returns:
      list[dict[str, Any]] | dict[str, Any]: List-converted value or the original dictionary
    """
    for key in value:
      if isinstance(value[key], dict):
        value[key] = dict2list(value[key])
    return list(value.values()) if all(key.isdigit() for key in value) else value

  normalDict: dict[str, Any] = {}
  for flatKey, value in data.items():
    nestedSetDict(normalDict, tuple(flatKey.split('.')), value)
  return dict2list(normalDict)                                                    # type: ignore[return-value]


def expandDocID2tupleInDict(d:dict[str,Any], database:'SqlLiteDB') -> None:
  """ Expand docIDs in docs to be a tuple (value, type, unit, description)
  Args:
    d (dict): doc
    database (sqlite): database for expanding
  """
  pattern = re.compile(r'^[a-z\-]-[a-z0-9]{32}$')
  for k, v in d.items():
    if isinstance(v, dict):
      expandDocID2tupleInDict(v, database)
    elif isinstance(v, tuple) and pattern.match(v[0]) and k not in ('id','oldIdentifier'):
      database.cursor.execute(f'SELECT name FROM main WHERE id=="{v[0]}"')
      names = database.cursor.fetchone()
      if names is None:
        logging.warning('Could not get name for docID %s : %s in %s', k, v[0], d)
        names = ('Could not find name',)
      name = f'\u260D {names[0]}'
      d[k] = (v[0], '', name , '')
  return


def diffDicts(dict1:dict[str,Any], dict2:dict[str,Any], onlyEssentials:bool=True) -> str:
  """ Check if two dictionaries differ. Just compare the lowest level keys/values and output string

  Args:
    dict1 (dict): dictionary 1 - disk
    dict2 (dict): dictionary 2 - database
    onlyEssentials (bool): compare only the essentials -- see below for includeKeys list

  Returns:
    str: output with \\n
  """
  ignoreKeys = ['client', '_rev', 'gui', '_attachments','externalId','dateSync']
  includeKeys= ['id']
  shortVersion = '__version__' in dict1 and dict1['__version__'] == 'short'
  outString = ''
  dict2Copy = dict(dict2)
  for key,value in dict1.items():
    if key in ignoreKeys or (onlyEssentials and key not in includeKeys):
      continue
    if key not in dict2Copy:
      if not shortVersion or key not in ('__version__','content','image','dataHash','extractorHash'):
        outString += f'key not in dictionary 2: {key}' + '\n'
      continue
    if value != dict2Copy[key]:
      if key=='branch':
        if len(value) != len(dict2Copy[key]):
          outString += 'branches have different lengths\n   '+str(value)+'\n   '+str(dict2Copy[key])+'\n'
        else:
          for branch1Raw, branch2Raw in zip(value, dict2Copy[key]):
            branch1 = {k:v for k,v in branch1Raw.items() if k != 'show'}
            branch2 = {k:v for k,v in branch2Raw.items() if k != 'show'}
            if branch1!=branch2:
              outString += 'branches differ\n   '+str(value)+'\n   '+str(dict2Copy[key])+'\n'
      elif isinstance(value, list):
        try:
          if set(value) != set(dict2Copy[key]):
            outString += (f'lists differ for key: {key}\n   {str(value)}\n   {str(dict2Copy[key])}\n')
        except TypeError:
          if json.loads(json.dumps(value, ensure_ascii=False)) != json.loads(json.dumps(dict2Copy[key],
                                                                                        ensure_ascii=False)):
            outString += f'Difference in key: {key}\n{str(value)}\n{str(dict2Copy[key])}\n'
      elif isinstance(value, dict):
        outString += (f'dicts differ for key: {key}\n   {str(value)}\n   {str(dict2Copy[key])}\n')
      elif isinstance(dict2Copy[key], tuple) and len(dict2Copy[key])==4:
        if value != dict2Copy[key][0]:
          outString += (f'property values differ for key: {key}\n   {str(value)}\n   {str(dict2Copy[key])}\n')
      elif isinstance(value,str):
        if value!=dict2Copy[key] and value.translate(SQLiteTranslation)!=dict2Copy[key]:
          diff = difflib.unified_diff(value.splitlines(), dict2Copy[key].splitlines(), fromfile='disk', tofile='database', n=0, lineterm='')
          outString += f'key:{key}\n'+'\n'.join(list(diff))+'\n'
      else:
        outString += (f'values differ for key: {key}\n   {str(value)}\n   {str(dict2Copy[key])}\n')
    del dict2Copy[key]
  extraKeys = set(dict2Copy.keys()).difference(ignoreKeys)
  if shortVersion:
    extraKeys = extraKeys.difference(['tags'])
  if onlyEssentials:
    extraKeys = extraKeys.intersection(includeKeys)
  if extraKeys:
    outString += f'keys not in dictionary 1: {extraKeys}\n'
  return outString


def squashTupleIntoValue(doc:dict[str,Any]) -> None:
  """ Squash tuple/list into value
  - if tuple is length 4, then it is a property tuple: (value, type, unit, description)
  - if tuple is length 1, then it is a value

  Args:
    doc (dict[str,Any]): document
  """
  for key0,value0 in doc.items():
    if isinstance(value0, dict):
      for key1,value1 in doc[key0].items():
        if isinstance(value1, (tuple,list)) and len(value1)==4:
          doc[key0][key1] = value1[0]
  return


def truncateMetadata(metadata:Any, maxChars:int) -> tuple[Any, bool, int, int]:
  """Truncate a JSON value, mark truncated content, and report serialized lengths

  The warning marker is added after truncation and can make the final length exceed
  ``maxChars``

  Args:
    metadata (Any): metadata value to prune
    maxChars (int): maximum serialized JSON length in characters

  Returns:
    tuple: pruned value, truncation flag, original length, and final length
  """
  oldLength = len(json.dumps(metadata, ensure_ascii=False))
  if oldLength <= maxChars:
    return metadata, False, oldLength, oldLength
  truncated, wasTruncated = _truncateJsonValue(metadata, maxChars)
  if wasTruncated:
    if isinstance(truncated, dict):
      truncated['WARNING'] = 'TRUNCATED'
    elif isinstance(truncated, list):
      truncated.append({'WARNING':'TRUNCATED'})
    else:
      truncated = {'WARNING':'TRUNCATED'}
  newLength = len(json.dumps(truncated, ensure_ascii=False))
  return truncated, wasTruncated, oldLength, newLength



def _truncateJsonValue(value:Any, maxChars:int) -> tuple[Any, bool]:
  """Recursive prune JSON values from the end until their serialized size fits

  Args:
    value (Any): JSON value to prune
    maxChars (int): maximum serialized JSON length in characters

  Returns:
    tuple: pruned value and whether content was removed
  """
  if isinstance(value, dict):
    dictResult:dict[Any, Any] = {}
    truncated = False
    for key, child in value.items():
      candidate = dict(dictResult)
      candidate[key] = child
      if len(json.dumps(candidate, ensure_ascii=False)) <= maxChars:
        dictResult[key] = child
        continue
      if isinstance(child, (dict, list)):
        remaining = max(0, maxChars - len(json.dumps({**dictResult, key: {} if isinstance(child, dict) else []},
                                                     ensure_ascii=False)))
        child, childTruncated = _truncateJsonValue(child, remaining)
        candidate = dict(dictResult)
        candidate[key] = child
        if len(json.dumps(candidate, ensure_ascii=False)) <= maxChars:
          dictResult[key] = child
        else:
          truncated = True
        truncated |= childTruncated
      else:
        truncated = True
      if len(json.dumps(dictResult, ensure_ascii=False)) >= maxChars:
        truncated |= len(value) > len(dictResult)
        break
    truncated |= len(dictResult) != len(value)
    return dictResult, truncated
  if isinstance(value, list):
    listResult:list[Any] = []
    truncated = False
    for child in value:
      listCandidate = listResult + [child]
      if len(json.dumps(listCandidate, ensure_ascii=False)) <= maxChars:
        listResult.append(child)
        continue
      if isinstance(child, (dict, list)):
        remaining = max(0, maxChars - len(json.dumps(listResult + [{} if isinstance(child, dict) else []],
                                                     ensure_ascii=False)))
        child, childTruncated = _truncateJsonValue(child, remaining)
        if len(json.dumps(listResult + [child], ensure_ascii=False)) <= maxChars:
          listResult.append(child)
        else:
          truncated = True
        truncated |= childTruncated
      else:
        truncated = True
      break
    truncated |= len(listResult) != len(value)
    return listResult, truncated
  return value, len(json.dumps(value, ensure_ascii=False)) > maxChars
