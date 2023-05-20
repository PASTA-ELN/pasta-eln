"""extract data from .csv file
"""
import re
from io import StringIO
import numpy as np
import pandas as pd
from pandas.errors import EmptyDataError
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
  # Extractor for fancy instrument
  delimiter = ','
  with open(filePath, encoding='utf-8') as fIn:
    content = fIn.read()
    countComma = content.count(',')
    countPoint = content.count('.')
    countTab   = content.count('\t')
    countSemicolon = content.count(';')
    countLines = content.count('\n')
    print('Counts of , . \\t ; \\n in csv file: ',countComma, countPoint, countTab, countSemicolon, countLines)
    if countSemicolon>=countLines:
      delimiter = ';'
  with open(filePath, encoding='utf-8') as fIn:
    startRow = 0
    while True:
      if len(re.findall('[a-zA-Z]', fIn.readline()))==0:
        break
      startRow+=1
  try:
    data = pd.read_csv(filePath, delimiter=delimiter, skiprows=startRow)
  except EmptyDataError:  #if no data left, import everything
    data = pd.read_csv(filePath, delimiter=delimiter)
  data = np.array(data)

  if recipe == 'measurement/table/red':           #: Draw with red curve
    plt.plot(data[:,0], data[:,1],'r')
  elif True or recipe == 'measurement/table/blue': #: Default | blueish curve
    plt.plot(data[:,0], data[:,1])
    recipe = 'measurement/table/blue'
  metaUser = {'max':data[:,1].max(), 'min':data[:,1].min()}

  #save to file
  if saveFileName is not None:
    plt.savefig(saveFileName, dpi=150, bbox_inches='tight')

  #convert axes to svg image
  figfile = StringIO()
  plt.savefig(figfile, format='svg')
  image = figfile.getvalue()

  # return everything
  return {'image':image, 'recipe':recipe, 'metaVendor':{}, 'metaUser':metaUser}

  #other datatypes follow here
  #...
  #final return if nothing successful
  #return {}
