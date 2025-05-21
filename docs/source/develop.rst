.. _develop:

Guides for Contributors and Developers
======================================

.. raw:: html

   <div class="three-columns">
      <a href="index.html" class="back-button" style="flex: 1; height: 25px;"><b>&larr; Back</b></a>
      <div style="flex: 12;">
         <h2>Guides for Contributors and Developers</h2>
      </div>
   </div>

**Overview**: PASTA-ELN has benefited from contributions by many individuals. This guide provides hints and rules for those interested in contributing.

Main Contributors
------------------
- **Steffen Brinckmann**: Principal investigator, Python backend.
- **Jithu Murugan**: Developer, front-end and back-end.
- **Hanna Tsybenko**: Testing.
- **Thomas Düren**: Graphical user interfaces.
- **Raphael Röske**: Graphical user interfaces.
- **Enmar Al-Khafagi**: Backend and debugging.
- **Velislava Yonkova**: First extensive user.
- **Colleagues**: Valuable discussions and insights.

Repair Instructions
-------------------

**Repair Database File**

While PASTA-ELN is designed for reliability, errors may occur. Advanced users can repair the database by modifying the `pastaELN.db` file. **Always create a backup before making changes**. Use a SQLite editor (e.g., SQLiteBrowser) for manual inspection.

**"ERROR: Path of folder is non-unique"**

1. Open the `branches` table in the database and verify that the affected IDs point to the same path.
2. Check the `main` table to confirm if both IDs correspond to the same document using the name as a filter.
3. Identify and delete the document with lesser quality data. **Proceed carefully to avoid data loss**.
4. Record the deleted and remaining document IDs for future reference.

Uninstalling
------------

Windows
^^^^^^^

* Uninstall both python
* remove shortcut on Windows desktop
* execute

.. code-block:: batch

   del %UserProfile%\.pastaELN.json
   rmdir /s /q %UserProfile%\Documents\PASTA_ELN_DATA
   rmdir /s /q  %UserProfile%\AppData\Local\Programs\Python


Subscription to RSS feed announcing new versions
-------------------------------------------------

In your email client (e.g. Thunderbird) you can subscribe to News. Create a new entry with "PastaELN" as the
title and "https://pypi.org/rss/project/pasta-eln/releases.xml" as the URL.


Notes for Documentation Developers
-----------------------------------

When updating the documentation, ensure it is professional and concise. Use tools like GitHub Copilot to assist in refining the text.
"Can you make the markdown text professional and concise?"

.. raw:: html

   <a href="index.html" class="back-button" style="flex: 1; height: 25px;"><b>&larr; Back</b></a>
   <span style="float: right"><img src="_static/pasta_logo.svg" alt="logo" style="width: 60px;"/></span>
