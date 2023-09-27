PASTA (adaPtive mAterials Science meTadatA) electronic lab notebook (ELN) | The favorite ELN for experimental scientists
************************************************************************************************************************

PASTA-ELN makes it easy and convenient for an experimental scientist to organize raw data with metadata. PASTA-ELN applies the extractors - Python scripts that 'extract' thumbnails, data, and metadata from the raw measurement files and automatically enter them into the database. These little programs can be written/adopted by scientists and can be shared. :ref:`To read more ... for advanced users <extractors>`.

The raw data is the origin of scientific work and has to follow the FAIR (Findable, Accessible, Interoperable, and Reusable) principles which also support the individual researcher who has an easier time to find and organize the data, which PASTA-ELN supports. Additionally, PASTA-ELN encourages the user to follow research data management guidelines, :ref:`which are given ... <dodonts>`. Since adaptive software development has revolutionized software projects, we believe that agile project planning is also highly beneficial for scientific research projects and encourage agile workflows while using PASTA-ELN. :ref:`To read more ... for all useres <Agile Project Planning>`.

Three (fictitious) user stories highlight different methods of using PASTA-ELN:

- Andrew plans his research first and then executes the tasks. :ref:`Read on how you can follow this path.. <Planning based research>`.

- Brenda has lots of data from her previous research in different folders and wants to integrate that data conveniently. :ref:`Read on how you can follow this path.. <Importing previous data>`.
- Claire goes to many conferences and meetings and wants to structure her notes. :ref:`Read on how you can follow this path.. <Recording meeting notes>`.

PASTA-ELN uses a local-first approach to store all data and metadata on user's storage devices and synchronize with a server upon user request. Thus, the data is always accessible through conventional software and its security and confidentiality are ensured. In addition, every researcher can fully adapt the metadata definitions to their personal taste and create an arbitrary folder structure in accordance with their typical workflows and research goals.

In PASTA-ELN, the meta-data is stored in a document database called CouchDB. This non-SQL database is highly adaptive to different raw data sources and corresponding metadata. People that want to contribute to PASTA-ELN, :ref:`read more on the CouchDB implementation <CouchDB information>`. If CouchDB and local storage are the two legs on which PASTA-ELN is built (and agile project planning is its heart), then the Python backend and graphical user interfaces (GUI) are its torso, which links everything together. :ref:`Read more on the implementation <Python implementation>`. People that want to contribute to PASTA-ELN, please visit us at github.com. Questions are answered in the :ref:`FAQs <faqs>`.

Overview
========

.. toctree::
   :maxdepth: 1

   install
   userstory
   dodonts
   faqs
   extractors
   ontology_configuration
   motivation


Main contributors
=================
* Steffen Brinckmann: principal investigator, focuses on python backend
* Thomas Düren: graphical user interfaces
* Raphael Röske: graphical user interfaces
* Velislava Yonkova: first extensive user
* Hanna Tsybenko: testing
* multiple colleagues that help with their valuable discussions


.. |---| unicode:: U+02014 .. em dash

