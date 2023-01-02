"""extract data from .csv file
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
    metaVendor = json.load(jsonFile)
  recipe = 'json'
  image = ''

  # return everything
  return {'image':image, 'recipe':recipe, 'metaVendor':metaVendor, 'metaUser':{}}

  #other datatypes follow here
  #...
  #final return if nothing successful
  #return {}
