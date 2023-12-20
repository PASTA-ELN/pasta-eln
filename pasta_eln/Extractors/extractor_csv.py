"""extract data from vendor
- comma and semicolor separated table
"""
from io import StringIO
import pandas as pd
import matplotlib.pyplot as plt

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
  producer = ''
  lines = []
  with open(filePath, encoding='unicode_escape') as fIn:
    for  j in range(10):
      lines.append(fIn.readline()[:-1])
    print('\n'.join(lines)) #temporary
    # files with some form of header: try 3 criteria
    if lines[0].count(';')>lines[0].count(' ') and lines[0].count(';')==lines[1].count(';') and \
                                                   lines[0].count(';')==lines[2].count(';'): #Separate by ; not ' '
      producer = 'semicolon separated'
      delimiter = ';'
    if lines[0].count(',')>lines[0].count(' ') and lines[0].count(',')==lines[1].count(',') and \
                                                   lines[0].count(',')==lines[2].count(','): #Separate by , not ' '
      producer = 'comma separated'
      delimiter = ','
  print('Producer ', producer)

  data = pd.read_csv(filePath, delimiter=delimiter)
  plt.plot(data.iloc[:,1])
  metaUser = {}
  metaVendor = {}
  links = []

  #save to file
  if saveFileName is not None:
    plt.savefig(saveFileName, dpi=150, bbox_inches='tight')

  #convert axes to svg image
  figfile = StringIO()
  plt.savefig(figfile, format='svg')
  image = figfile.getvalue()

  # return everything
  return {'image':image, 'recipe':recipe, 'metaVendor':metaVendor, 'metaUser':metaUser, 'links':links}

  #other datatypes follow here
  #...

  #final return if nothing successful
  # return {}

