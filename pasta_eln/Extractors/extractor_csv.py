"""extract data from vendor
- comma and semicolon separated table
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
  producer = 'comma separated'
  delimiter = ','
  lines = []
  skipRows = 0
  with open(filePath, encoding='unicode_escape') as fIn:
    for  _ in range(10):
      line = fIn.readline()[:-1]
      if line.startswith('#'):
        skipRows+=1
        continue
      lines.append(line)
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

  data = pd.read_csv(filePath, delimiter=delimiter, skiprows=skipRows-1)
  plt.plot(data.iloc[:,0], data.iloc[:,1],'o-')
  metaUser = {}
  metaVendor = {}
  links = []
  recipe = 'measurement/csv'

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
