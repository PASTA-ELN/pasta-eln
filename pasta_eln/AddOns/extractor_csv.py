"""extract data from vendor
- comma and semicolon separated table

THIS IS THE BASIC EXTRACTOR TUTORIAL, WHICH TEACHES
- how to use style recipes:
  - in the code these are lines which have an if-statement and this is followed by a comment "#:" which is then used for the human readable part
  - the default case is with "elif True and" which is a little strange but follows above rule of if-statement and ....
  - please use this way of writing code and the extractors should work
- how to create metadata conveniently using "Long name [Unit]" nomenclature
- how to create images
"""
from io import StringIO
import pandas as pd
import matplotlib.pyplot as plt

def use(filePath, style={'main':''}, saveFileName=None):
  """
  Args:
    filePath (string): full path file name
    style    (dict): supplied to guide the display / extraction style = recipe
                     main is / separated hierarchical elements parent->child
                     can contain more elements
    saveFileName (string): if given, save the image to this file-name
  Returns:
    dict: containing image, metaVendor, metaUser, style
  """
  # this part identifies how the csv-file is formatted: whether it uses , or ; to separate; you can skip this part when learning extractors
  # producer = 'comma separated'
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
      # producer = 'semicolon separated'
      delimiter = ';'
    if lines[0].count(',')>lines[0].count(' ') and lines[0].count(',')==lines[1].count(',') and \
                                                   lines[0].count(',')==lines[2].count(','): #Separate by , not ' '
      # producer = 'comma separated'
      delimiter = ','

  # THIS IS THE IMPORTANT PART OF THE EXTRACTOR
  data = pd.read_csv(filePath, delimiter=delimiter, skiprows=skipRows-1)     # use pandas to get data
  if style['main'] == 'measurement/csv/lines':    #: draw curve with lines
    plt.plot(data.iloc[:,0], data.iloc[:,1],'-')                             # plot data using matplotlib: check the differences in plotting
  elif style['main'] == 'measurement/csv/dots':     #: draw curve with dots
    plt.plot(data.iloc[:,0], data.iloc[:,1],'o')
  elif True or style['main'] == 'measurement/csv/linesAndDots': #: Default | uncropped
    style['main'] = 'measurement/csv/linesAndDots'                           # for the default case: set the main-style
    try:
      plt.plot(data.iloc[:,0], data.iloc[:,1],'o-')
    except Exception:
      plt.plot([0,1], [0,1],'o-')
      plt.text(0.5, 0.5, "ERROR: unclear csv file")
  plt.xlabel('time [sec]')
  plt.ylabel('value [m]')                                                    # the units are an example for this tutorial and should be changed
  try:
    if data.shape[0]>1:
      sampleFrequency = 1.0 / (data.iloc[1,0]-data.iloc[0,0])                  # a simple equation to calculate the sample frequency
    else: #if only one line in file
      sampleFrequency = 1.0
  except Exception:
    sampleFrequency = -1.0
  maxYData        = data.iloc[:,1].max()
  metaUser = {'Sample frequency [Hz]':sampleFrequency,                       # this is the easy way to denote metadata as scientists often use. Internally it is converted appropriately
              'Maximum y-data [m]':   maxYData}
  metaVendor = {}                                                            # this is translated metadata from the vendor of the instrument: since we don't know anything, leave it blank

  #Save to file: each extractor should have this as it allows the user to create a high quality image
  if saveFileName is not None:
    plt.savefig(saveFileName, dpi=150, bbox_inches='tight')

  #convert image to svg image: 2d graphs are good examples of svg files
  figfile = StringIO()
  plt.savefig(figfile, format='svg')
  image = figfile.getvalue()

  # return everything
  return {'image':image, 'style':style, 'metaVendor':metaVendor, 'metaUser':metaUser}
