"""extract data from vendor
- default jpeg image
"""
import base64, json
from io import BytesIO
import numpy as np
from PIL import Image
import PIL.ExifTags
import matplotlib.pyplot as plt
import cv2 as cv
from micromechanics.tif import Tif

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
  # Extractor
  image = Image.open(filePath)
  metaVendor = {k:str(v) for k, v in image.info.items()} #some of these are tuple of strange
  metaUser={}
  exif = image._getexif()                                # pylint: disable=protected-access
  imageCreated = False
  if exif is None:
    #JEOL SEM
    flagJeol = True
    txtFile = filePath.parent/(filePath.stem+'.txt')
    links = [{'docType':'sample', 'key':'-name', 'value':filePath.name[4:12]},
             {'docType':'instrument', 'key':'-name', 'value':'JEOL-SEM'}]
    if txtFile.exists():
      with open(txtFile) as txtIn:
        data = txtIn.read().split('\n')
        dataDict = {}
        for i in data:
          parts = i.split(' ')
          if parts[0]=='' or parts[0].startswith('$AN_'):
            continue
          dataDict[parts[0].replace('$','')] = ' '.join(parts[1:])
        metaVendor = dataDict
    #move into TIF lib
    if recipe.endswith('jeol/fancy'):  #: plot cropped image with nice scale-bar
      img = Tif('','Void')
      pixelSize = float(metaVendor['SM_MICRON_MARKER'][:-2])/int(metaVendor['SM_MICRON_BAR'])
      img.setData(image, pixelSize)
      img.crop(-1,-1, -1, int(metaVendor['CM_FULL_SIZE'].split(' ')[1]))
      img.addScaleBar()
      imgArr = np.array(img.image)
      plt.imshow(imgArr, cmap='gray')
      imageCreated = True
    elif recipe.endswith('jeol/crop'):  #: crop to meaningful domain
      imgArr = np.array(image)[:int(metaVendor['CM_FULL_SIZE'].split(' ')[1]),:]
      plt.imshow(imgArr, cmap='gray')
      imageCreated = True
    elif recipe.endswith('jeol/raw'):   #: raw image from SEM
      imgArr = np.array(image)
      plt.imshow(imgArr, cmap='gray')
      imageCreated = True

  else:
    flagJeol = False
    #Olympus Proimage
    exif = {PIL.ExifTags.TAGS[k]: str(v) for k, v in exif.items() if k in PIL.ExifTags.TAGS}
    del metaVendor['exif']
    metaVendor.update(exif)
    imgArr = np.array(image)[:,:,0]  #reduce to one layer
    #pixelSize=2.755
    links = [{'docType':'sample', 'key':'-name', 'value':filePath.name[12:-7]}]
    if recipe.endswith('metallo/domain'):  #: plot domain of intrest over image
      avrg0 = (np.average(imgArr, axis=0)>100).astype(np.int8)
      strt0 = np.argmax(np.gradient(avrg0))
      end_0 = np.argmin(np.gradient(avrg0))
      mid_0 = int((strt0+end_0)/2)
      avrg1 = (np.average(imgArr, axis=1)>100).astype(np.int8)
      strt1 = np.argmax(np.gradient(avrg1))
      end_1 = np.argmin(np.gradient(avrg1))
      mid_1 = int((strt1+end_1)/2)
      hLength = int(3276/2)
      plt.imshow(imgArr, cmap='gray')
      plt.axhline(mid_1)
      plt.axhline(mid_1-hLength, c='red', linestyle='dashed')
      plt.axhline(mid_1+hLength, c='red', linestyle='dashed')
      plt.axvline(mid_0)
      plt.axvline(mid_0-hLength, c='red', linestyle='dashed')
      plt.axvline(mid_0+hLength, c='red', linestyle='dashed')
      imageCreated = True
    if recipe.endswith('metallo/highlight'): #: highlight pores
      avrg0 = (np.average(imgArr, axis=0)>100).astype(np.int8)
      strt0 = np.argmax(np.gradient(avrg0))
      end_0 = np.argmin(np.gradient(avrg0))
      mid_0 = int((strt0+end_0)/2)
      avrg1 = (np.average(imgArr, axis=1)>100).astype(np.int8)
      strt1 = np.argmax(np.gradient(avrg1))
      end_1 = np.argmin(np.gradient(avrg1))
      mid_1 = int((strt1+end_1)/2)
      hLength = int(3276/2)
      plt.imshow(imgArr, cmap='gray')
      kernel = np.ones((40,40),np.uint8)
      imgArrCropped = imgArr[mid_0-hLength:mid_0+hLength, mid_1-hLength:mid_1+hLength]
      imgVoid       = (imgArrCropped>100).astype(np.uint8)
      metaUser['percent pores'] = (1-imgVoid).sum()/imgVoid.shape[0]/imgVoid.shape[1]*100.
      imgVoidLarge  = cv.erode(imgVoid,kernel,iterations = 1)
      plt.imshow(1-imgVoidLarge, extent=[mid_0-hLength,mid_0+hLength, mid_1-hLength,mid_1+hLength ], cmap='Reds', alpha=1-imgVoidLarge, vmax=2)
      plt.xlim((0,imgArr.shape[0]))
      plt.ylim((imgArr.shape[1],0))
      imageCreated = True
    elif recipe.endswith('metallo/raw'):  #: raw image from metallo
      plt.imshow(imgArr, cmap='gray')
      imageCreated = True

  if imageCreated:
    pass
  else: #: Default: raw image
    if flagJeol:
      imgArr = np.array(image)
      plt.imshow(imgArr, cmap='gray')
      recipe = 'jeol/raw'
    else:
      plt.imshow(imgArr, cmap='gray')
      recipe = 'metallo/raw'


  #save to file
  plt.axis('off')
  if saveFileName is not None:
    plt.save(saveFileName)

  # convert PIL image to base64
  figfile = BytesIO()
  plt.savefig(figfile, format="JPEG", dpi=150, bbox_inches='tight' )
  imageData = base64.b64encode(figfile.getvalue()).decode()
  imageData = "data:image/jpeg;base64," + imageData

  # return everything
  return {'image':imageData, 'recipe':recipe, 'metaVendor':metaVendor, 'metaUser':metaUser, 'links':links}

  #other datatypes could follow here if statements are used
  #...
  #final return if nothing successful
  #return {}
