Table of contents
=================

.. contents::
    :depth: 2

Extractors
==========

Extractors are little python programs that 'extract' metadata, thumbnails and user-metadata from the raw files. These little programs can be written/adopted by scientists and can be shared. Because of this, the extractors can have any level of data processing complexity, depending on the research goals. In detail, the extractor generates the following data that is automatically included in the ELN:

- the meaningfull thumbnail / image helps the user to curate and annotate the measurement. As such it should be sufficiently big to allow the user to judge the measurement qualitiy.
- the metadata as determined by the instrument vendor. This data is a typical dictionary of key-value terms that can be hierarchical.
- the scientist user can add additional metadata that is beneficial for the research project, e.g. outliers in this measurement. This step is a kind of post-processing by the scientist. Also this data is stored as key-value pairs in a dictionary.
- links to instruments, procedures, .... If all measurements of one type come from one machine or the measurements are based on one measurement procedure, a link to these descriptions can be added, such that it is automatically included in the ELN. Please note that this is optional and greatly depends on the individual lab.

The flow inside the extractor is guided by the recipe. As such, one can create a recipe to create only a list of outliers, create only a particular image, ...

The list of common extractors available for all PASTA-ELN users includes extractors for CSV, JPEG, JSON, MD, and PNG files. They are stored in a subdirectory of the PASTA-ELN program. If you want to have you own extractors, please put them in a separate directory and define this directory in the configuration file.

Tutorial: Extractor explained
=============================
A typical Python extractor file starts, as any python file, with a headerline with '"'-marks and the import of the required libraries::

  """extract data from vendor FEI/ThermoFischer """
  import base64
  from io import BytesIO
  import matplotlib.pyplot as plt
  import ncempy.io as nio

Here we want to create a thumbnail/image that is of jpg-type, therefore we need the base64 and BytesIO library. Since we also want to plot with matplotlib, we include that library. A TEM measurement can be opened with the ncempy library; your measurement might require different libraries.

All extractors have a common interface, which starts with the following python code::

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

The first argument is a path to the file as a string.  The recipe allows to guide the extraction: if you create an extractor for datafile.abc this recipe starts typically with 'measurement/abc/' and can be 'measurement/abc/outlier' if it is for outlier identifaction. The last argument is the fileName used for saving; if it is not given, no image is saved. This function is helpful if you create a extractor and want to verify things.

The main part of the extractor comes next. These lines have to be adopted for the measurement in question and might be adopted by the scientist for the individual preference (The other parts of the extractor are more-or-less identical for all extractors)::

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

Here we use a ncempy library to get the data, use matplotlib to plot it and calculate some metadata: the number of black and white pixel. We also see how if-else statements are used on recipes to guide the image creation and the creation of user-metadata.

Then a few lines are included, to create a image-file on the harddisk. This is only for testing and not used in the ELN::

    if saveFileName is not None:
      plt.savefig(saveFileName, dpi=150, bbox_inches='tight')

Next, the image / matplotlib graph is converted to a base64-image, which is a string of letters and numbers. Here we choose to convert it to a png-image. Alternatively you can also use a jpg, which you would have to change in two spots in the following lines.

    figfile = BytesIO()
    plt.savefig(figfile, format='PNG')
    imageData = base64.b64encode(figfile.getvalue()).decode()
    imageData = "data:image/png;base64," + imageData

Lastly, the metadata of the instrument vendor is saved into a dictionary. In this case, some files do not have that data so an additional if-statement is required to not cause unpredictable crashes::

    if 'metadata' in data:
      metaVendor = data['metadata']
    else:
      metaVendor = {}
    metaVendor['pixelSize'] = data['pixelSize']
    metaVendor['pixelUnit'] = data['pixelUnit']

All gathered information is returned to PASTA-ELN, or any other program calling this method::

    return {'image':imageData, 'recipe':recipe, 'metaVendor':metaVendor, 'metaUser':metaUser}


Extractor template
==================

If you want to create a new extractor for a datafile.abc then we suggest that you create a file 'extractor_abc.py' in the same directory as the datafile.abc and copy the following code into that file::

  """extract data from vendor ... """
  import base64
  from io import BytesIO
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
    # HERE MAIN PART OF EXTRACTOR

    #save to file; this is particular helpful for testing the extractor
    if saveFileName is not None:
      plt.savefig(saveFileName, dpi=150, bbox_inches='tight')

    figfile = BytesIO()
    plt.savefig(figfile, format='PNG')
    imageData = base64.b64encode(figfile.getvalue()).decode()
    imageData = "data:image/png;base64," + imageData

    return {'image':imageData, 'recipe':recipe, 'metaVendor':metaVendor, 'metaUser':metaUser}

  if __name__=='__main__':
    reply = use('datafile.abc',saveFileName='datafile.png')
    del reply[image]
    print(reply)

Then you can change and optimize the code by running 'python3 extractor_abc.py'. Of course you have to replace filenames and define imageData, metaVendor, .... After you have finished the extractor, you can remove the last four lines.

General information on file formats

General information on file formats can be found on different pages across the web and can help you to generate extractors

- https://en.wikipedia.org/wiki/List_of_filename_extensions_(alphabetical)
- https://en.wikipedia.org/wiki/Chemical_file_format
- https://en.wikipedia.org/wiki/List_of_file_formats



Help if extractors do cause errors
==================================

Python errors
-------------

Python errors should not occur after writing the extractor and are mainly connected to a library not being installed. Please check the last line of the output to guide your error-search.

Metadata error
--------------

Matadata should be key-value pairs stored in dictionaries: metaVendor={"username":"Elvis", "outlier":4}. As seen, the keys have to be strings, while the values can be strings, numbers (int, float) or even boolean values. You can even create hierarchical structures: metaVendor={"detector":{"calibration a":4, "calibration b":1}, "settings":"high"} where detector is another dictionary. Be careful which values you store. Some instruement vendors store non-latin letters or use different numbers which would lead to failures down the road. Therefore, it is good to always test your dictionary when creating them::

  json.dumps(metaVendor)

If that command is successful, everything is fine. If an error occurs, subdivide our previous metaVendor and test individual parts to find the offending section.


Matplotlib
----------

Please use the following code block to convert to matplotlib axis to svg image, that can be used in PASTA-ELN::

  from io import StringIO


  figfile = StringIO()
  plt.savefig(figfile, format="svg")
  image = figfile.getvalue()

Pillow image
------------

Please use the following code block to convert to matplotlib axis to a base64 encoded image::

  from io import BytesIO


  figfile = BytesIO()
  image.save(figfile, format="PNG")
  imageData = base64.b64encode(figfile.getvalue()).decode()
  image = "data:image/png;base64," + imageData

Please pay special attention when to use png and when jpg.
