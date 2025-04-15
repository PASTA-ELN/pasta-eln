.. _repositories:

Saving data to repositories
===========================

Zenodo
------

How to get an API key from Zenodo?

1. Go to Zenodo.
2. Log in or create an account.
3. Navigate to Applications under your user settings.
4. Generate a new Personal Access Token with deposit:write and deposit:actions permissions.
5. Copy-paste the key into the configuration

There are two instances of Zenodo

- Main instance: https://zenodo.org
- Testing instance: https://sandbox.zenodo.org

Zenodo typically requires this metadata:

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


Dataverse
---------

How to get an API key from Dataverse?

1. Go to your Dataverse instance
2. Log in
3. Navigate to "API Token" under your user settings (top-right).
4. Generate a new Token.
5. Copy-paste the key into the configuration

Oftentimes there are two instances of Dataverse: the main one and one for testing.

Dataverse requires this metadata:

- *title* (string): defaults to the project title
- *author* (string): defaults to the list of authors
- *datasetContact* (string): defaults to the one in the list of authors
- *dsDescription* (string): defaults to the project objective
- *keyword* (list): defaults to the tags of this project
- *subject* (choice): At least one subject from a controlled vocabulary
- relatedPublications: is empty



Comparison Zenodo and Dataverse terms
-------------------------------------

.. csv-table::
   :widths: 30, 70
   :header-rows: 1

   Zenodo, Dataverse
   author,	creators
   datasetContact,	Not required (optionally in creators or omitted)
   dsDescription,	description
   subject	keywords, communities (approx.)
   keyword,	keywords
   publicationDate,	publication_date
   license (from termsOfUse),	license
   language,	language
   series,	No direct match
   relatedPublications,	related_identifiers
   productionDate,	No direct match
   depositor (internal use),	Not explicitly captured
   distributor,	No direct match
   software (if included),	upload_type = software or related_identifiers
   notesText,	description (as additional info)
   fileDescription,	File-level metadata (manually added in Zenodo)
   geographicCoverage,	No direct match (can go in description or keywords)
   temporalCoverage,	No direct match
   dataSources,	description (or none)
   methods,	description (or none)
