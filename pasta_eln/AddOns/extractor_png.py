"""extract data from vendor
- default png file

THIS IS THE ADVANCED EXTRACTOR TUTORIAL, READ THE BASIC TUTORIAL (_csv.py) FIRST.
This tutorial teaches
- how to use style recipes with choices
  - you can specify sub-choices with the dict, as shown.
  - what you from the calling function is a string
  - for getting the value from the string, you might have to use split / strip, as shown
  - you can use as many dictionary entries as you want
  - just make sure dictionary entries are correct
  - please use this way of writing code and the extractors should work
  - for debugging: print / debuggers are working as normal
- how to create metadata data-scientifically using a list of dictionaries
  - here you can also use your language specific symbols
  - here you can also add uncertainty. If you need your uncertainty in a separate section, do so by creating a separate entry
- how to create images and scale them down to save space in the meta-data-base
- since this is a tutorial, it might not make scientific sense. The goal is teaching!
"""
import base64
from io import BytesIO
import numpy as np
from PIL import Image, ImageFilter

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
  # THIS IS THE IMPORTANT PART OF THE EXTRACTOR
  image = Image.open(filePath)
  metaVendor = image.info
  toDelete = [key for key, value in metaVendor.items() if not isinstance(value, (str, int, float, list))]
  for key in toDelete:
    del metaVendor[key]
  if style['main'] == 'measurement/image/crop':    #: Crop 3/4 of the image
    imgArr = np.array(image)
    newHeight = int(imgArr.shape[0]/2)
    newWidth  = int(imgArr.shape[1]/2)
    imgArr = imgArr[:newHeight, :newWidth, :]
    image = Image.fromarray(imgArr)
  elif style['main'] == 'measurement/image/gaussian':    #: Gaussian blur {'blur radius':['r = 1','r = 5','r = 10','r = 100']}
    radius = int(style.get('blur radius','r = 1').split('=')[-1].strip())
    image = image.filter(ImageFilter.GaussianBlur(radius = radius))
  elif True or style['main'] == 'measurement/image': #: Default | uncropped
    style['main'] = 'measurement/image'
  metaUser   = [{'key':'imageWidth',  'value':image.size[0], 'unit':'mm', 'label':'Largeur de l`image', 'IRI':'http://purl.allotrope.org/ontologies/result#AFR_0002468'},
                {'key':'imageHeight', 'value':f'{image.size[1]}+/- 3', 'unit':'mm', 'label':'Höhe des Bildes','IRI':'http://purl.allotrope.org/ontologies/result#AFR_0002467'}
               ]
  # save to file: this is the high quality image
  if saveFileName is not None:
    image.save(saveFileName)

  # convert PIL image to base64: here one should downscale
  maxSize = 400
  if max(image.size)>maxSize:
    scale = max(image.size)/maxSize
    newSize = (int(image.size[0]/scale), int(image.size[1]/scale))
    image = image.resize(newSize)
  figfile = BytesIO()
  image.save(figfile, format="PNG")
  imageB64 = base64.b64encode(figfile.getvalue()).decode()
  imageB64 = f"data:image/png;base64,{imageB64}"

  # return everything
  return {'image':imageB64, 'style':style, 'metaVendor':metaVendor, 'metaUser':metaUser}

  #other datatypes could follow here if statements are used
  #...

  #final return if nothing successful
  #return {'style': '-', 'metaVendor':{}, 'metaUser':{}}
