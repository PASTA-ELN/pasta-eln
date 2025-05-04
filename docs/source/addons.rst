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

**Overview**: Add-ons are small Python programs that extend PASTA-ELN's functionality. Researchers can develop or adopt these tools and share them. Add-ons are categorized into :ref:`Extractors <extractors>` and :ref:`other add-ons <otherAddOns>`. Access them via "Configuration" > "Project Group" to specify their location.

.. _extractors:

Extractor add-ons
-----------------

Extractors generate metadata when scanning projects or dropping files into folders. They provide:

* **Thumbnails** for curation and annotation.
* **User-metadata** for post-processing.
* **Vendor-metadata** detailing instrument settings.
* **Links** to instruments or procedures.

PASTA-ELN includes extractors for CSV, JPEG, JSON, MD, and PNG files. PNG and JPEG extractors serve as examples for custom development.

Testing and Optimizing Extractors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To test an extractor interactively, include the following code at the end of the extractor file:

.. code-block:: python

  if __name__ == '__main__':
    reply = use('datafile.abc', saveFileName='datafile.png')
    print('User meta:', reply['metaUser'])
    print('Vendor meta:', reply['metaVendor'])

Remove these lines before deployment.

Troubleshooting Extractor Issues
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Python Errors**: Ensure required libraries are installed. Use `pip install <library_name>` to resolve missing dependencies.

**Metadata Errors**: Store metadata as key-value dictionaries. Test with `json.dumps()` to identify issues.

.. code-block:: python

  import json

  meta_vendor = {"detector": {"calibration_a": 4, "calibration_b": 1}, "settings": "high"}
  try:
    json.dumps(meta_vendor)
  except Exception e:
    print(e)

**Matplotlib Image Conversion**: Convert Matplotlib axes to SVG:

.. code-block:: python

  from io import StringIO

  figfile = StringIO()
  plt.savefig(figfile, format="svg")
  image = figfile.getvalue()

**Pillow Image Conversion**: Convert Matplotlib axes to base64-encoded images:

.. code-block:: python

  from io import BytesIO
  import base64

  figfile = BytesIO()
  image.save(figfile, format="PNG")
  image_data = base64.b64encode(figfile.getvalue()).decode()
  image = "data:image/png;base64," + image_data

File Format Information and Extractor Development
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Understanding file formats is crucial for developing extractors. Refer to:

* [Wikipedia: List of filename extensions](https://en.wikipedia.org/wiki/List_of_filename_extensions_(alphabetical))
* [Wikipedia: Chemical file formats](https://en.wikipedia.org/wiki/Chemical_file_format)
* [Wikipedia: List of file formats](https://en.wikipedia.org/wiki/List_of_file_formats)

.. raw:: html

   <a href="index.html" class="back-button" style="flex: 1; height: 25px;"><b>&larr; Back</b></a>

.. _otherAddOns:

Other Add-ons
-------------

Other add-ons enhance functionality and may include API keys for external services.

Project Add-ons
^^^^^^^^^^^^^^^

Generate reports, presentations, and drafts for scientific papers using the project's hierarchical structure. A default example includes a customizable HTML-based report.

Table Add-ons
^^^^^^^^^^^^^

Process data from tables:

* Extract data directly from tables.
* Use filenames from table items to generate scientific graphs.

.. raw:: html

   <a href="index.html" class="back-button" style="flex: 1; height: 25px;"><b>&larr; Back</b></a>
   <span style="float: right"><img src="_static/pasta_logo.svg" alt="logo" style="width: 60px;"/></span>
