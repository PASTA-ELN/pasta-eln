"""Change the format of dictionaries"""
import re, uuid
from datetime import datetime

def ontology2Labels(ontology, tableFormat):
  """
  Extract labels and create lists of docType,docLabel pair
  - docLabel is the plural human-readable form of the docType
  - docType is the single-case noun

  Args:
     ontology (dict): ontology
     tableFormat (dict): tableFormat branch from .pastaELN.json

  Returns:
     dictionary: dataDict, hierarchyDict
  """
  dataDict = {}
  hierarchyDict = {}
  for key in ontology.keys():
    if key in ['_id', '_rev']:
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
  return {'dataDict':dataDict, 'hierarchyDict':hierarchyDict}


def fillDocBeforeCreate(data, docType):
  """ Fill the data before submission to database with common data
  - type, project, childs
  - separate comment into tags, fields
  - create id if needed
  
  used in backend.py and Store.js

  Args:
    data (dict): document to save
    docType (str): type of document, e.g. project

  Returns:
    str: document
  """
  protectedKeys = ['comment','tags','image']
  # Handle the important entries: -type, _id, -date, -branch
  if '-type' not in data:
    data['-type'] = [docType]
  if isinstance(data['-type'], str):
    data['-type'] = data['-type'].split('/')
  if '_id' not in data:  # if new (if not update): create new id
    prefix = 'x' if docType[0]=='x' else docType[0][0]
    data['_id'] = prefix+'-'+uuid.uuid4().hex
  data['-date']   = datetime.now().isoformat()
  if '-branch' not in data:
    data['-branch'] = [{'stack':[], 'path':null}]
  # separate comment into tags and fields
  # these tags are lost: '#d': too short; '#3tag': starts with number
  if 'comment' not in data:
    data['comment'] =''
  if 'tags' not in data:
    data['tags'] = []
  rating = re.findall(r'(^|\s)#\d\s', data['comment'])  # one number following up on #
  if rating is None:
    rating=[]
  otherTags = re.findall(r'(^|\s)#{1}[a-zA-Z][\w]', data['comment']) #TODO just as one above
  if otherTags is None:
    otherTags=[]
  data['tags'] = data['tags'] + otherTags
  data['comment'] = data['comment'].replace(r'(^|\s)#{1}[\w]',' ')
  fields = re.findall(r':[\S]+:[\S]+:', data['comment'])
  if fields is not None:
    for item in fields:
      aList = item.split(':')
      if aList[1] in data: #do not add if item already exists
        continue
      data[aList[1]] = aList[2]
  # clean the comments
  data['comment'] = data['comment'].replace(r':[\S]+:[\S]+:','')  #remove :field:data: information
  ## Remove - until it becomes important again - some prefix space cleaning
  # text = data['comment'].split('\n');
  # data['comment'] = '';
  # for line in text:
  #   initSpaces = line.search(/\S|$/)
  #   for (var prefixJ = '';prefixJ.length<Math.round(initSpaces/2)*2; prefixJ+=' ');//str.repeat(int) does not work for some reason
  #   data['comment'] += prefixJ+line.trim()+'\n';  //do not replace spaces inside the line
  # }
  # data['comment'] = data['comment'].substring(0, data['comment'].length-1);
  if isinstance(data['tags'], str):
    data['tags'] = data['tags'].split(' ')
  data['tags']= [i.strip() for i in data['tags']]
  #individual verification of documents
  if data['-type'][0]=='sample':
    if 'qrCode' not in data:
      data['qrCode']=[]
    if isinstance(data['qrCode'], str):
      data['qrCode'] = data['qrCode'].split(' ')
  if data['-type'][0] == 'measurement':
    if 'image' not in data:
      data['image'] = ''
    if 'shasum' not in data:
      data['shasum']=''
  # cleaning at end of all changes
  for key in data:
    if isinstance(data[key], str):
      if data[key]=='' and key not in protectedKeys:
        del data[key]
      else:
        data[key] = data[key].strip()
  return data
