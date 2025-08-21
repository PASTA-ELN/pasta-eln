"""Change the format of dictionaries"""
import difflib
import json
import logging
import re
import uuid
from datetime import datetime
from typing import Any
from ..fixedStringsJson import SORTED_KEYS, SQLiteTranslation
from .stringChanges import markdownEqualizer


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
    str: document
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
    print('Empty branch in data')
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
      except Exception:
        pass
    if isinstance(value, dict):
      valueString = dict2ul(value)
    elif isinstance(value, tuple) and len(value)==4:                        #tuple of value, unit, label, PURL
      key = key if value[2] is None or value[2]=='' else value[2]
      valueString = f'{value[0]} {value[1]}'
      valueString = valueString if value[3] is None or value[3]=='' else f'{valueString}&nbsp;<b><a href="{value[3]}">&uArr;</a></b>'
    elif isinstance(value, (list, tuple)):
      valueString = ',&nbsp;&nbsp;&nbsp;'.join([str(i) for i in value])
    else:
      valueString = str(value)
    text += f'<li>{key}: {valueString}</li>\n' if fmt=='html' else f'- {key}: {valueString}\n'
  return f'{text}</ul>' if fmt=='html' else f'{text}\n'


def doc2markdown(doc:dict[str,Any], ignoreKeys:list[str], dataHierarchyNode:list[dict[str,str]], widget:Any) -> str:
  """
  Convert document to markdown representation

  Args:
    doc (dict): document to be converted
    ignoreKeys (list): keys to be ignored
    dataHierarchyNode (dict): data hierarchy node
    widget (Any): widget to get comm and backend from

  Returns:
    str: markdown representation
  """
  markdown = ''
  for key in [i for i in SORTED_KEYS if i in doc]+[i for i in doc if i not in SORTED_KEYS]:
    value = doc[key]
    if key == '' and isinstance(value,dict):                                              #handle only key==''
      markdown += doc2markdown(value, ignoreKeys, dataHierarchyNode, widget)
      continue
    if key in ignoreKeys or not value:
      continue
    try:
      if key=='tags':
        tags = [f'#{i}' for i in value]
        tags = ['\u2605'*int(i[2]) if i[:2]=='#_' else i for i in tags]
        markdown += f'Tags: {" ".join(tags)} \n\n'
      elif (isinstance(value,str) and '\n' in value) or key=='comment':      # long values with /n or comments
        markdown += markdownEqualizer(value)+'\n\n'
      else:
        dataHierarchyItems = [dict(i) for i in dataHierarchyNode if i['name']==key]
        if len(dataHierarchyItems)==1 and 'list' in dataHierarchyItems[0] and dataHierarchyItems[0]['list'] and \
            not isinstance(dataHierarchyItems[0]['list'], list):                         #choice among docType
          #TODO: for now just specify that there is a link to an item
          #  better solution: already replace the value with the name of the item before calling this
          #table  = widget.comm.backend.db.getView('viewDocType/'+dataHierarchyItems[0]['list'])
          # names= list(table[table.id==value[0]]['name'])
          # if len(names)==1:                                            # default find one item that we link to
          #   value = '\u260D '+names[0]
          # elif not names:        # likely empty link because the value was not yet defined: just print to show
          #   value = value[0] if isinstance(value,tuple) else value
          # else:
          #   raise ValueError(f'list target exists multiple times. Key: {key}')
          if re.search(r'^[a-z\-]-[a-z0-9]{32}$',value[0]) is None:
            value = value[0] if isinstance(value,tuple) else value
          else:
            value = '\u260D link to entry'
        elif isinstance(value, list):
          value = ', '.join([str(i) for i in value])
          markdown += f'{key.capitalize()}: {value}\n\n'
        if isinstance(value, tuple) and len(value)==4:
          key = key if value[2] is None or value[2]=='' else value[2]
          valueString = f'{value[0]} {value[1]}'
          valueString = valueString if value[3] is None or value[3]=='' else f'{valueString}&nbsp;**[&uArr;]({value[3]})**'
          markdown += f'{key.capitalize()}: {valueString}\n\n'
        if isinstance(value, dict):
          value = dict2ul({k:(v[0]  if isinstance(v, (list,tuple)) else v) for k,v in value.items()}, 'markdown')
          markdown += f'{key.capitalize()}: {value}'
    except Exception:
      doc.pop('image','')
      logging.error('Could not convert to markdown value: %s\n  doc: %s',value, doc, exc_info=True, stack_info=True)
  return markdown


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
      if not shortVersion or key not in ('__version__','content','image','shasum'):
        print(shortVersion, key)
        outString += f'key not in dictionary 2: {key}' + '\n'
      continue
    if value != dict2Copy[key]:
      if key=='branch':
        if len(value) != len(dict2Copy[key]):
          outString += 'branches have different lengths\n   '+str(value)+'\n   '+str(dict2Copy[key])+'\n'
        else:
          for idx,_ in enumerate(value):
            branch1 = value[idx]
            branch2 = dict2Copy['branch'][idx]
            if 'show' in branch1:
              del branch1['show']
            if 'show' in branch2:
              del branch2['show']
            if branch1!=branch2:
              outString += 'branches differ\n   '+str(value)+'\n   '+str(dict2Copy[key])+'\n'
      elif isinstance(value, list):
        try:
          if set(value).difference(set(dict2Copy[key])):
            outString += (f'lists differ for key: {key}\n   {str(value)}\n   {str(dict2Copy[key])}\n')
        except Exception:
          if str(value)!= str(dict2Copy[key]).replace('(' ,'[').replace(')' ,']'):
            outString += f'Difference in key: {key}\n{str(value)}\n{str(dict2Copy[key])}\n'
      elif isinstance(value, dict):
        if json.dumps(value) != json.dumps(dict2Copy[key]):
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
