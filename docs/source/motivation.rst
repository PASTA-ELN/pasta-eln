Motivation
**********

Extractors are little python scripts that 'extract' metadata, thumbnails and user-metadata from the raw measurement files. These little programs can be written/adopted by scientists and can be shared. :ref:`To read more ... for advanced users <extractors>`.

Adaptive software development (scrum) has revolutionized software projects. We believe that **agile project planning** is also highly beneficial for scientific research projects. :ref:`To read more ... for all users <Agile Project Planning>`.

In `PASTA-ELN`_, the meta-data is stored in a document database called **CouchDB**. This non-SQL database is very adaptive to the different raw data sources and corresponding different meta-data. People that want to contribute to PASTA-ELN, :ref:`read more on the CouchDB implementation <CouchDB information>`.

The raw data is the origin of scientific work and has to follow the FAIR principles to be trusted. PASTA used and perhaps might use in the future **DataLad** for the raw data and simplifies it to the typical use of experimental material scientists.

If CouchDB and DataLad are the two legs on which PASTA is built (and agile project planning is its heart), then the **python backend and graphical user interfaces (GUI)** is its torso, which links everything together. People that want to contribute to PASTA-ELN, :ref:`Read more on the implementation <Python implementation>`.

The development of the software started shortly before the Corona-pandemic hit Germany in 2020.

.. _PASTA-ELN: https://pasta-eln.github.io/pasta-eln/


Agile Project Planning
======================

Motivation: one of the inspirations for PASTA was the agile project management for IT-projects `(wikipedia) <https://en.wikipedia.org/wiki/Scrum_(software_development)>`_. We believe that **agile project planning** is also highly beneficial for scientific research projects. Here, we briefly talk about how PASTA-ELN can be used for agile project planning.

PASTA uses a hierarchy in its datastructure and on the hard disk which is inspired by SCRUM.

- projects have

  - a name: e.g. Peter_Tribology
  - a objective/goal (paper, thesis *writing*, baked cake) [optional]
  - a status [paused, active, finished]

- steps, sprint, tasks:

  - should have mini-objectives
  - in SCRUM-projects it is in between one meeting and next
  - by default, they are called task to make it easier for beginners

- subtasks

  - the smallest level in the default configuration
  - in SCRUM-projects it is specified by the worker,

Benefits of this hierarchical local folders and projects are:

- programs can efficiently process it
- other people/supervisor can collaborate
- do not only exchange .pptx presentations but data, meta-data, and information

This could result in a project directory that looks like:

- 00\_Experiment_Instrument1
- 01\_Experiment_Instrument2
- 02\_Analysis
- PAPER
- TALK

CouchDB information
===================
Here we discuss design concepts of the chosen database and why we choose the CouchDB implementation

Why choose a NoSQL database and not a SQL database
--------------------------------------------------

- NoSQL databases (CouchDB, MongoDB)

  - are good for unstructured data. As such any document/information can be added. This is very beneficial in scientific environments and ELNs in particular since the structure is not fixed.
  - are a little slower when creating tables. This drawback is not so relevant for ELNs. However, if you are a bank with millions of customers, you want to scan that database fast.

- SQL databases (Oracle, MySQL, ...)

  - are good for structured data and metadata. Bank customers all have a name, address, portfolio value, ...
  - Could be appropriate for a lab-assistant structure in which 10 technicians create data according to fixed protocols and a single person digests it.

Why did we choose CouchDB and not MongoDB?
------------------------------------------

- The REST-API for CouchDB exists and that feature allows fast development of HTML pages, mobile access....
- The REST-API for MongoDB has to be written using a nodeJS server and should follow the same protocol as the REST-API for CouchDB.

Once the version of CouchDB is operational, the MongoDB API can be written and one could switch to MongoDB, which might have advantages in the future.

How is hierarchical information stored
--------------------------------------

One part of PASTA is the hierarchical information: a project is the "parent" of everything, task is a "child", a subtask is a "grandchild" in computer language. There are two possibilities to create this structure in a flat database:

- Case 1 - upward linking: "I am the child of ..."

  - The difficulty in this setup is that one needs to account for the order of child.
  - Hence two fields are required: ancestors tree (or only parent) and child-number ["I am the 3rd child"]
  - This approach is used in PASTA: "stack" has the id-numbers of the ancestors and childNum is count

- Case 2 - downward linking: "I have these children [list of children]"

  - Advantage: only order of children required and these are only stored once.
  - Disadvantage: adding one child requires that the parent is changed: it has a new child
  - Disadvantage: for fast indexing and table building, each person should know the project ID. This is not stored in this approach and hence an additional field would be required.
  - This approach was used in very early versions of PASTA until the 2nd disadvantage was identified.

- Implementation details

  - "path", "child-number" and "stack of id-numbers" (parental hierarchy) form a branch
  - a measurement, sample, procedure can have multiple branches as the scientist can use a measurement in different projects.
  - Projects/tasks/subtasks only have one branch as they are only existent in a project.


