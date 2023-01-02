""" Depricated functions that might be come usefull again in the future """

def stringToImage(aString, show=True):
  """
  convert a b64-string to png file
  - not really used

  Args:
    aString (string): 64byte string of image
    show (bool): show image

  Returns:
    Image: image of string
  """
  import base64, io
  from PIL import Image
  imgdata = base64.b64decode(aString)
  image = Image.open(io.BytesIO(imgdata))
  if show:
    image.show()
  return image
