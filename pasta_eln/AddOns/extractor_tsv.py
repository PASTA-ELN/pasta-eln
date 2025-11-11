"""extract data from vendor
- tabular separated table that is used in the tensile example

THIS IS THE BASIC EXTRACTOR TUTORIAL, WHICH TEACHES
- how to create metadata conveniently using "Long name [Unit]" nomenclature
- how to create images
- code is recreated in this example, which is not ideal. But this is a tutorial and ok
"""
from io import StringIO
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def use(filePath, style={'main':''}, saveFileName=None):
  """
  Args:
    filePath (Path): full path file name
    style    (dict): supplied to guide the display / extraction style = recipe
                     main is / separated hierarchical elements parent->child
                     can contain more elements
    saveFileName (string): if given, save the image to this file-name
  Returns:
    dict: containing image, metaVendor, metaUser, style
  """
  # general information
  with open(filePath, encoding='utf-8') as fIn:
    firstLine = fIn.readline()
  data = np.loadtxt(filePath, delimiter='\t')     # use numpy to get data
  style['main'] = 'measurement/tsv/lines'

  # metadata
  if firstLine.strip() == '# strain [%], stress [MPa]':  #easy way to include extractors for multiple files into one
    maxStrain = data[:,0].max()
    strength  = data[:,1].max()
    fit = np.polyfit(data[:6,0], data[:6,1], 1)
    youngsModulus = fit[0]
    yieldIdx = np.where( np.polyval([youngsModulus, -0.2*youngsModulus], data[:,0]) >
                         data[:,1])[0][0]
    yieldStress = data[yieldIdx,1]
    direction   = filePath.stem.split('_')[1]
    # print for visual inspection
    plt.axhline(strength, color='k', linestyle=':')
    plt.axvline(maxStrain, color='k', linestyle=':')
    plt.plot(data[:8,0], np.polyval(fit, data[:8,0]), 'k-', linewidth=2)  #original fit
    plt.plot(data[:8,0], np.polyval([youngsModulus, -0.2*youngsModulus], data[:8,0]), 'r-')  #0.2% offset
    plt.plot(data[yieldIdx,0], yieldStress, 'ro')
    # save metadata
    metaUser = {'maxStrain [%]':maxStrain, 'strength [MPa]':strength, 'youngsModulus [MPa]':round(youngsModulus,4),
                'yieldStress [MPa]':yieldStress, 'direction':direction}  #DO NOT USE SPACES OR .; do use camel-case
    metaVendor = {}

  #plot
  plt.plot(data[:,0], data[:,1],'-')     # plot data using matplotlib: check the differences in plotting
  plt.xlabel(firstLine[1:].split(',')[0])
  plt.ylabel(firstLine[1:].split(',')[1])
  if firstLine.strip() == '# strain [%], stress [MPa]':
    plt.xlim(left=0)
    plt.ylim(bottom=0)
  ## plt.show()  #for fast testing

  #Save to file: each extractor should have this as it allows the user to create a high quality image
  if saveFileName is not None:
    plt.savefig(saveFileName, dpi=150, bbox_inches='tight')

  #convert image to svg image: 2d graphs are good examples of svg files
  figfile = StringIO()
  plt.savefig(figfile, format='svg')
  image = figfile.getvalue()

  # return everything
  return {'image':image, 'style':style, 'metaVendor':metaVendor, 'metaUser':metaUser}


def data(filePath, style):
  """
  Args:
    filePath (Path): full path file name
    style    (dict): supplied to guide the display / extraction style

  Returns:
    df: pandas dataframe or any other data structure
  """
  with open(filePath, encoding='utf-8') as fIn:
    firstLine = fIn.readline()
  data = np.loadtxt(filePath, delimiter='\t')     # use numpy to get data
  return pd.DataFrame(data, columns=firstLine[1:].split(','))
