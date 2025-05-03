.. _addons:

Add-Ons
=======

.. raw:: html

   <div class="three-columns">
      <a href="index.html" class="back-button" style="flex: 1; height: 25px;"><b>&larr; Back</b></a>
      <div style="flex: 12;">
         <h2>Add-Ons</h2>
      </div>
   </div>

**Overview**: Add-ons are **small Python programs** that extend functionality, similar to browser add-ons. Researchers can develop or adopt these tools and share them with others. Add-ons are categorized into Extractors and other add-ons.

To access add-ons, navigate to "Configuration" > "Project Group" to specify their location. Existing add-ons can be copied from a previous location.

Extractors
----------

Extractors automatically generate metadata when a project is scanned or a file is dropped into a folder. They provide:

* **Thumbnails** or images to assist in curating and annotating measurements.
* **User-metadata** for automatic post-processing.
* **Vendor-metadata** detailing instrument settings.
* **Links** to instruments, procedures, or other elements when measurements originate from a single source.

Data processing in an extractor follows a style, allowing users to create custom styles for specific data types, such as outlier lists or images.

PASTA-ELN includes extractors for CSV, JPEG, JSON, MD, and PNG files. PNG and JPEG extractors serve as examples for users to develop their own extractors.

Testing and Optimizing Extractors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To test an extractor interactively, include the following code at the end of the extractor file. Modify filenames and data structures as needed:

.. code-block:: python

  if __name__ == '__main__':
    reply = use('datafile.abc', saveFileName='datafile.png')
    print('User meta:', reply['metaUser'], '\n\n')
    print('Vendor meta:', reply['metaVendor'], '\n\n')

Remove these lines before deploying the extractor to ensure production readiness.

Troubleshooting Extractor-Related Issues
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If errors occur during the extraction process, please refer to the following guidelines to identify and resolve the issue.

**Python Errors**: In the event of a Python error, it is essential to verify that the required library is installed. The error message typically indicates the missing library, and you can install it using pip. For example, if the error message mentions a missing library, you can install it by running `pip install <library_name>` from within the terminal.

**Metadata Errors**: Metadata should be stored as a dictionary of key-value pairs. Hierarchical structures can also be created by nesting dictionaries. To ensure the correctness of your metadata dictionary, we recommend testing it using the `json.dumps()` function. If an error occurs when testing the dictionary, break it down into individual components to identify the problematic section.

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


File Format Information and Extractor Development
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To develop effective extractors, understanding file formats is crucial. The following resources provide authoritative information:

* [Wikipedia: List of filename extensions](https://en.wikipedia.org/wiki/List_of_filename_extensions_(alphabetical)) - An alphabetical index of file format identifiers.
* [Wikipedia: Chemical file formats](https://en.wikipedia.org/wiki/Chemical_file_format) - Detailed information on formats used in chemistry and related disciplines.
* [Wikipedia: List of file formats](https://en.wikipedia.org/wiki/List_of_file_formats) - A comprehensive catalog of file formats and their extensions.

.. raw:: html

   <a href="index.html" class="back-button" style="flex: 1; height: 25px;"><b>&larr; Back</b></a>

Other Add-ons
-------------

Other add-ons enhance PASTA-ELN's functionality and can include API keys for accessing external services. They are categorized as follows:

Project Add-ons
^^^^^^^^^^^^^

These add-ons utilize the project's hierarchical structure to generate reports, presentations, and other documents, including drafts for scientific papers. A default example includes a customizable HTML-based report.

Table Add-ons
^^^^^^^^^^^^^

Table add-ons process data from tables and are divided into two types:

* Add-ons that extract data directly from tables.
* Add-ons that use filenames from table items to generate scientific graphs.



