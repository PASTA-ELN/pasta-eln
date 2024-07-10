"""extract data from vendor
- javascript object notion
For tutorials, see extractor_csv.py and extractor_png.py
"""
import json
import os

def use(filePath, style={'main':''}, saveFileName=None):
  """
  Args:
    filePath (Path): full path file name
    style    (dict): supplied to guide the display / extraction style = recipe
                     main is / separated hierarchical elements parent->child
                     can contain more elements
    saveFileName (string): if given, save the image to this file-name

  Returns:
    dict: containing image, metaVendor, metaUser, recipe
  """
  # Extractor for fancy instrument
  content = ''
  fileSize = os.stat(filePath).st_size / (1024*1024)  #in MB
  if fileSize<0.3:
    with open(filePath,'r', encoding='utf-8') as jsonFile:
      jsonContent = jsonFile.read()
      content = json.loads(jsonContent)
      if not isinstance(content, dict):
        content= {'content': json.loads(jsonContent)}
  else:
    content= 'Too large json file'
  style['main'] = 'procedure/json'
  content= f'```json\n{json.dumps(content, indent=2)}\n```'

  # return everything
  return {'content':content, 'style':style, 'metaVendor':{}, 'metaUser':{}}
