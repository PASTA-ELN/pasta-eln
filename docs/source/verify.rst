How to fix errors that occur during verification
************************************************

Obviously, verification errors should not occur. But bugs occur in all software. Since PastaELN is an open software, advanced users can repair the data structure of it. To do that, locate the pastaELN.db file in the root of your data structure and **make a backup**. Then open the .db file with a sqlite editor (for instance SQLiteBrowser)

For errors:
===========

1. **ERROR Path of folder is non-unique" do the following**

    - open 'branches' table in database: use both ids to check if they indeed have same path
    - open 'main' table in database: check if they are the same (you can use the name to filter both)
    - choose worse document and delete it (see below), as there was likely a copy error.
        to choose: check if data on harddisk can help determine which is better
    - save deleted and remaining doc-ids in table as information might be helpful down the road

2. **ERROR File on harddisk but not DB**

    - Scan folder to find new data

3. **ERROR bch01: These files of database not on filesystem**

    - open 'branches' table and search for that path in branch:
    - if indeed double AND if that docID is also present in other errors

        - ERROR branch stack parent is bad:
        - ERROR parent does not have corresponding path (remote)

    - delete that document

How to delete documents:
========================

Experience shows that the only error that occurs in Pasta is that documents got doubled. Hence, one has to be removed. To do that, use serverActions directly or write a small script to remove multiple.
