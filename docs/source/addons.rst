.. _addons:

Add-ons
*******

Add-ons are small, self-contained Python programs that enable multiple features. These tools can be developed or adopted by researchers and shared within the scientific community, allowing for a wide range of data processing complexities to be implemented, depending on the research goals.

Extractors
==========

Extractors are one type of add-ons, which can generate the following types of data that is automatically included in the Electronic Laboratory Notebook (ELN):

* A meaningful thumbnail or image, which helps the user to curate and annotate the measurement, and should be of sufficient size to allow for evaluation of measurement quality.
* Additional metadata, added by the scientist, which can include outliers in the measurement. This step represents a form of post-processing by the researcher, and the data is stored as a key-value pair in a dictionary.
* Metadata determined by the instrument vendor, typically in the form of a hierarchical dictionary of key-value pairs.
* Links to instruments, procedures, and other relevant elements, which can be included in the ELN if all measurements of a particular type originate from a single machine or procedure.

The flow of data processing within an add-on is guided by a style, allowing users to create custom styles to extract specific types of data. For example, a style can be created to generate a list of outliers, a particular image, or other specific data products.

The PASTA-ELN comes with a suite of common extractors for CSV, JPEG, JSON, MD, and PNG files, which are stored in a subdirectory of the program. Users can also develop their own add-ons, which should be stored in a separate directory and configured through the PASTA-ELN configuration file.

**Specifically, the extractors for PNG and JPEG are designed to serve as examples and teaching tools for users who wish to develop their own extractors.**

Project Add-ons
===============

Project add-ons leverage the hierarchical structure of the project to create reports, presentations, and other types of documents, including drafts for scientific papers. A default example includes a simple HTML-based report that can be customized to meet the user's requirements.

Table Add-ons
=============

Table add-ons draw information from tables, and can be categorized into two subtypes:

* Table add-ons that extract data directly from the table
* Table add-ons that use file names from table items to generate scientific graphs


Notes on extractors
===================

Facilitate testing and optimization of the extractor
----------------------------------------------------

You can add the following lines at the end of the extractor script:

.. code-block:: python

  if __name__ == '__main__':
    reply = use('datafile.abc', saveFileName='datafile.png')
    print('User meta:', reply['metaUser'], '\n\n')
    print('Vendor meta:', reply['metaVendor'], '\n\n')
    print('Recipe:', reply['style'])

When run from the extractor folder using `python3 extractor_abc.py`, this code enables interactive testing and debugging of the extractor. However, note that you will need to modify the code to reflect the correct filenames and data structures.

Once you have completed and optimized the extractor, you can remove these test lines to ensure the code is production-ready.

**Important Note:** When testing the extractor, avoid running it within the PASTA-ELN environment, as this can lead to inconsistent results due to the way Python loads and updates imported libraries during startup.

File Format Information and Extractor Generation
------------------------------------------------

Accurate knowledge of file formats is crucial for the development of effective extractors. To facilitate this understanding, we recommend consulting the following authoritative resources:

* The Wikipedia list of filename extensions, providing an alphabetical index of file format identifiers: https://en.wikipedia.org/wiki/List_of_filename_extensions_(alphabetical)
* The Wikipedia article on chemical file formats, offering detailed information on formats used in chemistry and related disciplines: https://en.wikipedia.org/wiki/Chemical_file_format
* The Wikipedia list of file formats, offering a comprehensive catalog of file formats and their associated extensions: https://en.wikipedia.org/wiki/List_of_file_formats



Troubleshooting Extractor-Related Issues
----------------------------------------

If errors occur during the extraction process, please refer to the following guidelines to identify and resolve the issue.

**Python Errors**: In the event of a Python error, it is essential to verify that the required library is installed. The error message typically indicates the missing library, and you can install it using pip. For example, if the error message mentions a missing library, you can install it by running `pip install <library_name>` from within the terminal.

**Metadata Errors**: Metadata should be stored as a dictionary of key-value pairs, where keys are strings and values can be strings, numbers (int or float), or boolean values. Hierarchical structures can also be created by nesting dictionaries. To ensure the correctness of your metadata dictionary, we recommend testing it using the `json.dumps()` function. If an error occurs when testing the dictionary, break it down into individual components to identify the problematic section.

.. code-block:: python

  import json

  meta_vendor = {"detector": {"calibration_a": 4, "calibration_b": 1}, "settings": "high"}
  try:
    json.dumps(meta_vendor)
  except Exception as e:
    # Break down the dictionary to identify the issue

**Matplotlib Image Conversion**: To convert a Matplotlib axis to an SVG image that can be used in PASTA-ELN, use the following code snippet:

.. code-block:: python

  from io import StringIO

  figfile = StringIO()
  plt.savefig(figfile, format="svg")
  image = figfile.getvalue()

**Pillow Image Conversion**: To convert a Matplotlib axis to a base64-encoded image, use the following code snippet. Note that you should use PNG format when creating high-contrast images and JPG format when working with images that are similar to photographs.

.. code-block:: python

  from io import BytesIO
  import base64

  figfile = BytesIO()
  image.save(figfile, format="PNG")
  image_data = base64.b64encode(figfile.getvalue()).decode()
  image = "data:image/png;base64," + image_data
