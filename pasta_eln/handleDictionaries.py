"""Change the format of dictionaries"""
import re, uuid, json
from typing import Any
from datetime import datetime

def dataHierarchy2Labels(dataHierarchy:dict[str,Any], tableFormat:dict[str,Any]) -> dict[str,Any]:
  """
  Extract labels and create lists of docType,docLabel pair
  - docLabel is the plural human-readable form of the docType
  - docType is the single-case noun

  Not sure if separation into datalabels and hierarchy labels is still needed. Join

  Args:
     dataHierarchy (dict): data hierarchy
     tableFormat (dict): tableFormat branch

  Returns:
     dict: dictionary
  """
  dataDict = {}
  hierarchyDict = {}
  for key in dataHierarchy:
    if key in ['id', '_rev']:
      continue
    label = None
    if key in tableFormat and '-label-' in tableFormat[key]:  #use label from tableFormat
      label = tableFormat[key]['-label-']
    elif key[0]=='x':                                         #use default structural elements
      label = ['Projects','Tasks','Subtasks','Subsubtasks'][int(key[1])]
    else:                                                     #default system  sample->Samples
      label = key[0].upper()+key[1:]+'s'
    if key[0]=='x':
      hierarchyDict[key] = label
    else:
      dataDict[key] = label
  dataDict |= hierarchyDict
  return dataDict


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
  if 'id' not in data:  # if new (if not update): create new id
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
  # separate comment into tags and fields
  # these tags are lost: '#d': too short; '#3tag': starts with number
  if 'comment' not in data:
    data['comment'] =''
  if 'tags' not in data:
    data['tags'] = []
  #always do regex expressions twice: if #lala at beginning or in middle of comment
  curated = re.findall(r'(?:^|\s)#_curated(?:\s|$)', data['comment']) # #_curated
  rating  = re.findall(r'(?:^|\s)#_\d(?:\s|$)',      data['comment']) # #_number
  if rating is None:
    rating=[]
  if len(rating)>1:  #prevent multiple new ratings
    rating=rating[:1]
  if len(rating)==1: #remove ratings that exist already
    data['tags'] = [i for i in data['tags'] if not re.compile(r'^_\d$').match(i)]
  otherTags = re.findall(r'(?:^|\s)#[a-zA-Z]\w+(?=\s|$)', data['comment'])
  if otherTags is None:
    otherTags=[]
  data['tags'] = rating + data['tags'] + otherTags + curated
  data['comment'] = re.sub(r'(?:^|\s)#\w+(?=\s|$)', '', data['comment']).strip()
  fields = re.findall(r':[\S]+:[\S]+:', data['comment'])
  if fields is not None:
    for item in fields:
      aList = item.split(':')
      if aList[1] in data: #do not add if item already exists
        continue
      data[aList[1]] = aList[2]
  data['comment'] = re.sub(r':[\S]+:[\S]+:','',data['comment'])  #remove :field:data: information
  if isinstance(data['tags'], str):
    data['tags'] = data['tags'].split(' ')
  data['tags'] = [i.strip()[1:] if i.strip()[0]=='#' else i.strip() for i in data['tags']]
  data['tags'] = list(set(data['tags']))  #ensure only one is inside
  #other cleaning
  if ('links' in data and isinstance(data['links'], list)) and \
     (len(data['links'])==0 or (len(data['links'])==1 and data['links'][0]=='')):
    del data['links']
  #individual verification of documents
  if data['type'][0]=='sample':
    if 'qrCode' not in data:
      data['qrCode']=[]
    if isinstance(data['qrCode'], str):
      data['qrCode'] = data['qrCode'].split(' ')
  if data['type'][0] == 'measurement':
    if 'image' not in data:
      data['image'] = ''
    if 'shasum' not in data:
      data['shasum']=''
  # cleaning at end of all changes
  toDelete = []
  for key in data:
    if isinstance(data[key], str):
      if data[key]=='' and key not in protectedKeys:
        toDelete.append(key)
      else:
        data[key] = data[key].strip()
  for key in toDelete:
    del data[key]
  return data


def dict2ul(aDict:dict[str,Any]) -> str:
  """
  convert a dictionary into a corresponding <ul>-html list

  Args:
    aDict (dict): dictionary to be translated
  """
  text = '<ul>'
  for key, value in aDict.items():
    if isinstance(value,str) and value.startswith('{') and value.endswith('}'):
      try:
        value = json.loads(value.replace("'",'"'))
      except Exception:
        pass
    if isinstance(value, dict):
      valueString = dict2ul(value)
    elif isinstance(value, tuple) and len(value)==4:  #tuple of value, unit, label, IRI
      key = key if value[2] is None or value[2]=='' else value[2]
      valueString = f'{value[0]} {value[1]}'
      valueString = valueString if value[3] is None or value[3]=='' else f'{valueString}&nbsp;<b><a href="{value[3]}">&uArr;</a></b>'
    elif isinstance(value, (list, tuple)):
      valueString = ',&nbsp;&nbsp;&nbsp;'.join([str(i) for i in value])
    else:
      valueString = str(value)
    text += f'<li>{key}: {valueString}</li>\n'
  return f'{text}</ul>'


def diffDicts(dict1:dict[str,Any], dict2:dict[str,Any]) -> str:
  """ Check if two dictionaries differ. Just compare the lowest level keys/values and output string

  Args:
    dict1 (dict): dictionary 1
    dict2 (dict): dictionary 2

  Returns:
    str: output with \\n
  """
  ignoreKeys = ['client', '_rev', 'gui', '_attachments']
  outString = ''
  dict2Copy = dict(dict2)
  for key,value in dict1.items():
    if key in ignoreKeys:
      continue
    if key not in dict2Copy:
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
        if set(value).difference(set(dict2Copy[key])):
          outString += (f'lists differ for key: {key}\n   {str(value)}\n   {str(dict2Copy[key])}\n')
      elif isinstance(dict2Copy[key], tuple) and len(dict2Copy[key])==4:
        if value != dict2Copy[key][0]:
          outString += (f'property values differ for key: {key}\n   {str(value)}\n   {str(dict2Copy[key])}\n')
      else:
        outString += (f'values differ for key: {key}\n   {str(value)}\n   {str(dict2Copy[key])}\n')
    del dict2Copy[key]
  for key in dict2Copy:
    if key in ignoreKeys:
      continue
    outString += f'key not in dictionary 1: {key}\n'
  return outString
