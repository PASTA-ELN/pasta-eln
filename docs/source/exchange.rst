.. _exchange:

Exchange Data with Other Tools
=============================

.. raw:: html

   <div class="three-columns">
      <a href="index.html" class="back-button" style="flex: 1; height: 25px;"><b>&larr; Back</b></a>
      <div style="flex: 12;">
         <h2>Data Interoperability with Other Tools</h2>
      </div>
   </div>

**Overview**: Pasta-ELN supports data exchange with other tools. Import data from a :ref:`Nextcloud server <nextcloud>`, synchronize between Pasta-ELN installations via an :ref:`elabFTW server <elabFTW>`, and upload to repositories like :ref:`Dataverse <dataverse>` and :ref:`Zenodo <zenodo>`.

.. _nextcloud:

Nextcloud server integration
----------------------------

(to be written)

.. _elabFTW:

Syncronize via ElabFTW server
-----------------------------

(to be written)

.. _dataverse:

Dataverse Repository
--------------------

Dataverse integration allows publishing PASTA projects on the `Dataverse platform <https://dataverse.org/>`_. Projects are packaged as ELN files, datasets are created, metadata is published, and files are uploaded. Metadata configuration is customizable for dataset creation.

**Steps to Obtain an API Key**:

1. Log in to your Dataverse instance.
2. Navigate to "API Token" under user settings.
3. Generate a new token.
4. Copy and paste the key into the configuration.

**Metadata Requirements**:

- *title* (string): defaults to the project title
- *author* (string): defaults to the list of authors
- *datasetContact* (string): defaults to the one in the list of authors
- *dsDescription* (string): defaults to the project objective
- *keyword* (list): defaults to the tags of this project
- *subject* (choice): At least one subject from a controlled vocabulary
- relatedPublications: is empty

.. _zenodo:

Zenodo
------

Zenodo integration supports publishing PASTA projects. Metadata is customizable, and files are uploaded to Zenodo's main or testing instance (https://zenodo.org, https://sandbox.zenodo.org).

**Steps to Obtain an API Key**:

1. Log in or create an account on Zenodo.
2. Navigate to "Applications" under user settings.
3. Generate a Personal Access Token with `deposit:write` and `deposit:actions` permissions.
4. Copy and paste the key into the configuration.

**Metadata Requirements**:

- *title* (string): defaults to the project title
- *creators* (list of dicts: name, affiliation, orcid): defaults to the list of authors
- *description* (string): defaults to the project objective
- *keywords* (list of strings): defaults to the tags of this project
- *additional keys* (dict): additional information
- publication_date (YYYY-MM-DD): is today
- upload_type (string, e.g. "dataset", "publication", etc.): is "dataset"
- access_right (e.g. "open", "embargoed", "restricted", "closed"): is "open"
- license (e.g. "CC-BY-4.0"): is "CC-BY-4.0"
- related_identifiers (list of dicts: identifier, relation, resource_type): is empty

The research domain can be encoded in:

 - "keywords": ["machine learning", "neuroscience", "data science"]
 - "communities": [{"identifier": "neuroscience"}]

Comparison of Zenodo and Dataverse Terms
----------------------------------------

.. csv-table::
   :widths: 30, 70
   :header-rows: 1

   Zenodo, Dataverse
   author, creators
   datasetContact, Not required (optionally in creators or omitted)
   dsDescription, description
   subject keywords, communities (approx.)
   keyword, keywords
   publicationDate, publication_date
   license (from termsOfUse), license
   language, language
   series, No direct match
   relatedPublications, related_identifiers
   productionDate, No direct match
   depositor (internal use), Not explicitly captured
   distributor, No direct match
   software (if included), upload_type = software or related_identifiers
   notesText, description (as additional info)
   fileDescription, File-level metadata (manually added in Zenodo)
   geographicCoverage, No direct match (can go in description or keywords)
   temporalCoverage, No direct match
   dataSources, description (or none)
   methods, description (or none)

.. raw:: html

   <a href="index.html" class="back-button" style="flex: 1; height: 25px;"><b>&larr; Back</b></a>
