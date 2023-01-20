"""extract data from .csv file
"""
import re
from io import StringIO
import numpy as np
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
  with open(filePath, encoding='utf-8') as fIn:
    startRow = 0
    while True:
      if len(re.findall('[a-zA-Z]', fIn.readline()))==0:
        break
      startRow+=1
  data = np.loadtxt(filePath, delimiter=',', skiprows=startRow)

  if recipe.endswith('red'):              #: Draw with red curve
    plt.plot(data[:,0], data[:,1],'r')
  else:                                   #: Default | blueish curve
    plt.plot(data[:,0], data[:,1])
  metaUser = {'max':data[:,1].max(), 'min':data[:,1].min()}
  recipe = 'csv'

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
