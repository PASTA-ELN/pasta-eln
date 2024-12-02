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

### 3. "ERROR: bch01: These files of database not on filesystem"

1. Open the 'branches' table and search for the affected path in the branch.
2. If both IDs are affected and the docID is also present in other errors, delete the document.

Deleting Documents
------------------

In most cases, errors occur due to document duplication. To resolve this, you can either use the serverActions API directly or write a small script to remove multiple documents.

By following these guidelines, you can effectively troubleshoot and resolve verification errors in PastaELN, ensuring the accuracy and reliability of your results.
