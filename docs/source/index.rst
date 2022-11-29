PASTA electronic lab notebook (ELN) | The favorite ELN for experimental scientists
**********************************************************************************

Pasta-dishes are a mixture pasta and sauce, the latter adds flavors and richness to the otherwise boring pasta. This ELN combines raw-data with rich metadata to allow advanced data science. In the database, one can fully adapt and improvise the metadata definitions to generate something novel. `PASTA-ELN`_ uses a local-first approach: store all data and metadata locally (always accessible to user) and synchronize with a server upon user request.

Extractors are little python scripts that 'extract' metadata, thumbnails and user-metadata from the raw measurement files. These little programs can be written/adopted by scientists and can be shared. :ref:`To read more ... for advanced users <extractors>`.

In `PASTA-ELN`_, the meta-data is stored in a document database called **CouchDB**. This non-SQL database is very adaptive to the different raw data sources and corresponding different meta-data. :ref:`Read more on this CouchDB implementation ... for developers of PASTA <couchDB>`.

Adaptive software development (scrum) has revolutionized software projects. We believe that **agile project planning** is also highly beneficial for scientific research projects. :ref:`To read more ... for all useres <agileProjects>`.

The raw data is the origin of scientific work and has to follow the FAIR principles to be trusted. PASTA uses **DataLad** for the raw data and simplifies it to the typical use of experimental material scientists. :ref:`To read more on the use of dataLad ... for developers <dataLad>`.

If CouchDB and DataLad are the two legs on which PASTA is built (and agile project planning is its heart), then the **python backend** is its torso, which links everything together. :ref:`Read more on the backend ... for developers <software>`.

All users will interact with the python backend via **graphical user interfaces (GUI)** that use Qt and python for responsive work. :ref:`Read more on the GUI and React implementation ... for developers <software>`.

.. image:: _static/pyside.png

The development of the software started shortly before the Corona-pandemic hit Germany in 2020. The current state is given in :ref:`features <features>`.

More questions are answered in the :ref:`FAQs <faqs>`.

Overview
========

.. toctree::
   :maxdepth: 1

   faqs
   extractors
   couchDB
   agileProjects
   datalad
   software
   _notes_on_rst

Main contributors
=================
* Steffen Brinckmann: principal investigator, focuses on python backend
* Thomas Düren: graphical user interfaces
* Velislava Yonkova: first extensive user
* Hanna Tsybenko: documentation improvements
* multiple colleagues that help with their valuable discussions


.. |---| unicode:: U+02014 .. em dash

.. _PASTA-ELN: https://pasta-eln.github.io/pasta-eln/
