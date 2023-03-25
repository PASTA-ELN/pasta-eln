Extractors
**********

This page should become an overview on extractors. Those are little python programs that 'extract' metadata, thumbnails and user-metadata from the raw files. These little programs can be written/adopted by scientists and can be shared. Because of this, the extractors can have any level of data processing complexity, depending on the research goals. The extraction output (usually an image or a plot) can be viewed via the GUI, and additional options can be defined for convenient post-processing by a scientist. Thus, PASTA-ELN provides a tool for the initial data analysis and overview of measurement results.

The list of extractors available for all PASTA-ELN users after installation includes extractors for CSV, JPEG, JSON, MD, and PNG files. They are stored in the following directory after installation of PASTA-ELN: home/./ PastaSoftware/Python/Extractors
A typical Python extractor file has the following structure::

  """extract data from vendor FEI/ThermoFischer """
  # import default libraries
  import base64
  from io import BytesIO
  import matplotlib.pyplot as plt
  # import a library for TEM images
  import ncempy.io as nio

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
    data = nio.read(filePath)
    if recipe.endswith('threshold'):             #: crop contrast to 200-500
      recipe = 'image/ser/threshold'
      plt.imshow(data['data'], vmin=200, vmax=500, cmap='gray')
      metaUser = {'num. black pixel':len(data['data'][data['data']<200]),\
                  'num. white pixel':len(data['data'][data['data']>500])}
    else:                                         #: Default | unchanged
      recipe = 'image/ser'
      plt.imshow(data['data'], cmap='gray')
      metaUser = {}
    plt.axis('off')

    #save to file; this is particular helpful for testing the extractor
    if saveFileName is not None:
      plt.savefig(saveFileName, dpi=150, bbox_inches='tight')

    # finally the image (PIL image) has to be converted to a base64 image
    figfile = BytesIO()
    plt.savefig(figfile, format='PNG')
    imageData = base64.b64encode(figfile.getvalue()).decode()
    imageData = "data:image/png;base64," + imageData

    # the vendor metadata is saved
    if 'metadata' in data:
      metaVendor = data['metadata']
    else:
      metaVendor = {}
    metaVendor['pixelSize'] = data['pixelSize']
    metaVendor['pixelUnit'] = data['pixelUnit']

    # all gathered information is returned to PASTA-ELN, or any other program calling this method
    return {'image':imageData, 'recipe':recipe, 'metaVendor':metaVendor, 'metaUser':metaUser}

    #if the .ser file extension is also used by other sources, those could follow here and be separated by
    #  if else statements. All of these should at least finish with a empty return
    # return {}


General information on file formats can be found:
- [https://en.wikipedia.org/wiki/List_of_filename_extensions_(alphabetical)]
- [https://en.wikipedia.org/wiki/Chemical_file_format]
- [https://en.wikipedia.org/wiki/List_of_file_formats]

Unidentified files can be viewed within the project, assigned to a particular type, and a scientist can add additional metadata via the GUI.

Help if extractors do cause errors
==================================

Python errors
-------------

Lala

Metadata error
-------------

Lala

Matplotlib
----------

Please use the following code block to convert to matplotlib axis to svg image::

  from io import StringIO
  # all other lines of code ...
  figfile = StringIO()
  plt.savefig(figfile, format="svg")
  image = figfile.getvalue()

Pillow image
------------

Please use the following code block to convert to matplotlib axis to a base64 encoded image::

  from io import BytesIO
  # all other lines of code ...
  figfile = BytesIO()
  image.save(figfile, format="PNG")
  imageData = base64.b64encode(figfile.getvalue()).decode()
  image = "data:image/png;base64," + imageData

Please pay special attention when to use png and when jpg.
