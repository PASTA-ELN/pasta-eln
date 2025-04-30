
**User-Centered Approaches**: Three distinct user stories illustrate the versatility of PASTA-ELN:

**Local-First Approach**: PASTA-ELN employs a local-first approach, storing all data and metadata on the user's storage device and synchronizing it with a server upon request. This ensures that data remains accessible through conventional software and maintains its security and confidentiality. Additionally, researchers can customize metadata definitions and create arbitrary folder structures to accommodate their unique workflows and research objectives. This flexibility allows users to easily transfer their data to other computers, collaborators, institutions, or archives by zipping the contents of their hard disk.


Main contributors
=================
* Steffen Brinckmann: principal investigator, focuses on python backend
* Jithu Murugan: developer, focuses on front-end and back-end
* Hanna Tsybenko: testing
* Thomas Düren: graphical user interfaces
* Raphael Röske: graphical user interfaces
* Enmar Al-Khafagi: backend and debugging
* Velislava Yonkova: first extensive user
* multiple colleagues that help with their valuable discussions

Troubleshooting Verification Errors in PastaELN
===============================================

While PastaELN is designed to be reliable, errors can still occur. In such cases, advanced users can take steps to repair the data structure by modifying the underlying database file. **Before attempting any repairs, it is essential to create a backup of the pastaELN.db file** to prevent any potential data loss. The user can always manually inspect the database by opening the .db file with a sqlite editor (for instance SQLiteBrowser)

Error Resolutions
-----------------

### 1. "ERROR: Path of folder is non-unique"

1. Open the 'branches' table in the database using the sqlite editor (see above) and verify that the two affected IDs indeed point to the same path.
2. Open the 'main' table and check if both IDs correspond to the same document, using the name as a filter.
3. Identify the document with the lesser quality data and delete it. **Please note that this may require careful consideration to avoid data loss**.
4. Record the deleted and remaining doc-IDs in the table, as this information may be useful for future reference.

### 2. "ERROR: File on harddisk but not DB"

1. Perform a scan of the folder to locate any new data.

Deleting Documents
------------------

In most cases, errors occur due to document duplication. To resolve this, you can either use the serverActions API directly or write a small script to remove multiple documents.

By following these guidelines, you can effectively troubleshoot and resolve verification errors in PastaELN, ensuring the accuracy and reliability of your results.

.. |---| unicode:: U+02014 .. em dash
