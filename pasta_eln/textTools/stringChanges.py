""" Functions that modify strings into the appropriate format """
import logging
from pathlib import Path
import re
import traceback
from typing import Any
from ..miscTools import Bcolors


def outputString(fmt:str='print', level:str='info', message:str='') -> str:
  """ Output a message into different formats:
    - print: print to stdout
    - logging; log to file
    - text: return text string (supersedes html)
    - html: return html string https://doc.qt.io/qtforpython/overviews/richtext-html-subset.html#supported-html-subset
    - else: no output
    - formats can be union ('print,text')
  """
  prefixes = {'h2':f'{Bcolors.UNDERLINE}\n*** ','bold':f'{Bcolors.BOLD}\n*** ', \
              'perfect':f'{Bcolors.OKGREEN}', 'ok':f'{Bcolors.OKBLUE}', 'unsure':f'{Bcolors.HEADER}',\
              'warning':f'{Bcolors.WARNING}**Warning','error':f'{Bcolors.FAIL}**ERROR '}
  if level=='info':
    txtOutput = message.strip()+'\n'
  elif level in prefixes:
    txtOutput = prefixes[level]+message
    txtOutput+= ' ***' if '***' in prefixes[level] else ''
    txtOutput+= f'{Bcolors.ENDC}\n'
  else:
    logging.error('Level not in prefixes %s',level)
  # depend on format
  if 'print' in fmt:
    print(txtOutput)
  if 'logging' in fmt and level in {'info', 'warning', 'error'}:
    getattr(logging,level)(message)
  if 'text' in fmt:
    return txtOutput
  if fmt=='html':
    colors = {'info':'black','error':'red','warning':'orangered','perfect':'green','ok':'blue','unsure':'magenta'}
    if level[0]=='h':
      return f'<{level}>{message}</{level}>'
    if level not in colors:
      logging.error('Wrong level %s', level)
      return ''
    return f'<font color="{colors[level]}">' + message.replace('\n', '<br>') + '</font><br>'
  return ''


def tracebackString(log:bool=False, docID:str='') -> str:
  """ Create a formatted string of traceback

  Args:
    log (bool): write to logging
    docID (str): docID used in comment

  Returns:
    str: | separated string of call functions
  """
  tracebackList = [i.split('\n')[0] for i in traceback.format_stack()[2:-2] if 'pasta_eln' in i]#skip first and last and then filter only things with pasta_eln
  reply = '|'.join([item.split('/')[-1].strip() for item in tracebackList])#| separated list of stack excluding last
  reply = reply.replace('",','')
  if log:
    logging.info(' traceback %s %s', docID, reply)
  return reply


def markdownEqualizer(text:str) -> str:
  """
  Create a markdown that well balanced with regard to font size, etc

  Args:
    text (str): input string

  Returns:
    str: output str
  """
  if isinstance(text, tuple):
    text=text[0]
  return re.sub(r'(^|\n)(#+)', r'\1##\2', text.strip())


def camelCase(text:str) -> str:
  """
  Produce camelCase from normal string
  - file names abcdefg.hij are only replaced spaces

  Args:
     text (str): string

  Returns:
    str: camel case of that string: CamelCaseString
  """
  if re.match(r'^[\w-]+\.[\w]+$', text):
    return text.replace(' ','_')
  return re.sub(r'(_|-)+', ' ', text).title().replace(' ','').replace('*','')


def createDirName(doc:dict[str,Any], thisChildNumber:int, parentDir:Path) -> str:
  """ create directory-name by using camelCase and a prefix

  Args:
      doc (dict): document with all information
      thisChildNumber (int): number of myself
      parentDir (Path): parent directory where the new directory should be created

  Returns:
    string: directory name with leading number
  """
  name = camelCase(doc['name']) if doc['type'][0] == 'x0' else \
         f'{thisChildNumber:03d}_{camelCase(doc['name'])}'
  if 'branch' in doc and name in [i['path'].split('/')[-1] for i in doc['branch']]:    #only change if not the same name as before
    logging.debug('createDirName: %s used', name)
    return name
  idx = 0
  nameTest = name
  while (parentDir/name).exists():
    idx += 1
    nameTest = f'{name}_{idx:02d}'
  logging.debug('createDirName: %s created', nameTest)
  return nameTest
