"""extract data from .csv file
"""
import re
from io import StringIO
import numpy as np
from scipy import stats
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
  startRow = -1
  dataType = ''
  with open(filePath, encoding='utf-8') as fIn:
    line = fIn.readline()
    if 'image,imprint size(micrometer)' in line:
      startRow = 0
      dataType = 'DFKI'
    elif 'Ananlysis with contact area from tip area function;' in line:
      startRow = 1
      dataType = 'FZJ'
    elif ',Al (at. %),Fe (at. %),Si (at. %),E (GPa)' in line:
      startRow = 0
      dataType = 'pyIron'
    else:
      fIn.seek(0)
      startRow = 0
      while True:
        if len(re.findall('[a-zA-Z]', fIn.readline()))==0:
          break
        startRow+=1
  print('delimiter',delimiter, 'startRow',startRow)
  try:
    data = pd.read_csv(filePath, delimiter=delimiter, skiprows=startRow)
  except EmptyDataError:  #if no data left, import everything
    data = pd.read_csv(filePath, delimiter=delimiter)
  # temporary fix for data from DFKI
  if dataType=='DFKI':
    imprintSize = list(data['imprint size(micrometer)'])
    imprintSize = [i.split(',')[0].replace('[','').replace(']','') for i in imprintSize]
    imprintSize = [float(i) for i in imprintSize]
    data['imprintSize'] = imprintSize
    force = list(data['image'])
    force = [int(i.split('mN')[0][3:]) for i in force]
    data['force'] = force
    data = data.drop(['image','imprint size(micrometer)'],axis=1)
    data = np.array(data)
    plt.plot(data[:,0], data[:,1],'o')
    plt.xlabel('force [mN]')
    plt.ylabel(r'area [$\mu m^2$]')
    metaUser = {'num files':data.shape[0]}
    if recipe == 'measurement/dkfi/fit':            #: With fitting line
      fit = np.polyfit(data[:,0], data[:,1], 1)
      x_ = np.array([0,np.max(data[:,0])])
      plt.plot(x_, np.polyval(fit, x_))
      metaUser['fitFunction'] = str(fit[0])+'x+'+str(fit[1])
      slope, intercept, r_value, p_value, std_err = stats.linregress(data[:,0], data[:,1])
      metaUser.update({'slope':slope, 'intercept':intercept, 'r_value':r_value, 'p_value':p_value, 'std_err':std_err})
    elif True or recipe == 'measurement/dkfi':      #: Default | raw data
      recipe = 'measurement/dkfi'
  elif dataType=='FZJ':
    data = pd.read_csv(filePath, delimiter=delimiter, skiprows=startRow, decimal=',')
    plt.plot(np.array(data['pMax_mN']), np.array(data['E_GPa'])  ,'o',label='Oliver-Pharr')
    plt.plot(np.array(data['pMax_mN']), np.array(data['E_GPa.1']),'o',label='Image analysis')
    plt.legend()
    plt.xlabel('force [$mN$]')
    plt.ylabel("Young's modulus [$GPa$]")
    recipe = 'measurement/fzj'
    metaUser = {'num files':data.shape[0]}
  elif dataType=='pyIron':
    ax = plt.figure().add_subplot(projection='3d')
    ax.plot(np.array(data['Fe (at. %)']),    np.array(data['Si (at. %)']), 'ok', zs=110, zdir='z')
    ax.scatter(np.array(data['Fe (at. %)']), np.array(data['Si (at. %)']), np.array(data['E (GPa)']), c='b')
    ax.set_xlabel('Fe (at. %)')
    ax.set_ylabel('Si (at. %)')
    ax.set_zlabel('E [GPa]')
    metaUser = {'num files':data.shape[0], 'max Fe':data['Fe (at. %)'].max(), 'max Si':data['Si (at. %)'].max()}
    recipe = 'measurement/pyIron'
  else:
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
