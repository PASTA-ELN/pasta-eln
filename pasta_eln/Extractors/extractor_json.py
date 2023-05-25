"""extract data from vendor
- javascript object notion
"""
import json

def use(filePath, recipe='', saveFileName=None):
  """
  Args:
    filePath (string): full path file name
    recipe (string): supplied to guide recipes
                     recipe is / separated hierarchical elements parent->child
    saveFileName (string): if given, save the image to this file-name

  Returns:
    dict: containing image, metaVendor, metaUser, recipe
  """
  # Extractor for fancy instrument
  metaVendor = ''
  with open(filePath,'r', encoding='utf-8') as jsonFile:
    jsonContent = jsonFile.read()
    metaVendor = json.loads(jsonContent)
    if not isinstance(metaVendor, dict):
      metaVendor= {'content': json.loads(jsonContent)}
  image = ''
  recipe = '-'

  # return everything
  return {'image':image, 'recipe':recipe, 'metaVendor':metaVendor, 'metaUser':{}}

  #other datatypes follow here
  #...
  #final return if nothing successful
  #return {}