What data is stored:
--------------------

Different types of data (different document types) are stored in the database:

- text items: projects, tasks, subtasks
- data: samples, procedures
- automatically added: measurements

Other things don't need to be stored:

- own papers (is an automatic result of projects)
- presentations (is an automatic result of projects)
- literature database: belong to project, can be searched anyhow


Database design technical details
---------------------------------

All documents have the following properties

- type is a list of hierarchical types:
  - examples for most data: ["measurement", "Zeiss tif image"], ["measurement", "Indentation", "Pop-in study"]
  - text items (projects, tasks) are ["x0"], ["x1"], ... as the types are non hierarchical in the class view (IT-term). A task is not a special class of the project class. Moreover, the hierarchical level is ingrained in the type
- Tags #tag, #1 (no spaces in the string). #1 implies one-star, #2 implies two-stars. Tags are stored as list of stings.
- other fields can be easily added in the comment field of the form and are thereafter separated. Examples for other fields:  :BakingTime:2h: :quality:3:  (':' is a marker here)
- Comments
  - If the user enters a comment in the comment field: tags and fields are subtracted and everything that remains is the comment
  - Comments should be in the Markdown format (Pandoc flavor)
- List of branches: each branch has a path (link to the file on disk, remote url), its hierarchy-stack and the number of this child
- all data should be saved in SI units or specified

Examples
--------

Essential items have a preceding '-'

Samples:
  {-type:["sample"], -name: "sample1", chemistry: "Cu50Co50", origin: "deposition in oven", size: "3 x 3 mm"}

Procedures:
  {-type:["procedure", "EM"], -name: "How to do TEM", content: "Arbitrary text in md-format including \n", tags: ["#TEM"]}

Text/Hierarchical entries: Project, Tasks
  {-type:["x0"], -name: "Identify phase", objective: "Identify phase at boundary", status: "active", tags: ["TEM","experiments"]}

  {-type:["x1"], -name: "Inspect in TEM", comment: "Text in md-format including \n", tags: ["TEM"]}

  {-type:["x2"], -name: "Inspect in TEM on Monday", text: "Text in md-format including \n", tags: ["TEM"], procedure:link to #id}

Measurements
  {-type: ["measurement", "Zeiss"], -branch:{path:<link>}, producer: Zeiss, SHASUM: "43aa", comment:"Ugly picture"}

  {-type: ["measurement", "Zwick"], -branch:{path:<link>}, producer: Zwick, SHASUM: "43aa", comment:"Slip in grips"}

  {-type: ["measurement"], Youngsmodulus: "300GPa", Hardness "10GPa"}

  All measurements have an SHASUM of their original state (Git-shasum see [dataLad](dataLad.md)) to ensure that the data is not changed from its original state. DataLad has an additional mechanism to ensure data integrity.

Views
-----

Views are tables that are created automatically and are rather fast. The following items should be in each table/view.

- ProjectID should be the key in each view to allow for easy filtering
- all project headers form a view for the project overview
- a hierarchical tree of a given project
- all procedures,... are assembled in a view
- all tags are assembled in a view and can be used in future to find items fast

Python implementation
=====================

Data storage
------------

- The filesystem is the general storage of data.
- DataLad allows the revision and inclusion of large external data. This is efficient and does not change the filesystem as general storage.
- A DataLad dataset can be projects, steps, task
- Data are measurements, Standard-Operating-Procedures, Sample-Figures, ...
- Project management (Projects, Steps, Tasks) form a hierarchical folder structure.
- Local filesystem
  - gives user incentive to use structure
  - to allow the user to drop in files
  - raw data can be stored here (.tif, .mss)
- Completely external data is possible as link and authorization is stored

Metadata storage
----------------

- Stored as CouchDB as most flexible as metadata for different experiments necessarily differs
- Project management (Project, Steps, Task) is included in metadata storage
- The result of curation "Low-quality image" is stored

Bracket across data and metadata storage
----------------------------------------

- Python backend that allows extractors (default and custom) for metadata from measurement files
- Python-Command-Line-Program interacts between user and backend
- React-Electron programs (GUI) interact in between user and backend
- All these form super layer on top of Metadata and Data storage

Access Control and Authorship
-----------------------------

- Layout depends on the filesystem, DataLad/Git and CouchDB; each has Access Control (read,write access)
- Software only has to interact with these (existing) access-control concepts
- Authorship is saved in data and meta-data automatically for data and semi-automatically for meta-data
- The authorship can be stolen in any case: "If I can read a file, I can copy/screenshot it and claim it is mine". The only weapon against authorship thieves is publishing to _trusted_ 3rd parties (journals, DataLad/Git repositories).
- Only one author/user PID has to be stored, e.g. ORCID-ID

Revision control is included
----------------------------
- in data and metadata storage

