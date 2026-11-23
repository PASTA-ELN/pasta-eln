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

Metadata categories
^^^^^^^^^^^^^^^^^^^

``metaVendor`` contains metadata read from the original data file and provided
by the scientific instrument or its vendor, such as acquisition settings.

``metaUser`` contains metadata derived by the extractor that is useful for
interpreting the scientific data, such as tensile strength. Technical
provenance is stored separately in the database.

PASTA-ELN includes extractors for CSV, JPEG/JPG, JSON, LOG, MD, PNG, PY, TIF, and TSV files, and for NCLINK
pointers to :ref:`Nextcloud <nextcloud>` files. The PNG and CSV extractors serve as examples for custom development.

Testing and Optimizing Extractors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To test an extractor interactively, include the following code at the end of the extractor file:

.. code-block:: python

  from pathlib import Path

  if __name__ == '__main__':
    reply = use(Path('datafile.abc'), {'main': ''}, print)
    print('User meta:', reply['metaUser'])
    print('Vendor meta:', reply['metaVendor'])

Remove these lines before deployment.

Saving exported figures
^^^^^^^^^^^^^^^^^^^^^^^

An extractor receives a ``Path`` as ``filePath``, a style dictionary, and
PASTA-ELN's ``saveFigure`` callback, i.e. ordinary print in the case above. Do not write figures directly with
``plt.savefig`` or ``image.save``.

.. code-block:: python

  PASTA_ELN_EXTRACTOR_API = 2

  def use(filePath, style, saveFigure):
      # Matplotlib: save the current figure
      saveFigure()

      # Pillow: save this image
      saveFigure(image)

``saveFigure`` supports PNG, JPEG, and SVG. It marks exported figures so
PASTA-ELN does not add them again during a scan.

Troubleshooting Extractor Issues
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Python Errors**: Ensure required libraries are installed. Use `pip install <library_name>` to resolve missing dependencies.

**Metadata Errors**: Store metadata as key-value dictionaries. Test with `json.dumps()` to identify issues.

.. code-block:: python

  import json

  meta_vendor = {"detector": {"calibration_a": 4, "calibration_b": 1}, "settings": "high"}
  try:
    json.dumps(meta_vendor)
  except Exception as e:
    print(e)

File Format Information and Extractor Development
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Understanding file formats is crucial for developing extractors. Refer to:

* `Wikipedia: List of filename extensions <https://en.wikipedia.org/wiki/List_of_filename_extensions_(alphabetical)>`_
* `Wikipedia: Chemical file formats <https://en.wikipedia.org/wiki/Chemical_file_format>`_
* `Wikipedia: List of file formats <https://en.wikipedia.org/wiki/List_of_file_formats>`_

.. _otherAddOns:

Other Add-ons
-------------

Other add-ons enhance functionality. Settings they require, such as API keys, are entered in **Other > Configuration > Add-on parameters**.

Project Add-ons
^^^^^^^^^^^^^^^

Project add-ons act on the selected folder: right-click a folder and select **Project add-ons**, or use the
project's **More** menu for the project folder. PASTA-ELN includes:

* **Create HTML report** of the folder and its content.
* **Import CSV file**: create one item per row in the folder.
* **Sort child items** of the folder by name.
* **Import files from Nextcloud**: see :ref:`Nextcloud server integration <nextcloud>`.

Table Add-ons
^^^^^^^^^^^^^

Table add-ons process the items of a table; open them via **More > Table add-ons**. **Analyze metadata** plots
metadata of the items, and **Analyze data** plots the data in their files.

.. raw:: html

   <a href="index.html" class="back-button" style="flex: 1; height: 25px;"><b>&larr; Back</b></a>
   <span style="float: right"><img src="_static/pasta_logo.svg" alt="logo" style="width: 60px;"/></span>
